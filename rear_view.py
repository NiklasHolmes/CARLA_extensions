#!/usr/bin/env python3
import carla
import pygame
import numpy as np
import time

# ----------------------------------------------------------
# Find ego vehicle
# ----------------------------------------------------------
def find_hero_vehicle(world):
    actors = world.get_actors().filter("vehicle.*")
    for v in actors:
        if v.attributes.get("role_name", "") == "hero":
            return v
    return None


def find_rear_camera(world, hero):
    sensors = world.get_actors().filter("sensor.camera.rgb")
    rear_candidates = []

    for s in sensors:
        parent = s.parent
        if parent and parent.id == hero.id:

            yaw = s.get_transform().rotation.yaw

            # ----- Robust rear detection -----
            # calculate yaw difference to perfect 180°
            angle = (yaw - 180) % 360
            if angle > 180:
                angle -= 360

            # camera faces backwards if yaw is within ±90° around 180°
            if abs(angle) < 90:
                rear_candidates.append(s)

    return rear_candidates[0] if rear_candidates else None


# ----------------------------------------------------------
# Convert CARLA image → pygame surface
# ----------------------------------------------------------
def to_surface(image):
    arr = np.frombuffer(image.raw_data, dtype=np.uint8)
    arr = arr.reshape((image.height, image.width, 4))
    arr = arr[:, :, :3][:, :, ::-1]
    return pygame.surfarray.make_surface(arr.swapaxes(0, 1))


# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------
def main():
    print("Connecting to CARLA...")

    client = carla.Client("127.0.0.1", 2000)
    client.set_timeout(5.0)

    world = client.get_world()

    # Wait for hero spawn
    hero = None
    for _ in range(60):
        hero = find_hero_vehicle(world)
        if hero:
            break
        time.sleep(0.1)

    if hero is None:
        raise RuntimeError("Hero vehicle (role_name=hero) not found!")

    print("Found ego vehicle:", hero)

    # Wait & find rear cam
    rear_cam = None
    for _ in range(60):
        rear_cam = find_rear_camera(world, hero)
        if rear_cam:
            break
        time.sleep(0.1)

    if not rear_cam:
        raise RuntimeError("Rear camera not found! Did manual_control spawn it?")

    print("Found rear camera:", rear_cam.id)

    # Start pygame
    pygame.init()
    pygame.display.set_caption("Rear View Camera")

    width = int(rear_cam.attributes["image_size_x"])
    height = int(rear_cam.attributes["image_size_y"])

    window = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    surface = None

    def callback(img):
        nonlocal surface
        surface = to_surface(img)

    # Start streaming
    rear_cam.listen(callback)

    print("Streaming…")

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if surface is not None:
            window.blit(surface, (0, 0))

        pygame.display.flip()

    rear_cam.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
