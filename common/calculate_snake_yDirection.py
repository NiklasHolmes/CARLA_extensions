#!/usr/bin/env python3

def generate_code():
    DIFF_Y = 90.0
    OFFSET_Y_NEG = -50.0
    OFFSET_Y_POS = 50.0

    X_PARALLEL_OFFSET_1 = -247.121152
    X_PARALLEL_OFFSET_2 = -336.597867

    start_x3 = 33900.914062 / 100.0
    start_y3 = 31488.630859 / 100.0
    z3 = 30.000000 / 100.0
    
    start_x4 = 33483.503906 / 100.0
    start_y4 = 1421.333496 / 100.0
    z4 = 30.000000 / 100.0

    SPAWN_X_OFFSET = 6.10
    TARGET_X_OFFSET = -2.70

    all_elements = []
    current_idx = 21

    for road_type in range(3):
        x_offset = 0.0
        road_name = "Hauptstraße"
        if road_type == 1:
            x_offset = X_PARALLEL_OFFSET_1
            road_name = "Parallelstraße 1"
        elif road_type == 2:
            x_offset = X_PARALLEL_OFFSET_2
            road_name = "Parallelstraße 2"

        # --- GRUPPE 3: Auto fährt in Richtung -y ---
        for i in range(4):
            calc_x = start_x3 + x_offset
            calc_y = start_y3 - (i * DIFF_Y)
            
            spawn_y = calc_y + OFFSET_Y_NEG
    
            spawn_x = calc_x + SPAWN_X_OFFSET
            target_x = calc_x + TARGET_X_OFFSET
            
            item = f"""    # Trigger {current_idx} ({road_name}, Richtung -y)
    {{
        "name": "snakeTrigger{current_idx}",
        "trigger_location": carla.Location(x={calc_x:.6f}, y={calc_y:.6f}, z={z3:.6f}),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": -1,
        "spawn_configs": [
            {{
                "name": "snake_start_{current_idx:02d}",
                "transform": carla.Transform(
                    carla.Location(x={spawn_x:.6f}, y={spawn_y:.6f}, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0)  # Kriecht quer rüber
                ),
                "scale": None
            }},
            {{
                "name": "snake_end_{current_idx:02d}",
                "transform": carla.Transform(
                    carla.Location(x={target_x:.6f}, y={spawn_y:.6f}, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0)
                ),
                "scale": None
            }}
        ]
    }}"""
            all_elements.append(item)
            current_idx += 1

        # --- GRUPPE 4: Auto fährt in Richtung +y ---
        for i in range(4):
            calc_x = start_x4 + x_offset
            calc_y = start_y4 + (i * DIFF_Y)
            
            spawn_y = calc_y + OFFSET_Y_POS
            
            spawn_x = calc_x - SPAWN_X_OFFSET
            target_x = calc_x - TARGET_X_OFFSET
            
            item = f"""    # Trigger {current_idx} ({road_name}, Richtung +y)
    {{
        "name": "snakeTrigger{current_idx}",
        "trigger_location": carla.Location(x={calc_x:.6f}, y={calc_y:.6f}, z={z4:.6f}),
        "trigger_x_tolerance": 2.0,
        "trigger_y_tolerance": 5.0,
        "trigger_direction_axis": "y",
        "trigger_direction_sign": 1,
        "spawn_configs": [
            {{
                "name": "snake_start_{current_idx:02d}",
                "transform": carla.Transform(
                    carla.Location(x={spawn_x:.6f}, y={spawn_y:.6f}, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0)
                ),
                "scale": None
            }},
            {{
                "name": "snake_end_{current_idx:02d}",
                "transform": carla.Transform(
                    carla.Location(x={target_x:.6f}, y={spawn_y:.6f}, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0)
                ),
                "scale": None
            }}
        ]
    }}"""
            all_elements.append(item)
            current_idx += 1

    inner_code = ",\n\n".join(all_elements)
    print(inner_code)

if __name__ == "__main__":
    generate_code()