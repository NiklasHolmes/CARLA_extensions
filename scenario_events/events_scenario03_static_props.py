import carla

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
