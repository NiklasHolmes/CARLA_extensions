import re
import carla

try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()
except Exception as e:
    raise RuntimeError(f"Could not connect to CARLA server: {e}")

spectator = world.get_spectator()

map_obj = world.get_map()
map_name = getattr(map_obj, 'name', '') or ''
town_match = re.search(r'Town(?:0*(\d+))', map_name, re.IGNORECASE)
town_name = ''
if town_match:
    town_name = 'Town%02d' % int(town_match.group(1))

town_spectator = {
    'Town02': carla.Transform(
        carla.Location(x=96.900, y=190.30, z=211.42),
        carla.Rotation(pitch=-90.0, yaw=0.0, roll=0.0)
    ),
    # Pseudo coordinates TODO => need adjustment
    'Town01': carla.Transform(
        carla.Location(x=158.080, y=27.180, z=120.0),
        carla.Rotation(pitch=-90.0, yaw=0.0, roll=0.0)
    ),
    'Town03': carla.Transform(
        carla.Location(x=-118.079287, y=0.275539, z=120.0),
        carla.Rotation(pitch=-90.0, yaw=0.0, roll=0.0)
    ),
    'Town04': carla.Transform(
        carla.Location(x=0.0, y=0.0, z=120.0),
        carla.Rotation(pitch=-90.0, yaw=0.0, roll=0.0)
    ),
}

default_transform = carla.Transform(
    carla.Location(x=0.0, y=0.0, z=120.0),
    carla.Rotation(pitch=-90.0, yaw=0.0, roll=0.0)
)

chosen = town_spectator.get(town_name, default_transform)
spectator.set_transform(chosen)

print(f"Server spectator set for map '{map_name}' -> '{town_name}' at {chosen.location}")

if town_name in ('Town01', 'Town03', 'Town04'):
    print("Note: spectator coordinates for this town are pseudo/placeholders and may need tuning.")

print("Server-Kamera wurde in die Vogelperspektive versetzt!")

