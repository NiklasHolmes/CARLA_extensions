#!/usr/bin/env python

import carla

START_FENCE_SPAWNS_OLD = [
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
	# Top barrier => not used for anger
    # {
    #     "name": "fence_25",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=110.2000, y=3.4000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
    # {
    #     "name": "fence_26",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=110.2000, y=-0.4000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
    # {
    #     "name": "fence_27",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=110.2000, y=-4.2000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
    # {
    #     "name": "fence_28",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=110.2000, y=-8.0000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
    # {
    #     "name": "fence_29",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=146.6000, y=3.4000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
    # {
    #     "name": "fence_30",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=146.6000, y=-0.4000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
    # {
    #     "name": "fence_31",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=146.6000, y=-4.2000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
    # {
    #     "name": "fence_32",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=146.6000, y=-8.0000, z=0.0000),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    #     "scale": None,
    # },
	{
        "name": "fence_001",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=155.10, y=11.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=00.0, roll=0.0),
        ),
        "scale": None,
    },
	{
        "name": "fence_002",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=151.50, y=11.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
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

START_BARRIER_AVOID_HIGHWAY = [                 # same as surprise
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
    },
	{
        "name": "temp_avoidHighway_barrier_20",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=35.10, y=151.30, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
    },
	{
		"name": "temp_avoidHighway_barrier_21",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=31.60, y=151.30, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
    },
	{
        "name": "temp_avoidHighway_barrier_22",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=28.10, y=151.30, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
    },
	{
        "name": "temp_avoidHighway_barrier_23",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=24.60, y=151.30, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
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
]

TJ_TEMP_BARRIER = [
	#	Top (or right)barrier => not used for anger
    {
        "name": "tj_fence_01",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=110.2000, y=3.4000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_02",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=110.2000, y=-0.4000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_03",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=110.2000, y=-4.2000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_04",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=110.2000, y=-8.0000, z=0.0000),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    # Right (or bottom) barrier
    {
        "name": "tj_fence_09",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-119.60, y=140.10, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_10",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-123.40, y=140.10, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_11",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-127.20, y=140.10, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_12",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-131.00, y=140.10, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_13",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-134.80, y=140.10, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
    },
    # Left (or top) barrier
    {
        "name": "tj_fence_14",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-120.20, y=-131.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_15",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-124.00, y=-131.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_16",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-127.80, y=-131.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_17",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-131.60, y=-131.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_18",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-135.40, y=-131.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
    },
	# 2b barriers:
    {
        "name": "tj_fence_19",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-199.40, y=92.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_20",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-199.40, y=89.10, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_21",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-199.40, y=85.30, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_22",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-199.40, y=81.50, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_23",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-180.30, y=92.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_24",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-180.30, y=89.10, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_25",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-180.30, y=85.30, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_26",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-180.30, y=81.50, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    # 3b abrriers:
	{
        "name": "tj_fence_27",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-199.40, y=-86.00, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_28",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-199.40, y=-89.80, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_29",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-199.40, y=-93.60, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "tj_fence_30",
        "blueprints": ["static.prop.sm_fencev7"],
        "transform": carla.Transform(
            carla.Location(x=-199.40, y=-97.40, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
	# old fence:
    # {
    #     "name": "tj_fence_31",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-180.30, y=-86.00, z=0.00),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    # },
    # {
    #     "name": "tj_fence_32",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-180.30, y=-89.80, z=0.00),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    # },
    # {
    #     "name": "tj_fence_33",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-180.30, y=-93.60, z=0.00),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    # },
    # {
    #     "name": "tj_fence_34",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-180.30, y=-97.40, z=0.00),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    # },
	{
        "name": "SM_walltunnel31",
        "blueprints": ["static.prop.sm_walltunnel01"],
        "transform": carla.Transform(
            carla.Location(x=-177.88, y=-72.02, z=6.11),
            carla.Rotation(pitch=180.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "SM_walltunnel32",
        "blueprints": ["static.prop.sm_walltunnel01"],
        "transform": carla.Transform(
            carla.Location(x=-177.88, y=-79.52, z=6.11),
            carla.Rotation(pitch=180.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "SM_walltunnel33",
        "blueprints": ["static.prop.sm_walltunnel01"],
        "transform": carla.Transform(
            carla.Location(x=-177.88, y=-87.02, z=6.11),
            carla.Rotation(pitch=180.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "SM_walltunnel34",
        "blueprints": ["static.prop.sm_walltunnel01"],
        "transform": carla.Transform(
            carla.Location(x=-177.88, y=-92.22, z=6.11),
            carla.Rotation(pitch=180.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "SM_walltunnel35",
        "blueprints": ["static.prop.sm_walltunnel01"],
        "transform": carla.Transform(
            carla.Location(x=-177.78, y=-99.82, z=6.11),
            carla.Rotation(pitch=180.0, yaw=180.0, roll=0.0),
        ),
    },
    {
        "name": "SM_walltunnel36",
        "blueprints": ["static.prop.sm_walltunnel01"],
        "transform": carla.Transform(
            carla.Location(x=-170.28, y=-99.82, z=6.11),
            carla.Rotation(pitch=180.0, yaw=180.0, roll=0.0),
        ),
    },
]

TJ_TEMP_BARRIER_TRIGGER6 = {
    "trigger_6_barrier": [
        {
            "name": "tj_wall_trigger6_01",
            "blueprints": ["static.prop.sm_wall13"],
            "transform": carla.Transform(
                carla.Location(x=-280.30, y=12.60, z=0.000000),
                carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
            ),
        },
        {
            "name": "tj_wall_trigger6_02",
            "blueprints": ["static.prop.sm_wall13"],
            "transform": carla.Transform(
                carla.Location(x=-274.90, y=12.60, z=0.000000),
                carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
            ),
        },
        {
            "name": "tj_wall_trigger6_03",
            "blueprints": ["static.prop.sm_wall13"],
            "transform": carla.Transform(
                carla.Location(x=-269.50, y=12.60, z=0.000000),
                carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
            ),
        },
		{
            "name": "tj_wall_trigger6_04",
            "blueprints": ["static.prop.sm_wall13"],
            "transform": carla.Transform(
                carla.Location(x=-264.10, y=12.60, z=0.000000),
                carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
            ),
        },
    ],
    "trigger_6b_barrier": [
        {
            "name": "tj_wall_trigger6b_05",
            "blueprints": ["static.prop.sm_wall13"],
            "transform": carla.Transform(
                carla.Location(x=-280.30, y=-8.50, z=0.000000),
                carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
            ),
        },
        {
            "name": "tj_wall_trigger6b_06",
            "blueprints": ["static.prop.sm_wall13"],
            "transform": carla.Transform(
                carla.Location(x=-274.90, y=-8.50, z=0.000000),
                carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
            ),
        },
        {
            "name": "tj_wall_trigger6b_07",
            "blueprints": ["static.prop.sm_wall13"],
            "transform": carla.Transform(
                carla.Location(x=-269.50, y=-8.50, z=0.000000),
                carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
            ),
        },
		{
            "name": "tj_wall_trigger6b_05",
            "blueprints": ["static.prop.sm_wall13"],
            "transform": carla.Transform(
                carla.Location(x=-264.10, y=-8.50, z=0.000000),
                carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
            ),
        },
    ],
}

	# bottom (or left) barrier:
    # {
    #     "name": "tj_fence_05",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-261.70, y=-6.60, z=0.00),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    # },
    # {
    #     "name": "tj_fence_06",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-261.70, y=-2.80, z=0.00),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    # },
    # {
    #     "name": "tj_fence_07",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-261.70, y=1.00, z=0.00),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    # },
    # {
    #     "name": "tj_fence_08",
    #     "blueprints": ["static.prop.sm_fencev7"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-261.70, y=4.80, z=0.00),
    #         carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
    #     ),
    # },

TRAFFICJAM_TRIGGER_CONFIGS = (
    {
		"name": "trafficjamTrigger_2",     # L
        "trigger_1": {
            "trigger_location": carla.Location(x=-193.00, y=100.80, z=0.40000000),
            "trigger_x_tolerance": 5.0,
            "trigger_y_tolerance": 2.0,
            "trigger_direction_axis": "y",
            "trigger_direction_sign": 1,
        },
        "trigger_2_destroyBarriers": {
            "trigger_location": carla.Location(x=-113.53, y=153.07, z=0.60000000),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": 1  # Richtung +x
        },
		"traffic_light_position":  {
        "name": "tl_2",
        "location": carla.Location(x=-37.45, y=78.00, z=0.00),
        "search_radius": 2.0,
        # "red_hold_duration": 20.0,
        },
		"spawn_configs": [
            {
                "name": "trafficjam_car_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-43.70, y=112.1, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
				"first": True,
            },
			{
                "name": "trafficjam_car_02",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-44.6, y=118.3, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
            },
			{
                "name": "trafficjam_car_02",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-47.3, y=112.1, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
				"first": True,
            },
			{
                "name": "trafficjam_car_02",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-48.20, y=118.3, z=0.10000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
            },
			{
                "name": "trafficjam_car_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-107.92, y=151.17, z=0.50000000),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
			{
                "name": "trafficjam_car_27",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-101.92, y=151.17, z=0.50),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_28",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-95.92, y=151.17, z=0.50),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_29",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-89.92, y=151.17, z=0.50),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_30",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-83.92, y=151.17, z=0.50),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
			# 2nd row
			{
                "name": "trafficjam_car_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-107.92, y=154.67, z=0.50000000),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
			{
                "name": "trafficjam_car_31",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-101.92, y=154.67, z=0.50),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_32",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-95.92, y=154.67, z=0.50),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_33",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-89.92, y=154.67, z=0.50),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_34",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-83.92, y=154.67, z=0.50),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
		],
	},
    {
		"name": "trafficjamTrigger_2b",     # L
        "trigger_1": {
            "trigger_location": carla.Location(x=-52.7, y=102.27, z=0.40000000),
            "trigger_x_tolerance": 5.0,
            "trigger_y_tolerance": 2.0,
            "trigger_direction_axis": "y",
            "trigger_direction_sign": 1,
        },
        "trigger_2_destroyBarriers": {
            "trigger_location": carla.Location(x=-139.01, y=145.57, z=0.60000000),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": -1  # Richtung +x
        },
		"traffic_light_position":  {
        "name": "tl_2b",
        "location": carla.Location(x=-179.25, y=-9.70, z=0.00),
        "search_radius": 2.0,
        },
		"spawn_configs": [
            {
                "name": "trafficjam_car_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-184.56, y=23.62, z=0.60000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "first": True,
            },
			{
                "name": "trafficjam_car_15",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-184.56, y=29.62, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_16",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-184.56, y=35.62, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_17",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-184.56, y=41.62, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_18",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-184.56, y=47.62, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_19",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-184.56, y=53.62, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_20",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-184.56, y=59.62, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
            },
			# 2nd row
			{
                "name": "trafficjam_car_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-188.06, y=23.62, z=0.60000000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
				"first": True,
            },
			{
                "name": "trafficjam_car_21",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-188.06, y=29.62, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_22",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-188.06, y=35.62, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_23",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-188.06, y=41.62, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_24",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-188.06, y=47.62, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_25",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-188.06, y=53.62, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_26",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-188.06, y=59.62, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
            },
		],
	},
	{
        "name": "trafficjamTrigger_3",      #LC
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
		"traffic_light_position":  {
        "name": "tl_3",
        "location": carla.Location(x=-61.15, y=-78.10, z=0.00),
        "search_radius": 2.0,
        # "red_hold_duration": 20.0,
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
		"name": "trafficjamTrigger_3b",     # L
        "trigger_1": {
            "trigger_location": carla.Location(x=-46.5559, y=-104.2830, z=0.40000000),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 4.0,
            "trigger_direction_axis": "y",
            "trigger_direction_sign": -1,
        },
        "trigger_2_destroyBarriers": {
            "trigger_location": carla.Location(x=-143.50, y=-143.89, z=0.60000000),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": -1  # Richtung +x
        },
		"traffic_light_position":  {
        "name": "tl_3b",
        "location": carla.Location(x=-201.55, y=12.45, z=0.00),
        "search_radius": 2.0,
        },
		"spawn_configs": [
            {
                "name": "trafficjam_car_02",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-195.20, y=-27.49, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
				"first": True,
            },
            {
                "name": "trafficjam_car_03",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-195.20, y=-33.49, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_04",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-195.20, y=-39.49, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_05",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-195.20, y=-45.49, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_06",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-195.20, y=-51.49, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_07",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-195.20, y=-57.49, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
            # 2nd row
            {
                "name": "trafficjam_car_09",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-191.50, y=-27.49, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
				"first": True,
            },
            {
                "name": "trafficjam_car_10",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-191.50, y=-33.49, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_11",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-191.50, y=-39.49, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_12",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-191.50, y=-45.49, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_13",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-191.50, y=-51.49, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_14",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-191.50, y=-57.49, z=0.60),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
        ],
	},
	{
        "name": "trafficjamTrigger_5",    # L
		"trigger_1": {
            "trigger_location": carla.Location(x=43.38, y=-85.79, z=0.30000000),        # CORRECT
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": 1,
            },
        "trigger_2_destroyBarriers": {
                "trigger_location": carla.Location(x=98.00, y=10.40, z=0.60000000),      # CORRECT
                "trigger_x_tolerance": 5.0,
                "trigger_y_tolerance": 2.0,
                "trigger_direction_axis": "y",
                "trigger_direction_sign": 1
            },
		"traffic_light_position":  {
        "name": "tl_5",
        "location": carla.Location(x=18.60, y=79.75, z=0.00),
        "search_radius": 2.0,
        # "red_hold_duration": 20.0,
        },
        "spawn_configs": [
			{
                "name": "trafficjam_car_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=51.10, y=84.90, z=0.30000000),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
				"first": True,
            },
			{
                "name": "trafficjam_car_35",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=57.10, y=84.90, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_36",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=63.10, y=83.90, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_37",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=69.10, y=83.90, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_38",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=75.10, y=82.90, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
            },
			{
                "name": "trafficjam_car_02",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=51.10, y=88.10, z=0.30000000),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
				"first": True,
            },
			{
                "name": "trafficjam_car_39",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=57.10, y=88.10, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_40",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=63.10, y=88.10, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_41",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=69.10, y=88.10, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_42",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=75.10, y=88.10, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0),
                ),
            },
			{
                "name": "trafficjam_car_43",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=96.40, y=15.60, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_44",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=96.40, y=21.60, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_45",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=96.40, y=27.60, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
			#2nd row:
            {
                "name": "trafficjam_car_46",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=99.80, y=15.60, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_47",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=99.80, y=21.60, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_48",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=99.80, y=27.60, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
                ),
            },
        ]
    },
	{
        "name": "trafficjamTrigger_5b",    # L
		"trigger_1": {
            "trigger_location": carla.Location(x=41.80, y=93.85, z=0.30000000),        # CORRECT
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": 1,
            },
        "trigger_2_destroyBarriers": {
                "trigger_location": carla.Location(x=105.10, y=-10.70, z=0.60000000),      # CORRECT
                "trigger_x_tolerance": 3.0,
                "trigger_y_tolerance": 5.0,
                "trigger_direction_axis": "y",
                "trigger_direction_sign": -1
            },
		"traffic_light_position":  {
        "name": "tl_5b",
        "location": carla.Location(x=20.25, y=-99.90, z=0.00),
        "search_radius": 2.0,
        # "red_hold_duration": 20.0,
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
    {
		"name": "trafficjamTrigger_6",     # L
        "trigger_1": {
            "trigger_location": carla.Location(x=-204.20, y=-93.50, z=0.40000000),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": -1,
        },
        "trigger_2_destroyBarriers": {
            "trigger_location": carla.Location(x=-260.50, y=5.10, z=0.40000000),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": 1  # Richtung +x
        },
		"traffic_light_position":  {
        "name": "tl_6_6b",
        "location": carla.Location(x=-179.35, y=12.45, z=0.00),
        "search_radius": 2.0,
        },
		"spawn_configs": [
            {
                "name": "trafficjam_car_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-209.40, y=6.70, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
				"first": True,
            },
			{
                "name": "trafficjam_car_02",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-215.40, y=6.70, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_03",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-221.40, y=6.70, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_04",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-227.40, y=6.70, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_05",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-233.40, y=6.70, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_06",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-239.40, y=6.70, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
			# 2nd row
            {
                "name": "trafficjam_car_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-209.40, y=3.00, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
				"first": True,
            },
			{
                "name": "trafficjam_car_02", # Suffix '_b' zur Unterscheidung der Spur
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-215.40, y=3.00, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_03",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-221.40, y=3.00, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_04",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-227.40, y=3.00, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_05",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-233.40, y=3.00, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_06",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-239.40, y=3.00, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
		],
	},
	{
		"name": "trafficjamTrigger_6b",     # L
        "trigger_1": {
            "trigger_location": carla.Location(x=-203.70, y=86.00, z=0.40000000),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": -1,
        },
        "trigger_2_destroyBarriers": {
            "trigger_location": carla.Location(x=-260.50, y=5.10, z=0.40000000),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": 1  # Richtung +x
        },
		"traffic_light_position":  {
        "name": "tl_6_6b",
        "location": carla.Location(x=-179.35, y=12.45, z=0.00),
        "search_radius": 2.0,
        },
		"spawn_configs": [
            {
                "name": "trafficjam_car_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-209.40, y=6.70, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
				"first": True,
            },
			{
                "name": "trafficjam_car_02",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-215.40, y=6.70, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_03",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-221.40, y=6.70, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_04",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-227.40, y=6.70, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_05",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-233.40, y=6.70, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_06",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-239.40, y=6.70, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
			# 2nd row
            {
                "name": "trafficjam_car_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-209.40, y=3.00, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
				"first": True,
            },
			{
                "name": "trafficjam_car_02", # Suffix '_b' zur Unterscheidung der Spur
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-215.40, y=3.00, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_03",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-221.40, y=3.00, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_04",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-227.40, y=3.00, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_05",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-233.40, y=3.00, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
            },
            {
                "name": "trafficjam_car_06",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-239.40, y=3.00, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
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

def get_start_barriers():
	return list(START_FENCE_SPAWNS + START_BARRIER_AVOID_HIGHWAY)

def get_static_prop_spawns(trigger_key=None):
	if trigger_key is None:
		return list(TRAFFICJAM_TRIGGER_CONFIGS)

	if trigger_key == "trafficjam":
		return list(TRAFFICJAM_TRIGGER_CONFIGS)

	return []

def get_routes():
	return list(ROUTES_CONFIG)
