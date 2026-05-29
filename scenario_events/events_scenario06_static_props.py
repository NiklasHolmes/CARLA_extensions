#!/usr/bin/env python

import carla


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
