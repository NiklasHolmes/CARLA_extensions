#!/usr/bin/env python

import carla


TRAFFICJAM_TRIGGER_CONFIGS = (
	{
		"name": "trafficjamTrigger1",
		"trigger_location": carla.Location(x=-88.64686523, y=-103.26611328, z=0.27530716),
		"trigger_x_tolerance": 2.0,
		"trigger_y_tolerance": 2.0,
		"trigger_direction_axis": "y",
		"trigger_direction_sign": 1,
		"spawn_configs": [
			{
				"name": "trafficjam_car_01",
				"blueprints": ["vehicle.*"],
				"transform": carla.Transform(
					carla.Location(x=-88.64686523, y=-85.06611328, z=0.27530716),
					carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
				),
				"scale": None,
			},
			{
				"name": "trafficjam_car_02",
				"blueprints": ["vehicle.*"],
				"transform": carla.Transform(
					carla.Location(x=-88.64686523, y=-65.06611328, z=0.27530716),
					carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
				),
				"scale": None,
			},
			{
				"name": "trafficjam_car_03",
				"blueprints": ["vehicle.*"],
				"transform": carla.Transform(
					carla.Location(x=-88.64686523, y=-45.06611328, z=0.27530716),
					carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
				),
				"scale": None,
			},
			{
				"name": "trafficjam_car_04",
				"blueprints": ["vehicle.*"],
				"transform": carla.Transform(
					carla.Location(x=-88.64686523, y=-25.06611328, z=0.27530716),
					carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
				),
				"scale": None,
			},
		],
	},
)


def get_static_prop_spawns(trigger_key=None):
	if trigger_key is None:
		return list(TRAFFICJAM_TRIGGER_CONFIGS)

	if trigger_key == "trafficjam":
		return list(TRAFFICJAM_TRIGGER_CONFIGS)

	return []
