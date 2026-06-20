import carla
import random

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
carla_map = world.get_map()

blueprints_pool = [
    "static.prop.ironplank",
    "static.prop.dirtdebris01",
    "static.prop.dirtdebris02",
    "static.prop.dirtdebris03"
]

all_waypoints = carla_map.generate_waypoints(2.0)
sampled_waypoints = random.sample(all_waypoints, min(1000, len(all_waypoints)))

successful_spawns = []
target_count = 80
spawned_count = 0
total_attempts = 0

print("Starte schnelles Platzieren von Fahrbahn-Objekten (80 Stück, angepasste Höhen)...")

for wp in sampled_waypoints:
    total_attempts += 1
    if spawned_count >= target_count:
        break
        
    lane_jitter = random.uniform(-1.0, 1.0)
    right_vector = wp.transform.get_right_vector()
    
    spawn_loc = wp.transform.location + (right_vector * lane_jitter)
    
    bp_name = random.choice(blueprints_pool)

    if "ironplank" in bp_name:
        spawn_loc.z += 0.01
    else:
        spawn_loc.z -= 0.02

    yaw = random.uniform(0.0, 360.0)
    spawn_transform = carla.Transform(spawn_loc, carla.Rotation(pitch=0.0, yaw=yaw, roll=0.0))
    
    blueprint = world.get_blueprint_library().find(bp_name)
    
    actor = world.try_spawn_actor(blueprint, spawn_transform)
    
    if actor is not None:
        successful_spawns.append({
            "blueprint": bp_name,
            "x": round(spawn_loc.x, 2),
            "y": round(spawn_loc.y, 2),
            "z": round(spawn_loc.z, 2), 
            "yaw": round(yaw, 1)
        })
        spawned_count += 1

print("\n--- POORROAD_OBJECTS_CONFIG ---")
print("POORROAD_OBJECTS_CONFIG = [")
for i, item in enumerate(successful_spawns):
    print(f"    {{")
    print(f"        'name': 'poorroad_obj_{i:03d}',")
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