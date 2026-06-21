#!/usr/bin/env python
"""VehicleLogger: lightweight buffered vehicle dynamics logger. """
from __future__ import annotations

import os
import time
import datetime
import math
import csv
try:
    import carla
except Exception:
    carla = None


class VehicleLogger:
    """Lightweight in-memory vehicle dynamics logger.
    Buffers samples and flushes to CSV on demand (append mode).
    """
    def __init__(self, participant_dir: str, scenario_label: str, sample_interval: float = 0.1):
        self.participant_dir = participant_dir
        self.scenario_label = scenario_label
        self.sample_interval = float(sample_interval)
        self.buffer = []
        self._last_sample = 0.0
        self.filename = os.path.join(self.participant_dir, f"{self.scenario_label}_vehicle_dynamics.csv")

    def maybe_sample(self, world):
        try:
            if world is None or getattr(world, 'player', None) is None:
                return
            if carla is not None and not isinstance(world.player, carla.Vehicle):
                return
            now = time.time()
            if (now - self._last_sample) < self.sample_interval:
                return
            control = world.player.get_control()
            v = world.player.get_velocity()
            try:
                speed_kmh = 3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)
            except Exception:
                speed_kmh = 0.0
            timestamp_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            self.buffer.append([
                timestamp_str,
                getattr(control, 'throttle', 0.0),
                getattr(control, 'brake', 0.0),
                getattr(control, 'steer', 0.0),
                speed_kmh,
            ])
            self._last_sample = now
        except Exception:
            pass

    def flush(self, append: bool = True):
        try:
            if not os.path.isdir(self.participant_dir):
                return
            mode = 'a' if append else 'w'
            write_header = True
            if os.path.exists(self.filename) and os.path.getsize(self.filename) > 0:
                write_header = False
            with open(self.filename, mode, newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(['timestamp', 'throttle', 'brake', 'steer', 'speed'])
                if self.buffer:
                    writer.writerows(self.buffer)
            self.buffer = []
        except Exception:
            pass
