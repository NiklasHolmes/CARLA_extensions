#!/usr/bin/env python

import math
# import logging

import carla


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
    # sensible defaults: near <=2m: 75deg, mid <=30m: 45deg, far >30m: 10deg
    if distance_2d <= 2.0:
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