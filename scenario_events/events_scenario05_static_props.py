#!/usr/bin/env python

import carla


STATIC_PROP_SPAWNS = [
    {
        "name": "mailbox",
        "blueprints": ["static.prop.mailbox"],
        "transform": carla.Transform(
            carla.Location(x=59.600, y=306.420, z=0.50),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
]
