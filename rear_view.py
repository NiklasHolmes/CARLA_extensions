#!/usr/bin/env python3
import argparse
import carla
import pygame
from pygame.locals import K_ESCAPE
import numpy as np
import time

# ==============================================================================
# -- Rear View Configuration (defined ONCE, used everywhere) ------------------
# ==============================================================================
REAR_VIEW_WIDTH = 1920
REAR_VIEW_HEIGHT = 1080
REAR_VIEW_SCREEN_PERCENTAGE = 0.3
REAR_VIEW_FPS = 10
REAR_VIEW_ROLE_NAME = "hero"


def parse_args():
    parser = argparse.ArgumentParser(description="Rear view camera for CARLA")
    parser.add_argument(
        '--sp-upscale',
        choices=['smooth', 'fast'],
        default='fast',
        help='upscaling filter for low internal camera resolution (default: fast)'
    )
    return parser.parse_args()

def find_hero_vehicle(world):
    actors = world.get_actors().filter("vehicle.*")
    for v in actors:
        if v.attributes.get("role_name", "") == REAR_VIEW_ROLE_NAME:
            return v
    return None

# convert CARLA image => pygame surface
def to_surface(image):
    arr = np.frombuffer(image.raw_data, dtype=np.uint8)
    arr = arr.reshape((image.height, image.width, 4))
    arr = arr[:, :, :3][:, :, ::-1]
    return pygame.surfarray.make_surface(arr.swapaxes(0, 1))

def main():
    args = parse_args()

    print("Connecting to CARLA...")

    client = carla.Client("127.0.0.1", 2000)
    client.set_timeout(5.0)

    world = client.get_world()

    # wait for hero spawn
    hero = None
    for _ in range(60):
        hero = find_hero_vehicle(world)
        if hero:
            break
        time.sleep(0.1)

    if hero is None:
        raise RuntimeError(f"Hero vehicle (role_name={REAR_VIEW_ROLE_NAME}) not found!")

    print("Found ego vehicle:", hero)

    # Spawn rear camera
    bp = world.get_blueprint_library().find('sensor.camera.rgb')
    
    sensor_width = max(1, int(REAR_VIEW_WIDTH * REAR_VIEW_SCREEN_PERCENTAGE))
    sensor_height = max(1, int(REAR_VIEW_HEIGHT * REAR_VIEW_SCREEN_PERCENTAGE))
    
    bp.set_attribute('image_size_x', str(sensor_width))
    bp.set_attribute('image_size_y', str(sensor_height))
    bp.set_attribute('sensor_tick', str(1.0 / REAR_VIEW_FPS))
    bp.set_attribute('gamma', '2.2')
    if bp.has_attribute('enable_postprocess_effects'):
        bp.set_attribute('enable_postprocess_effects', 'True')

    bound_x = 0.5 + hero.bounding_box.extent.x
    bound_z = 0.5 + hero.bounding_box.extent.z

    transform = carla.Transform(
        carla.Location(x=-1.5 * bound_x, z=1.2 * bound_z),
        carla.Rotation(yaw=180)
    )

    rear_cam = world.spawn_actor(
        bp, transform,
        attach_to=hero,
        attachment_type=carla.AttachmentType.Rigid
    )
    rear_cam.stop()

    # Start pygame
    pygame.init()
    pygame.display.set_caption("Rear View Camera")

    window = pygame.display.set_mode((REAR_VIEW_WIDTH, REAR_VIEW_HEIGHT))
    clock = pygame.time.Clock()

    surface = None

    def callback(img):
        nonlocal surface
        raw_surface = to_surface(img)
        if args.sp_upscale == 'smooth':
            surface = pygame.transform.smoothscale(raw_surface, (REAR_VIEW_WIDTH, REAR_VIEW_HEIGHT))
        else:
            surface = pygame.transform.scale(raw_surface, (REAR_VIEW_WIDTH, REAR_VIEW_HEIGHT))

    # Start streaming
    rear_cam.listen(callback)

    print("Streaming…")

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        if surface is not None:
            window.blit(surface, (0, 0))

        pygame.display.flip()

    rear_cam.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
