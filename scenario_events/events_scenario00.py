#!/usr/bin/env python

import logging
import random
import time
import sys
import argparse
from typing import List, Optional, Tuple
import carla

# Constants
TRAFFIC_SPAWN_DELAY_SECONDS = 5.0
VEHICLE_ACTIVE_SECONDS = 0.0                    # if > 0 => vehicles will be removed; if = 0 => stay infinitely
PEDESTRIAN_AFTER_VEHICLES_SECONDS = 2.0
PEDESTRIAN_SPAWN_DELAY_SECONDS = TRAFFIC_SPAWN_DELAY_SECONDS + max(VEHICLE_ACTIVE_SECONDS, 0.0) + PEDESTRIAN_AFTER_VEHICLES_SECONDS
HERO_GREEN_LIGHT_HOLD_SECONDS = 10.0
HERO_GREEN_LIGHT_MAX_DISTANCE = 25.0
SPAWN_CARS = 15
SPAWN_BIKES = 5
ENABLE_ROUTE_PEDESTRIANS = True
PEDESTRIAN_BLUEPRINT_ID = "walker.pedestrian.0046"
PEDESTRIAN_SPAWN_LOCATION = carla.Location(x=216.3, y=4.9, z=1.85)
PEDESTRIAN_TARGET_LOCATION = carla.Location(x=306.7, y=4.9, z=0.35)
PEDESTRIAN_MAX_SPEED = 1.4
PEDESTRIAN_WAIT_TIMEOUT_S = 180.0
PEDESTRIAN_STEP_S = 0.05
PEDESTRIAN_ARRIVE_THRESH = 1.0
SIM_STEP_S = 0.05

BLOCKED_VEHICLE_KEYWORDS = (
    "firetruck", "ambulance", "bus", "fusorosa", "carlacola", "truck", "european_hgv", "t2",
)

MIN_SPAWN_DISTANCE = 90.0
MAX_SPAWN_DISTANCE = 260.0
PREFERRED_SPAWN_DISTANCE = 140.0

STATIC_PROP_SPAWNS = [
    {
        "name": "mailbox",
        "blueprints": ["static.prop.mailbox"],
        "transform": carla.Transform(
            carla.Location(x=249.20, y=127.00, z=0.10),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "FireHydrantCustom",
        "blueprints": [
            "/Game/Carla/Static/Static/SM_FireHdrant.SM_FireHdrant",
            "static.prop.SM_FireHdrant",
            "static.prop.SM_Fire_Hdrant",
            "static.prop.SM_Fire_Hydrant",
        ],
        "transform": carla.Transform(
            carla.Location(x=251.20, y=127.00, z=0.10),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "TreePine2Custom_1",
        "blueprints": ["static.prop.treepine2custom"],
        "transform": carla.Transform(
            carla.Location(x=426.10, y=11.20, z=10.60),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": (1.5, 1.5, 2.0),
    },
    {
        "name": "TreePine2Custom_2",
        "blueprints": ["static.prop.treepine2custom"],
        "transform": carla.Transform(
            carla.Location(x=457.70, y=488.60, z=-3.50),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": (4.0, 4.0, 20.0),
    },
]

def get_actor_blueprints(world, filter_pattern):
    bps = list(world.get_blueprint_library().filter(filter_pattern))
    if not bps:
        print(f"[Scenario00] WARNUNG: Keine Blueprints für {filter_pattern} gefunden!")
    return bps

def filter_blocked_vehicle_blueprints(blueprints, blocked_keywords):
    return [bp for bp in blueprints if not any(k in bp.id.lower() for k in blocked_keywords)]

class Scenario00Runner:
    def __init__(self, host, port, tm_port):
        self.client = carla.Client(host, port)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()
        self._tm_port = tm_port
        self._rng = random.Random()
        
        self._start_sim_time = None
        self._traffic_spawned = False
        self._traffic_spawn_time = None
        self._vehicles_cleared = False
        self._pedestrian_spawned = False
        self._pedestrian_started = False
        self._pedestrian_done = False
        self._pedestrian_spawn_time = None
        self._pedestrian_walker_id = None
        self._pedestrian_controller_id = None
        
        self._static_actor_ids = []
        self._vehicle_actor_ids = []
        self._walker_actor_ids = []
        self._walker_controller_ids = []
        self._last_forced_light_id = None
        self._last_forced_light_time = None

    def _ensure_synchronous_mode(self):
        settings = self.world.get_settings()
        if not settings.synchronous_mode or settings.fixed_delta_seconds != 0.05:
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = 0.05
            self.world.apply_settings(settings)

        try:
            tm = self.client.get_trafficmanager(self._tm_port)
        except Exception:
            tm = self.client.get_trafficmanager()
        tm.set_synchronous_mode(True)

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
        try:
            tm = self.client.get_trafficmanager(self._tm_port)
            tm.set_synchronous_mode(self.world.get_settings().synchronous_mode)
        except:
            tm = self.client.get_trafficmanager()
            
        spawn_points = list(self.world.get_map().get_spawn_points())
        self._rng.shuffle(spawn_points)
        all_bps = get_actor_blueprints(self.world, "vehicle.*")
        vehicle_bps = filter_blocked_vehicle_blueprints(all_bps, BLOCKED_VEHICLE_KEYWORDS)
        
        car_points = self._pick_hidden_points(spawn_points, ego_transform, SPAWN_CARS)
        print(
            f"[Scenario00] Spawning vehicles at sim_time={sim_time:.2f}s: "
            #f"requested={len(car_points)}, blueprint_count={len(vehicle_bps)}"
        )
        self._spawn_batch_vehicles(car_points, vehicle_bps, tm)

    def _pick_hidden_points(self, points, ego_transform, count):
        if not ego_transform: return points[:count]
        hidden = []
        for p in points:
            dist = p.location.distance(ego_transform.location)
            if MIN_SPAWN_DISTANCE < dist < MAX_SPAWN_DISTANCE:
                hidden.append(p)
        return hidden[:count]

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
            f"[Scenario00] Vehicles spawned: {len(spawned_ids)}/{len(points)}"
        )

    def _force_green_light(self, ego, sim_time):
        if ego and ego.is_at_traffic_light():
            tl = ego.get_traffic_light()
            if tl:
                tl.set_state(carla.TrafficLightState.Green)
                tl.set_green_time(HERO_GREEN_LIGHT_HOLD_SECONDS)

    def _spawn_single_pedestrian(self):
        walker_bp = self.world.get_blueprint_library().find(PEDESTRIAN_BLUEPRINT_ID)
        if walker_bp.has_attribute("is_invincible"):
            walker_bp.set_attribute("is_invincible", "false")

        print(f"[Scenario00] Spawne Pedestrian bei {PEDESTRIAN_SPAWN_LOCATION}...")
        walker = self.world.spawn_actor(walker_bp, carla.Transform(PEDESTRIAN_SPAWN_LOCATION))
        controller = self.world.spawn_actor(
            self.world.get_blueprint_library().find("controller.ai.walker"),
            carla.Transform(),
            walker,
        )

        self._walker_actor_ids.append(walker.id)
        self._walker_controller_ids.append(controller.id)

        self._pedestrian_spawn_time = self.world.get_snapshot().timestamp.elapsed_seconds
        self._pedestrian_walker_id = walker.id
        self._pedestrian_controller_id = controller.id
        self._pedestrian_spawned = True
        self._pedestrian_started = False
        self._pedestrian_done = False

    def _start_single_pedestrian(self):
        walker = self.world.get_actor(self._pedestrian_walker_id)
        controller = self.world.get_actor(self._pedestrian_controller_id)
        if walker is None or controller is None:
            self._pedestrian_done = True
            return

        controller.start()
        controller.go_to_location(PEDESTRIAN_TARGET_LOCATION)
        controller.set_max_speed(PEDESTRIAN_MAX_SPEED)
        print(f"[Scenario00] Pedestrian {walker.id} ist jetzt unterwegs.")
        self._pedestrian_started = True

    def _update_single_pedestrian(self, sim_time):
        if self._pedestrian_done:
            return

        if not self._pedestrian_spawned:
            if sim_time >= PEDESTRIAN_SPAWN_DELAY_SECONDS:
                self._spawn_single_pedestrian()
            return

        if not self._pedestrian_started:
            self._start_single_pedestrian()
            return

        walker = self.world.get_actor(self._pedestrian_walker_id)
        if walker is None:
            self._pedestrian_done = True
            return

        loc = walker.get_location()
        distance = ((loc.x - PEDESTRIAN_TARGET_LOCATION.x) ** 2 + (loc.y - PEDESTRIAN_TARGET_LOCATION.y) ** 2 + (loc.z - PEDESTRIAN_TARGET_LOCATION.z) ** 2) ** 0.5
        if distance <= PEDESTRIAN_ARRIVE_THRESH:
            print("[Scenario00] Pedestrian angekommen.")
            self._pedestrian_done = True
            return

        if self._pedestrian_spawn_time is not None and (sim_time - self._pedestrian_spawn_time) > PEDESTRIAN_WAIT_TIMEOUT_S:
            print("[Scenario00] Pedestrian Timeout.")
            self._pedestrian_done = True

    def _destroy_pedestrian(self):
        controller = self.world.get_actor(self._pedestrian_controller_id) if self._pedestrian_controller_id is not None else None
        walker = self.world.get_actor(self._pedestrian_walker_id) if self._pedestrian_walker_id is not None else None
        if controller is not None:
            try:
                controller.stop()
            except Exception:
                pass
        if walker is not None:
            walker.destroy()
        if controller is not None:
            controller.destroy()

    def run(self):
        print("[Scenario00] Running...")
        self._ensure_synchronous_mode()
        self._spawn_static_prop_once()
        try:
            while True:
                self.world.tick()
                snapshot = self.world.get_snapshot()
                sim_time = snapshot.timestamp.elapsed_seconds
                if self._start_sim_time is None: self._start_sim_time = sim_time
                
                ego = self.find_hero()
                # Falls kein Hero gefunden wurde, nehmen wir die Standard-Koordinaten an
                ego_transform = ego.get_transform() if ego else carla.Transform(carla.Location(x=158.080, y=27.180, z=0.30))
                
                elapsed = sim_time - self._start_sim_time
                if not self._traffic_spawned and elapsed >= TRAFFIC_SPAWN_DELAY_SECONDS:
                    self._spawn_dynamic_traffic(ego_transform, sim_time)
                    self._traffic_spawned = True
                    self._traffic_spawn_time = sim_time
                
                if self._traffic_spawned and not self._vehicles_cleared:
                    if VEHICLE_ACTIVE_SECONDS > 0 and (sim_time - self._traffic_spawn_time) >= VEHICLE_ACTIVE_SECONDS:
                        destroyed_count = len(self._vehicle_actor_ids)
                        print(
                            f"[Scenario00] Destroying vehicles at sim_time={sim_time:.2f}s after "
                            f"{sim_time - self._traffic_spawn_time:.2f}s active time: count={destroyed_count}"
                        )
                        self.client.apply_batch([carla.command.DestroyActor(x) for x in self._vehicle_actor_ids])
                        self._vehicle_actor_ids = []
                        self._vehicles_cleared = True
                    elif VEHICLE_ACTIVE_SECONDS <= 0 and self._traffic_spawned and not self._vehicles_cleared:
                        print(
                            f"[Scenario00] Vehicle lifetime is infinite (VEHICLE_ACTIVE_SECONDS={VEHICLE_ACTIVE_SECONDS}); "
                            f"keeping {len(self._vehicle_actor_ids)} vehicles active."
                        )
                        self._vehicles_cleared = True

                if ENABLE_ROUTE_PEDESTRIANS:
                    self._update_single_pedestrian(sim_time)
                    if self._pedestrian_done:
                        self._destroy_pedestrian()
                        return
                
                if ego:
                    self._force_green_light(ego, sim_time)
                time.sleep(SIM_STEP_S)
        except KeyboardInterrupt:
            pass
        finally:
            self.destroy()

    def destroy(self):
        print("[Scenario00] Cleanup...")
        all_ids = self._static_actor_ids + self._vehicle_actor_ids + self._walker_actor_ids + self._walker_controller_ids
        self.client.apply_batch([carla.command.DestroyActor(x) for x in all_ids])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', default=2000, type=int)
    parser.add_argument('--tm-port', default=8000, type=int)
    args = parser.parse_args()
    Scenario00Runner(args.host, args.port, args.tm_port).run()
