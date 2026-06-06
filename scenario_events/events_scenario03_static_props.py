import carla

CARAWAY = (
    {
        "name": "trigger1",  
        "trigger_1": {
            "trigger_location": carla.Location(x=-1.0, y=-116.6, z=0.0),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "y",
            "trigger_direction_sign": -1,
        },
        "spawn_configs": [
            {
                "name": "carAway_01",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-184.4, y=-159.4, z=0.1),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
    {
        "name": "trigger2",  
        "trigger_1": {
            "trigger_location": carla.Location(x=-56.1, y=-158.1, z=0.1),
            "trigger_x_tolerance": 5.0,
            "trigger_y_tolerance": 2.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": 1,
        },
        "spawn_configs": [
            {
                "name": "carAway_02",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-2.3, y=46.7, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
    {
        "name": "trigger3",  
        "trigger_1": {
            "trigger_location": carla.Location(x=-173.9, y=-162.9, z=0.1),
            "trigger_x_tolerance": 5.0,
            "trigger_y_tolerance": 2.0,
            "trigger_direction_axis": "x",
            "trigger_direction_sign": -1,
        },
        "spawn_configs": [
            {
                "name": "carAway_03",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-199.9, y=37.1, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
    {
        "name": "trigger4",  
        "trigger_1": {
            "trigger_location": carla.Location(x=-5.9, y=36.0, z=0.0),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "y",
            "trigger_direction_sign": 1,
        },
        "spawn_configs": [
            {
                "name": "carAway_04",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-186.4, y=51.8, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
)

START_BARRIER_SPAWNS = (
	{
		"name": "SM_Bush",
		"blueprints": ["static.prop.sm_bush"],
		"transform": carla.Transform(
	        carla.Location(x=-78.90, y=-113.20, z=0.10),
            carla.Rotation(pitch=0.0, yaw=-45.0, roll=0.0),
        ),
        "scale": None,
    },
	{
		"name": "SM_haybale",
		"blueprints": ["static.prop.sm_bush"],
		"transform": carla.Transform(
	        carla.Location(x=-78.90, y=-113.20, z=0.90),
            carla.Rotation(pitch=0.0, yaw=-45.0, roll=0.0),
        ),
        "scale": None,
    },
	{
		"name": "SM_haybale",
		"blueprints": ["static.prop.haybalelb"],
		"transform": carla.Transform(
	        carla.Location(x=-82.90, y=-113.20, z=0.10),
            carla.Rotation(pitch=0.0, yaw=-45.0, roll=0.0),
        ),
        "scale": None,
    },
)

TEMP_BARRIER_FIRETRUCK = (
    {
        "name": "trigger_destroy_firetruck",  
        "trigger_1": {
            "trigger_location": carla.Location(x=-102.5, y=-34.7, z=0.3),
            "trigger_x_tolerance": 70.0,
            "trigger_y_tolerance": 70.0,
        },
        "spawn_configs": [
            {
                "name": "firetruck_01",
                "blueprints": ["vehicle.carlamotors.firetruck"],
                "transform": carla.Transform(
                    carla.Location(x=0.4, y=59.8, z=0.1),
                    carla.Rotation(pitch=0.0, yaw=120.0, roll=0.0),
                ),
                "scale": None,
                "immobilize_vehicle": True,
            },
            {
                "name": "firetruck_02",         # Windrad
                "blueprints": ["vehicle.carlamotors.firetruck"],
                "transform": carla.Transform(
                    carla.Location(x=-198.8, y=-165.8, z=0.05),
                    carla.Rotation(pitch=0.0, yaw=-20.0, roll=0.0),
                ),
                "scale": None,
                "immobilize_vehicle": True,
            },
        ],
    },
)

LTRUCK_SPAWN_CONFIGS = (
    {
        "name": "ltruckTrigger1",
        "trigger_location": carla.Location(x=73.54, y=57.75, z=0.30),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": 1,
        "trigger_direction_axis_2": "y",
        "trigger_direction_sign_2": -1,
        "spawn_configs": [
            {
                "name": "ltruck_spawn_1",
                "blueprints": ["vehicle.mitsubishi.fusorosa"],             # or vehicle.carlamotors.european_hgv
                "transform": carla.Transform(
                    carla.Location(x=33.15, y=63.71, z=0.30),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
                "color": "255,255,255",
                "audio_mode": "horn_only",
            },
        ],
    },
    {
        "name": "ltruckTrigger2",
        "trigger_location": carla.Location(x=-176.38, y=-245.38, z=1.21),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "spawn_configs": [
            {
                "name": "ltruck_spawn_2",
                "blueprints": ["vehicle.mitsubishi.fusorosa"],             # or vehicle.carlamotors.european_hgv
                "transform": carla.Transform(
                    carla.Location(x=-190.49, y=-241.71, z=1.40),
                    carla.Rotation(pitch=0.0, yaw=-30.0, roll=0.0),
                ),
                "scale": None,
                "color": "255,255,255",
                "audio_mode": "horn_only",
            },
        ],
    },
)

# Trigger-Konfigurationen für stehende Pedestrians (z.B. copWaving) beim police trigger
COPWAVING_TRIGGER_CONFIGS = (
    {
        "name": "copWaving_Trigger1",
        "trigger_location": carla.Location(x=-122.1000, y=-101.3000, z=0.00),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-148.4000, y=-100.9000, z=0.200),
        "spawn_yaw": 0.0,
        "blueprint_id": "walker.pedestrian.0053",
    },
    {
        "name": "copWaving_Trigger2",
        "trigger_location": carla.Location(x=-148.00, y=-70.90, z=0.00),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-148.40, y=-92.10, z=0.200),
        "spawn_yaw": 0.0,
        "blueprint_id": "walker.pedestrian.0053",
    },
)


def get_barrier_spawn():
	return list(START_BARRIER_SPAWNS)