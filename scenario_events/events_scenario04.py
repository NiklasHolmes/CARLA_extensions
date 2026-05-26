#!/usr/bin/env python

#import logging
import os
import random
import time
import argparse
import carla
try:
    from scenario_helper import is_transform_hidden_from_hero, pick_hidden_navigation_location, pick_hidden_navigation_location_near
except ModuleNotFoundError:
    from scenario_events.scenario_helper import is_transform_hidden_from_hero, pick_hidden_navigation_location, pick_hidden_navigation_location_near
from common.audio_paths import HAPPINESS_RP_UPTOWN_FUNK_PATH
from generate_audio import SongAudio

# Constants
TRAFFIC_SPAWN_DELAY_SECONDS = 5.0
VEHICLE_ACTIVE_SECONDS = 0.0                    # if > 0 => vehicles will be removed; if = 0 => stay infinitely
CAR_TO_PED_DELAY_SECONDS = 2.0
PED_TO_SONG_DELAY_SECONDS = 7.0
SONG_TO_END_DELAY_SECONDS = 5.0
SONG_START_OFFSET_SECONDS = 30.0
SONG_PLAY_DURATION_SECONDS = 30.0
SONG_FADE_IN_MS = 3000
SONG_FADE_OUT_MS = 3000
HERO_GREEN_LIGHT_HOLD_SECONDS = 10.0
SPAWN_CARS = 5                              # 15?
ENABLE_ROUTE_PEDESTRIANS = True
PEDESTRIAN_BLUEPRINT_ID = "walker.pedestrian.0046"
PEDESTRIAN_MAX_SPEED = 3.5
PEDESTRIAN_COUNT = 5                        # 15? 24 = no pedestrian walks
PEDESTRIAN_WAIT_TIMEOUT_S = 40.0
PEDESTRIAN_ARRIVE_THRESH = 1.0
SIM_STEP_S = 0.05

BLOCKED_VEHICLE_KEYWORDS = (
    "firetruck", "ambulance", "bus", "fusorosa", "carlacola", "truck", "european_hgv", "t2",
)

MIN_SPAWN_DISTANCE = 40.0
MAX_SPAWN_DISTANCE = 150.0
PEDESTRIAN_MIN_HIDDEN_DISTANCE = 2.0
PEDESTRIAN_MAX_HIDDEN_DISTANCE = 500.0
PEDESTRIAN_MIN_ROUTE_DISTANCE = 5.0
PEDESTRIAN_NAV_SAMPLES = 96

PEDESTRIAN_START_LOCATIONS = [
    carla.Location(x=137.80, y=-178.60, z=0.40),
    carla.Location(x=136.60, y=-227.90, z=0.30),
    carla.Location(x=195.30, y=-257.00, z=0.30),
    carla.Location(x=223.80, y=-253.30, z=0.30),
    carla.Location(x=231.90, y=-222.50, z=0.30),
    carla.Location(x=262.30, y=-266.60, z=0.30),
    carla.Location(x=262.40, y=-286.20, z=0.30),
    carla.Location(x=285.20, y=-227.80, z=0.30),
    carla.Location(x=267.90, y=-219.10, z=0.30),
    carla.Location(x=299.40, y=-176.00, z=0.60),
    carla.Location(x=299.40, y=-185.30, z=0.30),
    carla.Location(x=344.40, y=-155.20, z=0.30),
    carla.Location(x=344.60, y=-234.30, z=0.10),
    carla.Location(x=251.10, y=-191.60, z=0.30),
    carla.Location(x=217.80, y=-301.50, z=0.30),
    carla.Location(x=168.50, y=-301.50, z=0.30),
    carla.Location(x=122.10, y=-316.60, z=0.30),
    carla.Location(x=89.70, y=-288.10, z=0.30),
    carla.Location(x=73.80, y=-235.00, z=0.50),
    carla.Location(x=-203.90, y=-91.30, z=0.50),
    carla.Location(x=9.90, y=359.00, z=-0.80),
    carla.Location(x=89.0, y=365.30, z=-0.80),
    carla.Location(x=418.20, y=90.80, z=-0.70),
    carla.Location(x=405.80, y=93.90, z=-1.50),
]

STATIC_PROP_SPAWNS = [
    {
        "name": "mailbox",
        "blueprints": ["static.prop.mailbox"],
        "transform": carla.Transform(
            carla.Location(x=249.20, y=127.00, z=0.10),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    }
]

def get_actor_blueprints(world, filter_pattern):
    bps = list(world.get_blueprint_library().filter(filter_pattern))
    if not bps:
        print(f"[Scenario04] WARNUNG: Keine Blueprints für {filter_pattern} gefunden!")
    return bps

def filter_blocked_vehicle_blueprints(blueprints, blocked_keywords):
    return [bp for bp in blueprints if not any(k in bp.id.lower() for k in blocked_keywords)]

class Scenario04Runner:
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
        self._vehicles_cleared = False
        self._pedestrians_spawned = False
        self._pedestrians_started = False
        self._pedestrians_done = False
        self._pedestrian_spawn_time = None
        self._pedestrian_routes = []
        self._song_started = False
        self._song_start_time = None
        self._song_finished = False
        self._song_finish_time = None
        self._song_audio = SongAudio(
            HAPPINESS_RP_UPTOWN_FUNK_PATH,
            start_seconds=SONG_START_OFFSET_SECONDS,
            play_seconds=SONG_PLAY_DURATION_SECONDS,
            fade_in_ms=SONG_FADE_IN_MS,
            fade_out_ms=SONG_FADE_OUT_MS,
            volume=0.85,
            channel_index=6,
        )
        self._scenario_done = False
        self._cars_phase_done = False
        self._pedestrians_phase_done = False
        
        self._static_actor_ids = []
        self._vehicle_actor_ids = []
        self._walker_actor_ids = []
        self._walker_controller_ids = []

    def _get_traffic_manager(self):
        try:
            tm = self.client.get_trafficmanager(self._tm_port)
        except Exception:
            tm = self.client.get_trafficmanager()
        tm.set_synchronous_mode(self.world.get_settings().synchronous_mode)
        return tm

    def _project_location_to_navigation(self, location):
        waypoint = self.world.get_map().get_waypoint(
            location,
            project_to_road=True,
            lane_type=carla.LaneType.Any,
        )
        if waypoint is None:
            return carla.Location(x=location.x, y=location.y, z=location.z)
        nav_location = waypoint.transform.location
        return carla.Location(x=nav_location.x, y=nav_location.y, z=location.z)

    def find_hero(self):
        for actor in self.world.get_actors():
            if actor.attributes.get('role_name') in ['hero', 'default_player']:
                return actor
        return None

    def _spawn_static_prop_once(self):
        bp_lib = self.world.get_blueprint_library()
        for prop_config in STATIC_PROP_SPAWNS:
            prop_bp = None
            for bp_id in prop_config.get("blueprints", []):
                try:
                    prop_bp = bp_lib.find(bp_id)
                    break
                except: continue
            if prop_bp:
                actor = self.world.try_spawn_actor(prop_bp, prop_config["transform"])
                if actor: self._static_actor_ids.append(actor.id)

    def _spawn_dynamic_traffic(self, ego_transform, sim_time):
        tm = self._get_traffic_manager()
            
        spawn_points = list(self.world.get_map().get_spawn_points())
        self._rng.shuffle(spawn_points)
        all_bps = get_actor_blueprints(self.world, "vehicle.*")
        vehicle_bps = filter_blocked_vehicle_blueprints(all_bps, BLOCKED_VEHICLE_KEYWORDS)
        
        car_points = self._pick_hidden_points(spawn_points, ego_transform, SPAWN_CARS)
        print(
            f"[Scenario04] Spawning vehicles at sim_time={sim_time:.2f}s: "
            #f"requested={len(car_points)}, blueprint_count={len(vehicle_bps)}"
        )
        self._spawn_batch_vehicles(car_points, vehicle_bps, tm)
        self._cars_phase_done = True

    def _pick_hidden_points(self, points, ego_transform, count):
        if not ego_transform: return points[:count]
        hidden = []
        for p in points:
            if is_transform_hidden_from_hero(p, ego_transform, MIN_SPAWN_DISTANCE, MAX_SPAWN_DISTANCE):
                hidden.append(p)
        return hidden[:count]

    def _pick_hidden_navigation_location(self, ego_transform, used_locations=None, min_distance=MIN_SPAWN_DISTANCE, max_distance=MAX_SPAWN_DISTANCE):
        hidden_location = pick_hidden_navigation_location(
            self.world,
            ego_transform,
            used_locations=used_locations,
            min_distance=min_distance,
            max_distance=max_distance,
            min_route_distance=PEDESTRIAN_MIN_ROUTE_DISTANCE,
            sample_count=PEDESTRIAN_NAV_SAMPLES,
        )
        if hidden_location is not None:
            return hidden_location

        if ego_transform is not None:
            projected_hero_location = self._project_location_to_navigation(ego_transform.location)
            if is_transform_hidden_from_hero(carla.Transform(projected_hero_location), ego_transform, min_distance, max_distance):
                return projected_hero_location

        return None

    def _get_random_pedestrian_blueprint(self, excluded_ids=None):
        blueprints = get_actor_blueprints(self.world, "walker.pedestrian.*")
        if not blueprints:
            return self.world.get_blueprint_library().find(PEDESTRIAN_BLUEPRINT_ID)

        excluded_ids = set(excluded_ids or [])
        available_blueprints = [bp for bp in blueprints if bp.id not in excluded_ids]
        pool = available_blueprints if available_blueprints else blueprints

        walker_bp = self._rng.choice(pool)
        if walker_bp.has_attribute("is_invincible"):
            walker_bp.set_attribute("is_invincible", "false")
        if walker_bp.has_attribute("can_use_wheelchair") and self._rng.randint(0, 100) < 11:
            walker_bp.set_attribute("use_wheelchair", "true")
        return walker_bp

    def _get_random_pedestrian_speed(self):
        min_speed = 1.5
        max_speed = PEDESTRIAN_MAX_SPEED
        steps = int(round((max_speed - min_speed) / 0.5))
        if steps <= 0:
            return max_speed
        speed = min_speed + (0.5 * self._rng.randint(0, steps))
        return min(speed, max_speed)

    def _spawn_batch_vehicles(self, points, bps, tm):
        batch = []
        for p in points:
            bp = self._rng.choice(bps)
            batch.append(carla.command.SpawnActor(bp, p).then(
                carla.command.SetAutopilot(carla.command.FutureActor, True, tm.get_port())))
        results = self.client.apply_batch_sync(batch, False)
        spawned_ids = []
        for r in results:
            if not r.error:
                self._vehicle_actor_ids.append(r.actor_id)
                spawned_ids.append(r.actor_id)
        print(
            f"[Scenario04] Vehicles spawned: {len(spawned_ids)}/{len(points)}"
        )

    def _force_green_light(self, ego, sim_time):
        if ego and ego.is_at_traffic_light():
            tl = ego.get_traffic_light()
            if tl:
                tl.set_state(carla.TrafficLightState.Green)
                tl.set_green_time(HERO_GREEN_LIGHT_HOLD_SECONDS)

    def _spawn_pedestrians(self, ego_transform=None):
        walker_controller_bp = self.world.get_blueprint_library().find("controller.ai.walker")
        walker_batch = []
        pedestrian_routes = []
        used_locations = []
        used_blueprint_ids = set()
        skipped_visible_count = 0
        skipped_no_target_count = 0
        # self.logger.info(f"_spawn_pedestrians called; ego_transform={ego_transform}")

        for candidate_index, spawn_location in enumerate(PEDESTRIAN_START_LOCATIONS):
            if len(pedestrian_routes) >= PEDESTRIAN_COUNT:
                break

            if not is_transform_hidden_from_hero(
                carla.Transform(spawn_location),
                ego_transform,
                PEDESTRIAN_MIN_HIDDEN_DISTANCE,
                PEDESTRIAN_MAX_HIDDEN_DISTANCE,
            ):
                print(f"[Scenario04] WARNUNG: Startpunkt sichtbar, überspringe: {spawn_location}")
                skipped_visible_count += 1
                continue

            target_location = self._pick_hidden_navigation_location(
                ego_transform,
                used_locations + [spawn_location],
                PEDESTRIAN_MIN_HIDDEN_DISTANCE,
                PEDESTRIAN_MAX_HIDDEN_DISTANCE,
            )
            if target_location is None:
                print(f"[Scenario04] WARNUNG: Kein Hidden-Ziel gefunden für Startpunkt #{candidate_index + 1}; überspringe ihn.")
                skipped_no_target_count += 1
                continue

            # nav_spawn_location = self._project_location_to_navigation(spawn_location)
            # if nav_spawn_location != spawn_location:
            #     print(
            #         f"[Scenario04] INFO: Startpunkt auf Navigation projiziert: "
            #         f"({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f}) -> "
            #         f"({nav_spawn_location.x:.2f}, {nav_spawn_location.y:.2f}, {nav_spawn_location.z:.2f})"
            #     )
            # spawn_location = nav_spawn_location

            walker_bp = self._get_random_pedestrian_blueprint(used_blueprint_ids)
            used_blueprint_ids.add(walker_bp.id)

            used_locations.append(spawn_location)
            # self.logger.info(f"selected spawn_location={spawn_location} target={target_location}")
            walker_batch.append(carla.command.SpawnActor(walker_bp, carla.Transform(spawn_location)))
            pedestrian_routes.append({
                "spawn_location": spawn_location,
                "target_location": target_location,
                "current_target_location": target_location,
                "heading_to_target": True,
                "done": False,
                "max_speed": self._get_random_pedestrian_speed(),
            })

        print(
            f"[Scenario04] Pedestrian-Startpunkte: total={len(PEDESTRIAN_START_LOCATIONS)}, "
            f"used={len(pedestrian_routes)}, skipped={skipped_visible_count + skipped_no_target_count} "
            f"(visible={skipped_visible_count}, no_target={skipped_no_target_count})"
        )
        walker_results = self.client.apply_batch_sync(walker_batch, False)

        spawned_walkers = []
        collision_count = 0
        for index, result in enumerate(walker_results):
            if result.error:
                collision_count += 1
                route = pedestrian_routes[index]
                spawn_location = route["spawn_location"]
                print(
                    f"[Scenario04] WARNUNG: Pedestrian konnte nicht gespawnt werden: {result.error} | "
                    f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
                )
                continue
            spawned_walkers.append((result.actor_id, pedestrian_routes[index]))

        controller_batch = []
        for walker_id, _ in spawned_walkers:
            controller_batch.append(carla.command.SpawnActor(walker_controller_bp, carla.Transform(), walker_id))

        controller_results = self.client.apply_batch_sync(controller_batch, False)

        successful_routes = []
        controller_index = 0
        for walker_id, route in spawned_walkers:
            if controller_index >= len(controller_results):
                break
            controller_result = controller_results[controller_index]
            controller_index += 1
            if controller_result.error:
                print(f"[Scenario04] WARNUNG: Pedestrian-Controller konnte nicht gespawnt werden: {controller_result.error}")
                continue

            route["walker_id"] = walker_id
            route["controller_id"] = controller_result.actor_id
            successful_routes.append(route)
            self._walker_actor_ids.append(walker_id)
            self._walker_controller_ids.append(controller_result.actor_id)

        print(
            f"[Scenario04] Pedestrian-Spawn-Resultat: success={len(successful_routes)}, "
            f"collision={collision_count}, skipped={skipped_visible_count + skipped_no_target_count} "
            f"(visible={skipped_visible_count}, no_target={skipped_no_target_count})"
        )

        self._pedestrian_routes = successful_routes
        self._pedestrian_spawn_time = self.world.get_snapshot().timestamp.elapsed_seconds
        self._pedestrians_spawned = True
        self._pedestrians_started = False
        self._pedestrians_done = len(self._pedestrian_routes) == 0
        self._pedestrians_phase_done = True

    def _start_pedestrians(self):
        if not self._pedestrian_routes:
            self._pedestrians_done = True
            return

        for route in self._pedestrian_routes:
            walker = self.world.get_actor(route.get("walker_id"))
            controller = self.world.get_actor(route.get("controller_id"))
            if walker is None or controller is None:
                route["done"] = True
                continue

            controller.start()
            route["heading_to_target"] = True
            route["current_target_location"] = route["target_location"]
            controller.go_to_location(route["current_target_location"])
            controller.set_max_speed(route.get("max_speed", PEDESTRIAN_MAX_SPEED))
            print(f"[Scenario04] Pedestrian {walker.id} ist jetzt unterwegs mit speed={route.get('max_speed', PEDESTRIAN_MAX_SPEED):.1f}.")

        self._pedestrians_started = True

    def _start_song(self, sim_time):
        if self._song_started:
            return
        self._song_started = True
        self._song_start_time = sim_time
        print(f"[Scenario04] Song started at sim_time={sim_time:.2f}s")
        if not self._play_song(sim_time):
            print("[Scenario04] WARNUNG: Song konnte nicht gestartet werden; fahre ohne Song fort.")
            self._song_finished = True
            self._song_finish_time = sim_time

    def _play_song(self, sim_time):
        return self._song_audio.play(sim_time)

    def _update_song(self, sim_time):
        if not self._song_started or self._song_finished:
            return

        if self._song_start_time is None:
            self._song_start_time = sim_time

        self._song_audio.update(sim_time)

        if self._song_audio.is_finished:
            self._song_finished = True
            self._song_finish_time = sim_time
            print(f"[Scenario04] Song finished at sim_time={sim_time:.2f}s")

    def _update_pedestrians(self, sim_time):
        if self._pedestrians_done:
            return

        if not self._pedestrians_spawned:
            return

        if not self._pedestrians_started:
            self._start_pedestrians()
            return

        group_timed_out = self._pedestrian_spawn_time is not None and (sim_time - self._pedestrian_spawn_time) > PEDESTRIAN_WAIT_TIMEOUT_S
        if group_timed_out:
            print("[Scenario04] Pedestrian Timeout.")           # doesn't delete them, just makes sure the pedestrian phase is at least that long
            for route in self._pedestrian_routes:
                route["done"] = True
            self._pedestrians_done = True
            return

        all_done = True
        for route in self._pedestrian_routes:
            if route.get("done"):
                continue

            walker = self.world.get_actor(route.get("walker_id"))
            if walker is None:
                route["done"] = True
                continue

            loc = walker.get_location()
            target_location = route.get("current_target_location", route["target_location"])
            distance = ((loc.x - target_location.x) ** 2 + (loc.y - target_location.y) ** 2 + (loc.z - target_location.z) ** 2) ** 0.5
            if distance <= PEDESTRIAN_ARRIVE_THRESH:
                if route.get("heading_to_target", True):
                    next_target = route["spawn_location"]
                    route["heading_to_target"] = False
                else:
                    next_target = route["target_location"]
                    route["heading_to_target"] = True
                route["current_target_location"] = next_target
                controller = self.world.get_actor(route.get("controller_id"))
                if controller is not None:
                    controller.go_to_location(next_target)
                print(f"[Scenario04] Pedestrian {walker.id} wechselt Richtung.")
            else:
                all_done = False

        self._pedestrians_done = False
        return all_done

    def _should_spawn_pedestrians(self, sim_time):
        return self._cars_phase_done and not self._pedestrians_spawned and (sim_time - self._traffic_spawn_time) >= CAR_TO_PED_DELAY_SECONDS

    def _should_start_song(self, sim_time):
        return self._pedestrians_phase_done and not self._song_started and (sim_time - self._pedestrian_spawn_time) >= PED_TO_SONG_DELAY_SECONDS

    def _should_end_scenario(self, sim_time):
        return self._song_finished and self._song_finish_time is not None and (sim_time - self._song_finish_time) >= SONG_TO_END_DELAY_SECONDS

    def run(self):
        print("[Scenario04] Running...")
        self._spawn_static_prop_once()
        try:
            while True:
                self.world.wait_for_tick()
                snapshot = self.world.get_snapshot()
                sim_time = snapshot.timestamp.elapsed_seconds
                if self._start_sim_time is None: self._start_sim_time = sim_time
                
                ego = self.find_hero()
                # Falls kein Hero gefunden wurde, nehmen wir die feste Fahrzeugpose an
                ego_transform = ego.get_transform() if ego else carla.Transform(
                    carla.Location(x=150.60, y=-173.30, z=0.70),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                )
                
                elapsed = sim_time - self._start_sim_time
                if not self._traffic_spawned and elapsed >= TRAFFIC_SPAWN_DELAY_SECONDS:
                    self._spawn_dynamic_traffic(ego_transform, sim_time)
                    self._traffic_spawned = True
                    self._traffic_spawn_time = sim_time
                
                if self._traffic_spawned and not self._vehicles_cleared:
                    if VEHICLE_ACTIVE_SECONDS > 0 and (sim_time - self._traffic_spawn_time) >= VEHICLE_ACTIVE_SECONDS:
                        destroyed_count = len(self._vehicle_actor_ids)
                        print(
                            f"[Scenario04] Destroying vehicles at sim_time={sim_time:.2f}s after "
                            f"{sim_time - self._traffic_spawn_time:.2f}s active time: count={destroyed_count}"
                        )
                        self.client.apply_batch([carla.command.DestroyActor(x) for x in self._vehicle_actor_ids])
                        self._vehicle_actor_ids = []
                        self._vehicles_cleared = True
                    elif VEHICLE_ACTIVE_SECONDS <= 0 and self._traffic_spawned and not self._vehicles_cleared:
                        print(
                            f"[Scenario04] Vehicle lifetime is infinite (VEHICLE_ACTIVE_SECONDS={VEHICLE_ACTIVE_SECONDS}); "
                            f"keeping {len(self._vehicle_actor_ids)} vehicles active."
                        )
                        self._vehicles_cleared = True

                if ENABLE_ROUTE_PEDESTRIANS:
                    if self._should_spawn_pedestrians(sim_time):
                        self._spawn_pedestrians(ego_transform)
                    else:
                        self._update_pedestrians(sim_time)

                    if self._pedestrians_spawned and not self._song_started and self._should_start_song(sim_time):
                        self._start_song(sim_time)

                    self._update_song(sim_time)

                    if self._should_end_scenario(sim_time):
                        self._scenario_done = True

                    if self._scenario_done:
                        return
                
                if ego:
                    self._force_green_light(ego, sim_time)
                time.sleep(SIM_STEP_S)
        except KeyboardInterrupt:
            pass
        finally:
            self.destroy()
            self._signal_done()

    def destroy(self):
        print("[Scenario04] Cleanup...")
        all_ids = self._static_actor_ids + self._vehicle_actor_ids + self._walker_actor_ids + self._walker_controller_ids
        self.client.apply_batch([carla.command.DestroyActor(x) for x in all_ids])

    def _signal_done(self):
        if not self._done_file:
            return
        try:
            done_dir = os.path.dirname(self._done_file)
            if done_dir:
                os.makedirs(done_dir, exist_ok=True)
            with open(self._done_file, 'w', encoding='utf-8') as done_handle:
                done_handle.write('done\n')
        except Exception as exc:
            print(f"[Scenario04] WARNING: could not write done signal file: {exc}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=2000, type=int)
    parser.add_argument('--tm-port', default=8000, type=int)
    parser.add_argument('--done-file', default=None)
    args = parser.parse_args()
    Scenario04Runner(args.host, args.port, args.tm_port, args.done_file).run()
