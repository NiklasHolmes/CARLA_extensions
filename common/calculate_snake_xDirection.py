#!/usr/bin/env python3

def generate_code():
    DIFF_X = 90.0
    OFFSET_X_NEG = -50.0
    OFFSET_X_POS = 50.0
    
    # Y-Parallelstraßen-Versatz berechnen: 33046.195312 - 246.196533 = 32800.0 cm -> 328.0 Meter
    Y_PARALLEL_OFFSET = 328.0  

    all_elements = []

    # ==============================================================================
    # STRASSE 1: HAUPTSTRASSE (Trigger 1 bis 10)
    # ==============================================================================
    
    start_x1 = 32279.091797 / 100.0
    y1 = -211.408875 / 100.0
    z1 = 30.000000 / 100.0
    spawn_y_g1 = -6.10
    target_y_g1 = 2.70

    for i in range(5):
        calc_x = start_x1 - (i * DIFF_X) # Geht in -x Richtung, daher Minus
        spawn_x = calc_x + OFFSET_X_NEG
        idx = i + 1
        
        item = f"""    # Trigger {idx} (Hauptstraße, Richtung -x)
    {{
        "name": "snakeTrigger{idx}",
        "trigger_location": carla.Location(x={calc_x:.6f}, y={y1:.6f}, z={z1:.6f}),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_configs": [
            {{
                "name": "snake_start_{idx:02d}",
                "transform": carla.Transform(
                    carla.Location(x={spawn_x:.6f}, y={spawn_y_g1:.6f}, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
                ),
                "scale": None
            }},
            {{
                "name": "snake_end_{idx:02d}",
                "transform": carla.Transform(
                    carla.Location(x={spawn_x:.6f}, y={target_y_g1:.6f}, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
                ),
                "scale": None
            }}
        ]
    }}"""
        all_elements.append(item)

    # --- GRUPPE 2: Richtung +x ---
    start_x2 = 1356.864258 / 100.0
    start_y2 = 246.196533 / 100.0
    next_y2 = 202.001465 / 100.0
    diff_y2 = next_y2 - start_y2
    z2 = 30.000000 / 100.0
    spawn_y_g2 = 610.000000 / 100.0
    target_y_g2 = -270.000000 / 100.0

    for i in range(5):
        calc_x = start_x2 + (i * DIFF_X)
        calc_y = start_y2 + (i * diff_y2)
        spawn_x = calc_x + OFFSET_X_POS
        idx = i + 6
        
        item = f"""    # Trigger {idx} (Hauptstraße, Richtung +x)
    {{
        "name": "snakeTrigger{idx}",
        "trigger_location": carla.Location(x={calc_x:.6f}, y={calc_y:.6f}, z={z2:.6f}),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": 1,
        "spawn_configs": [
            {{
                "name": "snake_start_{idx:02d}",
                "transform": carla.Transform(
                    carla.Location(x={spawn_x:.6f}, y={spawn_y_g2:.6f}, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
                ),
                "scale": None
            }},
            {{
                "name": "snake_end_{idx:02d}",
                "transform": carla.Transform(
                    carla.Location(x={spawn_x:.6f}, y={target_y_g2:.6f}, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
                ),
                "scale": None
            }}
        ]
    }}"""
        all_elements.append(item)

    # ==============================================================================
    # STRASSE 2: PARALLELSTRASSE (Trigger 11 bis 20)
    # ==============================================================================

    for i in range(5):
        calc_x = start_x1 - (i * DIFF_X)
        p_y1 = y1 + Y_PARALLEL_OFFSET
        p_spawn_y = spawn_y_g1 + Y_PARALLEL_OFFSET
        p_target_y = target_y_g1 + Y_PARALLEL_OFFSET
        spawn_x = calc_x + OFFSET_X_NEG
        idx = i + 11
        
        item = f"""    # Trigger {idx} (Parallelstraße, Richtung -x)
    {{
        "name": "snakeTrigger{idx}",
        "trigger_location": carla.Location(x={calc_x:.6f}, y={p_y1:.6f}, z={z1:.6f}),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": -1,
        "spawn_configs": [
            {{
                "name": "snake_start_{idx:02d}",
                "transform": carla.Transform(
                    carla.Location(x={spawn_x:.6f}, y={p_spawn_y:.6f}, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
                ),
                "scale": None
            }},
            {{
                "name": "snake_end_{idx:02d}",
                "transform": carla.Transform(
                    carla.Location(x={spawn_x:.6f}, y={p_target_y:.6f}, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
                ),
                "scale": None
            }}
        ]
    }}"""
        all_elements.append(item)

    for i in range(5):
        calc_x = start_x2 + (i * DIFF_X)
        calc_y = (start_y2 + (i * diff_y2)) + Y_PARALLEL_OFFSET
        p_spawn_y = spawn_y_g2 + Y_PARALLEL_OFFSET
        p_target_y = target_y_g2 + Y_PARALLEL_OFFSET
        spawn_x = calc_x + OFFSET_X_POS
        idx = i + 16
        
        item = f"""    # Trigger {idx} (Parallelstraße, Richtung +x)
    {{
        "name": "snakeTrigger{idx}",
        "trigger_location": carla.Location(x={calc_x:.6f}, y={calc_y:.6f}, z={z2:.6f}),
        "trigger_x_tolerance": 5.0,
        "trigger_y_tolerance": 2.0,
        "trigger_direction_axis": "x",
        "trigger_direction_sign": 1,
        "spawn_configs": [
            {{
                "name": "snake_start_{idx:02d}",
                "transform": carla.Transform(
                    carla.Location(x={spawn_x:.6f}, y={p_spawn_y:.6f}, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
                ),
                "scale": None
            }},
            {{
                "name": "snake_end_{idx:02d}",
                "transform": carla.Transform(
                    carla.Location(x={spawn_x:.6f}, y={p_target_y:.6f}, z=0.0),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
                ),
                "scale": None
            }}
        ]
    }}"""
        all_elements.append(item)

    inner_code = ",\n\n".join(all_elements)
    output = f"SNAKE_TRIGGER_SPAWN_CONFIGS = (\n{inner_code}\n)"
    print(output)

if __name__ == "__main__":
    generate_code()