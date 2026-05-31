#!/usr/bin/env python

import argparse
import math
import os
import random
import time

import carla


START_TO_CAR_DELAY = 1.0
CAR_TO_SNOW_DELAY = 1.0
SNOW_TO_HIGHPED_DELAY = 1.0
HIGHPED_TO_BUS_DELAY = 1.0
BUS_TO_SANIMAL_DELAY = 1.0
SANIMAL_TO_COW_DELAY = 1.0
COW_TO_FUEL_DELAY = 1.0
FUEL_TO_END_DELAY = 1.0

SPAWN_CARS = 5
SIM_STEP_S = 0.05

BLOCKED_VEHICLE_KEYWORDS = (
    "firetruck",
    "ambulance",
    "bus",
    "fusorosa",
    "carlacola",
    "truck",
    "european_hgv",
    "t2",
    "police",
)

MIN_SPAWN_DISTANCE = 30.0
MAX_SPAWN_DISTANCE = 100.0
VEHICLE_SPAWN_MIN_SEPARATION = 8.0
run_in_singleFile_mode = True

experiment1_carRoute = True
experiment2_streetBlock = False                  # not working
STREET_BLOCK_ROUTE_MODE = "straight"

SINGLE_CAR_ROUTE_SCALE = 1.0
SINGLE_CAR_ROUTE_RAW_POINTS = (
    (24.70712402, -28.98084473, 0.30000000),
    (17.84708008, -4.49413452, 0.55000000),
    (-44.03149414, -11.26184448, 0.45000000),
    (-44.75590332, -104.28300781, 0.45000000),
)

STREET_BLOCK_START_RAW_POINT = (24.70712402, -28.98084473, 0.30000000)
STREET_BLOCK_TRIGGER_RAW_POINT = (24.39941162, -12.36304199, 0.55001526)
STREET_BLOCK_STRAIGHT_TARGET_RAW_POINT = (24.59944092, 31.59789795, 0.30000000)
STREET_BLOCK_RIGHT_TARGET_RAW_POINT = (5.64708008, -4.49413452, 0.30000000)
STREET_BLOCK_LEFT_TARGET_RAW_POINT = (-44.03149414, -11.26184448, 0.45000000)
STREET_BLOCK_STOP_BEFORE_BLOCK_METERS = 12.0


def get_actor_blueprints(world, filter_pattern):
    bps = list(world.get_blueprint_library().filter(filter_pattern))
    if not bps:
        print(f"[Scenario06Exp] WARNUNG: Keine Blueprints für {filter_pattern} gefunden!")
    return bps


def filter_blocked_vehicle_blueprints(blueprints, blocked_keywords):
    return [bp for bp in blueprints if not any(k in bp.id.lower() for k in blocked_keywords)]


class Scenario06ExperimentsRunner:
    def __init__(self, host, port, tm_port, done_file=None):
        self.client = carla.Client(host, port)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()
        self._tm_port = tm_port
        self._done_file = done_file
        self._rng = random.Random()

        self._start_sim_time = None
        self._traffic_spawned = False
        self._traffic_spawn_time = None
        self._scenario_done = False

        self._static_actor_ids = []
        self._vehicle_actor_ids = []
        self._route_vehicle_actor_id = None
        self._blocker_vehicle_actor_id = None
        self._route_vehicle_role_name = "scenario06exp_route_vehicle_01"
        self._street_block_trigger_location = None
        self._street_block_suffix_route_locations = []
        self._street_block_branch_applied = False

    def _get_traffic_manager(self):
        try:
            tm = self.client.get_trafficmanager(self._tm_port)
        except Exception:
            tm = self.client.get_trafficmanager()
        tm.set_synchronous_mode(self.world.get_settings().synchronous_mode)
        return tm

    def find_hero(self):
        for actor in self.world.get_actors():
            if actor.attributes.get("role_name") in ["hero", "default_player"]:
                return actor
        return None

    def _scaled_location(self, raw_point):
        x, y, z = raw_point
        return carla.Location(
            x=x * SINGLE_CAR_ROUTE_SCALE,
            y=y * SINGLE_CAR_ROUTE_SCALE,
            z=z * SINGLE_CAR_ROUTE_SCALE,
        )

    def _project_to_driving_lane(self, location):
        waypoint = self.world.get_map().get_waypoint(
            location,
            project_to_road=True,
            lane_type=carla.LaneType.Driving,
        )
        if waypoint is None:
            return location
        projected = waypoint.transform.location
        return carla.Location(x=projected.x, y=projected.y, z=projected.z)

    def _build_route_locations_from_raw_points(self, raw_points):
        route_locations = []
        for raw_point in raw_points:
            route_locations.append(self._project_to_driving_lane(self._scaled_location(raw_point)))
        return route_locations

    def _trace_route_locations(self, origin_raw_point, destination_raw_point):
        world_map = self.world.get_map()
        origin_location = self._project_to_driving_lane(self._scaled_location(origin_raw_point))
        destination_location = self._project_to_driving_lane(self._scaled_location(destination_raw_point))
        start_waypoint = world_map.get_waypoint(origin_location, project_to_road=True, lane_type=carla.LaneType.Driving)
        destination_waypoint = world_map.get_waypoint(destination_location, project_to_road=True, lane_type=carla.LaneType.Driving)
        if start_waypoint is None or destination_waypoint is None:
            return []

        route_locations = [start_waypoint.transform.location]
        current_waypoint = start_waypoint
        target_location = destination_waypoint.transform.location

        for _ in range(200):
            if current_waypoint.transform.location.distance(target_location) <= 2.0:
                break

            next_waypoints = current_waypoint.next(2.0)
            if not next_waypoints:
                break

            current_location = current_waypoint.transform.location

            def waypoint_score(waypoint):
                next_location = waypoint.transform.location
                branch_vector_x = next_location.x - current_location.x
                branch_vector_y = next_location.y - current_location.y
                target_vector_x = target_location.x - current_location.x
                target_vector_y = target_location.y - current_location.y

                branch_length = math.hypot(branch_vector_x, branch_vector_y)
                target_length = math.hypot(target_vector_x, target_vector_y)
                if branch_length == 0.0 or target_length == 0.0:
                    angle_penalty = 0.0
                else:
                    dot_product = branch_vector_x * target_vector_x + branch_vector_y * target_vector_y
                    cosine = max(-1.0, min(1.0, dot_product / (branch_length * target_length)))
                    angle_penalty = math.degrees(math.acos(cosine))

                distance_penalty = next_location.distance(target_location)
                return (angle_penalty, distance_penalty)

            chosen_waypoint = min(next_waypoints, key=waypoint_score)
            current_waypoint = chosen_waypoint
            route_locations.append(current_waypoint.transform.location)

        return route_locations

    def _spawn_vehicle(self, blueprint, transform, label, sim_time, use_autopilot=True, physics=True):
        if label == "Street-block route vehicle" and blueprint.has_attribute("role_name"):
            blueprint.set_attribute("role_name", self._route_vehicle_role_name)

        actor = self.world.try_spawn_actor(blueprint, transform)
        if actor is None:
            print(
                f"[Scenario06Exp] WARNUNG: {label} konnte nicht gespawnt werden | sim_time={sim_time:.2f}s | "
                f"spawn=({transform.location.x:.2f}, {transform.location.y:.2f}, {transform.location.z:.2f})"
            )
            return None

        if physics is False:
            try:
                actor.set_simulate_physics(False)
            except Exception:
                pass

        if use_autopilot:
            tm = self._get_traffic_manager()
            try:
                actor.set_autopilot(True, tm.get_port())
            except Exception:
                pass

        self._vehicle_actor_ids.append(actor.id)
        print(
            f"[Scenario06Exp] {label} spawned: id={actor.id}, sim_time={sim_time:.2f}s, "
            f"spawn=({transform.location.x:.2f}, {transform.location.y:.2f}, {transform.location.z:.2f})"
        )
        return actor

    def _spawn_experiment1_car_route(self, sim_time):
        route_locations = self._build_route_locations_from_raw_points(SINGLE_CAR_ROUTE_RAW_POINTS)
        if len(route_locations) < 2:
            print("[Scenario06Exp] WARNUNG: experiment1 route ist unvollständig.")
            return False

        all_bps = get_actor_blueprints(self.world, "vehicle.*")
        vehicle_bps = filter_blocked_vehicle_blueprints(all_bps, BLOCKED_VEHICLE_KEYWORDS)
        if not vehicle_bps:
            return False

        tm = self._get_traffic_manager()

        actor = None
        used_route_index = None
        spawn_transform = None
        for route_index, spawn_location in enumerate(route_locations[:-1]):
            next_location = route_locations[route_index + 1]
            yaw = math.degrees(math.atan2(next_location.y - spawn_location.y, next_location.x - spawn_location.x))
            candidate_transform = carla.Transform(spawn_location, carla.Rotation(pitch=0.0, yaw=yaw, roll=0.0))

            blueprint = self._rng.choice(vehicle_bps)
            actor = self._spawn_vehicle(blueprint, candidate_transform, "Experiment1 route vehicle", sim_time)
            if actor is None:
                continue

            used_route_index = route_index
            spawn_transform = candidate_transform
            break

        if actor is None or used_route_index is None or spawn_transform is None:
            return False

        try:
            tm.set_path(actor, route_locations[used_route_index:])
        except Exception as exc:
            print(f"[Scenario06Exp] WARNUNG: experiment1 route konnte nicht gesetzt werden: {exc}")

        self._route_vehicle_actor_id = actor.id
        return True

    def _spawn_experiment2_street_block(self, sim_time):
        start_location = self._scaled_location(STREET_BLOCK_START_RAW_POINT)
        route_target_by_mode = {
            "straight": STREET_BLOCK_STRAIGHT_TARGET_RAW_POINT,
            "right": STREET_BLOCK_RIGHT_TARGET_RAW_POINT,
            "left": STREET_BLOCK_LEFT_TARGET_RAW_POINT,
        }
        selected_mode = STREET_BLOCK_ROUTE_MODE if STREET_BLOCK_ROUTE_MODE in route_target_by_mode else "straight"
        selected_target_raw_point = route_target_by_mode[selected_mode]

        prefix_route_locations = self._trace_route_locations(STREET_BLOCK_START_RAW_POINT, STREET_BLOCK_TRIGGER_RAW_POINT)
        suffix_route_locations = self._trace_route_locations(STREET_BLOCK_TRIGGER_RAW_POINT, selected_target_raw_point)
        if len(prefix_route_locations) < 2 or len(suffix_route_locations) < 2:
            print("[Scenario06Exp] WARNUNG: experiment2 Route ist unvollständig.")
            return False

        all_bps = get_actor_blueprints(self.world, "vehicle.*")
        vehicle_bps = filter_blocked_vehicle_blueprints(all_bps, BLOCKED_VEHICLE_KEYWORDS)
        if not vehicle_bps:
            return False

        tm = self._get_traffic_manager()

        start_waypoint = self.world.get_map().get_waypoint(
            start_location,
            project_to_road=True,
            lane_type=carla.LaneType.Driving,
        )
        if start_waypoint is None:
            print("[Scenario06Exp] WARNUNG: Startpunkt kann nicht auf Fahrbahn projiziert werden.")
            return False

        spawn_transform = carla.Transform(
            start_waypoint.transform.location,
            carla.Rotation(pitch=0.0, yaw=start_waypoint.transform.rotation.yaw, roll=0.0),
        )

        route_blueprint = self._rng.choice(vehicle_bps)
        route_actor = self._spawn_vehicle(route_blueprint, spawn_transform, "Street-block route vehicle", sim_time)
        if route_actor is None:
            return False

        try:
            tm.set_path(route_actor, prefix_route_locations)
        except Exception as exc:
            print(f"[Scenario06Exp] WARNUNG: streetBlock route konnte nicht gesetzt werden: {exc}")

        self._route_vehicle_actor_id = route_actor.id
        self._street_block_trigger_location = prefix_route_locations[-1]
        self._street_block_suffix_route_locations = suffix_route_locations
        self._street_block_branch_applied = False
        print(
            f"[Scenario06Exp] Street block active: start=({start_location.x:.2f}, {start_location.y:.2f}, {start_location.z:.2f}) "
            f"route={selected_mode}"
        )
        return True

    def _force_route_vehicle_green_light(self):
        if self._route_vehicle_actor_id is None:
            return

        actor = self.world.get_actor(self._route_vehicle_actor_id)
        if actor is None or not actor.is_at_traffic_light():
            return

        traffic_light = actor.get_traffic_light()
        if traffic_light is None:
            return

        try:
            traffic_light.set_state(carla.TrafficLightState.Green)
            traffic_light.set_green_time(10.0)
        except Exception as exc:
            print(f"[Scenario06Exp] WARNUNG: Route vehicle traffic light konnte nicht auf grün gesetzt werden: {exc}")

    def _apply_street_block_branch_if_needed(self):
        if self._route_vehicle_actor_id is None or self._street_block_branch_applied:
            return
        if not self._street_block_trigger_location or len(self._street_block_suffix_route_locations) < 2:
            return

        actor = self.world.get_actor(self._route_vehicle_actor_id)
        if actor is None:
            return

        if actor.get_location().distance(self._street_block_trigger_location) > 6.0:
            return

        tm = self._get_traffic_manager()
        try:
            tm.set_path(actor, self._street_block_suffix_route_locations)
            self._street_block_branch_applied = True
        except Exception as exc:
            print(f"[Scenario06Exp] WARNUNG: streetBlock branch konnte nicht gesetzt werden: {exc}")

    def _force_green_light(self, ego):
        if ego and ego.is_at_traffic_light():
            tl = ego.get_traffic_light()
            if tl:
                tl.set_state(carla.TrafficLightState.Green)
                tl.set_green_time(10.0)

    def run(self):
        print("[Scenario06Exp] Running...")

        try:
            while True:
                self.world.wait_for_tick()
                sim_time = self.world.get_snapshot().timestamp.elapsed_seconds
                if self._start_sim_time is None:
                    self._start_sim_time = sim_time

                ego = self.find_hero()
                ego_transform = ego.get_transform() if ego else carla.Transform(
                    carla.Location(x=150.60, y=-173.30, z=0.70),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                )

                if not self._traffic_spawned and (sim_time - self._start_sim_time) >= START_TO_CAR_DELAY:
                    spawned = False
                    if experiment1_carRoute:
                        spawned = self._spawn_experiment1_car_route(sim_time)
                    elif experiment2_streetBlock:
                        spawned = self._spawn_experiment2_street_block(sim_time)

                    if spawned:
                        self._traffic_spawned = True
                        self._traffic_spawn_time = sim_time

                self._force_route_vehicle_green_light()
                self._apply_street_block_branch_if_needed()

                if ego:
                    self._force_green_light(ego)

                if self._scenario_done:
                    return

                time.sleep(SIM_STEP_S)
        except KeyboardInterrupt:
            pass
        finally:
            self.destroy()
            self._signal_done()

    def destroy(self):
        print("[Scenario06Exp] Cleanup...")
        all_ids = self._static_actor_ids + self._vehicle_actor_ids
        if all_ids:
            self.client.apply_batch([carla.command.DestroyActor(actor_id) for actor_id in all_ids])

    def _signal_done(self):
        if not self._done_file:
            return
        try:
            done_dir = os.path.dirname(self._done_file)
            if done_dir:
                os.makedirs(done_dir, exist_ok=True)
            with open(self._done_file, "w", encoding="utf-8") as done_handle:
                done_handle.write("done\n")
        except Exception as exc:
            print(f"[Scenario06Exp] WARNING: could not write done signal file: {exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=2000, type=int)
    parser.add_argument("--tm-port", default=8000, type=int)
    parser.add_argument("--done-file", default=None)
    args = parser.parse_args()
    Scenario06ExperimentsRunner(args.host, args.port, args.tm_port, args.done_file).run()