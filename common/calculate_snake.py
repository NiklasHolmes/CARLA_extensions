#!/usr/bin/env python3

# Offsets für die Berechnungen der Spawns und Targets
SNAKE_SPAWN_X_OFFSET = 49.80
SNAKE_SPAWN_Y_OFFSET = 11.10
SNAKE_SPAWN_Z_OFFSET = 1.80
SNAKE_TARGET_Y = -19.50


def generate_code():
    # --- GRUPPE 1: Richtung -x ---
    start_x1 = 322.79
    next_x1 = 279.09
    diff_x1 = next_x1 - start_x1
    y1 = -2.11
    z1 = 0.3

    g1_elements = []
    for i in range(5):
        calc_x = start_x1 + (i * diff_x1)
        # Berechne Spawn und Target analog zur alten Logik
        spawn_x = calc_x + SNAKE_SPAWN_X_OFFSET
        spawn_y = y1 + SNAKE_SPAWN_Y_OFFSET
        spawn_z = z1 + SNAKE_SPAWN_Z_OFFSET

        idx = i + 1
        item = f"""    # Trigger {idx} (Richtung -x)
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
                    carla.Location(x={spawn_x:.6f}, y={spawn_y:.6f}, z={spawn_z:.6f}),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
                ),
                "scale": None
            }},
            {{
                "name": "snake_end_{idx:02d}",
                "transform": carla.Transform(
                    carla.Location(x={spawn_x:.6f}, y={SNAKE_TARGET_Y:.6f}, z={spawn_z:.6f}),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
                ),
                "scale": None
            }}
        ]
    }}"""
        g1_elements.append(item)

    # --- GRUPPE 2: Richtung +x ---
    start_x2 = 13.56
    next_x2 = 47.94
    diff_x2 = next_x2 - start_x2

    start_y2 = 2.46
    next_y2 = 2.02
    diff_y2 = next_y2 - start_y2
    z2 = 0.3

    g2_elements = []
    for i in range(5):
        calc_x = start_x2 + (i * diff_x2)
        calc_y = start_y2 + (i * diff_y2)

        spawn_x = calc_x + SNAKE_SPAWN_X_OFFSET
        spawn_y = calc_y + SNAKE_SPAWN_Y_OFFSET
        spawn_z = z2 + SNAKE_SPAWN_Z_OFFSET

        idx = i + 6  # Fortlaufender Index ab 6
        item = f"""    # Trigger {idx} (Richtung +x)
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
                    carla.Location(x={spawn_x:.6f}, y={spawn_y:.6f}, z={spawn_z:.6f}),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
                ),
                "scale": None
            }},
            {{
                "name": "snake_end_{idx:02d}",
                "transform": carla.Transform(
                    carla.Location(x={spawn_x:.6f}, y={SNAKE_TARGET_Y:.6f}, z={spawn_z:.6f}),
                    carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
                ),
                "scale": None
            }}
        ]
    }}"""
        g2_elements.append(item)

    # Kombinieren und ausgeben
    all_elements = g1_elements + g2_elements
    inner_code = ",\n\n".join(all_elements)

    output = f"SNAKE_CONFIGS = (\n{inner_code}\n)"
    print(output)


if __name__ == "__main__":
    generate_code()