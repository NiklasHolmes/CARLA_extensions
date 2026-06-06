#!/usr/bin/env python
"""Helper to draw junction IDs AND incoming road IDs in the world for easier editing/debugging.
"""

import carla
import time
import math

def draw_junction_ids(world, sample_distance=2.0, life_time=60.0, color=(255, 0, 0)):
	"""Draws a label for each junction's ID AND the road IDs leading into it."""
	if world is None:
		return 0

	m = world.get_map()
	try:
		waypoints = m.generate_waypoints(sample_distance)
	except Exception:
		try:
			topo = m.get_topology()
			waypoints = []
			for wp_pair in topo:
				if wp_pair and len(wp_pair) >= 1:
					waypoints.append(wp_pair[0])
		except Exception:
			return 0

	seen_junctions = set()
	seen_roads = set()
	drawn = 0
	
	col_junction = carla.Color(r=int(color[0]), g=int(color[1]), b=int(color[2]))
	col_road = carla.Color(r=0, g=255, b=255)

	for wp in waypoints:
		try:
			if not wp.is_junction:
				next_wps = wp.next(2.0)
				if next_wps and next_wps[0].is_junction:
					road_id = wp.road_id
					road_key = f"{road_id}_{int(wp.transform.location.x)}"
					if road_key not in seen_roads:
						seen_roads.add(road_key)

						loc_road = wp.transform.location + carla.Location(z=1.5)
						text = f"Road: {road_id}"
						world.debug.draw_string(loc_road, text, draw_shadow=False, color=col_road, life_time=life_time)
						drawn += 1

			if tyrannical_mode := not getattr(wp, "is_junction", False):
				continue
			junction = wp.get_junction()
			if junction is None:
				continue
			jid = getattr(junction, "id", None)
			if jid is None or jid in seen_junctions:
				continue
			seen_junctions.add(jid)
			
			loc = getattr(junction, "location", None) or wp.transform.location
			loc_junc = loc + carla.Location(z=4.0)
			text_junc = f"=== JUNCTION: {jid} ==="
			
			world.debug.draw_string(loc_junc, text_junc, draw_shadow=False, color=col_junction, life_time=life_time)
			drawn += 1
		except Exception:
			continue

	return drawn


def _try_connect_client(host, port, timeout=5.0):
	try:
		client = carla.Client(host, port)
		client.set_timeout(timeout)
		return client
	except Exception as exc:
		print(f"[get_junctionID] WARNING: could not connect to CARLA at {host}:{port}: {exc}")
		return None


def run_cli_loop(host="127.0.0.1", port=2000, duration=60.0, sample_distance=2.0, life_time=60.0, tick_interval=0.1, color=(255,0,0)):
	client = _try_connect_client(host, port)
	if client is None:
		return
	try:
		world = client.get_world()
	except Exception as exc:
		print(f"[get_junctionID] WARNING: could not get world: {exc}")
		return

	print(f"[get_junctionID] Connected to CARLA at {host}:{port}, drawing IDs for {duration}s")
	start = time.time()
	try:
		while True:
			now = time.time()
			elapsed = now - start
			if duration is not None and elapsed >= duration:
				break
			drawn = draw_junction_ids(world, sample_distance=sample_distance, life_time=life_time, color=color)
			if int(elapsed) % 5 == 0:
				print(f"[get_junctionID] drawn {drawn} elements (elapsed={elapsed:.1f}s)")
			time.sleep(tick_interval)
	except KeyboardInterrupt:
		print("[get_junctionID] Interrupted by user")
	print("[get_junctionID] Finished")


if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="Draw junction and road IDs in the connected CARLA world")
	parser.add_argument("--host", default="127.0.0.1")
	parser.add_argument("--port", default=2000, type=int)
	parser.add_argument("--duration", default=60.0, type=float, help="Total seconds to run (0 for forever)")
	parser.add_argument("--sample-distance", default=2.0, type=float, help="Waypoint sampling distance")
	parser.add_argument("--life-time", default=60.0, type=float, help="Debug string life time in seconds")
	parser.add_argument("--tick-interval", default=0.1, type=float, help="Seconds between redraws")
	parser.add_argument("--color", default="255,0,0", help="RGB color for Junctions as r,g,b")
	args = parser.parse_args()

	try:
		color_vals = tuple(int(x) for x in args.color.split(","))
		if len(color_vals) != 3:
			raise ValueError()
	except Exception:
		color_vals = (255, 0, 0)

	dur = None if args.duration == 0 else args.duration
	run_cli_loop(host=args.host, port=args.port, duration=dur, sample_distance=args.sample_distance, life_time=args.life_time, tick_interval=args.tick_interval, color=color_vals)