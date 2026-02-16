import carla
import time
import math
import random

WAIT_UNTIL_ARRIVAL = True   # False: fixed duration; True: wait until arrival
TIMEOUT_S = 180.0           # safety timeout
ARRIVE_THRESH = 1.0         # meters
STEP_S = 0.05               # tick step

def main():
    client = carla.Client("127.0.0.1", 2000)
    client.set_timeout(5.0)
    world = client.get_world()

    # blueprint
    bp = world.get_blueprint_library().find('walker.pedestrian.0030')
    bp.set_attribute('is_invincible', 'false')

    # spawn point
    spawn_point = carla.Transform(
        carla.Location(x=79.99, y=309.48, z=1.85),
        carla.Rotation(yaw=0)
    )

    # spawn walker + controller
    walker = world.spawn_actor(bp, spawn_point)
    controller = world.spawn_actor(
        world.get_blueprint_library().find('controller.ai.walker'),
        carla.Transform(), walker
    )

    world.tick()
    controller.start()

    # target
    target = carla.Location(x=116.2, y=310.0, z=0.35)
    controller.go_to_location(target)
    controller.set_max_speed(1.4)  # m/s

    print("Pedestrian running...")

    if not WAIT_UNTIL_ARRIVAL:
        # fixed duration
        for _ in range(600):
            world.tick()
            time.sleep(STEP_S)
    else:
        # wait until arrival or timeout
        start = time.time()
        while True:
            world.tick()
            time.sleep(STEP_S)
            loc = walker.get_location()
            dist = math.sqrt((loc.x - target.x)**2 + (loc.y - target.y)**2 + (loc.z - target.z)**2)
            if dist <= ARRIVE_THRESH:
                print("Arrived.")
                break
            if time.time() - start > TIMEOUT_S:
                print("Timeout.")
                break

    # cleanup
    controller.stop()
    walker.destroy()
    controller.destroy()

if __name__ == "__main__":
    main()