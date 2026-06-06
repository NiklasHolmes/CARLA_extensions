#!/usr/bin/env python

import argparse
import glob
import math
import os
import sys
import time

try:
	sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
		sys.version_info.major,
		sys.version_info.minor,
		'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
	pass

sys.path.insert(0, r'c:\C_CARLA\PythonAPI')
sys.path.insert(0, r'c:\C_CARLA\PythonAPI\carla')

import carla

try:
	from agents.navigation.basic_agent import BasicAgent  # pyright: ignore[reportMissingImports]
except ImportError as exc:
	print(f"Error: Could not import BasicAgent: {exc}")
	raise SystemExit(1)


SPAWN_TRANSFORM = carla.Transform(
	carla.Location(x=-60.70000000, y=-119.80000000, z=0.10000000),
	carla.Rotation(pitch=0.0, yaw=60.0, roll=0.0),
)

TARGET_POINTS = [
	# (-55.10, -99.8, 0.60545044),
	# (-55.10, -98.6, 0.60545044),
	# (-55.10, -97.4, 0.60545044),
	# (-55.10, -95.8, 0.60545044),
	# (-55.10, -94.4, 0.60545044),
	# (-55.10, -93.4, 0.60545044),
	# (-55.10, -92.4, 0.60545044),
	# (-55.10, -91.4, 0.60545044),
	# (-55.10, -90.4, 0.60545044),
	(-54.92,-77.22,0.60),
	(-54.92,-59.71,0.60),
]

TARGET_REACHED_DISTANCE = 1.0
TARGET_SPEED_KMH = 6.0
TM_DISTANCE_TO_LEADING_VEHICLE = 2.5
BLOCKED_ROAD_IDS = {7}


def _get_project_root_python_paths():
	return [r'c:\C_CARLA\PythonAPI', r'c:\C_CARLA\PythonAPI\carla']


def _create_agent(world, vehicle):
	agent = BasicAgent(vehicle, target_speed=TARGET_SPEED_KMH)
	try:
		agent.ignore_traffic_lights(True)
	except Exception:
		pass
	try:
		agent.ignore_stop_signs(True)
	except Exception:
		pass
	return agent


def _project_to_driving_lane(world_map, location):
	waypoint = world_map.get_waypoint(
		location,
		project_to_road=True,
		lane_type=carla.LaneType.Driving,
	)
	if waypoint is None:
		return location
	projected = waypoint.transform.location
	return carla.Location(x=projected.x, y=projected.y, z=projected.z)


def _build_goal_queue(world):
	world_map = world.get_map()
	goals = []
	for x, y, z in TARGET_POINTS:
		goals.append(_project_to_driving_lane(world_map, carla.Location(x=x, y=y, z=z)))
	return goals


def _set_agent_route(agent, world, destination_location, blocked_road_ids=BLOCKED_ROAD_IDS):
	world_map = world.get_map()
	start_waypoint = world_map.get_waypoint(
		agent._vehicle.get_location(),
		project_to_road=True,
		lane_type=carla.LaneType.Driving,
	)
	end_waypoint = world_map.get_waypoint(
		destination_location,
		project_to_road=True,
		lane_type=carla.LaneType.Driving,
	)
	if start_waypoint is None or end_waypoint is None:
		agent.set_destination(destination_location)
		return destination_location
	route = agent.trace_route(start_waypoint, end_waypoint)
	if not route:
		agent.set_destination(destination_location)
		return destination_location

	safe_route = []
	safe_goal = destination_location
	blocked_hit = None
	for route_wp, road_option in route:
		road_id = getattr(route_wp, 'road_id', None)
		if road_id in blocked_road_ids:
			blocked_hit = road_id
			break
		safe_route.append((route_wp, road_option))
		loc = route_wp.transform.location
		safe_goal = carla.Location(x=loc.x, y=loc.y, z=loc.z)

	if not safe_route:
		agent.set_destination(destination_location)
		return destination_location

	if blocked_hit is not None:
		print(
			f'[Scenario01Exp] Road block active: route to ({destination_location.x:.2f}, {destination_location.y:.2f}, {destination_location.z:.2f}) '
			f'stops before blocked road_id={blocked_hit} at ({safe_goal.x:.2f}, {safe_goal.y:.2f}, {safe_goal.z:.2f})'
		)

	agent.set_global_plan(safe_route, stop_waypoint_creation=True, clean_queue=True)
	return safe_goal


def _get_tm(client, tm_port, world):
	tm = client.get_trafficmanager(tm_port)
	tm.set_synchronous_mode(world.get_settings().synchronous_mode)
	try:
		tm.set_global_distance_to_leading_vehicle(TM_DISTANCE_TO_LEADING_VEHICLE)
	except Exception:
		pass
	return tm


def _configure_world_sync(world, enable_sync):
	settings = world.get_settings()
	original = (settings.synchronous_mode, settings.fixed_delta_seconds)
	if enable_sync:
		settings.synchronous_mode = True
		if settings.fixed_delta_seconds is None:
			settings.fixed_delta_seconds = 0.05
	world.apply_settings(settings)
	return original


def _restore_world_sync(world, original_state):
	settings = world.get_settings()
	settings.synchronous_mode, settings.fixed_delta_seconds = original_state
	world.apply_settings(settings)


def _spawn_vehicle(world):
	blueprint = world.get_blueprint_library().find('vehicle.lincoln.mkz_2020')
	if blueprint.has_attribute('role_name'):
		blueprint.set_attribute('role_name', 'scenario01_experiment_vehicle')
	actor = world.try_spawn_actor(blueprint, SPAWN_TRANSFORM)
	return actor


def main():
	argparser = argparse.ArgumentParser(description=__doc__)
	argparser.add_argument('--host', default='127.0.0.1', help='CARLA host')
	argparser.add_argument('-p', '--port', default=2000, type=int, help='CARLA port')
	argparser.add_argument('--tm-port', default=8000, type=int, help='Traffic Manager port')
	args = argparser.parse_args()

	client = carla.Client(args.host, args.port)
	client.set_timeout(10.0)
	world = client.get_world()
	original_sync_state = None

	vehicle = None
	try:
		original_sync_state = _configure_world_sync(world, True)

		tm = _get_tm(client, args.tm_port, world)

		vehicle = _spawn_vehicle(world)
		if vehicle is None:
			print('[Scenario01Exp] ERROR: vehicle.lincoln.mkz_2020 could not be spawned at the requested location.')
			return

		agent = _create_agent(world, vehicle)
		goal_queue = _build_goal_queue(world)
		if not goal_queue:
			print('[Scenario01Exp] ERROR: no target points could be projected onto the road.')
			return

		current_goal = None
		goal_index = 0
		last_report_time = 0.0

		print(f'[Scenario01Exp] Spawned vehicle id={vehicle.id} at {vehicle.get_location()}')
		print(f'[Scenario01Exp] Goals: {len(goal_queue)}')

		current_goal = goal_queue[goal_index]
		current_goal = _set_agent_route(agent, world, current_goal)
		print(f'[Scenario01Exp] Goal 1/{len(goal_queue)} set to ({current_goal.x:.2f}, {current_goal.y:.2f}, {current_goal.z:.2f})')

		# Give the spawned actor one frame to settle into the synced world state.
		world.tick()

		while True:
			if vehicle is None:
				print('[Scenario01Exp] Vehicle reference lost; stopping.')
				break

			if not vehicle.is_alive:
				print('[Scenario01Exp] Vehicle no longer alive; stopping.')
				break

			location = vehicle.get_location()
			speed = vehicle.get_velocity()
			speed_kmh = 3.6 * math.sqrt(speed.x * speed.x + speed.y * speed.y + speed.z * speed.z)

			if current_goal is not None and location.distance(current_goal) <= TARGET_REACHED_DISTANCE:
				goal_index += 1
				if goal_index >= len(goal_queue):
					print('[Scenario01Exp] Final goal reached.')
					break

				current_goal = goal_queue[goal_index]
				current_goal = _set_agent_route(agent, world, current_goal)
				print(f'[Scenario01Exp] Goal {goal_index + 1}/{len(goal_queue)} set to ({current_goal.x:.2f}, {current_goal.y:.2f}, {current_goal.z:.2f})')

			control = agent.run_step()
			vehicle.apply_control(control)
			world.tick()

			now = time.time()
			if now - last_report_time >= 1.0:
				print(
					f'[Scenario01Exp] vehicle={vehicle.id} loc=({location.x:.2f},{location.y:.2f},{location.z:.2f}) '
					f'speed={speed_kmh:.1f} km/h goal_index={goal_index + 1}/{len(goal_queue)} '
					f'current_goal=({current_goal.x:.2f},{current_goal.y:.2f},{current_goal.z:.2f})'
				)
				last_report_time = now

	finally:
		if original_sync_state is not None:
			_restore_world_sync(world, original_sync_state)

		if vehicle is not None:
			try:
				vehicle.destroy()
			except Exception:
				pass


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
	finally:
		print('\ndone.')
