#!/usr/bin/env python

import carla


TRAFFICJAM_TRIGGER_CONFIGS = (
	{
		"name": "trafficjamTrigger1",
		"trigger_location": carla.Location(x=-115.92690430, y=-145.73909180, z=0.60545044),
		"trigger_x_tolerance": 2.0,
		"trigger_y_tolerance": 5.0,
		"trigger_direction_axis": "x",
		"trigger_direction_sign": -1,
		"spawn_configs": [
			{
				"name": "trafficjam_car_01",
				"blueprints": ["vehicle.*"],
				"transform": carla.Transform(
					carla.Location(x=-195.20000000, y=-43.40000000, z=0.10000000),
					carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
				),
				"scale": None,
			},
			{
				"name": "trafficjam_car_02",
				"blueprints": ["vehicle.*"],
				"transform": carla.Transform(
					carla.Location(x=-195.20000000, y=-51.40000000, z=0.10000000),
					carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
				),
				"scale": None,
			},
			{
				"name": "trafficjam_car_03",
				"blueprints": ["vehicle.*"],
				"transform": carla.Transform(
					carla.Location(x=-195.20000000, y=-59.40000000, z=0.10000000),
					carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
				),
				"scale": None,
			},
			{
				"name": "trafficjam_car_04",
				"blueprints": ["vehicle.*"],
				"transform": carla.Transform(
					carla.Location(x=-195.20000000, y=-67.40000000, z=0.10000000),
					carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
				),
				"scale": None,
			},
			{
				"name": "trafficjam_car_05",
				"blueprints": ["vehicle.*"],
				"transform": carla.Transform(
					carla.Location(x=-190.20000000, y=-43.40000000, z=0.10000000),
					carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
				),
				"scale": None,
			},
			{
				"name": "trafficjam_car_06",
				"blueprints": ["vehicle.*"],
				"transform": carla.Transform(
					carla.Location(x=-190.20000000, y=-51.40000000, z=0.10000000),
					carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
				),
				"scale": None,
			},
			{
				"name": "trafficjam_car_07",
				"blueprints": ["vehicle.*"],
				"transform": carla.Transform(
					carla.Location(x=-190.20000000, y=-59.40000000, z=0.10000000),
					carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
				),
				"scale": None,
			},
			{
				"name": "trafficjam_car_08",
				"blueprints": ["vehicle.*"],
				"transform": carla.Transform(
					carla.Location(x=-190.20000000, y=-67.40000000, z=0.10000000),
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
