#!/usr/bin/env python

import carla


START_FENCE_SPAWNS = [
    {
        "name": "fence_01",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-62.60, y=93.50, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_02",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-62.60, y=89.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_03",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-62.60, y=85.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_04",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-62.60, y=82.10, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_05",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-112.50, y=93.50, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_06",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-112.50, y=89.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_07",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-112.50, y=85.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_08",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-112.50, y=82.10, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
]


HIGHPED_ROUTE_CONFIGS = (
    {
        "name": "highPedTrigger1",
        "trigger_location": carla.Location(x=105.40, y=-190.10, z=0.00),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "spawn_location": carla.Location(x=197.70, y=-52.60, z=1.90),
        "spawn_yaw": None,
        "target_location": carla.Location(x=184.30, y=-72.60,z=1.90),
    },
    {
        "name": "highPedTrigger2",
        "trigger_location": carla.Location(x=112.80, y=204.40, z=0.00),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "spawn_location": carla.Location(x=200.90, y=65.60, z=1.90),
        "spawn_yaw": 90.0,
        "target_location": carla.Location(x=215.40, y=81.20, z=1.90),
    },
)


def get_start_fence_spawns():
    return START_FENCE_SPAWNS


SANIMAL_ROUTE_CONFIGS = (
    {
        "name": "sanimalTrigger1",
        "trigger_location": carla.Location(x=151.50, y=25.0, z=0.20),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=146.00, y=48.20, z=0.90),
        "spawn_yaw": 0.0,
        "target_location": carla.Location(x=158.0, y=48.20, z=0.20),
    },
    {
        "name": "sanimalTrigger2",
        "trigger_location": carla.Location(x=104.50, y=-145.10, z=0.20),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=79.00, y=-153.00, z=0.90),
        "spawn_yaw": None,
        "target_location": carla.Location(x=73.90, y=-142.80, z=0.20),
    },

)
