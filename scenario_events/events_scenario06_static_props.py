#!/usr/bin/env python

import carla


START_FENCE_SPAWNS = [
    {
        "name": "fence_01",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-62.60, y=4.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_02",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-62.60, y=0.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_03",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-62.60, y=-2.9, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_04",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-62.60, y=-6.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_05",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-180.0, y=4.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_06",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-180.0, y=0.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_07",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-180.0, y=-2.9, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_08",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-180.0, y=-6.7, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
]

CAR_START_LOCATIONS = [
    carla.Transform(carla.Location(x=-54.3000, y=-40.7000, z=0.2000), carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0)),
    carla.Transform(carla.Location(x=-44.3000, y=-40.7000, z=0.2000), carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)),
    carla.Transform(carla.Location(x=-111.8000, y=154.5000, z=0.2000), carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0)),
    carla.Transform(carla.Location(x=-101.1000, y=144.3000, z=0.2000), carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0)),
    carla.Transform(carla.Location(x=-184.7000, y=60.6000, z=0.2000), carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)),
    carla.Transform(carla.Location(x=-195.1000, y=60.6000, z=0.21000), carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0)),
    # horizontal 
    carla.Transform(carla.Location(x=-275.7000, y=-22.7000, z=0.2000), carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0)),
    carla.Transform(carla.Location(x=-265.2000, y=-22.7000, z=0.2000), carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)),
    carla.Transform(carla.Location(x=-70.7000, y=-84.4000, z=0.2000), carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0)),
    carla.Transform(carla.Location(x=-70.7000, y=-95.0000, z=0.2000), carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0)),
    carla.Transform(carla.Location(x=96.3000, y=15.8000, z=0.2000), carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0)),
    carla.Transform(carla.Location(x=106.6000, y=15.8000, z=0.2000), carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)),
    # Highway
    carla.Transform(carla.Location(x=-228.9000, y=2.4000, z=10.2000), carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)),
    carla.Transform(carla.Location(x=-243.0000, y=2.4000, z=10.2000), carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0))
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

HIGHPED_BARRIER_CONFIGS = (
    {
        "name": "highpedBarrierTrigger1",
        "trigger_location": carla.Location(x=-132.80, y=-190.10, z=10.00),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "spawn_configs": [
            {
                "name": "highped_barrier_2_firetruck_01",
                "blueprints": ["vehicle.carlamotors.firetruck"],
                "transform": carla.Transform(
                    carla.Location(x=37.80, y=-179.40, z=2.00),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "highped_barrier_2_firetruck_02",
                "blueprints": ["vehicle.carlamotors.firetruck"],
                "transform": carla.Transform(
                    carla.Location(x=29.30, y=-182.80, z=2.00),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
    {
        "name": "highpedBarrierTrigger2",
        "trigger_location": carla.Location(x=-144.70, y=205.00, z=8.60),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "spawn_configs": [
            {
                "name": "highped_barrier_1_firetruck_01",
                "blueprints": ["vehicle.carlamotors.firetruck"],
                "transform": carla.Transform(
                    carla.Location(x=25.10, y=182.20, z=2.00),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "highped_barrier_1_firetruck_02",
                "blueprints": ["vehicle.carlamotors.firetruck"],
                "transform": carla.Transform(
                    carla.Location(x=33.60, y=185.60, z=2.00),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
)

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

BUS_DISP_CONFIG = (
    {
        "name": "bus_trigger1",
        "trigger_location": carla.Location(x=-193.0668, y=15.8513, z=0.6000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-216.1000, y=91.2000, z=0.0000),
        "spawn_yaw": None,
    },
    {
        "name": "bus_trigger2",
        "trigger_location": carla.Location(x=-141.6022, y=-95.1071, z=0.3000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-184.3000, y=-65.9000, z=0.1000),
        "spawn_yaw": -90.0,
    },
    {
        "name": "bus_trigger3",
        "trigger_location": carla.Location(x=-112.2053, y=-86.1628, z=0.3000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-55.1000, y=-65.3000, z=0.1000),
        "spawn_yaw": -90.0,
    },
    {
        "name": "bus_trigger4",
        "trigger_location": carla.Location(x=-109.6865, y=92.9412, z=0.3000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-54.4000, y=66.3000, z=0.1000),
        "spawn_yaw": 90.0,
    },
    {
        "name": "bus_trigger5",
        "trigger_location": carla.Location(x=-52.2807, y=14.4338, z=0.6000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-78.2000, y=84.3000, z=0.0000),
        "spawn_yaw": None,
    },
    {
        "name": "bus_trigger6",
        "trigger_location": carla.Location(x=-45.6918, y=-21.4710, z=0.4500),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-24.0000, y=-84.4000, z=0.0000),
        "spawn_yaw": 180.0,
    },
    {
        "name": "bus_trigger7",
        "trigger_location": carla.Location(x=16.2114, y=86.3852, z=0.3000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-44.1000, y=115.2000, z=0.1000),
        "spawn_yaw": -90.0,
    },
)

def get_highped_barrier_spawns():
    return HIGHPED_BARRIER_CONFIGS

def get_start_fence_spawns():
    return START_FENCE_SPAWNS

