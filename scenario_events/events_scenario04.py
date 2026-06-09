#!/usr/bin/env python

#import logging
import os
import random
import threading
import time
import argparse
import carla
try:
    from scenario_helper import (
        is_transform_hidden_from_hero,
        pick_hidden_navigation_location,
        pick_navigation_location,
        get_random_pedestrian_blueprint,
        build_trigger_box_configs,
        draw_trigger_boxes,
    )
except ModuleNotFoundError:
    from scenario_events.scenario_helper import (
        is_transform_hidden_from_hero,
        pick_hidden_navigation_location,
        pick_navigation_location,
        get_random_pedestrian_blueprint,
        build_trigger_box_configs,
        draw_trigger_boxes,
    )
try:
    from events_scenario04_static_props import STATIC_PROP_SPAWNS, PEDESTRIAN_START_LOCATIONS, CATSITTING_TRIGGER_CONFIGS
except ModuleNotFoundError:
    from scenario_events.events_scenario04_static_props import STATIC_PROP_SPAWNS, PEDESTRIAN_START_LOCATIONS, CATSITTING_TRIGGER_CONFIGS
from common.audio_paths import HAPPINESS_RP_UPTOWN_FUNK_PATH
from generate_audio import SongAudio

# Constants
START_TO_ANIMCAT_DELAY_SECONDS = 30.0
ANIMCAT_TO_SONG_DELAY_SECONDS = 20.0
SONG_TO_DANCINGM_DELAY_SECONDS = 30.0
DANCINGM_TO_END_DELAY_SECONDS = 20.0

SONG_START_OFFSET_SECONDS = 30.0
SONG_PLAY_DURATION_SECONDS = 30.0
SONG_FADE_IN_MS = 3000
SONG_FADE_OUT_MS = 3000
HERO_GREEN_LIGHT_HOLD_SECONDS = 10.0
SPAWN_CARS = 15                              # 15?
ENABLE_ROUTE_PEDESTRIANS = True
PEDESTRIAN_MAX_SPEED = 3.5
PEDESTRIAN_COUNT = 15                        # 15? 24 = no pedestrian walks
PEDESTRIAN_ARRIVE_THRESH = 1.0
ANIMCAT_SIT_SECONDS = 15.0
SIM_STEP_S = 0.05

DEBUG_MODE = False

BLOCKED_VEHICLE_KEYWORDS = (
    "firetruck", "ambulance", "bus", "fusorosa", "carlacola", "truck", "european_hgv", "t2",
)

MIN_SPAWN_DISTANCE = 40.0
MAX_SPAWN_DISTANCE = 150.0
PEDESTRIAN_MIN_HIDDEN_DISTANCE = 2.0
PEDESTRIAN_MAX_HIDDEN_DISTANCE = 500.0
PEDESTRIAN_MIN_ROUTE_DISTANCE = 5.0
PEDESTRIAN_NAV_SAMPLES = 96
DANCINGM_PEDESTRIAN_BLUEPRINT_ID = "walker.pedestrian.0054"
DANCINGM_MAX_DISTANCE = 50.0
DANCINGM_MIN_DISTANCE = 0.0
DANCINGM_SEARCH_SAMPLES = 128
DANCINGM_SPAWN_CLEARANCE_METERS = 2.0
DANCINGM_SPAWN_HEIGHT_OFFSET = 1.0
DANCINGM_MAX_SPAWN_ATTEMPTS = 12
DANCINGM_VISIBLE_SECONDS = 60.0
DANCINGM_SPAWN_MAX_WAIT_SECONDS = 20.0
DANCINGM_PREFERRED_AHEAD_DISTANCE = 50.0
DANCINGM_AHEAD_SEARCH_RADIUS = 20.0
DANCINGM_FORWARD_MIN_DISTANCE = 45.0
DANCINGM_FORWARD_MAX_DISTANCE = 55.0
DANCINGM_TRAFFIC_LIGHT_LOOKAHEAD_METERS = 90.0
DANCINGM_TRAFFIC_LIGHT_SPAWN_RADIUS = 18.0
DANCINGM_TRAFFIC_LIGHT_RED_HOLD_SECONDS = 10.0
DANCINGM_TRAFFIC_LIGHT_GREEN_RELEASE_SECONDS = 10.0

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
        self._animcat_spawned = False
        self._animcat_actor_id = None
        self._animcat_spawn_time = None
        self._animcat_destroy_time = None
        self._animcat_active_trigger_name = None
        self._animcat_triggered_keys = set()
        self._animcat_finished = False
        self._animcat_waiting_logged = False
        self._dancingm_pedestrian_spawned = False
        self._dancingm_pedestrian_actor_id = None
        self._dancingm_pedestrian_spawn_time = None
        self._dancingm_spawn_last_warning_time = None
        self._dancingm_traffic_light_actor_id = None
        self._dancingm_traffic_light_original_state = None
        self._dancingm_traffic_light_forced_time = None
        self._dancingm_confirmation_pending = False
        self._dancingm_confirmation_listener_started = False
        self._dancingm_confirmation_response = None
        self._dancingm_release_active = False
        self._dancingm_release_start_time = None
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
        self._debug_trigger_box_lifetime = SIM_STEP_S * 2.0
        
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

    def _draw_animcat_trigger_boxes(self):
        if not DEBUG_MODE or self._animcat_finished or self._animcat_active_trigger_name is not None:
            return

        box_configs = build_trigger_box_configs(
            CATSITTING_TRIGGER_CONFIGS,
            z_extra=2.0,
            color=(255, 0, 0, 255),
            thickness=0.1,
        )
        draw_trigger_boxes(self.world, box_configs, life_time=self._debug_trigger_box_lifetime)

    def _get_animcat_trigger_config(self, hero_location, hero_velocity=None):
        if hero_location is None:
            return None

        for trigger_config in CATSITTING_TRIGGER_CONFIGS:
            trigger_location = trigger_config.get("trigger_location")
            if trigger_location is None:
                continue

            if abs(hero_location.x - trigger_location.x) > float(trigger_config.get("trigger_x_tolerance", 0.0)):
                continue
            if abs(hero_location.y - trigger_location.y) > float(trigger_config.get("trigger_y_tolerance", 0.0)):
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

            required_axis_2 = trigger_config.get("trigger_direction_axis_2")
            required_sign_2 = trigger_config.get("trigger_direction_sign_2")
            if required_axis_2 is not None and required_sign_2 is not None:
                if hero_velocity is None:
                    continue
                if required_axis_2 == "x":
                    axis_velocity_2 = hero_velocity.x
                elif required_axis_2 == "y":
                    axis_velocity_2 = hero_velocity.y
                else:
                    continue
                if axis_velocity_2 * required_sign_2 <= 0.0:
                    continue

            return trigger_config

        return None

    def _spawn_animcat_from_config(self, trigger_config):
        if trigger_config is None:
            return False

        trigger_name = trigger_config.get("name", "unknown")
        if trigger_name in self._animcat_triggered_keys:
            return False

        spawn_location = trigger_config.get("spawn_location")
        blueprint_id = trigger_config.get("blueprint_id", "walker.pedestrian.0060")
        spawn_yaw = trigger_config.get("spawn_yaw", 0.0)

        if spawn_location is None:
            print(f"[Scenario04] WARNUNG: Keine spawn_location für {trigger_name}")
            return False

        bp_lib = self.world.get_blueprint_library()
        try:
            walker_bp = bp_lib.find(blueprint_id)
        except Exception as exc:
            print(f"[Scenario04] WARNUNG: Blueprint {blueprint_id} nicht gefunden für {trigger_name}: {exc}")
            return False

        if walker_bp.has_attribute("is_invincible"):
            try:
                walker_bp.set_attribute("is_invincible", "false")
            except Exception:
                pass

        transform = carla.Transform(
            spawn_location,
            carla.Rotation(pitch=0.0, yaw=spawn_yaw if spawn_yaw is not None else 0.0, roll=0.0),
        )
        actor = self.world.try_spawn_actor(walker_bp, transform)
        if actor is None:
            print(
                f"[Scenario04] WARNUNG: {trigger_name} konnte nicht gespawnt werden | "
                f"blueprint={blueprint_id}, spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
            )
            return False

        try:
            if hasattr(actor, "set_target_velocity"):
                actor.set_target_velocity(carla.Vector3D(0.0, 0.0, 0.0))
            if hasattr(actor, "set_target_angular_velocity"):
                actor.set_target_angular_velocity(carla.Vector3D(0.0, 0.0, 0.0))
            if hasattr(actor, "set_simulate_physics"):
                actor.set_simulate_physics(False)
        except Exception:
            pass

        self._walker_actor_ids.append(actor.id)
        self._animcat_spawned = True
        self._animcat_actor_id = actor.id
        self._animcat_spawn_time = self.world.get_snapshot().timestamp.elapsed_seconds
        self._animcat_destroy_time = None
        self._animcat_active_trigger_name = trigger_name

        print(
            f"[Scenario04] {trigger_name} aktiviert -> ANIMCAT gespawnt: id={actor.id}, blueprint={blueprint_id}, "
            f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
        )
        return True

    def _start_animcat_trigger(self, trigger_config, sim_time):
        if trigger_config is None:
            return False

        trigger_name = trigger_config.get("name", "unknown")
        if trigger_name in self._animcat_triggered_keys:
            return False

        if not self._spawn_animcat_from_config(trigger_config):
            return False

        self._animcat_triggered_keys.add(trigger_name)
        self._animcat_active_trigger_name = trigger_name
        self._animcat_spawn_time = sim_time
        self._animcat_finished = False
        return True

    def _destroy_animcat_actor(self, sim_time):
        if self._animcat_actor_id is None:
            return

        actor_id = self._animcat_actor_id
        self._animcat_actor_id = None

        try:
            actor = self.world.get_actor(actor_id)
            if actor is not None:
                actor.destroy()
            else:
                self.client.apply_batch([carla.command.DestroyActor(actor_id)])
        except Exception:
            pass

        if actor_id in self._walker_actor_ids:
            try:
                self._walker_actor_ids.remove(actor_id)
            except ValueError:
                pass

        self._animcat_destroy_time = sim_time
        self._animcat_active_trigger_name = None
        self._animcat_finished = True
        print(f"[Scenario04] ANIMCAT destroyed: id={actor_id}")

    def _update_animcat(self, sim_time, hero_location, hero_velocity=None):
        if self._animcat_finished:
            return

        if self._start_sim_time is None:
            return

        if (sim_time - self._start_sim_time) < START_TO_ANIMCAT_DELAY_SECONDS:
            return

        if self._animcat_active_trigger_name is None:
            if not self._animcat_waiting_logged:
                print("[Scenario04] Waiting for cat trigger...", flush=True)
                self._animcat_waiting_logged = True

            self._draw_animcat_trigger_boxes()

            trigger_config = self._get_animcat_trigger_config(hero_location, hero_velocity)
            if trigger_config is not None:
                self._start_animcat_trigger(trigger_config, sim_time)
            return

        if self._animcat_actor_id is None or self._animcat_spawn_time is None:
            return

        if (sim_time - self._animcat_spawn_time) >= ANIMCAT_SIT_SECONDS:
            self._destroy_animcat_actor(sim_time)

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

    def _find_upcoming_traffic_light(self, ego_transform, lookahead_meters=DANCINGM_TRAFFIC_LIGHT_LOOKAHEAD_METERS):
        if ego_transform is None:
            return None

        ego_location = ego_transform.location
        ego_forward = ego_transform.get_forward_vector()
        best_light = None
        best_distance = None

        for landmark in self.world.get_map().get_all_landmarks_of_type('1000001'):
            if landmark.id == '':
                continue

            traffic_light = self.world.get_traffic_light(landmark)
            if traffic_light is None:
                continue

            light_location = traffic_light.get_transform().location
            dx = light_location.x - ego_location.x
            dy = light_location.y - ego_location.y
            dz = light_location.z - ego_location.z
            distance = (dx * dx + dy * dy + dz * dz) ** 0.5
            if distance > lookahead_meters:
                continue

            forward_dot = ego_forward.x * dx + ego_forward.y * dy + ego_forward.z * dz
            if forward_dot <= 0.0:
                continue

            if best_distance is None or distance < best_distance:
                best_light = traffic_light
                best_distance = distance

        return best_light

    def _find_sidewalk_spawn_transform(self, ego_transform, center_location=None, ahead_distance=DANCINGM_PREFERRED_AHEAD_DISTANCE, search_radius=DANCINGM_AHEAD_SEARCH_RADIUS, min_distance=DANCINGM_MIN_DISTANCE, max_distance=DANCINGM_MAX_DISTANCE, min_forward_distance=DANCINGM_FORWARD_MIN_DISTANCE, max_forward_distance=DANCINGM_FORWARD_MAX_DISTANCE, used_locations=None):
        """Find a sidewalk spawn transform that stays in front of ego.

        If center_location is set, candidates are sampled near that point.
        Otherwise the search is centered ahead of the ego by ahead_distance.
        In both cases the candidate must remain within the forward distance band.
        """
        if ego_transform is None:
            return None

        used_locations = used_locations or []
        ego_location = ego_transform.location
        ego_forward = ego_transform.get_forward_vector()
        car_map = self.world.get_map()

        actor_locations = []
        for actor in self.world.get_actors():
            try:
                actor_locations.append(actor.get_location())
            except Exception:
                continue

        if center_location is not None:
            center = center_location
        else:
            center = carla.Location(
                x=ego_location.x + ego_forward.x * ahead_distance,
                y=ego_location.y + ego_forward.y * ahead_distance,
                z=ego_location.z,
            )

        for _ in range(DANCINGM_SEARCH_SAMPLES):
            location = self.world.get_random_location_from_navigation()
            if location is None:
                continue

            if center is not None and location.distance(center) > search_radius:
                continue

            if any(location.distance(existing) < PEDESTRIAN_MIN_ROUTE_DISTANCE for existing in used_locations):
                continue

            waypoint = car_map.get_waypoint(
                location,
                project_to_road=False,
                lane_type=carla.LaneType.Sidewalk,
            )
            if waypoint is None:
                continue

            waypoint_location = waypoint.transform.location
            dx = waypoint_location.x - ego_location.x
            dy = waypoint_location.y - ego_location.y
            dz = waypoint_location.z - ego_location.z
            forward_distance = ego_forward.x * dx + ego_forward.y * dy + ego_forward.z * dz
            if forward_distance < min_forward_distance or forward_distance > max_forward_distance:
                continue

            euclidean_distance = (dx * dx + dy * dy + dz * dz) ** 0.5
            if euclidean_distance < min_distance or euclidean_distance > max_distance:
                continue

            if any(waypoint_location.distance(existing) < DANCINGM_SPAWN_CLEARANCE_METERS for existing in actor_locations):
                continue

            spawn_location = carla.Location(
                x=waypoint_location.x,
                y=waypoint_location.y,
                z=waypoint_location.z + DANCINGM_SPAWN_HEIGHT_OFFSET,
            )
            base_rot = waypoint.transform.rotation
            rot = carla.Rotation(pitch=base_rot.pitch, yaw=base_rot.yaw + 90.0, roll=base_rot.roll)
            return carla.Transform(spawn_location, rot)

        return None

    def _spawn_stationary_pedestrian(self, blueprint_id, ego_transform, label, min_distance=DANCINGM_MIN_DISTANCE, max_distance=DANCINGM_MAX_DISTANCE, used_locations=None):
        walker_bp = self.world.get_blueprint_library().find(blueprint_id)
        if walker_bp.has_attribute("is_invincible"):
            walker_bp.set_attribute("is_invincible", "false")
        sim_time = self.world.get_snapshot().timestamp.elapsed_seconds
        # First try to spawn in front of the ego on the sidewalk
        front_transform = self._find_sidewalk_spawn_transform(
            ego_transform,
            ahead_distance=DANCINGM_PREFERRED_AHEAD_DISTANCE,
            search_radius=DANCINGM_AHEAD_SEARCH_RADIUS,
            min_distance=min_distance,
            max_distance=max_distance,
            used_locations=used_locations,
        )
        if front_transform is not None:
            actor = self.world.try_spawn_actor(walker_bp, front_transform)
            if actor is not None:
                self._walker_actor_ids.append(actor.id)
                print(
                    f"[Scenario04] {label} gespawnt (vor dem Auto): id={actor.id}, blueprint={blueprint_id}, "
                    f"spawn=({front_transform.location.x:.2f}, {front_transform.location.y:.2f}, {front_transform.location.z:.2f})"
                )
                return actor

        last_spawn_transform = None
        for _ in range(DANCINGM_MAX_SPAWN_ATTEMPTS):
            spawn_transform = self._find_sidewalk_spawn_transform(
                ego_transform,
                min_distance=min_distance,
                max_distance=max_distance,
                used_locations=used_locations,
            )
            if spawn_transform is None:
                continue

            last_spawn_transform = spawn_transform
            actor = self.world.try_spawn_actor(walker_bp, spawn_transform)
            if actor is not None:
                self._walker_actor_ids.append(actor.id)
                print(
                    f"[Scenario04] {label} gespawnt: id={actor.id}, blueprint={blueprint_id}, "
                    f"spawn=({spawn_transform.location.x:.2f}, {spawn_transform.location.y:.2f}, {spawn_transform.location.z:.2f})"
                )
                return actor

        if last_spawn_transform is None:
            if self._dancingm_spawn_last_warning_time is None or (sim_time - self._dancingm_spawn_last_warning_time) >= 10.0:
                print(
                    f"[Scenario04] WARNUNG: Kein Gehsteig-Spawnpunkt für {label} gefunden | "
                    f"max_distance={max_distance:.1f}m"
                )
                self._dancingm_spawn_last_warning_time = sim_time
        else:
            if self._dancingm_spawn_last_warning_time is None or (sim_time - self._dancingm_spawn_last_warning_time) >= 10.0:
                print(
                    f"[Scenario04] WARNUNG: {label} konnte nicht gespawnt werden | "
                    f"spawn=({last_spawn_transform.location.x:.2f}, {last_spawn_transform.location.y:.2f}, {last_spawn_transform.location.z:.2f})"
                )
                self._dancingm_spawn_last_warning_time = sim_time
        return None

    def _spawn_dancingm_pedestrian(self, ego_transform):
        if self._dancingm_pedestrian_spawned:
            return True

        actor = None
        traffic_light = self._find_upcoming_traffic_light(ego_transform)
        if traffic_light is not None:
            traffic_light_location = traffic_light.get_transform().location
            spawn_transform = self._find_sidewalk_spawn_transform(
                ego_transform,
                center_location=traffic_light_location,
                min_distance=DANCINGM_MIN_DISTANCE,
                max_distance=DANCINGM_MAX_DISTANCE,
                used_locations=None,
            )
            if spawn_transform is not None:
                actor = self.world.try_spawn_actor(
                    self.world.get_blueprint_library().find(DANCINGM_PEDESTRIAN_BLUEPRINT_ID),
                    spawn_transform,
                )
                if actor is not None:
                    self._walker_actor_ids.append(actor.id)
                    self._dancingm_traffic_light_actor_id = traffic_light.id
                    try:
                        self._dancingm_traffic_light_original_state = traffic_light.get_state()
                    except Exception:
                        self._dancingm_traffic_light_original_state = None
                    try:
                        traffic_light.set_state(carla.TrafficLightState.Red)
                        self._dancingm_traffic_light_forced_time = self.world.get_snapshot().timestamp.elapsed_seconds
                        print(
                            f"[Scenario04] DANCINGM gespawnt bei Ampel: id={actor.id}, blueprint={DANCINGM_PEDESTRIAN_BLUEPRINT_ID}, "
                            f"light_id={traffic_light.id}, spawn=({spawn_transform.location.x:.2f}, {spawn_transform.location.y:.2f}, {spawn_transform.location.z:.2f})"
                        )
                    except Exception:
                        print(f"[Scenario04] WARNUNG: Ampel konnte nicht auf Rot gesetzt werden: light_id={traffic_light.id}")

        if actor is None:
            actor = self._spawn_stationary_pedestrian(
                DANCINGM_PEDESTRIAN_BLUEPRINT_ID,
                ego_transform,
                "DANCINGM",
                max_distance=DANCINGM_MAX_DISTANCE,
            )
        if actor is None:
            return False

        self._dancingm_pedestrian_spawned = True
        self._dancingm_pedestrian_actor_id = actor.id
        self._dancingm_pedestrian_spawn_time = self.world.get_snapshot().timestamp.elapsed_seconds
        self._dancingm_confirmation_pending = True
        self._dancingm_confirmation_response = None
        self._dancingm_confirmation_listener_started = False
        self._start_dancingm_confirmation_listener()
        return True

    def _start_dancingm_confirmation_listener(self):
        if self._dancingm_confirmation_listener_started or not self._dancingm_confirmation_pending:
            return
        self._dancingm_confirmation_listener_started = True

        def _wait_for_dancingm_response():
            try:
                response = input("DANCINGM gesehen? J/N? ").strip().lower()
            except EOFError:
                response = "j"
                print("[Scenario04] WARNUNG: Kein stdin verfügbar; DANCINGM-Bestätigung default auf Ja.")

            self._dancingm_confirmation_response = response
            print(f"[Scenario04] DANCINGM-Bestätigung empfangen: {response}")

        listener_thread = threading.Thread(target=_wait_for_dancingm_response, daemon=True)
        listener_thread.start()

    def _reset_dancingm_phase(self):
        self._update_dancingm_traffic_light_experiment(0.0, force_restore=True)

        if self._dancingm_pedestrian_actor_id is not None:
            actor = self.world.get_actor(self._dancingm_pedestrian_actor_id)
            if actor is not None:
                try:
                    actor.destroy()
                except Exception:
                    pass
            if self._dancingm_pedestrian_actor_id in self._walker_actor_ids:
                self._walker_actor_ids.remove(self._dancingm_pedestrian_actor_id)

        self._dancingm_pedestrian_spawned = False
        self._dancingm_pedestrian_actor_id = None
        self._dancingm_pedestrian_spawn_time = None
        self._dancingm_confirmation_pending = False
        self._dancingm_confirmation_listener_started = False
        self._dancingm_confirmation_response = None
        self._dancingm_release_active = False
        self._dancingm_release_start_time = None

    def _start_dancingm_release(self, sim_time):
        if self._dancingm_traffic_light_actor_id is None:
            return

        traffic_light = self.world.get_actor(self._dancingm_traffic_light_actor_id)
        if traffic_light is not None:
            try:
                traffic_light.set_state(carla.TrafficLightState.Green)
                if hasattr(traffic_light, "set_green_time"):
                    traffic_light.set_green_time(DANCINGM_TRAFFIC_LIGHT_GREEN_RELEASE_SECONDS)
                print(
                    f"[Scenario04] DANCINGM-Ampel freigegeben für {DANCINGM_TRAFFIC_LIGHT_GREEN_RELEASE_SECONDS:.0f}s: "
                    f"light_id={self._dancingm_traffic_light_actor_id}"
                )
            except Exception:
                print(f"[Scenario04] WARNUNG: DANCINGM-Ampel konnte nicht auf Grün gesetzt werden: light_id={self._dancingm_traffic_light_actor_id}")

        self._dancingm_release_active = True
        self._dancingm_release_start_time = sim_time

    def _restore_dancingm_traffic_light(self, traffic_light):
        if traffic_light is None:
            return

        try:
            if hasattr(traffic_light, "reset_group"):
                traffic_light.reset_group()
                print(f"[Scenario04] DANCINGM-Ampel an Stadtlogik zurückgegeben: light_id={self._dancingm_traffic_light_actor_id}")
                return
        except Exception:
            pass

        if self._dancingm_traffic_light_original_state is not None:
            try:
                traffic_light.set_state(self._dancingm_traffic_light_original_state)
                print(f"[Scenario04] Ampel wiederhergestellt: light_id={self._dancingm_traffic_light_actor_id}")
            except Exception:
                print(f"[Scenario04] WARNUNG: Ampel konnte nicht wiederhergestellt werden: light_id={self._dancingm_traffic_light_actor_id}")

    def _update_dancingm_confirmation(self, sim_time):
        if not self._dancingm_confirmation_pending:
            return

        if self._dancingm_confirmation_response is None:
            if not self._dancingm_confirmation_listener_started:
                self._start_dancingm_confirmation_listener()
            return

        response = self._dancingm_confirmation_response
        self._dancingm_confirmation_response = None
        self._dancingm_confirmation_listener_started = False

        if response in ("j", "ja", "y", "yes", ""):
            self._start_dancingm_release(sim_time)
            print("[Scenario04] DANCINGM bestätigt; fahre normal bis zum Ende weiter.")
            self._dancingm_confirmation_pending = False
            return

        if response in ("n", "nein", "no"):
            print("[Scenario04] DANCINGM nicht gesehen; setze Phase zurück.")
            self._reset_dancingm_phase()
            return

        print("[Scenario04] WARNUNG: Ungültige DANCINGM-Eingabe; bitte J oder N eingeben.")
        self._dancingm_confirmation_pending = True

    def _update_dancingm_traffic_light_experiment(self, sim_time, force_restore=False):
        if self._dancingm_traffic_light_actor_id is None:
            return

        if self._dancingm_traffic_light_forced_time is None:
            return

        if self._dancingm_confirmation_pending and not force_restore:
            return

        if self._dancingm_release_active:
            if self._dancingm_release_start_time is None:
                self._dancingm_release_start_time = sim_time

            if not force_restore and (sim_time - self._dancingm_release_start_time) < DANCINGM_TRAFFIC_LIGHT_GREEN_RELEASE_SECONDS:
                return

        if not force_restore and self._dancingm_confirmation_pending:
            return

        traffic_light = self.world.get_actor(self._dancingm_traffic_light_actor_id)
        self._restore_dancingm_traffic_light(traffic_light)

        self._dancingm_traffic_light_actor_id = None
        self._dancingm_traffic_light_original_state = None
        self._dancingm_traffic_light_forced_time = None
        self._dancingm_release_active = False
        self._dancingm_release_start_time = None

    def _should_start_song(self, sim_time):
        return (
            self._animcat_finished
            and not self._song_started
            and self._animcat_destroy_time is not None
            and (sim_time - self._animcat_destroy_time) >= ANIMCAT_TO_SONG_DELAY_SECONDS
        )

    def _should_spawn_dancingm_pedestrian(self, sim_time):
        return (
            self._song_finished
            and not self._dancingm_pedestrian_spawned
            and self._song_finish_time is not None
            and (sim_time - self._song_finish_time) >= SONG_TO_DANCINGM_DELAY_SECONDS
        )

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
            if tl is None:
                return

            if self._dancingm_confirmation_pending:
                try:
                    tl.set_state(carla.TrafficLightState.Red)
                    if hasattr(tl, "set_red_time"):
                        tl.set_red_time(DANCINGM_TRAFFIC_LIGHT_RED_HOLD_SECONDS)
                except Exception:
                    pass
                return

            if tl.id != self._dancingm_traffic_light_actor_id:
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

            target_location = pick_navigation_location(
                self.world,
                used_locations + [spawn_location],
                min_route_distance=PEDESTRIAN_MIN_ROUTE_DISTANCE,
                sample_count=PEDESTRIAN_NAV_SAMPLES,
            )
            if target_location is None:
                target_location = self._project_location_to_navigation(spawn_location)
            if target_location is None:
                target_location = self._pick_hidden_navigation_location(
                    ego_transform,
                    used_locations + [spawn_location],
                    PEDESTRIAN_MIN_HIDDEN_DISTANCE,
                    PEDESTRIAN_MAX_HIDDEN_DISTANCE,
                )
            if target_location is None:
                print(f"[Scenario04] WARNUNG: Kein Ziel auf Navigation gefunden für Startpunkt #{candidate_index + 1}; überspringe ihn.")
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

            walker_bp = get_random_pedestrian_blueprint(self.world, self._rng, excluded_ids=used_blueprint_ids, max_numeric_id=50)
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

    def _should_end_scenario(self, sim_time):
        if self._dancingm_confirmation_pending or self._dancingm_release_active:
            return False

        if self._dancingm_pedestrian_spawned and self._dancingm_pedestrian_spawn_time is not None:
            return (sim_time - self._dancingm_pedestrian_spawn_time) >= DANCINGM_TO_END_DELAY_SECONDS

        return False

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
                
                if not self._traffic_spawned:
                    self._spawn_dynamic_traffic(ego_transform, sim_time)
                    self._traffic_spawned = True
                    self._traffic_spawn_time = sim_time

                hero_velocity = None
                if ego is not None:
                    try:
                        hero_velocity = ego.get_velocity()
                    except Exception:
                        hero_velocity = None

                self._update_animcat(sim_time, ego_transform.location, hero_velocity)

                if not self._pedestrians_spawned and ENABLE_ROUTE_PEDESTRIANS:
                    self._spawn_pedestrians(ego_transform)

                if ENABLE_ROUTE_PEDESTRIANS:
                    self._update_pedestrians(sim_time)

                    self._update_song(sim_time)

                    self._update_dancingm_traffic_light_experiment(sim_time)
                    self._update_dancingm_confirmation(sim_time)

                    if self._should_spawn_dancingm_pedestrian(sim_time):
                        self._spawn_dancingm_pedestrian(ego_transform)

                    if self._should_end_scenario(sim_time):
                        self._scenario_done = True

                    if self._scenario_done:
                        return

                if self._should_start_song(sim_time):
                    self._start_song(sim_time)
                
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
        self._update_dancingm_traffic_light_experiment(0.0, force_restore=True)
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
