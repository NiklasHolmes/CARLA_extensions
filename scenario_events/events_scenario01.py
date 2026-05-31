#!/usr/bin/env python

import argparse
import math
import os
import random
import time

import carla

try:
	from events_scenario01_static_props import get_static_prop_spawns
except ModuleNotFoundError:
	from scenario_events.events_scenario01_static_props import get_static_prop_spawns


def get_actor_blueprints(world, filter_pattern):
	bps = list(world.get_blueprint_library().filter(filter_pattern))
	if not bps:
		print(f"[Scenario01] WARNUNG: Keine Blueprints für {filter_pattern} gefunden!")
	return bps


def filter_blocked_vehicle_blueprints(blueprints, blocked_keywords):
	result = []
	for bp in blueprints:
		tid = bp.id.lower() if hasattr(bp, "id") else ""
		if any(k in tid for k in blocked_keywords):
			continue

		result.append(bp)
	return result


START_TO_REDLIGHT_DELAY = 1.0
REDLIGHT_TO_TRAFFICJAM_DELAY = 1.0
TRAFFICJAM_TO_BADGUY_DELAY = 50.0
BADGUY_TO_SONG_DELAY = 100.0
SONG_TO_CROSSPED_DELAY = 1.0
CROSSPED_TO_OCCUPY_DELAY = 1.0
OCCUPY_TO_END_DELAY = 1.0
REDLIGHT_PHASE_MAX_SECONDS = 40.0
REDLIGHT_YELLOW_SECONDS = 2.0
HERO_GREEN_LIGHT_HOLD_SECONDS = 3.0
HERO_RED_LIGHT_HOLD_SECONDS = 8.0
REDLIGHT_MIN_RED_SECONDS = 8.0
REDLIGHT_MAX_RED_SECONDS = 12.0
REDLIGHT_GREEN_RELEASE_SECONDS = 8.0
REDLIGHT_MAX_TRAFFIC_LIGHTS = 4
TRAFFICJAM_PRUNE_DISTANCE_METERS = 150.0
TRAFFICJAM_TRAFFIC_LIGHT_RED_SECONDS = 15.0
TRAFFICJAM_TRAFFIC_LIGHT_GREEN_SECONDS = 10.0

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

SIM_STEP_S = 0.05
run_in_singleFile_mode = True

TRIGGER_REDLIGHT = False
TRIGGER_TRAFFICJAM = True
TRIGGER_BADGUY = True
TRIGGER_SONG = True
TRIGGER_CROSSPED = True
TRIGGER_OCCUPY = True
PRUNE_TJ_CARS = True
DEBUG_MODE = True

class Scenario01Runner:
	def __init__(self, host, port, tm_port, done_file=None, trigger_redlight=True, trigger_trafficjam=True, trigger_badguy=True, trigger_song=True, trigger_crossped=True, trigger_occupy=True):
		self.client = carla.Client(host, port)
		self.client.set_timeout(10.0)
		self.world = self.client.get_world()
		self._tm_port = tm_port
		self._done_file = done_file
		self._rng = random.Random()
		self._debug_trafficjam_box_lifetime = SIM_STEP_S * 2.0
		# control pruning of trafficjam vehicles via module-level boolean PRUNE_TJ_CARS
		self._prune_tj_cars = PRUNE_TJ_CARS

		self._trigger_redlight = trigger_redlight
		self._trigger_trafficjam = trigger_trafficjam
		self._trigger_badguy = trigger_badguy
		self._trigger_song = trigger_song
		self._trigger_crossped = trigger_crossped
		self._trigger_occupy = trigger_occupy

		self._start_sim_time = None
		self._scenario_done = False

		self.redlight_finished = False
		self.redlight_active = False
		self._redlight_started_at = None
		self._redlight_traffic_light_states = {}
		self._redlight_seen_traffic_light_ids = set()
		self._redlight_seen_traffic_light_count = 0
		self._trafficjam_spawned = False
		self._trafficjam_spawn_time = None
		self._trafficjam_traffic_light = None
		self._trafficjam_traffic_light_state = None
		self._trafficjam_traffic_light_started_at = None
		self.trafficjam_finished = False
		self.badguy_finished = False
		self.song_finished = False
		self.crossped_finished = False
		self.occupy_started = False
		self.occupy_finished = False
		self._vehicle_actor_ids = []

		self._delay_states = {
			"start_to_redlight": {
				"delay": START_TO_REDLIGHT_DELAY,
				"started_at": None,
				"finished": False,
			},
			"redlight_to_trafficjam": {
				"delay": REDLIGHT_TO_TRAFFICJAM_DELAY,
				"started_at": None,
				"finished": False,
			},
			"trafficjam_to_badguy": {
				"delay": TRAFFICJAM_TO_BADGUY_DELAY,
				"started_at": None,
				"finished": False,
			},
			"badguy_to_song": {
				"delay": BADGUY_TO_SONG_DELAY,
				"started_at": None,
				"finished": False,
			},
			"song_to_crossped": {
				"delay": SONG_TO_CROSSPED_DELAY,
				"started_at": None,
				"finished": False,
			},
			"crossped_to_occupy": {
				"delay": CROSSPED_TO_OCCUPY_DELAY,
				"started_at": None,
				"finished": False,
			},
			"occupy_to_end": {
				"delay": OCCUPY_TO_END_DELAY,
				"started_at": None,
				"finished": False,
			},
		}

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

	def _get_trafficjam_trigger_config(self, hero_location, hero_velocity=None):
		for trigger_config in get_static_prop_spawns("trafficjam"):
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

			return trigger_config
		return None

	def _draw_trafficjam_trigger_box(self):
		for trigger_config in get_static_prop_spawns("trafficjam"):
			center = trigger_config["trigger_location"]
			x_tol = float(trigger_config.get("trigger_x_tolerance", 0.0))
			y_tol = float(trigger_config.get("trigger_y_tolerance", 0.0))
			z_base = center.z
			z_top = z_base + 2.0
			color = carla.Color(r=255, g=0, b=0, a=255)
			thickness = 0.1
			life_time = self._debug_trafficjam_box_lifetime

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

	def _find_trafficjam_traffic_light(self, first_vehicle=None):
		if first_vehicle is None and self._vehicle_actor_ids:
			first_vehicle = self.world.get_actor(self._vehicle_actor_ids[0])
		if first_vehicle is None:
			return None, None

		vehicle_transform = first_vehicle.get_transform()
		vehicle_location = vehicle_transform.location
		vehicle_forward = vehicle_transform.get_forward_vector()
		best_traffic_light = None
		best_landmark = None
		best_distance = None

		for landmark in self.world.get_map().get_all_landmarks_of_type("1000001"):
			if landmark.id == "":
				continue

			traffic_light = self.world.get_traffic_light(landmark)
			if traffic_light is None:
				continue

			light_location = traffic_light.get_transform().location
			dx = light_location.x - vehicle_location.x
			dy = light_location.y - vehicle_location.y
			dz = light_location.z - vehicle_location.z
			if (vehicle_forward.x * dx) + (vehicle_forward.y * dy) + (vehicle_forward.z * dz) <= 0.0:
				continue

			distance = (dx * dx + dy * dy + dz * dz) ** 0.5
			if best_distance is None or distance < best_distance:
				best_traffic_light = traffic_light
				best_landmark = landmark
				best_distance = distance

		return best_traffic_light, best_landmark

	def _draw_trafficjam_traffic_light_box(self):
		if not DEBUG_MODE:
			return

		traffic_light = self._trafficjam_traffic_light
		if traffic_light is None:
			return

		try:
			self.world.debug.draw_box(
				traffic_light.bounding_box,
				traffic_light.get_transform(),
				thickness=0.1,
				color=carla.Color(r=255, g=255, b=0, a=255),
				life_time=self._debug_trafficjam_box_lifetime,
			)
		except Exception:
			pass

	def _start_trafficjam_traffic_light_control(self, sim_time):
		traffic_light, landmark = self._find_trafficjam_traffic_light()
		self._trafficjam_traffic_light = traffic_light
		self._trafficjam_traffic_light_state = None
		self._trafficjam_traffic_light_started_at = sim_time

		if traffic_light is None:
			print("[Scenario01] WARNUNG: TrafficJam-Ampel nicht gefunden.")
			return

		traffic_light_location = traffic_light.get_transform().location
		landmark_id = landmark.id if landmark is not None else "unknown"
		opendrive_id = traffic_light.get_opendrive_id() if hasattr(traffic_light, "get_opendrive_id") else "unknown"
		print(
			f"[Scenario01] TrafficJam traffic light selected | light_id={traffic_light.id} | "
			f"opendrive_id={opendrive_id} | landmark_id={landmark_id} | "
			f"pos=({traffic_light_location.x:.2f}, {traffic_light_location.y:.2f}, {traffic_light_location.z:.2f})"
		)

		try:
			if hasattr(traffic_light, "freeze"):
				traffic_light.freeze(True)
			traffic_light.set_state(carla.TrafficLightState.Red)
			if hasattr(traffic_light, "set_red_time"):
				traffic_light.set_red_time(TRAFFICJAM_TRAFFIC_LIGHT_RED_SECONDS)
			self._trafficjam_traffic_light_state = "red"
			print(
				f"[Scenario01] Ampel auf rot geschaltet | light_id={traffic_light.id} | "
				f"red_hold={TRAFFICJAM_TRAFFIC_LIGHT_RED_SECONDS:.1f}s"
			)
		except Exception:
			print(f"[Scenario01] WARNUNG: TrafficJam-Ampel konnte nicht auf Rot gesetzt werden | light_id={traffic_light.id}")

	def _update_trafficjam_traffic_light_control(self, sim_time):
		traffic_light = self._trafficjam_traffic_light
		if traffic_light is None or self._trafficjam_traffic_light_started_at is None:
			return

		elapsed = sim_time - self._trafficjam_traffic_light_started_at
		state = self._trafficjam_traffic_light_state

		if state == "red" and elapsed >= TRAFFICJAM_TRAFFIC_LIGHT_RED_SECONDS:
			try:
				traffic_light.set_state(carla.TrafficLightState.Green)
				if hasattr(traffic_light, "set_green_time"):
					traffic_light.set_green_time(TRAFFICJAM_TRAFFIC_LIGHT_GREEN_SECONDS)
				self._trafficjam_traffic_light_state = "green"
				self._trafficjam_traffic_light_started_at = sim_time
				print(
					f"[Scenario01] Ampel auf gruen geschaltet | light_id={traffic_light.id} | "
					f"elapsed={elapsed:.2f}s | green_hold={TRAFFICJAM_TRAFFIC_LIGHT_GREEN_SECONDS:.1f}s"
				)
			except Exception:
				print(f"[Scenario01] WARNUNG: TrafficJam-Ampel konnte nicht auf Gruen gesetzt werden | light_id={traffic_light.id}")
			return

		if state == "green" and elapsed >= TRAFFICJAM_TRAFFIC_LIGHT_GREEN_SECONDS:
			self._trafficjam_traffic_light_state = "released"
			self._trafficjam_traffic_light_started_at = None
			try:
				if hasattr(traffic_light, "freeze"):
					traffic_light.freeze(False)
			except Exception:
				pass
		print(f"[Scenario01] Ampel losgelassen | light_id={traffic_light.id} | elapsed={elapsed:.2f}s")

	def _project_transform_to_driving_lane(self, spawn_transform):
		waypoint = self.world.get_map().get_waypoint(
			spawn_transform.location,
			project_to_road=True,
			lane_type=carla.LaneType.Driving,
		)
		if waypoint is None:
			return spawn_transform

		projected_location = waypoint.transform.location
		projected_rotation = waypoint.transform.rotation
		return carla.Transform(
			carla.Location(x=projected_location.x, y=projected_location.y, z=spawn_transform.location.z),
			carla.Rotation(pitch=projected_rotation.pitch, yaw=projected_rotation.yaw, roll=projected_rotation.roll),
		)

	def _spawn_trafficjam_vehicle(self, spawn_config, sim_time):
		all_bps = get_actor_blueprints(self.world, "vehicle.*")
		vehicle_bps = filter_blocked_vehicle_blueprints(all_bps, BLOCKED_VEHICLE_KEYWORDS)
		if not vehicle_bps:
			return False

		spawn_transform = spawn_config.get("transform")
		if spawn_transform is None:
			return False

		spawn_transform = self._project_transform_to_driving_lane(spawn_transform)

		bp = self._rng.choice(vehicle_bps)
		tm = self._get_traffic_manager()
		actor = self.world.try_spawn_actor(bp, spawn_transform)
		if actor is None:
			print(
				f"[Scenario01] WARNUNG: TrafficJam-Fahrzeug konnte nicht gespawnt werden | sim_time={sim_time:.2f}s | "
				f"spawn=({spawn_transform.location.x:.2f}, {spawn_transform.location.y:.2f}, {spawn_transform.location.z:.2f})"
			)
			return False

		try:
			if hasattr(actor, "set_simulate_physics"):
				actor.set_simulate_physics(True)
			actor.set_autopilot(True, tm.get_port())
		except Exception:
			pass

		self._vehicle_actor_ids.append(actor.id)
		print(
			f"[Scenario01] TrafficJam vehicle spawned: id={actor.id}, sim_time={sim_time:.2f}s, "
			f"spawn=({spawn_transform.location.x:.2f}, {spawn_transform.location.y:.2f}, {spawn_transform.location.z:.2f})"
		)
		return True

	def _spawn_trafficjam_vehicles(self, trigger_config, sim_time):
		if self._trafficjam_spawned:
			return True

		spawn_configs = trigger_config.get("spawn_configs", [])
		spawned_count = 0
		for spawn_config in spawn_configs:
			if self._spawn_trafficjam_vehicle(spawn_config, sim_time):
				spawned_count += 1

		print(f"[Scenario01] TrafficJam vehicles spawned: {spawned_count}/{len(spawn_configs)}")
		if spawned_count > 0:
			self._trafficjam_spawned = True
			self._trafficjam_spawn_time = sim_time
		return spawned_count > 0

	def _prune_far_trafficjam_vehicles(self, ego_location):
		delay_state = self._delay_states.get("trafficjam_to_badguy")
		if not self._prune_tj_cars or ego_location is None or not self._vehicle_actor_ids:
			return
		if delay_state is None or not delay_state["finished"]:
			return

		active_vehicle_ids = []
		for vehicle_id in list(self._vehicle_actor_ids):
			actor = self.world.get_actor(vehicle_id)
			if actor is None:
				continue

			try:
				vehicle_location = actor.get_location()
			except Exception:
				continue

			distance = math.hypot(vehicle_location.x - ego_location.x, vehicle_location.y - ego_location.y)
			if distance > TRAFFICJAM_PRUNE_DISTANCE_METERS:
				print(f"[Scenario01] TrafficJam vehicle removed: id={vehicle_id}, distance={distance:.1f}m")
				try:
					actor.destroy()
				except Exception:
					pass
				continue

			active_vehicle_ids.append(vehicle_id)

		self._vehicle_actor_ids = active_vehicle_ids

	def _reset_redlight_control(self):
		self.redlight_active = False
		self._redlight_started_at = None
		self._redlight_traffic_light_states.clear()
		self._redlight_seen_traffic_light_ids.clear()
		self._redlight_seen_traffic_light_count = 0

	def _start_redlight_control(self, sim_time):
		self.redlight_active = True
		self.redlight_finished = False
		self._redlight_started_at = sim_time
		self._redlight_traffic_light_states.clear()
		self._redlight_seen_traffic_light_ids.clear()
		self._redlight_seen_traffic_light_count = 0
		print("[Scenario01] Ampelsteuerung gestartet.")

	def _finish_redlight_control(self, sim_time):
		if not self.redlight_active:
			return

		self.redlight_active = False
		self.redlight_finished = True
		self._redlight_started_at = None
		self._redlight_traffic_light_states.clear()
		self._redlight_seen_traffic_light_ids.clear()
		self._redlight_seen_traffic_light_count = 0
		self._finish_delay_timer("redlight_to_trafficjam", sim_time)
		print("[Scenario01] Redlight phase finished.")

	def _update_redlight_phase(self, sim_time):
		if not self.redlight_active or self._redlight_started_at is None:
			return

		if (sim_time - self._redlight_started_at) >= REDLIGHT_PHASE_MAX_SECONDS:
			self._finish_redlight_control(sim_time)

	def _get_or_create_redlight_state(self, tl, sim_time):
		state = self._redlight_traffic_light_states.get(tl.id)
		if state is not None:
			return state

		state = {
			"mode": "forced_red",
			"red_started_at": sim_time,
			"red_hold_seconds": self._rng.uniform(REDLIGHT_MIN_RED_SECONDS, REDLIGHT_MAX_RED_SECONDS),
			"green_started_at": None,
			"released": False,
		}
		self._redlight_traffic_light_states[tl.id] = state
		return state

	def _register_redlight_traffic_light(self, tl, sim_time):
		if tl.id in self._redlight_seen_traffic_light_ids:
			return

		self._redlight_seen_traffic_light_ids.add(tl.id)
		self._redlight_seen_traffic_light_count += 1
		print(
			f"[Scenario01] REDLIGHT traffic lights encountered: "
			f"{self._redlight_seen_traffic_light_count}/{REDLIGHT_MAX_TRAFFIC_LIGHTS}"
		)

		if self._redlight_seen_traffic_light_count >= REDLIGHT_MAX_TRAFFIC_LIGHTS:
			self._finish_redlight_control(sim_time)

	def _update_redlight_traffic_light_state(self, tl, sim_time):
		state = self._redlight_traffic_light_states.get(tl.id)
		if state is None:
			state = self._get_or_create_redlight_state(tl, sim_time)

		if state["released"]:
			return

		if state["mode"] == "forced_red":
			if tl.get_state() != carla.TrafficLightState.Red:
				tl.set_state(carla.TrafficLightState.Red)
				print(f"[Scenario01] Ampel auf rot geschaltet | light_id={tl.id}")
			if hasattr(tl, "set_red_time"):
				tl.set_red_time(state["red_hold_seconds"])
			if (sim_time - state["red_started_at"]) >= state["red_hold_seconds"]:
				state["mode"] = "forced_green"
				state["green_started_at"] = sim_time
				if tl.get_state() != carla.TrafficLightState.Green:
					tl.set_state(carla.TrafficLightState.Green)
					print(f"[Scenario01] Ampel auf gruen geschaltet | light_id={tl.id}")
				if hasattr(tl, "set_green_time"):
					tl.set_green_time(REDLIGHT_GREEN_RELEASE_SECONDS)
			return

		if state["mode"] == "forced_green":
			if tl.get_state() != carla.TrafficLightState.Green:
				tl.set_state(carla.TrafficLightState.Green)
				print(f"[Scenario01] Ampel auf gruen gehalten | light_id={tl.id}")
			if hasattr(tl, "set_green_time"):
				tl.set_green_time(REDLIGHT_GREEN_RELEASE_SECONDS)
			if (sim_time - state["green_started_at"]) >= REDLIGHT_GREEN_RELEASE_SECONDS:
				state["mode"] = "released"
				state["released"] = True
				print(f"[Scenario01] Ampel losgelassen | light_id={tl.id}")
			return

		if state["mode"] == "released":
			if tl.get_state() != carla.TrafficLightState.Green:
				tl.set_state(carla.TrafficLightState.Green)
			if hasattr(tl, "set_green_time"):
				tl.set_green_time(HERO_GREEN_LIGHT_HOLD_SECONDS)

	def _force_hero_traffic_light(self, ego, sim_time):
		if ego is None or not ego.is_at_traffic_light():
			return

		tl = ego.get_traffic_light()
		if tl is None:
			return

		if self.redlight_active:
			self._register_redlight_traffic_light(tl, sim_time)
			self._update_redlight_traffic_light_state(tl, sim_time)

		if not self.redlight_active:
			if tl.get_state() != carla.TrafficLightState.Green:
				tl.set_state(carla.TrafficLightState.Green)
			if hasattr(tl, "set_green_time"):
				tl.set_green_time(HERO_GREEN_LIGHT_HOLD_SECONDS)
			return

	def _start_delay_timer(self, delay_name, sim_time):
		delay_state = self._delay_states.get(delay_name)
		if delay_state is None:
			return

		if delay_state["started_at"] is None:
			print(f"{delay_name} delay started!")

		delay_state["started_at"] = sim_time
		delay_state["finished"] = False

	def _finish_delay_timer(self, delay_name, sim_time):
		delay_state = self._delay_states.get(delay_name)
		if delay_state is None:
			return

		if delay_state["started_at"] is None:
			print(f"{delay_name} delay started!")
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

	def start_redlight(self):
		print("start redlight now")
		self._start_redlight_control(self.world.get_snapshot().timestamp.elapsed_seconds)

	def start_trafficjam(self, trigger_config=None, sim_time=None):
		print("start trafficjam now")
		if trigger_config is None:
			trigger_configs = get_static_prop_spawns("trafficjam")
			trigger_config = trigger_configs[0] if trigger_configs else None
		spawned_any = True
		if trigger_config is not None and sim_time is not None:
			spawned_any = self._spawn_trafficjam_vehicles(trigger_config, sim_time)
			if spawned_any:
				self._start_trafficjam_traffic_light_control(sim_time)
		self.trafficjam_finished = bool(spawned_any)

	def start_badguy(self):
		print("start badguy now")
		self.badguy_finished = True

	def start_song(self):
		print("start song now")
		self.song_finished = True

	def start_crossped(self):
		print("start crossped now")
		self.crossped_finished = True

	def start_occupy(self):
		print("start occupy now")
		self.occupy_started = True
		self.occupy_finished = True

	def _skip_redlight_trigger(self, sim_time):
		if self.redlight_finished or self.redlight_active:
			return

		self._reset_redlight_control()
		self.redlight_finished = True
		self._finish_delay_timer("start_to_redlight", sim_time)
		print("[Scenario01] Redlight trigger skipped.")

	def _skip_trafficjam_trigger(self, sim_time):
		if self.trafficjam_finished:
			return

		self._finish_delay_timer("redlight_to_trafficjam", sim_time)
		self.start_trafficjam()
		print("[Scenario01] Trafficjam trigger skipped.")

	def _skip_badguy_trigger(self, sim_time):
		if self.badguy_finished:
			return

		self._finish_delay_timer("trafficjam_to_badguy", sim_time)
		self.start_badguy()
		print("[Scenario01] Badguy trigger skipped.")

	def _skip_song_trigger(self, sim_time):
		if self.song_finished:
			return

		self._finish_delay_timer("badguy_to_song", sim_time)
		self.start_song()
		print("[Scenario01] Song trigger skipped.")

	def _skip_crossped_trigger(self, sim_time):
		if self.crossped_finished:
			return

		self._finish_delay_timer("song_to_crossped", sim_time)
		self.start_crossped()
		print("[Scenario01] Crossped trigger skipped.")

	def _skip_occupy_trigger(self, sim_time):
		if self.occupy_finished:
			return

		self._finish_delay_timer("crossped_to_occupy", sim_time)
		self.start_occupy()
		print("[Scenario01] Occupy trigger skipped.")

	def _update_redlight_trigger(self):
		delay_state = self._delay_states.get("start_to_redlight")
		return delay_state is not None and delay_state["finished"]

	def _update_trafficjam_trigger(self):
		delay_state = self._delay_states.get("redlight_to_trafficjam")
		return delay_state is not None and delay_state["finished"]

	def _update_badguy_trigger(self):
		delay_state = self._delay_states.get("trafficjam_to_badguy")
		return delay_state is not None and delay_state["finished"]

	def _update_song_trigger(self):
		delay_state = self._delay_states.get("badguy_to_song")
		return delay_state is not None and delay_state["finished"]

	def _update_crossped_trigger(self):
		delay_state = self._delay_states.get("song_to_crossped")
		return delay_state is not None and delay_state["finished"]

	def _update_occupy_trigger(self):
		delay_state = self._delay_states.get("crossped_to_occupy")
		return delay_state is not None and delay_state["finished"]

	def run(self):
		print("[Scenario01] Running...")
		if run_in_singleFile_mode:
			self.world.set_weather(carla.WeatherParameters.CloudySunset)
			print("[Scenario01] Weather set to CloudySunset for single-file mode")

		try:
			while True:
				self.world.wait_for_tick()
				if DEBUG_MODE:
					self._draw_trafficjam_trigger_box()
				sim_time = self.world.get_snapshot().timestamp.elapsed_seconds
				self._update_trafficjam_traffic_light_control(sim_time)
				ego = self.find_hero()
				ego_location = ego.get_location() if ego is not None else None
				ego_velocity = ego.get_velocity() if ego is not None else None

				if self._start_sim_time is None:
					self._start_sim_time = sim_time

				if self._start_sim_time is not None:
					start_to_redlight_state = self._delay_states["start_to_redlight"]
					if start_to_redlight_state["started_at"] is None:
						self._start_delay_timer("start_to_redlight", sim_time)
					self._update_delay_timer("start_to_redlight", sim_time)

				if not self._trigger_redlight and self._update_redlight_trigger():
					self._skip_redlight_trigger(sim_time)

				if self._update_redlight_trigger() and not self.redlight_active and not self.redlight_finished:
					if self._trigger_redlight:
						self.start_redlight()

				self._update_redlight_phase(sim_time)
				self._force_hero_traffic_light(ego, sim_time)

				redlight_to_trafficjam_state = self._delay_states["redlight_to_trafficjam"]
				if self.redlight_finished:
					if redlight_to_trafficjam_state["started_at"] is None:
						self._start_delay_timer("redlight_to_trafficjam", sim_time)
					self._update_delay_timer("redlight_to_trafficjam", sim_time)

				if self.redlight_finished and redlight_to_trafficjam_state["finished"] and not self.trafficjam_finished:
					if not self._trigger_trafficjam:
						self._skip_trafficjam_trigger(sim_time)
					else:
						trafficjam_trigger_config = None
						if ego_location is not None:
							trafficjam_trigger_config = self._get_trafficjam_trigger_config(ego_location, ego_velocity)
						if trafficjam_trigger_config is not None:
							self.start_trafficjam(trafficjam_trigger_config, sim_time)

				trafficjam_to_badguy_state = self._delay_states["trafficjam_to_badguy"]
				if self.trafficjam_finished:
					if trafficjam_to_badguy_state["started_at"] is None:
						self._start_delay_timer("trafficjam_to_badguy", sim_time)
					self._update_delay_timer("trafficjam_to_badguy", sim_time)

				if self.trafficjam_finished and trafficjam_to_badguy_state["finished"] and not self.badguy_finished:
					if not self._trigger_badguy:
						self._skip_badguy_trigger(sim_time)
					else:
						self.start_badguy()

				badguy_to_song_state = self._delay_states["badguy_to_song"]
				if self.badguy_finished:
					if badguy_to_song_state["started_at"] is None:
						self._start_delay_timer("badguy_to_song", sim_time)
					self._update_delay_timer("badguy_to_song", sim_time)

				if self.badguy_finished and badguy_to_song_state["finished"] and not self.song_finished:
					if not self._trigger_song:
						self._skip_song_trigger(sim_time)
					else:
						self.start_song()

				song_to_crossped_state = self._delay_states["song_to_crossped"]
				if self.song_finished:
					if song_to_crossped_state["started_at"] is None:
						self._start_delay_timer("song_to_crossped", sim_time)
					self._update_delay_timer("song_to_crossped", sim_time)

				if self.song_finished and song_to_crossped_state["finished"] and not self.crossped_finished:
					if not self._trigger_crossped:
						self._skip_crossped_trigger(sim_time)
					else:
						self.start_crossped()

				crossped_to_occupy_state = self._delay_states["crossped_to_occupy"]
				if self.crossped_finished:
					if crossped_to_occupy_state["started_at"] is None:
						self._start_delay_timer("crossped_to_occupy", sim_time)
					self._update_delay_timer("crossped_to_occupy", sim_time)

				if self.crossped_finished and crossped_to_occupy_state["finished"] and not self.occupy_started:
					if not self._trigger_occupy:
						self._skip_occupy_trigger(sim_time)
					else:
						self.start_occupy()

				occupy_to_end_state = self._delay_states["occupy_to_end"]
				if self.occupy_finished:
					if occupy_to_end_state["started_at"] is None:
						self._start_delay_timer("occupy_to_end", sim_time)
					self._update_delay_timer("occupy_to_end", sim_time)

				if self.occupy_finished and occupy_to_end_state["finished"]:
					self._scenario_done = True

				if self._trafficjam_spawned:
					self._prune_far_trafficjam_vehicles(ego_location)

				if self._scenario_done:
					return

				time.sleep(SIM_STEP_S)
		except KeyboardInterrupt:
			pass
		finally:
			self.destroy()
			self._signal_done()

	def destroy(self):
		print("[Scenario01] Cleanup...")
		if self._vehicle_actor_ids:
			self.client.apply_batch([carla.command.DestroyActor(actor_id) for actor_id in self._vehicle_actor_ids])

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
			print(f"[Scenario01] WARNING: could not write done signal file: {exc}")


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--host", default="127.0.0.1")
	parser.add_argument("--port", default=2000, type=int)
	parser.add_argument("--tm-port", default=8000, type=int)
	parser.add_argument("--done-file", default=None)
	args = parser.parse_args()

	Scenario01Runner(
		args.host,
		args.port,
		args.tm_port,
		args.done_file,
		trigger_redlight=TRIGGER_REDLIGHT,
		trigger_trafficjam=TRIGGER_TRAFFICJAM,
		trigger_badguy=TRIGGER_BADGUY,
		trigger_song=TRIGGER_SONG,
		trigger_crossped=TRIGGER_CROSSPED,
		trigger_occupy=TRIGGER_OCCUPY,
	).run()
