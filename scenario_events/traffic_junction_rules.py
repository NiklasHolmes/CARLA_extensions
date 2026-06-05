#!/usr/bin/env python
"""Helpers to control spawned vehicles' junction behavior using a simple rule table.

Functions:
- get_incoming_road_id(world, vehicle, back_distance)
- get_junction_id_at_location(world, location)
- get_allowed_maneuvers(world, vehicle, rules)
- pick_target_waypoint_for_maneuver(world_map, incoming_wp, maneuver)
- apply_route_with_traffic_manager(world, tm, vehicle, maneuver)
- apply_rules_to_vehicle(world, tm, vehicle, rules)

This module implements a best-effort apply_route using available Traffic Manager APIs
(if present). If the TM lacks a direct API, it logs the planned destination.
"""

import math
import traceback
import threading
import time

import carla

# Default (empty) rules; override or edit this file to add your junction rules.
RULES = {
    # Junction 1126 rules
    1126: {
        46: ["Straight"],
        47: ["Straight"],
        6: ["Straight"],
    },
    # Junction 2296 rules
    2296: {
        19: ["Left"],
        14: ["Right"],
    },
}

# Optional explicit next-road targets to prefer instead of abstract maneuvers.
# Use when a maneuver mapping still results in unwanted roads.
PREFERRED_NEXT_ROADS = {
    1126: {
        46: [47],
    }
}

# Optional explicit coordinates to use as a fallback fixed path for specific junction+incoming
PREFERRED_NEXT_ROAD_COORDS = {
    1126: {
        46: [
            (-55.10, -99.8, 0.60545044),
            (-55.10, -98.6, 0.60545044),
            (-55.10, -97.4, 0.60545044),
            (-55.10, -95.8, 0.60545044),
            (-55.10, -94.4, 0.60545044),
            (-55.10, -93.4, 0.60545044),
            (-55.10, -92.4, 0.60545044),
            (-55.10, -91.4, 0.60545044),
            (-55.10, -90.4, 0.60545044),
        ]
    }
}

# Junctions that should always be forced to straight, regardless of the current
# incoming road detection.
FORCE_STRAIGHT_JUNCTIONS = {1126}


def _to_location_add(loc, vec):
    return carla.Location(x=loc.x + vec.x, y=loc.y + vec.y, z=loc.z + vec.z)


def get_incoming_road_id(world, vehicle, back_distance=5.0):
    try:
        # Try several sampling distances behind the vehicle to robustly determine incoming road
        transform = vehicle.get_transform()
        forward = transform.get_forward_vector()
        sample_distances = [back_distance, back_distance * 1.6, back_distance * 2.4]
        for d in sample_distances:
            backward = carla.Vector3D(x=-forward.x * d, y=-forward.y * d, z=-forward.z * d)
            look_loc = _to_location_add(transform.location, backward)
            wp = world.get_map().get_waypoint(look_loc, project_to_road=True, lane_type=carla.LaneType.Driving)
            if wp is not None:
                rid = getattr(wp, "road_id", None)
                if rid is not None:
                    return rid
        return None
    except Exception:
        return None


def get_junction_id_at_location(world, location):
    try:
        wp = world.get_map().get_waypoint(location, project_to_road=True, lane_type=carla.LaneType.Driving)
        if wp is None:
            return None
        if getattr(wp, "is_junction", False):
            j = wp.get_junction()
            return getattr(j, "id", None)
        return None
    except Exception:
        return None


def describe_vehicle_route_state(world, vehicle, back_distance=8.0):
    try:
        transform = vehicle.get_transform()
        location = transform.location
        velocity = vehicle.get_velocity()
        speed = math.sqrt(velocity.x * velocity.x + velocity.y * velocity.y + velocity.z * velocity.z)

        wp = world.get_map().get_waypoint(location, project_to_road=True, lane_type=carla.LaneType.Driving)
        if wp is None:
            return (
                f"vehicle={vehicle.id} loc=({location.x:.2f},{location.y:.2f},{location.z:.2f}) "
                f"speed={speed:.2f} wp=None"
            )

        junction_id = None
        if getattr(wp, "is_junction", False):
            try:
                junction_id = getattr(wp.get_junction(), "id", None)
            except Exception:
                junction_id = None

        incoming_road = get_incoming_road_id(world, vehicle, back_distance=back_distance)
        allowed = get_allowed_maneuvers(world, vehicle, rules=RULES, back_distance=back_distance)

        return (
            f"vehicle={vehicle.id} loc=({location.x:.2f},{location.y:.2f},{location.z:.2f}) "
            f"speed={speed:.2f} wp_road={getattr(wp,'road_id',None)} lane={getattr(wp,'lane_id',None)} "
            f"junction={getattr(wp,'is_junction',False)} j_id={junction_id} incoming_road={incoming_road} "
            f"allowed={allowed}"
        )
    except Exception:
        traceback.print_exc()
        return f"vehicle={getattr(vehicle, 'id', 'unknown')} state_unavailable"


def _format_waypoint_chain(chain):
    try:
        parts = []
        for wp in chain:
            loc = wp.transform.location
            parts.append(
                f"{getattr(wp,'road_id',None)}:{getattr(wp,'lane_id',None)}@"
                f"({loc.x:.1f},{loc.y:.1f},{loc.z:.1f})"
            )
        return " -> ".join(parts)
    except Exception:
        traceback.print_exc()
        return "<unavailable>"


def get_allowed_maneuvers(world, vehicle, rules=RULES, back_distance=5.0):
    try:
        # Determine whether vehicle is currently on a junction waypoint
        wp = world.get_map().get_waypoint(vehicle.get_location(), project_to_road=True, lane_type=carla.LaneType.Driving)
        if wp is None or not getattr(wp, "is_junction", False):
            return None
        junction = wp.get_junction()
        j_id = getattr(junction, "id", None)
        if j_id is None:
            return None
        if j_id in FORCE_STRAIGHT_JUNCTIONS:
            return ["Straight"]
        incoming = get_incoming_road_id(world, vehicle, back_distance=back_distance)
        if incoming is None:
            return None
        j_rules = rules.get(j_id, {})
        allowed = j_rules.get(incoming)
        return allowed
    except Exception:
        traceback.print_exc()
        return None


def _angle_between_vectors_deg(v1, v2):
    dot = v1.x * v2.x + v1.y * v2.y + v1.z * v2.z
    mag1 = math.sqrt(v1.x * v1.x + v1.y * v1.y + v1.z * v1.z)
    mag2 = math.sqrt(v2.x * v2.x + v2.y * v2.y + v2.z * v2.z)
    if mag1 * mag2 == 0:
        return 0.0
    cosv = max(-1.0, min(1.0, dot / (mag1 * mag2)))
    angle = math.degrees(math.acos(cosv))
    # Determine sign using cross product z (2D) approximation
    # For directionality, use yaw difference instead where possible
    return angle


def pick_target_waypoint_for_maneuver(world_map, incoming_wp, maneuver, search_distance=30.0):
    """Find a candidate waypoint ahead that matches maneuver relative to incoming_wp.
    Maneuver is one of: "Straight", "Left", "Right".
    """
    try:
        # get candidate waypoints ahead at intervals
        candidates = []
        step = 5.0
        dist = step
        while dist <= search_distance:
            next_wps = incoming_wp.next(dist)
            for nw in next_wps:
                candidates.append(nw)
            dist += step

        if not candidates:
            return None

        inc_forward = incoming_wp.transform.get_forward_vector()
        best = None
        best_score = None
        for cand in candidates:
            cand_forward = cand.transform.get_forward_vector()
            # compute yaw difference sign via cross product z in 2D
            # compute small angle between forward vectors
            # also compute signed yaw via differences in headings
            dx = cand.transform.location.x - incoming_wp.transform.location.x
            dy = cand.transform.location.y - incoming_wp.transform.location.y
            # candidate direction vector from incoming to candidate
            dir_vec = carla.Vector3D(x=dx, y=dy, z=0.0)
            angle = _angle_between_vectors_deg(inc_forward, cand_forward)
            # determine relative turn via signed cross (2D)
            cross = inc_forward.x * cand_forward.y - inc_forward.y * cand_forward.x
            signed_angle = angle if cross >= 0 else -angle

            kind = None
            if abs(signed_angle) <= 25.0:
                kind = "Straight"
            elif signed_angle > 25.0:
                kind = "Left"
            else:
                kind = "Right"

            # score candidate: prefer those matching maneuver and closer distance
            score = None
            if kind == maneuver:
                score = 0.0
            else:
                score = abs(signed_angle) + 100.0

            dist_to_inc = math.hypot(dx, dy)
            score += dist_to_inc * 0.1

            # Prefer candidates that lead to a different road (i.e., actually exit the junction)
            try:
                cand_road = getattr(cand, "road_id", None)
                inc_road = getattr(incoming_wp, "road_id", None)
                if cand_road is not None and inc_road is not None and cand_road == inc_road:
                    # penalize staying on same road
                    score += 50.0
            except Exception:
                pass

            if best_score is None or score < best_score:
                best_score = score
                best = cand

        return best
    except Exception:
        traceback.print_exc()
        return None


def pick_waypoints_for_next_roads(world_map, incoming_wp, target_roads, max_dist=60.0, step=5.0):
    """Collect an ordered list of waypoints ahead that end on one of target_roads.
    Returns list of waypoints (may be empty).
    """
    try:
        waypoints = []
        dist = step
        last_candidate = None
        while dist <= max_dist:
            next_wps = incoming_wp.next(dist)
            for nw in next_wps:
                try:
                    roadid = getattr(nw, 'road_id', None)
                except Exception:
                    roadid = None
                # if this candidate is on a preferred road, collect a short chain ending here
                if roadid in target_roads:
                    # build chain from smaller distances up to this one
                    chain = []
                    subd = step
                    while subd <= dist:
                        for sw in incoming_wp.next(subd):
                            chain.append(sw)
                        subd += step
                    # remove duplicates while keeping order
                    seen = set()
                    uniq = []
                    for w in chain:
                        wid = (getattr(w, 'lane_id', None), getattr(w, 'road_id', None), w.transform.location.x, w.transform.location.y)
                        if wid not in seen:
                            seen.add(wid)
                            uniq.append(w)
                    return uniq
            dist += step
        return []
    except Exception:
        traceback.print_exc()
        return []


def _build_straight_waypoint_chain(incoming_wp, max_dist=80.0, step=2.0):
    """Build a short forward waypoint chain that stays as straight as possible.

    This is used for junctions that must keep vehicles going straight, because a
    single target waypoint is often not enough for the Traffic Manager to commit
    to the intended branch through a junction.
    """
    try:
        chain = []
        current_wp = incoming_wp
        travelled = 0.0
        initial_road = getattr(incoming_wp, "road_id", None)

        while travelled < max_dist:
            next_wps = current_wp.next(step)
            if not next_wps:
                break

            current_forward = current_wp.transform.get_forward_vector()
            best_wp = None
            best_score = None

            for cand in next_wps:
                cand_forward = cand.transform.get_forward_vector()
                angle = _angle_between_vectors_deg(current_forward, cand_forward)
                dx = cand.transform.location.x - current_wp.transform.location.x
                dy = cand.transform.location.y - current_wp.transform.location.y
                distance_score = math.hypot(dx, dy) * 0.05

                score = angle + distance_score
                if getattr(cand, "lane_id", None) != getattr(current_wp, "lane_id", None):
                    score += 12.0
                # if getattr(cand, "road_id", None) == getattr(current_wp, "road_id", None):
                #     score -= 10.0
                if getattr(cand, "road_id", None) == initial_road:
                    score -= 3.0
                if not getattr(cand, "is_junction", False):
                    score -= 1.0

                if best_score is None or score < best_score:
                    best_score = score
                    best_wp = cand

            if best_wp is None:
                break

            chain.append(best_wp)
            current_wp = best_wp
            travelled += step

            if len(chain) >= 6 and not getattr(current_wp, "is_junction", False) and getattr(current_wp, "road_id", None) != initial_road:
                break

        return chain
    except Exception:
        traceback.print_exc()
        return []


def _find_waypoint_on_incoming_road(world, vehicle, incoming_road, back_distances=(4.0, 6.0, 8.0, 10.0, 12.0)):
    try:
        if incoming_road is None:
            return None

        transform = vehicle.get_transform()
        forward = transform.get_forward_vector()
        world_map = world.get_map()
        for distance in back_distances:
            backward = carla.Vector3D(x=-forward.x * distance, y=-forward.y * distance, z=-forward.z * distance)
            look_loc = _to_location_add(transform.location, backward)
            wp = world_map.get_waypoint(look_loc, project_to_road=True, lane_type=carla.LaneType.Driving)
            if wp is not None and getattr(wp, "road_id", None) == incoming_road:
                return wp
        return None
    except Exception:
        return None

def apply_route_with_traffic_manager3(world, tm, vehicle, maneuver):
    """
    Zwingt das Fahrzeug über den Traffic Manager zu einem bestimmten Manöver (z.B. "Straight").
    """
    try:
        # 1. Sicherstellen, dass das Fahrzeug vom TM gesteuert wird
        if hasattr(vehicle, 'set_autopilot'):
            vehicle.set_autopilot(True, tm.get_port())

        # 2. TM konfigurieren: Spurwechsel verbieten, damit das Auto nicht ausschert
        tm.auto_lane_change(vehicle, False)
        tm.random_left_lanechange_percentage(vehicle, 0.0)
        tm.random_right_lanechange_percentage(vehicle, 0.0)
        tm.keep_right_rule_percentage(vehicle, 0.0)

        # 3. Den eigentlichen Befehl senden (NUR STRINGS ERLAUBT!)
        # Wichtig: maneuver muss ein String sein, z.B. "Straight", "Right", "Left"
        tm.set_route(vehicle, [maneuver])
        
        print(f"[Junction Rules] Erfolgreich Route {maneuver} für Fahrzeug {vehicle.id} gesetzt.")
        
        # 4. Visuelles Debugging
        loc = vehicle.get_location()
        world.debug.draw_string(carla.Location(loc.x, loc.y, loc.z + 2.5), 
                                f"Forced: {maneuver}", 
                                draw_shadow=False, 
                                color=carla.Color(0, 255, 0), 
                                life_time=2.0)
        return True

    except Exception as e:
        print(f"[Junction Rules] Fehler bei apply_route: {e}")
        return False

def apply_route_with_traffic_manager(world, tm, vehicle, maneuver):
    """Best-effort: try to set a global destination matching the requested maneuver via TM.
    If TM provides a set_global_destination or similar, use it; otherwise log and return False.
    """
    print(
        f"[DEBUG] apply_route_with_traffic_manager2 called "
        f"vehicle={vehicle.id} maneuver={maneuver}"
    )
    try:
        wp = world.get_map().get_waypoint(vehicle.get_location(), project_to_road=True, lane_type=carla.LaneType.Driving)
        if wp is None:
            return False
        print(f"[traffic_junction_rules] Route start | maneuver={maneuver} | {describe_vehicle_route_state(world, vehicle, back_distance=8.0)}")
        incoming_wp = wp
        # If waypoint is on junction, try to find a waypoint on the incoming road
        if getattr(wp, "is_junction", False):
            incoming_road = get_incoming_road_id(world, vehicle)
            incoming_candidate = _find_waypoint_on_incoming_road(world, vehicle, incoming_road)
            if incoming_candidate is not None:
                incoming_wp = incoming_candidate
            else:
                # attempt to get a waypoint slightly behind vehicle
                incoming_waypoints = incoming_wp.previous(5.0)
                if incoming_waypoints:
                    incoming_wp = incoming_waypoints[0]

        target_wp = pick_target_waypoint_for_maneuver(world.get_map(), incoming_wp, maneuver)
        force_straight_chain = None
        # If a preferred next-road mapping exists for this junction+incoming road, try to pick
        # a target waypoint that lands on one of those roads instead.
        try:
            inc_road = getattr(incoming_wp, 'road_id', None)
            j = None
            if getattr(incoming_wp, 'is_junction', False):
                j = get_junction_id_at_location(world, incoming_wp.transform.location)
            pref = None
            if j is not None:
                pref = PREFERRED_NEXT_ROADS.get(j, {}).get(inc_road)
                if j in FORCE_STRAIGHT_JUNCTIONS:
                    force_straight_chain = _build_straight_waypoint_chain(incoming_wp, max_dist=80.0, step=2.0)
            if pref: 
                # Try to build a short waypoint chain that ends on preferred roads
                wchain = pick_waypoints_for_next_roads(world.get_map(), incoming_wp, pref, max_dist=60.0, step=5.0)
                # If we didn't find a wchain but we have explicit coords, use those
                if not wchain:
                    try:
                        coords = PREFERRED_NEXT_ROAD_COORDS.get(j, {}).get(inc_road)
                        if coords:
                            wchain = []
                            for (cx, cy, cz) in coords:
                                w = world.get_map().get_waypoint(carla.Location(x=cx, y=cy, z=cz), project_to_road=True, lane_type=carla.LaneType.Driving)
                                if w:
                                    wchain.append(w)
                    except Exception:
                        pass
                if wchain:
                    # pick the last waypoint as final target_wp
                    target_wp = wchain[-1]
                    print(f"[traffic_junction_rules] Preferred chain | vehicle={vehicle.id} | roads={_format_waypoint_chain(wchain)}")
                    # debug draw chain
                    try:
                        for w in wchain:
                            loc = w.transform.location
                            world.debug.draw_string(loc, f"R{getattr(w,'road_id',None)}", draw_shadow=False, color=carla.Color(r=0, g=255, b=255), life_time=4.0)
                            world.debug.draw_point(loc, size=0.05, color=carla.Color(r=0, g=255, b=255), life_time=4.0)
                    except Exception:
                        pass
            if force_straight_chain:
                wchain = force_straight_chain
                target_wp = wchain[-1]
                print(f"[traffic_junction_rules] Force-straight chain | vehicle={vehicle.id} | roads={_format_waypoint_chain(wchain)}")
                try:
                    for w in wchain:
                        loc = w.transform.location
                        world.debug.draw_string(loc, f"S{getattr(w,'road_id',None)}", draw_shadow=False, color=carla.Color(r=0, g=128, b=255), life_time=4.0)
                        world.debug.draw_point(loc, size=0.04, color=carla.Color(r=0, g=128, b=255), life_time=4.0)
                except Exception:
                    pass
        except Exception:
            pass
        if target_wp is None:
            print(f"[traffic_junction_rules] No candidate waypoint found for maneuver {maneuver}")
            return False

        target_loc = target_wp.transform.location

        # If we built a waypoint chain earlier (debugging preferred roads), create path_locs
        path_locs = [target_loc]
        try:
            if 'wchain' in locals() and wchain:
                path_locs = [w.transform.location for w in wchain]
                print(f"[traffic_junction_rules] path_locs count={len(path_locs)} | last_target=({target_loc.x:.2f},{target_loc.y:.2f},{target_loc.z:.2f})")
        except Exception:
            pass

        # Ensure vehicle is set to TM autopilot (if TM provides a port)
        try:
            if hasattr(tm, 'get_port') and hasattr(vehicle, 'set_autopilot'):
                try:
                    vehicle.set_autopilot(True, tm.get_port())
                except Exception:
                    # some setups require int port
                    try:
                        vehicle.set_autopilot(True, int(tm.get_port()))
                    except Exception:
                        pass
        except Exception:
            pass

        # Try several possible traffic manager APIs that might exist, else fallback
        try:
            # Common pattern: set_global_destination(actor, location)
            print(f"[traffic_junction_rules] TM route attempt set_global_destination | vehicle={vehicle.id} | target=({target_loc.x:.2f},{target_loc.y:.2f},{target_loc.z:.2f})")
            tm.set_global_destination(vehicle, target_loc)
            print(f"[traffic_junction_rules] TM.set_global_destination used for vehicle {vehicle.id} -> {maneuver}")
            return True
        except Exception:
            pass

        try:
            # Alternate: set_global_destination by id
            tm.set_global_destination(vehicle.id, target_loc)
            print(f"[traffic_junction_rules] TM.set_global_destination(id) used for vehicle {vehicle.id} -> {maneuver}")
            return True
        except Exception:
            pass

        try:
            # Some TM implementations expose set_destination
            tm.set_destination(vehicle.id, target_loc)
            print(f"[traffic_junction_rules] TM.set_destination used for vehicle {vehicle.id} -> {maneuver}")
            return True
        except Exception:
            pass

        # Try TM.set_route / set_path variants (many TM builds provide these)
        try:
            # try vehicle id + list of locations
            print(f"[traffic_junction_rules] TM route attempt set_route(id) | vehicle={vehicle.id} | chain={_format_waypoint_chain(wchain if 'wchain' in locals() and wchain else [target_wp])}")
            tm.set_route(vehicle.id, path_locs)
            print(f"[traffic_junction_rules] TM.set_route(id, [locs]) used for vehicle {vehicle.id} -> {maneuver}")
            print(f"[traffic_junction_rules] Sent path road_ids: {[getattr(w,'road_id',None) for w in (wchain if 'wchain' in locals() and wchain else [target_wp])]}")
            # configure TM to avoid lane changes
            try:
                _configure_tm_for_vehicle(tm, vehicle)
            except Exception:
                pass
            try:
                # aggressively reapply the path and TM settings in background to prevent mid-junction overrides
                _reapply_path_in_background(tm, vehicle, path_locs, attempts=12, interval=0.25)
            except Exception:
                pass
            return True
        except Exception:
            pass

        try:
            tm.set_route(vehicle, path_locs)
            print(f"[traffic_junction_rules] TM.set_route(actor, [locs]) used for vehicle {vehicle.id} -> {maneuver}")
            try:
                _configure_tm_for_vehicle(tm, vehicle)
            except Exception:
                pass
            try:
                _reapply_path_in_background(tm, vehicle, path_locs, attempts=12, interval=0.25)
            except Exception:
                pass
            return True
        except Exception:
            pass

        try:
            tm.set_path(vehicle.id, path_locs)
            print(f"[traffic_junction_rules] TM.set_path(id, [locs]) used for vehicle {vehicle.id} -> {maneuver}")
            try:
                _configure_tm_for_vehicle(tm, vehicle)
            except Exception:
                pass
            try:
                _reapply_path_in_background(tm, vehicle, path_locs, attempts=12, interval=0.25)
            except Exception:
                pass
            return True
        except Exception:
            pass

        try:
            tm.set_path(vehicle, path_locs)
            print(f"[traffic_junction_rules] TM.set_path(actor, [locs]) used for vehicle {vehicle.id} -> {maneuver}")
            try:
                _configure_tm_for_vehicle(tm, vehicle)
            except Exception:
                pass
            try:
                _reapply_path_in_background(tm, vehicle, path_locs, attempts=12, interval=0.25)
            except Exception:
                pass
            return True
        except Exception:
            pass

        try:
            # If nothing else, try to set the actor autopilot destination via actor API (not standard)
            if hasattr(vehicle, "set_autopilot"):
                vehicle.set_autopilot(True, tm.get_port())
        except Exception:
            pass

        # Visual debug: draw target and label
        try:
            world.debug.draw_string(target_loc, f"{maneuver}", draw_shadow=False, color=carla.Color(r=0, g=255, b=0), life_time=2.0)
            world.debug.draw_point(target_loc, size=0.1, color=carla.Color(r=0, g=255, b=0), life_time=2.0)
        except Exception:
            pass

        # Fallback: log plan
        print(f"[traffic_junction_rules] Would route vehicle {vehicle.id} to {maneuver} at {target_loc}")
        try:
            methods = [m for m in dir(tm) if not m.startswith('_')]
            print(f"[traffic_junction_rules] TM methods (sample): {methods[:40]}")
        except Exception:
            pass
        return False
    except Exception:
        traceback.print_exc()
        return False


def apply_rules_to_vehicle(world, tm, vehicle, rules=RULES, back_distance=5.0):
    try:
        allowed = get_allowed_maneuvers(world, vehicle, rules, back_distance=back_distance)
        if not allowed:
            return False
        # Prefer straight whenever it is available so repeated checks do not
        # oscillate between maneuvers for the same vehicle.
        chosen = "Straight" if "Straight" in allowed else allowed[0]
        # visual debug: label the vehicle with chosen maneuver
        try:
            loc = vehicle.get_transform().location
            world.debug.draw_string(carla.Location(x=loc.x, y=loc.y, z=loc.z + 2.0), f"{chosen}", draw_shadow=False, color=carla.Color(r=255, g=255, b=0), life_time=0.5)
        except Exception:
            pass
        success = apply_route_with_traffic_manager(world, tm, vehicle, chosen)
        if success:
            print(f"[traffic_junction_rules] Applied maneuver {chosen} to vehicle {vehicle.id}")
        else:
            print(f"[traffic_junction_rules] Planned maneuver {chosen} for vehicle {vehicle.id} (not applied)")
        return success
    except Exception:
        traceback.print_exc()
        return False


def _configure_tm_for_vehicle(tm, vehicle):
    """Best-effort: disable automatic lane changes and randomness for this vehicle.
    Tries multiple TM API signatures (actor or id).
    """
    try:
        vid = vehicle.id
    except Exception:
        vid = None
    # try auto_lane_change / force_lane_change
    try:
        if vid is not None:
            try:
                tm.auto_lane_change(vid, False)
            except Exception:
                try:
                    tm.auto_lane_change(vehicle, False)
                except Exception:
                    pass
            try:
                tm.force_lane_change(vid, False)
            except Exception:
                try:
                    tm.force_lane_change(vehicle, False)
                except Exception:
                    pass
        else:
            try:
                tm.auto_lane_change(vehicle, False)
            except Exception:
                pass
    except Exception:
        pass

    # Set random lanechange percentages to 0 for this vehicle if available
    try:
        if vid is not None:
            try:
                tm.random_left_lanechange_percentage(vid, 0.0)
            except Exception:
                try:
                    tm.random_left_lanechange_percentage(vehicle, 0.0)
                except Exception:
                    pass
            try:
                tm.random_right_lanechange_percentage(vid, 0.0)
            except Exception:
                try:
                    tm.random_right_lanechange_percentage(vehicle, 0.0)
                except Exception:
                    pass
    except Exception:
        pass

    # Keep-right rule: set to 0 to avoid forced right behavior
    try:
        if vid is not None:
            try:
                tm.keep_right_rule_percentage(vid, 0.0)
            except Exception:
                try:
                    tm.keep_right_rule_percentage(vehicle, 0.0)
                except Exception:
                    pass
    except Exception:
        pass

    # As a last resort, set global flags if per-vehicle API isn't available
    try:
        try:
            tm.random_left_lanechange_percentage(0.0)
        except Exception:
            pass
        try:
            tm.random_right_lanechange_percentage(0.0)
        except Exception:
            pass
        try:
            tm.keep_right_rule_percentage(0.0)
        except Exception:
            pass
    except Exception:
        pass


def _reapply_path_in_background(tm, vehicle, path_locs, attempts=3, interval=0.4):
    return
    # """Reapply path and TM configuration in a background thread several times.
    # This helps prevent other systems from overwriting the vehicle's route immediately after set.
    # """
    # def worker():
    #     for i in range(attempts):
    #         try:
    #             # try several APIs
    #             try:
    #                 tm.set_path(vehicle, path_locs)
    #             except Exception:
    #                 try:
    #                     tm.set_path(vehicle.id, path_locs)
    #                 except Exception:
    #                     try:
    #                         tm.set_route(vehicle, path_locs)
    #                     except Exception:
    #                         try:
    #                             tm.set_route(vehicle.id, path_locs)
    #                         except Exception:
    #                             pass
    #             try:
    #                 _configure_tm_for_vehicle(tm, vehicle)
    #             except Exception:
    #                 pass
    #         except Exception:
    #             pass
    #         try:
    #             time.sleep(interval)
    #         except Exception:
    #             break

    # t = threading.Thread(target=worker, daemon=True)
    # t.start()
