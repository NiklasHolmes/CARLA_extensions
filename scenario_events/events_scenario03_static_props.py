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
                    carla.Location(x=-110.4, y=-159.4, z=0.1),
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
                    carla.Location(x=-110.4, y=51.8, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
	{
        "name": "trigger5",  
        "trigger_1": {
            "trigger_location": carla.Location(x=-102.33, y=-86.34, z=0.30),
            "trigger_x_tolerance": 2.0,
            "trigger_y_tolerance": 5.0,
            "trigger_direction_axis": "y",
            "trigger_direction_sign": 1,
        },
        "spawn_configs": [
            {
                "name": "carAway_05",
                "blueprints": ["vehicle.*"],
                "transform": carla.Transform(
                    carla.Location(x=-99.5, y=0.80, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    },
)

# Traffic lights that should be held Red when ltruck triggered.
TARGET_TL_RED = [
    {
        "name": "tl_1",
        "location": carla.Location(x=4.91, y=-229.97, z=0.18),
        "search_radius": 2.0,
        "red_hold_duration": 40.0,
    },
    {
        "name": "tl_2",     # lake
        "location": carla.Location(x=62.72, y=-9.22, z=0.07),
        "search_radius": 2.0,
        "red_hold_duration": 20.0,
    },
]

START_BARRIER_SPAWNS = (
	{
		"name": "SM_Bush01",
		"blueprints": ["static.prop.sm_bush"],
		"transform": carla.Transform(
	        carla.Location(x=-78.90, y=-113.20, z=0.10),
            carla.Rotation(pitch=0.0, yaw=-45.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush01",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-78.90, y=-113.20, z=0.90),
            carla.Rotation(pitch=0.0, yaw=-45.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush01",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-79.80, y=-110.90, z=0.10),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush01",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-79.80, y=-110.90, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush01",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-80.60, y=-108.30, z=0.10),
            carla.Rotation(pitch=0.0, yaw=-45.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush01",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-80.60, y=-108.30, z=0.90),
            carla.Rotation(pitch=0.0, yaw=-45.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush01",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-81.60, y=-105.90, z=0.10),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush01",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-81.60, y=-105.90, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush01",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-81.60, y=-104.50, z=0.10),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush01",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-81.60, y=-104.50, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush11",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-76.70, y=-100.60, z=0.10),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush12",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-76.70, y=-100.60, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush13",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-79.10, y=-100.60, z=0.10),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush14",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-79.10, y=-100.60, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush15",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-81.80, y=-100.60, z=0.10),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush16",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-81.80, y=-100.60, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush17",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-84.20, y=-100.60, z=0.10),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush18",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-84.20, y=-100.60, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush19",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-86.50, y=-100.60, z=0.10),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush20",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-86.50, y=-100.60, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },

    # Zweiter Block (inklusive des bereits vorhandenen Paars)
    {
        "name": "SM_Bush21",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-93.80, y=-69.20, z=0.10),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush22",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-93.80, y=-69.20, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush23",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-93.80, y=-66.60, z=0.10),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush24",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-93.80, y=-66.60, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush25",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-93.80, y=-64.10, z=0.10),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush26",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-93.80, y=-64.10, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush27",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-93.80, y=-61.40, z=0.10),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush28",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-93.80, y=-61.40, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush29",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-93.80, y=-58.80, z=0.10),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush30",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-93.80, y=-58.80, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },

    # Dritter Block (Bergseite)
    {
        "name": "SM_Bush31",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-110.80, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush32",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-110.80, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush33",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-108.30, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush34",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-108.30, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush35",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-105.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush36",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-105.70, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush37",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-103.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush38",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-103.70, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush39",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-68.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush40",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-68.20, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush41",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-65.70, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush42",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-65.70, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush43",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-63.10, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush44",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-63.10, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush45",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-61.10, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    {
        "name": "SM_Bush46",
        "blueprints": ["static.prop.sm_bush"],
        "transform": carla.Transform(
            carla.Location(x=-10.60, y=-61.10, z=0.90),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
	{
        "name": "tree01",
        "blueprints": ["static.prop.treepine2custom"],
        "transform": carla.Transform(
            carla.Location(x=3.9, y=-9.70, z=2.4),
            carla.Rotation(pitch=100.0, yaw=-90.0, roll=0.0),
        ),
        "scale": None,
    },
	{
        "name": "tree02",
        "blueprints": ["static.prop.treepine2custom"],
        "transform": carla.Transform(
            carla.Location(x=5.10, y=5.9, z=2.4),
            carla.Rotation(pitch=100.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
	{
        "name": "tree03",
        "blueprints": ["static.prop.treepine2custom"],
        "transform": carla.Transform(
            carla.Location(x=63.10, y=5.50, z=2.40),
            carla.Rotation(pitch=100.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
	{
        "name": "bush_wall",
        "blueprints": ["static.prop.sm_t03_wall_27"],
        "transform": carla.Transform(
            carla.Location(x=-6.8, y=-232.90, z=0.00),
            carla.Rotation(pitch=0.0, yaw=150.0, roll=0.0),
        ),
        "scale": None,
    },
	{
        "name": "bush_wall2",
        "blueprints": ["static.prop.sm_t03_wall_27"],
        "transform": carla.Transform(
            carla.Location(x=-9, y=-223.00, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
	{
        "name": "bush_wall3",
        "blueprints": ["static.prop.sm_t03_wall_27"],
        "transform": carla.Transform(
            carla.Location(x=1, y=-163.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=-10.0, roll=0.0),
        ),
        "scale": None,
    },
	{
        "name": "wooden_fence1",
        "blueprints": ["static.prop.sm_woodenfence"],
        "transform": carla.Transform(
            carla.Location(x=73.20, y=62.00, z=0.0),
            carla.Rotation(pitch=0.0, yaw=60.0, roll=0.0),
        ),
        "scale": None,
    },
	{
        "name": "wooden_fence2",
        "blueprints": ["static.prop.sm_woodenfence"],
        "transform": carla.Transform(
            carla.Location(x=67.00, y=65.600, z=0.0),
            carla.Rotation(pitch=0.0, yaw=70.0, roll=0.0),
        ),
        "scale": None,
    },
	{
        "name": "cypress_bush02",
        "blueprints": ["static.prop.sm_cypress_bush"],
        "transform": carla.Transform(
            carla.Location(x=-99.200, y=111.50, z=0.0),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
		{
        "name": "cypress_bush01",
        "blueprints": ["static.prop.sm_cypress_bush"],
        "transform": carla.Transform(
            carla.Location(x=-100.900, y=110.100, z=0.0),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
	{
        "name": "cypress_bush0",
        "blueprints": ["static.prop.sm_cypress_bush"],
        "transform": carla.Transform(
            carla.Location(x=-102.600, y=110.70, z=0.0),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
	{
        "name": "cypress_bush1",
        "blueprints": ["static.prop.sm_cypress_bush"],
        "transform": carla.Transform(
            carla.Location(x=-103.100, y=113.20, z=0.0),
            carla.Rotation(pitch=0.0, yaw=45.0, roll=0.0),
        ),
        "scale": None,
    },
		{
        "name": "cypress_bush2",
        "blueprints": ["static.prop.sm_cypress_bush"],
        "transform": carla.Transform(
            carla.Location(x=-104.00, y=115.400, z=0.0),
            carla.Rotation(pitch=0.0, yaw=45.0, roll=0.0),
        ),
        "scale": None,
    },
    	{
        "name": "cypress_bush3",
        "blueprints": ["static.prop.sm_cypress_bush"],
        "transform": carla.Transform(
            carla.Location(x=-104.80, y=117.40, z=0.0),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
		{
        "name": "cypress_bush4",
        "blueprints": ["static.prop.sm_cypress_bush"],
        "transform": carla.Transform(
            carla.Location(x=-105.70, y=119.20, z=0.0),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
        ),
        "scale": None,
    },
    	{
        "name": "cypress_bush5",
        "blueprints": ["static.prop.sm_cypress_bush"],
        "transform": carla.Transform(
            carla.Location(x=-107.100, y=121.00, z=0.0),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
        "scale": None,
    },
    # {
    #     "name": "SM_haybale01",
    #     "blueprints": ["static.prop.haybalelb"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-11.30, y=1.70, z=1.50),
    #         carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
    #     ),
    #     "scale": 2.5,
    # },
    # {
    #     "name": "SM_haybale02",
    #     "blueprints": ["static.prop.haybalelb"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-11.30, y=-1.30, z=1.50),
    #         carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
    #     ),
    #     "scale": 2.5,
    # },
    # {
    #     "name": "SM_haybale03",
    #     "blueprints": ["static.prop.haybalelb"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-11.30, y=-4.30, z=1.50),
    #         carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
    #     ),
    #     "scale": 2.5,
    # },
    # {
    #     "name": "SM_haybale04",
    #     "blueprints": ["static.prop.haybalelb"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-11.30, y=0.30, z=4.00),
    #         carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
    #     ),
    #     "scale": 2.5,
    # },
    # {
    #     "name": "SM_haybale05",
    #     "blueprints": ["static.prop.haybalelb"],
    #     "transform": carla.Transform(
    #         carla.Location(x=-11.30, y=-2.70, z=4.00),
    #         carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
    #     ),
    #     "scale": 10.5,
    # },
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

COPWAVING_TRIGGER_CONFIGS = (
    {
        "name": "copWaving_Trigger1",
        "trigger_location": carla.Location(x=-119.1000, y=-101.3000, z=0.00),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-145.500, y=-99.9000, z=0.200),
		"target_location1": carla.Location(x=-145.500, y=-95.000, z=0.20),
		"target_location2": carla.Location(x=-130.500, y=-95.000, z=0.20),
        "spawn_yaw": 0.0,
        "blueprint_id": "walker.pedestrian.0053",
		"blueprint_id_walk": "walker.pedestrian.0030"
    },
    {
        "name": "copWaving_Trigger2",
        "trigger_location": carla.Location(x=-148.00, y=-70.90, z=0.00),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-148.40, y=-92.10, z=0.200),
		"target_location1": carla.Location(x=-153.30, y=-92.10, z=0.200),
		"target_location2": carla.Location(x=-153.30, y=-77.10, z=0.200),
        "spawn_yaw": 90.0,
        "blueprint_id": "walker.pedestrian.0053",
		"blueprint_id_walk": "walker.pedestrian.0030"
    },
	{
        "name": "copWaving_Trigger3",
        "trigger_location": carla.Location(x=-102.3350, y=-86.3428, z=0.3000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-105.5000, y=-30.4000, z=0.3000),
        "target_location1": carla.Location(x=-97.30, y=-30.4000, z=0.2000),
		"target_location2": carla.Location(x=-97.30, y=-47.20, z=0.2000),
        "spawn_yaw": -90.0,
        "blueprint_id": "walker.pedestrian.0053",
        "blueprint_id_walk": "walker.pedestrian.0030"
    },
    {
        "name": "copWaving_Trigger4",
        "trigger_location": carla.Location(x=-141.4667, y=-33.3875, z=0.2000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-110.2938, y=-30.6057, z=0.2000),
        "target_location1": carla.Location(x=-110.2938, y=-38.8, z=0.2000),
		"target_location2": carla.Location(x=-123.60, y=-38.8, z=0.2000),
        "spawn_yaw": 180.0,
        "blueprint_id": "walker.pedestrian.0053",
        "blueprint_id_walk": "walker.pedestrian.0030"
    },
    {
        "name": "copWaving_Trigger5", 
        "trigger_location": carla.Location(x=-151.9533, y=-08.5505, z=0.2000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_location": carla.Location(x=-155.4001, y=40.9059, z=0.4000),
        "target_location1": carla.Location(x=-147.200, y=40.9059, z=0.2000),
		"target_location2": carla.Location(x=-147.200, y=30.80, z=0.2000),
        "spawn_yaw": -90.0,
        "blueprint_id": "walker.pedestrian.0053",
        "blueprint_id_walk": "walker.pedestrian.0030"
    },
	{
        "name": "copWaving_Trigger6",
        "trigger_location": carla.Location(x=-158.83, y=-36.62, z=0.5000),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-190.80, y=-38.80, z=0.4000),
        "target_location1": carla.Location(x=-190.80, y=-31.500, z=0.2000),
		"target_location2": carla.Location(x=-183.00, y=-31.500, z=0.2000),
        "spawn_yaw": 0.0,
        "blueprint_id": "walker.pedestrian.0053",
        "blueprint_id_walk": "walker.pedestrian.0030"
    },
	{
        "name": "copWaving_Trigger7",
        "trigger_location": carla.Location(x=-99.60, y=43.71, z=0.5000),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": -1,
        "spawn_location": carla.Location(x=-98.40, y=-10.80, z=0.4000),
        "target_location1": carla.Location(x=-104.10, y=-10.80, z=0.2000),
		"target_location2": carla.Location(x=-104.10, y=0.0, z=0.2000),
        "spawn_yaw": 90.0,
        "blueprint_id": "walker.pedestrian.0053",
        "blueprint_id_walk": "walker.pedestrian.0030"
    },
)


def get_barrier_spawn():
	return list(START_BARRIER_SPAWNS)