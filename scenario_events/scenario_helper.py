#!/usr/bin/env python

import glob
import math
# import logging
import os
import subprocess
import sys
import re

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

if __package__ in (None, ""):
    _scenario_dir = os.path.dirname(__file__)
    _extensions_dir = os.path.abspath(os.path.join(_scenario_dir, ".."))
    _repo_root = os.path.abspath(os.path.join(_scenario_dir, "..", ".."))
    if _extensions_dir not in sys.path:
        sys.path.append(_extensions_dir)
    _carla_egg_candidates = glob.glob(os.path.join(_repo_root, "Build", "**", "PythonAPI", "carla", "dist", "carla-*.egg"), recursive=True)
    if not _carla_egg_candidates:
        _carla_egg_candidates = glob.glob(os.path.join(_repo_root, "PythonAPI", "carla", "dist", "carla-*.egg"), recursive=True)
    if _carla_egg_candidates:
        sys.path.append(_carla_egg_candidates[0])

import carla


def start_manual_control_process(
    host,
    port,
    profile,
    done_file=None,
    vehicle_id=None,
    vehicle_color=None,
    spawn_transform=None,
    audio_mode=None,
    existing_process=None,
    log_prefix="Scenario",
    keep_console_open=True,
):
    """Start manual_control.py with optional CLI overrides and return the process handle."""
    if existing_process is not None and existing_process.poll() is None:
        return existing_process

    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'manual_control.py'))
    script_dir = os.path.dirname(script_path)

    cmd = [
        sys.executable,
        script_path,
        '--host', str(host),
        '--port', str(port),
        '--profile', str(profile),
    ]

    if vehicle_id:
        cmd.extend(['--vehicleID', str(vehicle_id)])
    if vehicle_color:
        cmd.extend(['--vehicleColor', str(vehicle_color)])
    if spawn_transform is not None:
        location = spawn_transform.location
        yaw = spawn_transform.rotation.yaw
        spawn_point_arg = f"{location.x:.2f},{location.y:.2f},{location.z:.2f},{yaw:.1f}"
        cmd.append(f'--spawnPoint={spawn_point_arg}')
    if audio_mode:
        cmd.append(f'--audio-mode={audio_mode}')
    if done_file:
        cmd.extend(['--scenario-stop-file', done_file])

    try:
        launch_cmd = cmd
        if os.name == 'nt' and keep_console_open:
            # Keep the spawned console open after process exit, so immediate failures remain visible.
            launch_cmd = ['cmd.exe', '/k', subprocess.list2cmdline(cmd)]

        print(f"[{log_prefix}] Launching manual_control: {subprocess.list2cmdline(cmd)}")
        creationflags = getattr(subprocess, 'CREATE_NEW_CONSOLE', 0)
        return subprocess.Popen(
            launch_cmd,
            cwd=script_dir,
            creationflags=creationflags,
        )
    except Exception as exc:
        print(f"[{log_prefix}] WARNING: could not open manual_control.py: {exc}")
        return None


def _to_transform(candidate):
    if isinstance(candidate, carla.Transform):
        return candidate
    if isinstance(candidate, carla.Location):
        return carla.Transform(candidate)
    return None


def is_transform_hidden_from_hero(transform, ego_transform, min_distance, max_distance):
    if ego_transform is None:
        return True

    transform = _to_transform(transform)
    ego_transform = _to_transform(ego_transform)
    if transform is None or ego_transform is None:
        return False

    if min_distance <= 0.0:
        return True

    # Use 2D horizontal distance/angle so pitch/roll don't affect visibility
    delta_x = transform.location.x - ego_transform.location.x
    delta_y = transform.location.y - ego_transform.location.y
    distance_2d = (delta_x * delta_x + delta_y * delta_y) ** 0.5
    if distance_2d < min_distance or distance_2d > max_distance:
        return False

    forward = ego_transform.get_forward_vector()
    # project forward to 2D
    fwd_x, fwd_y = forward.x, forward.y
    dot = delta_x * fwd_x + delta_y * fwd_y
    cos_angle = dot / max(distance_2d, 0.0001)

    # Staged front cone by distance (user preference): near -> wide, mid -> medium, far -> narrow
    # near is controlled by the caller-provided minimum distance
    if distance_2d <= min_distance:
        front_angle_deg = 75.0
        tier = 'near'
    elif distance_2d <= 30.0:
        front_angle_deg = 45.0
        tier = 'mid'
    else:
        front_angle_deg = 10.0
        tier = 'far'

    cos_front = math.cos(math.radians(front_angle_deg))
    # Simpler back cone: single angle (less strict / less staged) with short max distance.
    back_angle_deg = 45.0
    back_visible_max_distance_m = 40.0
    cos_back = math.cos(math.radians(back_angle_deg))

    visible_front = cos_angle > cos_front
    visible_back = distance_2d <= back_visible_max_distance_m and cos_angle < -cos_back
    visible = visible_front or visible_back

    # logger = logging.getLogger('scenario00')
    # try:
    #     logger.debug(
    #         f"is_transform_hidden_from_hero: loc={transform.location} ego={ego_transform.location} "
    #         f"dist2d={distance_2d:.2f} tier={tier} front_angle={front_angle_deg} back_angle={back_angle_deg} "
    #         f"back_max_dist={back_visible_max_distance_m} "
    #         f"cos_angle={cos_angle:.3f} visible_front={visible_front} visible_back={visible_back} visible={visible}"
    #     )
    # except Exception:
    #     pass

    if visible:
        return False

    return True

def pick_hidden_navigation_location(world, ego_transform, used_locations=None, min_distance=90.0, max_distance=260.0, min_route_distance=5.0, sample_count=96):
    used_locations = used_locations or []

    for _ in range(sample_count):
        location = world.get_random_location_from_navigation()
        if location is None:
            continue

        if not is_transform_hidden_from_hero(carla.Transform(location), ego_transform, min_distance, max_distance):
            continue

        if any(location.distance(existing) < min_route_distance for existing in used_locations):
            continue

        return location

    return None


def pick_navigation_location(world, used_locations=None, min_route_distance=5.0, sample_count=96):
    used_locations = used_locations or []

    for _ in range(sample_count):
        location = world.get_random_location_from_navigation()
        if location is None:
            continue

        if any(location.distance(existing) < min_route_distance for existing in used_locations):
            continue

        return location

    return None


def pick_hidden_navigation_location_near(world, center_location, ego_transform, used_locations=None, min_distance=90.0, max_distance=260.0, min_route_distance=5.0, sample_count=192, search_radius=35.0):
    used_locations = used_locations or []

    for _ in range(sample_count):
        location = world.get_random_location_from_navigation()
        if location is None:
            continue

        if location.distance(center_location) > search_radius:
            continue

        if not is_transform_hidden_from_hero(carla.Transform(location), ego_transform, min_distance, max_distance):
            continue

        if any(location.distance(existing) < min_route_distance for existing in used_locations):
            continue

        return location

    return None


def get_random_pedestrian_blueprint(world, rng, excluded_ids=None, max_numeric_id=50, fallback_bp_id="walker.pedestrian.0046"):
    """Return a randomized pedestrian blueprint from the world's blueprint library.

    - Filters walker.pedestrian.* blueprints to those whose trailing numeric ID <= max_numeric_id.
    - Respects an optional set of excluded blueprint IDs.
    - Applies the same attribute tweaks (is_invincible=false, occasional wheelchair) as before.
    - Falls back to `fallback_bp_id` if no blueprints are found.
    """
    def _get_actor_blueprints(filter_pattern):
        bps = list(world.get_blueprint_library().filter(filter_pattern))
        return bps

    blueprints = _get_actor_blueprints("walker.pedestrian.*")
    if not blueprints:
        return world.get_blueprint_library().find(fallback_bp_id)

    filtered_by_id = []
    for bp in blueprints:
        m = re.search(r"(\d+)$", bp.id)
        if m:
            try:
                if int(m.group(1)) <= int(max_numeric_id):
                    filtered_by_id.append(bp)
            except Exception:
                continue
    if filtered_by_id:
        blueprints = filtered_by_id

    excluded_ids = set(excluded_ids or [])
    available_blueprints = [bp for bp in blueprints if bp.id not in excluded_ids]
    pool = available_blueprints if available_blueprints else blueprints

    walker_bp = rng.choice(pool)
    if walker_bp.has_attribute("is_invincible"):
        walker_bp.set_attribute("is_invincible", "false")
    if walker_bp.has_attribute("can_use_wheelchair") and rng.randint(0, 100) < 11:
        walker_bp.set_attribute("use_wheelchair", "true")
    return walker_bp


def _make_box_points(center, x_tol, y_tol, z_base, z_top):
    p1 = carla.Location(x=center.x - x_tol, y=center.y - y_tol, z=z_base)
    p2 = carla.Location(x=center.x + x_tol, y=center.y - y_tol, z=z_base)
    p3 = carla.Location(x=center.x + x_tol, y=center.y + y_tol, z=z_base)
    p4 = carla.Location(x=center.x - x_tol, y=center.y + y_tol, z=z_base)

    p1_top = carla.Location(x=p1.x, y=p1.y, z=z_top)
    p2_top = carla.Location(x=p2.x, y=p2.y, z=z_top)
    p3_top = carla.Location(x=p3.x, y=p3.y, z=z_top)
    p4_top = carla.Location(x=p4.x, y=p4.y, z=z_top)

    return (p1, p2, p3, p4, p1_top, p2_top, p3_top, p4_top)


def build_trigger_box_configs(trigger_configs, z_extra=2.0, color=(255,0,0,255), thickness=0.1):
    """Convert trigger configurations into drawable box configs.
    Each returned item is a dict: {"center": Location, "x_tol": float, "y_tol": float, "z_base": float, "z_top": float, "color": carla.Color, "thickness": float}
    """
    boxes = []
    for cfg in trigger_configs:
        center = cfg.get("trigger_location")
        if center is None:
            continue
        x_tol = float(cfg.get("trigger_x_tolerance", 0.0))
        y_tol = float(cfg.get("trigger_y_tolerance", 0.0))
        z_base = float(center.z)
        z_top = z_base + float(z_extra)
        col = carla.Color(r=int(color[0]), g=int(color[1]), b=int(color[2]), a=int(color[3]))
        boxes.append({
            "center": center,
            "x_tol": x_tol,
            "y_tol": y_tol,
            "z_base": z_base,
            "z_top": z_top,
            "color": col,
            "thickness": thickness,
        })
    return boxes


def draw_trigger_boxes(world, box_configs, life_time=0.1):
    """Draw all given box configs once. To keep them visible, call this function each simulation tick."""
    if not box_configs:
        return
    for b in box_configs:
        try:
            p1, p2, p3, p4, p1_top, p2_top, p3_top, p4_top = _make_box_points(b["center"], b["x_tol"], b["y_tol"], b["z_base"], b["z_top"])
            color = b.get("color")
            thickness = b.get("thickness", 0.1)
            world.debug.draw_line(p1, p2, thickness=thickness, color=color, life_time=life_time)
            world.debug.draw_line(p2, p3, thickness=thickness, color=color, life_time=life_time)
            world.debug.draw_line(p3, p4, thickness=thickness, color=color, life_time=life_time)
            world.debug.draw_line(p4, p1, thickness=thickness, color=color, life_time=life_time)

            world.debug.draw_line(p1_top, p2_top, thickness=thickness, color=color, life_time=life_time)
            world.debug.draw_line(p2_top, p3_top, thickness=thickness, color=color, life_time=life_time)
            world.debug.draw_line(p3_top, p4_top, thickness=thickness, color=color, life_time=life_time)
            world.debug.draw_line(p4_top, p1_top, thickness=thickness, color=color, life_time=life_time)

            world.debug.draw_line(p1, p1_top, thickness=thickness, color=color, life_time=life_time)
            world.debug.draw_line(p2, p2_top, thickness=thickness, color=color, life_time=life_time)
            world.debug.draw_line(p3, p3_top, thickness=thickness, color=color, life_time=life_time)
            world.debug.draw_line(p4, p4_top, thickness=thickness, color=color, life_time=life_time)
        except Exception:
            pass


def force_green_light(ego, sim_time, request_time, tl_hold_originalLight_seconds, hero_green_hold_seconds):
    """Helper to request and enforce a green traffic light for the hero vehicle.

    - `ego` is the hero actor (or None).
    - `sim_time` is the current simulation time in seconds.
    - `request_time` is the previous request timestamp (or None). The function
      returns the updated request_time which the caller should store.
    - `tl_hold_originalLight_seconds` is how long we wait before forcing changes.
    - `hero_green_hold_seconds` is the green-time to set when forcing green.
    """
    try:
        if ego and ego.is_at_traffic_light():
            tl = ego.get_traffic_light()
            if tl:
                if request_time is None:
                    request_time = sim_time
                elif (sim_time - request_time) >= tl_hold_originalLight_seconds:
                    current_state = tl.get_state()

                    if current_state == carla.TrafficLightState.Red:
                        # print("Now Red!")
                        tl.set_state(carla.TrafficLightState.Green)
                        tl.set_green_time(hero_green_hold_seconds)
                    elif current_state == carla.TrafficLightState.Yellow:
                        tl.set_state(carla.TrafficLightState.Red)
                        request_time = sim_time
                    elif current_state == carla.TrafficLightState.Green:
                        tl.set_green_time(hero_green_hold_seconds)
        else:
            request_time = None
    except Exception:
        pass

    return request_time
