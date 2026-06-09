#!/usr/bin/env python

import carla

START_BARRIER_SPAWNS = [
    {
        "name": "fence_03",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-14.80, y=250.10, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_04",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-14.80, y=246.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_05",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-14.80, y=242.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_06",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-14.80, y=239.50, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_07",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-14.80, y=145.50, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_08",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-14.80, y=142.60, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_09",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-14.80, y=139.00, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_10",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-14.80, y=135.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_11",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-14.80, y=132.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_12",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-16.50, y=54.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_13",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-16.50, y=51.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_14",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-16.50, y=48.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_15",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-16.50, y=45.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_16",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-16.50, y=43.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_17",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-16.50, y=40.10, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_18",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-16.50, y=-10.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_19",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-16.50, y=-12.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_20",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-16.50, y=-15.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_21",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-16.50, y=-18.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_22",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-16.50, y=-21.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_23",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=-16.50, y=-24.50, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    # {
    #     "name": "fence_24",
    #     "blueprints": ["static.prop.streetbarrier"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-14.4000, y=106.9000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=45.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
    # {
    #     "name": "fence_25",
    #     "blueprints": ["static.prop.streetbarrier"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-13.5000, y=107.8000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=45.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
    # {
    #     "name": "fence_26",
    #     "blueprints": ["static.prop.streetbarrier"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-12.6000, y=108.7000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=45.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
    # {
    #     "name": "fence_27",
    #     "blueprints": ["static.prop.streetbarrier"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-11.7000, y=109.6000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=45.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
    # {
    #     "name": "fence_28",
    #     "blueprints": ["static.prop.streetbarrier"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-14.1000, y=-36.3000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=45.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
    # {
    #     "name": "fence_29",
    #     "blueprints": ["static.prop.streetbarrier"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-13.2000, y=-35.4000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=45.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
    # {
    #     "name": "fence_30",
    #     "blueprints": ["static.prop.streetbarrier"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-12.3000, y=-34.5000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=45.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
    # {
    #     "name": "fence_31",
    #     "blueprints": ["static.prop.streetbarrier"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-11.4000, y=-33.6000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=45.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
]

def get_start_barrier_spawns():
    return START_BARRIER_SPAWNS # + SECFENCE_YELLOW_SPAWNS


# SECFENCE_YELLOW_SPAWNS = [
#     {
#         "name": f"secfence_yellow_{index + 1:02d}",
#         "blueprints": ["static.prop.secfence_yellow"],
#         "transform": carla.Transform(
#             carla.Location(x=-11.10, y=-29.50 + (3.4 * index), z=0.00),
#             carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
#         ),
#         "scale": None,
#     }
#     for index in range(100)
# ]


TRAFFIC_ROUTE_CONFIGS = [
    {
        "name": "route1",
        "waypoints": [
            carla.Location(x=12.64985229, y=346.27230469, z=1.0),
            carla.Location(x=12.00188477, y=227.40572266, z=1.3),
            carla.Location(x=4.24975647, y=162.37706055, z=1.3),
            carla.Location(x=2.82100555, y=125.16694336, z=1.3),
            carla.Location(x=2.32962250, y=20.50780273, z=1.3),
            carla.Location(x=2.69918793, y=-34.87793457, z=1.3),
            carla.Location(x=-4.87654449, y=-98.48838867, z=1.3),
            carla.Location(x=-5.64858459, y=17.21485352, z=1.3),
            carla.Location(x=-5.51978516, y=110.24966797, z=1.3),
            carla.Location(x=-7.26356262, y=162.45070312, z=1.3),
            carla.Location(x=-2.43586609, y=263.16437500, z=1.3),
            carla.Location(x=-1220.000000, y=-6460.000000, z=0.000000),
        ],
    },
    {"name": "route2", "waypoints": []},
    {"name": "route3", "waypoints": []},
    {"name": "route4", "waypoints": []},
    {"name": "route5", "waypoints": []},
]


def get_traffic_route_configs():
    return TRAFFIC_ROUTE_CONFIGS

DESTROY_ZONE = (
    {
        "name": "destroytrigger",
        "trigger_location": carla.Location(x=-16, y=115, z=0.50),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 150.0,
    }
)

def get_destroy_zone_config():
    return DESTROY_ZONE

TRASH_TRIGGER_CONFIG = (
    {
        "name": "trashtrigger",
        "trigger_location": carla.Location(x=8, y=114.5, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 145.0,
        "spawn_configs": [
            {
                "name": "trashbag_01",
                "blueprints": ["static.prop.trashbag"],
                "transform": carla.Transform(
                    carla.Location(x=16.00, y=221.30, z=0.20),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "container_01",
                "blueprints": ["static.prop.container"],
                "transform": carla.Transform(
                    carla.Location(x=16.00, y=216.60, z=0.20),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
)

POORROAD_TRIGGER_CONFIG = (
    {
        "name": "poorroadtrigger1",
        "trigger_location": carla.Location(x=8, y=114.5, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 145.0,

    },
    {
        "name": "poorroadtrigger2",
        "trigger_location": carla.Location(x=665, y=114.5, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 145.0,
        "spawn_configs": [],
    },
)

POORROAD_SPAWNBOX_CONFIG = (
    {
        "name": "PoorRoadBox1",
        "x_min": 46.70,
        "x_max": 578.00,
        "y_min": 237.50,
        "y_max": 251.80,
        "z": 0.0,
    },
    {
        "name": "PoorRoadBox2",
        "x_min": 46.70,
        "x_max": 578.00,
        "y_min": 136.80,
        "y_max": 153.60,
        "z": 0.0,
    },
    {
        "name": "PoorRoadBox3",
        "x_min": 46.70,
        "x_max": 578.00,
        "y_min": 237.50,
        "y_max": 251.80,
        "z": 0.0,
    },
    {
        "name": "PoorRoadBox4",
        "x_min": 46.70,
        "x_max": 578.00,
        "y_min": -25.30,
        "y_max": -8.70,
        "z": 0.0,
    },
)

SNAKE_TRIGGER_TOLERANCE_X = 5.0
SNAKE_TRIGGER_TOLERANCE_Y = 10.0
SNAKE_TRIGGER_DIRECTION_AXIS = "x"
SNAKE_TRIGGER_DIRECTION_SIGN = 1
SNAKE_SPAWN_X_OFFSET = 49.80
SNAKE_SPAWN_Y_OFFSET = 11.10
SNAKE_SPAWN_Z_OFFSET = 1.80
SNAKE_TARGET_Y = -19.50
DRIVERTRASH_SPAWN_X_OFFSET = -30.0
DRIVERTRASH_SPAWN_Y_OFFSET = 0.0
DRIVERTRASH_SPAWN_Z = 1.50

def _build_snake_config(index, trigger_location):
    spawn_location = carla.Location(
        x=trigger_location.x + SNAKE_SPAWN_X_OFFSET,
        y=trigger_location.y + SNAKE_SPAWN_Y_OFFSET,
        z=trigger_location.z + SNAKE_SPAWN_Z_OFFSET,
    )
    target_location = carla.Location(
        x=spawn_location.x,
        y=SNAKE_TARGET_Y,
        z=spawn_location.z,
    )
    return {
        "name": f"snakeTrigger{index}",
        "trigger_location": trigger_location,
        "trigger_x_tolerance": SNAKE_TRIGGER_TOLERANCE_X,
        "trigger_y_tolerance": SNAKE_TRIGGER_TOLERANCE_Y,
        "trigger_direction_axis": SNAKE_TRIGGER_DIRECTION_AXIS,
        "trigger_direction_sign": SNAKE_TRIGGER_DIRECTION_SIGN,
        "spawn_configs": [
            {
                "name": f"snake_start_{index:02d}",
                "transform": carla.Transform(
                    spawn_location,
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": f"snake_end_{index:02d}",
                "transform": carla.Transform(
                    target_location,
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    }

SNAKE_AND_DRIVERTRASH_TRIGGER_LOCATIONS = (
    # first lane
    carla.Location(x=114.6000, y=244.5000, z=0.3000),
    carla.Location(x=176.7000, y=244.5000, z=0.3000),
    carla.Location(x=308.6000, y=244.5000, z=0.0000),
    carla.Location(x=442.4000, y=244.5000, z=0.0000),
    carla.Location(x=517.6000, y=244.5000, z=0.0000),

    carla.Location(x=114.6000, y=141.5000, z=0.3000),
    carla.Location(x=176.7000, y=141.5000, z=0.3000),
    carla.Location(x=308.6000, y=141.5000, z=0.0000),
    carla.Location(x=442.4000, y=141.5000, z=0.0000),
    carla.Location(x=517.6000, y=141.5000, z=0.0000),

    carla.Location(x=114.6000, y=41.9000, z=0.3000),
    carla.Location(x=176.7000, y=41.9000, z=0.3000),
    carla.Location(x=308.6000, y=41.9000, z=0.0000),
    carla.Location(x=442.4000, y=41.9000, z=0.0000),
    carla.Location(x=517.6000, y=41.9000, z=0.0000),
)

# Backwards-compatible alias while all route generation uses the shared list.
SNAKE_TRIGGER_LOCATIONS = SNAKE_AND_DRIVERTRASH_TRIGGER_LOCATIONS

SNAKE_CONFIGS = tuple(
    _build_snake_config(index + 1, trigger_location)
    for index, trigger_location in enumerate(SNAKE_AND_DRIVERTRASH_TRIGGER_LOCATIONS)
)


def _build_drivertrash_config(index, trigger_location):
    spawn_location = carla.Location(
        x=trigger_location.x + DRIVERTRASH_SPAWN_X_OFFSET,
        y=trigger_location.y + DRIVERTRASH_SPAWN_Y_OFFSET,
        z=DRIVERTRASH_SPAWN_Z,
    )
    return {
        "name": f"drivertrash_trigger{index}",
        "trigger_location": trigger_location,
        "trigger_x_tolerance": SNAKE_TRIGGER_TOLERANCE_X,
        "trigger_y_tolerance": SNAKE_TRIGGER_TOLERANCE_Y,
        "trigger_direction_axis": SNAKE_TRIGGER_DIRECTION_AXIS,
        "trigger_direction_sign": SNAKE_TRIGGER_DIRECTION_SIGN,
        "spawn_configs": [
            {
                "name": f"drivertrash_spawn_{index:02d}",
                "blueprints": ["vehicle.nissan.patrol"],
                "transform": carla.Transform(
                    spawn_location,
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
                #"color": "255,255,255",
                "audio_mode": "horn_only",
            },
        ],
    }

DRIVERTRASH_SPAWN_CONFIGS = tuple(
    _build_drivertrash_config(index + 1, trigger_location)
    for index, trigger_location in enumerate(SNAKE_AND_DRIVERTRASH_TRIGGER_LOCATIONS)
)

def get_trash_trigger_config():
    return TRASH_TRIGGER_CONFIG

def get_poorroad_trigger_config():
    return POORROAD_TRIGGER_CONFIG

def get_snake_configs():
    return SNAKE_CONFIGS

def get_drivertrash_spawn_configs():
    return DRIVERTRASH_SPAWN_CONFIGS