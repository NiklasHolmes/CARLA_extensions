#!/usr/bin/env python

import argparse
import math
import os
import random
import time
import threading

import carla

try:
    from scenario_helper import (
        get_random_pedestrian_blueprint,
        is_transform_hidden_from_hero,
        pick_hidden_navigation_location_near,
        pick_navigation_location,
    )
except ModuleNotFoundError:
    from scenario_events.scenario_helper import (
        get_random_pedestrian_blueprint,
        is_transform_hidden_from_hero,
        pick_hidden_navigation_location_near,
        pick_navigation_location,
    )

try:
    from events_scenario05_static_props import get_static_prop_spawns
except ModuleNotFoundError:
    from scenario_events.events_scenario05_static_props import get_static_prop_spawns

from common.audio_paths import SADNESS_RP_MAD_WORLD_PATH
from generate_audio import SongAudio

START_TO_CARPED_DELAY_SECONDS = 3.0
CAR_TO_PED_DELAY_SECONDS = 2.0
ACCIDENT_TO_RADIO_DELAY_SECONDS = 1.0
RADIO_TO_END_DELAY_SECONDS = 100.0

SONG_START_OFFSET_SECONDS = 30.0
SONG_PLAY_DURATION_SECONDS = 2.0
SONG_FADE_IN_MS = 3000
SONG_FADE_OUT_MS = 3000
HERO_GREEN_LIGHT_HOLD_SECONDS = 10.0
SPAWN_CARS = 5
PEDESTRIAN_COUNT = 1
ENABLE_ROUTE_PEDESTRIANS = True
PEDESTRIAN_BLUEPRINT_ID = "walker.pedestrian.0046"
PEDESTRIAN_MAX_SPEED = 1.5
PEDESTRIAN_WAIT_TIMEOUT_S = 40.0
PEDESTRIAN_ARRIVE_THRESH = 1.0
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
PED_RESPAWN_MAX_DISTANCE = 50.0
VEHICLE_SPAWN_MIN_SEPARATION = 8.0
PEDESTRIAN_MIN_HIDDEN_DISTANCE = 2.0
PEDESTRIAN_MAX_HIDDEN_DISTANCE = 50.0
PEDESTRIAN_MIN_ROUTE_DISTANCE = 5.0
PEDESTRIAN_NAV_SAMPLES = 96
PEDESTRIAN_NEAR_SEARCH_RADIUS = 25.0
IMMOBILIZE_VEHICLE_DELAY_SECONDS = 2.0
# When True, delete all non-hero vehicles and pedestrians before spawning the accident props
CLEAN_UP_BEFORE_ACCIDENT = True             # TODO: work with hidden radius so that car/ped doesn't disappear if hero is too close

ACCIDENT_TRIGGER_LOCATIONS = (
    carla.Location(x=-7.53, y=288.22, z=0.50),
    carla.Location(x=41.39, y=257.46, z=0.50),
    carla.Location(x=189.93, y=266.43, z=0.50),
)
ACCIDENT_TRIGGER_KEYS = (
    "bottom_corner",
    "bottom_junction",
    "top_corner",
)
ACCIDENT_TRIGGER_X_TOLERANCE = 2.0
ACCIDENT_TRIGGER_Y_TOLERANCE = 5.0
ACCIDENT_TRIGGER_FORWARD_MIN_ALIGNMENT = 0.85

# loneleyPed-like sidewalk spawn tuning
LONELEYPED_PREFERRED_AHEAD_DISTANCE = 10.0
LONELEYPED_AHEAD_SEARCH_RADIUS = 12.0
LONELEYPED_FORWARD_MIN_DISTANCE = 1.0
LONELEYPED_FORWARD_MAX_DISTANCE = 50.0
LONELEYPED_SPAWN_CLEARANCE_METERS = 2.0
LONELEYPED_SPAWN_HEIGHT_OFFSET = 1.0
LONELEYPED_MAX_SPAWN_ATTEMPTS = 12
PED_CONFIRM_AHEAD_DISTANCE = 44.0
PED_CONFIRM_SEARCH_RADIUS = 20.0
PED_CONFIRM_FORWARD_MIN_DISTANCE = 32.0
PED_CONFIRM_FORWARD_MAX_DISTANCE = 90.0
PED_CONFIRM_HIDDEN_MIN_DISTANCE = 46.0
PED_CONFIRM_HIDDEN_MAX_DISTANCE = 150.0
PED_CONFIRM_CONE_ANGLE_DEGREES = 45.0


def get_actor_blueprints(world, filter_pattern):
    bps = list(world.get_blueprint_library().filter(filter_pattern))
    if not bps:
        print(f"[Scenario05] WARNUNG: Keine Blueprints für {filter_pattern} gefunden!")
    return bps


def filter_blocked_vehicle_blueprints(blueprints, blocked_keywords):
    return [bp for bp in blueprints if not any(k in bp.id.lower() for k in blocked_keywords)]


class Scenario05Runner:
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
        self._cars_spawn_time = None
        self._pedestrians_spawned = False
        self._pedestrians_started = False
        self._pedestrians_done = False
        self._pedestrian_spawn_time = None
        self._pedestrian_routes = []
        self._song_started = False
        self._song_start_time = None
        self._song_finished = False
        self._song_finish_time = None
        self._accident_spawned = False
        self._accident_spawn_time = None
        self._radio_started = False
        self._radio_start_time = None
        self._radio_finished = False
        self._radio_finish_time = None
        self._pedestrian_confirmation_pending = False
        self._pedestrian_confirmation_listener_started = False
        self._pedestrian_confirmation_response = None
        self._ped_to_song = False
        self._song_audio = SongAudio(
            SADNESS_RP_MAD_WORLD_PATH,
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
        self._bottom_loop_walker_spawned = False
        self._bottom_loop_walker_actor_id = None
        self._bottom_loop_walker_controller_id = None
        self._bottom_loop_walker_route = None
        self._pending_vehicle_immobilizations = {}

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
            if actor.attributes.get("role_name") in ["hero", "default_player"]:
                return actor
        return None

    def _spawn_static_prop_once(self, trigger_key=None):
        bp_lib = self.world.get_blueprint_library()
        spawns = get_static_prop_spawns(trigger_key)
        try:
            print(f"[Scenario05] Spawning static props for trigger='{trigger_key}' count={len(spawns)}")
        except Exception:
            pass

        for prop_config in spawns:
            name = prop_config.get("name")
            blueprints = prop_config.get("blueprints", [])
            try:
                print(f"[Scenario05] Trying to spawn prop '{name}' blueprints={blueprints} transform={prop_config.get('transform')}")
            except Exception:
                pass

            prop_bp = None
            found_bp_id = None
            for bp_id in blueprints:
                try:
                    prop_bp = bp_lib.find(bp_id)
                    found_bp_id = bp_id
                    try:
                        print(f"[Scenario05] Found blueprint '{bp_id}' -> id='{prop_bp.id}'")
                    except Exception:
                        pass
                    break
                except Exception as e:
                    print(f"[Scenario05] Blueprint lookup failed for '{bp_id}': {e}")
                    continue

            if prop_bp is None:
                print(f"[Scenario05] WARNUNG: Keine Blueprint für prop '{name}' gefunden. Versuchete IDs: {blueprints}")
                continue

            try:
                actor = self.world.try_spawn_actor(prop_bp, prop_config["transform"])
                if actor:
                    if prop_config.get("immobilize_vehicle"):
                        try:
                            if hasattr(actor, "set_simulate_physics"):
                                actor.set_simulate_physics(True)
                            if hasattr(actor, "set_enable_gravity"):
                                actor.set_enable_gravity(True)
                            immobilize_after_seconds = prop_config.get("immobilize_after_seconds", IMMOBILIZE_VEHICLE_DELAY_SECONDS)
                            if immobilize_after_seconds is not None and immobilize_after_seconds >= 0.0:
                                current_time = self.world.get_snapshot().timestamp.elapsed_seconds
                                self._pending_vehicle_immobilizations[actor.id] = current_time + immobilize_after_seconds
                        except Exception as e:
                            print(f"[Scenario05] WARNUNG: Fahrzeug '{name}' konnte nicht für verzögertes Fixieren vorbereitet werden: {e}")
                    light_state = prop_config.get("light_state")
                    if light_state is not None and hasattr(actor, "set_light_state"):
                        try:
                            actor.set_light_state(light_state)
                            print(f"[Scenario05] Applied light state for '{name}': {light_state}")
                        except Exception as e:
                            print(f"[Scenario05] WARNUNG: Lichtzustand für '{name}' konnte nicht gesetzt werden: {e}")
                    open_doors = prop_config.get("open_doors", [])
                    if open_doors and hasattr(actor, "open_door"):
                        for door in open_doors:
                            try:
                                actor.open_door(door)
                                print(f"[Scenario05] Opened door for '{name}': {door}")
                            except Exception as e:
                                print(f"[Scenario05] WARNUNG: Tür für '{name}' konnte nicht geöffnet werden ({door}): {e}")
                    self._static_actor_ids.append(actor.id)
                    print(f"[Scenario05] Spawned '{name}' actor id={actor.id} bp='{found_bp_id}'")
                else:
                    print(f"[Scenario05] WARNUNG: Spawn für '{name}' fehlgeschlagen (try_spawn_actor returned None).")
            except Exception as e:
                print(f"[Scenario05] ERROR beim Spawnen von '{name}': {e}")

    def _spawn_bottom_loop_walker(self, trigger_key=None):
        if self._bottom_loop_walker_spawned:
            return True

        spawns = get_static_prop_spawns(trigger_key)
        bp_lib = self.world.get_blueprint_library()

        for prop_config in spawns:
            walker_bp_id = prop_config.get("walker_blueprint")
            if not walker_bp_id:
                continue

            spawn_transform = prop_config.get("transform")
            target_location = prop_config.get("target_location")
            if spawn_transform is None or target_location is None:
                print(f"[Scenario05] WARNUNG: Walker-Config '{prop_config.get('name')}' ist unvollständig.")
                continue

            try:
                walker_bp = bp_lib.find(walker_bp_id)
            except Exception as e:
                print(f"[Scenario05] WARNUNG: Walker-Blueprint '{walker_bp_id}' nicht gefunden: {e}")
                continue

            if walker_bp.has_attribute("is_invincible"):
                walker_bp.set_attribute("is_invincible", "false")
            if walker_bp.has_attribute("role_name"):
                walker_bp.set_attribute("role_name", "walker")

            walker_actor = self.world.try_spawn_actor(walker_bp, spawn_transform)
            if walker_actor is None:
                print(f"[Scenario05] WARNUNG: AI-Walker '{prop_config.get('name')}' konnte nicht gespawnt werden.")
                continue

            controller_bp = bp_lib.find("controller.ai.walker")
            controller_actor = self.world.try_spawn_actor(controller_bp, carla.Transform(), walker_actor)
            if controller_actor is None:
                try:
                    walker_actor.destroy()
                except Exception:
                    pass
                print(f"[Scenario05] WARNUNG: Walker-Controller für '{prop_config.get('name')}' konnte nicht gespawnt werden.")
                continue

            self._walker_actor_ids.append(walker_actor.id)
            self._walker_controller_ids.append(controller_actor.id)
            self._bottom_loop_walker_spawned = True
            self._bottom_loop_walker_actor_id = walker_actor.id
            self._bottom_loop_walker_controller_id = controller_actor.id
            self._bottom_loop_walker_route = {
                "spawn_location": spawn_transform.location,
                "target_location": target_location,
                "current_target_location": target_location,
                "heading_to_target": True,
                "walker_id": walker_actor.id,
                "controller_id": controller_actor.id,
                "max_speed": prop_config.get("max_speed", 1.4),
                "arrive_threshold": PEDESTRIAN_ARRIVE_THRESH,
                "name": prop_config.get("name", "bottom_loop_walker"),
            }

            try:
                controller_actor.start()
                controller_actor.go_to_location(target_location)
                controller_actor.set_max_speed(self._bottom_loop_walker_route["max_speed"])
                print(
                    f"[Scenario05] AI-Walker gespawnt: id={walker_actor.id}, blueprint={walker_bp_id}, "
                    f"spawn=({spawn_transform.location.x:.2f}, {spawn_transform.location.y:.2f}, {spawn_transform.location.z:.2f}), "
                    f"target=({target_location.x:.2f}, {target_location.y:.2f}, {target_location.z:.2f})"
                )
            except Exception as e:
                print(f"[Scenario05] WARNUNG: AI-Walker '{prop_config.get('name')}' konnte nicht gestartet werden: {e}")
            return True

        return False

    def _update_bottom_loop_walker(self, sim_time):
        if not self._bottom_loop_walker_spawned or not self._bottom_loop_walker_route:
            return

        walker = self.world.get_actor(self._bottom_loop_walker_route.get("walker_id"))
        controller = self.world.get_actor(self._bottom_loop_walker_route.get("controller_id"))
        if walker is None or controller is None:
            self._bottom_loop_walker_spawned = False
            self._bottom_loop_walker_route = None
            self._bottom_loop_walker_actor_id = None
            self._bottom_loop_walker_controller_id = None
            return

        target_location = self._bottom_loop_walker_route.get("current_target_location")
        if target_location is None:
            return

        try:
            loc = walker.get_location()
        except Exception:
            return

        distance = ((loc.x - target_location.x) ** 2 + (loc.y - target_location.y) ** 2 + (loc.z - target_location.z) ** 2) ** 0.5
        if distance > self._bottom_loop_walker_route.get("arrive_threshold", PEDESTRIAN_ARRIVE_THRESH):
            return

        next_target = self._bottom_loop_walker_route["spawn_location"] if self._bottom_loop_walker_route.get("heading_to_target", True) else self._bottom_loop_walker_route["target_location"]
        self._bottom_loop_walker_route["heading_to_target"] = not self._bottom_loop_walker_route.get("heading_to_target", True)
        self._bottom_loop_walker_route["current_target_location"] = next_target

        try:
            controller.go_to_location(next_target)
            controller.set_max_speed(self._bottom_loop_walker_route.get("max_speed", 1.4))
            print(f"[Scenario05] AI-Walker wechselt Richtung bei sim_time={sim_time:.2f}s")
        except Exception as e:
            print(f"[Scenario05] WARNUNG: AI-Walker konnte Ziel nicht wechseln: {e}")

    def _update_pending_vehicle_immobilizations(self, sim_time):
        if not self._pending_vehicle_immobilizations:
            return

        for actor_id, freeze_at_time in list(self._pending_vehicle_immobilizations.items()):
            if sim_time < freeze_at_time:
                continue

            actor = self.world.get_actor(actor_id)
            if actor is None:
                self._pending_vehicle_immobilizations.pop(actor_id, None)
                continue

            try:
                if hasattr(actor, "set_target_velocity"):
                    actor.set_target_velocity(carla.Vector3D(0.0, 0.0, 0.0))
                if hasattr(actor, "set_target_angular_velocity"):
                    actor.set_target_angular_velocity(carla.Vector3D(0.0, 0.0, 0.0))
                if hasattr(actor, "set_simulate_physics"):
                    actor.set_simulate_physics(False)
                print(f"[Scenario05] Vehicle immobilized: id={actor_id}, sim_time={sim_time:.2f}s")
            except Exception as e:
                print(f"[Scenario05] WARNUNG: Fahrzeug id={actor_id} konnte nicht immobilisiert werden: {e}")
            finally:
                self._pending_vehicle_immobilizations.pop(actor_id, None)

    def _cleanup_scene_before_accident(self):
        """Destroy non-hero vehicles and pedestrians/controllers and clear internal lists."""
        hero = self.find_hero()
        hero_id = hero.id if hero is not None else None

        actors = list(self.world.get_actors())
        for actor in actors:
            try:
                tid = actor.type_id
            except Exception:
                continue

            # Vehicles (skip hero/default player)
            if tid.startswith("vehicle."):
                if actor.id == hero_id:
                    continue
                try:
                    actor.destroy()
                except Exception:
                    pass
                if actor.id in self._vehicle_actor_ids:
                    try:
                        self._vehicle_actor_ids.remove(actor.id)
                    except ValueError:
                        pass

            # Walkers and their controllers
            if tid.startswith("walker.") or tid == "controller.ai.walker":
                try:
                    actor.destroy()
                except Exception:
                    pass
                if actor.id in self._walker_actor_ids:
                    try:
                        self._walker_actor_ids.remove(actor.id)
                    except ValueError:
                        pass
                if actor.id in self._walker_controller_ids:
                    try:
                        self._walker_controller_ids.remove(actor.id)
                    except ValueError:
                        pass

        # Clear pedestrian routes and flags
        self._pedestrian_routes = []
        self._pedestrians_spawned = False
        self._pedestrians_started = False
        self._pedestrian_confirmation_pending = False

    def _pick_hidden_points(self, points, ego_transform, count):
        if not ego_transform:
            return points[:count]
        hidden = []
        for p in points:
            if is_transform_hidden_from_hero(p, ego_transform, MIN_SPAWN_DISTANCE, MAX_SPAWN_DISTANCE):
                hidden.append(p)
        return hidden[:count]

    def _pick_hidden_navigation_location(self, ego_transform, used_locations=None, min_distance=MIN_SPAWN_DISTANCE, max_distance=MAX_SPAWN_DISTANCE):
        hidden_location = pick_hidden_navigation_location_near(
            self.world,
            ego_transform.location if ego_transform is not None else carla.Location(),
            ego_transform,
            used_locations=used_locations,
            min_distance=min_distance,
            max_distance=max_distance,
            min_route_distance=PEDESTRIAN_MIN_ROUTE_DISTANCE,
            sample_count=PEDESTRIAN_NAV_SAMPLES,
            search_radius=PEDESTRIAN_NEAR_SEARCH_RADIUS,
        )
        if hidden_location is not None:
            return hidden_location

        if ego_transform is not None:
            projected_hero_location = self._project_location_to_navigation(ego_transform.location)
            if is_transform_hidden_from_hero(
                carla.Transform(projected_hero_location),
                ego_transform,
                min_distance,
                max_distance,
            ):
                return projected_hero_location

        return None

    def _find_sidewalk_spawn_transform(self, ego_transform, center_location=None, ahead_distance=LONELEYPED_PREFERRED_AHEAD_DISTANCE, search_radius=LONELEYPED_AHEAD_SEARCH_RADIUS, min_distance=PEDESTRIAN_MIN_HIDDEN_DISTANCE, max_distance=PEDESTRIAN_MAX_HIDDEN_DISTANCE, min_forward_distance=LONELEYPED_FORWARD_MIN_DISTANCE, max_forward_distance=LONELEYPED_FORWARD_MAX_DISTANCE, used_locations=None):
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

        for _ in range(LONELEYPED_MAX_SPAWN_ATTEMPTS):
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

            # Enforce cone constraint: only allow spawn within ±45° of forward direction
            cone_angle_rad = math.radians(PED_CONFIRM_CONE_ANGLE_DEGREES)
            cos_cone_angle = math.cos(cone_angle_rad)
            forward_2d = (ego_forward.x, ego_forward.y)
            forward_2d_len = (forward_2d[0] ** 2 + forward_2d[1] ** 2) ** 0.5
            delta_2d = (dx, dy)
            delta_2d_len = (delta_2d[0] ** 2 + delta_2d[1] ** 2) ** 0.5
            if forward_2d_len > 0.0 and delta_2d_len > 0.0:
                cos_angle = (forward_2d[0] * delta_2d[0] + forward_2d[1] * delta_2d[1]) / (forward_2d_len * delta_2d_len)
                if cos_angle < cos_cone_angle:
                    continue

            if any(waypoint_location.distance(existing) < LONELEYPED_SPAWN_CLEARANCE_METERS for existing in actor_locations):
                continue

            spawn_location = carla.Location(
                x=waypoint_location.x,
                y=waypoint_location.y,
                z=waypoint_location.z + LONELEYPED_SPAWN_HEIGHT_OFFSET,
            )
            base_rot = waypoint.transform.rotation
            rot = carla.Rotation(pitch=base_rot.pitch, yaw=base_rot.yaw + 90.0, roll=base_rot.roll)
            return carla.Transform(spawn_location, rot)

        return None

    def _spawn_dynamic_traffic(self, ego_transform, sim_time):
        target_count = SPAWN_CARS
        attempts = 0
        max_attempts = max(20, target_count * 20)

        while len(self._vehicle_actor_ids) < target_count and attempts < max_attempts:
            attempts += 1
            if not self._spawn_single_vehicle(ego_transform, sim_time):
                continue

        print(
            f"[Scenario05] Vehicles spawned: {len(self._vehicle_actor_ids)}/{target_count} after attempts={attempts}"
        )

        # Inform about upcoming pedestrian (loneleyPed) spawn search after car->ped delay
        try:
            print(f"[Scenario05] Pedestrian (loneleyPed) spawn location wird in {CAR_TO_PED_DELAY_SECONDS:.1f}s gesucht.")
        except Exception:
            print("[Scenario05] Pedestrian (loneleyPed) spawn location wird in CAR_TO_PED_DELAY_SECONDS gesucht.")

        if len(self._vehicle_actor_ids) >= target_count:
            self._cars_phase_done = True
            try:
                self._cars_spawn_time = sim_time
            except Exception:
                # fallback if sim_time not provided
                try:
                    self._cars_spawn_time = self.world.get_snapshot().timestamp.elapsed_seconds
                except Exception:
                    self._cars_spawn_time = None
            return True

        return False

    def _spawn_batch_vehicles(self, points, bps, tm):
        if not points or not bps:
            print(f"[Scenario05] WARNUNG: Keine Fahrzeug-Spawns möglich (points={len(points)}, blueprints={len(bps)})")
            return

        batch = []
        for p in points:
            bp = self._rng.choice(bps)
            batch.append(
                carla.command.SpawnActor(bp, p).then(
                    carla.command.SetAutopilot(carla.command.FutureActor, True, tm.get_port())
                )
            )
        results = self.client.apply_batch_sync(batch, False)
        spawned_ids = []
        for r in results:
            if not r.error:
                self._vehicle_actor_ids.append(r.actor_id)
                spawned_ids.append(r.actor_id)
        print(f"[Scenario05] Vehicles spawned: {len(spawned_ids)}/{len(points)}")

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

    def _distance_2d(self, location_a, location_b):
        dx = location_a.x - location_b.x
        dy = location_a.y - location_b.y
        return (dx * dx + dy * dy) ** 0.5

    def _actor_distance_to_hero(self, actor, ego_transform):
        if actor is None or ego_transform is None:
            return None
        try:
            actor_location = actor.get_location()
        except Exception:
            return None
        return self._distance_2d(actor_location, ego_transform.location)

    def _destroy_actor_id(self, actor_id, actor_id_list):
        actor = self.world.get_actor(actor_id)
        if actor is not None:
            try:
                actor.destroy()
            except Exception:
                pass
        if actor_id in actor_id_list:
            actor_id_list.remove(actor_id)

    def _destroy_pedestrian_route(self, route):
        walker_id = route.get("walker_id")
        controller_id = route.get("controller_id")
        if walker_id is not None:
            self._destroy_actor_id(walker_id, self._walker_actor_ids)
        if controller_id is not None and controller_id in self._walker_controller_ids:
            self._walker_controller_ids.remove(controller_id)

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
                f"[Scenario05] WARNUNG: Vehicle konnte nicht gespawnt werden | sim_time={sim_time:.2f}s | "
                f"spawn=({spawn_transform.location.x:.2f}, {spawn_transform.location.y:.2f}, {spawn_transform.location.z:.2f})"
            )
            return False

        try:
            actor.set_autopilot(True, tm.get_port())
        except Exception:
            pass
        self._vehicle_actor_ids.append(actor.id)
        print(
            f"[Scenario05] Vehicle respawned: id={actor.id}, sim_time={sim_time:.2f}s, "
            f"spawn=({spawn_transform.location.x:.2f}, {spawn_transform.location.y:.2f}, {spawn_transform.location.z:.2f})"
        )
        return True

    def _get_random_non_cop_pedestrian_blueprint(self):
        excluded_ids = set()
        for _ in range(32):
            walker_bp = get_random_pedestrian_blueprint(self.world, self._rng, excluded_ids=excluded_ids, max_numeric_id=50)
            if "cop" not in walker_bp.id.lower():
                return walker_bp
            excluded_ids.add(walker_bp.id)

        fallback_bp = self.world.get_blueprint_library().find(PEDESTRIAN_BLUEPRINT_ID)
        if fallback_bp.has_attribute("is_invincible"):
            fallback_bp.set_attribute("is_invincible", "false")
        return fallback_bp

    def _spawn_single_pedestrian(self, ego_transform, sim_time):
        walker_controller_bp = self.world.get_blueprint_library().find("controller.ai.walker")
        walker_bp = self._get_random_non_cop_pedestrian_blueprint()

        hero_location = ego_transform.location if ego_transform is not None else carla.Location()
        used_locations = [route["spawn_location"] for route in self._pedestrian_routes if route.get("spawn_location") is not None]
        spawn_location = pick_hidden_navigation_location_near(
            self.world,
            hero_location,
            ego_transform,
            used_locations,
            PEDESTRIAN_MIN_HIDDEN_DISTANCE,
            PEDESTRIAN_MAX_HIDDEN_DISTANCE,
            min_route_distance=PEDESTRIAN_MIN_ROUTE_DISTANCE,
            sample_count=PEDESTRIAN_NAV_SAMPLES * 2,
            search_radius=PEDESTRIAN_NEAR_SEARCH_RADIUS,
        )
        if spawn_location is None:
            return False

        target_location = pick_navigation_location(
            self.world,
            used_locations + [spawn_location],
            min_route_distance=PEDESTRIAN_MIN_ROUTE_DISTANCE,
            sample_count=PEDESTRIAN_NAV_SAMPLES,
        )
        if target_location is None:
            target_location = self._project_location_to_navigation(spawn_location)
        if target_location is None:
            return False

        walker_results = self.client.apply_batch_sync([carla.command.SpawnActor(walker_bp, carla.Transform(spawn_location))], False)
        if not walker_results or walker_results[0].error:
            print(
                f"[Scenario05] WARNUNG: Pedestrian konnte nicht gespawnt werden | sim_time={sim_time:.2f}s | "
                f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
            )
            return False

        walker_id = walker_results[0].actor_id
        controller_results = self.client.apply_batch_sync([
            carla.command.SpawnActor(walker_controller_bp, carla.Transform(), walker_id)
        ], False)
        if not controller_results or controller_results[0].error:
            walker_actor = self.world.get_actor(walker_id)
            if walker_actor is not None:
                try:
                    walker_actor.destroy()
                except Exception:
                    pass
            return False

        controller_id = controller_results[0].actor_id
        route = {
            "spawn_location": spawn_location,
            "target_location": target_location,
            "current_target_location": target_location,
            "heading_to_target": True,
            "done": False,
            "max_speed": self._get_random_pedestrian_speed(),
            "walker_id": walker_id,
            "controller_id": controller_id,
        }
        self._walker_actor_ids.append(walker_id)
        self._walker_controller_ids.append(controller_id)
        self._pedestrian_routes.append(route)

        if self._pedestrians_started:
            controller = self.world.get_actor(controller_id)
            if controller is not None:
                try:
                    controller.start()
                    controller.go_to_location(route["target_location"])
                    controller.set_max_speed(route["max_speed"])
                except Exception:
                    pass

        print(
            f"[Scenario05] Pedestrian respawned: id={walker_id}, sim_time={sim_time:.2f}s, "
            f"spawn=({spawn_location.x:.2f}, {spawn_location.y:.2f}, {spawn_location.z:.2f})"
        )
        return True

    def _spawn_single_confirmation_pedestrian(self, ego_transform, sim_time):
        if self._pedestrians_spawned:
            return True

        # Try to spawn on the sidewalk in front of the hero first (loneleyPed-like)
        hero_forward = ego_transform.get_forward_vector() if ego_transform is not None else carla.Vector3D(x=1.0, y=0.0, z=0.0)
        hero_location = ego_transform.location if ego_transform is not None else carla.Location()
        ahead_center = carla.Location(
            x=hero_location.x + hero_forward.x * PED_CONFIRM_AHEAD_DISTANCE,
            y=hero_location.y + hero_forward.y * PED_CONFIRM_AHEAD_DISTANCE,
            z=hero_location.z,
        )
        spawn_transform = None
        for search_radius, min_distance in (
            (PED_CONFIRM_SEARCH_RADIUS, PED_CONFIRM_HIDDEN_MIN_DISTANCE),
            (max(PED_CONFIRM_SEARCH_RADIUS, LONELEYPED_AHEAD_SEARCH_RADIUS), PED_CONFIRM_HIDDEN_MIN_DISTANCE),
        ):
            spawn_transform = self._find_sidewalk_spawn_transform(
                ego_transform,
                center_location=ahead_center,
                ahead_distance=PED_CONFIRM_AHEAD_DISTANCE,
                search_radius=search_radius,
                min_distance=min_distance,
                min_forward_distance=PED_CONFIRM_FORWARD_MIN_DISTANCE,
                max_forward_distance=PED_CONFIRM_FORWARD_MAX_DISTANCE,
            )
            if spawn_transform is not None and is_transform_hidden_from_hero(
                spawn_transform,
                ego_transform,
                PED_CONFIRM_HIDDEN_MIN_DISTANCE,
                PED_CONFIRM_HIDDEN_MAX_DISTANCE,
            ):
                break
            spawn_transform = None

        if spawn_transform is not None:
            walker_bp = self._get_random_non_cop_pedestrian_blueprint()

            walker_results = self.client.apply_batch_sync([carla.command.SpawnActor(walker_bp, spawn_transform)], False)
            if walker_results and not walker_results[0].error:
                walker_id = walker_results[0].actor_id
                controller_bp = self.world.get_blueprint_library().find("controller.ai.walker")
                controller_results = self.client.apply_batch_sync([carla.command.SpawnActor(controller_bp, carla.Transform(), walker_id)], False)
                if controller_results and not controller_results[0].error:
                    controller_id = controller_results[0].actor_id
                    target_location = pick_navigation_location(
                        self.world,
                        [spawn_transform.location],
                        min_route_distance=PEDESTRIAN_MIN_ROUTE_DISTANCE,
                        sample_count=PEDESTRIAN_NAV_SAMPLES,
                    )
                    if target_location is None:
                        target_location = self._project_location_to_navigation(spawn_transform.location)
                    route = {
                        "spawn_location": spawn_transform.location,
                        "target_location": target_location,
                        "current_target_location": target_location,
                        "heading_to_target": True,
                        "done": False,
                        "max_speed": self._get_random_pedestrian_speed(),
                        "walker_id": walker_id,
                        "controller_id": controller_id,
                    }
                    self._walker_actor_ids.append(walker_id)
                    self._walker_controller_ids.append(controller_id)
                    self._pedestrian_routes.append(route)

                    controller = self.world.get_actor(controller_id)
                    if controller is not None:
                        try:
                            controller.start()
                            controller.go_to_location(route["current_target_location"])
                            controller.set_max_speed(route["max_speed"])
                        except Exception:
                            pass

                    self._pedestrians_spawned = True
                    self._pedestrians_started = True
                    self._pedestrians_done = False
                    self._pedestrian_confirmation_pending = True
                    self._pedestrian_confirmation_response = None
                    self._pedestrian_confirmation_listener_started = False
                    self._start_pedestrian_confirmation_listener()
                    print(f"[Scenario05] Pedestrian gespawnt (vor dem Auto): id={walker_id}")
                    return True

        return False

    def _start_pedestrian_confirmation_listener(self):
        if self._pedestrian_confirmation_listener_started or not self._pedestrian_confirmation_pending:
            return
        self._pedestrian_confirmation_listener_started = True

        def _wait_for_confirmation():
            try:
                response = input("loneleyPed gesehen? J/N? ").strip().lower()
            except EOFError:
                response = "j"
                print("[Scenario05] WARNUNG: Kein stdin verfügbar; loneleyPed-Bestätigung default auf Ja.")

            self._pedestrian_confirmation_response = response
            print(f"[Scenario05] loneleyPed-Bestätigung empfangen: {response}")

        listener_thread = threading.Thread(target=_wait_for_confirmation, daemon=True)
        listener_thread.start()

    def _reset_confirmation_pedestrian(self):
        # destroy any spawned confirmation pedestrian(s) and allow respawn
        for route in list(self._pedestrian_routes):
            self._destroy_pedestrian_route(route)
        self._pedestrian_routes = []
        self._walker_actor_ids = []
        self._walker_controller_ids = []
        self._pedestrians_spawned = False
        self._pedestrians_started = False
        self._pedestrians_done = False
        self._pedestrian_confirmation_pending = False
        self._pedestrian_confirmation_listener_started = False
        self._pedestrian_confirmation_response = None

    def _update_pedestrian_confirmation(self):
        if not self._pedestrian_confirmation_pending:
            return

        if self._pedestrian_confirmation_response is None:
            if not self._pedestrian_confirmation_listener_started:
                self._start_pedestrian_confirmation_listener()
            return

        response = self._pedestrian_confirmation_response
        self._pedestrian_confirmation_response = None
        self._pedestrian_confirmation_listener_started = False
        if response in ("j", "ja", "y", "yes", ""):
            print("[Scenario05] loneleyPed bestätigt; starte Pedestrian und erlaube Fortsetzung.")
            self._pedestrian_confirmation_pending = False
            self._ped_to_song = True
            # allow song start when conditions met
            return

        if response in ("n", "nein", "no"):
            print("[Scenario05] loneleyPed nicht gesehen; setze Phase zurück.")
            self._reset_confirmation_pedestrian()
            return

        print("[Scenario05] WARNUNG: Ungültige loneleyPed-Eingabe; bitte J oder N eingeben.")
        self._pedestrian_confirmation_pending = True
        return

    def _prune_far_vehicles(self, ego_transform):
        if ego_transform is None:
            return

        active_vehicle_ids = []
        for vehicle_id in list(self._vehicle_actor_ids):
            actor = self.world.get_actor(vehicle_id)
            if actor is None:
                continue

            distance = self._actor_distance_to_hero(actor, ego_transform)
            if distance is not None and distance > CAR_RESPAWN_MAX_DISTANCE:
                print(f"[Scenario05] Vehicle removed: id={vehicle_id}, distance={distance:.1f}m")
                try:
                    actor.destroy()
                except Exception:
                    pass
                continue

            active_vehicle_ids.append(vehicle_id)

        self._vehicle_actor_ids = active_vehicle_ids

    def _prune_far_pedestrians(self, ego_transform):
        if ego_transform is None:
            return

        active_routes = []
        active_walker_ids = []
        active_controller_ids = []

        for route in list(self._pedestrian_routes):
            walker_id = route.get("walker_id")
            controller_id = route.get("controller_id")
            walker = self.world.get_actor(walker_id) if walker_id is not None else None
            controller = self.world.get_actor(controller_id) if controller_id is not None else None
            if walker is None or controller is None:
                self._destroy_pedestrian_route(route)
                continue

            distance = self._actor_distance_to_hero(walker, ego_transform)
            if distance is not None and distance > PED_RESPAWN_MAX_DISTANCE:
                print(f"[Scenario05] Pedestrian removed: id={walker_id}, distance={distance:.1f}m")
                self._destroy_pedestrian_route(route)
                continue

            active_routes.append(route)
            active_walker_ids.append(walker_id)
            if controller_id is not None:
                active_controller_ids.append(controller_id)

        self._pedestrian_routes = active_routes
        self._walker_actor_ids = active_walker_ids
        self._walker_controller_ids = active_controller_ids

    def _maintain_spawn_pools(self, ego_transform, sim_time):
        self._prune_far_vehicles(ego_transform)
        self._prune_far_pedestrians(ego_transform)

        vehicle_attempts = max(1, (SPAWN_CARS - len(self._vehicle_actor_ids)) * 3)
        for _ in range(vehicle_attempts):
            if len(self._vehicle_actor_ids) >= SPAWN_CARS:
                break
            if not self._spawn_single_vehicle(ego_transform, sim_time):
                break

        pedestrian_attempts = max(1, (PEDESTRIAN_COUNT - len(self._pedestrian_routes)) * 3)
        for _ in range(pedestrian_attempts):
            if len(self._pedestrian_routes) >= PEDESTRIAN_COUNT:
                break
            if not self._spawn_single_pedestrian(ego_transform, sim_time):
                break

    def _get_random_pedestrian_speed(self):
        min_speed = 1.5
        max_speed = PEDESTRIAN_MAX_SPEED
        steps = int(round((max_speed - min_speed) / 0.5))
        if steps <= 0:
            return max_speed
        speed = min_speed + (0.5 * self._rng.randint(0, steps))
        return min(speed, max_speed)

    def _spawn_pedestrians(self, ego_transform=None):
        if self._spawn_single_confirmation_pedestrian(ego_transform, self.world.get_snapshot().timestamp.elapsed_seconds):
            self._pedestrian_spawn_time = self.world.get_snapshot().timestamp.elapsed_seconds
            return True
        return False

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
            print(
                f"[Scenario05] Pedestrian {walker.id} ist jetzt unterwegs mit speed={route.get('max_speed', PEDESTRIAN_MAX_SPEED):.1f}."
            )

        self._pedestrians_started = True

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
            print("[Scenario05] Pedestrian Timeout.")
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
                route["done"] = True
                print(f"[Scenario05] Pedestrian {walker.id} hat das Ziel erreicht.")
            else:
                all_done = False

        self._pedestrians_done = False
        return all_done

    def _force_green_light(self, ego, sim_time):
        if ego and ego.is_at_traffic_light():
            tl = ego.get_traffic_light()
            if tl:
                tl.set_state(carla.TrafficLightState.Green)
                tl.set_green_time(HERO_GREEN_LIGHT_HOLD_SECONDS)

    def _is_accident_trigger_reached(self, ego_transform):
        if ego_transform is None:
            return None

        location = ego_transform.location
        matched_trigger_key = None
        for trigger_key, trigger in zip(ACCIDENT_TRIGGER_KEYS, ACCIDENT_TRIGGER_LOCATIONS):
            if abs(location.x - trigger.x) <= ACCIDENT_TRIGGER_X_TOLERANCE and abs(location.y - trigger.y) <= ACCIDENT_TRIGGER_Y_TOLERANCE:
                matched_trigger_key = trigger_key
                break

        if matched_trigger_key is None:
            return None

        forward = ego_transform.get_forward_vector()
        forward_length = (forward.x * forward.x + forward.y * forward.y) ** 0.5
        if forward_length <= 0.0:
            return None

        y_alignment = abs(forward.y) / forward_length
        if y_alignment >= ACCIDENT_TRIGGER_FORWARD_MIN_ALIGNMENT:
            return matched_trigger_key

        return None

    def _start_song(self, sim_time):
        if self._song_started:
            return
        self._song_started = True
        self._song_start_time = sim_time
        print(f"[Scenario05] Song started at sim_time={sim_time:.2f}s")
        if not self._play_song(sim_time):
            print("[Scenario05] WARNUNG: Song konnte nicht gestartet werden; fahre ohne Song fort.")
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
            print(f"[Scenario05] Song finished at sim_time={sim_time:.2f}s")

    def _spawn_accident_placeholder(self, sim_time, trigger_key=None):
        if self._accident_spawned:
            return True

        if CLEAN_UP_BEFORE_ACCIDENT:
            try:
                self._cleanup_scene_before_accident()
                print(f"[Scenario05] Scene cleaned up before accident spawn")
            except Exception as e:
                print(f"[Scenario05] WARNUNG: Fehler beim Aufräumen vor Unfall: {e}")

        self._spawn_static_prop_once(trigger_key)
        self._spawn_bottom_loop_walker(trigger_key)
        self._accident_spawned = True
        self._accident_spawn_time = sim_time
        print(f"[Scenario05] Unfall-Trigger erreicht; Static Prop gespawnt bei sim_time={sim_time:.2f}s")
        return True

    def _start_radio_voice_placeholder(self, sim_time):
        if self._radio_started:
            return True
        self._radio_started = True
        self._radio_start_time = sim_time
        print(f"[Scenario05] Radio-Voice-Phase noch nicht implementiert; Marker erreicht bei sim_time={sim_time:.2f}s")
        return True

    def _update_post_song_phases(self, sim_time, ego_transform=None):
        if self._song_finished and not self._accident_spawned:
            trigger_key = self._is_accident_trigger_reached(ego_transform)
            if trigger_key is not None:
                self._spawn_accident_placeholder(sim_time, trigger_key)

        if self._accident_spawned and not self._radio_started and self._accident_spawn_time is not None:
            if (sim_time - self._accident_spawn_time) >= ACCIDENT_TO_RADIO_DELAY_SECONDS:
                self._start_radio_voice_placeholder(sim_time)

        if self._radio_started and not self._radio_finished and self._radio_start_time is not None:
            if (sim_time - self._radio_start_time) >= RADIO_TO_END_DELAY_SECONDS:
                self._radio_finished = True
                self._radio_finish_time = sim_time
                self._scenario_done = True

    def _should_spawn_traffic(self, sim_time):
        return (not self._traffic_spawned) and (not getattr(self, '_cars_phase_done', False)) and (sim_time - self._start_sim_time) >= START_TO_CARPED_DELAY_SECONDS

    def _should_start_song(self, sim_time):
        return (
            getattr(self, '_cars_phase_done', False)
            and self._pedestrians_spawned
            and getattr(self, '_ped_to_song', False)
            and not self._song_started
        )

    def run(self):
        print("[Scenario05] Running...")
        try:
            while True:
                self.world.wait_for_tick()
                snapshot = self.world.get_snapshot()
                sim_time = snapshot.timestamp.elapsed_seconds
                if self._start_sim_time is None:
                    self._start_sim_time = sim_time

                ego = self.find_hero()
                trigger_ego_transform = ego.get_transform() if ego else None
                ego_transform = ego.get_transform() if ego else carla.Transform(
                    carla.Location(x=150.60, y=-173.30, z=0.70),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                )

                if self._should_spawn_traffic(sim_time):
                    if self._spawn_dynamic_traffic(ego_transform, sim_time):
                        if self._spawn_pedestrians(ego_transform):
                            self._traffic_spawned = True
                            self._traffic_spawn_time = sim_time

                # After cars spawned, wait CAR_TO_PED_DELAY_SECONDS then spawn pedestrian
                if getattr(self, '_cars_phase_done', False) and self._cars_spawn_time is not None and not self._pedestrians_spawned:
                    if (sim_time - self._cars_spawn_time) >= CAR_TO_PED_DELAY_SECONDS:
                        if self._spawn_pedestrians(ego_transform):
                            self._pedestrian_spawn_time = sim_time
                            # mark traffic fully spawned when ped is spawned
                            self._traffic_spawned = True
                            self._traffic_spawn_time = sim_time

                # If traffic already spawned but the confirmation pedestrian was deleted (N), allow respawn
                if self._traffic_spawned and not self._pedestrians_spawned:
                    if self._spawn_pedestrians(ego_transform):
                        self._pedestrian_spawn_time = sim_time

                if ENABLE_ROUTE_PEDESTRIANS:
                    self._update_pedestrians(sim_time)
                    self._update_pedestrian_confirmation()

                if self._should_start_song(sim_time):
                    self._start_song(sim_time)

                self._update_song(sim_time)
                self._update_post_song_phases(sim_time, trigger_ego_transform)
                self._update_bottom_loop_walker(sim_time)
                self._update_pending_vehicle_immobilizations(sim_time)

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
        print("[Scenario05] Cleanup...")
        self._song_audio.stop(0)
        self._pending_vehicle_immobilizations = {}
        all_ids = self._static_actor_ids + self._vehicle_actor_ids + self._walker_actor_ids + self._walker_controller_ids
        self.client.apply_batch([carla.command.DestroyActor(x) for x in all_ids])

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
            print(f"[Scenario05] WARNING: could not write done signal file: {exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=2000, type=int)
    parser.add_argument("--tm-port", default=8000, type=int)
    parser.add_argument("--done-file", default=None)
    args = parser.parse_args()
    Scenario05Runner(args.host, args.port, args.tm_port, args.done_file).run()
