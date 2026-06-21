import argparse
import os
import math
import random
import sys
import time

import carla
from carla import VehicleLightState
import threading

# For debug start manual control with: 
# --enable-brake-warning

BRAKE_SIGNAL_FILE_DEFAULT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    'common',
    'scenario_brake.signal',
)
BRAKE_SIGNAL_FILE_DEFAULT = os.path.normpath(os.path.abspath(BRAKE_SIGNAL_FILE_DEFAULT))
BRAKE_WARNING_CHIME_PATH = r"C:\C_CARLA\CARLA_extensions\audio\car_low_fuel_chime.wav"

try:
    from common.audio_paths import FEAR_RP_NEUROSIS_FEAR_AND_SICKNESS_PATH
    from generate_audio import RepeatingAudio, SongAudio
except ModuleNotFoundError:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    extensions_root = os.path.normpath(os.path.join(current_dir, ".."))
    if extensions_root not in sys.path:
        sys.path.insert(0, extensions_root)
    from common.audio_paths import FEAR_RP_NEUROSIS_FEAR_AND_SICKNESS_PATH
    from generate_audio import RepeatingAudio, SongAudio

try:
    from scenario_helper import start_manual_control_process
except ModuleNotFoundError:
    from scenario_events.scenario_helper import start_manual_control_process

try:
    from scenario_helper import build_trigger_box_configs, draw_trigger_boxes, force_green_light
except ModuleNotFoundError:
    from scenario_events.scenario_helper import build_trigger_box_configs, draw_trigger_boxes, force_green_light

from scenario_logger import TriggerLogger, parse_logging_arg

try:
    from events_scenario03_static_props import (
        get_barrier_spawn,
        TEMP_BARRIER_FIRETRUCK,
        SPAWN_TEMP_BARRIER_FIRETRUCK,
        LTRUCK_SPAWN_CONFIGS,
        COPWAVING_TRIGGER_CONFIGS,
        CARAWAY,
        TARGET_TL_RED,
        LTRUCK_NAVIGATION_BARRIER_CONFIGS,
    )
except ModuleNotFoundError:
    from scenario_events.events_scenario03_static_props import (
        get_barrier_spawn,
        TEMP_BARRIER_FIRETRUCK,
        LTRUCK_SPAWN_CONFIGS,
        COPWAVING_TRIGGER_CONFIGS,
        CARAWAY,
        TARGET_TL_RED,
        LTRUCK_NAVIGATION_BARRIER_CONFIGS,
    )

DEBUG_MODE = False

if DEBUG_MODE:
    START_TO_CARAWAY_DELAY = 2.0
    CARAWAY_TO_LTRUCK_DELAY = 3.0
    LTRUCK_TO_SONG_DELAY = 3.0
    SONG_TO_POLICE_DELAY = 2.0
    POLICE_TO_BRAKE_DELAY = 3.0
    BRAKE_TO_END_DELAY = 5.0

    TRIGGER_CARAWAY = False
    TRIGGER_LTRUCK = False
    TRIGGER_SONG = False
    TRIGGER_POLICE = True
    TRIGGER_BRAKE = True

    run_in_singleFile_mode = True
    SUPERVISOR_PROFILE = 'supervisor4home'
else:
    START_TO_CARAWAY_DELAY = 10.0
    CARAWAY_TO_LTRUCK_DELAY = 20.0
    LTRUCK_TO_SONG_DELAY = 30.0
    SONG_TO_POLICE_DELAY = 10.0
    POLICE_TO_BRAKE_DELAY = 30.0
    BRAKE_TO_END_DELAY = 5.0

    TRIGGER_CARAWAY = True
    TRIGGER_LTRUCK = True
    TRIGGER_SONG = True
    TRIGGER_POLICE = True
    TRIGGER_BRAKE = True

    run_in_singleFile_mode = False
    SUPERVISOR_PROFILE = 'supervisor'

SONG_START_OFFSET_SECONDS = 0.0
SONG_PLAY_DURATION_SECONDS = 20.0
SONG_FADE_IN_MS = 3000
SONG_FADE_OUT_MS = 3000
SIM_STEP_S = 0.05

route_green = ["Straight", "Straight", "Straight", "Straight", "Straight", "Straight"]


# copWaving lifetime (seconds) before removal
COPWAVING_LIFETIME_S = 30.0
COPWAVING_WALK_SPEED = 1.4
COPWAVING_ARRIVE_THRESH = 1.2
COPWAVING_STATUS_LOG_INTERVAL_S = 1.0
COPWAVING_TRANSITION_BACKSTEP_M = 0.0

# For testing: when True, ltruckTrigger 1 or 2 is considered triggered instantly
TEST_INSTANT_TRIGGER_LTRUCK = False
ltruck_spawn_idx = 0
TEST_INSTANT_TRIGGER_COP = False
cop_spawn_idx = 0
cop_wave_duration = 5.0

DELAY_LABELS = {
    "start_to_caraway": "caraway",
    "caraway_to_ltruck": "ltruck",
    "ltruck_to_song": "song",
    "song_to_police": "police",
    "police_to_brake": "brake",
    "brake_to_end": "end",
}

class Scenario03Runner:
    def __init__(self, host, port, tm_port, done_file=None, logging=None, trigger_caraway=True, trigger_ltruck=True, trigger_song=True, trigger_police=True, trigger_brake=True):
        self.client = carla.Client(host, port)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()
        self.host = host
        self.port = port
        self._tm_port = tm_port
        self._done_file = done_file
        self._rng = random.Random()
        self._all_traffic_lights = []
        # Will pin the target traffic lights by location during init
        self._pinned_traffic_light_ids = set()
        # Mapping of pinned TL id -> red hold duration (seconds)
        self._pinned_traffic_light_durations = {}
        self._ltruck_tl_hold_start = None
        self._init_all_traffic_lights()

        self._trigger_caraway = trigger_caraway
        self._trigger_ltruck = trigger_ltruck
        self._trigger_song = trigger_song
        self._trigger_police = trigger_police
        self._trigger_brake = trigger_brake

        self._start_sim_time = None
        self._scenario_done = False
        self._force_green_light_request_time = None

        self.caraway_finished = False
        self.caraway_active = False
        self.ltruck_active = False
        self.ltruck_finished = False
        self.song_started = False
        self.song_finished = False
        self.police_finished = False
        self.police_active = False
        self.brake_finished = False

        self._start_static_props_spawned = False
        self._persistent_static_actor_ids = []
        self._temp_firetruck_actor_ids = []
        self._temp_firetruck_trigger_config = TEMP_BARRIER_FIRETRUCK[0].get("trigger_1") if TEMP_BARRIER_FIRETRUCK else None
        self._temp_firetruck_trigger_active = False
        self._temp_firetruck_trigger_triggered = False

        # SPAWN_TEMP_BARRIER_FIRETRUCK triggers (activated when ltruck spawns)
        self._spawn_temp_firetruck_trigger_configs = SPAWN_TEMP_BARRIER_FIRETRUCK if 'SPAWN_TEMP_BARRIER_FIRETRUCK' in globals() else None
        self._spawn_temp_firetruck_active = False
        self._spawn_temp_firetruck_triggered = False

        # L-truck navigation barrier triggers (activated after temp firetruck barriers destroyed)
        self._ltruck_nav_barrier_configs = LTRUCK_NAVIGATION_BARRIER_CONFIGS if 'LTRUCK_NAVIGATION_BARRIER_CONFIGS' in globals() else None
        self._ltruck_nav_barriers_active = False
        self._ltruck_nav_barriers_triggered_keys = set()
        self._ltruck_nav_barrier_actor_ids = []

        self._ltruck_triggered_keys = set()
        self._caraway_triggered_keys = set()
        self._ltruck_process = None
        self._static_actor_ids = []
        self._vehicle_actor_ids = []
        self._caraway_vehicle_spawn_locations = {}
        self._caraway_vehicle_last_locations = {}
        self._caraway_vehicle_distances_m = {}
        self._debug_trigger_box_lifetime = SIM_STEP_S * 2.0

        self.trigger_logger = None
        if logging:
            pid, scen = parse_logging_arg(logging)
            if pid and scen:
                self.trigger_logger = TriggerLogger(pid, scen)
                print(f"[Scenario00] TriggerLogger attached for participant={pid}, scenario={scen}")
            else:
                print(f"[Scenario00] Could not parse --logging arg: {logging}")

        # copWaving tracking
        self._copwaving_triggered_keys = set()
        self._copwaving_actor_ids = {}
        self._copwaving_spawn_time = {}
        self._copwaving_active_trigger_name = None
        self._copwaving_active_trigger_config = None
        self._copwaving_wave_actor_id = None
        self._copwaving_walk_actor_id = None
        self._copwaving_walk_controller_id = None
        self._copwaving_walk_started = False
        self._copwaving_target_location = None
        self._copwaving_last_update_time = None
        self._copwaving_last_status_log_time = None
        self._copwaving_transition_pending = False
        self._copwaving_transition_spawn_transform = None
        self._copwaving_target_locations = None
        self._copwaving_current_target_idx = 0
        # copWaving phase start time (used to enforce COPWAVING_LIFETIME_S)
        self._copwaving_phase_start_time = None
        # support multiple sequential targets for cop waving (list of carla.Location)
        self._copwaving_target_locations = None
        self._copwaving_current_target_idx = 0

        self._brake_signal_file = BRAKE_SIGNAL_FILE_DEFAULT

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
            "police_to_brake": {
                "delay": POLICE_TO_BRAKE_DELAY,
                "started_at": None,
                "finished": False,
            },
            "brake_to_end": {
                "delay": BRAKE_TO_END_DELAY,
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
        self._brake_warning_audio = RepeatingAudio(
            BRAKE_WARNING_CHIME_PATH,
            repeat_count=5,
            volume=0.85,
            channel_index=7,
        )

    def _init_all_traffic_lights(self):
        actors = self.world.get_actors()
        self._all_traffic_lights = [actor for actor in actors if 'traffic_light' in actor.type_id]

        for tl in self._all_traffic_lights:
            # tln.freeze(True) => stops all traffic lights
            try:
                tl.freeze(True)
            except Exception:
                pass
            try:
                loc = tl.get_transform().location
                print(f"[Scenario03] TrafficLight found: id={tl.id} type_id={tl.type_id} loc=({loc.x:.2f},{loc.y:.2f},{loc.z:.2f}) state={tl.get_state()}")
            except Exception:
                try:
                    print(f"[Scenario03] TrafficLight found: id={getattr(tl, 'id', 'n/a')} type_id={getattr(tl, 'type_id', 'n/a')}")
                except Exception:
                    pass

        # Try to pin traffic lights based on TARGET_TL_RED definitions from static props
        try:
            for targ_idx, targ in enumerate(TARGET_TL_RED, start=1):
                tloc = targ.get("location")
                trad = float(targ.get("search_radius", 2.0))
                hold_dur = float(targ.get("red_hold_duration", 20.0))
                best_tl = None
                best_dist = None
                for tl in self._all_traffic_lights:
                    try:
                        loc = tl.get_transform().location
                    except Exception:
                        continue
                    dx = loc.x - tloc.x
                    dy = loc.y - tloc.y
                    dist = math.hypot(dx, dy)
                    if dist <= trad and (best_dist is None or dist < best_dist):
                        best_dist = dist
                        best_tl = tl
                if best_tl is not None:
                    tl_id = best_tl.id
                    self._pinned_traffic_light_ids.add(tl_id)
                    self._pinned_traffic_light_durations[tl_id] = hold_dur
                    try:
                        loc = best_tl.get_transform().location
                        print(f"[Scenario03] Pinned traffic light[{targ_idx}] id={tl_id} at loc=({loc.x:.2f},{loc.y:.2f},{loc.z:.2f}) dist={best_dist:.2f}m hold={hold_dur:.1f}s")
                    except Exception:
                        print(f"[Scenario03] Pinned traffic light[{targ_idx}] id={tl_id} (no transform) hold={hold_dur:.1f}s")
                else:
                    print(f"[Scenario03] Kein TrafficLight innerhalb {trad}m von {tloc} gefunden (target {targ_idx}).")
        except Exception:
            pass

    def update_blinking_lights(self, sim_time):
        try:
            cycle_time = sim_time % 1.0
            
            if cycle_time < 0.5:
                target_state = carla.TrafficLightState.Yellow
            else:
                target_state = carla.TrafficLightState.Off

            # Compute elapsed time since L-truck hold started (if any)
            hold_elapsed = None
            try:
                if self._ltruck_tl_hold_start is not None:
                    hold_elapsed = time.time() - self._ltruck_tl_hold_start
            except Exception:
                hold_elapsed = None

            for tl in self._all_traffic_lights:
                try:
                    tl_id = getattr(tl, 'id', None)
                    # If hold is active for this pinned TL, keep it red
                    if tl_id in self._pinned_traffic_light_ids and hold_elapsed is not None:
                        try:
                            dur = float(self._pinned_traffic_light_durations.get(tl_id, 0.0))
                        except Exception:
                            dur = 0.0
                        if hold_elapsed < dur:
                            if tl.get_state() != carla.TrafficLightState.Red:
                                tl.set_state(carla.TrafficLightState.Red)
                            continue

                    # All other traffic lights: blink yellow (toggle Yellow/Off)
                    if tl.get_state() != target_state:
                        tl.set_state(target_state)
                except Exception:
                    # ignore per-light errors
                    pass

            # Expire hold if elapsed longer than all pinned durations
            try:
                if self._ltruck_tl_hold_start is not None:
                    max_dur = max(self._pinned_traffic_light_durations.values()) if self._pinned_traffic_light_durations else 0.0
                    if hold_elapsed is not None and hold_elapsed >= max_dur:
                        self._ltruck_tl_hold_start = None
            except Exception:
                pass
                    
        except Exception:
            pass

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

    def _snap_location_to_navigation(self, location):
        try:
            waypoint = self.world.get_map().get_waypoint(
                location,
                project_to_road=True,
                lane_type=carla.LaneType.Any,
            )
        except Exception:
            waypoint = None

        if waypoint is None:
            return location

        snapped = waypoint.transform.location
        return carla.Location(x=snapped.x, y=snapped.y, z=location.z)

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
        if not LTRUCK_SPAWN_CONFIGS:
            return None

        for config in LTRUCK_SPAWN_CONFIGS:
            trigger_name = config.get("name")
            # skip triggers that already fired once                 # not necessary?!
            if trigger_name in self._ltruck_triggered_keys:
                continue

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
            profile=SUPERVISOR_PROFILE,
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
            f"2. turn on light (with L or X)\n"
            f"3. drive next to car"
        )

        # Mark this trigger so we don't re-enter this routine repeatedly
        try:
            self._ltruck_triggered_keys.add(name)
        except Exception:
            pass

        # Activate SPAWN_TEMP_BARRIER_FIRETRUCK triggers now that the ltruck manual-control process started
        try:
            self._start_spawn_temp_firetruck_triggers()
        except Exception:
            pass

        # Start a background thread to wait for 'J' confirmation so the main simulation loop with hold tl red etc. is not blocked
        def _wait_for_confirm():
            try:
                while True:
                    user_input = input("\n[Scenario03] Press 'J' + Enter to continue scenario: ").strip().upper()
                    if user_input == 'J' or user_input == 'j':
                        break
            except Exception:
                return

            try:
                # set finished flag when user confirms
                self.ltruck_finished = True
                print(f"[Scenario03] LTruck manual control confirmed by user (J).")
            except Exception:
                pass

        t = threading.Thread(target=_wait_for_confirm, daemon=True)
        t.start()

        # Return False to indicate manual-control confirmation will happen asynchronously
        return False

    def start_ltruck(self):
        if self.ltruck_active or self.ltruck_finished:
            return
        print("[Scenario03] ltruck started!")
        self.ltruck_active = True

    def _draw_ltruck_trigger_boxes(self):
        if not DEBUG_MODE or not self.ltruck_active or self.ltruck_finished:
            return

        # If any ltruck trigger has already fired, stop drawing/listening
        if self._ltruck_triggered_keys:
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

    def _start_spawn_temp_firetruck_triggers(self):
        if self._spawn_temp_firetruck_active or self._spawn_temp_firetruck_triggered:
            return

        if not self._spawn_temp_firetruck_trigger_configs:
            return

        self._spawn_temp_firetruck_active = True
        print("[Scenario03] SPAWN_TEMP_BARRIER_FIRETRUCK triggers activated!")

    def _draw_spawn_temp_firetruck_boxes(self):
        if not DEBUG_MODE or not self._spawn_temp_firetruck_active or self._spawn_temp_firetruck_triggered:
            return

        configs = []
        for cfg in (self._spawn_temp_firetruck_trigger_configs or []):
            if not isinstance(cfg, dict):
                continue
            # collect any trigger_* entries (trigger_1, trigger_2, ...)
            for k, v in cfg.items():
                if isinstance(k, str) and k.startswith("trigger") and isinstance(v, dict):
                    configs.append(v)

        if not configs:
            return

        box_configs = build_trigger_box_configs(
            configs,
            z_extra=2.0,
            color=(0, 255, 0, 255),
            thickness=0.1,
        )
        draw_trigger_boxes(self.world, box_configs, life_time=self._debug_trigger_box_lifetime)

    def _spawn_from_spawn_temp_firetruck(self, trigger_entry):
        if not trigger_entry or not isinstance(trigger_entry, dict):
            return False

        bp_lib = self.world.get_blueprint_library()
        spawned_count = 0

        for prop_config in trigger_entry.get("spawn_configs", []):
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
                print(f"[Scenario03] WARNUNG: Kein Blueprint für SPAWN_TEMP_BARRIER_FIRETRUCK gefunden: {blueprint_ids}")
                continue

            actor = self.world.try_spawn_actor(vehicle_bp, transform)
            if actor is None:
                print(
                    f"[Scenario03] WARNUNG: SPAWN_TEMP_BARRIER_FIRETRUCK spawn fehlgeschlagen | "
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
            print(f"[Scenario03] SPAWN_TEMP_BARRIER_FIRETRUCK gespawnt: id={actor.id}, blueprint={vehicle_bp.id}")

        return spawned_count > 0

    def _spawn_temp_firetruck_reached(self, hero_location, hero_velocity=None):
        if hero_location is None or not self._spawn_temp_firetruck_active or self._spawn_temp_firetruck_triggered:
            return False
        for cfg in (self._spawn_temp_firetruck_trigger_configs or []):
            if not isinstance(cfg, dict):
                continue

            # check all trigger_* entries inside this config
            for k, trigger_point in cfg.items():
                if not (isinstance(k, str) and k.startswith("trigger") and isinstance(trigger_point, dict)):
                    continue

                trigger_location = trigger_point.get("trigger_location")
                if trigger_location is None:
                    continue

                if abs(hero_location.x - trigger_location.x) > float(trigger_point.get("trigger_x_tolerance", 0.0)):
                    continue
                if abs(hero_location.y - trigger_location.y) > float(trigger_point.get("trigger_y_tolerance", 0.0)):
                    continue

                required_axis = trigger_point.get("trigger_direction_axis")
                required_sign = trigger_point.get("trigger_direction_sign")
                if required_axis is not None and required_sign is not None:
                    if hero_velocity is None:
                        continue
                    axis_velocity = hero_velocity.x if required_axis == "x" else hero_velocity.y if required_axis == "y" else None
                    if axis_velocity is None:
                        continue
                    if axis_velocity * required_sign <= 0.0:
                        continue

                # reached -> spawn this trigger's spawn_configs and deactivate all spawn triggers
                time.sleep(3.0)
                try:
                    self._spawn_from_spawn_temp_firetruck(cfg)
                except Exception:
                    pass

                self._spawn_temp_firetruck_triggered = True
                self._spawn_temp_firetruck_active = False
                print("[Scenario03] SPAWN_TEMP_BARRIER_FIRETRUCK trigger reached and spawned.")
                return True

        return False

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
        # After destroying temp firetruck barriers, activate L-truck navigation barrier triggers
        try:
            self._start_ltruck_navigation_barriers()
        except Exception:
            pass

    def _start_ltruck_navigation_barriers(self):
        if self._ltruck_nav_barriers_active or not self._ltruck_nav_barrier_configs:
            return
        self._ltruck_nav_barriers_active = True
        print("[Scenario03] LTRUCK_NAVIGATION_BARRIER_CONFIGS triggers activated!")

    def _draw_ltruck_navigation_barrier_boxes(self):
        if not DEBUG_MODE or not self._ltruck_nav_barriers_active:
            return
        if not self._ltruck_nav_barrier_configs:
            return
        box_configs = build_trigger_box_configs(
            self._ltruck_nav_barrier_configs,
            z_extra=2.0,
            color=(255, 255, 0, 255),
            thickness=0.1,
        )
        # print("Draw trigger box!")
        draw_trigger_boxes(self.world, box_configs, life_time=self._debug_trigger_box_lifetime)

    def _check_and_spawn_ltruck_nav_barrier(self, hero_location, hero_velocity=None):
        if not self._ltruck_nav_barriers_active or not self._ltruck_nav_barrier_configs:
            return False

        for cfg in self._ltruck_nav_barrier_configs:
            if not isinstance(cfg, dict):
                continue
            name = cfg.get("name")
            if name in self._ltruck_nav_barriers_triggered_keys:
                continue

            trigger_location = cfg.get("trigger_location")
            if trigger_location is None:
                continue

            if abs(hero_location.x - trigger_location.x) > cfg.get("trigger_x_tolerance", 0.0):
                continue
            if abs(hero_location.y - trigger_location.y) > cfg.get("trigger_y_tolerance", 0.0):
                continue

            required_axis = cfg.get("trigger_direction_axis")
            required_sign = cfg.get("trigger_direction_sign")
            if required_axis is not None and required_sign is not None:
                if hero_velocity is None:
                    continue
                axis_velocity = hero_velocity.x if required_axis == "x" else hero_velocity.y if required_axis == "y" else None
                if axis_velocity is None:
                    continue
                if axis_velocity * required_sign <= 0.0:
                    continue

            # Spawn spawn_configs for this barrier
            spawned_ids = []
            bp_lib = self.world.get_blueprint_library()
            for prop in cfg.get("spawn_configs", []):
                blueprint_ids = prop.get("blueprints", [])
                transform = prop.get("transform")
                if transform is None or not blueprint_ids:
                    continue
                bp = None
                for bid in blueprint_ids:
                    try:
                        bp = bp_lib.find(bid)
                        break
                    except Exception:
                        bp = None
                if bp is None:
                    print(f"[Scenario03] WARNUNG: Kein Blueprint für LTRUCK_NAVIGATION_BARRIER gefunden: {blueprint_ids}")
                    continue
                actor = self.world.try_spawn_actor(bp, transform)
                if actor is None:
                    print(f"[Scenario03] WARNUNG: LTRUCK_NAVIGATION_BARRIER spawn fehlgeschlagen | blueprint={bp.id}")
                    continue
                self._ltruck_nav_barrier_actor_ids.append(actor.id)
                spawned_ids.append(actor.id)
                print(f"[Scenario03] LTRUCK_NAVIGATION_BARRIER gespawnt: id={actor.id}, blueprint={bp.id}")

            # mark triggered and deactivate listening for further triggers if desired
            try:
                if name:
                    self._ltruck_nav_barriers_triggered_keys.add(name)
            except Exception:
                pass

            # schedule destruction after 30s
            if spawned_ids:
                try:
                    t = threading.Timer(30.0, lambda ids=spawned_ids: self._destroy_ltruck_navigation_barrier_actors(ids))
                    t.daemon = True
                    t.start()
                except Exception:
                    pass

            # stop listening after first trigger (per requirement)
            self._ltruck_nav_barriers_active = False
            return True

        return False

    def _destroy_ltruck_navigation_barrier_actors(self, actor_ids):
        if not actor_ids:
            return
        try:
            self.client.apply_batch([carla.command.DestroyActor(aid) for aid in list(actor_ids)])
        except Exception:
            pass
        for aid in actor_ids:
            try:
                if aid in self._ltruck_nav_barrier_actor_ids:
                    self._ltruck_nav_barrier_actor_ids.remove(aid)
            except Exception:
                pass
        print(f"[Scenario03] LTRUCK_NAVIGATION_BARRIER actors destroyed: {actor_ids}")

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
        try:
            if getattr(self, 'trigger_logger', None):
                self.trigger_logger.log_trigger('03', 'song_start', window_duration_seconds=SONG_PLAY_DURATION_SECONDS)
        except Exception:
            pass
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

        if self._copwaving_active_trigger_name is not None:
            return

        box_configs = build_trigger_box_configs(
            COPWAVING_TRIGGER_CONFIGS,
            z_extra=2.0,
            color=(255, 0, 0, 255),
            thickness=0.1,
        )
        draw_trigger_boxes(self.world, box_configs, life_time=self._debug_trigger_box_lifetime)

    def _destroy_actor_safely(self, actor_id):
        if actor_id is None:
            return

        try:
            actor = self.world.get_actor(actor_id)
            if actor is not None:
                actor.destroy()
            else:
                self.client.apply_batch([carla.command.DestroyActor(actor_id)])
        except Exception:
            pass

        if actor_id in self._static_actor_ids:
            try:
                self._static_actor_ids.remove(actor_id)
            except ValueError:
                pass
        if actor_id in self._vehicle_actor_ids:
            try:
                self._vehicle_actor_ids.remove(actor_id)
            except ValueError:
                pass

    def _spawn_copwaving_walker_controller(self, trigger_config, spawn_transform=None):
        spawn_location = trigger_config.get("spawn_location")
        target_location = trigger_config.get("target_location")
        target_location1 = trigger_config.get("target_location1")
        target_location2 = trigger_config.get("target_location2")
        blueprint_id_walk = trigger_config.get("blueprint_id_walk", "walker.pedestrian.0030")
        spawn_yaw = trigger_config.get("spawn_yaw", 0.0)

        if spawn_location is None or target_location is None:
            print("[Scenario03] WARNUNG: copWaving walker needs spawn_location and target_location.")
            return False

        bp_lib = self.world.get_blueprint_library()
        try:
            walker_bp = bp_lib.find(blueprint_id_walk)
        except Exception as exc:
            print(f"[Scenario03] WARNUNG: Blueprint {blueprint_id_walk} nicht gefunden: {exc}")
            return False

        if walker_bp.has_attribute("is_invincible"):
            try:
                walker_bp.set_attribute("is_invincible", "false")
            except Exception:
                pass

        # build target list
        targets = []
        if target_location1 is not None and target_location2 is not None:
            targets = [self._snap_location_to_navigation(target_location1), self._snap_location_to_navigation(target_location2)]
        elif target_location is not None:
            targets = [self._snap_location_to_navigation(target_location)]

        if not targets:
            print("[Scenario03] WARNUNG: copWaving walker needs at least one target_location.")
            return False

        # log first target
        t0 = targets[0]
        print(
            f"[Scenario03] copWaving switching to walking model | blueprint={blueprint_id_walk} | "
            f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f}) | "
            f"target=({t0.x:.2f}, {t0.y:.2f}, {t0.z:.2f})"
        )

        if spawn_transform is None:
            walker_transform = carla.Transform(
                carla.Location(x=spawn_location.x, y=spawn_location.y, z=spawn_location.z),
                carla.Rotation(pitch=0.0, yaw=spawn_yaw if spawn_yaw is not None else 0.0, roll=0.0),
            )
        else:
            walker_transform = carla.Transform(
                carla.Location(
                    x=spawn_transform.location.x,
                    y=spawn_transform.location.y,
                    z=spawn_transform.location.z,
                ),
                carla.Rotation(
                    pitch=spawn_transform.rotation.pitch,
                    yaw=spawn_transform.rotation.yaw,
                    roll=spawn_transform.rotation.roll,
                ),
            )
        walker_actor = self.world.try_spawn_actor(walker_bp, walker_transform)
        if walker_actor is None:
            print(
                f"[Scenario03] WARNUNG: Walker-Spawn fehlgeschlagen | blueprint={blueprint_id_walk}, "
                f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
            )
            return False

        self._copwaving_walk_actor_id = walker_actor.id
        self._copwaving_walk_controller_id = None
        self._copwaving_walk_started = True
        self._copwaving_target_locations = targets
        self._copwaving_current_target_idx = 0
        self._copwaving_target_location = self._copwaving_target_locations[0]
        self._copwaving_last_update_time = None
        self._copwaving_last_status_log_time = None
        self._static_actor_ids.append(walker_actor.id)
        print(
            f"[Scenario03] copWaving walker spawned: walker_id={walker_actor.id}, "
            f"speed={COPWAVING_WALK_SPEED:.2f} m/s"
        )
        return True

    def _transition_copwaving_to_walk(self, trigger_config, wave_actor, wave_transform):
        if trigger_config is None or wave_actor is None or wave_transform is None:
            return False

        spawn_location = carla.Location(
            x=wave_transform.location.x,
            y=wave_transform.location.y,
            z=wave_transform.location.z,
        )
        spawn_rotation = carla.Rotation(
            pitch=wave_transform.rotation.pitch,
            yaw=wave_transform.rotation.yaw,
            roll=wave_transform.rotation.roll,
        )
        spawn_transform = carla.Transform(spawn_location, spawn_rotation)
        blueprint_id_walk = trigger_config.get("blueprint_id_walk", "walker.pedestrian.0030")

        bp_lib = self.world.get_blueprint_library()
        try:
            walker_bp = bp_lib.find(blueprint_id_walk)
        except Exception as exc:
            print(f"[Scenario03] WARNUNG: Blueprint {blueprint_id_walk} nicht gefunden für Transition: {exc}")
            return False

        if walker_bp.has_attribute("is_invincible"):
            try:
                walker_bp.set_attribute("is_invincible", "false")
            except Exception:
                pass

        print(
            f"[Scenario03] copWaving transactional swap prepared | old_id={wave_actor.id} | "
            f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f}) | "
            f"blueprint={blueprint_id_walk}"
        )

        batch = [
            carla.command.DestroyActor(wave_actor.id),
            carla.command.SpawnActor(walker_bp, spawn_transform),
        ]

        new_actor = None
        try:
            responses = self.client.apply_batch_sync(batch, False)
        except Exception as exc:
            print(f"[Scenario03] WARNUNG: copWaving batch swap failed: {exc}")
            responses = []

        if len(responses) >= 2 and not responses[1].error:
            try:
                new_actor = self.world.get_actor(responses[1].actor_id)
            except Exception:
                new_actor = None
        else:
            if len(responses) >= 2 and responses[1].error:
                print(f"[Scenario03] WARNUNG: copWaving batch spawn error: {responses[1].error}")

            print("[Scenario03] copWaving batch swap fallback -> direct spawn after destroy")
            new_actor = self.world.try_spawn_actor(walker_bp, spawn_transform)

        if new_actor is None:
            print(
                f"[Scenario03] WARNUNG: copWaving transition failed completely | "
                f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
            )
            return False

        self._copwaving_walk_actor_id = new_actor.id
        self._copwaving_walk_controller_id = None
        self._copwaving_walk_started = True
        # handle multiple sequential targets if provided
        t1 = trigger_config.get("target_location1")
        t2 = trigger_config.get("target_location2")
        t_single = trigger_config.get("target_location")
        targets = []
        if t1 is not None and t2 is not None:
            targets = [self._snap_location_to_navigation(t1), self._snap_location_to_navigation(t2)]
        elif t_single is not None:
            targets = [self._snap_location_to_navigation(t_single)]
        else:
            targets = []

        if not targets:
            print("[Scenario03] WARNUNG: copWaving transition has no target(s).")
            return False

        self._copwaving_target_locations = targets
        self._copwaving_current_target_idx = 0
        self._copwaving_target_location = self._copwaving_target_locations[0]
        self._copwaving_last_update_time = None
        self._copwaving_last_status_log_time = None
        self._static_actor_ids.append(new_actor.id)

        if self._copwaving_active_trigger_name in self._copwaving_spawn_time:
            self._copwaving_spawn_time.pop(self._copwaving_active_trigger_name, None)
        self._copwaving_wave_actor_id = None

        print(
            f"[Scenario03] copWaving walker spawned after swap: walker_id={new_actor.id}, "
            f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f}), "
            f"target=({self._copwaving_target_location.x:.2f}, {self._copwaving_target_location.y:.2f}, {self._copwaving_target_location.z:.2f})"
        )
        return True

    def _start_copwaving_trigger(self, trigger_config, sim_time):
        if trigger_config is None:
            return False

        trigger_name = trigger_config.get("name")
        if trigger_name in self._copwaving_triggered_keys:
            return False

        if not self._spawn_copwaving_pedestrian(trigger_config):
            return False

        self._copwaving_triggered_keys.add(trigger_name)
        self._copwaving_active_trigger_name = trigger_name
        self._copwaving_active_trigger_config = trigger_config
        self._copwaving_wave_actor_id = self._copwaving_actor_ids.get(trigger_name)
        self._copwaving_spawn_time[trigger_name] = sim_time
        # record phase start so we can enforce a maximum lifetime
        try:
            self._copwaving_phase_start_time = float(sim_time)
        except Exception:
            self._copwaving_phase_start_time = sim_time
        try:
            if getattr(self, 'trigger_logger', None):
                self.trigger_logger.log_trigger('04', 'police', window_duration_seconds=10.0)
        except Exception:
            pass
        print(f"[Scenario03] {trigger_name} aktiviert -> policeman waving actor_id={self._copwaving_wave_actor_id}")
        return True

    def _destroy_copwaving_wave_actor(self):
        if self._copwaving_wave_actor_id is None:
            return

        actor_id = self._copwaving_wave_actor_id
        self._copwaving_wave_actor_id = None
        self._destroy_actor_safely(actor_id)
        if self._copwaving_active_trigger_name in self._copwaving_spawn_time:
            self._copwaving_spawn_time.pop(self._copwaving_active_trigger_name, None)
        print(f"[Scenario03] copWaving waving actor destroyed: id={actor_id}")

    def _finish_copwaving_phase(self):
        self._destroy_copwaving_wave_actor()
        self._destroy_actor_safely(self._copwaving_walk_controller_id)
        self._destroy_actor_safely(self._copwaving_walk_actor_id)
        self._copwaving_walk_controller_id = None
        self._copwaving_walk_actor_id = None
        self._copwaving_walk_started = False
        self._copwaving_target_location = None
        self._copwaving_last_update_time = None
        self._copwaving_last_status_log_time = None
        self._copwaving_transition_pending = False
        self._copwaving_transition_spawn_transform = None
        self._copwaving_active_trigger_name = None
        self._copwaving_active_trigger_config = None
        self._copwaving_phase_start_time = None
        self.police_finished = True
        self.police_active = False
        print("[Scenario03] copWaving finished -> police phase completed.")

    def _update_copwaving_walk(self, sim_time):
        if not self._copwaving_walk_started or self._copwaving_walk_actor_id is None:
            return

        walker = self.world.get_actor(self._copwaving_walk_actor_id)
        target_location = self._copwaving_target_location
        if walker is None or target_location is None:
            print(
                f"[Scenario03] WARNUNG: copWaving walk aborted - walker or target missing | "
                f"walker_id={self._copwaving_walk_actor_id}, target={target_location}"
            )
            self._finish_copwaving_phase()
            return

        if self._copwaving_last_update_time is None:
            delta_time = SIM_STEP_S
        else:
            delta_time = max(0.0, sim_time - self._copwaving_last_update_time)
            if delta_time == 0.0:
                delta_time = SIM_STEP_S
        self._copwaving_last_update_time = sim_time

        try:
            current_location = walker.get_location()
        except Exception as exc:
            print(f"[Scenario03] WARNUNG: copWaving walker location konnte nicht gelesen werden: {exc}")
            self._finish_copwaving_phase()
            return

        distance = current_location.distance(target_location)
        if self._copwaving_last_status_log_time is None or (sim_time - self._copwaving_last_status_log_time) >= COPWAVING_STATUS_LOG_INTERVAL_S:
            self._copwaving_last_status_log_time = sim_time
            print(
                f"[Scenario03] copWaving move tick | sim_time={sim_time:.2f}s | dt={delta_time:.3f}s | "
                f"dist={distance:.2f}m | current=({current_location.x:.2f}, {current_location.y:.2f}, {current_location.z:.2f}) | "
                f"target=({target_location.x:.2f}, {target_location.y:.2f}, {target_location.z:.2f})"
            )

        if distance <= COPWAVING_ARRIVE_THRESH:
            # if multiple targets are defined, advance to the next one
            if self._copwaving_target_locations and self._copwaving_current_target_idx < (len(self._copwaving_target_locations) - 1):
                self._copwaving_current_target_idx += 1
                self._copwaving_target_location = self._copwaving_target_locations[self._copwaving_current_target_idx]
                print(
                    f"[Scenario03] copWaving walker reached intermediate target and moving to next | walker_id={walker.id} | sim_time={sim_time:.2f}s | "
                    f"next_target=({self._copwaving_target_location.x:.2f}, {self._copwaving_target_location.y:.2f}, {self._copwaving_target_location.z:.2f})"
                )
                return

            print(
                f"[Scenario03] copWaving walker reached final target | walker_id={walker.id} | sim_time={sim_time:.2f}s | "
                f"distance={distance:.2f}m"
            )
            self._finish_copwaving_phase()
            return

        direction_x = target_location.x - current_location.x
        direction_y = target_location.y - current_location.y
        direction_length = math.hypot(direction_x, direction_y)
        if direction_length == 0.0:
            print(f"[Scenario03] WARNUNG: copWaving direction length is zero for walker_id={walker.id}")
            self._finish_copwaving_phase()
            return

        try:
            walker.apply_control(
                carla.WalkerControl(
                    direction=carla.Vector3D(x=direction_x / direction_length, y=direction_y / direction_length, z=0.0),
                    speed=COPWAVING_WALK_SPEED,
                    jump=False,
                )
            )
        except Exception:
            print(
                f"[Scenario03] WARNUNG: copWaving walker control failed | walker_id={walker.id} | "
                f"sim_time={sim_time:.2f}s | speed={COPWAVING_WALK_SPEED:.2f}"
            )
            self._finish_copwaving_phase()

    def _update_copwaving_phase(self, sim_time, hero_location, hero_velocity):
        if not self.police_active or self.police_finished:
            return

        self._draw_copwaving_trigger_boxes()

        if self._copwaving_active_trigger_name is None:
            copwaving_config = None
            if TEST_INSTANT_TRIGGER_COP:
                copwaving_config = COPWAVING_TRIGGER_CONFIGS[cop_spawn_idx] if COPWAVING_TRIGGER_CONFIGS else None
            elif hero_location is not None:
                copwaving_config = self._get_copwaving_trigger_config(hero_location, hero_velocity)

            if copwaving_config is not None:
                self._start_copwaving_trigger(copwaving_config, sim_time)
            return

        if self._copwaving_wave_actor_id is not None:
            trigger_name = self._copwaving_active_trigger_name
            spawn_time = self._copwaving_spawn_time.get(trigger_name)
            if spawn_time is not None and (sim_time - spawn_time) >= cop_wave_duration:
                wave_actor = self.world.get_actor(self._copwaving_wave_actor_id)
                wave_transform = None
                if wave_actor is not None:
                    try:
                        wave_transform = wave_actor.get_transform()
                    except Exception:
                        wave_transform = None

                print(
                    f"[Scenario03] copWaving waving phase elapsed | trigger={trigger_name} | "
                    f"sim_time={sim_time:.2f}s | swapping immediately in one batch"
                )
                trigger_config = self._copwaving_active_trigger_config
                if trigger_config is not None and wave_transform is not None:
                    if self._transition_copwaving_to_walk(trigger_config, wave_actor, wave_transform):
                        return
                    print("[Scenario03] WARNUNG: copWaving transactional swap failed, keeping phase active for retry.")
                return

        if self._copwaving_wave_actor_id is None and not self._copwaving_walk_started:
            trigger_config = self._copwaving_active_trigger_config
            if trigger_config is not None:
                self._spawn_copwaving_walker_controller(trigger_config)
            return

        self._update_copwaving_walk(sim_time)

        # enforce maximum copWaving lifetime so scenario cannot get stuck
        try:
            if self._copwaving_phase_start_time is not None:
                if (sim_time - self._copwaving_phase_start_time) >= float(COPWAVING_LIFETIME_S):
                    print(
                        f"[Scenario03] copWaving lifetime exceeded ({COPWAVING_LIFETIME_S}s) -> forcing finish | sim_time={sim_time:.2f}s"
                    )
                    self._finish_copwaving_phase()
                    return
        except Exception:
            pass

    def _get_copwaving_trigger_config(self, hero_location, hero_velocity=None):
        if hero_location is None:
            return None
        
        for trigger_config in COPWAVING_TRIGGER_CONFIGS:
            trigger_name = trigger_config.get("name")
            
            # skip triggers that already fired once
            if trigger_name in self._copwaving_triggered_keys:
                continue
            
            trigger_location = trigger_config["trigger_location"]
            
            if abs(hero_location.x - trigger_location.x) > trigger_config["trigger_x_tolerance"]:
                continue
            if abs(hero_location.y - trigger_location.y) > trigger_config["trigger_y_tolerance"]:
                continue

            required_axis = trigger_config.get("trigger_direction_axis")
            required_sign = trigger_config.get("trigger_direction_sign")
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

        walker_bp = self.world.get_blueprint_library().find(blueprint_id)
        if walker_bp is None:
            print(f"[Scenario03] WARNUNG: Blueprint {blueprint_id} nicht gefunden für {trigger_name}")
            return False
        
        if walker_bp.has_attribute("is_invincible"):
            walker_bp.set_attribute("is_invincible", "false")
  
        rotation = carla.Rotation(pitch=0.0, yaw=spawn_yaw if spawn_yaw is not None else 0.0, roll=0.0)
        transform = carla.Transform(spawn_location, rotation)

        actor = self.world.try_spawn_actor(walker_bp, transform)
        if actor is None:
            print(
                f"[Scenario03] WARNUNG: {trigger_name} konnte nicht gespawnt werden | "
                f"blueprint={blueprint_id}, spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
            )
            return False
        
        self._copwaving_triggered_keys.add(trigger_name)
        self._copwaving_actor_ids[trigger_name] = actor.id
        self._static_actor_ids.append(actor.id)
        
        print(
            f"[Scenario03] {trigger_name} (police waving) gespawnt: id={actor.id}, blueprint={blueprint_id}, "
            f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
        )
        return True

    def start_brake(self):
        if self.brake_finished:
            return
        print("[Scenario03] brake started!")
        if self._brake_signal_file:
            try:
                brake_signal_file = os.path.normpath(os.path.abspath(self._brake_signal_file))
                brake_dir = os.path.dirname(brake_signal_file)
                if brake_dir:
                    os.makedirs(brake_dir, exist_ok=True)
                with open(brake_signal_file, "w", encoding="utf-8") as brake_handle:
                    brake_handle.write("brake\n")
                print(f"[Scenario03] brake signal sent to manual_control: {brake_signal_file}")
            except Exception as exc:
                print(f"[Scenario03] WARNING: could not write brake signal file: {exc}")

        if not self._brake_warning_audio.play():
            print("[Scenario03] WARNING: brake warning sound konnte nicht gestartet werden.")
        try:
            if getattr(self, 'trigger_logger', None):
                self.trigger_logger.log_trigger('05', 'brake_warning', window_duration_seconds=BRAKE_TO_END_DELAY)
        except Exception:
            pass
        self.brake_finished = True

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

    def _skip_brake_trigger(self, sim_time):
        if self.brake_finished:
            return
        self._finish_delay_timer("police_to_brake", sim_time)
        self.brake_finished = True
        print("[Scenario03] brake trigger skipped.")

    def run(self):
        print("[Scenario03] Running...")
        world_settings = self.world.get_settings()
        print(
            f"[Scenario03] World settings | synchronous_mode={world_settings.synchronous_mode} | "
            f"fixed_delta_seconds={world_settings.fixed_delta_seconds}"
        )
        if run_in_singleFile_mode:
            #self.world.set_weather(carla.WeatherParameters.CloudyNight)
            self.world.set_weather(carla.WeatherParameters.CloudyNoon)        # CloudyNight
            print("[Scenario03] Weather set to CloudyNight for single-file mode")

        try:
            while True:
                self.world.wait_for_tick()
                sim_time = self.world.get_snapshot().timestamp.elapsed_seconds

                ego = self.find_hero()
                ego_location = ego.get_location() if ego else None
                ego_velocity = ego.get_velocity() if ego else None

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
                        # Trigger box activated for caraway -> log and spawn
                        try:
                            if getattr(self, 'trigger_logger', None):
                                self.trigger_logger.log_trigger('01', 'caraway', window_duration_seconds=10.0)
                        except Exception:
                            pass
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

                    # Draw and check SPAWN_TEMP_BARRIER_FIRETRUCK triggers (activated when ltruck spawns)
                    if self._spawn_temp_firetruck_active and not self._spawn_temp_firetruck_triggered:
                        self._draw_spawn_temp_firetruck_boxes()
                        if ego_location is not None and self._spawn_temp_firetruck_reached(ego_location, ego_velocity):
                            # spawning handled inside _spawn_temp_firetruck_reached
                            pass

                    if caraway_to_ltruck["finished"] and self._temp_firetruck_trigger_triggered and not self.ltruck_active and not self.ltruck_finished:
                        if not self._trigger_ltruck:
                            self._skip_ltruck_trigger(sim_time)
                        else:
                            self.start_ltruck()

                    self._draw_ltruck_trigger_boxes()

                    if self.ltruck_active and not self.ltruck_finished:
                        config = None
                        if TEST_INSTANT_TRIGGER_LTRUCK:
                            # For instant-test mode, pick the first LTRUCK config that hasn't fired yet
                            config = None
                            if LTRUCK_SPAWN_CONFIGS:
                                for c in LTRUCK_SPAWN_CONFIGS:
                                    name = c.get("name")
                                    if name in self._ltruck_triggered_keys:
                                        continue
                                    config = c
                                    break
                        elif ego_location:
                            config = self._get_ltruck_config(ego_location, ego_velocity)

                        if config:
                            # L-truck trigger detected -> start hold timer once and immediately set pinned TLs to Red
                            try:
                                if self._ltruck_tl_hold_start is None:
                                    self._ltruck_tl_hold_start = time.time()
                                    try:
                                        max_dur = max(self._pinned_traffic_light_durations.values()) if self._pinned_traffic_light_durations else 0.0
                                    except Exception:
                                        max_dur = 0.0
                                    print(f"[Scenario03] LTruck trigger detected - holding pinned traffic lights red for {max_dur}s")
                                    # immediately set pinned TL actors to Red:
                                    for tl in self._all_traffic_lights:
                                        try:
                                            if getattr(tl, 'id', None) in self._pinned_traffic_light_ids:
                                                tl.set_state(carla.TrafficLightState.Red)
                                        except Exception:
                                            pass
                            except Exception:
                                pass

                            # Log LTruck trigger at the moment the trigger box is detected
                            try:
                                if getattr(self, 'trigger_logger', None):
                                    self.trigger_logger.log_trigger('02', 'ltruck', window_duration_seconds=30.0)
                            except Exception:
                                pass

                            if self._start_ltruck_manual_control_from_config(config):
                                self.ltruck_finished = True
                # Draw and check LTRUCK navigation barrier triggers (activated after temp firetruck barriers destroyed)
                if self._ltruck_nav_barriers_active:
                    self._draw_ltruck_navigation_barrier_boxes()
                    if ego_location is not None and self._check_and_spawn_ltruck_nav_barrier(ego_location, ego_velocity):
                        # handled inside method (spawns and schedules destruction)
                        pass
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

                self._update_copwaving_phase(sim_time, ego_location, ego_velocity)

                if self.police_finished:
                    police_to_brake = self._delay_states["police_to_brake"]
                    if police_to_brake["started_at"] is None:
                        self._start_delay_timer("police_to_brake", sim_time)
                    self._update_delay_timer("police_to_brake", sim_time)

                    if police_to_brake["finished"] and not self.brake_finished:
                        if not self._trigger_brake:
                            self._skip_brake_trigger(sim_time)
                        else:
                            self.start_brake()

                if self.brake_finished:
                    brake_to_end = self._delay_states["brake_to_end"]
                    if brake_to_end["started_at"] is None:
                        self._start_delay_timer("brake_to_end", sim_time)
                    self._update_delay_timer("brake_to_end", sim_time)

                    if brake_to_end["finished"]:
                        self._scenario_done = True

                if ego:
                    self.update_blinking_lights(sim_time)

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
            self._copwaving_spawn_time.clear()
            self._copwaving_actor_ids.clear()
            self._copwaving_active_trigger_name = None
            self._copwaving_active_trigger_config = None
            self._copwaving_wave_actor_id = None
            self._copwaving_walk_actor_id = None
            self._copwaving_walk_controller_id = None
            self._copwaving_walk_started = False
            self._copwaving_target_location = None
            self._destroy_temp_firetruck_barriers()
            self._brake_warning_audio.stop(0)
        except Exception:
            pass

        # Remove stale brake signal file so the next run starts clean.
        if self._brake_signal_file:
            try:
                brake_signal_file = os.path.normpath(os.path.abspath(self._brake_signal_file))
                if os.path.exists(brake_signal_file):
                    os.remove(brake_signal_file)
                    print(f"[Scenario03] brake signal file removed during destroy: {brake_signal_file}")
            except Exception as exc:
                print(f"[Scenario03] WARNING: could not remove brake signal file during destroy: {exc}")

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
    parser.add_argument('--logging', default=None, help='pass participant and scenario token, e.g. "(P_01_...,S01)"')
    args = parser.parse_args()

    Scenario03Runner(
        args.host,
        args.port,
        args.tm_port,
        args.done_file,
        args.logging,
        trigger_caraway=TRIGGER_CARAWAY,
        trigger_ltruck=TRIGGER_LTRUCK,
        trigger_song=TRIGGER_SONG,
        trigger_police=TRIGGER_POLICE,
        trigger_brake=TRIGGER_BRAKE,
    ).run()
