#!/usr/bin/env python

import logging
import random
from typing import List, Optional, Tuple
import carla

TRAFFIC_SPAWN_DELAY_SECONDS = 10.0
VEHICLE_ACTIVE_SECONDS = 30.0

# Keep the hero's traffic light green for a bit once we force it.
HERO_GREEN_LIGHT_HOLD_SECONDS = 10.0
# Only override lights that are plausibly the one ahead of the hero.
HERO_GREEN_LIGHT_MAX_DISTANCE = 25.0

SPAWN_CARS = 15
SPAWN_BIKES = 5

# Optional second pedestrian mode: one walker per route pair, walking back and forth.
ENABLE_ROUTE_PEDESTRIANS = False
CUSTOM_PEDESTRIAN_ROUTE_PAIRS = [
	((216.3, 4.9, 0.1), (306.7, 4.9, 0.1)),
	#((125.2, 5.6, 0.1), (150.1, 40.7, 0.1)),
	#((163.2, 11.9, 0.1), (180.1, 50.7, 0.1)),
]

BLOCKED_VEHICLE_KEYWORDS = (
	"firetruck",
	"ambulance",
	"bus",
	"fusorosa",                 # big mitsubishi bus
	"carlacola",
	"truck",
	"european_hgv",             # big truck with trailer
	"t2",
)

# Keep spawns far enough so that it is not visible for hero
MIN_SPAWN_DISTANCE = 90.0
MAX_SPAWN_DISTANCE = 260.0
# Prefer spawns closer to the hero so a small amount of traffic is still noticeable.
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
        "scale": (1.5, 1.5, 2.0),       # geht nicht
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


def get_actor_blueprints(world: carla.World, filter_pattern: str, generation: str):
	bps = world.get_blueprint_library().filter(filter_pattern)

	if generation.lower() == "all":
		return bps

	if len(bps) == 1:
		return bps

	try:
		int_generation = int(generation)
	except Exception:
		logging.warning("[Scenario00] Invalid actor generation %s for filter %s", generation, filter_pattern)
		return []

	if int_generation in [1, 2, 3]:
		return [bp for bp in bps if int(bp.get_attribute("generation")) == int_generation]

	logging.warning("[Scenario00] Invalid actor generation %s for filter %s", generation, filter_pattern)
	return []


def filter_blocked_vehicle_blueprints(blueprints, blocked_keywords):
	if not blueprints:
		return []
	if not blocked_keywords:
		return list(blueprints)
	return [
		bp for bp in blueprints
		if not any(keyword in bp.id.lower() for keyword in blocked_keywords)
	]


def create(client: carla.Client, world: carla.World, args=None):
	return ScenarioEvents(client=client, world=world, args=args)


class ScenarioEvents:
	def __init__(self, client: carla.Client, world: carla.World, args=None):
		self.client = client
		self.world = world
		self.args = args
		self._start_sim_time: Optional[float] = None
		self._traffic_spawned = False
		self._traffic_spawn_time: Optional[float] = None
		self._vehicles_cleared = False
		self._route_pedestrians_spawned = False
		self._route_pedestrians_spawn_time: Optional[float] = None
		self._last_forced_light_id: Optional[int] = None
		self._last_forced_light_time: Optional[float] = None

		self._static_actor_ids: List[int] = []
		self._vehicle_actor_ids: List[int] = []
		self._walker_actor_ids: List[int] = []
		self._walker_controller_ids: List[int] = []
		self._route_pedestrian_routes: List[dict] = []

		self._tm_port = int(getattr(args, "tm_port", 8000))
		self._rng = random.Random()

		self._spawn_static_prop_once()

	def tick(self, ego_vehicle: Optional[carla.Actor], ego_transform: Optional[carla.Transform], sim_time: float) -> bool:
		if self._start_sim_time is None:
			self._start_sim_time = float(sim_time)

		elapsed = float(sim_time) - self._start_sim_time
		if (not self._traffic_spawned) and elapsed >= TRAFFIC_SPAWN_DELAY_SECONDS:
			self._spawn_dynamic_traffic_offscreen(ego_transform)
			self._traffic_spawned = True
			self._traffic_spawn_time = float(sim_time)

		if self._traffic_spawned and (not self._vehicles_cleared) and self._traffic_spawn_time is not None:
			if (float(sim_time) - self._traffic_spawn_time) >= VEHICLE_ACTIVE_SECONDS:
				self._clear_spawned_vehicles()
				self._vehicles_cleared = True
				if ENABLE_ROUTE_PEDESTRIANS and CUSTOM_PEDESTRIAN_ROUTE_PAIRS and not self._route_pedestrians_spawned:
					logging.info("[Scenario00] Spawning custom route pedestrians after vehicle cleanup.")
					self._spawn_route_pedestrians(CUSTOM_PEDESTRIAN_ROUTE_PAIRS)
					self._route_pedestrians_spawned = True
					self._route_pedestrians_spawn_time = float(sim_time)

		if self._route_pedestrians_spawned and self._route_pedestrians_spawn_time is not None:
			if float(sim_time) > self._route_pedestrians_spawn_time:
				self._update_route_pedestrians()

		self._force_hero_green_light(ego_vehicle, sim_time)

		# Scenario-end logic can be added here (e.g. stop sign trigger).
		return False

	def destroy(self):
		self._stop_walker_controllers()
		ids = self._vehicle_actor_ids + self._walker_controller_ids + self._walker_actor_ids + self._static_actor_ids
		if ids:
			self.client.apply_batch([carla.command.DestroyActor(actor_id) for actor_id in ids])
		self._vehicle_actor_ids.clear()
		self._walker_actor_ids.clear()
		self._walker_controller_ids.clear()
		self._static_actor_ids.clear()
		self._route_pedestrian_routes.clear()
		self._traffic_spawn_time = None
		self._vehicles_cleared = False
		self._route_pedestrians_spawn_time = None

	def _spawn_static_prop_once(self):
		for prop_config in STATIC_PROP_SPAWNS:
			self._spawn_static_prop(prop_config)

	def _spawn_static_prop(self, prop_config):
		bp_lib = self.world.get_blueprint_library()
		prop_bp = None

		# First try the exact candidates we know about.
		for bp_id in prop_config.get("blueprints", []):
			try:
				prop_bp = bp_lib.find(bp_id)
				break
			except Exception:
				continue

		# Then do a broader scan over all static props and pick the mailbox blueprint.
		if prop_bp is None:
			try:
				all_props = bp_lib.filter('static.*')
				for bp in all_props:
					bp_id = bp.id.lower()
					if prop_config.get("name", "").lower() in bp_id:
						prop_bp = bp
						logging.info("[Scenario00] Found %s blueprint: %s", prop_config.get("name", "prop"), bp.id)
						break
			except Exception:
				prop_bp = None

		if prop_bp is None:
			logging.warning(
				"[Scenario00] Could not find %s blueprint. Checked exact candidates plus static.* scan.",
				prop_config.get("name", "prop"),
			)
			return

		scale = prop_config.get("scale")
		if scale is not None and prop_bp.has_attribute("scale"):
			try:
				prop_bp.set_attribute("scale", f"{scale[0]},{scale[1]},{scale[2]}")
			except Exception:
				logging.warning("[Scenario00] %s blueprint does not accept scale=%s", prop_bp.id, scale)

		actor = self.world.try_spawn_actor(prop_bp, prop_config["transform"])
		if actor is None:
			logging.warning("[Scenario00] Failed to spawn static prop %s at configured transform.", prop_config.get("name", "prop"))
			return

		self._static_actor_ids.append(actor.id)
		logging.info("[Scenario00] Static prop spawned: name=%s blueprint=%s actor_id=%s", prop_config.get("name", "prop"), prop_bp.id, actor.id)

	def _spawn_dynamic_traffic_offscreen(self, ego_transform: Optional[carla.Transform]):
		try:
			traffic_manager = self.client.get_trafficmanager(self._tm_port)
			traffic_manager.set_synchronous_mode(self.world.get_settings().synchronous_mode)
			traffic_manager.global_percentage_speed_difference(25.0)
			traffic_manager.set_global_distance_to_leading_vehicle(2.5)
		except Exception as exc:
			logging.warning("[Scenario00] Could not configure Traffic Manager on port %s: %s", self._tm_port, exc)
			traffic_manager = self.client.get_trafficmanager()

		spawn_points = list(self.world.get_map().get_spawn_points())
		self._rng.shuffle(spawn_points)
		all_vehicle_bps = get_actor_blueprints(self.world, "vehicle.*", "All")
		vehicle_bps = filter_blocked_vehicle_blueprints(all_vehicle_bps, BLOCKED_VEHICLE_KEYWORDS)
		if not vehicle_bps:
			logging.warning("[Scenario00] Vehicle spawn skipped: blacklist removed all vehicle blueprints.")
			return
		logging.info(
			"[Scenario00] Vehicle blueprint filter active: allowed=%d blocked=%d",
			len(vehicle_bps),
			max(0, len(all_vehicle_bps) - len(vehicle_bps)),
		)

		bike_keywords = ("bike", "bicycle", "crossbike", "omafiets", "century")
		bike_bps = [bp for bp in vehicle_bps if any(k in bp.id.lower() for k in bike_keywords)]
		car_bps = [bp for bp in vehicle_bps if bp not in bike_bps]

		car_points = self._pick_hidden_spawn_points(spawn_points, ego_transform, SPAWN_CARS)
		used = set(id(p) for p in car_points)
		bike_candidates = [p for p in spawn_points if id(p) not in used]
		bike_points = self._pick_hidden_spawn_points(bike_candidates, ego_transform, SPAWN_BIKES)

		self._spawn_vehicles(car_points, car_bps, traffic_manager)
		self._spawn_vehicles(bike_points, bike_bps if bike_bps else car_bps, traffic_manager)

		logging.info(
			"[Scenario00] Dynamic traffic spawned: cars=%d bikes=%d",
			len(car_points),
			len(bike_points),
		)

	def _clear_spawned_vehicles(self):
		if not self._vehicle_actor_ids:
			return

		actor_ids = list(self._vehicle_actor_ids)
		self.client.apply_batch([carla.command.DestroyActor(actor_id) for actor_id in actor_ids])
		self._vehicle_actor_ids.clear()
		logging.info("[Scenario00] Cleared spawned vehicles after active phase.")

	def _force_hero_green_light(self, ego_vehicle: Optional[carla.Actor], sim_time: float):
		if ego_vehicle is None:
			return

		try:
			if not ego_vehicle.is_at_traffic_light():
				return

			traffic_light = ego_vehicle.get_traffic_light()
			if traffic_light is None:
				return

			try:
				light_location = traffic_light.get_location()
				ego_location = ego_vehicle.get_location()
				dx = light_location.x - ego_location.x
				dy = light_location.y - ego_location.y
				dz = light_location.z - ego_location.z
				distance = (dx * dx + dy * dy + dz * dz) ** 0.5
				if distance > HERO_GREEN_LIGHT_MAX_DISTANCE:
					return
			except Exception:
				pass

			if traffic_light.get_state() == carla.TrafficLightState.Green:
				return

			light_id = int(traffic_light.id)
			if self._last_forced_light_id != light_id or self._last_forced_light_time is None or (sim_time - self._last_forced_light_time) >= 1.0:
				logging.info("[Scenario00] Hero traffic light forced to green (light_id=%s)", light_id)

			traffic_light.set_state(carla.TrafficLightState.Green)
			try:
				traffic_light.set_green_time(HERO_GREEN_LIGHT_HOLD_SECONDS)
			except Exception:
				pass

			self._last_forced_light_id = light_id
			self._last_forced_light_time = sim_time
		except Exception as exc:
			logging.warning("[Scenario00] Could not force hero traffic light to green: %s", exc)

	def _spawn_vehicles(self, points: List[carla.Transform], blueprints, traffic_manager):
		if not points or not blueprints:
			return

		synchronous_master = False

		batch = []
		for transform in points:
			bp = self._rng.choice(blueprints)
			if bp.has_attribute("color"):
				bp.set_attribute("color", self._rng.choice(bp.get_attribute("color").recommended_values))
			if bp.has_attribute("driver_id"):
				bp.set_attribute("driver_id", self._rng.choice(bp.get_attribute("driver_id").recommended_values))
			bp.set_attribute("role_name", "autopilot")

			batch.append(
				carla.command.SpawnActor(bp, transform).then(
					carla.command.SetAutopilot(carla.command.FutureActor, True, traffic_manager.get_port())
				)
			)

		for response in self.client.apply_batch_sync(batch, synchronous_master):
			if response.error:
				logging.warning("[Scenario00] Vehicle spawn failed: %s", response.error)
				continue
			self._vehicle_actor_ids.append(response.actor_id)

	def _spawn_route_pedestrians(self, route_pairs):
		walker_bps = get_actor_blueprints(self.world, "walker.pedestrian.*", "2")
		if not walker_bps:
			logging.warning("[Scenario00] Skipping route pedestrians: walker blueprints unavailable.")
			return

		self._route_pedestrian_routes.clear()
		batch = []
		route_specs = []

		for pair_index, pair in enumerate(route_pairs):
			start_location, end_location = self._normalize_route_pair(pair)
			if start_location is None or end_location is None:
				logging.warning("[Scenario00] Invalid route pair at index %d: %s", pair_index, pair)
				continue

			start_location = self._project_location_to_navigation(carla.Location(x=start_location[0], y=start_location[1], z=start_location[2]))
			end_location = self._project_location_to_navigation(carla.Location(x=end_location[0], y=end_location[1], z=end_location[2]))

			spawn_point = carla.Transform(start_location)
			blueprint = self._rng.choice(walker_bps)
			if blueprint.has_attribute("is_invincible"):
				blueprint.set_attribute("is_invincible", "false")
			speed = 1.2
			if blueprint.has_attribute("speed"):
				speed_values = blueprint.get_attribute("speed").recommended_values
				if len(speed_values) > 1:
					speed = float(speed_values[1])

			batch.append(carla.command.SpawnActor(blueprint, spawn_point))
			route_specs.append((tuple(start_location), tuple(end_location), speed))

		if not batch:
			logging.warning("[Scenario00] No valid custom pedestrian routes configured.")
			return

		spawn_results = self.client.apply_batch_sync(batch, False)
		spawned_walker_ids = []
		filtered_route_specs = []
		for i, result in enumerate(spawn_results):
			if result.error:
				logging.warning("[Scenario00] Route walker spawn failed: %s", result.error)
				continue
			spawned_walker_ids.append(result.actor_id)
			filtered_route_specs.append(route_specs[i])

		if not spawned_walker_ids:
			return

		controller_bp = self.world.get_blueprint_library().find("controller.ai.walker")
		controller_batch = [
			carla.command.SpawnActor(controller_bp, carla.Transform(), actor_id)
			for actor_id in spawned_walker_ids
		]
		controller_results = self.client.apply_batch_sync(controller_batch, False)

		valid_routes = []
		for i, result in enumerate(controller_results):
			if result.error:
				logging.warning("[Scenario00] Route walker controller spawn failed: %s", result.error)
				continue
			valid_routes.append((result.actor_id, spawned_walker_ids[i], filtered_route_specs[i]))

		if not valid_routes:
			self.client.apply_batch([carla.command.DestroyActor(actor_id) for actor_id in spawned_walker_ids])
			return

		controller_ids = [controller_id for controller_id, _, _ in valid_routes]
		walker_ids = [walker_id for _, walker_id, _ in valid_routes]
		controllers = self.world.get_actors(controller_ids)

		self.world.set_pedestrians_cross_factor(0.0)
		for i, controller in enumerate(controllers):
			try:
				route_spec = valid_routes[i][2]
				start_location, end_location, speed = route_spec
				self._route_pedestrian_routes.append(
					{
						"controller": controller,
						"walker_id": walker_ids[i],
						"points": (
							carla.Location(x=start_location[0], y=start_location[1], z=start_location[2]),
							carla.Location(x=end_location[0], y=end_location[1], z=end_location[2]),
						),
						"speed": float(speed),
						"started": False,
						"target_index": 1,
						"switch_distance": 1.75,
					}
				)
			except Exception as exc:
				logging.warning("[Scenario00] Route walker setup failed: %s", exc)

		self._walker_controller_ids.extend(controller_ids)
		self._walker_actor_ids.extend(walker_ids)
		logging.info("[Scenario00] Custom route pedestrians spawned: %d", len(valid_routes))

	def _update_route_pedestrians(self):
		if not self._route_pedestrian_routes:
			return

		for route in self._route_pedestrian_routes:
			try:
				walker = self.world.get_actor(route["walker_id"])
				controller = route["controller"]
				if walker is None or controller is None:
					continue

				points = route["points"]
				if not route.get("started", False):
					controller.start()
					controller.go_to_location(points[1])
					controller.set_max_speed(float(route.get("speed", 1.2)))
					route["started"] = True
					continue

				target_index = int(route.get("target_index", 1))
				target_location = points[target_index]
				current_location = walker.get_location()
				dx = current_location.x - target_location.x
				dy = current_location.y - target_location.y
				dz = current_location.z - target_location.z
				distance = (dx * dx + dy * dy + dz * dz) ** 0.5
				if distance <= float(route.get("switch_distance", 1.75)):
					new_target_index = 0 if target_index == 1 else 1
					route["target_index"] = new_target_index
					new_target = points[new_target_index]
					controller.go_to_location(new_target)
			except Exception:
				continue

	def _normalize_route_pair(self, pair):
		if isinstance(pair, dict):
			start = pair.get("start")
			end = pair.get("end")
		else:
			if not isinstance(pair, (list, tuple)) or len(pair) != 2:
				return None, None
			start, end = pair

		start_location = self._normalize_location_tuple(start)
		end_location = self._normalize_location_tuple(end)
		return start_location, end_location

	def _normalize_location_tuple(self, value):
		if isinstance(value, carla.Location):
			return (float(value.x), float(value.y), float(value.z))
		if not isinstance(value, (list, tuple)) or len(value) != 3:
			return None
		return (float(value[0]), float(value[1]), float(value[2]))

	def _project_location_to_navigation(self, location: carla.Location) -> carla.Location:
		waypoint = self.world.get_map().get_waypoint(
			location,
			project_to_road=True,
			lane_type=carla.LaneType.Any,
		)
		nav_location = waypoint.transform.location
		return carla.Location(x=nav_location.x, y=nav_location.y, z=location.z)

	def _pick_hidden_spawn_points(
		self,
		spawn_points: List[carla.Transform],
		ego_transform: Optional[carla.Transform],
		target_count: int,
	) -> List[carla.Transform]:
		if target_count <= 0:
			return []

		nearby_candidates: List[Tuple[float, carla.Transform]] = []
		fallback_candidates: List[Tuple[float, carla.Transform]] = []
		for transform in spawn_points:
			if not self._is_transform_hidden_from_ego(transform, ego_transform):
				continue

			distance = self._distance_to_ego(transform, ego_transform)
			candidate = (distance, transform)
			fallback_candidates.append(candidate)
			if distance <= PREFERRED_SPAWN_DISTANCE:
				nearby_candidates.append(candidate)

		selected = nearby_candidates if len(nearby_candidates) >= target_count else fallback_candidates
		selected.sort(key=lambda item: item[0])
		return [transform for _, transform in selected[:target_count]]

	def _is_transform_hidden_from_ego(self, transform: carla.Transform, ego_transform: Optional[carla.Transform]) -> bool:
		if ego_transform is None:
			return True

		distance, dx, dy, dz = self._distance_components(transform, ego_transform)

		if distance < MIN_SPAWN_DISTANCE or distance > MAX_SPAWN_DISTANCE:
			return False

		# Avoid spawn in the forward view and also behind the ego, where the rear mirror could reveal it.
		fwd = ego_transform.get_forward_vector()
		dot = (dx * fwd.x + dy * fwd.y + dz * fwd.z)
		cos_angle = dot / max(distance, 0.001)
		if abs(cos_angle) > 0.35 and distance < 150.0:
			return False

		return True

	def _distance_to_ego(self, transform: carla.Transform, ego_transform: Optional[carla.Transform]) -> float:
		if ego_transform is None:
			return float("inf")

		distance, _, _, _ = self._distance_components(transform, ego_transform)
		return distance

	def _distance_components(
		self,
		transform: carla.Transform,
		ego_transform: carla.Transform,
	) -> Tuple[float, float, float, float]:
		ego_loc = ego_transform.location
		candidate_loc = transform.location
		dx = candidate_loc.x - ego_loc.x
		dy = candidate_loc.y - ego_loc.y
		dz = candidate_loc.z - ego_loc.z
		distance = (dx * dx + dy * dy + dz * dz) ** 0.5
		return distance, dx, dy, dz

	def _stop_walker_controllers(self):
		if not self._walker_controller_ids:
			return
		controllers = self.world.get_actors(self._walker_controller_ids)
		for controller in controllers:
			try:
				controller.stop()
			except Exception:
				pass


if __name__ == '__main__':
	print('[Scenario00] Modul ist bereit. Direktstart fuehrt keine Simulation aus; bitte ueber manual_control oder session_runner starten.')
