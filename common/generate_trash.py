import carla
import random
import time

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
carla_map = world.get_map()

blueprints_pool = [
    "static.prop.garbage06", "static.prop.trashcan01", "static.prop.plasticbag",
    "static.prop.shoppingcart", "static.prop.trashbag", "static.prop.trashbag",
    "static.prop.trashbag", "static.prop.box03", "static.prop.box03", "static.prop.trashcan03"
]

all_waypoints = carla_map.generate_waypoints(2.0)
sampled_waypoints = random.sample(all_waypoints, min(1000, len(all_waypoints)))

successful_spawns = []
target_count = 200
spawned_count = 0
total_attempts = 0

print("Starte echtes Physik-Spawning... Objekte fallen gelassen per CARLA-Engine.")

for wp in sampled_waypoints:
    total_attempts += 1
    if spawned_count >= target_count:
        break
        
    side_multiplier = random.choice([-1.0, 1.0])
    right_vector = wp.transform.get_right_vector()
    
    offset_distance = random.uniform(4.8, 5.5)
    spawn_loc = wp.transform.location + (right_vector * offset_distance * side_multiplier)
    
    spawn_loc.z += 2.0 
    
    check_wp = carla_map.get_waypoint(spawn_loc, project_to_road=True, lane_type=carla.LaneType.Driving)
    if check_wp:
        if spawn_loc.distance(check_wp.transform.location) < 2.5:
            continue

    yaw = random.uniform(0.0, 360.0)
    spawn_transform = carla.Transform(spawn_loc, carla.Rotation(yaw=yaw))
    
    bp_name = random.choice(blueprints_pool)
    blueprint = world.get_blueprint_library().find(bp_name)
    

    actor = world.try_spawn_actor(blueprint, spawn_transform)
    
    if actor is not None:
        actor.set_simulate_physics(True)
        
        last_z = actor.get_location().z
        still_falling = True
        ticks_stabilized = 0
        max_ticks = 150
        
        for _ in range(max_ticks):
            world.tick()
            time.sleep(0.005)
            
            current_z = actor.get_location().z
            
            if abs(last_z - current_z) < 0.005:
                ticks_stabilized += 1
                if ticks_stabilized > 5:
                    break
            else:
                ticks_stabilized = 0
                
            last_z = current_z

        actual_loc = actor.get_location()
        
        successful_spawns.append({
            "blueprint": bp_name,
            "x": round(actual_loc.x, 2),
            "y": round(actual_loc.y, 2),
            "z": round(actual_loc.z, 2), 
            "yaw": round(yaw, 1)
        })
        spawned_count += 1
        
        # actor.destroy()

print("\n--- TRASH_OBJECTS_CONFIG ---")
print("TRASH_OBJECTS_CONFIG = [")
for i, item in enumerate(successful_spawns):
    print(f"    {{")
    print(f"        'name': 'trash_obj_{i:03d}',")
    print(f"        'blueprints': ['{item['blueprint']}'],")
    print(f"        'transform': carla.Transform(")
    print(f"            carla.Location(x={item['x']}, y={item['y']}, z={item['z']}),")
    print(f"            carla.Rotation(pitch=0.0, yaw={item['yaw']}, roll=0.0)")
    print(f"        )")
    print(f"    }},")
print("]")

print("\n========================================")
print("             SPAWN STATISTIK            ")
print("========================================")
print(f"Geprüfte Wegpunkte gesamt:  {total_attempts}")
print(f"Erfolgreich gespawnt:       {spawned_count} von gewünschten {target_count} Objekten.")
print("========================================")