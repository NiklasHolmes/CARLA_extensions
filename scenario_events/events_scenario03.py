
import argparse
import os
import math
import random
import sys
import time

import carla
from carla import VehicleLightState

try:
    from common.audio_paths import FEAR_RP_NEUROSIS_FEAR_AND_SICKNESS_PATH
    from generate_audio import SongAudio
except ModuleNotFoundError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    extensions_root = os.path.normpath(os.path.join(current_dir, ".."))
    if extensions_root not in sys.path:
        sys.path.insert(0, extensions_root)
    from common.audio_paths import FEAR_RP_NEUROSIS_FEAR_AND_SICKNESS_PATH
    from generate_audio import SongAudio

try:
    from scenario_helper import start_manual_control_process
except ModuleNotFoundError:
    from scenario_events.scenario_helper import start_manual_control_process

try:
    from scenario_helper import build_trigger_box_configs, draw_trigger_boxes
except ModuleNotFoundError:
    from scenario_events.scenario_helper import build_trigger_box_configs, draw_trigger_boxes

try:
    from events_scenario03_static_props import get_barrier_spawn, TEMP_BARRIER_FIRETRUCK, LTRUCK_SPAWN_CONFIGS, COPWAVING_TRIGGER_CONFIGS, CARAWAY
except ModuleNotFoundError:
    from scenario_events.events_scenario03_static_props import get_barrier_spawn, TEMP_BARRIER_FIRETRUCK, LTRUCK_SPAWN_CONFIGS, COPWAVING_TRIGGER_CONFIGS, CARAWAY

START_TO_CARAWAY_DELAY = 1.0
CARAWAY_TO_LTRUCK_DELAY = 1.0
LTRUCK_TO_SONG_DELAY = 2.0
SONG_TO_POLICE_DELAY = 1.0
POLICE_TO_BREAK_DELAY = 1.0
BREAK_TO_END_DELAY = 1.0

SONG_START_OFFSET_SECONDS = 0.0
SONG_PLAY_DURATION_SECONDS = 5.0
SONG_FADE_IN_MS = 3000
SONG_FADE_OUT_MS = 3000
SIM_STEP_S = 0.05
run_in_singleFile_mode = True

route_green = ["Straight", "Straight", "Straight", "Straight", "Straight", "Straight"]

# copWaving lifetime (seconds) before removal
COPWAVING_LIFETIME_S = 10.0
TRIGGER_CARAWAY = True
TRIGGER_LTRUCK = True
TRIGGER_SONG = False
TRIGGER_POLICE = True
TRIGGER_BREAK = True
DEBUG_MODE = True

# For testing: when True, ltruckTrigger 1 or 2 is considered triggered instantly
TEST_INSTANT_TRIGGER_LTRUCK = False
ltruck_spawn_idx = 0
TEST_INSTANT_TRIGGER_COP = False
cop_spawn_idx = 0

DELAY_LABELS = {
    "start_to_caraway": "caraway",
    "caraway_to_ltruck": "ltruck",
    "ltruck_to_song": "song",
    "song_to_police": "police",
    "police_to_break": "break",
    "break_to_end": "end",
}

class Scenario03Runner:
    def __init__(self, host, port, tm_port, done_file=None, trigger_caraway=True, trigger_ltruck=True, trigger_song=True, trigger_police=True, trigger_break=True):
        self.client = carla.Client(host, port)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()
        self.host = host
        self.port = port
        self._tm_port = tm_port
        self._done_file = done_file
        self._rng = random.Random()

        self._trigger_caraway = trigger_caraway
        self._trigger_ltruck = trigger_ltruck
        self._trigger_song = trigger_song
        self._trigger_police = trigger_police
        self._trigger_break = trigger_break

        self._start_sim_time = None
        self._scenario_done = False

        self.caraway_finished = False
        self.caraway_active = False
        self.ltruck_active = False
        self.ltruck_finished = False
        self.song_started = False
        self.song_finished = False
        self.police_finished = False
        self.police_active = False
        self.break_finished = False

        self._start_static_props_spawned = False
        self._persistent_static_actor_ids = []
        self._temp_firetruck_actor_ids = []
        self._temp_firetruck_trigger_config = TEMP_BARRIER_FIRETRUCK[0].get("trigger_1") if TEMP_BARRIER_FIRETRUCK else None
        self._temp_firetruck_trigger_active = False
        self._temp_firetruck_trigger_triggered = False

        self._ltruck_triggered_keys = set()
        self._caraway_triggered_keys = set()
        self._ltruck_process = None
        self._static_actor_ids = []
        self._vehicle_actor_ids = []
        self._caraway_vehicle_spawn_locations = {}
        self._caraway_vehicle_last_locations = {}
        self._caraway_vehicle_distances_m = {}
        self._debug_trigger_box_lifetime = SIM_STEP_S * 2.0

        # copWaving tracking
        self._copwaving_triggered_keys = set()
        self._copwaving_actor_ids = {}
        self._copwaving_spawn_time = {}

        self._delay_states = {
            "start_to_caraway": {
                "delay": START_TO_CARAWAY_DELAY,
                "started_at": None,
                "finished": False,
            },
            "caraway_to_ltruck": {
                "delay": CARAWAY_TO_LTRUCK_DELAY,
                "started_at": None,
                "finished": False,
            },
            "ltruck_to_song": {
                "delay": LTRUCK_TO_SONG_DELAY,
                "started_at": None,
                "finished": False,
            },
            "song_to_police": {
                "delay": SONG_TO_POLICE_DELAY,
                "started_at": None,
                "finished": False,
            },
            "police_to_break": {
                "delay": POLICE_TO_BREAK_DELAY,
                "started_at": None,
                "finished": False,
            },
            "break_to_end": {
                "delay": BREAK_TO_END_DELAY,
                "started_at": None,
                "finished": False,
            },
        }

        self._song_audio = SongAudio(
            FEAR_RP_NEUROSIS_FEAR_AND_SICKNESS_PATH,
            start_seconds=SONG_START_OFFSET_SECONDS,
            play_seconds=SONG_PLAY_DURATION_SECONDS,
            fade_in_ms=SONG_FADE_IN_MS,
            fade_out_ms=SONG_FADE_OUT_MS,
            volume=0.85,
            channel_index=6,
        )

    def _start_delay_timer(self, delay_name, sim_time):
        delay_state = self._delay_states.get(delay_name)
        if delay_state is None:
            return

        if delay_state["started_at"] is None:
            label = DELAY_LABELS.get(delay_name, delay_name)
            print(f"[Scenario03] {label} delay started!")

        delay_state["started_at"] = sim_time
        delay_state["finished"] = False

    def _finish_delay_timer(self, delay_name, sim_time):
        delay_state = self._delay_states.get(delay_name)
        if delay_state is None:
            return

        if delay_state["started_at"] is None:
            delay_state["started_at"] = sim_time
        delay_state["finished"] = True
        label = DELAY_LABELS.get(delay_name, delay_name)
        print(f"[Scenario03] {label} delay endet!")

    def _update_delay_timer(self, delay_name, sim_time):
        delay_state = self._delay_states.get(delay_name)
        if delay_state is None or delay_state["finished"]:
            return

        if delay_state["started_at"] is None:
            delay_state["started_at"] = sim_time
            return

        if (sim_time - delay_state["started_at"]) >= delay_state["delay"]:
            delay_state["finished"] = True
            label = DELAY_LABELS.get(delay_name, delay_name)
            print(f"[Scenario03] {label} delay endet!")

    def start_caraway(self):
        if self.caraway_active or self.caraway_finished:
            return
        print("[Scenario03] caraway started!")
        self.caraway_active = True

    def find_hero(self):
        for actor in self.world.get_actors():
            if actor.attributes.get("role_name") in ["hero", "default_player"]:
                return actor
        return None

    def _get_traffic_manager(self):
        try:
            tm = self.client.get_trafficmanager(self._tm_port)
        except Exception:
            tm = self.client.get_trafficmanager()

        try:
            tm.set_synchronous_mode(self.world.get_settings().synchronous_mode)
        except Exception:
            pass

        return tm

    def _get_caraway_trigger_config(self, hero_location, hero_velocity=None):
        if hero_location is None:
            return None

        for trigger_config in CARAWAY:
            trigger_name = trigger_config.get("name")
            if trigger_name in self._caraway_triggered_keys:
                continue

            trigger_point = trigger_config.get("trigger_1")
            if not isinstance(trigger_point, dict):
                continue

            trigger_location = trigger_point.get("trigger_location")
            if trigger_location is None:
                continue

            if abs(hero_location.x - trigger_location.x) > trigger_point.get("trigger_x_tolerance", 0.0):
                continue
            if abs(hero_location.y - trigger_location.y) > trigger_point.get("trigger_y_tolerance", 0.0):
                continue

            required_axis = trigger_point.get("trigger_direction_axis")
            required_sign = trigger_point.get("trigger_direction_sign")
            if required_axis is not None and required_sign is not None:
                if hero_velocity is None:
                    continue
                if required_axis == "x":
                    axis_velocity = hero_velocity.x
                elif required_axis == "y":
                    axis_velocity = hero_velocity.y
                else:
                    continue
                if axis_velocity * required_sign <= 0.0:
                    continue

            return trigger_config

        return None

    def _draw_caraway_trigger_boxes(self):
        if not DEBUG_MODE or not self.caraway_active or self.caraway_finished:
            return

        trigger_points = []
        for trigger_config in CARAWAY:
            trigger_point = trigger_config.get("trigger_1")
            if isinstance(trigger_point, dict):
                trigger_points.append(trigger_point)

        if not trigger_points:
            return

        box_configs = build_trigger_box_configs(
            trigger_points,
            z_extra=2.0,
            color=(255, 0, 0, 255),
            thickness=0.1,
        )
        draw_trigger_boxes(self.world, box_configs, life_time=self._debug_trigger_box_lifetime)

    def _spawn_caraway_vehicle_from_config(self, trigger_config):
        if trigger_config is None:
            return False

        trigger_name = trigger_config.get("name", "unknown")
        spawn_configs = trigger_config.get("spawn_configs", [])
        if not spawn_configs:
            print(f"[Scenario03] WARNUNG: caraway trigger {trigger_name} hat keine spawn_configs")
            return False

        spawn_config = spawn_configs[0]
        transform = spawn_config.get("transform")
        if transform is None:
            print(f"[Scenario03] WARNUNG: caraway trigger {trigger_name} hat keinen Transform")
            return False

        #blueprint_id = "vehicle.ford.mustang"
        blueprint_id = "vehicle.ford.crown"
        try:
            vehicle_bp = self.world.get_blueprint_library().find(blueprint_id)
        except Exception as exc:
            print(f"[Scenario03] WARNUNG: Blueprint {blueprint_id} nicht gefunden für {trigger_name}: {exc}")
            return False

        if vehicle_bp.has_attribute("color"):
            try:
                vehicle_bp.set_attribute("color", "0,0,0")
            except Exception:
                pass

        actor = self.world.try_spawn_actor(vehicle_bp, transform)
        if actor is None:
            location = transform.location
            for offset in (0.6, 1.0):
                retry_transform = carla.Transform(
                    carla.Location(x=location.x, y=location.y, z=location.z + offset),
                    transform.rotation,
                )
                actor = self.world.try_spawn_actor(vehicle_bp, retry_transform)
                if actor is not None:
                    transform = retry_transform
                    break

        if actor.get_light_state() is not None:
            try:
                new_light_stage = VehicleLightState.Position | VehicleLightState.LowBeam
                
                actor.set_light_state(carla.VehicleLightState(new_light_stage))
                print(f"[Scenario03] Licht für {trigger_name} erfolgreich eingeschaltet.")
            except Exception as exc:
                print(f"[Scenario03] WARNUNG: Licht konnte nicht eingeschaltet werden: {exc}")

        if actor is None:
            print(
                f"[Scenario03] WARNUNG: caraway spawn fehlgeschlagen für {trigger_name} | "
                f"blueprint={blueprint_id}, spawn=({transform.location.x:.2f}, {transform.location.y:.2f}, {transform.location.z:.2f})"
            )
            return False

        try:
            tm = self._get_traffic_manager()
            actor.set_autopilot(True, tm.get_port())
            try:
                tm.auto_lane_change(actor, False)
                tm.random_left_lanechange_percentage(actor, 0.0)
                tm.random_right_lanechange_percentage(actor, 0.0)
                tm.keep_right_rule_percentage(actor, 0.0)
            except Exception:
                pass
            try:
                tm.set_route(actor, route_green)
            except Exception:
                tm.set_route(actor.id, route_green)
        except Exception as exc:
            print(f"[Scenario03] WARNUNG: Route für caraway actor {actor.id} konnte nicht gesetzt werden: {exc}")

        self._caraway_triggered_keys.add(trigger_name)
        self._vehicle_actor_ids.append(actor.id)
        self._caraway_vehicle_spawn_locations[actor.id] = actor.get_location()
        self._caraway_vehicle_last_locations[actor.id] = actor.get_location()
        self._caraway_vehicle_distances_m[actor.id] = 0.0
        self.caraway_active = False
        self.caraway_finished = True

        print(
            f"[Scenario03] {trigger_name} aktiviert -> caraway vehicle gespawnt: id={actor.id}, blueprint={blueprint_id}, route={route_green}"
        )
        return True

    def _update_caraway_vehicle_lifetimes(self):
        if not self._caraway_vehicle_distances_m:
            return

        for actor_id in list(self._caraway_vehicle_distances_m.keys()):
            try:
                actor = self.world.get_actor(actor_id)
            except Exception:
                actor = None

            if actor is None:
                self._caraway_vehicle_distances_m.pop(actor_id, None)
                self._caraway_vehicle_last_locations.pop(actor_id, None)
                self._caraway_vehicle_spawn_locations.pop(actor_id, None)
                if actor_id in self._vehicle_actor_ids:
                    try:
                        self._vehicle_actor_ids.remove(actor_id)
                    except ValueError:
                        pass
                continue

            try:
                current_location = actor.get_location()
            except Exception:
                continue

            last_location = self._caraway_vehicle_last_locations.get(actor_id)
            if last_location is not None:
                traveled = self._caraway_vehicle_distances_m.get(actor_id, 0.0)
                traveled += last_location.distance(current_location)
                self._caraway_vehicle_distances_m[actor_id] = traveled

                if traveled >= 200.0:
                    try:
                        self.client.apply_batch([carla.command.DestroyActor(actor_id)])
                    except Exception:
                        pass
                    self._caraway_vehicle_distances_m.pop(actor_id, None)
                    self._caraway_vehicle_last_locations.pop(actor_id, None)
                    self._caraway_vehicle_spawn_locations.pop(actor_id, None)
                    if actor_id in self._vehicle_actor_ids:
                        try:
                            self._vehicle_actor_ids.remove(actor_id)
                        except ValueError:
                            pass
                    print(f"[Scenario03] caraway vehicle id={actor_id} after 200m destroyed.")
                    continue

            self._caraway_vehicle_last_locations[actor_id] = current_location

    def _get_ltruck_config(self, hero_location, hero_velocity=None):
        for config in LTRUCK_SPAWN_CONFIGS:
            trigger_location = config["trigger_location"]
            if abs(hero_location.x - trigger_location.x) > config["trigger_x_tolerance"]:
                continue
            if abs(hero_location.y - trigger_location.y) > config["trigger_y_tolerance"]:
                continue

            required_axis = config.get("trigger_direction_axis")
            required_sign = config.get("trigger_direction_sign")
            if required_axis is not None and required_sign is not None:
                if hero_velocity is None: continue
                vel = hero_velocity.x if required_axis == "x" else hero_velocity.y
                if vel * required_sign <= 0.0: continue

            required_axis_2 = config.get("trigger_direction_axis_2")
            required_sign_2 = config.get("trigger_direction_sign_2")
            if required_axis_2 is not None and required_sign_2 is not None:
                if hero_velocity is None: continue
                vel2 = hero_velocity.x if required_axis_2 == "x" else hero_velocity.y
                if vel2 * required_sign_2 <= 0.0: continue
            return config
        return None

    def _start_ltruck_manual_control_from_config(self, config):
        name = config.get("name")
        if name in self._ltruck_triggered_keys:
            return False

        spawn_configs = config.get("spawn_configs", [])
        if not spawn_configs:
            return False

        prop = spawn_configs[0]
        blueprints = prop.get("blueprints", [])
        if not blueprints:
            return False

        vehicle_id = blueprints[0]
        vehicle_color = prop.get("color")
        spawn_transform = prop.get("transform")
        audio_mode = prop.get("audio_mode")

        self._ltruck_process = start_manual_control_process(
            host=self.host,
            port=self.port,
            profile='supervisor4home',
            done_file=None,
            vehicle_id=vehicle_id,
            vehicle_color=vehicle_color,
            spawn_transform=spawn_transform,
            audio_mode=audio_mode,
            existing_process=self._ltruck_process,
            log_prefix='Scenario03',
        )

        if self._ltruck_process is None:
            return False

        print(
            f"[Scenario03] Started ltruck manual_control: "
            f"vehicleID={vehicle_id}, vehicleColor={vehicle_color}, audio_mode={audio_mode}\n"
            f"1. honk from behind\n"
            f"2. turn on light (with TODO)\n"
            f"3. drive next to car"
        )

        while True:
            user_input = input("\n[Scenario03] Press 'J' + Enter to continue scenario: ").strip().upper()
            if user_input == 'J':
                break

        self._ltruck_triggered_keys.add(name)
        return True

    def start_ltruck(self):
        if self.ltruck_active or self.ltruck_finished:
            return
        print("[Scenario03] ltruck started!")
        self.ltruck_active = True

    def _draw_ltruck_trigger_boxes(self):
        if not DEBUG_MODE or not self.ltruck_active or self.ltruck_finished:
            return

        box_configs = build_trigger_box_configs(
            LTRUCK_SPAWN_CONFIGS,
            z_extra=2.0,
            color=(255, 0, 0, 255),
            thickness=0.1,
        )
        draw_trigger_boxes(self.world, box_configs, life_time=self._debug_trigger_box_lifetime)

    def _spawn_temp_firetruck_barriers(self):
        if self._temp_firetruck_actor_ids:
            return True

        if not TEMP_BARRIER_FIRETRUCK:
            return False

        bp_lib = self.world.get_blueprint_library()
        spawned_count = 0

        for trigger_config in TEMP_BARRIER_FIRETRUCK:
            spawn_configs = trigger_config.get("spawn_configs", [])
            for prop_config in spawn_configs:
                blueprint_ids = prop_config.get("blueprints", [])
                transform = prop_config.get("transform")
                if transform is None or not blueprint_ids:
                    continue

                vehicle_bp = None
                for blueprint_id in blueprint_ids:
                    try:
                        vehicle_bp = bp_lib.find(blueprint_id)
                        break
                    except Exception:
                        vehicle_bp = None

                if vehicle_bp is None:
                    print(f"[Scenario03] WARNUNG: Kein Blueprint für TEMP_BARRIER_FIRETRUCK gefunden: {blueprint_ids}")
                    continue

                actor = self.world.try_spawn_actor(vehicle_bp, transform)
                if actor is None:
                    print(
                        f"[Scenario03] WARNUNG: TEMP_BARRIER_FIRETRUCK spawn fehlgeschlagen | "
                        f"blueprint={vehicle_bp.id}, spawn=({transform.location.x:.2f}, {transform.location.y:.2f}, {transform.location.z:.2f})"
                    )
                    continue

                try:
                    if hasattr(actor, "set_target_velocity"):
                        actor.set_target_velocity(carla.Vector3D(0.0, 0.0, 0.0))
                    if hasattr(actor, "set_target_angular_velocity"):
                        actor.set_target_angular_velocity(carla.Vector3D(0.0, 0.0, 0.0))
                    if hasattr(actor, "set_simulate_physics"):
                        actor.set_simulate_physics(False)
                except Exception:
                    pass

                self._temp_firetruck_actor_ids.append(actor.id)
                spawned_count += 1
                print(f"[Scenario03] TEMP_BARRIER_FIRETRUCK gespawnt: id={actor.id}, blueprint={vehicle_bp.id}")

        return spawned_count > 0

    def _start_temp_firetruck_trigger(self):
        if self._temp_firetruck_trigger_active or self._temp_firetruck_trigger_triggered:
            return

        if self._temp_firetruck_trigger_config is None:
            return

        self._temp_firetruck_trigger_active = True
        print("[Scenario03] TEMP_BARRIER_FIRETRUCK trigger activated!")

    def _draw_temp_firetruck_trigger_box(self):
        if not DEBUG_MODE or not self._temp_firetruck_trigger_active or self._temp_firetruck_trigger_triggered:
            return

        if self._temp_firetruck_trigger_config is None:
            return

        box_configs = build_trigger_box_configs(
            [self._temp_firetruck_trigger_config],
            z_extra=2.0,
            color=(255, 0, 0, 255),
            thickness=0.1,
        )
        draw_trigger_boxes(self.world, box_configs, life_time=self._debug_trigger_box_lifetime)

    def _destroy_temp_firetruck_barriers(self):
        if not self._temp_firetruck_actor_ids:
            self._temp_firetruck_trigger_triggered = True
            self._temp_firetruck_trigger_active = False
            return

        try:
            self.client.apply_batch([carla.command.DestroyActor(actor_id) for actor_id in list(self._temp_firetruck_actor_ids)])
        except Exception:
            pass

        self._temp_firetruck_actor_ids.clear()
        self._temp_firetruck_trigger_triggered = True
        self._temp_firetruck_trigger_active = False
        print("[Scenario03] TEMP_BARRIER_FIRETRUCK destroyed.")

    def _temp_firetruck_trigger_reached(self, hero_location, hero_velocity=None):
        trigger_point = self._temp_firetruck_trigger_config
        if hero_location is None or not isinstance(trigger_point, dict):
            return False

        trigger_location = trigger_point.get("trigger_location")
        if trigger_location is None:
            return False

        if abs(hero_location.x - trigger_location.x) > float(trigger_point.get("trigger_x_tolerance", 0.0)):
            return False
        if abs(hero_location.y - trigger_location.y) > float(trigger_point.get("trigger_y_tolerance", 0.0)):
            return False

        required_axis = trigger_point.get("trigger_direction_axis")
        required_sign = trigger_point.get("trigger_direction_sign")
        if required_axis is not None and required_sign is not None:
            if hero_velocity is None:
                return False
            axis_velocity = hero_velocity.x if required_axis == "x" else hero_velocity.y if required_axis == "y" else None
            if axis_velocity is None:
                return False
            if axis_velocity * required_sign <= 0.0:
                return False

        return True

    def _spawn_start_static_props(self):
        if self._start_static_props_spawned:
            return True

        bp_lib = self.world.get_blueprint_library()
        spawn_configs = get_barrier_spawn()
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
            
            if DEBUG_MODE:
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
        self._spawn_temp_firetruck_barriers()
        if spawned_count == len(spawn_configs):
            print(f"[Scenario06] Start-Props: {spawned_count}/{len(spawn_configs)} gespawnt.")
        else:
            print(
                f"[Scenario06] Start-Props: {spawned_count}/{len(spawn_configs)} gespawnt, "
                f"nicht alle konnten gesetzt werden. Fehlschläge={failed_configs}"
            )
        return spawned_count == len(spawn_configs)

    def start_song(self):
        if self.song_started:
            return
        self.song_started = True
        self._song_start_time = self.world.get_snapshot().timestamp.elapsed_seconds
        print(f"[Scenario03] song started at sim_time={self._song_start_time:.2f}s")
        if self._song_audio.play(self._song_start_time):
            print("[Scenario03] song play requested")
        else:
            print("[Scenario03] WARNUNG: Song konnte nicht gestartet werden.")
            self.song_finished = True

    def _update_song(self, sim_time):
        if not self.song_started or self.song_finished:
            return

        self._song_audio.update(sim_time)
        if self._song_audio.is_finished:
            self.song_finished = True
            print("[Scenario03] song finished!")

    def start_police(self):
        if self.police_active or self.police_finished:
            return
        print("[Scenario03] police started!")
        self.police_active = True

    def _draw_copwaving_trigger_boxes(self):
        if not DEBUG_MODE or not self.police_active or self.police_finished:
            return

        box_configs = build_trigger_box_configs(
            COPWAVING_TRIGGER_CONFIGS,
            z_extra=2.0,
            color=(255, 0, 0, 255),
            thickness=0.1,
        )
        draw_trigger_boxes(self.world, box_configs, life_time=self._debug_trigger_box_lifetime)

    def _get_copwaving_trigger_config(self, hero_location, hero_velocity=None):
        if hero_location is None:
            return None
        
        for trigger_config in COPWAVING_TRIGGER_CONFIGS:
            trigger_name = trigger_config.get("name")
            
            # Überspringe den Trigger, wenn er bereits ausgelöst wurde
            if trigger_name in self._copwaving_triggered_keys:
                continue
            
            trigger_location = trigger_config["trigger_location"]
            
            # Überprüfe X Position
            if abs(hero_location.x - trigger_location.x) > trigger_config["trigger_x_tolerance"]:
                continue
            
            # Überprüfe Y Position
            if abs(hero_location.y - trigger_location.y) > trigger_config["trigger_y_tolerance"]:
                continue
            
            # Überprüfe Fahrtrichtung wenn vorhanden
            required_axis = trigger_config.get("trigger_direction_axis")
            required_sign = trigger_config.get("trigger_direction_sign")
            if required_axis is not None and required_sign is not None:
                if hero_velocity is None:
                    continue
                
                # Prüfe ob Hero in die richtige Richtung fährt
                if required_axis == "x":
                    axis_velocity = hero_velocity.x
                elif required_axis == "y":
                    axis_velocity = hero_velocity.y
                else:
                    continue
                
                # Muss in die richtige Richtung fahren (Vorzeichen passt)
                if axis_velocity * required_sign <= 0.0:
                    continue
            
            return trigger_config
        
        return None

    def _spawn_copwaving_pedestrian(self, trigger_config):
        if trigger_config is None:
            return False
        
        trigger_name = trigger_config.get("name")
        blueprint_id = trigger_config.get("blueprint_id", "walker.pedestrian.0053")
        spawn_location = trigger_config.get("spawn_location")
        spawn_yaw = trigger_config.get("spawn_yaw", 0.0)
        
        if spawn_location is None:
            print(f"[Scenario03] WARNUNG: Keine spawn_location für {trigger_name}")
            return False
        
        # Erstelle Blueprint
        walker_bp = self.world.get_blueprint_library().find(blueprint_id)
        if walker_bp is None:
            print(f"[Scenario03] WARNUNG: Blueprint {blueprint_id} nicht gefunden für {trigger_name}")
            return False
        
        # Setze is_invincible auf false
        if walker_bp.has_attribute("is_invincible"):
            walker_bp.set_attribute("is_invincible", "false")
        
        # Erstelle Transform
        rotation = carla.Rotation(pitch=0.0, yaw=spawn_yaw if spawn_yaw is not None else 0.0, roll=0.0)
        transform = carla.Transform(spawn_location, rotation)
        
        # Spawne Actor
        actor = self.world.try_spawn_actor(walker_bp, transform)
        if actor is None:
            print(
                f"[Scenario03] WARNUNG: {trigger_name} konnte nicht gespawnt werden | "
                f"blueprint={blueprint_id}, spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
            )
            return False
        
        # Tracking
        self._copwaving_triggered_keys.add(trigger_name)
        self._copwaving_actor_ids[trigger_name] = actor.id
        self._static_actor_ids.append(actor.id)
        
        print(
            f"[Scenario03] {trigger_name} (police waving) gespawnt: id={actor.id}, blueprint={blueprint_id}, "
            f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
        )
        return True

    def start_break(self):
        if self.break_finished:
            return
        print("[Scenario03] break started!")
        self.break_finished = True

    def _skip_caraway_trigger(self, sim_time):
        if self.caraway_finished:
            return
        self._finish_delay_timer("start_to_caraway", sim_time)
        self.caraway_active = False
        self.caraway_finished = True
        print("[Scenario03] caraway trigger skipped.")

    def _skip_ltruck_trigger(self, sim_time):
        if self.ltruck_finished:
            return
        self._finish_delay_timer("caraway_to_ltruck", sim_time)
        self._destroy_temp_firetruck_barriers()
        self.ltruck_finished = True
        print("[Scenario03] ltruck trigger skipped.")

    def _skip_song_trigger(self, sim_time):
        if self.song_finished:
            return
        self._finish_delay_timer("ltruck_to_song", sim_time)
        self.song_started = True
        self.song_finished = True
        print("[Scenario03] song trigger skipped.")

    def _skip_police_trigger(self, sim_time):
        if self.police_finished:
            return
        self._finish_delay_timer("song_to_police", sim_time)
        self.police_finished = True
        print("[Scenario03] police trigger skipped.")

    def _skip_break_trigger(self, sim_time):
        if self.break_finished:
            return
        self._finish_delay_timer("police_to_break", sim_time)
        self.break_finished = True
        print("[Scenario03] break trigger skipped.")

    def run(self):
        print("[Scenario03] Running...")
        if run_in_singleFile_mode:
            self.world.set_weather(carla.WeatherParameters.CloudyNoon)        # CloudyNight
            print("[Scenario03] Weather set to CloudyNight for single-file mode")

        try:
            while True:
                self.world.wait_for_tick()
                sim_time = self.world.get_snapshot().timestamp.elapsed_seconds

                hero = self.find_hero()
                ego_location = hero.get_location() if hero else None
                ego_velocity = hero.get_velocity() if hero else None

                if self._start_sim_time is None:
                    self._start_sim_time = sim_time
                    self._spawn_start_static_props()

                start_to_caraway = self._delay_states["start_to_caraway"]
                if start_to_caraway["started_at"] is None:
                    self._start_delay_timer("start_to_caraway", sim_time)
                self._update_delay_timer("start_to_caraway", sim_time)

                if start_to_caraway["finished"] and not self.caraway_finished:
                    if not self._trigger_caraway:
                        self._skip_caraway_trigger(sim_time)
                    else:
                        self.start_caraway()

                if self.caraway_active and not self.caraway_finished:
                    self._draw_caraway_trigger_boxes()

                    caraway_trigger_config = None
                    if ego_location is not None:
                        caraway_trigger_config = self._get_caraway_trigger_config(ego_location, ego_velocity)

                    if caraway_trigger_config is not None:
                        if self._spawn_caraway_vehicle_from_config(caraway_trigger_config):
                            self._finish_delay_timer("start_to_caraway", sim_time)

                self._update_caraway_vehicle_lifetimes()

                if self.caraway_finished:
                    caraway_to_ltruck = self._delay_states["caraway_to_ltruck"]
                    if caraway_to_ltruck["started_at"] is None:
                        self._start_delay_timer("caraway_to_ltruck", sim_time)
                    self._update_delay_timer("caraway_to_ltruck", sim_time)

                    if caraway_to_ltruck["finished"] and not self._temp_firetruck_trigger_active and not self._temp_firetruck_trigger_triggered:
                        self._start_temp_firetruck_trigger()

                    if self._temp_firetruck_trigger_active and not self._temp_firetruck_trigger_triggered:
                        self._draw_temp_firetruck_trigger_box()
                        if ego_location is not None and self._temp_firetruck_trigger_reached(ego_location, ego_velocity):
                            self._destroy_temp_firetruck_barriers()

                    if caraway_to_ltruck["finished"] and self._temp_firetruck_trigger_triggered and not self.ltruck_active and not self.ltruck_finished:
                        if not self._trigger_ltruck:
                            self._skip_ltruck_trigger(sim_time)
                        else:
                            self.start_ltruck()

                    self._draw_ltruck_trigger_boxes()

                    if self.ltruck_active and not self.ltruck_finished:
                        config = None
                        if TEST_INSTANT_TRIGGER_LTRUCK:
                            config = LTRUCK_SPAWN_CONFIGS[ltruck_spawn_idx] if LTRUCK_SPAWN_CONFIGS else None
                        elif ego_location:
                            config = self._get_ltruck_config(ego_location, ego_velocity)

                        if config:
                            if self._start_ltruck_manual_control_from_config(config):
                                self.ltruck_finished = True

                if self.ltruck_finished:
                    ltruck_to_song = self._delay_states["ltruck_to_song"]
                    if ltruck_to_song["started_at"] is None:
                        self._start_delay_timer("ltruck_to_song", sim_time)
                    self._update_delay_timer("ltruck_to_song", sim_time)

                    if ltruck_to_song["finished"] and not self.song_finished:
                        if not self._trigger_song:
                            self._skip_song_trigger(sim_time)
                        else:
                            self.start_song()

                self._update_song(sim_time)

                if self.song_finished:
                    song_to_police = self._delay_states["song_to_police"]
                    if song_to_police["started_at"] is None:
                        self._start_delay_timer("song_to_police", sim_time)
                    self._update_delay_timer("song_to_police", sim_time)

                    if song_to_police["finished"] and not self.police_finished:
                        if not self._trigger_police:
                            self._skip_police_trigger(sim_time)
                        else:
                            self.start_police()

                # Police phase: spawn copWaving when police active; wait for lifetime then finish
                if self.police_active and not self.police_finished:
                    self._draw_copwaving_trigger_boxes()

                    copwaving_config = None
                    if TEST_INSTANT_TRIGGER_COP:
                        copwaving_config = COPWAVING_TRIGGER_CONFIGS[cop_spawn_idx] if COPWAVING_TRIGGER_CONFIGS else None
                    elif hero:
                        hero_velocity = hero.get_velocity()
                        copwaving_config = self._get_copwaving_trigger_config(ego_location, hero_velocity)

                    if copwaving_config is not None:
                        name = copwaving_config.get("name")
                        if name not in self._copwaving_triggered_keys:
                            spawned = self._spawn_copwaving_pedestrian(copwaving_config)
                            if spawned:
                                self._copwaving_spawn_time[name] = sim_time

                    # Check for spawned cop lifetimes
                    if self._copwaving_spawn_time:
                        for name, spawn_t in list(self._copwaving_spawn_time.items()):
                            if (sim_time - spawn_t) >= COPWAVING_LIFETIME_S:
                                actor_id = self._copwaving_actor_ids.get(name)
                                if actor_id is not None:
                                    try:
                                        self.client.apply_batch([carla.command.DestroyActor(actor_id)])
                                    except Exception:
                                        pass
                                    if actor_id in self._vehicle_actor_ids:
                                        try:
                                            self._vehicle_actor_ids.remove(actor_id)
                                        except ValueError:
                                            pass
                                    if actor_id in self._static_actor_ids:
                                        try:
                                            self._static_actor_ids.remove(actor_id)
                                        except ValueError:
                                            pass
                                # cleanup
                                try:
                                    del self._copwaving_spawn_time[name]
                                except KeyError:
                                    pass
                                if name in self._copwaving_actor_ids:
                                    del self._copwaving_actor_ids[name]
                                # mark police phase finished so police_to_break can start
                                self.police_finished = True
                                self.police_active = False
                                break

                if self.police_finished:
                    police_to_break = self._delay_states["police_to_break"]
                    if police_to_break["started_at"] is None:
                        self._start_delay_timer("police_to_break", sim_time)
                    self._update_delay_timer("police_to_break", sim_time)

                    if police_to_break["finished"] and not self.break_finished:
                        if not self._trigger_break:
                            self._skip_break_trigger(sim_time)
                        else:
                            self.start_break()

                if self.break_finished:
                    break_to_end = self._delay_states["break_to_end"]
                    if break_to_end["started_at"] is None:
                        self._start_delay_timer("break_to_end", sim_time)
                    self._update_delay_timer("break_to_end", sim_time)

                    if break_to_end["finished"]:
                        self._scenario_done = True

                if self._scenario_done:
                    return

                time.sleep(SIM_STEP_S)
        except KeyboardInterrupt:
            pass
        finally:
            self.destroy()
            self._signal_done()

    def destroy(self):
        try:
            self._song_audio.stop(0)
            if self._ltruck_process is not None and self._ltruck_process.poll() is None:
                self._ltruck_process.terminate()
            all_ids = self._static_actor_ids + self._vehicle_actor_ids
            if all_ids:
                self.client.apply_batch([carla.command.DestroyActor(x) for x in all_ids])
            self._caraway_vehicle_spawn_locations.clear()
            self._caraway_vehicle_last_locations.clear()
            self._caraway_vehicle_distances_m.clear()
            self._destroy_temp_firetruck_barriers()
        except Exception:
            pass

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
            print(f"[Scenario03] WARNING: could not write done signal file: {exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=2000, type=int)
    parser.add_argument("--tm-port", default=8000, type=int)
    parser.add_argument("--done-file", default=None)
    args = parser.parse_args()

    Scenario03Runner(
        args.host,
        args.port,
        args.tm_port,
        args.done_file,
        trigger_caraway=TRIGGER_CARAWAY,
        trigger_ltruck=TRIGGER_LTRUCK,
        trigger_song=TRIGGER_SONG,
        trigger_police=TRIGGER_POLICE,
        trigger_break=TRIGGER_BREAK,
    ).run()
