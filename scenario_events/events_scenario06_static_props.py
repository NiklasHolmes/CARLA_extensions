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
    {
        "name": "fence_09",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-39.0000, y=4.7000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_10",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-39.0000, y=0.9000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_11",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-39.0000, y=-2.9000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_12",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-39.0000, y=-6.7000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_13",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=18.8000, y=4.7000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_14",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=18.8000, y=0.9000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_15",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=18.8000, y=-2.9000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_16",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=18.8000, y=-6.7000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_17",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=39.5000, y=3.8000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_18",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=39.5000, y=0.0000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_19",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=39.5000, y=-3.8000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_20",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=39.5000, y=-7.6000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_21",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=91.9000, y=3.8000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_22",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=91.9000, y=0.0000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_23",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=91.9000, y=-3.8000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_24",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=91.9000, y=-7.6000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_25",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=110.2000, y=3.4000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_26",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=110.2000, y=-0.4000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_27",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=110.2000, y=-4.2000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_28",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=110.2000, y=-8.0000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_29",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=146.6000, y=3.4000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_30",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=146.6000, y=-0.4000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_31",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=146.6000, y=-4.2000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_32",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=146.6000, y=-8.0000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },

    # KEINE Rotation (yaw=0.0):
    {
        "name": "fence_33",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-120.5000, y=-79.7000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_34",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-124.3000, y=-79.7000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_35",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-128.1000, y=-79.7000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_36",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-131.9000, y=-79.7000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_37",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-135.7000, y=-79.7000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_38",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-120.0000, y=79.0000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_39",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-123.8000, y=79.0000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_40",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-127.6000, y=79.0000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_41",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-131.4000, y=79.0000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "fence_42",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-135.2000, y=79.0000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
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
                "name": "highped_barrier_1_firetruck_03",
                "blueprints": ["vehicle.carlamotors.firetruck"],
                "transform": carla.Transform(
                    carla.Location(x=25.10, y=182.20, z=2.00),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "highped_barrier_1_firetruck_04",
                "blueprints": ["vehicle.carlamotors.firetruck"],
                "transform": carla.Transform(
                    carla.Location(x=33.60, y=185.60, z=2.00),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
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
                "name": "highped_barrier_1_firetruck_03",
                "blueprints": ["vehicle.carlamotors.firetruck"],
                "transform": carla.Transform(
                    carla.Location(x=25.10, y=182.20, z=2.00),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "highped_barrier_1_firetruck_04",
                "blueprints": ["vehicle.carlamotors.firetruck"],
                "transform": carla.Transform(
                    carla.Location(x=33.60, y=185.60, z=2.00),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
    {
        "name": "highpedBarrierTrigger3",
        "trigger_location": carla.Location(x=200.400, y=3.5, z=0.4),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "spawn_configs": [
            # {
            #     "name": "highped_barrier_1_firetruck_01",
            #     "blueprints": ["vehicle.carlamotors.firetruck"],
            #     "transform": carla.Transform(
            #         carla.Location(x=25.10, y=182.20, z=2.00),
            #         carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
            #     ),
            #     "scale": None,
            # },
            # {
            #     "name": "highped_barrier_1_firetruck_02",
            #     "blueprints": ["vehicle.carlamotors.firetruck"],
            #     "transform": carla.Transform(
            #         carla.Location(x=33.60, y=185.60, z=2.00),
            #         carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
            #     ),
            #     "scale": None,
            # },
        ],
    },
)

START_TEMP_BARRIER_CONFIGS = [
    {
        "name": "temp_start_barrier_01",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=41.50, y=84.60, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "temp_start_barrier_02",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=41.50, y=88.00, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "temp_start_barrier_03",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=41.50, y=91.50, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "temp_start_barrier_04",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=41.50, y=94.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "temp_start_barrier_05",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=20.70, y=84.60, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
        {
        "name": "temp_start_barrier_06",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=20.70, y=88.00, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "temp_start_barrier_07",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=20.70, y=91.50, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "temp_start_barrier_08",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=20.70, y=94.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    # FIRE TRUCKS:
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
]

SANIMAL_ROUTE_CONFIGS = (
    {
        "name": "sanimalTrigger1",
        "trigger_location": carla.Location(x=-206.7000, y=-93.1000, z=0.0000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-261.1000, y=-9.9000, z=0.5000),
        "spawn_yaw": -180.0,
    },
    {
        "name": "sanimalTrigger2",
        "trigger_location": carla.Location(x=-193.3000, y=21.9000, z=0.1000),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-200.9000, y=79.6000, z=0.5000),
        "spawn_yaw": 0.0,
    },
    {
        "name": "sanimalTrigger3",
        "trigger_location": carla.Location(x=-193.2000, y=105.9000, z=0.1000),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-141.60, y=158.000, z=0.5000),
        "spawn_yaw": -90.0,
    },
    {
        "name": "sanimalTrigger4",
        "trigger_location": carla.Location(x=-96.7461, y=-86.3397, z=0.3000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-60.5000, y=-77.0000, z=0.5000),
        "spawn_yaw": -90.0,
    },
    {
        "name": "sanimalTrigger5",
        "trigger_location": carla.Location(x=-52.7099, y=-22.8105, z=0.4500),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-63.0003, y=15.7000, z=0.5003),
        "spawn_yaw": 0.0,
    },
    {
        "name": "sanimalTrigger6",
        "trigger_location": carla.Location(x=-77.9000, y=-141.8000, z=0.1000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-110.900, y=-149.7000, z=0.5000),
        "spawn_yaw": 90.0,
    },
    {
        "name": "sanimalTrigger7",
        "trigger_location": carla.Location(x=29.5196, y=-141.6128, z=0.3000),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=19.9000, y=-98.9000, z=0.5000),
        "spawn_yaw": 0.0,
    },
    {
        "name": "sanimalTrigger8",
        "trigger_location": carla.Location(x=131.90, y=-135.10, z=0.20),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=79.00, y=-153.00, z=0.90),
        "spawn_yaw": 0.0,
        "target_location": carla.Location(x=73.90, y=-142.80, z=0.20),
    },
    {
        "name": "sanimalTrigger9",
        "trigger_location": carla.Location(x=151.50, y=-5.0, z=0.20),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=146.00, y=48.20, z=0.90),
        "spawn_yaw": 0.0,
        "target_location": carla.Location(x=158.0, y=48.20, z=0.20),
    },
    {
        "name": "sanimalTrigger10",
        "trigger_location": carla.Location(x=98.1000, y=-5.0000, z=0.3000),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=90.0998, y=51.0000, z=0.5002),
        "spawn_yaw": 0.0,
    },
    {
        "name": "sanimalTrigger11",
        "trigger_location": carla.Location(x=33.2993, y=54.5896, z=0.3000),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=44.2000, y=9.5, z=0.5000),
        "spawn_yaw": 180.0,
    },
    {
        "name": "sanimalTrigger12",
        "trigger_location": carla.Location(x=10.0114, y=86.5852, z=0.3000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-39.4000, y=77.8000, z=0.5000),
        "spawn_yaw": 90.0,
    },
    {
        "name": "sanimalTrigger13",
        "trigger_location": carla.Location(x=26.2527, y=144.3343, z=0.3000),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=15.3000, y=179.9000, z=0.5000),
        "spawn_yaw": 0.0,
    },
    {
        "name": "sanimalTrigger14",
        "trigger_location": carla.Location(x=69.9, y=91.40, z=0.500),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=112.00, y=25.40, z=0.5000),
        "spawn_yaw": 180.0,
    },
    {
        "name": "sanimalTrigger15",
        "trigger_location": carla.Location(x=-108.10, y=-137.32, z=0.6000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-63.1000, y=-100.500, z=0.5000),
        "spawn_yaw": 0.0,
    },
)

TEMP_BARRIER_AVOID_HIGHWAY_TRIGGER = [ {
        "name": "ah_trigger",
        "trigger_location": carla.Location(x=80, y=0.0, z=0.0),
        "trigger_x_tolerance": 80.0,
        "trigger_y_tolerance": 100.0,
    }
]

TEMP_BARRIER_AVOID_HIGHWAY = [
    {
        "name": "temp_avoidHighway_barrier_01",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=24.20, y=101.0, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "temp_avoidHighway_barrier_02",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=27.50, y=101.0, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "temp_avoidHighway_barrier_03",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=41.70, y=-152.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=-45.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "temp_avoidHighway_barrier_04",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=38.60, y=-150.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=-45.0, roll=0.0),
        ),
        "scale": None,
    },
        {
        "name": "temp_avoidHighway_barrier_05",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=35.50, y=-148.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=-45.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "temp_avoidHighway_barrier_06",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=31.50, y=-147.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=-45.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "temp_avoidHighway_barrier_07",     # right lane
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=37.30, y=-98.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "temp_avoidHighway_barrier_08",     # right lane
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=33.80, y=-98.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "temp_avoidHighway_barrier_10",
        "blueprints": ["static.prop.treepine2custom"],
        "transform": carla.Transform(
            carla.Location(x=40.10, y=-156.80, z=1.0),
            carla.Rotation(pitch=90.0, yaw=-45.0, roll=0.0),
        ),
        "scale": None,
    },
    # {
    #     "name": "temp_avoidHighway_barrier_08",
    #     "blueprints": ["vehicle.carlamotors.firetruck"],
    #     "transform": carla.Transform(
    #         carla.Location(x=30.90, y=156.30, z=0.00),
    #         carla.Rotation(pitch=0.0, yaw=135.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
]

BUS_DISP_CONFIG = (
    {
        "name": "bus_trigger1",
        "trigger_location": carla.Location(x=-193.28, y=20.0, z=0.3000),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-161.350, y=84.3800, z=0.3000),
        "spawn_yaw": 180,
    },
    {
        "name": "bus_trigger2",
        "trigger_location": carla.Location(x=-141.6022, y=-95.1071, z=0.3000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-185.3000, y=-65.9000, z=0.5000),
        "spawn_yaw": -90.0,
    },
    {
        "name": "bus_trigger3",
        "trigger_location": carla.Location(x=-112.2053, y=-86.1628, z=0.3000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-54.9000, y=-109.8000, z=0.5000),
        "spawn_yaw": 75.0,
    },
    {
        "name": "bus_trigger4",
        "trigger_location": carla.Location(x=-109.6865, y=92.9412, z=0.3000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-54.4000, y=66.3000, z=0.3000),
        "spawn_yaw": 90.0,
    },
    {
        "name": "bus_trigger5",
        "trigger_location": carla.Location(x=-52.51, y=34.89, z=0.3000),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-19.30, y=84.50, z=0.3000),
        "spawn_yaw": 180.0,
    },
    {
        "name": "bus_trigger6",
        "trigger_location": carla.Location(x=-45.6918, y=-21.4710, z=0.4500),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-71.35, y=-84.500, z=0.5000),
        "spawn_yaw": 0.0,
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
    {
        "name": "bus_trigger11",
        "trigger_location": carla.Location(x=-193.1000, y=104.6000, z=0.1000),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-130.5000, y=116.8000, z=0.10000),
        "spawn_yaw": 90.0,
    },
    {
        "name": "bus_trigger21",
        "trigger_location": carla.Location(x=-143.7276, y=86.2022, z=0.3000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-184.2000, y=120.1000, z=0.1000),
        "spawn_yaw": -90.0,
    },
    {
        "name": "bus_trigger22",
        "trigger_location": carla.Location(x=-130.0000, y=-132.0000, z=0.0000),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-95.4000, y=-94.9000, z=0.10000),
        "spawn_yaw": 180.0,
    },
    {
        "name": "bus_trigger8",
        "trigger_location": carla.Location(x=87.5000, y=72.4000, z=0.0000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=35.1000, y=119.2000, z=0.1000),
        "spawn_yaw": -90.0,
    },
)

def get_highped_barrier_spawns():
    return HIGHPED_BARRIER_CONFIGS

def get_start_fence_spawns():
    return START_FENCE_SPAWNS + START_TEMP_BARRIER_CONFIGS

