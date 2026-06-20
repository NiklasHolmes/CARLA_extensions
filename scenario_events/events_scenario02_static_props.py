#!/usr/bin/env python

import carla

START_BARRIER_SPAWNS = [
    {
        "name": "barrier01",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=346.30, y=-1.60, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "barrier02",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=346.30, y=2.0, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "barrier03",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=346.30, y=326.60, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
    {
        "name": "barrier04",
        "blueprints": ["static.prop.streetbarrier"],
        "transform": carla.Transform(
            carla.Location(x=346.30, y=330.20, z=0.00),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0),
        ),
    },
]

def get_start_barrier_spawns():
    return START_BARRIER_SPAWNS # + SECFENCE_YELLOW_SPAWNS


# SECFENCE_YELLOW_SPAWNS = [
#     {
#         "name": f"secfence_yellow_{index + 1:02d}",
#         "blueprints": ["static.prop.secfence_yellow"],
#         "transform": carla.Transform(
#             carla.Location(x=-11.10, y=-29.50 + (3.4 * index), z=0.00),
#             carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
#         ),
#         "scale": None,
#     }
#     for index in range(100)
# ]


TRAFFIC_ROUTE_CONFIGS = [
    {
        "name": "route1",
        "waypoints": [
            carla.Location(x=12.64985229, y=346.27230469, z=1.0),
            carla.Location(x=12.00188477, y=227.40572266, z=1.3),
            carla.Location(x=4.24975647, y=162.37706055, z=1.3),
            carla.Location(x=2.82100555, y=125.16694336, z=1.3),
            carla.Location(x=2.32962250, y=20.50780273, z=1.3),
            carla.Location(x=2.69918793, y=-34.87793457, z=1.3),
            carla.Location(x=-4.87654449, y=-98.48838867, z=1.3),
            carla.Location(x=-5.64858459, y=17.21485352, z=1.3),
            carla.Location(x=-5.51978516, y=110.24966797, z=1.3),
            carla.Location(x=-7.26356262, y=162.45070312, z=1.3),
            carla.Location(x=-2.43586609, y=263.16437500, z=1.3),
            carla.Location(x=-1220.000000, y=-6460.000000, z=0.000000),
        ],
    },
    {"name": "route2", "waypoints": []},
    {"name": "route3", "waypoints": []},
    {"name": "route4", "waypoints": []},
    {"name": "route5", "waypoints": []},
]


def get_traffic_route_configs():
    return TRAFFIC_ROUTE_CONFIGS

DESTROY_ZONE = (
    {
        "name": "destroytrigger",
        "trigger_location": carla.Location(x=-16, y=115, z=0.50),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 150.0,
    }
)

def get_destroy_zone_config():
    return DESTROY_ZONE

TRASH_TRIGGER_CONFIG = [
    {
        "name": "trashtrigger01",
        "trigger_location": carla.Location(x=335.80, y=3.00, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 7.0,
    },
    {
        "name": "trashtrigger02",
        "trigger_location": carla.Location(x=3.300, y=3.00, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 7.0,
    },
    {
        "name": "trashtrigger03",
        "trigger_location": carla.Location(x=3.300, y=325.20, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 7.0,
    },
    {
        "name": "trashtrigger04",
        "trigger_location": carla.Location(x=335.80, y=325.20, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 7.0,
    },
    {
        "name": "trashtrigger05",
        "trigger_location": carla.Location(x=89.90, y=166.00, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 7.0,
    },
    {
        "name": "trashtrigger06",
        "trigger_location": carla.Location(x=335.80, y=166.00, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 7.0,
    },
]

TRASH_OBJECTS_CONFIG = [
    {
        'name': 'trash_obj_000',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=101.42, y=124.46, z=0.29),
            carla.Rotation(pitch=0.0, yaw=129.0, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_001',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=-7.4, y=45.96, z=1.18),
            carla.Rotation(pitch=0.0, yaw=39.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_002',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=99.3, y=7.59, z=0.29),
            carla.Rotation(pitch=0.0, yaw=61.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_003',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=233.42, y=204.16, z=0.1),
            carla.Rotation(pitch=0.0, yaw=147.0, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_004',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=-7.16, y=181.96, z=0.63),
            carla.Rotation(pitch=0.0, yaw=342.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_005',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=315.63, y=7.03, z=0.1),
            carla.Rotation(pitch=0.0, yaw=347.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_006',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=301.63, y=-7.27, z=0.11),
            carla.Rotation(pitch=0.0, yaw=43.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_007',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=135.39, y=64.99, z=0.1),
            carla.Rotation(pitch=0.0, yaw=137.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_008',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=313.18, y=-29.97, z=-19.13),
            carla.Rotation(pitch=0.0, yaw=137.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_009',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=-7.23, y=275.96, z=0.63),
            carla.Rotation(pitch=0.0, yaw=355.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_010',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=81.64, y=335.86, z=1.18),
            carla.Rotation(pitch=0.0, yaw=104.0, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_011',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=219.62, y=335.5, z=0.11),
            carla.Rotation(pitch=0.0, yaw=119.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_012',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=295.17, y=50.66, z=0.28),
            carla.Rotation(pitch=0.0, yaw=214.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_013',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=236.39, y=7.09, z=1.37),
            carla.Rotation(pitch=0.0, yaw=319.0, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_014',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=400.84, y=3.76, z=0.1),
            carla.Rotation(pitch=0.0, yaw=188.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_015',
        'blueprints': ['static.prop.trashcan01'],
        'transform': carla.Transform(
            carla.Location(x=7.42, y=266.26, z=0.31),
            carla.Rotation(pitch=0.0, yaw=273.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_016',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=4.28, y=148.15, z=0.6),
            carla.Rotation(pitch=0.0, yaw=311.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_017',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=273.17, y=50.64, z=1.18),
            carla.Rotation(pitch=0.0, yaw=190.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_018',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=75.78, y=334.98, z=1.34),
            carla.Rotation(pitch=0.0, yaw=344.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_019',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=42.01, y=321.72, z=0.63),
            carla.Rotation(pitch=0.0, yaw=249.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_020',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=344.13, y=14.79, z=0.64),
            carla.Rotation(pitch=0.0, yaw=0.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_021',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=239.42, y=124.43, z=0.28),
            carla.Rotation(pitch=0.0, yaw=207.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_022',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=6.99, y=277.96, z=1.18),
            carla.Rotation(pitch=0.0, yaw=160.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_023',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=97.86, y=141.71, z=0.11),
            carla.Rotation(pitch=0.0, yaw=251.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_024',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=239.62, y=321.66, z=0.28),
            carla.Rotation(pitch=0.0, yaw=143.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_025',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=97.91, y=49.55, z=2.3),
            carla.Rotation(pitch=0.0, yaw=164.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_026',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=97.78, y=13.24, z=0.64),
            carla.Rotation(pitch=0.0, yaw=72.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_027',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=189.42, y=138.63, z=1.18),
            carla.Rotation(pitch=0.0, yaw=288.0, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_028',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=-7.13, y=121.96, z=0.1),
            carla.Rotation(pitch=0.0, yaw=232.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_029',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=55.38, y=-7.2, z=0.1),
            carla.Rotation(pitch=0.0, yaw=235.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_030',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=149.27, y=35.07, z=0.29),
            carla.Rotation(pitch=0.0, yaw=345.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_031',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=358.59, y=6.94, z=0.28),
            carla.Rotation(pitch=0.0, yaw=182.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_032',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=87.59, y=-6.11, z=1.18),
            carla.Rotation(pitch=0.0, yaw=290.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_033',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=344.42, y=7.08, z=0.29),
            carla.Rotation(pitch=0.0, yaw=271.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_034',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=387.14, y=318.5, z=1.22),
            carla.Rotation(pitch=0.0, yaw=143.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_035',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=86.26, y=334.83, z=0.1),
            carla.Rotation(pitch=0.0, yaw=228.0, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_036',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=97.58, y=280.33, z=0.1),
            carla.Rotation(pitch=0.0, yaw=310.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_037',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=101.42, y=204.16, z=0.63),
            carla.Rotation(pitch=0.0, yaw=141.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_038',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=86.71, y=56.01, z=1.08),
            carla.Rotation(pitch=0.0, yaw=312.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_039',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=330.98, y=203.83, z=1.19),
            carla.Rotation(pitch=0.0, yaw=57.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_040',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=299.42, y=204.38, z=0.1),
            carla.Rotation(pitch=0.0, yaw=187.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_041',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=259.42, y=124.07, z=0.63),
            carla.Rotation(pitch=0.0, yaw=110.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_042',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=149.62, y=321.28, z=1.43),
            carla.Rotation(pitch=0.0, yaw=85.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_043',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=166.08, y=-7.25, z=1.18),
            carla.Rotation(pitch=0.0, yaw=280.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_044',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=328.23, y=7.41, z=1.18),
            carla.Rotation(pitch=0.0, yaw=230.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_045',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=7.26, y=237.96, z=0.28),
            carla.Rotation(pitch=0.0, yaw=338.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_046',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=97.84, y=29.24, z=0.1),
            carla.Rotation(pitch=0.0, yaw=322.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_047',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=329.42, y=307.16, z=0.28),
            carla.Rotation(pitch=0.0, yaw=114.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_048',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=97.48, y=169.84, z=0.09),
            carla.Rotation(pitch=0.0, yaw=153.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_049',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=103.42, y=189.67, z=0.12),
            carla.Rotation(pitch=0.0, yaw=248.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_050',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=401.8, y=284.54, z=0.11),
            carla.Rotation(pitch=0.0, yaw=237.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_051',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=295.63, y=7.38, z=1.18),
            carla.Rotation(pitch=0.0, yaw=151.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_052',
        'blueprints': ['static.prop.trashcan01'],
        'transform': carla.Transform(
            carla.Location(x=-7.38, y=7.4, z=0.29),
            carla.Rotation(pitch=0.0, yaw=182.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_053',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=257.62, y=335.63, z=0.11),
            carla.Rotation(pitch=0.0, yaw=249.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_054',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=163.42, y=138.89, z=1.18),
            carla.Rotation(pitch=0.0, yaw=100.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_055',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=362.58, y=6.84, z=0.42),
            carla.Rotation(pitch=0.0, yaw=109.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_056',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=343.91, y=320.1, z=1.18),
            carla.Rotation(pitch=0.0, yaw=14.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_057',
        'blueprints': ['static.prop.trashcan01'],
        'transform': carla.Transform(
            carla.Location(x=7.09, y=199.96, z=0.29),
            carla.Rotation(pitch=0.0, yaw=215.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_058',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=101.42, y=138.87, z=0.11),
            carla.Rotation(pitch=0.0, yaw=326.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_059',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=345.28, y=5.86, z=0.38),
            carla.Rotation(pitch=0.0, yaw=143.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_060',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=7.03, y=69.96, z=0.11),
            carla.Rotation(pitch=0.0, yaw=61.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_061',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=97.69, y=82.15, z=0.09),
            carla.Rotation(pitch=0.0, yaw=282.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_062',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=149.15, y=39.01, z=0.64),
            carla.Rotation(pitch=0.0, yaw=316.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_063',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=97.31, y=7.74, z=2.3),
            carla.Rotation(pitch=0.0, yaw=203.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_064',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=185.42, y=204.01, z=0.28),
            carla.Rotation(pitch=0.0, yaw=216.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_065',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=-7.15, y=289.96, z=0.1),
            carla.Rotation(pitch=0.0, yaw=333.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_066',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=127.42, y=189.82, z=0.1),
            carla.Rotation(pitch=0.0, yaw=223.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_067',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=219.17, y=50.43, z=0.1),
            carla.Rotation(pitch=0.0, yaw=131.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_068',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=-6.95, y=199.96, z=0.1),
            carla.Rotation(pitch=0.0, yaw=120.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_069',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=97.71, y=45.94, z=0.88),
            carla.Rotation(pitch=0.0, yaw=162.0, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_070',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=267.17, y=50.02, z=0.1),
            carla.Rotation(pitch=0.0, yaw=230.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_071',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=358.59, y=-7.38, z=0.09),
            carla.Rotation(pitch=0.0, yaw=43.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_072',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=329.55, y=189.41, z=0.63),
            carla.Rotation(pitch=0.0, yaw=260.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_073',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=281.42, y=124.11, z=0.11),
            carla.Rotation(pitch=0.0, yaw=73.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_074',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=401.38, y=266.54, z=0.1),
            carla.Rotation(pitch=0.0, yaw=301.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_075',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=213.42, y=124.53, z=0.1),
            carla.Rotation(pitch=0.0, yaw=243.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_076',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=151.62, y=335.91, z=0.11),
            carla.Rotation(pitch=0.0, yaw=227.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_077',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=163.62, y=322.75, z=0.28),
            carla.Rotation(pitch=0.0, yaw=21.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_078',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=235.62, y=321.7, z=0.09),
            carla.Rotation(pitch=0.0, yaw=311.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_079',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=349.73, y=321.73, z=0.1),
            carla.Rotation(pitch=0.0, yaw=323.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_080',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=401.23, y=152.54, z=0.1),
            carla.Rotation(pitch=0.0, yaw=248.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_081',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=117.42, y=203.96, z=0.63),
            carla.Rotation(pitch=0.0, yaw=341.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_082',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=343.6, y=273.16, z=0.1),
            carla.Rotation(pitch=0.0, yaw=118.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_083',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=83.24, y=206.33, z=0.1),
            carla.Rotation(pitch=0.0, yaw=186.0, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_084',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=204.36, y=322.98, z=0.12),
            carla.Rotation(pitch=0.0, yaw=281.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_085',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=387.11, y=228.54, z=1.18),
            carla.Rotation(pitch=0.0, yaw=62.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_086',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=148.93, y=29.02, z=0.11),
            carla.Rotation(pitch=0.0, yaw=218.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_087',
        'blueprints': ['static.prop.trashcan01'],
        'transform': carla.Transform(
            carla.Location(x=-6.15, y=324.92, z=0.29),
            carla.Rotation(pitch=0.0, yaw=226.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_088',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=401.61, y=110.54, z=0.11),
            carla.Rotation(pitch=0.0, yaw=259.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_089',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=329.95, y=109.03, z=0.1),
            carla.Rotation(pitch=0.0, yaw=138.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_090',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=97.79, y=25.25, z=0.11),
            carla.Rotation(pitch=0.0, yaw=257.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_091',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=124.96, y=7.27, z=0.1),
            carla.Rotation(pitch=0.0, yaw=102.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_092',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=249.42, y=124.65, z=0.11),
            carla.Rotation(pitch=0.0, yaw=188.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_093',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=7.29, y=9.96, z=0.28),
            carla.Rotation(pitch=0.0, yaw=265.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_094',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=74.01, y=335.77, z=0.1),
            carla.Rotation(pitch=0.0, yaw=87.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_095',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=330.94, y=319.95, z=0.58),
            carla.Rotation(pitch=0.0, yaw=139.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_096',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=223.62, y=335.93, z=0.28),
            carla.Rotation(pitch=0.0, yaw=200.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_097',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=401.41, y=260.54, z=0.09),
            carla.Rotation(pitch=0.0, yaw=93.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_098',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=386.99, y=102.54, z=1.18),
            carla.Rotation(pitch=0.0, yaw=246.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_099',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=344.25, y=136.58, z=0.1),
            carla.Rotation(pitch=0.0, yaw=251.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_100',
        'blueprints': ['static.prop.trashcan01'],
        'transform': carla.Transform(
            carla.Location(x=83.05, y=33.24, z=0.29),
            carla.Rotation(pitch=0.0, yaw=173.0, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_101',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=83.48, y=139.84, z=0.1),
            carla.Rotation(pitch=0.0, yaw=132.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_102',
        'blueprints': ['static.prop.trashcan01'],
        'transform': carla.Transform(
            carla.Location(x=263.62, y=335.82, z=0.29),
            carla.Rotation(pitch=0.0, yaw=85.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_103',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=163.42, y=190.31, z=0.28),
            carla.Rotation(pitch=0.0, yaw=114.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_104',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=83.2, y=92.15, z=0.1),
            carla.Rotation(pitch=0.0, yaw=161.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_105',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=387.15, y=200.54, z=0.63),
            carla.Rotation(pitch=0.0, yaw=139.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_106',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=44.46, y=321.45, z=0.34),
            carla.Rotation(pitch=0.0, yaw=113.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_107',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=387.28, y=276.54, z=0.1),
            carla.Rotation(pitch=0.0, yaw=252.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_108',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=5.8, y=10.43, z=0.28),
            carla.Rotation(pitch=0.0, yaw=69.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_109',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=343.63, y=203.65, z=0.11),
            carla.Rotation(pitch=0.0, yaw=242.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_110',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=401.41, y=26.55, z=0.28),
            carla.Rotation(pitch=0.0, yaw=236.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_111',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=343.18, y=46.16, z=0.14),
            carla.Rotation(pitch=0.0, yaw=62.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_112',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=97.36, y=64.61, z=0.1),
            carla.Rotation(pitch=0.0, yaw=53.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_113',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=343.81, y=7.32, z=0.11),
            carla.Rotation(pitch=0.0, yaw=14.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_114',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=97.32, y=276.33, z=0.1),
            carla.Rotation(pitch=0.0, yaw=252.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_115',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=243.62, y=335.44, z=0.1),
            carla.Rotation(pitch=0.0, yaw=76.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_116',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=101.29, y=50.42, z=1.19),
            carla.Rotation(pitch=0.0, yaw=10.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_117',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=343.65, y=307.16, z=0.28),
            carla.Rotation(pitch=0.0, yaw=190.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_118',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=13.38, y=7.35, z=0.1),
            carla.Rotation(pitch=0.0, yaw=282.0, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_119',
        'blueprints': ['static.prop.trashcan01'],
        'transform': carla.Transform(
            carla.Location(x=133.42, y=204.18, z=0.29),
            carla.Rotation(pitch=0.0, yaw=112.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_120',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=225.17, y=50.67, z=0.11),
            carla.Rotation(pitch=0.0, yaw=21.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_121',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=275.17, y=50.66, z=0.1),
            carla.Rotation(pitch=0.0, yaw=294.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_122',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=297.42, y=189.79, z=0.1),
            carla.Rotation(pitch=0.0, yaw=184.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_123',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=163.26, y=47.03, z=0.1),
            carla.Rotation(pitch=0.0, yaw=161.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_124',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=183.68, y=7.07, z=0.11),
            carla.Rotation(pitch=0.0, yaw=339.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_125',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=97.44, y=80.15, z=0.63),
            carla.Rotation(pitch=0.0, yaw=177.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_126',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=205.17, y=50.1, z=0.63),
            carla.Rotation(pitch=0.0, yaw=135.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_127',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=313.42, y=190.02, z=1.18),
            carla.Rotation(pitch=0.0, yaw=82.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_128',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=329.46, y=181.67, z=0.28),
            carla.Rotation(pitch=0.0, yaw=46.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_129',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=4.61, y=161.19, z=0.6),
            carla.Rotation(pitch=0.0, yaw=325.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_130',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=117.41, y=321.8, z=0.33),
            carla.Rotation(pitch=0.0, yaw=16.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_131',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=329.46, y=122.57, z=0.1),
            carla.Rotation(pitch=0.0, yaw=149.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_132',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=148.74, y=50.33, z=2.15),
            carla.Rotation(pitch=0.0, yaw=181.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_133',
        'blueprints': ['static.prop.trashcan01'],
        'transform': carla.Transform(
            carla.Location(x=83.4, y=17.24, z=0.29),
            carla.Rotation(pitch=0.0, yaw=267.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_134',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=83.21, y=13.24, z=0.11),
            carla.Rotation(pitch=0.0, yaw=64.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_135',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=171.63, y=6.96, z=0.29),
            carla.Rotation(pitch=0.0, yaw=300.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_136',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=343.71, y=207.65, z=0.09),
            carla.Rotation(pitch=0.0, yaw=259.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_137',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=329.28, y=139.94, z=0.29),
            carla.Rotation(pitch=0.0, yaw=10.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_138',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=163.07, y=33.03, z=0.1),
            carla.Rotation(pitch=0.0, yaw=153.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_139',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=173.62, y=335.91, z=0.63),
            carla.Rotation(pitch=0.0, yaw=248.3, roll=0.0)
        )
    },
    # {
    #     'name': 'trash_obj_140',
    #     'blueprints': ['static.prop.shoppingcart'],
    #     'transform': carla.Transform(
    #         carla.Location(x=337.93, y=45.17, z=0.36),
    #         carla.Rotation(pitch=0.0, yaw=144.0, roll=0.0)
    #     )
    # },
    {
        'name': 'trash_obj_141',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=83.28, y=135.84, z=0.1),
            carla.Rotation(pitch=0.0, yaw=66.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_142',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=97.79, y=123.3, z=1.19),
            carla.Rotation(pitch=0.0, yaw=165.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_143',
        'blueprints': ['static.prop.trashcan01'],
        'transform': carla.Transform(
            carla.Location(x=105.62, y=335.74, z=0.29),
            carla.Rotation(pitch=0.0, yaw=68.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_144',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=80.69, y=-7.23, z=0.63),
            carla.Rotation(pitch=0.0, yaw=328.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_145',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=97.82, y=155.84, z=0.1),
            carla.Rotation(pitch=0.0, yaw=103.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_146',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=401.45, y=236.54, z=0.1),
            carla.Rotation(pitch=0.0, yaw=57.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_147',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=342.11, y=198.6, z=0.28),
            carla.Rotation(pitch=0.0, yaw=337.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_148',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=387.41, y=74.53, z=0.28),
            carla.Rotation(pitch=0.0, yaw=27.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_149',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=387.21, y=152.54, z=0.1),
            carla.Rotation(pitch=0.0, yaw=270.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_150',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=267.63, y=7.42, z=0.1),
            carla.Rotation(pitch=0.0, yaw=28.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_151',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=98.36, y=124.3, z=0.12),
            carla.Rotation(pitch=0.0, yaw=297.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_152',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=329.53, y=42.79, z=0.1),
            carla.Rotation(pitch=0.0, yaw=103.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_153',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=153.66, y=63.67, z=0.11),
            carla.Rotation(pitch=0.0, yaw=31.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_154',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=-7.11, y=211.96, z=0.1),
            carla.Rotation(pitch=0.0, yaw=70.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_155',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=83.49, y=278.33, z=0.1),
            carla.Rotation(pitch=0.0, yaw=168.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_156',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=185.42, y=124.58, z=0.11),
            carla.Rotation(pitch=0.0, yaw=140.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_157',
        'blueprints': ['static.prop.trashcan01'],
        'transform': carla.Transform(
            carla.Location(x=387.19, y=24.53, z=0.29),
            carla.Rotation(pitch=0.0, yaw=32.0, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_158',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=328.41, y=189.88, z=0.1),
            carla.Rotation(pitch=0.0, yaw=197.0, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_159',
        'blueprints': ['static.prop.trashcan01'],
        'transform': carla.Transform(
            carla.Location(x=83.28, y=45.24, z=0.29),
            carla.Rotation(pitch=0.0, yaw=152.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_160',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=239.63, y=-6.99, z=0.1),
            carla.Rotation(pitch=0.0, yaw=202.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_161',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=32.01, y=321.67, z=0.1),
            carla.Rotation(pitch=0.0, yaw=274.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_162',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=351.73, y=321.78, z=0.1),
            carla.Rotation(pitch=0.0, yaw=357.0, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_163',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=7.39, y=251.96, z=0.09),
            carla.Rotation(pitch=0.0, yaw=314.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_164',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=215.42, y=124.3, z=0.63),
            carla.Rotation(pitch=0.0, yaw=322.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_165',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=-6.9, y=187.96, z=0.63),
            carla.Rotation(pitch=0.0, yaw=294.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_166',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=110.97, y=6.81, z=0.28),
            carla.Rotation(pitch=0.0, yaw=119.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_167',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=221.65, y=204.26, z=0.21),
            carla.Rotation(pitch=0.0, yaw=208.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_168',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=7.17, y=133.96, z=0.11),
            carla.Rotation(pitch=0.0, yaw=239.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_169',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=343.83, y=317.16, z=0.1),
            carla.Rotation(pitch=0.0, yaw=78.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_170',
        'blueprints': ['static.prop.trashcan03'],
        'transform': carla.Transform(
            carla.Location(x=255.63, y=7.06, z=0.28),
            carla.Rotation(pitch=0.0, yaw=19.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_171',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=99.28, y=50.56, z=0.1),
            carla.Rotation(pitch=0.0, yaw=27.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_172',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=22.01, y=335.75, z=0.1),
            carla.Rotation(pitch=0.0, yaw=123.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_173',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=95.62, y=334.9, z=0.11),
            carla.Rotation(pitch=0.0, yaw=117.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_174',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=124.96, y=-7.38, z=0.63),
            carla.Rotation(pitch=0.0, yaw=147.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_175',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=146.99, y=50.52, z=0.1),
            carla.Rotation(pitch=0.0, yaw=199.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_176',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=163.45, y=7.06, z=0.1),
            carla.Rotation(pitch=0.0, yaw=150.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_177',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=319.62, y=335.82, z=0.63),
            carla.Rotation(pitch=0.0, yaw=90.0, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_178',
        'blueprints': ['static.prop.trashcan01'],
        'transform': carla.Transform(
            carla.Location(x=305.17, y=64.6, z=0.29),
            carla.Rotation(pitch=0.0, yaw=61.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_179',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=329.84, y=273.16, z=0.1),
            carla.Rotation(pitch=0.0, yaw=83.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_180',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=-7.44, y=151.96, z=0.1),
            carla.Rotation(pitch=0.0, yaw=237.1, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_181',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=343.7, y=142.59, z=0.63),
            carla.Rotation(pitch=0.0, yaw=197.9, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_182',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=97.28, y=78.13, z=0.11),
            carla.Rotation(pitch=0.0, yaw=48.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_183',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=193.42, y=203.97, z=0.11),
            carla.Rotation(pitch=0.0, yaw=294.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_184',
        'blueprints': ['static.prop.trashcan01'],
        'transform': carla.Transform(
            carla.Location(x=97.84, y=242.33, z=0.29),
            carla.Rotation(pitch=0.0, yaw=111.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_185',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=215.63, y=7.01, z=0.11),
            carla.Rotation(pitch=0.0, yaw=113.7, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_186',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=152.08, y=-7.05, z=0.11),
            carla.Rotation(pitch=0.0, yaw=210.4, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_187',
        'blueprints': ['static.prop.garbage06'],
        'transform': carla.Transform(
            carla.Location(x=343.79, y=303.16, z=0.1),
            carla.Rotation(pitch=0.0, yaw=77.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_188',
        'blueprints': ['static.prop.shoppingcart'],
        'transform': carla.Transform(
            carla.Location(x=97.15, y=322.74, z=1.18),
            carla.Rotation(pitch=0.0, yaw=163.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_189',
        'blueprints': ['static.prop.plasticbag'],
        'transform': carla.Transform(
            carla.Location(x=83.37, y=136.92, z=0.63),
            carla.Rotation(pitch=0.0, yaw=341.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_190',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=7.78, y=319.5, z=0.11),
            carla.Rotation(pitch=0.0, yaw=270.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_191',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=329.48, y=320.13, z=0.11),
            carla.Rotation(pitch=0.0, yaw=238.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_192',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=359.73, y=335.47, z=0.1),
            carla.Rotation(pitch=0.0, yaw=121.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_193',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=343.81, y=271.16, z=0.09),
            carla.Rotation(pitch=0.0, yaw=100.6, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_194',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=6.88, y=171.96, z=0.11),
            carla.Rotation(pitch=0.0, yaw=273.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_195',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=401.29, y=180.54, z=0.11),
            carla.Rotation(pitch=0.0, yaw=258.5, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_196',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=387.12, y=56.53, z=0.11),
            carla.Rotation(pitch=0.0, yaw=95.2, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_197',
        'blueprints': ['static.prop.trashbag'],
        'transform': carla.Transform(
            carla.Location(x=161.42, y=189.75, z=0.1),
            carla.Rotation(pitch=0.0, yaw=344.3, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_198',
        'blueprints': ['static.prop.box03'],
        'transform': carla.Transform(
            carla.Location(x=243.63, y=-6.9, z=0.11),
            carla.Rotation(pitch=0.0, yaw=118.8, roll=0.0)
        )
    },
    {
        'name': 'trash_obj_199',
        'blueprints': ['static.prop.trashcan01'],
        'transform': carla.Transform(
            carla.Location(x=401.2, y=302.54, z=0.29),
            carla.Rotation(pitch=0.0, yaw=261.2, roll=0.0)
        )
    },
]

POORROAD_TRIGGER_CONFIG = (
    {
        "name": "trashtrigger01",
        "trigger_location": carla.Location(x=335.80, y=3.00, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 7.0,
    },
    {
        "name": "trashtrigger02",
        "trigger_location": carla.Location(x=3.300, y=3.00, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 7.0,
    },
    {
        "name": "trashtrigger03",
        "trigger_location": carla.Location(x=3.300, y=325.20, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 7.0,
    },
    {
        "name": "trashtrigger04",
        "trigger_location": carla.Location(x=335.80, y=325.20, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 7.0,
    },
    {
        "name": "trashtrigger05",
        "trigger_location": carla.Location(x=89.90, y=166.00, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 7.0,
    },
    {
        "name": "trashtrigger06",
        "trigger_location": carla.Location(x=335.80, y=166.00, z=0.30),
        "trigger_x_tolerance": 7.0,
        "trigger_y_tolerance": 7.0,
    },
)

POORROAD_OBJECTS_CONFIG = [
    {
        'name': 'poorroad_obj_000',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=352.59, y=-2.03, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=155.2, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_001',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=62.01, y=326.18, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=44.2, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_002',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=335.72, y=303.16, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=296.1, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_003',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=93.13, y=206.33, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=137.7, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_004',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=231.17, y=55.56, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=38.4, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_005',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=88.87, y=135.84, z=0.01),
            carla.Rotation(pitch=0.0, yaw=114.6, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_006',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=93.21, y=292.33, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=173.3, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_007',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=321.62, y=330.5, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=145.5, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_008',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=336.35, y=58.25, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=176.3, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_009',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=339.69, y=215.16, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=237.0, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_010',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=-2.0, y=151.96, z=0.01),
            carla.Rotation(pitch=0.0, yaw=221.7, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_011',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=377.73, y=329.94, z=0.01),
            carla.Rotation(pitch=0.0, yaw=299.8, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_012',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=285.42, y=129.21, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=354.3, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_013',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=94.71, y=3.72, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=247.1, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_014',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=59.38, y=-2.46, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=242.5, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_015',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=223.42, y=133.9, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=86.9, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_016',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=317.42, y=133.73, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=330.7, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_017',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=205.17, y=54.65, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=224.1, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_018',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=339.5, y=151.67, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=51.2, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_019',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=299.62, y=330.69, z=0.01),
            carla.Rotation(pitch=0.0, yaw=319.7, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_020',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=247.62, y=330.63, z=0.01),
            carla.Rotation(pitch=0.0, yaw=108.8, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_021',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=93.27, y=280.33, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=212.7, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_022',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=-1.58, y=53.96, z=0.01),
            carla.Rotation(pitch=0.0, yaw=30.4, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_023',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=273.42, y=198.25, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=22.3, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_024',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=395.97, y=162.54, z=0.01),
            carla.Rotation(pitch=0.0, yaw=356.5, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_025',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=89.13, y=218.33, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=136.3, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_026',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=52.01, y=330.15, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=181.5, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_027',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=271.42, y=129.81, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=53.9, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_028',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=213.63, y=1.09, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=324.2, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_029',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=338.2, y=219.16, z=0.01),
            carla.Rotation(pitch=0.0, yaw=183.1, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_030',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=335.72, y=330.48, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=265.2, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_031',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=332.94, y=54.63, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=247.2, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_032',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=92.72, y=8.18, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=203.8, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_033',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=156.19, y=0.83, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=243.1, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_034',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=331.67, y=56.5, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=14.7, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_035',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=79.64, y=330.33, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=264.5, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_036',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=139.42, y=133.46, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=270.2, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_037',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=197.42, y=130.25, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=211.8, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_038',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=91.42, y=186.33, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=188.3, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_039',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=339.67, y=263.16, z=0.01),
            carla.Rotation(pitch=0.0, yaw=265.0, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_040',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=152.99, y=55.11, z=0.01),
            carla.Rotation(pitch=0.0, yaw=282.4, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_041',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=90.66, y=59.29, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=15.9, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_042',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=150.99, y=54.86, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=232.1, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_043',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=173.62, y=325.84, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=143.7, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_044',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=396.68, y=108.54, z=0.01),
            carla.Rotation(pitch=0.0, yaw=25.0, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_045',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=223.62, y=329.76, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=304.1, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_046',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=338.42, y=251.16, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=343.3, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_047',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=347.47, y=325.89, z=0.01),
            carla.Rotation(pitch=0.0, yaw=191.4, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_048',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=396.96, y=242.54, z=0.01),
            carla.Rotation(pitch=0.0, yaw=252.4, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_049',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=392.06, y=282.54, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=105.4, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_050',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=88.24, y=320.7, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=21.8, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_051',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=88.45, y=190.64, z=0.01),
            carla.Rotation(pitch=0.0, yaw=348.1, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_052',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=396.89, y=14.54, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=134.0, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_053',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=201.42, y=195.57, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=2.1, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_054',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=-2.77, y=301.96, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=77.3, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_055',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=195.42, y=198.6, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=353.2, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_056',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=245.63, y=-2.72, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=136.3, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_057',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=361.73, y=330.03, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=148.5, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_058',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=92.17, y=220.33, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=158.6, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_059',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=339.55, y=107.03, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=145.6, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_060',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=338.71, y=231.16, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=112.9, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_061',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=191.42, y=133.41, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=97.0, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_062',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=79.38, y=2.26, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=86.2, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_063',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=89.13, y=15.24, z=0.01),
            carla.Rotation(pitch=0.0, yaw=38.9, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_064',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=391.32, y=128.54, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=44.3, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_065',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=46.01, y=330.48, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=255.9, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_066',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=396.14, y=264.54, z=0.01),
            carla.Rotation(pitch=0.0, yaw=199.6, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_067',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=2.4, y=27.96, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=203.2, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_068',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=197.42, y=133.29, z=0.01),
            carla.Rotation(pitch=0.0, yaw=165.4, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_069',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=86.69, y=-1.19, z=0.01),
            carla.Rotation(pitch=0.0, yaw=66.2, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_070',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=101.62, y=326.04, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=99.6, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_071',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=261.63, y=-1.38, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=112.2, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_072',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=147.42, y=134.01, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=189.8, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_073',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=193.17, y=55.12, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=179.0, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_074',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=241.63, y=1.74, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=174.0, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_075',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=225.42, y=129.83, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=47.5, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_076',
        'blueprints': ['static.prop.ironplank'],
        'transform': carla.Transform(
            carla.Location(x=309.42, y=194.57, z=0.01),
            carla.Rotation(pitch=0.0, yaw=218.2, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_077',
        'blueprints': ['static.prop.dirtdebris01'],
        'transform': carla.Transform(
            carla.Location(x=91.69, y=110.15, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=61.9, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_078',
        'blueprints': ['static.prop.dirtdebris02'],
        'transform': carla.Transform(
            carla.Location(x=391.32, y=206.54, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=226.5, roll=0.0)
        )
    },
    {
        'name': 'poorroad_obj_079',
        'blueprints': ['static.prop.dirtdebris03'],
        'transform': carla.Transform(
            carla.Location(x=54.01, y=330.12, z=-0.02),
            carla.Rotation(pitch=0.0, yaw=165.2, roll=0.0)
        )
    },
]

SNAKE_TRIGGER_TOLERANCE_X = 5.0
SNAKE_TRIGGER_TOLERANCE_Y = 10.0
SNAKE_TRIGGER_DIRECTION_AXIS = "x"
SNAKE_TRIGGER_DIRECTION_SIGN = 1
SNAKE_SPAWN_X_OFFSET = 49.80
SNAKE_SPAWN_Y_OFFSET = 11.10
SNAKE_SPAWN_Z_OFFSET = 1.80
SNAKE_TARGET_Y = -19.50
DRIVERTRASH_SPAWN_X_OFFSET = -30.0
DRIVERTRASH_SPAWN_Y_OFFSET = 0.0
DRIVERTRASH_SPAWN_Z = 1.50

def _build_snake_config(index, trigger_location):
    spawn_location = carla.Location(
        x=trigger_location.x + SNAKE_SPAWN_X_OFFSET,
        y=trigger_location.y + SNAKE_SPAWN_Y_OFFSET,
        z=trigger_location.z + SNAKE_SPAWN_Z_OFFSET,
    )
    target_location = carla.Location(
        x=spawn_location.x,
        y=SNAKE_TARGET_Y,
        z=spawn_location.z,
    )
    return {
        "name": f"snakeTrigger{index}",
        "trigger_location": trigger_location,
        "trigger_x_tolerance": SNAKE_TRIGGER_TOLERANCE_X,
        "trigger_y_tolerance": SNAKE_TRIGGER_TOLERANCE_Y,
        "trigger_direction_axis": SNAKE_TRIGGER_DIRECTION_AXIS,
        "trigger_direction_sign": SNAKE_TRIGGER_DIRECTION_SIGN,
        "spawn_configs": [
            {
                "name": f"snake_start_{index:02d}",
                "transform": carla.Transform(
                    spawn_location,
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
            {
                "name": f"snake_end_{index:02d}",
                "transform": carla.Transform(
                    target_location,
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0),
                ),
                "scale": None,
            },
        ],
    }

SNAKE_AND_DRIVERTRASH_TRIGGER_LOCATIONS = (
    # first lane
    carla.Location(x=114.6000, y=244.5000, z=0.3000),
    carla.Location(x=176.7000, y=244.5000, z=0.3000),
    carla.Location(x=308.6000, y=244.5000, z=0.0000),
    carla.Location(x=442.4000, y=244.5000, z=0.0000),
    carla.Location(x=517.6000, y=244.5000, z=0.0000),

    carla.Location(x=114.6000, y=141.5000, z=0.3000),
    carla.Location(x=176.7000, y=141.5000, z=0.3000),
    carla.Location(x=308.6000, y=141.5000, z=0.0000),
    carla.Location(x=442.4000, y=141.5000, z=0.0000),
    carla.Location(x=517.6000, y=141.5000, z=0.0000),

    carla.Location(x=114.6000, y=41.9000, z=0.3000),
    carla.Location(x=176.7000, y=41.9000, z=0.3000),
    carla.Location(x=308.6000, y=41.9000, z=0.0000),
    carla.Location(x=442.4000, y=41.9000, z=0.0000),
    carla.Location(x=517.6000, y=41.9000, z=0.0000),
)

# Backwards-compatible alias while all route generation uses the shared list.
SNAKE_TRIGGER_LOCATIONS = SNAKE_AND_DRIVERTRASH_TRIGGER_LOCATIONS

SNAKE_CONFIGS = tuple(
    _build_snake_config(index + 1, trigger_location)
    for index, trigger_location in enumerate(SNAKE_AND_DRIVERTRASH_TRIGGER_LOCATIONS)
)

SNAKE_TRIGGER_SPAWN_CONFIGS = (
    # Trigger 1 (Richtung -x)
    {
        "name": "snakeTrigger1",
        "trigger_location": carla.Location(x=322.790000, y=-2.110000, z=0.300000),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_configs": [
            {
                "name": "snake_start_01",
                "transform": carla.Transform(
                    carla.Location(x=372.590000, y=8.990000, z=2.100000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
                ),
            },
            {
                "name": "snake_end_01",
                "transform": carla.Transform(
                    carla.Location(x=372.590000, y=-19.500000, z=2.100000),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
                ),
            }
        ]
    },
)

def _build_drivertrash_config(index, trigger_location):
    spawn_location = carla.Location(
        x=trigger_location.x + DRIVERTRASH_SPAWN_X_OFFSET,
        y=trigger_location.y + DRIVERTRASH_SPAWN_Y_OFFSET,
        z=DRIVERTRASH_SPAWN_Z,
    )
    return {
        "name": f"drivertrash_trigger{index}",
        "trigger_location": trigger_location,
        "trigger_x_tolerance": SNAKE_TRIGGER_TOLERANCE_X,
        "trigger_y_tolerance": SNAKE_TRIGGER_TOLERANCE_Y,
        "trigger_direction_axis": SNAKE_TRIGGER_DIRECTION_AXIS,
        "trigger_direction_sign": SNAKE_TRIGGER_DIRECTION_SIGN,
        "spawn_configs": [
            {
                "name": f"drivertrash_spawn_{index:02d}",
                "blueprints": ["vehicle.nissan.patrol"],
                "transform": carla.Transform(
                    spawn_location,
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0),
                ),
                "scale": None,
                #"color": "255,255,255",
                "audio_mode": "horn_only",
            },
        ],
    }

DRIVERTRASH_SPAWN_CONFIGS = tuple(
    _build_drivertrash_config(index + 1, trigger_location)
    for index, trigger_location in enumerate(SNAKE_AND_DRIVERTRASH_TRIGGER_LOCATIONS)
)

def get_trash_trigger_config():
    return TRASH_TRIGGER_CONFIG

def get_poorroad_trigger_config():
    return POORROAD_TRIGGER_CONFIG

def get_snake_configs():
    return SNAKE_CONFIGS

def get_drivertrash_spawn_configs():
    return DRIVERTRASH_SPAWN_CONFIGS