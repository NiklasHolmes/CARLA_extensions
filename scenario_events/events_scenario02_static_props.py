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
]

def get_start_barrier_spawns():
    return START_BARRIER_SPAWNS


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
        ],
    },
    {"name": "route2", "waypoints": []},
    {"name": "route3", "waypoints": []},
    {"name": "route4", "waypoints": []},
    {"name": "route5", "waypoints": []},
]


def get_traffic_route_configs():
    return TRAFFIC_ROUTE_CONFIGS


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
        "spawn_configs": [
            {
                "name": "trashbag_01",
                "blueprints": ["static.prop.ironplank"],
                "transform": carla.Transform(
                    carla.Location(x=16.00, y=231.30, z=0.20),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "container_01",
                "blueprints": ["static.prop.ironplank"],
                "transform": carla.Transform(
                    carla.Location(x=16.00, y=236.60, z=0.20),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
    {
        "name": "poorroadtrigger2",
        "trigger_location": carla.Location(x=665, y=114.5, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 145.0,
        "spawn_configs": [],
    },
)

SNAKE_CONFIGS = (
    {
        "name": "snakeTrigger1",
        "trigger_location": carla.Location(x=107.91, y=251.56, z=0.30),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 5.0,
        "spawn_configs": [
            {
                "name": "snake_start_01",
                "transform": carla.Transform(
                    carla.Location(x=163.40, y=255.70, z=2.10),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "snake_end_01",
                "transform": carla.Transform(
                    carla.Location(x=163.40, y=236.10, z=2.10),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
    {
        "name": "snakeTrigger2",
        "trigger_location": carla.Location(x=175.70, y=244.60, z=0.10),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "spawn_configs": [
            {
                "name": "highped_barrier_start_02",
                "blueprints": ["vehicle.carlamotors.firetruck"],
                "transform": carla.Transform(
                    carla.Location(x=213.90, y=255.20, z=0.20),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "highped_barrier_ende_02",
                "blueprints": ["static.prop.container"],
                "transform": carla.Transform(
                    carla.Location(x=213.90, y=236.00, z=0.20),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
)

DRIVERTRASH_SPAWN_CONFIGS = (
    {
        "name": "drivertrash_trigger1",
        "trigger_location": carla.Location(x=107.91, y=244.56, z=0.30),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": 1,
        "trigger_direction_axis_2": "y",
        "trigger_direction_sign_2": -1,
        "spawn_configs": [
            {
                "name": "drivertrash_spawn_1",
                "blueprints": ["vehicle.nissan.patrol"],
                "transform": carla.Transform(
                    carla.Location(x=100, y=244, z=1.50),                     # CHANGE?
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
                #"color": "255,255,255",
                "audio_mode": "horn_only",
            },
        ],
    },
    {
        "name": "drivertrash_trigger2",
        "trigger_location": carla.Location(x=175.70, y=244.60, z=0.10),     # CHANGE?
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": 1,
        "trigger_direction_axis_2": "y",
        "trigger_direction_sign_2": -1,
        "spawn_configs": [
            {
                "name": "drivertrash_spawn_1",
                "blueprints": ["vehicle.nissan.patrol"],
                "transform": carla.Transform(
                    carla.Location(x=175.70, y=244.60, z=1.50),                    # CHANGE!
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
                #"color": "255,255,255",
                "audio_mode": "horn_only",
            },
        ],
    },
)

def get_trash_trigger_config():
    return TRASH_TRIGGER_CONFIG

def get_poorroad_trigger_config():
    return POORROAD_TRIGGER_CONFIG

def get_snake_configs():
    return SNAKE_CONFIGS

def get_drivertrash_spawn_configs():
    return DRIVERTRASH_SPAWN_CONFIGS