#!/usr/bin/env python

import carla

START_FENCE_SPAWNS = [
	{
		"name": "Secfence_grey",
		"blueprints": ["static.prop.secfence_grey"],
		"transform": carla.Transform(
	        carla.Location(x=-60.00, y=-82.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-60.00, y=-86.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-60.00, y=-90.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-60.00, y=-94.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-176.40, y=-94.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-176.40, y=-90.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-176.40, y=-86.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-176.40, y=-82.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-199.90, y=-82.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-199.90, y=-86.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-199.90, y=-90.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-199.90, y=-94.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
	{
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-199.90, y=-3.30, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-199.90, y=0.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-199.90, y=4.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-199.90, y=8.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-199.90, y=84.80, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-199.90, y=88.80, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-199.90, y=92.80, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-199.90, y=97.00, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=40.10, y=98.10, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=40.10, y=93.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=40.10, y=89.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=40.10, y=85.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=40.10, y=7.80, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=40.10, y=3.60, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=40.10, y=-0.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=40.10, y=-4.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=91.50, y=-4.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=91.50, y=-0.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=91.50, y=3.60, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=91.50, y=7.80, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
	{
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=93.70, y=9.00, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=97.80, y=9.00, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=101.80, y=9.00, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=105.70, y=9.00, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=147.50, y=9.00, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=151.50, y=9.00, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=155.40, y=9.00, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=22.10, y=100.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=26.20, y=100.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=30.20, y=100.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=34.10, y=100.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=38.20, y=-154.60, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=34.30, y=-154.60, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=30.30, y=-154.60, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=26.20, y=-154.60, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-135.60, y=-129.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-131.70, y=-129.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-127.60, y=-129.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-123.60, y=-129.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-119.70, y=-129.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-120.50, y=-9.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-124.40, y=-9.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-128.40, y=-9.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-132.50, y=-9.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-136.40, y=-9.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-197.30, y=12.50, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-193.40, y=12.50, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-189.30, y=12.50, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-185.30, y=12.50, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-185.30, y=79.30, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-189.30, y=79.30, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-193.40, y=79.30, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "Secfence_grey",
        "blueprints": ["static.prop.secfence_grey"],
        "transform": carla.Transform(
            carla.Location(x=-197.30, y=79.30, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
]

TRAFFICJAM_TRIGGER_CONFIGS = (
	{
		"name": "trafficjamTrigger1",   # CORRECT
		"trigger_1": {
            "trigger_location": carla.Location(x=-115.92690430, y=-145.73909180, z=0.60545044),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": -1,
        },
        "trigger_2_destroyBarriers": {
            "trigger_location": carla.Location(x=-195.09, y=-78.55, z=0.60000000),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": 1  # Richtung +x
        },
		"spawn_configs": [
			{
				"name": "trafficjam_car_01",
				"blueprints": ["vehicle.*"],
				"transform": carla.Transform(
					carla.Location(x=-195.20000000, y=-43.40000000, z=0.30000000),
					carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
				),
				"scale": None,
				"first": True,
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
					carla.Location(x=-190.20000000, y=-43.40000000, z=0.30000000),
					carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
				),
				"scale": None,
				"first": True,
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
	{
		"name": "trafficjamTrigger2",
        "trigger_1": {
            "trigger_location": carla.Location(x=-36.26219482, y=93.32519531, z=0.30000000),        # CORRECT
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 4.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": 1,
        },
        "trigger_2_destroyBarriers": {
            "trigger_location": carla.Location(x=33.38, y=72.71, z=0.60000000),
            "trigger_x_tolerance": 3.0,
            "trigger_y_tolerance": 3.0,
            "trigger_direction_axis": "y",
            "trigger_direction_sign": -1  # Richtung +x
        },
		"spawn_configs": [
{
                "name": "trafficjam_car_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=35.10000000, y=16.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
				"first": True,
            },
            {
                "name": "trafficjam_car_02",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=35.10000000, y=23.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_03",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=35.10000000, y=30.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_04",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=35.10000000, y=37.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_05",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=35.10000000, y=44.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_06",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=35.10000000, y=51.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_07",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=35.10000000, y=58.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_08",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=35.10000000, y=65.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            # --- Reihe 2 (Start bei X=31.6) ---
            {
                "name": "trafficjam_car_09",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=31.60000000, y=16.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
				"first": True,
            },
            {
                "name": "trafficjam_car_10",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=31.60000000, y=23.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_11",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=31.60000000, y=30.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_12",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=31.60000000, y=37.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_13",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=31.60000000, y=44.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_14",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=31.60000000, y=51.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_15",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=31.60000000, y=58.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_16",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=31.60000000, y=65.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
                "scale": None,
            },
		],
	},
	{
        "name": "trafficjamTrigger3",
        "trigger_1": {
            "trigger_location": carla.Location(x=-186.40000000, y=-103.90000000, z=0.10000000),
            "trigger_x_tolerance": 4.0,
            "trigger_y_tolerance": 2.0,
            "trigger_direction_axis": "y",
            "trigger_direction_sign": -1,  # Richtung -y
        },
        "trigger_2_destroyBarriers": {
            "trigger_location": carla.Location(x=-116.00, y=-135.23, z=0.60000000),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": 1  # Richtung +x
        },
		"spawn_configs": [
            {
                "name": "trafficjam_car_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-60.70000000, y=-119.80000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=60.0, roll=0.0),
                ),
                "scale": None,
				"first": True,
				# "route_start_idx": 2,
				# "route": "green_right",
            },
            {
                "name": "trafficjam_car_02",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-56.90000000, y=-119.80000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=60.0, roll=0.0),
                ),
                "scale": None,
				"first": True,
            },
            {
                "name": "trafficjam_car_03",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-67.30000000, y=-126.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=40.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_04",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-67.30000000, y=-131.10000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=40.0, roll=0.0),
                ),
                "scale": None,
            },
            # --- Reihe 1 (Start bei X=-106.00, Y=-135.00) + 3 Autos (+7m auf X) ---
            {
                "name": "trafficjam_car_05",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-106.00000000, y=-135.00000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_06",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-99.00000000, y=-135.00000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_07",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-92.00000000, y=-135.00000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_08",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-85.00000000, y=-135.00000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
            # --- Reihe 2 (Start bei X=-106.00, Y=-138.70) + 3 Autos (+7m auf X) ---
            {
                "name": "trafficjam_car_09",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-106.00000000, y=-138.70000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_10",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-99.00000000, y=-138.70000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_11",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-92.00000000, y=-138.70000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_12",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-85.00000000, y=-138.70000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
    {
        "name": "trafficjamTrigger4",
        "trigger_1": {
            "trigger_location": carla.Location(x=-145.60232422, y=-2.26561096, z=0.30000000),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": -1
        },
        "trigger_2_destroyBarriers": {
            "trigger_location": carla.Location(x=-186.67, y=-13.59, z=0.60000000),
            "trigger_x_tolerance": 3.0,
            "trigger_y_tolerance": 4.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": 1  # Richtung +x
        },
		"spawn_configs": [
            # --- Reihe 1 (Start bei X=-184.80) ---
            {
                "name": "trafficjam_car_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-184.80000000, y=-72.40000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
				"first": True,
            },
            {
                "name": "trafficjam_car_02",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-184.80000000, y=-65.40000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_03",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-184.80000000, y=-58.40000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_04",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-184.80000000, y=-51.40000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_05",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-184.80000000, y=-44.40000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_06",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-184.80000000, y=-37.40000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            # --- Reihe 2 (Start bei X=-187.90) ---
            {
                "name": "trafficjam_car_07",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-187.90000000, y=-72.40000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
				"first": True,
            },
            {
                "name": "trafficjam_car_08",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-187.90000000, y=-65.40000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_09",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-187.90000000, y=-58.40000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_10",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-187.90000000, y=-51.40000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_11",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-187.90000000, y=-44.40000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_12",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-187.90000000, y=-37.40000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
	{
        "name": "trafficjamTrigger5",
		"trigger_1": {
            "trigger_location": carla.Location(x=143.92219727, y=-3.16232452, z=0.50000000),        # CORRECT
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 3.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": -1,
            },
        "trigger_2_destroyBarriers": {
                "trigger_location": carla.Location(x=105.10, y=-12.60, z=0.60000000),      # CORRECT
                "trigger_x_tolerance": 3.0,
                "trigger_y_tolerance": 5.0,
                "trigger_direction_axis": "x",
                "trigger_direction_sign": 1  # Richtung +x
            },
        "spawn_configs": [
            {
                "name": "trafficjam_car_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=54.40000000, y=-94.90000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
                "scale": None,
				"first": True,
            },
            {
                "name": "trafficjam_car_02",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=54.40000000, y=-91.30000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
                "scale": None,
				"first": True,
            },
            {
                "name": "trafficjam_car_03",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=61.50000000, y=-94.90000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_04",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=60.80000000, y=-91.30000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_05",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=68.20000000, y=-90.20000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-170.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_06",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=68.90000000, y=-93.80000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-170.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_07",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=75.90000000, y=-91.20000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-160.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_08",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=75.90000000, y=-87.50000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-160.0, roll=0.0),
                ),
                "scale": None,
            },
            # --- Reihe mit X=107.10 (Start + 4 Autos im Abstand von -7m auf Y) ---
            {
                "name": "trafficjam_car_09",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=107.10000000, y=-46.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_10",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=107.10000000, y=-53.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_11",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=107.10000000, y=-60.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_12",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=107.10000000, y=-67.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_13",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=107.10000000, y=-74.60000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            # --- Reihe mit X=103.70 (Start + 4 Autos im Abstand von -7m auf Y) ---
            {
                "name": "trafficjam_car_14",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=103.70000000, y=-46.00000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_15",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=103.70000000, y=-53.00000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
			{
                "name": "trafficjam_car_16",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=103.70000000, y=-39.00000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_17",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=103.70000000, y=-24.00000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": "trafficjam_car_18",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=103.70000000, y=-17.00000000, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
)

ROUTES_CONFIG = (
	{
		"name": "green_right",
		"route": ["Straight", "Straight", "Straight", "Right", "Straight", "Right"]
	},
	{
		"name": "green_left",
		"route": ["Straight", "Straight", "Left", "Straight", "Straight", "Straight", "Straight", "Left", "Left", "Left", "Left", "Left", "Left", "Left", "Left", "Left"]
	},
	{
		"name": "blue_right", # TODO
		"route": ["Straight", "Straight", "Straight", "Straight", "Straight", "Straight", "Straight", "Straight"]
	},
	{
		"name": "blue_extended", # TODO
		"route": ["Straight", "Right", "Straight", "Straight", "Straight", "Straight", "Straight", "Straight", "Straight", "Straight"]
	}
)

def get_start_fence_spawns():
	return list(START_FENCE_SPAWNS)

def get_static_prop_spawns(trigger_key=None):
	if trigger_key is None:
		return list(TRAFFICJAM_TRIGGER_CONFIGS)

	if trigger_key == "trafficjam":
		return list(TRAFFICJAM_TRIGGER_CONFIGS)

	return []

def get_routes():
	return list(ROUTES_CONFIG)
