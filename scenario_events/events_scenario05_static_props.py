#!/usr/bin/env python

import carla


CONSTRUCTION_CONE_SPAWNS = [
    {
        "name": "construction_cone_01",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=102.200, y=301.200, z=0.250),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_02",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=103.100, y=302.700, z=0.250),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_03",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=104.500, y=304.000, z=0.250),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_04",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=108.200, y=304.600, z=0.250),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_05",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=114.100, y=304.600, z=0.250),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_06",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=120.100, y=304.600, z=0.200),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_07",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=124.600, y=304.000, z=0.200),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_08",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=126.000, y=302.700, z=0.200),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_09",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=126.900, y=301.200, z=0.200),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
]

BOTTOM_CONSTRUCTION_CONE_SPAWNS = [
    {
        "name": "construction_cone_10",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=103.000, y=308.000, z=0.250),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_11",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=100.800, y=307.000, z=0.250),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_12",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=98.800, y=306.000, z=0.250),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_13",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=95.700, y=305.300, z=0.250),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_14",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=92.300, y=305.300, z=0.250),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_15",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=88.600, y=306.000, z=0.250),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_16",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=85.900, y=307.000, z=0.250),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "construction_cone_17",
        "blueprints": ["static.prop.constructioncone"],
        "transform": carla.Transform(
            carla.Location(x=83.700, y=308.000, z=0.250),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
]

BOTTOM_LOOP_WALKER_SPAWNS = [
    {
        "name": "woman_walking_blue_0057",
        "walker_blueprint": "walker.pedestrian.0057",
        "transform": carla.Transform(
            carla.Location(x=109.800, y=296.000, z=1.900),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "target_location": carla.Location(x=102.200, y=299.400, z=1.900),
        "target_rotation": carla.Rotation(pitch=0.0, yaw=70.0, roll=0.0),
        "max_speed": 1.4,
    },
]

WARNING_ACCIDENT_SPAWNS = [
    {
        "name": "warning_accident_01",
        "blueprints": ["static.prop.warningaccident"],
        "transform": carla.Transform(
            carla.Location(x=155.600, y=302.400, z=0.200),
            carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "warning_accident_02",
        "blueprints": ["static.prop.warningaccident"],
        "transform": carla.Transform(
            carla.Location(x=54.600, y=302.900, z=0.200),
            carla.Rotation(pitch=0.0, yaw=70.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "warning_accident_03",
        "blueprints": ["static.prop.warningaccident"],
        "transform": carla.Transform(
            carla.Location(x=54.600, y=302.900, z=0.200),               # CHANGE
            carla.Rotation(pitch=0.0, yaw=110.0, roll=0.0),
        ),
        "scale": None,
    },
]

STATIC_PROP_SPAWNS_BY_TRIGGER = {
    "bottom_corner": [
        {
            "name": "street_barrier_01",
            "blueprints": ["static.prop.streetbarrier"],
            "transform": carla.Transform(
                carla.Location(x=45.800, y=295.000, z=0.200),
                carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
            ),
            "scale": None,
        },
        {
            "name": "street_barrier_02",
            "blueprints": ["static.prop.streetbarrier"],
            "transform": carla.Transform(
                carla.Location(x=41.600, y=295.000, z=0.200),
                carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
            ),
            "scale": None,
        },
        {
            "name": "ambulance_01",
            "blueprints": ["vehicle.ford.ambulance"],
            "transform": carla.Transform(
                carla.Location(x=97.200, y=308.400, z=2.000),
                carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
            ),
            "scale": None,
            "light_state": carla.VehicleLightState(
                carla.VehicleLightState.Special1 | carla.VehicleLightState.LowBeam
            ),
            "open_doors": [carla.VehicleDoor.FR],
        },
        {
            "name": "tesla_model3_01",
            "blueprints": ["vehicle.tesla.model3"],
            "transform": carla.Transform(
                carla.Location(x=110.300, y=301.000, z=2.000),
                carla.Rotation(pitch=0.0, yaw=200.0, roll=0.0),
            ),
            "scale": None,
            "immobilize_vehicle": True,
        },
        {
            "name": "audi_a2_01",
            "blueprints": ["vehicle.audi.a2"],
            "transform": carla.Transform(
                carla.Location(x=111.500, y=294.500, z=2.000),
                carla.Rotation(pitch=-10.0, yaw=45.0, roll=180.0),
            ),
            "scale": None,
            "immobilize_vehicle": True,
        },
        {
            "name": "fabienne_0056",
            "blueprints": ["walker.pedestrian.0056"],
            "transform": carla.Transform(
                carla.Location(x=101.200, y=300.000, z=2.00),
                carla.Rotation(pitch=0.0, yaw=-140.0, roll=0.0),
            ),
            "scale": None,
        },
        {
            "name": "man_talking_0058",
            "blueprints": ["walker.pedestrian.0058"],
            "transform": carla.Transform(
                carla.Location(x=102.300, y=300.100, z=2.000),
                carla.Rotation(pitch=0.0, yaw=95.0, roll=0.0),
            ),
            "scale": None,
        },
        {
            "name": "man_sitting_0059",
            "blueprints": ["walker.pedestrian.0059"],
            "transform": carla.Transform(
                carla.Location(x=108.900, y=301.7, z=2.000),
                carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
            ),
            "scale": None,
        },
    ] + CONSTRUCTION_CONE_SPAWNS + BOTTOM_CONSTRUCTION_CONE_SPAWNS + BOTTOM_LOOP_WALKER_SPAWNS + WARNING_ACCIDENT_SPAWNS,
    "bottom_junction": [
        {
            "name": "street_barrier_03",
            "blueprints": ["static.prop.streetbarrier"],
            "transform": carla.Transform(
                carla.Location(x=34.200, y=302.300, z=0.200),
                carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
            ),
            "scale": None,
        },
        {
            "name": "street_barrier_04",
            "blueprints": ["static.prop.streetbarrier"],
            "transform": carla.Transform(
                carla.Location(x=34.200, y=305.700, z=0.200),
                carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
            ),
            "scale": None,
        },
        {
            "name": "ambulance_01",
            "blueprints": ["vehicle.ford.ambulance"],
            "transform": carla.Transform(
                carla.Location(x=97.200, y=308.400, z=2.000),
                carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
            ),
            "scale": None,
            "light_state": carla.VehicleLightState(
                carla.VehicleLightState.Special1 | carla.VehicleLightState.LowBeam
            ),
            "open_doors": [carla.VehicleDoor.All],
        },
        {
            "name": "tesla_model3_01",
            "blueprints": ["vehicle.tesla.model3"],
            "transform": carla.Transform(
                carla.Location(x=110.300, y=301.000, z=2.000),
                carla.Rotation(pitch=0.0, yaw=200.0, roll=0.0),
            ),
            "scale": None,
            "immobilize_vehicle": True,
        },
        {
            "name": "audi_a2_01",
            "blueprints": ["vehicle.audi.a2"],
            "transform": carla.Transform(
                carla.Location(x=111.500, y=294.500, z=2.000),
                carla.Rotation(pitch=-10.0, yaw=45.0, roll=180.0),
            ),
            "scale": None,
            "immobilize_vehicle": True,
        },
        {
            "name": "fabienne_0056",
            "blueprints": ["walker.pedestrian.0056"],
            "transform": carla.Transform(
                carla.Location(x=101.200, y=300.000, z=2.00),
                carla.Rotation(pitch=0.0, yaw=-140.0, roll=0.0),
            ),
            "scale": None,
        },
        {
            "name": "man_talking_0058",
            "blueprints": ["walker.pedestrian.0058"],
            "transform": carla.Transform(
                carla.Location(x=102.300, y=300.100, z=2.0),
                carla.Rotation(pitch=0.0, yaw=95.0, roll=0.0),
            ),
            "scale": None,
        },
        {
            "name": "man_sitting_0059",
            "blueprints": ["walker.pedestrian.0059"],
            "transform": carla.Transform(
                carla.Location(x=108.900, y=301.700, z=2.000),
                carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
            ),
            "scale": None,
        },
    ] + CONSTRUCTION_CONE_SPAWNS + BOTTOM_CONSTRUCTION_CONE_SPAWNS + BOTTOM_LOOP_WALKER_SPAWNS + WARNING_ACCIDENT_SPAWNS,
    "top_corner": CONSTRUCTION_CONE_SPAWNS + WARNING_ACCIDENT_SPAWNS,
}

STATIC_PROP_SPAWNS = [
    prop_config
    for trigger_spawns in STATIC_PROP_SPAWNS_BY_TRIGGER.values()
    for prop_config in trigger_spawns
]


def get_static_prop_spawns(trigger_key=None):
    if trigger_key is None:
        return STATIC_PROP_SPAWNS
    return STATIC_PROP_SPAWNS_BY_TRIGGER.get(trigger_key, [])
