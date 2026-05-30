#!/usr/bin/env python

import argparse
import os
import math
import random
import sys
import time

import carla
try:
    from common.audio_paths import SURPRISE_RP_LITTLE_NUMBERS_PATH
    from generate_audio import RepeatingAudio, SongAudio
except ModuleNotFoundError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    extensions_root = os.path.normpath(os.path.join(current_dir, ".."))
    if extensions_root not in sys.path:
        sys.path.insert(0, extensions_root)
    from common.audio_paths import SURPRISE_RP_LITTLE_NUMBERS_PATH
    from generate_audio import RepeatingAudio, SongAudio

try:
    from scenario_helper import is_transform_hidden_from_hero
except ModuleNotFoundError:
    from scenario_events.scenario_helper import is_transform_hidden_from_hero

try:
    from events_scenario06_static_props import HIGHPED_ROUTE_CONFIGS, SANIMAL_ROUTE_CONFIGS, get_highped_barrier_spawns, get_start_fence_spawns
except ModuleNotFoundError:
    from scenario_events.events_scenario06_static_props import HIGHPED_ROUTE_CONFIGS, SANIMAL_ROUTE_CONFIGS, get_highped_barrier_spawns, get_start_fence_spawns


START_TO_CAR_DELAY = 1.0
CAR_TO_RAIN_DELAY = 1.0
MID_RAIN_LEAD_IN_S = 1.0
HARD_RAIN_DURATION_S = 1.0
MID_RAIN_FOLLOW_UP_S = 1.0
SOFT_RAIN_DURATION_S = 1.0

RAIN_TO_HIGHPED_DELAY = 1.0
HIGHPED_TO_BUS_DELAY = 1.0
BUS_TO_SONG_DELAY = 20.0
SONG_TO_SANIMAL_DELAY = 1.0
SANIMAL_TO_COW_DELAY = 1.0
COW_TO_FUEL_DELAY = 1.0
FUEL_TO_END_DELAY = 1.0

SONG_START_OFFSET_SECONDS = 0.0
SONG_PLAY_DURATION_SECONDS = 10.0
SONG_FADE_IN_MS = 3000
SONG_FADE_OUT_MS = 3000
FUEL_EMPTY_CHIME_PATH = r"C:\C_CARLA\CARLA_extensions\audio\car_low_fuel_chime.wav"


HIGHPED_BLUEPRINT_ID = "walker.pedestrian.0038"
HIGHPED_MAX_SPEED = 1.0
HIGHPED_ARRIVE_THRESH = 1.0
HIGHPED_STOP_AT_TARGET_DURATION = 1.0
HIGHPED_LIFETIME_S = 1.0

SANIMAL_BLUEPRINT_ID = "walker.pedestrian.0055"
SANIMAL_MAX_SPEED = 1.0 # 0.5
SANIMAL_ARRIVE_THRESH = 1.0
SANIMAL_STOP_AT_TARGET_DURATION = 1.0
SANIMAL_LIFETIME_S = 20.0

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

TRIGGER_TRAFFIC =False
TRIGGER_WEATHER = True
TRIGGER_HIGHPED = True
TRIGGER_BUS = True
TRIGGER_SONG = False
TRIGGER_SANIMAL = True
TRIGGER_COW = False
TRIGGER_FUELEMPTY = True
TRIGGER_SANIMAL_IMMEDIATE = False


def get_actor_blueprints(world, filter_pattern):
    bps = list(world.get_blueprint_library().filter(filter_pattern))
    if not bps:
        print(f"[Scenario06] WARNUNG: Keine Blueprints für {filter_pattern} gefunden!")
    return bps


def filter_blocked_vehicle_blueprints(blueprints, blocked_keywords):
    return [bp for bp in blueprints if not any(k in bp.id.lower() for k in blocked_keywords)]


class Scenario06Runner:
    def __init__(self, host, port, tm_port, done_file=None, trigger_traffic=True, trigger_weather=True, trigger_highped=True, trigger_bus=True, trigger_song=True, trigger_sanimal=True, trigger_cow=True, trigger_fuelempty=True):
        self.client = carla.Client(host, port)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()
        self._tm_port = tm_port
        self._done_file = done_file
        self._rng = random.Random()
        self._trigger_traffic = trigger_traffic
        self._trigger_weather = trigger_weather
        self._trigger_highped = trigger_highped
        self._trigger_bus = trigger_bus
        self._trigger_song = trigger_song
        self._trigger_sanimal = trigger_sanimal
        self._trigger_cow = trigger_cow
        self._trigger_fuelempty = trigger_fuelempty
        self._highped_skip_applied = False
        self._highped_barrier_triggered_keys = set()
        self._highped_barrier_actor_ids = []
        self._sanimal_trigger_forced = False
        self._start_static_props_spawned = False

        self._start_sim_time = None
        self._traffic_spawned = False
        self._traffic_spawn_time = None
        self._cars_phase_done = False
        self._scenario_done = False
        self._weather_start_value = None
        self._weather_phase = "idle"
        self._weather_phase_start_time = None
        self._song_audio = SongAudio(
            SURPRISE_RP_LITTLE_NUMBERS_PATH,
            start_seconds=SONG_START_OFFSET_SECONDS,
            play_seconds=SONG_PLAY_DURATION_SECONDS,
            fade_in_ms=SONG_FADE_IN_MS,
            fade_out_ms=SONG_FADE_OUT_MS,
            volume=0.85,
            channel_index=6,
        )
        self._fuel_empty_audio = RepeatingAudio(
            FUEL_EMPTY_CHIME_PATH,
            repeat_count=5,
            volume=0.85,
            channel_index=7,
        )

        self._highped_route_done = False
        self._highped_route_active = False
        self._highped_route_config = None
        self._highped_walker_id = None
        self._highped_spawn_time = None
        self._highped_last_update_time = None
        self._highped_arrival_time = None
        self._highped_route_forward = True
        self.highped_finished = False
        self.bus_finished = False
        self.song_finished = False

        self._sanimal_route_done = False
        self._sanimal_route_active = False
        self._sanimal_route_config = None
        self._sanimal_walker_id = None
        self._sanimal_spawn_time = None
        self._sanimal_last_update_time = None
        self._sanimal_arrival_time = None
        self._sanimal_route_forward = True
        self.sanimal_finished = False
        self.cow_finished = False
        self.fuelempty_started = False
        self.fuelempty_finished = False
        self._delay_states = {
            "car_to_rain": {
                "delay": CAR_TO_RAIN_DELAY,
                "started_at": None,
                "finished": False,
            },
            "rain_to_highped": {
                "delay": RAIN_TO_HIGHPED_DELAY,
                "started_at": None,
                "finished": False,
            },
            "highped_to_bus": {
                "delay": HIGHPED_TO_BUS_DELAY,
                "started_at": None,
                "finished": False,
            },
            "bus_to_song": {
                "delay": BUS_TO_SONG_DELAY,
                "started_at": None,
                "finished": False,
            },
            "song_to_sanimal": {
                "delay": SONG_TO_SANIMAL_DELAY,
                "started_at": None,
                "finished": False,
            },
            "sanimal_to_cow": {
                "delay": SANIMAL_TO_COW_DELAY,
                "started_at": None,
                "finished": False,
            },
            "cow_to_fuel": {
                "delay": COW_TO_FUEL_DELAY,
                "started_at": None,
                "finished": False,
            },
            "fuel_to_end": {
                "delay": FUEL_TO_END_DELAY,
                "started_at": None,
                "finished": False,
            }
        }

        self._static_actor_ids = []
        self._persistent_static_actor_ids = []
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

    def _get_route_config(self, route_configs, hero_location, hero_velocity=None):
        for route_config in route_configs:
            trigger_location = route_config["trigger_location"]
            if abs(hero_location.x - trigger_location.x) > route_config["trigger_x_tolerance"]:
                continue
            if abs(hero_location.y - trigger_location.y) > route_config["trigger_y_tolerance"]:
                continue

            required_axis = route_config.get("trigger_direction_axis")
            required_sign = route_config.get("trigger_direction_sign")
            if required_axis is not None and required_sign is not None:
                if hero_velocity is None:
                    continue

                velocity_x = hero_velocity.x
                velocity_y = hero_velocity.y
                speed = math.hypot(velocity_x, velocity_y)
                if speed < 0.5:
                    continue

                if required_axis == "x":
                    axis_component = velocity_x
                    cross_component = velocity_y
                elif required_axis == "y":
                    axis_component = velocity_y
                    cross_component = velocity_x
                else:
                    continue

                if axis_component * required_sign <= 0.0:
                    continue
                if abs(axis_component) < abs(cross_component):
                    continue

            return route_config
        return None

    def _get_highped_route_config(self, hero_location):
        return self._get_route_config(HIGHPED_ROUTE_CONFIGS, hero_location)

    def _get_sanimal_route_config(self, hero_location, hero_velocity=None):
        return self._get_route_config(SANIMAL_ROUTE_CONFIGS, hero_location, hero_velocity)

    def _spawn_highped(self, route_config, sim_time):
        if self._highped_route_done or self._highped_route_active:
            return False

        self._cleanup_highped_barrier_props()

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
        self.highped_finished = False
        self._delay_states["highped_to_bus"]["started_at"] = None
        self._delay_states["highped_to_bus"]["finished"] = False
        self._walker_actor_ids.append(walker.id)

        print(
            f"[Scenario06] HighPed spawned: id={walker.id}, route={route_config['name']}, sim_time={sim_time:.2f}s, "
            f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
        )
        return True

    def _finish_highped_route(self, walker, sim_time):
        if walker is not None:
            try:
                walker.destroy()
            except Exception:
                pass

        self._cleanup_highped_barrier_props()

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
        self.highped_finished = True
        print("[Scenario06] HighPed route finished. Continuing with HIGHPED_TO_BUS_DELAY.")

    def _spawn_sanimal(self, route_config, sim_time):
        if self._sanimal_route_done or self._sanimal_route_active:
            return False

        walker_bp = self.world.get_blueprint_library().find(SANIMAL_BLUEPRINT_ID)
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
                f"[Scenario06] WARNUNG: SANIMAL konnte nicht gespawnt werden | sim_time={sim_time:.2f}s | "
                f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
            )
            return False

        self._sanimal_route_active = True
        self._sanimal_route_config = route_config
        self._sanimal_walker_id = walker.id
        self._sanimal_spawn_time = sim_time
        self._sanimal_last_update_time = sim_time
        self._sanimal_arrival_time = None
        self._sanimal_route_forward = True
        self.sanimal_finished = False
        self._delay_states["sanimal_to_cow"]["started_at"] = None
        self._delay_states["sanimal_to_cow"]["finished"] = False
        self._walker_actor_ids.append(walker.id)

        print(
            f"[Scenario06] SANIMAL spawned: id={walker.id}, route={route_config['name']}, sim_time={sim_time:.2f}s, "
            f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
        )
        return True

    def _finish_sanimal_route(self, walker, sim_time):
        if walker is not None:
            try:
                walker.destroy()
            except Exception:
                pass

        if self._sanimal_walker_id in self._walker_actor_ids:
            self._walker_actor_ids.remove(self._sanimal_walker_id)

        self._sanimal_route_active = False
        self._sanimal_route_done = True
        self._sanimal_route_config = None
        self._sanimal_walker_id = None
        self._sanimal_spawn_time = None
        self._sanimal_last_update_time = None
        self._sanimal_arrival_time = None
        self._sanimal_route_forward = True
        self.sanimal_finished = True
        print("[Scenario06] SANIMAL route finished. Continuing with SANIMAL_TO_COW_DELAY.")

    def _start_delay_timer(self, delay_name, sim_time):
        delay_state = self._delay_states.get(delay_name)
        if delay_state is None:
            return

        delay_state["started_at"] = sim_time
        delay_state["finished"] = False

    def _finish_delay_timer(self, delay_name, sim_time):
        delay_state = self._delay_states.get(delay_name)
        if delay_state is None:
            return

        if delay_state["started_at"] is None:
            delay_state["started_at"] = sim_time
        delay_state["finished"] = True

    def _update_delay_timer(self, delay_name, sim_time):
        delay_state = self._delay_states.get(delay_name)
        if delay_state is None or delay_state["finished"]:
            return

        if delay_state["started_at"] is None:
            delay_state["started_at"] = sim_time
            return

        if (sim_time - delay_state["started_at"]) >= delay_state["delay"]:
            delay_state["finished"] = True
            print(f"{delay_name} delay finished!")

    def _start_bus_trigger(self):
        print("Bus is starting now")
        self.bus_finished = True

    def _start_song_trigger(self):
        if self._song_audio.play(self.world.get_snapshot().timestamp.elapsed_seconds):
            print("spielt song")
        else:
            print("[Scenario06] WARNUNG: Song konnte nicht gestartet werden.")
        self.song_finished = True

    def _start_cow_trigger(self):
        print("start cows now")
        self.cow_finished = True

    def _start_fuelempty_trigger(self):
        if not self._fuel_empty_audio.play():
            print("[Scenario06] WARNUNG: Fuel empty sound konnte nicht gestartet werden.")
            self.fuelempty_started = True
            self.fuelempty_finished = True
            return

        print("start fuel empty sound now")
        self.fuelempty_started = True
        self.fuelempty_finished = False

    def _update_fuelempty_audio(self):
        if not self.fuelempty_started or self.fuelempty_finished:
            return

        self._fuel_empty_audio.update()
        if self._fuel_empty_audio.is_finished:
            self.fuelempty_finished = True

    def _update_song(self, sim_time):
        self._song_audio.update(sim_time)

    def _skip_traffic_trigger(self, sim_time):
        if self._traffic_spawned:
            return

        self._traffic_spawned = True
        self._traffic_spawn_time = sim_time
        self._cars_phase_done = True
        self._finish_delay_timer("car_to_rain", sim_time)
        print("[Scenario06] Traffic trigger skipped.")

    def _skip_weather_trigger(self, sim_time):
        if self._weather_phase == "restored":
            return

        if self._weather_start_value is None:
            self._weather_start_value = self.world.get_weather()
        self.world.set_weather(self._weather_start_value)
        self._weather_phase = "restored"
        self._weather_phase_start_time = sim_time
        self._finish_delay_timer("rain_to_highped", sim_time)
        print("[Scenario06] Weather trigger skipped.")

    def _skip_highped_trigger(self, sim_time):
        if self.highped_finished or self._highped_skip_applied:
            return

        self._cleanup_highped_barrier_props()
        self._highped_route_done = True
        self._highped_route_active = False
        self.highped_finished = True
        self._highped_skip_applied = True
        self._finish_delay_timer("highped_to_bus", sim_time)
        print("[Scenario06] HighPed trigger skipped.")

    def _skip_bus_trigger(self, sim_time):
        if self.bus_finished:
            return

        self._finish_delay_timer("bus_to_song", sim_time)
        self._start_bus_trigger()
        print("[Scenario06] Bus trigger skipped.")

    def _skip_song_trigger(self, sim_time):
        if self.song_finished:
            return

        print("[Scenario06] Song trigger skipped.")
        self._finish_delay_timer("song_to_sanimal", sim_time)
        self.song_finished = True

    def _skip_sanimal_trigger(self, sim_time):
        if self.sanimal_finished:
            return

        self._sanimal_route_done = True
        self._sanimal_route_active = False
        self.sanimal_finished = True
        self._finish_delay_timer("sanimal_to_cow", sim_time)
        print("[Scenario06] SANIMAL trigger skipped.")

    def _skip_cow_trigger(self, sim_time):
        if self.cow_finished:
            return

        self.cow_finished = True
        self._finish_delay_timer("cow_to_fuel", sim_time)
        print("[Scenario06] Cow trigger skipped.")

    def _skip_fuelempty_trigger(self, sim_time):
        if self.fuelempty_started and self.fuelempty_finished:
            return

        self.fuelempty_started = True
        self.fuelempty_finished = True
        self._finish_delay_timer("fuel_to_end", sim_time)
        print("[Scenario06] Fuel empty trigger skipped.")

    def _force_sanimal_trigger(self, sim_time):
        if self.sanimal_finished or self._sanimal_route_active or self._sanimal_trigger_forced:
            return

        self._finish_delay_timer("song_to_sanimal", sim_time)
        self._sanimal_trigger_forced = True
        print("[Scenario06] SANIMAL trigger forced to start immediately.")

    def _spawn_sanimal_forced(self, sim_time):
        if self._sanimal_route_done or self._sanimal_route_active:
            return

        route_config = None
        ego = self.find_hero()
        if ego is not None:
            route_config = self._get_sanimal_route_config(ego.get_location(), ego.get_velocity())

        if route_config is None and SANIMAL_ROUTE_CONFIGS:
            route_config = SANIMAL_ROUTE_CONFIGS[0]

        if route_config is None:
            print("[Scenario06] WARNUNG: SANIMAL route config not available for forced spawn.")
            return

        self._spawn_sanimal(route_config, sim_time)

    def _spawn_start_static_props(self):
        if self._start_static_props_spawned:
            return True

        bp_lib = self.world.get_blueprint_library()
        spawn_configs = get_start_fence_spawns()
        spawned_count = 0
        failed_configs = []

        for prop_config in spawn_configs:
            name = prop_config.get("name", "unknown_prop")
            blueprint_id = prop_config.get("blueprints", [None])[0]
            if not blueprint_id:
                print(f"[Scenario06] Start-Props WARNUNG: '{name}' hat keine Blueprint-ID.")
                failed_configs.append(name)
                continue

            transform = prop_config.get("transform")
            location = transform.location if transform is not None else None
            rotation = transform.rotation if transform is not None else None
            matches = [bp.id for bp in bp_lib.filter(blueprint_id)]
            print(
                f"[Scenario06] Start-Props versuche '{name}' blueprint='{blueprint_id}' "
                f"matches={matches} "
                f"loc=({location.x:.2f}, {location.y:.2f}, {location.z:.2f}) "
                f"rot=({rotation.pitch:.1f}, {rotation.yaw:.1f}, {rotation.roll:.1f})"
                if location is not None and rotation is not None
                else f"[Scenario06] Start-Props versuche '{name}' blueprint='{blueprint_id}' matches={matches}"
            )

            try:
                prop_bp = bp_lib.find(blueprint_id)
                print(f"[Scenario06] Start-Props Blueprint gefunden für '{name}': {prop_bp.id}")
            except Exception as exc:
                print(f"[Scenario06] Start-Props WARNUNG: Blueprint '{blueprint_id}' für '{name}' nicht gefunden: {exc}")
                failed_configs.append(name)
                continue

            actor = self.world.try_spawn_actor(prop_bp, transform)
            if actor is None:
                print(
                    f"[Scenario06] Start-Props WARNUNG: Spawn für '{name}' fehlgeschlagen. "
                    f"Wahrscheinliche Ursache: Collision / ungültiger Transform. "
                    f"blueprint='{prop_bp.id}'"
                )
                failed_configs.append(name)
                continue

            self._persistent_static_actor_ids.append(actor.id)
            spawned_count += 1
            print(f"[Scenario06] Start-Props OK: '{name}' actor_id={actor.id} blueprint='{prop_bp.id}' persistent=True")

        self._start_static_props_spawned = True
        if spawned_count == len(spawn_configs):
            print(f"[Scenario06] Start-Props: {spawned_count}/{len(spawn_configs)} gespawnt.")
        else:
            print(
                f"[Scenario06] Start-Props: {spawned_count}/{len(spawn_configs)} gespawnt, "
                f"nicht alle konnten gesetzt werden. Fehlschläge={failed_configs}"
            )
        return spawned_count == len(spawn_configs)

    def _get_highped_barrier_config(self, hero_location):
        return self._get_route_config(get_highped_barrier_spawns(), hero_location)

    def _spawn_highped_barrier_props(self, barrier_config):
        barrier_name = barrier_config.get("name", "highped_barrier")
        if barrier_name in self._highped_barrier_triggered_keys:
            return False

        bp_lib = self.world.get_blueprint_library()
        spawn_configs = barrier_config.get("spawn_configs", [])
        spawned_count = 0
        failed_configs = []

        for prop_config in spawn_configs:
            name = prop_config.get("name", "unknown_prop")
            blueprint_id = prop_config.get("blueprints", [None])[0]
            if not blueprint_id:
                failed_configs.append(name)
                continue

            try:
                prop_bp = bp_lib.find(blueprint_id)
            except Exception as exc:
                print(f"[Scenario06] Barrier-Props WARNUNG: Blueprint '{blueprint_id}' für '{name}' nicht gefunden: {exc}")
                failed_configs.append(name)
                continue

            actor = self.world.try_spawn_actor(prop_bp, prop_config.get("transform"))
            if actor is None:
                print(f"[Scenario06] Barrier-Props WARNUNG: Spawn für '{name}' fehlgeschlagen | blueprint='{prop_bp.id}'")
                failed_configs.append(name)
                continue

            self._static_actor_ids.append(actor.id)
            self._highped_barrier_actor_ids.append(actor.id)
            spawned_count += 1
            print(f"[Scenario06] Barrier-Props OK: '{name}' actor_id={actor.id} blueprint='{prop_bp.id}'")

        self._highped_barrier_triggered_keys.add(barrier_name)
        if spawned_count == len(spawn_configs):
            print(f"[Scenario06] HighPed-Barrier: {spawned_count}/{len(spawn_configs)} gespawnt.")
        else:
            print(
                f"[Scenario06] HighPed-Barrier: {spawned_count}/{len(spawn_configs)} gespawnt, "
                f"Fehlschläge={failed_configs}"
            )
        return spawned_count > 0

    def _cleanup_highped_barrier_props(self):
        if not self._highped_barrier_actor_ids:
            self._highped_barrier_triggered_keys.clear()
            return

        for actor_id in list(self._highped_barrier_actor_ids):
            actor = self.world.get_actor(actor_id)
            if actor is not None:
                try:
                    actor.destroy()
                except Exception:
                    pass
            if actor_id in self._static_actor_ids:
                self._static_actor_ids.remove(actor_id)

        self._highped_barrier_actor_ids = []
        self._highped_barrier_triggered_keys.clear()
        print("[Scenario06] HighPed barrier props removed.")

    def _update_bus_trigger(self):
        delay_state = self._delay_states.get("highped_to_bus")
        return delay_state is not None and delay_state["finished"]

    def _update_highped_route(self, sim_time):
        if not self._highped_route_active or self._highped_route_config is None or self._highped_walker_id is None:
            return

        walker = self.world.get_actor(self._highped_walker_id)
        if walker is None:
            self._finish_highped_route(None, sim_time)
            return

        start_location = self._highped_route_config["spawn_location"]
        end_location = self._highped_route_config["target_location"]
        target_location = end_location if self._highped_route_forward else start_location
        current_location = walker.get_location()

        if self._highped_spawn_time is not None and (sim_time - self._highped_spawn_time) >= HIGHPED_LIFETIME_S:
            print(
                f"[Scenario06] HighPed lifetime reached: id={walker.id}, sim_time={sim_time:.2f}s, lifetime={HIGHPED_LIFETIME_S:.1f}s"
            )
            self._finish_highped_route(walker, sim_time)
            return

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

            if (sim_time - self._highped_arrival_time) >= HIGHPED_STOP_AT_TARGET_DURATION:
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
            self._finish_highped_route(walker, sim_time)

    def _update_sanimal_route(self, sim_time):
        if not self._sanimal_route_active or self._sanimal_route_config is None or self._sanimal_walker_id is None:
            return

        walker = self.world.get_actor(self._sanimal_walker_id)
        if walker is None:
            self._finish_sanimal_route(None, sim_time)
            return

        start_location = self._sanimal_route_config["spawn_location"]
        end_location = self._sanimal_route_config["target_location"]
        target_location = end_location if self._sanimal_route_forward else start_location
        current_location = walker.get_location()

        if self._sanimal_spawn_time is not None and (sim_time - self._sanimal_spawn_time) >= SANIMAL_LIFETIME_S:
            print(
                f"[Scenario06] SANIMAL lifetime reached: id={walker.id}, sim_time={sim_time:.2f}s, lifetime={SANIMAL_LIFETIME_S:.1f}s"
            )
            self._finish_sanimal_route(walker, sim_time)
            return

        if self._sanimal_last_update_time is None:
            delta_time = SIM_STEP_S
        else:
            delta_time = max(0.0, sim_time - self._sanimal_last_update_time)
            if delta_time == 0.0:
                delta_time = SIM_STEP_S
        self._sanimal_last_update_time = sim_time

        distance = self._distance_2d(current_location, target_location)
        if distance <= SANIMAL_ARRIVE_THRESH:
            if self._sanimal_arrival_time is None:
                self._sanimal_arrival_time = sim_time
                print(
                    f"[Scenario06] SANIMAL reached {'target' if self._sanimal_route_forward else 'start'}: id={walker.id}, sim_time={sim_time:.2f}s"
                )

            if (sim_time - self._sanimal_arrival_time) >= SANIMAL_STOP_AT_TARGET_DURATION:
                self._sanimal_route_forward = not self._sanimal_route_forward
                self._sanimal_arrival_time = None
            return

        max_step = SANIMAL_MAX_SPEED * delta_time
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
                    speed=SANIMAL_MAX_SPEED,
                    jump=False,
                )
            )
        except Exception as exc:
            print(f"[Scenario06] WARNUNG: SANIMAL konnte nicht manuell bewegt werden: {exc}")
            self._finish_sanimal_route(walker, sim_time)

    def _maybe_spawn_highped(self, ego_transform, sim_time):
        if ego_transform is None or self._highped_route_done or self._highped_route_active:
            return

        route_config = self._get_highped_route_config(ego_transform.location)
        if route_config is None:
            return

        self._spawn_highped(route_config, sim_time)

    def _maybe_spawn_sanimal(self, ego_transform, sim_time):
        if ego_transform is None or self._sanimal_route_done or self._sanimal_route_active:
            return

        hero = self.find_hero()
        hero_velocity = hero.get_velocity() if hero is not None else None
        route_config = self._get_sanimal_route_config(ego_transform.location, hero_velocity)
        if route_config is None:
            return

        self._spawn_sanimal(route_config, sim_time)

    def _should_spawn_traffic(self, sim_time):
        return (not self._traffic_spawned) and (sim_time - self._start_sim_time) >= START_TO_CAR_DELAY

    def _update_weather_cycle(self, sim_time):
        if self._start_sim_time is None:
            return

        if self._weather_phase == "idle":
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
                    self._spawn_start_static_props()

                ego = self.find_hero()
                ego_transform = ego.get_transform() if ego else carla.Transform(
                    carla.Location(x=150.60, y=-173.30, z=0.70),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                )

                if self._should_spawn_traffic(sim_time) and self._spawn_dynamic_traffic(ego_transform, sim_time):
                    self._traffic_spawned = True
                    self._traffic_spawn_time = sim_time

                if not self._trigger_traffic:
                    self._skip_traffic_trigger(sim_time)

                car_to_rain_state = self._delay_states["car_to_rain"]
                if self._traffic_spawned:
                    if car_to_rain_state["started_at"] is None:
                        self._start_delay_timer("car_to_rain", sim_time)
                    self._update_delay_timer("car_to_rain", sim_time)

                if car_to_rain_state["finished"]:
                    if not self._trigger_weather:
                        self._skip_weather_trigger(sim_time)
                    else:
                        self._update_weather_cycle(sim_time)

                rain_to_highped_state = self._delay_states["rain_to_highped"]
                if self._weather_phase == "restored":
                    if rain_to_highped_state["started_at"] is None:
                        self._start_delay_timer("rain_to_highped", sim_time)
                    self._update_delay_timer("rain_to_highped", sim_time)

                if not self._trigger_highped and rain_to_highped_state["finished"]:
                    self._skip_highped_trigger(sim_time)

                if ego and rain_to_highped_state["finished"] and not self._highped_route_done and not self._highped_route_active:
                    barrier_config = self._get_highped_barrier_config(ego_transform.location)
                    if barrier_config is not None:
                        self._spawn_highped_barrier_props(barrier_config)

                if ego and rain_to_highped_state["finished"]:
                    self._maybe_spawn_highped(ego_transform, sim_time)

                self._update_highped_route(sim_time)
                self._update_sanimal_route(sim_time)
                self._update_song(sim_time)
                self._update_fuelempty_audio()
                delay_state = self._delay_states["highped_to_bus"]
                if self.highped_finished:
                    if delay_state["started_at"] is None:
                        self._start_delay_timer("highped_to_bus", sim_time)
                    self._update_delay_timer("highped_to_bus", sim_time)

                if self.highped_finished and self._update_bus_trigger():
                    if not self._trigger_bus:
                        self._skip_bus_trigger(sim_time)
                    else:
                        self._start_bus_trigger()
                    self.highped_finished = False

                bus_to_song_state = self._delay_states["bus_to_song"]
                if self.bus_finished:
                    if bus_to_song_state["started_at"] is None:
                        self._start_delay_timer("bus_to_song", sim_time)
                    self._update_delay_timer("bus_to_song", sim_time)

                if self.bus_finished and bus_to_song_state["finished"] and not self.song_finished:
                    if not self._trigger_song:
                        self._skip_song_trigger(sim_time)
                    else:
                        self._start_song_trigger()

                song_to_sanimal_state = self._delay_states["song_to_sanimal"]
                if self.song_finished:
                    if song_to_sanimal_state["started_at"] is None:
                        self._start_delay_timer("song_to_sanimal", sim_time)
                    if self._trigger_sanimal and TRIGGER_SANIMAL_IMMEDIATE:
                        self._force_sanimal_trigger(sim_time)
                    else:
                        self._update_delay_timer("song_to_sanimal", sim_time)

                if not self._trigger_sanimal and self.song_finished and song_to_sanimal_state["finished"]:
                    self._skip_sanimal_trigger(sim_time)

                if self.song_finished and song_to_sanimal_state["finished"]:
                    if self._trigger_sanimal and TRIGGER_SANIMAL_IMMEDIATE:
                        self._spawn_sanimal_forced(sim_time)
                    else:
                        self._maybe_spawn_sanimal(ego_transform, sim_time)

                if self._traffic_spawned:
                    self._maintain_spawn_pools(ego_transform, sim_time)

                sanimal_to_cow_state = self._delay_states["sanimal_to_cow"]
                if self.sanimal_finished:
                    if sanimal_to_cow_state["started_at"] is None:
                        self._start_delay_timer("sanimal_to_cow", sim_time)
                    self._update_delay_timer("sanimal_to_cow", sim_time)

                if self.sanimal_finished and sanimal_to_cow_state["finished"] and not self.cow_finished:
                    if not self._trigger_cow:
                        self._skip_cow_trigger(sim_time)
                    else:
                        self._start_cow_trigger()

                cow_to_fuel_state = self._delay_states["cow_to_fuel"]
                if self.cow_finished:
                    if cow_to_fuel_state["started_at"] is None:
                        self._start_delay_timer("cow_to_fuel", sim_time)
                    self._update_delay_timer("cow_to_fuel", sim_time)

                if self.cow_finished and cow_to_fuel_state["finished"] and not self.fuelempty_started:
                    if not self._trigger_fuelempty:
                        self._skip_fuelempty_trigger(sim_time)
                    else:
                        self._start_fuelempty_trigger()

                fuel_to_end_state = self._delay_states["fuel_to_end"]
                if self.fuelempty_finished:
                    if fuel_to_end_state["started_at"] is None:
                        self._start_delay_timer("fuel_to_end", sim_time)
                    self._update_delay_timer("fuel_to_end", sim_time)

                if self.fuelempty_finished and fuel_to_end_state["finished"]:
                    self._scenario_done = True

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
        self._song_audio.stop(0)
        self._fuel_empty_audio.stop(0)
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
    Scenario06Runner(
        args.host,
        args.port,
        args.tm_port,
        args.done_file,
        trigger_traffic=TRIGGER_TRAFFIC,
        trigger_weather=TRIGGER_WEATHER,
        trigger_highped=TRIGGER_HIGHPED,
        trigger_bus=TRIGGER_BUS,
        trigger_song=TRIGGER_SONG,
        trigger_sanimal=TRIGGER_SANIMAL,
        trigger_cow=TRIGGER_COW,
        trigger_fuelempty=TRIGGER_FUELEMPTY,
    ).run()