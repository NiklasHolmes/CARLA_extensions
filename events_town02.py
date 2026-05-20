import carla
import math
import time


WAIT_UNTIL_ARRIVAL = True   # whether to wait for the walker to arrive at the target location
TIMEOUT_S = 180.0           # max walker duration
ARRIVE_THRESH = 1.0         # thresh for goal coordinates
STEP_S = 0.1                # tick step for waiting loops


# Trigger settings: spawn pedestrian when hero vehicle passes near this point
TRIGGER_LOCATION = carla.Location(x=88.30, y=306.40, z=0.20)
TRIGGER_X_TOLERANCE = 2.0
TRIGGER_Y_TOLERANCE = 5.0

# how long to wait for the vehicle to arrive (s)
TRIGGER_TIMEOUT = 90.0


def main():
	client = carla.Client("127.0.0.1", 2000)
	client.set_timeout(5.0)
	world = client.get_world()

	def find_hero_vehicle():
		actors = world.get_actors().filter('vehicle.*')
		for actor in actors:
			if actor.attributes.get('role_name', '') == 'hero':
				return actor
		return None

	def wait_for_hero_and_trigger(trigger_loc, x_tol, y_tol, timeout_s):
		start = time.time()
		hero = None

		print('Waiting for hero vehicle to appear...')
		while hero is None:
			world.tick()
			time.sleep(STEP_S)
			hero = find_hero_vehicle()
			if hero is not None:
				print(f'Found hero vehicle {hero.id}. Waiting for trigger area...')
				break
			if time.time() - start > timeout_s:
				print('Hero vehicle did not appear in time.')
				return False

		while True:
			world.tick()
			time.sleep(STEP_S)

			hero = find_hero_vehicle()
			if hero is None:
				print('Hero vehicle lost. Waiting for it to appear again...')
				while hero is None:
					world.tick()
					time.sleep(STEP_S)
					hero = find_hero_vehicle()
					if hero is not None:
						print(f'Found hero vehicle {hero.id}. Resuming trigger check...')
						break

			loc = hero.get_location()
			dx = abs(loc.x - trigger_loc.x)
			dy = abs(loc.y - trigger_loc.y)
			if dx <= x_tol and dy <= y_tol:
				print('Trigger condition met. Spawning pedestrian now.')
				return True
			if time.time() - start > timeout_s:
				print('Trigger wait timed out.')
				return False

	blueprint_library = world.get_blueprint_library()
	walker_bp = blueprint_library.find("walker.pedestrian.0048")
	walker_bp.set_attribute("is_invincible", "false")

	spawn_point = carla.Transform(
		carla.Location(x=122.20, y=311.70, z=0.40),
		carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
	)
	target = carla.Location(x=123.30, y=284.10, z=0.40)

	walker = None
	controller = None

	# wait for hero vehicle to pass trigger point before spawning walker
	if not wait_for_hero_and_trigger(TRIGGER_LOCATION, TRIGGER_X_TOLERANCE, TRIGGER_Y_TOLERANCE, TRIGGER_TIMEOUT):
		return

	try:
		walker = world.spawn_actor(walker_bp, spawn_point)
		controller = world.spawn_actor(
			blueprint_library.find("controller.ai.walker"),
			carla.Transform(),
			walker,
		)

		world.tick()
		controller.start()
		controller.go_to_location(target)
		controller.set_max_speed(3.0)

		print("Pedestrian running...")

		if not WAIT_UNTIL_ARRIVAL:
			for _ in range(600):
				world.tick()
				time.sleep(STEP_S)
		else:
			start_time = time.time()
			while True:
				world.tick()
				time.sleep(STEP_S)

				location = walker.get_location()
				distance = math.sqrt(
					(location.x - target.x) ** 2
					+ (location.y - target.y) ** 2
					+ (location.z - target.z) ** 2
				)

				if distance <= ARRIVE_THRESH:
					print("Arrived. Walker will be removed.")
					break

				if time.time() - start_time > TIMEOUT_S:
					print("Timeout. Walker will be removed.")
					break
	finally:
		if controller is not None:
			controller.stop()
		if walker is not None:
			walker.destroy()
		if controller is not None:
			controller.destroy()


if __name__ == "__main__":
	main()


