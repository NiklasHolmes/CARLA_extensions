#!/usr/bin/env python

import argparse
import os
import math
import random
import time

import carla

try:
    from scenario_helper import is_transform_hidden_from_hero
except ModuleNotFoundError:
    from scenario_events.scenario_helper import is_transform_hidden_from_hero

try:
    from events_scenario06_static_props import HIGHPED_ROUTE_CONFIGS
except ModuleNotFoundError:
    from scenario_events.events_scenario06_static_props import HIGHPED_ROUTE_CONFIGS


START_TO_CAR_DELAY = 1.0
CAR_TO_RAIN_DELAY = 1.0
MID_RAIN_LEAD_IN_S = 5.0
HARD_RAIN_DURATION_S = 5.0
MID_RAIN_FOLLOW_UP_S = 5.0
SOFT_RAIN_DURATION_S = 5.0
RAIN_TO_HIGHPED_DELAY = 1.0
HIGHPED_TO_BUS_DELAY = 1.0
BUS_TO_SANIMAL_DELAY = 1.0
SANIMAL_TO_COW_DELAY = 1.0
COW_TO_FUEL_DELAY = 1.0
FUEL_TO_END_DELAY = 1.0

HIGHPED_BLUEPRINT_ID = "walker.pedestrian.0038"
HIGHPED_MAX_SPEED = 1.0
HIGHPED_ARRIVE_THRESH = 1.0

#weather: 
# 1 - ClearNoon
# 2 - CloudyNoon
# 3 - WetNoon
# 4 - WetCloudyNoon
# 5 - MidRainyNoon
# 6 - HardRainNoon
# 7 - SoftRainNoon

SPAWN_CARS = 0
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
CAR_RESPAWN_MAX_DISTANCE = 80.0
VEHICLE_SPAWN_MIN_SEPARATION = 8.0
run_in_singleFile_mode = True


def get_actor_blueprints(world, filter_pattern):
    bps = list(world.get_blueprint_library().filter(filter_pattern))
    if not bps:
        print(f"[Scenario06] WARNUNG: Keine Blueprints für {filter_pattern} gefunden!")
    return bps


def filter_blocked_vehicle_blueprints(blueprints, blocked_keywords):
    return [bp for bp in blueprints if not any(k in bp.id.lower() for k in blocked_keywords)]


class Scenario06Runner:
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
        self._cars_phase_done = False
        self._scenario_done = False
        self._weather_start_value = None
        self._weather_phase = "idle"
        self._weather_phase_start_time = None

        self._highped_route_done = False
        self._highped_route_active = False
        self._highped_route_config = None
        self._highped_walker_id = None
        self._highped_spawn_time = None
        self._highped_last_update_time = None
        self._highped_arrival_time = None
        self._highped_route_forward = True

        self._static_actor_ids = []
        self._vehicle_actor_ids = []
        self._walker_actor_ids = []

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

    def _distance_2d(self, location_a, location_b):
        dx = location_a.x - location_b.x
        dy = location_a.y - location_b.y
        return (dx * dx + dy * dy) ** 0.5

    def _get_actor_locations(self, excluded_ids=None):
        excluded_ids = set(excluded_ids or [])
        actor_locations = []
        for actor in self.world.get_actors():
            if actor.id in excluded_ids:
                continue
            try:
                actor_locations.append(actor.get_location())
            except Exception:
                continue
        return actor_locations

    def _pick_hidden_vehicle_spawn_transform(self, ego_transform, used_locations=None, max_attempts=64):
        used_locations = used_locations or []
        actor_locations = self._get_actor_locations()
        spawn_points = list(self.world.get_map().get_spawn_points())
        self._rng.shuffle(spawn_points)

        for spawn_point in spawn_points[:max_attempts]:
            if not is_transform_hidden_from_hero(spawn_point, ego_transform, MIN_SPAWN_DISTANCE, MAX_SPAWN_DISTANCE):
                continue

            spawn_location = spawn_point.location
            if any(self._distance_2d(spawn_location, existing) < VEHICLE_SPAWN_MIN_SEPARATION for existing in used_locations):
                continue

            if any(self._distance_2d(spawn_location, existing) < VEHICLE_SPAWN_MIN_SEPARATION for existing in actor_locations):
                continue

            return spawn_point

        return None

    def _spawn_single_vehicle(self, ego_transform, sim_time):
        all_bps = get_actor_blueprints(self.world, "vehicle.*")
        vehicle_bps = filter_blocked_vehicle_blueprints(all_bps, BLOCKED_VEHICLE_KEYWORDS)
        if not vehicle_bps:
            return False

        active_locations = []
        for vehicle_id in self._vehicle_actor_ids:
            actor = self.world.get_actor(vehicle_id)
            if actor is None:
                continue
            try:
                active_locations.append(actor.get_location())
            except Exception:
                continue

        spawn_transform = self._pick_hidden_vehicle_spawn_transform(ego_transform, active_locations)
        if spawn_transform is None:
            return False

        bp = self._rng.choice(vehicle_bps)
        tm = self._get_traffic_manager()
        actor = self.world.try_spawn_actor(bp, spawn_transform)
        if actor is None:
            print(
                f"[Scenario06] WARNUNG: Vehicle konnte nicht gespawnt werden | sim_time={sim_time:.2f}s | "
                f"spawn=({spawn_transform.location.x:.2f}, {spawn_transform.location.y:.2f}, {spawn_transform.location.z:.2f})"
            )
            return False

        try:
            actor.set_autopilot(True, tm.get_port())
        except Exception:
            pass
        self._vehicle_actor_ids.append(actor.id)
        print(
            f"[Scenario06] Vehicle respawned: id={actor.id}, sim_time={sim_time:.2f}s, "
            f"spawn=({spawn_transform.location.x:.2f}, {spawn_transform.location.y:.2f}, {spawn_transform.location.z:.2f})"
        )
        return True

    def _prune_far_vehicles(self, ego_transform):
        if ego_transform is None:
            return

        active_vehicle_ids = []
        for vehicle_id in list(self._vehicle_actor_ids):
            actor = self.world.get_actor(vehicle_id)
            if actor is None:
                continue

            try:
                actor_location = actor.get_location()
            except Exception:
                continue

            distance = self._distance_2d(actor_location, ego_transform.location)
            if distance > CAR_RESPAWN_MAX_DISTANCE:
                print(f"[Scenario06] Vehicle removed: id={vehicle_id}, distance={distance:.1f}m")
                try:
                    actor.destroy()
                except Exception:
                    pass
                continue

            active_vehicle_ids.append(vehicle_id)

        self._vehicle_actor_ids = active_vehicle_ids

    def _maintain_spawn_pools(self, ego_transform, sim_time):
        self._prune_far_vehicles(ego_transform)

        vehicle_attempts = max(1, (SPAWN_CARS - len(self._vehicle_actor_ids)) * 3)
        for _ in range(vehicle_attempts):
            if len(self._vehicle_actor_ids) >= SPAWN_CARS:
                break
            if not self._spawn_single_vehicle(ego_transform, sim_time):
                break

    def _spawn_dynamic_traffic(self, ego_transform, sim_time):
        target_count = SPAWN_CARS
        attempts = 0
        max_attempts = max(20, target_count * 20)

        while len(self._vehicle_actor_ids) < target_count and attempts < max_attempts:
            attempts += 1
            if not self._spawn_single_vehicle(ego_transform, sim_time):
                continue

        print(
            f"[Scenario06] Vehicles spawned: {len(self._vehicle_actor_ids)}/{target_count} after attempts={attempts}"
        )

        if len(self._vehicle_actor_ids) >= target_count:
            self._cars_phase_done = True
            self._traffic_spawn_time = sim_time
            return True

        return False

    def _force_green_light(self, ego):
        if ego and ego.is_at_traffic_light():
            tl = ego.get_traffic_light()
            if tl:
                tl.set_state(carla.TrafficLightState.Green)
                tl.set_green_time(10.0)

    def _get_highped_route_config(self, hero_location):
        for route_config in HIGHPED_ROUTE_CONFIGS:
            trigger_location = route_config["trigger_location"]
            if abs(hero_location.x - trigger_location.x) <= route_config["trigger_x_tolerance"] and abs(hero_location.y - trigger_location.y) <= route_config["trigger_y_tolerance"]:
                return route_config
        return None

    def _spawn_highped(self, route_config, sim_time):
        if self._highped_route_done or self._highped_route_active:
            return False

        walker_bp = self.world.get_blueprint_library().find(HIGHPED_BLUEPRINT_ID)
        if walker_bp.has_attribute("is_invincible"):
            walker_bp.set_attribute("is_invincible", "false")

        spawn_location = route_config["spawn_location"]
        spawn_yaw = route_config.get("spawn_yaw")
        if spawn_yaw is None:
            target_location = route_config["target_location"]
            spawn_yaw = math.degrees(math.atan2(target_location.y - spawn_location.y, target_location.x - spawn_location.x))

        spawn_transform = carla.Transform(
            spawn_location,
            carla.Rotation(pitch=0.0, yaw=spawn_yaw, roll=0.0),
        )

        walker = self.world.try_spawn_actor(walker_bp, spawn_transform)
        if walker is None:
            print(
                f"[Scenario06] WARNUNG: HighPed konnte nicht gespawnt werden | sim_time={sim_time:.2f}s | "
                f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
            )
            return False

        self._highped_route_active = True
        self._highped_route_config = route_config
        self._highped_walker_id = walker.id
        self._highped_spawn_time = sim_time
        self._highped_last_update_time = sim_time
        self._highped_arrival_time = None
        self._highped_route_forward = True
        self._walker_actor_ids.append(walker.id)

        print(
            f"[Scenario06] HighPed spawned: id={walker.id}, route={route_config['name']}, sim_time={sim_time:.2f}s, "
            f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
        )
        return True

    def _finish_highped_route(self, walker):
        if walker is not None:
            try:
                walker.destroy()
            except Exception:
                pass

        if self._highped_walker_id in self._walker_actor_ids:
            self._walker_actor_ids.remove(self._highped_walker_id)

        self._highped_route_active = False
        self._highped_route_done = True
        self._highped_route_config = None
        self._highped_walker_id = None
        self._highped_spawn_time = None
        self._highped_last_update_time = None
        self._highped_arrival_time = None
        self._highped_route_forward = True
        print("[Scenario06] HighPed route finished. Continuing with HIGHPED_TO_BUS.")

    def _update_highped_route(self, sim_time):
        if not self._highped_route_active or self._highped_route_config is None or self._highped_walker_id is None:
            return

        walker = self.world.get_actor(self._highped_walker_id)
        if walker is None:
            self._finish_highped_route(None)
            return

        start_location = self._highped_route_config["spawn_location"]
        end_location = self._highped_route_config["target_location"]
        target_location = end_location if self._highped_route_forward else start_location
        current_location = walker.get_location()

        if self._highped_last_update_time is None:
            delta_time = SIM_STEP_S
        else:
            delta_time = max(0.0, sim_time - self._highped_last_update_time)
            if delta_time == 0.0:
                delta_time = SIM_STEP_S
        self._highped_last_update_time = sim_time

        distance = self._distance_2d(current_location, target_location)
        if distance <= HIGHPED_ARRIVE_THRESH:
            if self._highped_arrival_time is None:
                self._highped_arrival_time = sim_time
                print(
                    f"[Scenario06] HighPed reached {'target' if self._highped_route_forward else 'start'}: id={walker.id}, sim_time={sim_time:.2f}s"
                )

            if (sim_time - self._highped_arrival_time) >= HIGHPED_TO_BUS_DELAY:
                self._highped_route_forward = not self._highped_route_forward
                self._highped_arrival_time = None
            return

        max_step = HIGHPED_MAX_SPEED * delta_time
        if max_step <= 0.0:
            return

        travel_ratio = min(1.0, max_step / distance)
        try:
            direction_x = target_location.x - current_location.x
            direction_y = target_location.y - current_location.y
            direction_length = math.hypot(direction_x, direction_y)
            if direction_length == 0.0:
                return

            walker.apply_control(
                carla.WalkerControl(
                    direction=carla.Vector3D(x=direction_x / direction_length, y=direction_y / direction_length, z=0.0),
                    speed=HIGHPED_MAX_SPEED,
                    jump=False,
                )
            )
        except Exception as exc:
            print(f"[Scenario06] WARNUNG: HighPed konnte nicht manuell bewegt werden: {exc}")
            self._finish_highped_route(walker)

    def _maybe_spawn_highped(self, ego_transform, sim_time):
        if ego_transform is None or self._highped_route_done or self._highped_route_active:
            return

        route_config = self._get_highped_route_config(ego_transform.location)
        if route_config is None:
            return

        self._spawn_highped(route_config, sim_time)

    def _should_spawn_traffic(self, sim_time):
        return (not self._traffic_spawned) and (sim_time - self._start_sim_time) >= START_TO_CAR_DELAY

    def _update_weather_cycle(self, sim_time):
        if self._start_sim_time is None:
            return

        elapsed = sim_time - self._start_sim_time

        if self._weather_phase == "idle" and elapsed >= CAR_TO_RAIN_DELAY:
            if self._weather_start_value is None:
                self._weather_start_value = self.world.get_weather()

            self.world.set_weather(carla.WeatherParameters.MidRainyNoon)
            self._weather_phase = "mid_rain_lead_in"
            self._weather_phase_start_time = sim_time
            print(f"[Scenario06] Weather changed to MidRainyNoon at sim_time={sim_time:.2f}s")
            return

        if self._weather_phase == "mid_rain_lead_in":
            if (sim_time - self._weather_phase_start_time) < MID_RAIN_LEAD_IN_S:
                return

            self.world.set_weather(carla.WeatherParameters.HardRainNoon)
            self._weather_phase = "hard_rain"
            self._weather_phase_start_time = sim_time
            print(f"[Scenario06] Weather changed to HardRainNoon at sim_time={sim_time:.2f}s")
            return

        if self._weather_phase == "hard_rain":
            if (sim_time - self._weather_phase_start_time) < HARD_RAIN_DURATION_S:
                return

            self.world.set_weather(carla.WeatherParameters.MidRainyNoon)
            self._weather_phase = "mid_rain_follow_up"
            self._weather_phase_start_time = sim_time
            print(f"[Scenario06] Weather changed to MidRainyNoon at sim_time={sim_time:.2f}s")
            return

        if self._weather_phase == "mid_rain_follow_up":
            if (sim_time - self._weather_phase_start_time) < MID_RAIN_FOLLOW_UP_S:
                return

            self.world.set_weather(carla.WeatherParameters.SoftRainNoon)
            self._weather_phase = "soft_rain"
            self._weather_phase_start_time = sim_time
            print(f"[Scenario06] Weather changed to SoftRainNoon at sim_time={sim_time:.2f}s")
            return

        if self._weather_phase == "soft_rain":
            if (sim_time - self._weather_phase_start_time) < SOFT_RAIN_DURATION_S:
                return

            if self._weather_start_value is not None:
                self.world.set_weather(self._weather_start_value)
            self._weather_phase = "restored"
            self._weather_phase_start_time = sim_time
            print(f"[Scenario06] Weather restored at sim_time={sim_time:.2f}s")

    def run(self):
        print("[Scenario06] Running...")
        if run_in_singleFile_mode:
            self.world.set_weather(carla.WeatherParameters.CloudyNoon)
            print("[Scenario06] Weather set to CloudyNoon for single-file mode")

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

                if self._should_spawn_traffic(sim_time) and self._spawn_dynamic_traffic(ego_transform, sim_time):
                    self._traffic_spawned = True
                    self._traffic_spawn_time = sim_time

                self._update_weather_cycle(sim_time)

                if ego:
                    self._maybe_spawn_highped(ego_transform, sim_time)

                self._update_highped_route(sim_time)

                if self._traffic_spawned:
                    self._maintain_spawn_pools(ego_transform, sim_time)

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
        print("[Scenario06] Cleanup...")
        all_ids = self._static_actor_ids + self._vehicle_actor_ids + self._walker_actor_ids
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
            print(f"[Scenario06] WARNING: could not write done signal file: {exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=2000, type=int)
    parser.add_argument("--tm-port", default=8000, type=int)
    parser.add_argument("--done-file", default=None)
    args = parser.parse_args()
    Scenario06Runner(args.host, args.port, args.tm_port, args.done_file).run()