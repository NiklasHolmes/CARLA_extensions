#!/usr/bin/env python

import glob
import os
import sys
import time
import math

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
from carla import VehicleLightState as vls

import argparse
import logging
from numpy import random

# Import the navigation agent
sys.path.insert(0, r'c:\C_CARLA\PythonAPI')
sys.path.insert(0, r'c:\C_CARLA\PythonAPI\carla')

try:
    from agents.navigation.basic_agent import BasicAgent
except ImportError as e:
    print(f"Error: Could not import BasicAgent: {e}")
    sys.exit(1)

# ==============================================================================
# -- Constants -----------------------------------------------------------------
# ==============================================================================

AGENT_OPT_DICT = {
    'base_vehicle_threshold': 6.0,  # Following distance in meters (increased for earlier braking)
    'detection_speed_ratio': 1.2,   # Higher ratio for earlier reaction to obstacles
    'max_brake': 2.0                # Higher brake for quick stops
}

TARGET_SPEED = 45           # km/h (reduced for safer following)
VEHICLE_COLOR = '90,0,0'    # Dark red
VEHICLE_MODEL = 'vehicle.dodge.charger_2020'
DISAPPEAR_DISTANCE = 60.0  # meters - if stuck and this far from hero, exit

# ==============================================================================
# -- Helper Functions ----------------------------------------------------------
# ==============================================================================

def create_vehicle_blueprint(world):
    """Create and configure vehicle blueprint."""
    blueprint = world.get_blueprint_library().find(VEHICLE_MODEL)
    
    if blueprint.has_attribute('color'):
        blueprint.set_attribute('color', VEHICLE_COLOR)
    if blueprint.has_attribute('driver_id'):
        driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
        blueprint.set_attribute('driver_id', driver_id)
    else:
        blueprint.set_attribute('role_name', 'autopilot')
    
    return blueprint

def configure_agent(agent):
    """Configure agent behavior for following."""
    agent.ignore_traffic_lights(True)
    agent.ignore_stop_signs(True)
    agent.ignore_vehicles(False)  # Still respect other vehicles

def is_too_far_from_hero(vehicle, hero):
    """Check if vehicle is too far from hero (> DISAPPEAR_DISTANCE meters)."""
    vehicle_loc = vehicle.get_location()
    hero_loc = hero.get_location()
    distance = vehicle_loc.distance(hero_loc)
    return distance > DISAPPEAR_DISTANCE

def main():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-n', '--number-of-vehicles',
        metavar='N',
        default=1,
        type=int,
        help='Number of vehicles (default: 30)')
    argparser.add_argument(
        '--safe',
        action='store_true',
        help='Avoid spawning vehicles prone to accidents')
    argparser.add_argument(
        '--tm-port',
        metavar='P',
        default=8000,
        type=int,
        help='Port to communicate with TM (default: 8000)')
    argparser.add_argument(
        '--asynch',
        action='store_true',
        help='Activate asynchronous mode execution')
    argparser.add_argument(
        '--hybrid',
        action='store_true',
        help='Activate hybrid mode for Traffic Manager')
    argparser.add_argument(
        '-s', '--seed',
        metavar='S',
        type=int,
        help='Set random device seed and deterministic mode for Traffic Manager')
    argparser.add_argument(
        '--car-lights-on',
        action='store_true',
        default=False,
        help='Enable automatic car light management')

    args = argparser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    vehicles_list = []
    client = carla.Client(args.host, args.port)
    client.set_timeout(10.0)
    synchronous_master = False
    random.seed(args.seed if args.seed is not None else int(time.time()))

    try:
        world = client.get_world()

        traffic_manager = client.get_trafficmanager(args.tm_port)
        traffic_manager.set_global_distance_to_leading_vehicle(2.5)
        if args.hybrid:
            traffic_manager.set_hybrid_physics_mode(True)
            traffic_manager.set_hybrid_physics_radius(70.0)
        if args.seed is not None:
            traffic_manager.set_random_device_seed(args.seed)

        settings = world.get_settings()
        if not args.asynch:
            traffic_manager.set_synchronous_mode(True)
            if not settings.synchronous_mode:
                synchronous_master = True
                settings.synchronous_mode = True                            # default = synchronous mode
                settings.fixed_delta_seconds = 0.05
            else:
                synchronous_master = False
        else:
            print("You are currently in asynchronous mode. If this is a traffic simulation, \
            you could experience some issues. If it's not working correctly, switch to synchronous \
            mode by using traffic_manager.set_synchronous_mode(True)")

        world.apply_settings(settings)

        # @todo cannot import these directly.
        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        FutureActor = carla.command.FutureActor

        # --------------
        # Spawn vehicles
        # --------------

        # red: '73,0,0'
        # blue: '0,39,105'
        # black: '0,0,0'
        # yellow: '211,142,0'

        batch = []
        
        # Create vehicle blueprint
        blueprint = create_vehicle_blueprint(world)
        
        spawn_point = carla.Transform(
            carla.Location(x=14.01001953, y=306.42000000, z=0.50),
            # (X=1401.001953,Y=30642.000000,Z=50.000000) # PlayerStart46
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0)
        )

        # spawn the car without autopilot - we'll control it manually
        batch.append(SpawnActor(blueprint, spawn_point))

        for response in client.apply_batch_sync(batch, synchronous_master):
            if response.error:
                logging.error(response.error)
            else:
                vehicles_list.append(response.actor_id)

        # Set automatic vehicle lights update if specified
        if args.car_lights_on:
            all_vehicle_actors = world.get_actors(vehicles_list)
            for actor in all_vehicle_actors:
                traffic_manager.update_vehicle_lights(actor, True)

        print('spawned %d vehicles, press Ctrl+C to exit.' % (len(vehicles_list)))

        # Get the spawned vehicle
        all_vehicle_actors = world.get_actors(vehicles_list)
        spawned_vehicle = all_vehicle_actors[0] if all_vehicle_actors else None
        
        if spawned_vehicle is None:
            print("Error: Vehicle not spawned correctly")
            return
        
        # Find the hero vehicle
        hero_vehicle = None
        for actor in world.get_actors().filter('vehicle.*'):
            if actor.attributes.get('role_name') == 'hero':
                hero_vehicle = actor
                break
        
        if hero_vehicle is None:
            print("Error: Hero vehicle not found in the world")
            return
        
        print(f"Hero vehicle found at: {hero_vehicle.get_location()}")
        print(f"Spawned vehicle at: {spawned_vehicle.get_location()}")
        
        # Store original spawn point
        original_spawn_point = spawn_point
        
        # Get collision sensor blueprint (will be reused on respawn)
        collision_bp = world.get_blueprint_library().find('sensor.other.collision')
        
        # Create collision sensor
        collision_sensor = world.spawn_actor(collision_bp, carla.Transform(), attach_to=spawned_vehicle)
        
        # Track collisions
        collision_detected = {'active': False, 'first_time': None, 'last_time': None}
        
        def on_collision(event):
            """Callback when collision is detected - only track static objects"""
            current_time = time.time()
            other_actor = event.other_actor
            
            # Only track collisions with STATIC objects (walls, buildings, etc.)
            if not other_actor.type_id.startswith('static.'):
                return  # Ignore collisions with vehicles and other dynamic objects
            
            if not collision_detected['active']:
                # First collision with static object detected
                collision_detected['active'] = True
                collision_detected['first_time'] = current_time
                collision_detected['last_time'] = current_time
                print(f"\n--- Collision started with STATIC object: {other_actor.type_id}")
            else:
                # Update last collision time (collision is ongoing)
                collision_detected['last_time'] = current_time
        
        collision_sensor.listen(on_collision)
        
        # Create a navigation agent for the spawned vehicle
        agent = BasicAgent(spawned_vehicle, target_speed=TARGET_SPEED, opt_dict=AGENT_OPT_DICT)
        configure_agent(agent)
        
        # Configuration parameters
        PRINT_INTERVAL = 5.0  # seconds - print status every 5 seconds
        DEST_UPDATE_INTERVAL = 1.0  # seconds - avoid replanning every tick
        DEST_MIN_MOVE = 4.0  # meters - update route only if hero moved enough
        
        last_print_time = time.time()
        last_destination = hero_vehicle.get_location()
        last_dest_update_time = time.time()

        # Initial destination for the agent
        agent.set_destination(last_destination)
        
        print("\nStarting continuous following of hero vehicle...")
        print("="*50)
        
        while True:
            if not args.asynch and synchronous_master:
                world.tick()
            else:
                world.wait_for_tick()
            
            current_time = time.time()
            
            # Get current positions
            spawned_location = spawned_vehicle.get_location()
            hero_location = hero_vehicle.get_location()
            
            # Calculate distance to hero
            distance = spawned_location.distance(hero_location)
            
            # Check if collision is ongoing for more than 5 seconds
            COLLISION_TIMEOUT = 5.0  # seconds
            COLLISION_RESET_TIME = 1.0  # seconds - if no collision for this long, reset
            
            if collision_detected['active']:
                time_since_first_collision = current_time - collision_detected['first_time']
                time_since_last_collision = current_time - collision_detected['last_time']
                
                # Reset if no collision in the last second
                if time_since_last_collision > COLLISION_RESET_TIME:
                    print(f"--- Collision ended (lasted {time_since_first_collision:.1f}s)")
                    collision_detected['active'] = False
                    collision_detected['first_time'] = None
                    collision_detected['last_time'] = None
                
                # Exit if stuck for 5+ seconds AND more than 60m from hero
                elif time_since_first_collision > COLLISION_TIMEOUT:
                    # Check if vehicle is too far from hero
                    too_far = is_too_far_from_hero(spawned_vehicle, hero_vehicle)
                    
                    if too_far:
                        print(f"\n=== VEHICLE STUCK (5s collision + {distance:.2f}m from hero) ===")
                        print(f"Vehicle location: {spawned_vehicle.get_location()}")
                        print(f"Hero location: {hero_vehicle.get_location()}")
                        print(f"Distance: {distance:.2f}m (threshold: {DISAPPEAR_DISTANCE}m)")
                        print("\nVehicle disappeared (out of sight)")
                        return  # Exit the script
                    else:
                        print(f"\n! Vehicle stuck for {time_since_first_collision:.1f}s but still close ({distance:.2f}m < {DISAPPEAR_DISTANCE}m)")
                        print("  Continuing to follow...")
                        # Reset collision timer to give it more time
                        collision_detected['first_time'] = current_time
            
            # Print status every 5 seconds
            if current_time - last_print_time >= PRINT_INTERVAL:
                # Get current speed
                spawned_velocity = spawned_vehicle.get_velocity()
                current_speed_kmh = 3.6 * math.sqrt(spawned_velocity.x ** 2 + spawned_velocity.y ** 2 + spawned_velocity.z ** 2)
                
                print(f"Distance to hero: {distance:.2f}m | Speed: {current_speed_kmh:.1f} km/h")
                #print(f"Hero location: ({hero_location.x:.2f}, {hero_location.y:.2f}, {hero_location.z:.2f})")
                #print(f"Vehicle location: ({spawned_location.x:.2f}, {spawned_location.y:.2f}, {spawned_location.z:.2f})")
                print("-"*50)
                
                last_print_time = current_time
            
            # Continuously follow hero - update destination periodically for stability
            time_since_dest_update = current_time - last_dest_update_time
            hero_moved = hero_location.distance(last_destination)
            if time_since_dest_update >= DEST_UPDATE_INTERVAL and hero_moved >= DEST_MIN_MOVE:
                agent.set_destination(hero_location)
                last_destination = hero_location
                last_dest_update_time = current_time

            control = agent.run_step()
            spawned_vehicle.apply_control(control)

    finally:

        if not args.asynch and synchronous_master:
            settings = world.get_settings()
            settings.synchronous_mode = False
            settings.fixed_delta_seconds = None
            world.apply_settings(settings)

        print('\ndestroying sensors and vehicles')
        
        # Destroy collision sensor if it exists
        try:
            if 'collision_sensor' in locals() and collision_sensor is not None:
                collision_sensor.destroy()
        except:
            pass
        
        # Destroy all vehicles
        print('destroying %d vehicles' % len(vehicles_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])

        time.sleep(0.5)

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
