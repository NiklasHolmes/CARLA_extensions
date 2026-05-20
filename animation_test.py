import time
import argparse
import math

import carla


SNAKE_BLUEPRINT_ID = "walker.pedestrian.0052"
POLICE_WAVING_ID = "walker.pedestrian.0053"  # duplicated waving blueprint (Use Animation Asset)
POLICE_NORMAL_ID = "walker.pedestrian.0030"  # original police blueprint

SNAKE_SPAWN_LOCATION = carla.Location(x=122.20, y=311.70, z=0.40)
POLICE_SPAWN_LOCATION = carla.Location(x=112.20, y=311.70, z=0.40)
TARGET_LOCATION = carla.Location(x=104.00, y=317.80, z=0.40)
SPAWN_ROTATION = carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0)
TIMEOUT_S = 180.0
ARRIVE_THRESH = 1.0
STEP_S = 0.1
WAVING_SECONDS = 2.0


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--actor", choices=["snake", "police", "both"], default="police",
						help="Which actor(s) to spawn: snake (default), police, or both")
	args = parser.parse_args()

	client = carla.Client("127.0.0.1", 2000)
	client.set_timeout(5.0)
	world = client.get_world()
	blueprint_library = world.get_blueprint_library()

	do_snake = args.actor in ("snake", "both")
	do_police = args.actor in ("police", "both")

	# Verify required blueprints
	if do_snake:
		if SNAKE_BLUEPRINT_ID not in {bp.id for bp in blueprint_library.filter(SNAKE_BLUEPRINT_ID)}:
			raise RuntimeError(
				f"Blueprint {SNAKE_BLUEPRINT_ID} is not registered in the running CARLA server."
			)
	if do_police:
		missing = [bid for bid in (POLICE_WAVING_ID, POLICE_NORMAL_ID)
				   if bid not in {bp.id for bp in blueprint_library.filter(bid)}]
		if missing:
			raise RuntimeError(f"Blueprint(s) {missing} not registered in running CARLA server.")

	snake = None
	controller = None
	police = None
	police_controller = None

	try:
		if do_snake:
			snake_bp = blueprint_library.find(SNAKE_BLUEPRINT_ID)
			if snake_bp.has_attribute("is_invincible"):
				snake_bp.set_attribute("is_invincible", "false")
			if snake_bp.has_attribute("role_name"):
				snake_bp.set_attribute("role_name", "snake")

			spawn_point = carla.Transform(SNAKE_SPAWN_LOCATION, SPAWN_ROTATION)
			snake = world.spawn_actor(snake_bp, spawn_point)
			controller = world.spawn_actor(
				blueprint_library.find("controller.ai.walker"),
				carla.Transform(),
				snake,
			)
			world.tick()
			print(f"Snake spawned: id={snake.id}, type={snake.type_id}")

			controller.start()
			controller.go_to_location(TARGET_LOCATION)
			controller.set_max_speed(3.0)
			print("Snake is moving...")

		if do_police:
			waving_bp = blueprint_library.find(POLICE_WAVING_ID)
			if waving_bp.has_attribute("is_invincible"):
				waving_bp.set_attribute("is_invincible", "false")

			police_spawn = carla.Transform(POLICE_SPAWN_LOCATION, SPAWN_ROTATION)
			police = world.spawn_actor(waving_bp, police_spawn)
			world.tick()
			print(f"Waving police spawned: id={police.id}")

			# Let the waving animation play for a short time
			start_time = time.time()
			while time.time() - start_time < WAVING_SECONDS:
				world.tick()
				time.sleep(STEP_S)

			# Stage 2: swap to normal police at same transform
			print("Swapping waving police to normal police...")
			current_transform = police.get_transform()
			police.destroy()

			normal_bp = blueprint_library.find(POLICE_NORMAL_ID)
			if normal_bp.has_attribute("is_invincible"):
				normal_bp.set_attribute("is_invincible", "false")
			if normal_bp.has_attribute("role_name"):
				normal_bp.set_attribute("role_name", "police")

			normal_police = world.spawn_actor(normal_bp, current_transform)
			world.tick()

			# Stage 3: attach controller and make him walk away (follow events_town02 pattern)
			controller_bp = blueprint_library.find('controller.ai.walker')
			police_controller = world.spawn_actor(
				controller_bp,
				carla.Transform(),
				normal_police,
			)
			world.tick()
			police_controller.start()

			# Keep your original target, but snap it to a navigable waypoint.
			carla_map = world.get_map()
			target_wp = carla_map.get_waypoint(
				TARGET_LOCATION,
				project_to_road=True,
				lane_type=carla.LaneType.Any,
			)
			target_loc = target_wp.transform.location
			target_loc = carla.Location(
				x=target_loc.x,
				y=target_loc.y,
				z=TARGET_LOCATION.z,
			)

			police_controller.go_to_location(target_loc)
			police_controller.set_max_speed(5.0)
			world.tick()
			print(f"Normal police spawned: id={normal_police.id} and walking to {target_loc}")

			# Wait until arrival or timeout (similar to events_town02)
			start_time = time.time()
			while True:
				world.tick()
				time.sleep(STEP_S)

				loc = normal_police.get_location()
				distance = math.sqrt(
					(loc.x - target_loc.x) ** 2 + (loc.y - target_loc.y) ** 2 + (loc.z - target_loc.z) ** 2
				)
				if distance <= ARRIVE_THRESH:
					print("Police arrived at target.")
					break
				if time.time() - start_time > TIMEOUT_S:
					print("Police movement timeout.")
					break

		# If snake is moving, wait until it arrives or timeout; keep snake and police afterwards
		if do_snake and controller is not None:
			start_time = time.time()
			while True:
				world.tick()
				time.sleep(STEP_S)

				location = snake.get_location()
				distance = ((location.x - TARGET_LOCATION.x) ** 2 + (location.y - TARGET_LOCATION.y) ** 2 + (location.z - TARGET_LOCATION.z) ** 2) ** 0.5
				if distance <= ARRIVE_THRESH:
					print("Snake arrived.")
					break

				if time.time() - start_time > TIMEOUT_S:
					print("Snake movement timeout.")
					break

	finally:
		# stop and remove only the controller; leave spawned actors (snake/police) in world per user request
		if controller is not None:
			try:
				controller.stop()
			except Exception:
				pass
			try:
				controller.destroy()
			except Exception:
				pass
		if police_controller is not None:
			try:
				police_controller.stop()
			except Exception:
				pass
			try:
				police_controller.destroy()
			except Exception:
				pass


if __name__ == "__main__":
	main()
