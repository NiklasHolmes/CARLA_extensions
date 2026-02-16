#!/usr/bin/env python3
import carla
import time

def main():
    # connect to the CARLA server
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    bp_lib = world.get_blueprint_library()
    
    # Container Blueprint vorbereiten
    container_bp = bp_lib.find('static.prop.mesh')
    mesh_path = '/Game/Carla/Static/Dynamic/Trash/SM_Container.SM_Container'
    container_bp.set_attribute('mesh_path', mesh_path)
    
    spawn_point = carla.Transform(
        carla.Location(x=69.30, y=310.90, z=0.30),
        carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0)
    )
    
    # Spawn container
    container = world.spawn_actor(container_bp, spawn_point)
    print(f"Container gespawnt: ID={container.id}")
    
    # destroy container after some time
    try:
        time.sleep(15)
    finally:
        container.destroy()
        print("Container entfernt")

if __name__ == '__main__':
    main()
