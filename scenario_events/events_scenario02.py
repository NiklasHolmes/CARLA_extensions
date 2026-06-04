#!/usr/bin/env python

import argparse
import math
import os
import random
import sys
import time

import carla

try:
    from events_scenario02_static_props import get_start_barrier_spawns, get_trash_trigger_config, get_poorroad_trigger_config, get_traffic_route_configs
except ModuleNotFoundError:
    from scenario_events.events_scenario02_static_props import get_start_barrier_spawns, get_trash_trigger_config, get_poorroad_trigger_config, get_traffic_route_configs

try:
    from scenario_helper import start_manual_control_process
except ModuleNotFoundError:
    from scenario_events.scenario_helper import start_manual_control_process


START_TO_TRAFFIC_DELAY = 1.0
TRAFFIC_TO_TRASH_DELAY = 1.0
TRASH_TO_SNAKE_DELAY = 1.0
SNAKE_TO_SMELL_DELAY = 2.0
SMELL_TO_POORROAD_DELAY = 1.0
POORROAD_TO_DRIVERTRASH_DELAY = 1.0
DRIVERTRASH_TO_END_DELAY = 1.0

SIM_STEP_S = 0.05
run_in_singleFile_mode = True
DEBUG_MODE = True

TRIGGER_TRAFFIC = True
TRIGGER_TRASH = False
TRIGGER_POORROAD = False
TRIGGER_SMELL = True
TRIGGER_DRIVERTRASH = True
TRIGGER_SNAKE = True
# if set to an integer index (0-based) that snake config will be spawned immediately
# None (default) = normal hero-triggering is used
TRIGGER_SNAKE_IMMEDIATE = None

traffic_vehicle_count = 8
HERO_GREEN_LIGHT_HOLD_SECONDS = 2.0
hero_green = True

SNAKE_MAX_SPEED = 1.0
SNAKE_ARRIVE_THRESH = 1.0
SNAKE_STOP_AT_TARGET_DURATION = 1.0
SNAKE_LIFETIME_S = 20.0

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
	# exclude two-wheelers
	"motorcycle",
	"bicycle",
	"vehicle.harley-davidson.low_rider",
	"vehicle.kawasaki.ninja",
	"vehicle.vespa.zx125",
	"vehicle.yamaha.yzf",
	"vehicle.bh.crossbike",
	"vehicle.diamondback.century",
	"vehicle.gazelle.omafiets",
)

class Scenario02Runner:
    def __init__(self, host, port, tm_port, done_file=None, trigger_traffic=True, trigger_trash=True,
                 trigger_poorroad=True, trigger_smell=True, trigger_drivertrash=True, trigger_snake=True):
        self.client = carla.Client(host, port)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()
        self.host = host
        self.port = port
        self._tm_port = tm_port
        self._done_file = done_file
        self._rng = random.Random()
        self._debug_trash_box_lifetime = SIM_STEP_S * 2.0

        # load trash trigger config from static props module
        trash_configs = get_trash_trigger_config()
        self._trash_trigger_config = trash_configs[0] if trash_configs else None
        self._poorroad_trigger_configs = get_poorroad_trigger_config()
        self._traffic_route_configs = get_traffic_route_configs()
        self.poorroad_started = False
        self._poorroad_active_trigger_name = None
        self._poorroad_actor_ids = []
        self._traffic_vehicle_actor_ids = []

        self._trigger_traffic = trigger_traffic
        self._trigger_trash = trigger_trash
        self._trigger_poorroad = trigger_poorroad
        self._trigger_smell = trigger_smell
        self._trigger_drivertrash = trigger_drivertrash
        self._trigger_snake = trigger_snake
        # prefer explicit constructor arg; if None, fall back to module-level TRIGGER_SNAKE_IMMEDIATE
        self._trigger_snake_immediate = TRIGGER_SNAKE_IMMEDIATE

        self._start_sim_time = None
        self._scenario_done = False

        self.traffic_finished = False
        self.trash_finished = False
        self.poorroad_finished = False
        self.smell_finished = False
        self.drivertrash_finished = False
        self.snake_finished = False

        self._start_static_props_spawned = False
        self._persistent_static_actor_ids = []
        self._walker_actor_ids = []
        self._forced_hero_tl = {}
        self._snake_triggered = set()
        self._snake_routes = {}
        self._snake_route_active = False
        self._snake_route_done = False
        self._snake_walker_id = None
        self._snake_controller_id = None
        self._snake_spawn_time = None
        self._snake_last_update_time = None
        self._delay_states = {
            "start_to_traffic": {
                "delay": START_TO_TRAFFIC_DELAY,
                "started_at": None,
                "finished": False,
            },
            "traffic_to_trash": {
                "delay": TRAFFIC_TO_TRASH_DELAY,
                "started_at": None,
                "finished": False,
            },
            "trash_to_snake": {
                "delay": TRASH_TO_SNAKE_DELAY,
                "started_at": None,
                "finished": False,
            },
            "snake_to_smell": {
                "delay": SNAKE_TO_SMELL_DELAY,
                "started_at": None,
                "finished": False,
            },
            "smell_to_poorroad": {
                "delay": SMELL_TO_POORROAD_DELAY,
                "started_at": None,
                "finished": False,
            },
            "poorroad_to_drivertrash": {
                "delay": POORROAD_TO_DRIVERTRASH_DELAY,
                "started_at": None,
                "finished": False,
            },
            "drivertrash_to_end": {
                "delay": DRIVERTRASH_TO_END_DELAY,
                "started_at": None,
                "finished": False,
            },
        }
        # drivertrash manual control process tracking
        self.drivertrash_active = False
        self._drivertrash_triggered_keys = set()
        self._drivertrash_process = None

    def _start_delay_timer(self, delay_name, sim_time):
        delay_state = self._delay_states.get(delay_name)
        if delay_state is None:
            return
        if delay_state["started_at"] is None:
            print(f"[{delay_name}] delay started!")
        delay_state["started_at"] = sim_time
        delay_state["finished"] = False

    def _finish_delay_timer(self, delay_name, sim_time):
        delay_state = self._delay_states.get(delay_name)
        if delay_state is None:
            return
        if delay_state["started_at"] is None:
            print(f"[{delay_name}] delay started!")
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
            print(f"[{delay_name}] delay finished!")

    def _is_within_trigger(self, trigger_config, hero_location):
        if hero_location is None or trigger_config is None:
            return False
        center = trigger_config.get("trigger_location")
        x_tol = float(trigger_config.get("trigger_x_tolerance", 0.0))
        y_tol = float(trigger_config.get("trigger_y_tolerance", 0.0))
        if abs(hero_location.x - center.x) > x_tol:
            return False
        if abs(hero_location.y - center.y) > y_tol:
            return False
        return True

    def _draw_trash_trigger_box(self):
        if not DEBUG_MODE:
            return

        cfg = self._trash_trigger_config
        if cfg is None:
            return

        center = cfg.get("trigger_location")
        x_tol = float(cfg.get("trigger_x_tolerance", 0.0))
        y_tol = float(cfg.get("trigger_y_tolerance", 0.0))
        z_base = center.z
        z_top = z_base + 2.0
        color = carla.Color(r=0, g=255, b=0, a=255)
        thickness = 0.1
        life_time = self._debug_trash_box_lifetime

        p1 = carla.Location(x=center.x - x_tol, y=center.y - y_tol, z=z_base)
        p2 = carla.Location(x=center.x + x_tol, y=center.y - y_tol, z=z_base)
        p3 = carla.Location(x=center.x + x_tol, y=center.y + y_tol, z=z_base)
        p4 = carla.Location(x=center.x - x_tol, y=center.y + y_tol, z=z_base)

        p1_top = carla.Location(x=p1.x, y=p1.y, z=z_top)
        p2_top = carla.Location(x=p2.x, y=p2.y, z=z_top)
        p3_top = carla.Location(x=p3.x, y=p3.y, z=z_top)
        p4_top = carla.Location(x=p4.x, y=p4.y, z=z_top)

        self.world.debug.draw_line(p1, p2, thickness=thickness, color=color, life_time=life_time)
        self.world.debug.draw_line(p2, p3, thickness=thickness, color=color, life_time=life_time)
        self.world.debug.draw_line(p3, p4, thickness=thickness, color=color, life_time=life_time)
        self.world.debug.draw_line(p4, p1, thickness=thickness, color=color, life_time=life_time)

        self.world.debug.draw_line(p1_top, p2_top, thickness=thickness, color=color, life_time=life_time)
        self.world.debug.draw_line(p2_top, p3_top, thickness=thickness, color=color, life_time=life_time)
        self.world.debug.draw_line(p3_top, p4_top, thickness=thickness, color=color, life_time=life_time)
        self.world.debug.draw_line(p4_top, p1_top, thickness=thickness, color=color, life_time=life_time)

        self.world.debug.draw_line(p1, p1_top, thickness=thickness, color=color, life_time=life_time)
        self.world.debug.draw_line(p2, p2_top, thickness=thickness, color=color, life_time=life_time)
        self.world.debug.draw_line(p3, p3_top, thickness=thickness, color=color, life_time=life_time)
        self.world.debug.draw_line(p4, p4_top, thickness=thickness, color=color, life_time=life_time)
        return

    def _get_poorroad_trigger_for_location(self, hero_location):
        if hero_location is None or not self._poorroad_trigger_configs:
            return None
        for trigger_config in self._poorroad_trigger_configs:
            center = trigger_config.get("trigger_location")
            x_tol = float(trigger_config.get("trigger_x_tolerance", 0.0))
            y_tol = float(trigger_config.get("trigger_y_tolerance", 0.0))
            if abs(hero_location.x - center.x) <= x_tol and abs(hero_location.y - center.y) <= y_tol:
                return trigger_config
        return None

    def _spawn_poorroad_static_props(self, trigger_config):
        if not trigger_config:
            return False
        bp_lib = self.world.get_blueprint_library()
        spawned = 0
        for spawn in trigger_config.get("spawn_configs", []):
            transform = spawn.get("transform")
            blueprint_ids = spawn.get("blueprints", [])
            bp = None
            for bid in blueprint_ids:
                try:
                    bp = bp_lib.find(bid)
                except Exception:
                    bp = None
                if bp is not None:
                    break
            if bp is None:
                matches = list(bp_lib.filter("static.prop.*"))
                bp = matches[0] if matches else None
            if bp is None:
                print("[Scenario02] WARNUNG: Keine static props Blueprints gefunden fuer PoorRoad.")
                continue
            actor = self.world.try_spawn_actor(bp, transform)
            if actor is None:
                print(f"[Scenario02] WARNUNG: PoorRoad static prop spawn fehlgeschlagen blueprint={bp.id}")
                continue
            self._poorroad_actor_ids.append(actor.id)
            spawned += 1
            print(f"[Scenario02] PoorRoad static prop gespawnt id={actor.id} blueprint={bp.id}")
        return spawned > 0

    def _destroy_poorroad_static_props(self):
        if not self._poorroad_actor_ids:
            return
        try:
            self.client.apply_batch([carla.command.DestroyActor(actor_id) for actor_id in self._poorroad_actor_ids])
        except Exception:
            for actor_id in list(self._poorroad_actor_ids):
                try:
                    actor = self.world.get_actor(actor_id)
                    if actor is not None:
                        actor.destroy()
                except Exception:
                    pass
        self._poorroad_actor_ids = []
        self._poorroad_active_trigger_name = None
        print("[Scenario02] PoorRoad props entfernt.")

    def _update_poorroad_phase(self, hero_location):
        if not self.poorroad_started or self.poorroad_finished:
            return
        trigger_config = self._get_poorroad_trigger_for_location(hero_location)
        if trigger_config is None:
            return
        trigger_name = trigger_config.get("name")
        if trigger_name == self._poorroad_active_trigger_name:
            return
        if self._poorroad_active_trigger_name is None:
            self._poorroad_active_trigger_name = trigger_name
            spawn_config = trigger_config if trigger_config.get("spawn_configs") else next(
                (cfg for cfg in self._poorroad_trigger_configs if cfg.get("spawn_configs")),
                None,
            )
            spawned = False
            if spawn_config is not None:
                spawned = self._spawn_poorroad_static_props(spawn_config)
            if spawned:
                print(f"[Scenario02] PoorRoad props bei erstem Trigger '{trigger_name}' gespawnt.")
            else:
                print(f"[Scenario02] PoorRoad erster Trigger '{trigger_name}' erkannt, aber keine Props gespawnt.")
            return
        if self._poorroad_active_trigger_name is not None and trigger_name != self._poorroad_active_trigger_name:
            self._destroy_poorroad_static_props()
            self.poorroad_finished = True
            print(f"[Scenario02] PoorRoad zweiter Trigger '{trigger_name}' erreicht, Props entfernt. PoorRoad abgeschlossen.")
            return

    def _update_traffic_trigger(self):
        delay_state = self._delay_states.get("start_to_traffic")
        return delay_state is not None and delay_state["finished"]

    def _get_actor_blueprints(self, filter_pattern):
        bps = list(self.world.get_blueprint_library().filter(filter_pattern))
        if not bps:
            print(f"[Scenario02] WARNUNG: Keine Blueprints für {filter_pattern} gefunden!")
        return bps

    def _filter_blocked_vehicle_blueprints(self, blueprints):
        return [bp for bp in blueprints if not any(k in bp.id.lower() for k in BLOCKED_VEHICLE_KEYWORDS)]

    def _get_traffic_manager(self):
        return self.client.get_trafficmanager(self._tm_port)

    def _force_hero_traffic_light(self, ego, sim_time):
        if not hero_green:
            return
        if ego is None:
            return
        
        try:
            if not ego.is_at_traffic_light():
                return
        except Exception as e:
            return

        try:
            tl = ego.get_traffic_light()
        except Exception as e:
            return

        if tl is None:
            return

        try:
            current_state = tl.get_state()
            state_name = "Unknown"
            if current_state == carla.TrafficLightState.Red:
                state_name = "Red"
            elif current_state == carla.TrafficLightState.Yellow:
                state_name = "Yellow"
            elif current_state == carla.TrafficLightState.Green:
                state_name = "Green"
            
            print(f"[Scenario02] HERO TRAFFIC LIGHT DETECTED: light_id={tl.id}, current_state={state_name}")
            if current_state != carla.TrafficLightState.Green:
                print(f"[Scenario02] HERO setting traffic light to GREEN (was {state_name})")
                tl.set_state(carla.TrafficLightState.Green)
            if hasattr(tl, 'set_green_time'):
                tl.set_green_time(HERO_GREEN_LIGHT_HOLD_SECONDS)
                print(f"[Scenario02] HERO traffic light green time set to {HERO_GREEN_LIGHT_HOLD_SECONDS}s")
            # record forced green timestamp so we can release control after hold time
            try:
                self._forced_hero_tl[tl.id] = sim_time
            except Exception:
                pass
        except Exception as e:
            print(f"[Scenario02] ERROR setting hero traffic light: {e}")

    def _project_to_driving_lane(self, location):
        map_ = self.world.get_map()
        waypoint = map_.get_waypoint(location, project_to_road=True, lane_type=carla.LaneType.Driving)
        return waypoint.transform.location if waypoint is not None else location

    def _update_forced_hero_lights(self, sim_time):
        # release any traffic lights forced for hero after hold seconds
        removed = []
        for tl_id, started in list(self._forced_hero_tl.items()):
            try:
                if (sim_time - started) >= HERO_GREEN_LIGHT_HOLD_SECONDS:
                    tl = self.world.get_actor(tl_id)
                    if tl is not None:
                        # release: allow normal logic to resume by not touching state further
                        print(f"[Scenario02] HERO releasing traffic light id={tl_id} after {HERO_GREEN_LIGHT_HOLD_SECONDS}s")
                    removed.append(tl_id)
            except Exception:
                removed.append(tl_id)
        for r in removed:
            self._forced_hero_tl.pop(r, None)

    def _build_route_locations_from_waypoints(self, waypoints):
        route_locations = []
        for waypoint in waypoints:
            if isinstance(waypoint, carla.Location):
                projected = self._project_to_driving_lane(waypoint)
                route_locations.append(projected)
        return route_locations

    def _spawn_traffic_route_vehicle(self, blueprint, transform, route_locations, sim_time):
        if blueprint is None or transform is None or len(route_locations) < 2:
            return None

        # try initial spawn
        actor = self.world.try_spawn_actor(blueprint, transform)
        if actor is None:
            loc = transform.location if transform is not None else None
            offsets = [0.6, 1.0]
            for off in offsets:
                try:
                    if loc is None:
                        break
                    new_loc = carla.Location(x=loc.x, y=loc.y, z=loc.z + off)
                    new_transform = carla.Transform(new_loc, transform.rotation)
                    actor = self.world.try_spawn_actor(blueprint, new_transform)
                    if actor is not None:
                        transform = new_transform
                        break
                except Exception:
                    actor = None

            if actor is None:
                return None

        # if spawned (initial or retry), continue setup
        try:
            actor.set_autopilot(True, self._get_traffic_manager().get_port())
        except Exception:
            pass

        try:
            self._get_traffic_manager().set_path(actor, route_locations)
        except Exception as exc:
            print(f"[Scenario02] WARNUNG: set_path fehlgeschlagen für actor id={actor.id}: {exc}")

        self._traffic_vehicle_actor_ids.append(actor.id)
        return actor

    def _update_trash_trigger(self):
        delay_state = self._delay_states.get("traffic_to_trash")
        return delay_state is not None and delay_state["finished"]

    def _update_snake_trigger(self):
        delay_state = self._delay_states.get("trash_to_snake")
        return delay_state is not None and delay_state["finished"]

    def _update_smell_trigger(self):
        delay_state = self._delay_states.get("snake_to_smell")
        return delay_state is not None and delay_state["finished"]

    def _update_poorroad_trigger(self):
        delay_state = self._delay_states.get("smell_to_poorroad")
        return delay_state is not None and delay_state["finished"]

    def _update_drivertrash_trigger(self):
        delay_state = self._delay_states.get("poorroad_to_drivertrash")
        return delay_state is not None and delay_state["finished"]

    def _update_end_trigger(self):
        delay_state = self._delay_states.get("drivertrash_to_end")
        return delay_state is not None and delay_state["finished"]

    def find_hero(self):
        for actor in self.world.get_actors():
            if actor.attributes.get("role_name") in ["hero", "default_player"]:
                return actor
        return None

    def start_trash(self):
        def _spawn_trash_static_props(self, trigger_config=None):
            spawn_configs = []
            if trigger_config is None:
                trigger_config = self._trash_trigger_config
            spawn_configs = trigger_config.get("spawn_configs", []) if trigger_config is not None else []

            bp_lib = self.world.get_blueprint_library()
            spawned = 0
            for spawn in spawn_configs:
                transform = spawn.get("transform")
                blueprint_ids = spawn.get("blueprints", [])
                bp = None
                if blueprint_ids:
                    # try the first blueprint id that exists
                    for bid in blueprint_ids:
                        try:
                            bp = bp_lib.find(bid)
                        except Exception:
                            bp = None
                        if bp is not None:
                            break
                # fallback: try generic static.prop filter
                if bp is None:
                    matches = list(bp_lib.filter("static.prop.*"))
                    bp = matches[0] if matches else None

                if bp is None:
                    print("[Scenario02] WARNUNG: Keine static props Blueprints gefunden.")
                    continue

                actor = self.world.try_spawn_actor(bp, transform)
                if actor is None:
                    print(f"[Scenario02] WARNUNG: static prop spawn fehlgeschlagen blueprint={bp.id}")
                    continue
                self._persistent_static_actor_ids.append(actor.id)
                spawned += 1
                print(f"[Scenario02] Static prop gespawnt id={actor.id} blueprint={bp.id}")

            return spawned > 0

        # make function visible as method
        setattr(self, "_spawn_trash_static_props", _spawn_trash_static_props.__get__(self))

        if self.trash_finished:
            return
        print("[Scenario02] start_trash()")
        # spawn static props defined in trigger config
        try:
            ok = self._spawn_trash_static_props(self._trash_trigger_config)
            if not ok:
                print("[Scenario02] WARNUNG: Keine statischen Props gespawnt.")
        except Exception as exc:
            print(f"[Scenario02] ERROR beim Spawnen statischer Props: {exc}")

        self.trash_finished = True

    def start_traffic(self, sim_time=0.0, traffic_vehicle_count=None):
        if self.traffic_finished:
            return
        traffic_count = int(traffic_vehicle_count) if traffic_vehicle_count is not None else int(globals().get('traffic_vehicle_count', 8))
        print("[Scenario02] start_traffic()")
        total_route_configs = len(self._traffic_route_configs) if self._traffic_route_configs is not None else 0
        print(f"[Scenario02] Traffic: route config count={total_route_configs}")

        route_entries = []
        for route_config in self._traffic_route_configs:
            route_locations = self._build_route_locations_from_waypoints(route_config.get("waypoints", []))
            if len(route_locations) < 2:
                print(f"[Scenario02] Traffic: Route '{route_config.get('name')}' skipped (not enough projected waypoints: {len(route_locations)})")
                continue
            max_starts = len(route_locations) - 1
            route_entries.append({
                "route_config": route_config,
                "route_locations": route_locations,
                "max_starts": max_starts,
                "next_start": 0,
            })

        if not route_entries:
            print("[Scenario02] WARNUNG: Keine Traffic-Routen verfügbar, Traffic event abgeschlossen.")
            self.traffic_finished = True
            return

        # allocate vehicles evenly across routes in round-robin order
        allocations = []
        while len(allocations) < traffic_count:
            allocated_this_round = False
            for entry in route_entries:
                if len(allocations) >= traffic_count:
                    break
                if entry["next_start"] < entry["max_starts"]:
                    allocations.append((entry["route_config"], entry["route_locations"], entry["next_start"]))
                    entry["next_start"] += 1
                    allocated_this_round = True
            if not allocated_this_round:
                break

        possible_spawns = len(allocations)
        if possible_spawns == 0:
            print("[Scenario02] WARNUNG: Keine möglichen Spawn-Positionen für Traffic erkannt.")
            self.traffic_finished = True
            return

        vehicle_blueprints = self._filter_blocked_vehicle_blueprints(self._get_actor_blueprints("vehicle.*"))
        if not vehicle_blueprints:
            print("[Scenario02] WARNUNG: Keine geeigneten Fahrzeug-Blueprints für Traffic-Spawn gefunden.")
            self.traffic_finished = True
            return

        spawned = 0
        failed_spawns = 0
        for route_config, route_locations, start_index in allocations:
            transform_location = route_locations[start_index]
            next_location = route_locations[start_index + 1]
            yaw = math.degrees(math.atan2(next_location.y - transform_location.y, next_location.x - transform_location.x))
            transform = carla.Transform(transform_location, carla.Rotation(yaw=yaw, pitch=0.0, roll=0.0))
            blueprint = self._rng.choice(vehicle_blueprints)
            route_path = route_locations[start_index:]
            actor = self._spawn_traffic_route_vehicle(blueprint, transform, route_path, sim_time)
            if actor is not None:
                spawned += 1
            else:
                failed_spawns += 1

        print(f"[Scenario02] Traffic: spawned {spawned}/{possible_spawns} vehicles (requested={traffic_count}, routes={len(route_entries)})")
        if failed_spawns > 0:
            print(f"[Scenario02] Traffic: failed to spawn {failed_spawns} vehicles")

        self.traffic_finished = True

    def start_uncivbehav(self):
        if self.uncivbehav_finished:
            return
        print("[Scenario02] start_uncivbehav()")
        self.uncivbehav_finished = True

    def start_poorroad(self, hero_location=None):
        if self.poorroad_finished or self.poorroad_started:
            return
        print("[Scenario02] start_poorroad()")
        self.poorroad_started = True
        self._update_poorroad_phase(hero_location)

    def start_smell(self):
        if self.smell_finished:
            return
        print("[Scenario02] start_smell()")
        print("Confront with smelly stuff now!")
        while True:
            try:
                user_input = input("Press J + Enter to continue: ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print("[Scenario02] Smell prompt interrupted, waiting for J + Enter...")
                continue
            if user_input == "j":
                break
            print("Please press J and Enter to continue.")
        self.smell_finished = True

    def start_drivertrash(self):
        if self.drivertrash_finished:
            return
        print("[Scenario02] start_drivertrash()")
        # mark active and let main loop handle spawn/launch logic
        self.drivertrash_active = True

    def _get_snake_route_config(self, hero_location, hero_velocity=None):
        try:
            from events_scenario02_static_props import get_snake_configs
        except Exception:
            from scenario_events.events_scenario02_static_props import get_snake_configs

        snake_configs = get_snake_configs() if callable(get_snake_configs) else []
        for cfg in snake_configs:
            trigger_location = cfg.get("trigger_location")
            if trigger_location is None:
                continue
            if abs(hero_location.x - trigger_location.x) > cfg.get("trigger_x_tolerance", 2.0):
                continue
            if abs(hero_location.y - trigger_location.y) > cfg.get("trigger_y_tolerance", 2.0):
                continue
            # optional direction check
            required_axis = cfg.get("trigger_direction_axis")
            required_sign = cfg.get("trigger_direction_sign")
            if required_axis is not None and required_sign is not None:
                if hero_velocity is None:
                    continue
                axis_vel = hero_velocity.x if required_axis == "x" else hero_velocity.y
                if axis_vel * required_sign <= 0.0:
                    continue
            return cfg
        return None

    def _get_drivertrash_config(self, hero_location, hero_velocity=None):
        try:
            from events_scenario02_static_props import DRIVERTRASH_SPAWN_CONFIGS
        except Exception:
            from scenario_events.events_scenario02_static_props import DRIVERTRASH_SPAWN_CONFIGS

        configs = DRIVERTRASH_SPAWN_CONFIGS if isinstance(DRIVERTRASH_SPAWN_CONFIGS, (list, tuple)) else []
        for cfg in configs:
            trigger_location = cfg.get("trigger_location")
            if trigger_location is None:
                continue
            if abs(hero_location.x - trigger_location.x) > cfg.get("trigger_x_tolerance", 2.0):
                continue
            if abs(hero_location.y - trigger_location.y) > cfg.get("trigger_y_tolerance", 2.0):
                continue
            # optional direction check
            required_axis = cfg.get("trigger_direction_axis")
            required_sign = cfg.get("trigger_direction_sign")
            if required_axis is not None and required_sign is not None:
                if hero_velocity is None:
                    continue
                axis_vel = hero_velocity.x if required_axis == "x" else hero_velocity.y
                if axis_vel * required_sign <= 0.0:
                    continue
            # second optional axis
            required_axis_2 = cfg.get("trigger_direction_axis_2")
            required_sign_2 = cfg.get("trigger_direction_sign_2")
            if required_axis_2 is not None and required_sign_2 is not None:
                if hero_velocity is None:
                    continue
                axis_vel2 = hero_velocity.x if required_axis_2 == "x" else hero_velocity.y
                if axis_vel2 * required_sign_2 <= 0.0:
                    continue
            return cfg
        return None

    def _start_drivertrash_manual_control_from_config(self, config):
        name = config.get("name")
        if name in self._drivertrash_triggered_keys:
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

        self._drivertrash_process = start_manual_control_process(
            host=self.host,
            port=self.port,
            profile='supervisor4home',
            done_file=None,
            vehicle_id=vehicle_id,
            vehicle_color=vehicle_color,
            spawn_transform=spawn_transform,
            audio_mode=audio_mode,
            existing_process=self._drivertrash_process,
            log_prefix='Scenario02',
        )

        if self._drivertrash_process is None:
            return False

        print(
            f"[Scenario02] Started drivertrash manual_control: "
            f"vehicleID={vehicle_id}, vehicleColor={vehicle_color}, audio_mode={audio_mode}"
        )

        while True:
            try:
                user_input = input("\n[Scenario02] Press 'J' + Enter to continue scenario: ").strip().upper()
            except (KeyboardInterrupt, EOFError):
                print("[Scenario02] DriverTrash prompt interrupted, waiting for J + Enter...")
                continue
            if user_input == 'J':
                break

        self._drivertrash_triggered_keys.add(name)
        return True

    def start_snake(self, sim_time=None):
        # spawn exactly one snake route when hero triggers one
        if self.snake_finished or self._snake_route_active or self._snake_route_done:
            return False

        ego = self.find_hero()
        if ego is None:
            return False
        hero_loc = ego.get_location()
        hero_vel = ego.get_velocity()
        route_config = self._get_snake_route_config(hero_loc, hero_vel)
        if route_config is None:
            # nothing to spawn yet
            return False

        try:
            from events_scenario02_static_props import get_snake_configs
        except Exception:
            from scenario_events.events_scenario02_static_props import get_snake_configs

        bp_lib = self.world.get_blueprint_library()
        walker_bp_id = "walker.pedestrian.0052"
        walker_bp = bp_lib.find(walker_bp_id)
        if walker_bp is None:
            print(f"[Scenario02] WARNUNG: Walker blueprint {walker_bp_id} nicht gefunden.")
            return False

        if walker_bp.has_attribute("is_invincible"):
            try:
                walker_bp.set_attribute("is_invincible", "false")
            except Exception:
                pass

        spawn_confs = route_config.get("spawn_configs", [])
        if not spawn_confs:
            print(f"[Scenario02] WARNUNG: Snake route {route_config.get('name')} hat keine spawn_configs.")
            return False

        spawn_transform = spawn_confs[0].get("transform")
        target_loc = None
        if len(spawn_confs) > 1:
            t = spawn_confs[1].get("transform")
            target_loc = t.location if t is not None else None

        walker = self.world.try_spawn_actor(walker_bp, spawn_transform)
        if walker is None:
            print(f"[Scenario02] WARNUNG: Snake walker '{route_config.get('name')}' konnte nicht gespawnt werden.")
            return False

        # Do not spawn a controller for snake; use manual walker.apply_control like SANIMAL
        controller = None

        # set active route state similar to SANIMAL in scenario06
        self._snake_route_active = True
        self._snake_route_done = False
        self._snake_walker_id = walker.id
        self._snake_controller_id = controller.id if controller is not None else None
        self._snake_spawn_time = sim_time
        self._snake_last_update_time = sim_time
        self._snake_route_config = route_config
        self._snake_route_forward = True
        self._snake_arrival_time = None
        self.snake_finished = False
        self._walker_actor_ids.append(walker.id)

        print(f"[Scenario02] Snake spawned: id={walker.id}, route={route_config.get('name')}, sim_time={sim_time}")

        # start movement like SANIMAL
        try:
            if controller is not None and target_loc is not None:
                controller.start()
                controller.go_to_location(target_loc)
                controller.set_max_speed(route_config.get("max_speed", 1.0))
                print(f"[Scenario02] Snake controller started, target=({target_loc.x:.2f},{target_loc.y:.2f},{target_loc.z:.2f})")
        except Exception as e:
            print(f"[Scenario02] WARNUNG: Snake controller start failed: {e}")

        return True

    def _spawn_snake_by_config(self, route_config, sim_time=None):
        # spawn snake directly from a given route_config (used for immediate testing)
        if self.snake_finished or self._snake_route_active or self._snake_route_done:
            return False

        if route_config is None:
            return False

        bp_lib = self.world.get_blueprint_library()
        walker_bp_id = "walker.pedestrian.0052"
        walker_bp = bp_lib.find(walker_bp_id)
        if walker_bp is None:
            print(f"[Scenario02] WARNUNG: Walker blueprint {walker_bp_id} nicht gefunden.")
            return False

        try:
            if walker_bp.has_attribute("is_invincible"):
                walker_bp.set_attribute("is_invincible", "false")
        except Exception:
            pass

        spawn_confs = route_config.get("spawn_configs", [])
        if not spawn_confs:
            print(f"[Scenario02] WARNUNG: Snake route {route_config.get('name')} hat keine spawn_configs.")
            return False

        spawn_transform = spawn_confs[0].get("transform")
        target_loc = None
        if len(spawn_confs) > 1:
            t = spawn_confs[1].get("transform")
            target_loc = t.location if t is not None else None

        walker = self.world.try_spawn_actor(walker_bp, spawn_transform)
        if walker is None:
            print(f"[Scenario02] WARNUNG: Snake walker '{route_config.get('name')}' konnte nicht gespawnt werden.")
            return False

        # set active route state similar to SANIMAL in scenario06
        self._snake_route_active = True
        self._snake_route_done = False
        self._snake_walker_id = walker.id
        self._snake_controller_id = None
        self._snake_spawn_time = sim_time
        self._snake_last_update_time = sim_time
        self._snake_route_config = route_config
        self._snake_route_forward = True
        self._snake_arrival_time = None
        self.snake_finished = False
        self._walker_actor_ids.append(walker.id)

        print(f"[Scenario02] Immediate Snake spawned: id={walker.id}, route={route_config.get('name')}, sim_time={sim_time}")
        return True

    def _update_snake(self, sim_time):
        if not self._snake_route_active:
            return

        walker = self.world.get_actor(self._snake_walker_id) if self._snake_walker_id else None
        controller = self.world.get_actor(self._snake_controller_id) if self._snake_controller_id else None
        if walker is None:
            # walker missing -> finish
            self._snake_route_active = False
            self._snake_route_done = True
            self.snake_finished = True
            self._finish_delay_timer("snake_to_smell", sim_time)
            print("[Scenario02] Snake walker missing; marking snake finished.")
            return

        # follow SANIMAL movement logic: manual walker.apply_control towards target
        route_cfg = self._snake_route_config if hasattr(self, '_snake_route_config') else None
        if route_cfg is None:
            return

        start_location = route_cfg.get("spawn_configs", [None])[0].get("transform").location if route_cfg.get("spawn_configs") else None
        end_location = None
        spawn_confs = route_cfg.get("spawn_configs", [])
        if len(spawn_confs) > 1:
            t = spawn_confs[1].get("transform")
            end_location = t.location if t is not None else None

        # choose target depending on current route direction
        target_location = end_location if getattr(self, '_snake_route_forward', True) else start_location
        current_location = walker.get_location()

        if self._snake_spawn_time is not None and (sim_time - self._snake_spawn_time) >= SNAKE_LIFETIME_S:
            try:
                walker.destroy()
            except Exception:
                pass
            self._snake_route_active = False
            self._snake_route_done = True
            self.snake_finished = True
            self._finish_delay_timer("snake_to_smell", sim_time)
            print(f"[Scenario02] Snake lifetime reached: id={walker.id}, sim_time={sim_time:.2f}s")
            return

        if self._snake_last_update_time is None:
            delta_time = SIM_STEP_S
        else:
            delta_time = max(0.0, sim_time - self._snake_last_update_time)
            if delta_time == 0.0:
                delta_time = SIM_STEP_S
        self._snake_last_update_time = sim_time

        if target_location is None:
            return

        distance = math.hypot(current_location.x - target_location.x, current_location.y - target_location.y)
        if distance <= SNAKE_ARRIVE_THRESH:
            if getattr(self, '_snake_arrival_time', None) is None:
                self._snake_arrival_time = sim_time
                loc_desc = 'end' if self._snake_route_forward else 'start'
                print(f"[Scenario02] Snake reached {loc_desc}: id={walker.id}, sim_time={sim_time:.2f}s")

            if (sim_time - self._snake_arrival_time) >= SNAKE_STOP_AT_TARGET_DURATION:
                if self._snake_route_forward:
                    # reached end first time -> turn around and go back
                    self._snake_route_forward = False
                    self._snake_arrival_time = None
                    print(f"[Scenario02] Snake turning around at end and returning to start: id={walker.id}")
                else:
                    # returned to start -> finish and cleanup
                    try:
                        walker.destroy()
                    except Exception:
                        pass
                    if self._snake_walker_id in self._walker_actor_ids:
                        self._walker_actor_ids.remove(self._snake_walker_id)
                    self._snake_route_active = False
                    self._snake_route_done = True
                    self._snake_walker_id = None
                    self._snake_controller_id = None
                    self.snake_finished = True
                    self._finish_delay_timer("snake_to_smell", sim_time)
                    print("[Scenario02] Snake returned to start and finished; starting snake_to_smell delay.")
                return

        max_step = SNAKE_MAX_SPEED * delta_time
        if max_step <= 0.0:
            return

        try:
            direction_x = target_location.x - current_location.x
            direction_y = target_location.y - current_location.y
            direction_length = math.hypot(direction_x, direction_y)
            if direction_length == 0.0:
                return

            walker.apply_control(
                carla.WalkerControl(
                    direction=carla.Vector3D(x=direction_x / direction_length, y=direction_y / direction_length, z=0.0),
                    speed=SNAKE_MAX_SPEED,
                    jump=False,
                )
            )
        except Exception as exc:
            print(f"[Scenario02] WARNUNG: Snake konnte nicht manuell bewegt werden: {exc}")
            try:
                walker.destroy()
            except Exception:
                pass
            self._snake_route_active = False
            self._snake_route_done = True
            self.snake_finished = True
            self._finish_delay_timer("snake_to_smell", sim_time)

    def _skip_traffic_trigger(self, sim_time):
        if self.traffic_finished:
            return
        self._finish_delay_timer("start_to_traffic", sim_time)
        self.traffic_finished = True
        print("[Scenario02] Traffic trigger skipped.")

    def _skip_trash_trigger(self, sim_time):
        if self.trash_finished:
            return
        self._finish_delay_timer("traffic_to_trash", sim_time)
        self.start_trash()
        print("[Scenario02] Trash trigger skipped.")

    def _skip_poorroad_trigger(self, sim_time):
        if self.poorroad_finished:
            return
        self._finish_delay_timer("smell_to_poorroad", sim_time)
        self.poorroad_started = True
        self.poorroad_finished = True
        print("[Scenario02] PoorRoad trigger skipped.")

    def _skip_smell_trigger(self, sim_time):
        if self.smell_finished:
            return
        self._finish_delay_timer("snake_to_smell", sim_time)
        self.start_smell()
        print("[Scenario02] Smell trigger skipped.")

    def _skip_drivertrash_trigger(self, sim_time):
        if self.drivertrash_finished:
            return
        self._finish_delay_timer("poorroad_to_drivertrash", sim_time)
        self.start_drivertrash()
        print("[Scenario02] DriverTrash trigger skipped.")

    def _skip_snake_trigger(self, sim_time):
        if self.snake_finished:
            return
        self._finish_delay_timer("trash_to_snake", sim_time)
        self.start_snake()
        print("[Scenario02] Snake trigger skipped.")

    def _spawn_start_static_props(self):
        if self._start_static_props_spawned:
            return True

        bp_lib = self.world.get_blueprint_library()
        spawn_configs = get_start_barrier_spawns()
        spawned_count = 0
        failed_configs = []

        for prop_config in spawn_configs:
            name = prop_config.get("name", "unknown_prop")
            blueprint_id = prop_config.get("blueprints", [None])[0]
            if not blueprint_id:
                print(f"[Scenario02] Start-Props WARNUNG: '{name}' hat keine Blueprint-ID.")
                failed_configs.append(name)
                continue

            transform = prop_config.get("transform")
            location = transform.location if transform is not None else None
            rotation = transform.rotation if transform is not None else None
            matches = [bp.id for bp in bp_lib.filter(blueprint_id)]
            print(
                f"[Scenario02] Start-Props versuche '{name}' blueprint='{blueprint_id}' "
                f"matches={matches} "
                f"loc=({location.x:.2f}, {location.y:.2f}, {location.z:.2f}) "
                f"rot=({rotation.pitch:.1f}, {rotation.yaw:.1f}, {rotation.roll:.1f})"
                if location is not None and rotation is not None
                else f"[Scenario02] Start-Props versuche '{name}' blueprint='{blueprint_id}' matches={matches}"
            )

            try:
                prop_bp = bp_lib.find(blueprint_id)
                print(f"[Scenario02] Start-Props Blueprint gefunden für '{name}': {prop_bp.id}")
            except Exception as exc:
                print(f"[Scenario02] Start-Props WARNUNG: Blueprint '{blueprint_id}' für '{name}' nicht gefunden: {exc}")
                failed_configs.append(name)
                continue

            actor = self.world.try_spawn_actor(prop_bp, transform)
            if actor is None:
                print(
                    f"[Scenario02] Start-Props WARNUNG: Spawn für '{name}' fehlgeschlagen. "
                    f"Wahrscheinliche Ursache: Collision / ungültiger Transform. "
                    f"blueprint='{prop_bp.id}'"
                )
                failed_configs.append(name)
                continue

            self._persistent_static_actor_ids.append(actor.id)
            spawned_count += 1
            print(f"[Scenario02] Start-Props OK: '{name}' actor_id={actor.id} blueprint='{prop_bp.id}' persistent=True")

        self._start_static_props_spawned = True
        if spawned_count == len(spawn_configs):
            print(f"[Scenario02] Start-Props: {spawned_count}/{len(spawn_configs)} gespawnt.")
        else:
            print(
                f"[Scenario02] Start-Props: {spawned_count}/{len(spawn_configs)} gespawnt, "
                f"nicht alle konnten gesetzt werden. Fehlschläge={failed_configs}"
            )
        return spawned_count == len(spawn_configs)

    def destroy(self):
        # destroy any persistent static actors we spawned
        if self._persistent_static_actor_ids:
            try:
                self.client.apply_batch([carla.command.DestroyActor(actor_id) for actor_id in self._persistent_static_actor_ids])
            except Exception:
                for actor_id in list(self._persistent_static_actor_ids):
                    try:
                        actor = self.world.get_actor(actor_id)
                        if actor is not None:
                            actor.destroy()
                    except Exception:
                        pass
            self._persistent_static_actor_ids = []
        # destroy any poorroad static props we spawned
        if self._poorroad_actor_ids:
            self._destroy_poorroad_static_props()
        # destroy any traffic vehicles we spawned
        if self._traffic_vehicle_actor_ids:
            try:
                self.client.apply_batch([carla.command.DestroyActor(actor_id) for actor_id in self._traffic_vehicle_actor_ids])
            except Exception:
                for actor_id in list(self._traffic_vehicle_actor_ids):
                    try:
                        actor = self.world.get_actor(actor_id)
                        if actor is not None:
                            actor.destroy()
                    except Exception:
                        pass
            self._traffic_vehicle_actor_ids = []

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
            print(f"[Scenario02] WARNING: could not write done signal file: {exc}")

    def run(self):
        print("[Scenario02] Running...")
        if run_in_singleFile_mode:
            self.world.set_weather(carla.WeatherParameters.WetCloudyNoon)
            print("[Scenario02] Weather set to WetCloudyNoon for single-file mode")

        try:
            while True:
                self.world.wait_for_tick()
                if DEBUG_MODE:
                    self._draw_trash_trigger_box()
                sim_time = self.world.get_snapshot().timestamp.elapsed_seconds
                ego = self.find_hero()
                hero_location = ego.get_location() if ego is not None else None
                self._update_poorroad_phase(hero_location)

                if self._start_sim_time is None:
                    self._start_sim_time = sim_time
                    self._spawn_start_static_props()

                self._force_hero_traffic_light(ego, sim_time)
                self._update_forced_hero_lights(sim_time)
                # update snake route state if active
                try:
                    self._update_snake(sim_time)
                except Exception:
                    pass

                start_to_traffic_state = self._delay_states["start_to_traffic"]
                if start_to_traffic_state["started_at"] is None:
                    self._start_delay_timer("start_to_traffic", sim_time)
                self._update_delay_timer("start_to_traffic", sim_time)

                if self._update_traffic_trigger() and not self.traffic_finished:
                    if not self._trigger_traffic:
                        self._skip_traffic_trigger(sim_time)
                    else:
                        self.start_traffic(sim_time)

                traffic_to_trash_state = self._delay_states["traffic_to_trash"]
                if self.traffic_finished:
                    if traffic_to_trash_state["started_at"] is None:
                        self._start_delay_timer("traffic_to_trash", sim_time)
                    self._update_delay_timer("traffic_to_trash", sim_time)

                if self.traffic_finished and traffic_to_trash_state["finished"] and not self.trash_finished:
                    if not self._trigger_trash:
                        self._skip_trash_trigger(sim_time)
                    else:
                        if self._is_within_trigger(self._trash_trigger_config, hero_location):
                            self.start_trash()
                        else:
                            if DEBUG_MODE:
                                print("[Scenario02] Hero not inside trash trigger zone yet.")

                trash_to_snake_state = self._delay_states["trash_to_snake"]
                if self.trash_finished:
                    if trash_to_snake_state["started_at"] is None:
                        self._start_delay_timer("trash_to_snake", sim_time)
                    self._update_delay_timer("trash_to_snake", sim_time)

                if self.trash_finished and trash_to_snake_state["finished"] and not self.snake_finished:
                    if not self._trigger_snake:
                        self._skip_snake_trigger(sim_time)
                    else:
                        # determine immediate index: prefer instance value, fallback to global
                        raw_idx = getattr(self, '_trigger_snake_immediate', TRIGGER_SNAKE_IMMEDIATE)
                        # print(f"[Scenario02] trigger_snake_immediate raw value: {raw_idx}")
                        # if None -> normal hero-triggered spawn
                        if raw_idx is None:
                            # print("[Scenario02] trigger_snake_immediate is None -> waiting for hero trigger")
                            self.start_snake(sim_time)
                        else:
                            # accept True -> index 0, or integer index or numeric string
                            idx_int = None
                            if isinstance(raw_idx, bool):
                                if raw_idx:
                                    idx_int = 0
                            else:
                                try:
                                    idx_int = int(raw_idx)
                                except Exception:
                                    idx_int = None

                            try:
                                from events_scenario02_static_props import get_snake_configs
                            except Exception:
                                from scenario_events.events_scenario02_static_props import get_snake_configs
                            snake_configs = get_snake_configs() if callable(get_snake_configs) else []
                            # print(f"[Scenario02] snake_configs count={len(snake_configs)}")

                            if idx_int is None:
                                # print(f"[Scenario02] WARNUNG: trigger_snake_immediate value invalid: {raw_idx}")
                                pass
                            elif idx_int < 0 or idx_int >= len(snake_configs):
                                # print(f"[Scenario02] WARNUNG: trigger_snake_immediate index out of range: {idx_int}")
                                pass
                            else:
                                route_config = snake_configs[idx_int]
                                # print(f"[Scenario02] spawning immediate snake index={idx_int} name={route_config.get('name')}")
                                # spawn immediately now that the delay finished
                                try:
                                    self._spawn_snake_by_config(route_config, sim_time)
                                except Exception as e:
                                    print(f"[Scenario02] WARNUNG: failed to spawn immediate snake index={idx_int}: {e}")

                snake_to_smell_state = self._delay_states["snake_to_smell"]
                if self.snake_finished:
                    if snake_to_smell_state["started_at"] is None:
                        self._start_delay_timer("snake_to_smell", sim_time)
                    self._update_delay_timer("snake_to_smell", sim_time)

                if self.snake_finished and snake_to_smell_state["finished"] and not self.smell_finished:
                    if not self._trigger_smell:
                        self._skip_smell_trigger(sim_time)
                    else:
                        self.start_smell()

                smell_to_poorroad_state = self._delay_states["smell_to_poorroad"]
                if self.smell_finished:
                    if smell_to_poorroad_state["started_at"] is None:
                        self._start_delay_timer("smell_to_poorroad", sim_time)
                    self._update_delay_timer("smell_to_poorroad", sim_time)

                if self.smell_finished and smell_to_poorroad_state["finished"] and not self.poorroad_started:
                    if not self._trigger_poorroad:
                        self._skip_poorroad_trigger(sim_time)
                    else:
                        self.start_poorroad(hero_location)

                poorroad_to_drivertrash_state = self._delay_states["poorroad_to_drivertrash"]
                if self.poorroad_finished:
                    if poorroad_to_drivertrash_state["started_at"] is None:
                        self._start_delay_timer("poorroad_to_drivertrash", sim_time)
                    self._update_delay_timer("poorroad_to_drivertrash", sim_time)

                if self.poorroad_finished and poorroad_to_drivertrash_state["finished"] and not self.drivertrash_finished:
                    if not self._trigger_drivertrash:
                        self._skip_drivertrash_trigger(sim_time)
                    else:
                        self.start_drivertrash()

                drivertrash_to_end_state = self._delay_states["drivertrash_to_end"]
                if self.drivertrash_active and not self.drivertrash_finished:
                    # try to find a drivertrash config matching hero location/direction and launch manual control
                    config = None
                    try:
                        from events_scenario02_static_props import DRIVERTRASH_SPAWN_CONFIGS as DRIVERTRASH_CONFIGS
                    except Exception:
                        from scenario_events.events_scenario02_static_props import DRIVERTRASH_SPAWN_CONFIGS as DRIVERTRASH_CONFIGS
                    # prefer matching config based on hero location/direction
                    hero_vel = ego.get_velocity() if ego is not None else None
                    if DRIVERTRASH_CONFIGS:
                        config = self._get_drivertrash_config(hero_location, hero_vel) if hero_location is not None else (DRIVERTRASH_CONFIGS[0] if len(DRIVERTRASH_CONFIGS) == 1 else None)

                    if config:
                        if self._start_drivertrash_manual_control_from_config(config):
                            self.drivertrash_finished = True
                            self.drivertrash_active = False

                if self.drivertrash_finished:
                    if drivertrash_to_end_state["started_at"] is None:
                        self._start_delay_timer("drivertrash_to_end", sim_time)
                    self._update_delay_timer("drivertrash_to_end", sim_time)

                if self.drivertrash_finished and drivertrash_to_end_state["finished"]:
                    self._scenario_done = True

                if self._scenario_done:
                    return

                time.sleep(SIM_STEP_S)
        except KeyboardInterrupt:
            pass
        finally:
            self.destroy()
            self._signal_done()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=2000, type=int)
    parser.add_argument("--tm-port", default=8000, type=int)
    parser.add_argument("--done-file", default=None)
    args = parser.parse_args()

    Scenario02Runner(
        args.host,
        args.port,
        args.tm_port,
        args.done_file,
        trigger_traffic=TRIGGER_TRAFFIC,
        trigger_trash=TRIGGER_TRASH,
        trigger_poorroad=TRIGGER_POORROAD,
        trigger_smell=TRIGGER_SMELL,
        trigger_drivertrash=TRIGGER_DRIVERTRASH,
        trigger_snake=TRIGGER_SNAKE,
    ).run()
