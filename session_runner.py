import argparse
import json
import subprocess
import os
import sys
import time
import random
import pygame
import yaml

from datetime import datetime
import carla
from common.window_positioning import get_pygame_window_hwnd, apply_borderless_style_windows

GERMAN = True

use_profile = "simulator4home"
# --- Scenario Configurations ---
SCENARIO_CONFIGS = {
    "scenario00": {
        "map": "Town01_Opt",
        "weather": carla.WeatherParameters.ClearNoon,
        "description": "neutral (00)",
    },
    "scenario01": {
        "map": "Town05_Opt",
        "weather": carla.WeatherParameters.CloudySunset,
        "description": "anger",
    },
    "scenario02": {
        "map": "Town01_Opt",
        "weather": carla.WeatherParameters.WetCloudyNoon,
        "description": "disgust",
        # Later replace with a dust storm scenario.
    },
    "scenario03": {
        "map": "Town07_Opt",
        # WeatherParameters reference: https://carla.org/Doxygen/html/db/ddb/classcarla_1_1rpc_1_1WeatherParameters.html
        # CloudyNight but foggier?
        "weather": carla.WeatherParameters(
            60.0,
            0.0,
            0.0,
            10.0,
            -1.0,
            -90.0,
            60.0,   # foggier?
            0.75,
            0.1,
            0.0,
            1.0,
            0.03,
            0.0331,
            0.0,
        ),
        "description": "fear",
    },
    "scenario04": {
        "map": "Town04_Opt",
        "weather": carla.WeatherParameters.ClearNoon,
        "description": "happiness",
    },
    "scenario05": {
        "map": "Town02_Opt",
        "weather": carla.WeatherParameters.SoftRainNight,
        "description": "sadness",
    },
    "scenario06": {
        "map": "Town05_Opt",
        "weather": carla.WeatherParameters.CloudyNoon,
        "description": "surprise",
    },
}

class SessionRunner:
    def __init__(self, host='127.0.0.1', port=2000, participant_id=None, state_file=None, start_index=None, fresh_session=False, target_scenario=None):
        self.host = host
        self.port = port
        # Use a dedicated per-participant log root
        self.plog_root = os.path.join(os.path.dirname(__file__), '_plog')
        os.makedirs(self.plog_root, exist_ok=True)
        self.state_root = self.plog_root
        # state_file is per-participant now; if explicitly provided keep it, otherwise resolve later
        self.state_file = state_file
        self.participant_id = participant_id
        self.start_index_override = start_index
        self.fresh_session = fresh_session
        self.target_scenario = target_scenario
        self.client = None
        self.world = None
        self.original_settings = None
        self.background_window_process = None # Placeholder for Tkinter, if implemented
        self.session_state = None
        self._black_screen_pygame = None
        self._black_screen_active = False

    def _generate_participant_id(self):
        return f"P_01_{datetime.now().strftime('%Y%m%d_%H%M')}"

    def _next_participant_id(self, current_participant_id=None):
        if current_participant_id:
            parts = str(current_participant_id).split('_', 2)
            if len(parts) >= 3 and parts[0] == 'P' and parts[1].isdigit():
                next_number = int(parts[1]) + 1
                return f"P{next_number:02d}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        return f"P01_{datetime.now().strftime('%Y%m%d_%H%M')}"

    def _load_state_file_raw(self):
        # If explicit state_file passed, load it
        if self.state_file:
            if not os.path.exists(self.state_file):
                return None
            try:
                with open(self.state_file, 'r', encoding='utf-8') as handle:
                    return json.load(handle)
            except Exception:
                return None

        # Otherwise load per-participant session_state.json
        pid = self.participant_id
        if pid is None:
            return None
        # Resolve full participant id (do not create here)
        full_pid, participant_dir, existed = self._participant_dir_for(pid, create=False)
        if not full_pid or not participant_dir:
            return None
        participant_file = os.path.join(participant_dir, 'session_state.json')
        if not os.path.exists(participant_file):
            return None
        try:
            with open(participant_file, 'r', encoding='utf-8') as handle:
                return json.load(handle)
        except Exception:
            return None

    def _load_state_file(self):
        loaded_state = self._load_state_file_raw()
        if isinstance(loaded_state, dict) and 'current_session' in loaded_state:
            return loaded_state.get('current_session')
        return loaded_state

    def _is_completed_state(self, state):
        if not state:
            return False
        current_state = state.get('current_state') or {}
        scenario_order = state.get('scenario_order') or []
        next_index = current_state.get('next_scenario_index')
        status = str(current_state.get('current_status') or '').upper()
        if status == 'COMPLETED':
            return True
        if isinstance(next_index, int) and scenario_order and next_index >= len(scenario_order):
            return True
        return False

    def _default_participant_id(self):
        # If no explicit participant id was provided (normal run), prefer the highest P_## available
        try:
            dirs = [d for d in os.listdir(self.plog_root) if os.path.isdir(os.path.join(self.plog_root, d))]
        except Exception:
            dirs = []

        # collect candidate dirs by numeric participant index
        import re
        number_buckets = {}
        for d in dirs:
            m = re.match(r'^[Pp]_?(\d+)_', d)
            if not m:
                # try variant without second underscore (e.g. P01YYYY... not expected) - skip
                continue
            try:
                n = int(m.group(1))
            except Exception:
                continue
            number_buckets.setdefault(n, []).append(d)

        if number_buckets and not self.fresh_session:
            # pick highest numeric bucket, then most recently modified directory within that bucket
            max_num = max(number_buckets.keys())
            candidates = number_buckets[max_num]
            candidates_full = [(c, os.path.getmtime(os.path.join(self.plog_root, c))) for c in candidates]
            candidates_full.sort(key=lambda t: t[1], reverse=True)
            chosen = candidates_full[0][0]
            return chosen

        # If fresh session requested: pick next sequential participant number (P_01 -> P_02 -> ...)
        if self.fresh_session:
            try:
                max_num = 0
                for d in dirs:
                    m = re.match(r'^[Pp]_?(\d+)', d)
                    if m:
                        try:
                            n = int(m.group(1))
                            if n > max_num:
                                max_num = n
                        except Exception:
                            continue
                next_num = max_num + 1 if max_num >= 0 else 1
                participant_id = f"P_{next_num:02d}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                return participant_id
            except Exception:
                return f"P_01_{datetime.now().strftime('%Y%m%d_%H%M')}"

        # Fallback: try to continue the most recent participant with incomplete state
        if not self.fresh_session:
            try:
                dirs_full = [os.path.join(self.plog_root, d) for d in dirs]
                dirs_full.sort(key=lambda p: os.path.getmtime(p), reverse=True)
                for p in dirs_full:
                    candidate = os.path.join(p, 'session_state.json')
                    if os.path.exists(candidate):
                        try:
                            with open(candidate, 'r', encoding='utf-8') as handle:
                                loaded = json.load(handle)
                            if isinstance(loaded, dict) and not self._is_completed_state(loaded):
                                pid = loaded.get('participant_id')
                                if pid:
                                    return pid
                        except Exception:
                            continue
            except Exception:
                pass

        # As last resort, create a new P_01 timestamped id
        return f"P_01_{datetime.now().strftime('%Y%m%d_%H%M')}"

    def _participant_dir_for(self, raw_participant_id=None, create=True):
        """Resolve a participant directory name and path.
        - If `raw_participant_id` contains '_' it's treated as full id.
        - If short like 'P01', find latest matching dir 'P01_YYYYMMDD_HHMM' or create one.
        Returns (participant_id, participant_dir, existed)
        """
        if raw_participant_id is None:
            return (None, None, False)

        # Full id provided? Only treat as full id when it matches the expected full-id pattern
        # e.g. P_01_20260621_1435 or P01_20260621_1435
        try:
            import re
            if re.match(r'^[Pp]_?\d{1,2}_\d{8}_\d{4}$', raw_participant_id):
                participant_id = raw_participant_id
                participant_dir = os.path.join(self.plog_root, participant_id)
                existed = os.path.isdir(participant_dir)
                if not existed and create:
                    os.makedirs(participant_dir, exist_ok=True)
                return (participant_id, participant_dir, existed)
        except Exception:
            pass

        # Short id: search for existing directories matching the prefix.
        # Match flexibly by comparing names with underscores removed so 'P_01' matches 'P01_...'.
        prefix = raw_participant_id
        norm_prefix = prefix.replace('_', '').lower()
        candidates = []
        try:
            for d in os.listdir(self.plog_root):
                full = os.path.join(self.plog_root, d)
                if not os.path.isdir(full):
                    continue
                d_norm = d.replace('_', '').lower()
                if d_norm.startswith(norm_prefix):
                    candidates.append((d, os.path.getmtime(full)))
        except Exception:
            candidates = []

        if candidates:
            candidates.sort(key=lambda t: t[1], reverse=True)
            chosen = candidates[0][0]
            participant_id = chosen
            participant_dir = os.path.join(self.plog_root, participant_id)
            return (participant_id, participant_dir, True)

        # Not found -> create new
        participant_id = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        participant_dir = os.path.join(self.plog_root, participant_id)
        if create:
            os.makedirs(participant_dir, exist_ok=True)
        return (participant_id, participant_dir, False)

    def _now_text(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _atomic_write_json(self, path, data):
        target_dir = os.path.dirname(path)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
        temp_path = f"{path}.tmp"
        with open(temp_path, 'w', encoding='utf-8') as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)

    def _load_session_archive(self):
        # Archive concept removed; per-participant session files are used.
        loaded_state = self._load_state_file_raw()
        return {
            'current_session': loaded_state,
            'session_history': [],
        }

    def _build_new_session_state(self, scenario_order):
        return {
            'participant_id': self.participant_id,
            'scenario_order': list(scenario_order),
            'current_state': {
                'next_scenario_index': 0,
                'current_scenario_name': None,
                'current_run_number': None,
                'current_status': 'NOT_STARTED',
                'comment': 'Index des nächsten zu startenden Szenarios aus der Liste',
            },
            'scenarios_log': [],
        }

    def _load_or_initialize_session_state(self, scenario_order):
        # If the user provided a participant id, try to attach to an existing participant.
        if self.participant_id is not None:
            # First check if a matching participant folder already exists (do not create yet)
            full_pid, participant_dir, existed = self._participant_dir_for(self.participant_id, create=False)
            if existed:
                # attach to existing
                self.participant_id = full_pid
            else:
                print(f"[SessionRunner] No participant found for '{self.participant_id}'. Aborting.")
                sys.exit(1)
        else:
            self.participant_id = self._default_participant_id()

        loaded_state = None if self.fresh_session else self._load_state_file()
        if loaded_state and loaded_state.get('participant_id') == self.participant_id and not self._is_completed_state(loaded_state):
            self.session_state = loaded_state
            if 'scenario_order' not in self.session_state:
                self.session_state['scenario_order'] = list(scenario_order)
            if 'current_state' not in self.session_state:
                self.session_state['current_state'] = {
                    'next_scenario_index': 0,
                    'current_scenario_name': None,
                    'current_run_number': None,
                    'current_status': 'NOT_STARTED',
                    'comment': 'Index des nächsten zu startenden Szenarios aus der Liste',
                }
            if 'scenarios_log' not in self.session_state:
                self.session_state['scenarios_log'] = []
        else:
            self.session_state = self._build_new_session_state(scenario_order)

        if self.start_index_override is not None:
            self.session_state['current_state']['next_scenario_index'] = max(0, int(self.start_index_override))

        self._save_session_state()

    def _save_session_state(self):
        if self.session_state is None:
            return
        # Write only per-participant session_state.json into _plog/<participant_id>/session_state.json
        try:
            participant_id = self.session_state.get('participant_id') or self.participant_id
            if participant_id:
                participant_dir = os.path.join(self.plog_root, participant_id)
                os.makedirs(participant_dir, exist_ok=True)
                participant_path = os.path.join(participant_dir, 'session_state.json')
                self._atomic_write_json(participant_path, self.session_state)
        except Exception:
            pass

    def _scenario_run_count(self, scenario_name):
        if self.session_state is None:
            return 0
        return sum(1 for entry in self.session_state['scenarios_log'] if entry.get('scenario_name') == f'events_{scenario_name}.py')

    def _record_scenario_start(self, scenario_name, scenario_index):
        run_number = self._scenario_run_count(scenario_name) + 1
        entry = {
            'scenario_name': f'events_{scenario_name}.py',
            'run_number': run_number,
            'started_at': self._now_text(),
            'duration_seconds': None,
            'status': 'STARTED',
            'error_message': None,
            'ended_at': None,
            'scenario_index': scenario_index,
        }
        self.session_state['scenarios_log'].append(entry)
        self.session_state['current_state'].update({
            'next_scenario_index': scenario_index,
            'current_scenario_name': scenario_name,
            'current_run_number': run_number,
            'current_status': 'STARTED',
        })
        self._save_session_state()
        return run_number

    def _record_scenario_result(self, scenario_name, run_number, scenario_index, status, started_at_text, error_message=None, advance_next_index=False):
        duration_seconds = None
        try:
            duration_seconds = max(0.0, time.time() - time.mktime(datetime.strptime(started_at_text, '%Y-%m-%d %H:%M:%S').timetuple()))
        except Exception:
            duration_seconds = None

        for entry in reversed(self.session_state['scenarios_log']):
            if entry.get('scenario_name') == f'events_{scenario_name}.py' and entry.get('run_number') == run_number:
                entry['status'] = status
                entry['error_message'] = error_message
                entry['ended_at'] = self._now_text()
                entry['duration_seconds'] = duration_seconds
                break

        if advance_next_index:
            self.session_state['current_state']['next_scenario_index'] = scenario_index + 1
        else:
            self.session_state['current_state']['next_scenario_index'] = scenario_index
        self.session_state['current_state']['current_status'] = status
        if status in ('COMPLETED', 'SKIPPED_MISSING'):
            self.session_state['current_state']['current_scenario_name'] = None
            self.session_state['current_state']['current_run_number'] = None
        else:
            self.session_state['current_state']['current_scenario_name'] = scenario_name
            self.session_state['current_state']['current_run_number'] = run_number
        self._save_session_state()

    def _mark_scenario_completed(self, scenario_name, run_number, scenario_index, started_at_text):
        self._record_scenario_result(scenario_name, run_number, scenario_index, 'COMPLETED', started_at_text, None, advance_next_index=True)

    def _mark_scenario_failed(self, scenario_name, run_number, scenario_index, started_at_text, error_message):
        self._record_scenario_result(scenario_name, run_number, scenario_index, 'FAILED_OR_ABORTED', started_at_text, error_message, advance_next_index=False)

    def _mark_scenario_skipped(self, scenario_name, run_number, scenario_index, started_at_text, error_message):
        self._record_scenario_result(scenario_name, run_number, scenario_index, 'SKIPPED_MISSING', started_at_text, error_message, advance_next_index=True)

    def _scenario_signal_paths(self, scenario_name):
        signal_dir = os.path.join(self.state_root, 'signals')
        os.makedirs(signal_dir, exist_ok=True)
        done_file = os.path.join(signal_dir, f'{scenario_name}_done.signal')
        stop_file = os.path.join(signal_dir, f'{scenario_name}_stop.signal')
        for path in (done_file, stop_file):
            if os.path.exists(path):
                os.remove(path)
        return done_file, stop_file

    def _connect_to_carla(self):
        print(f"Connecting to CARLA server at {self.host}:{self.port}...")
        self.client = carla.Client(self.host, self.port)
        self.client.set_timeout(30.0)
        self.world = self.client.get_world()
        self.original_settings = self.world.get_settings()
        print("Connected to CARLA server.")


    def _reset_carla_world(self):
        if self.original_settings:
            self.world.apply_settings(self.original_settings)
        # Ensure all actors that might be left are destroyed
        self.client.apply_batch([carla.command.DestroyActor(x) for x in self.world.get_actors().filter('vehicle.*')])
        self.client.apply_batch([carla.command.DestroyActor(x) for x in self.world.get_actors().filter('walker.*')])
        # Load an empty or default map to clear previous assets.
        # This is important before loading a *new* specific map for a scenario.
        self.client.load_world('Town01_Opt') # Load a known minimal map for a clean start
        self.world.wait_for_tick() # Wait until the world has applied the changes

    def _load_scenario_map_and_weather(self, scenario_name):
        config = SCENARIO_CONFIGS.get(scenario_name)
        if not config:
            print(f"[Error] No configuration found for scenario: {scenario_name}. Skipping setup.")
            return

        target_map = config["map"]
        target_weather = config["weather"]

        print(f"Loading map '{target_map}' for scenario '{scenario_name}'...")
        try:
            self.world = self.client.load_world(target_map)
            self.world.wait_for_tick() # Wait until the map is loaded
            print(f"Map '{target_map}' loaded successfully.")
        except Exception as e:
            print(f"[Error] Failed to load map '{target_map}': {e}. Using current map.")
            self.world = self.client.get_world() # Fallback to current world if loading fails

        print(f"Setting weather to '{target_weather}' for scenario '{scenario_name}'...")
        self.world.set_weather(target_weather)
        print("Weather set.")


    def _run_manual_control(self, scenario_name, stop_file):
        print(f"Starting manual_control.py for scenario: {scenario_name}...")
        script_path = os.path.join(os.path.dirname(__file__), 'manual_control.py')
        
        cmd = [
            sys.executable,
            script_path,
            '--host', self.host,
            '--port', str(self.port),
            '--scenario-stop-file', stop_file,
            '--profile', use_profile,
        ]
        if scenario_name == 'scenario03':
            cmd.append('--enable-brake-warning')
        if scenario_name == 'scenario06':
            cmd.append('--enable-fuel-empty-warning')
        manual_control_process = subprocess.Popen(cmd)
        return manual_control_process

    def _run_events_scenario(self, scenario_name, done_file):
        print(f"Starting events_scenario file for scenario: {scenario_name}...")
        script_path = os.path.join(os.path.dirname(__file__), 'scenario_events', f'events_{scenario_name}.py')
        if not os.path.exists(script_path):
            print(f"[Warning] events file not found for {scenario_name}: {script_path}")
            return None
        cmd = [
            sys.executable,
            script_path,
            '--host', self.host,
            '--port', str(self.port),
            '--tm-port', '8000',
            '--done-file', done_file,
        ]
        return subprocess.Popen(cmd)
    
    def _run_rear_view(self):
        print("Starting rear_view.py...")
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, 'rear_view.py')

        if not os.path.exists(script_path):
            print(f"[Error] rear_view.py not available via: {script_path}")
            return None

        cmd = [
            sys.executable,
            script_path,
        ]
        
        return subprocess.Popen(cmd, cwd=current_dir, env=os.environ)

    def _show_black_screen2(self):
        try:
            import pygame
        except Exception:
            print("[SessionRunner] pygame not available for black screen; continuing without pause.")
            return

        pygame.init()
        try:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
            pygame.display.set_caption("CARLA Session Runner - Black Screen")
            hwnd = get_pygame_window_hwnd(pygame)
            if hwnd:
                apply_borderless_style_windows(hwnd)
            screen.fill((0, 0, 0))
            pygame.display.flip()
            pygame.mouse.set_visible(False)
            self._black_screen_pygame = pygame
            self._black_screen_active = True
            print("[SessionRunner] Black screen displayed fullscreen.")
            return
        finally:
            pass
        
    def _show_black_screen(self):
        try:
            import pygame
        except Exception:
            print("[SessionRunner] pygame not available for black screen; continuing without pause.")
            return
        
        try:
            from screeninfo import get_monitors
        except Exception:
            get_monitors = None

        try:
            with open("config.yaml", "r") as f:
                cfg = yaml.load(f, Loader=yaml.FullLoader)
            sim_display_name = cfg["monitor"]["simulator"]  # e.g. "\\\\.\\DISPLAY1"
        except Exception as e:
            print(f"[SessionRunner] Could not load monitor.simulator from config.yaml: {e}")
            sim_display_name = None

        pygame.init()
        try:
            target_x = target_y = 0
            target_w = target_h = 0
            monitor_index = 0
            found = False

            if sim_display_name and get_monitors is not None:
                for i, m in enumerate(get_monitors()):
                    if getattr(m, "name", None) == sim_display_name:
                        target_x = m.x
                        target_y = m.y
                        target_w = m.width
                        target_h = m.height
                        monitor_index = i
                        found = True
                        break

            if not found:
                print("[SessionRunner] Target monitor not found via screeninfo; falling back to default fullscreen.")
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
            else:
                os.environ['SDL_VIDEO_WINDOW_POS'] = f"{target_x},{target_y}"
                screen = pygame.display.set_mode((target_w, target_h), pygame.FULLSCREEN | pygame.DOUBLEBUF, display=monitor_index)

            pygame.display.set_caption("CARLA Session Runner - Black Screen")

            try:
                hwnd = get_pygame_window_hwnd(pygame)
                if hwnd:
                    apply_borderless_style_windows(hwnd)
            except Exception:
                pass

            screen.fill((0, 0, 0))
            pygame.display.flip()
            pygame.mouse.set_visible(False)

            self._black_screen_pygame = pygame
            self._black_screen_active = True
            print("[SessionRunner] Black screen displayed fullscreen on configured simulator monitor." if found else "[SessionRunner] Black screen displayed fullscreen (fallback).")
            return
        finally:
            pass

    def _destroy_black_screen(self):
        if not self._black_screen_active:
            return

        pygame_module = self._black_screen_pygame
        self._black_screen_active = False
        self._black_screen_pygame = None

        if pygame_module is None:
            return

        try:
            pygame_module.mouse.set_visible(True)
        except Exception:
            pass

        try:
            pygame_module.display.quit()
        except Exception:
            pass

        try:
            pygame_module.quit()
        except Exception:
            pass

    def _wait_for_process(self, process, label):
        process.wait()
        print(f"{label} finished.")
        if process.returncode != 0:
            print(f"[Warning] {label} exited with code {process.returncode}")

    def _monitor_scenario_processes(self, scenario_name, scenario_index, manual_control_process, events_process, done_file, stop_file, run_number, started_at_text):
        while True:
            manual_code = manual_control_process.poll()
            events_code = events_process.poll()
            if os.path.exists(done_file):
                with open(stop_file, 'w', encoding='utf-8') as handle:
                    handle.write('stop\n')
                break
            if manual_code is not None:
                self._mark_scenario_failed(
                    scenario_name,
                    run_number,
                    scenario_index,
                    started_at_text,
                    f'manual_control exited prematurely with code {manual_code}',
                )
                try:
                    if events_process.poll() is None:
                        events_process.terminate()
                except Exception:
                    pass
                manual_control_process.wait(timeout=5)
                if events_process.poll() is None:
                    events_process.wait(timeout=5)
                return False
            if events_code is not None:
                self._mark_scenario_failed(
                    scenario_name,
                    run_number,
                    scenario_index,
                    started_at_text,
                    f'events process exited prematurely with code {events_code}',
                )
                try:
                    if manual_control_process.poll() is None:
                        manual_control_process.terminate()
                except Exception:
                    pass
                if manual_control_process.poll() is None:
                    manual_control_process.wait(timeout=5)
                return False
            time.sleep(0.25)

        self._wait_for_process(manual_control_process, 'manual_control.py')
        self._wait_for_process(events_process, f"events_{scenario_name}.py")
        self._mark_scenario_completed(scenario_name, run_number, scenario_index, started_at_text)
        return True

    def _monitor_scenario_processes_no_logging(self, scenario_name, manual_control_process, events_process, done_file, stop_file):
        """Monitor processes without writing session state or logs. Returns True if completed normally."""
        while True:
            manual_code = manual_control_process.poll()
            events_code = events_process.poll()
            if os.path.exists(done_file):
                try:
                    with open(stop_file, 'w', encoding='utf-8') as handle:
                        handle.write('stop\n')
                except Exception:
                    pass
                break
            if manual_code is not None:
                print(f"[SessionRunner] manual_control exited prematurely with code {manual_code}")
                try:
                    if events_process.poll() is None:
                        events_process.terminate()
                except Exception:
                    pass
                try:
                    manual_control_process.wait(timeout=5)
                except Exception:
                    pass
                try:
                    if events_process.poll() is None:
                        events_process.wait(timeout=5)
                except Exception:
                    pass
                return False
            if events_code is not None:
                print(f"[SessionRunner] events process exited prematurely with code {events_code}")
                try:
                    if manual_control_process.poll() is None:
                        manual_control_process.terminate()
                except Exception:
                    pass
                try:
                    if manual_control_process.poll() is None:
                        manual_control_process.wait(timeout=5)
                except Exception:
                    pass
                return False
            time.sleep(0.25)

        self._wait_for_process(manual_control_process, 'manual_control.py')
        self._wait_for_process(events_process, f"events_{scenario_name}.py")
        print(f"[SessionRunner] Scenario '{scenario_name}' completed (no-logging mode).")
        return True

    def _run_scenario_pair(self, scenario_name):
        done_file, stop_file = self._scenario_signal_paths(scenario_name)
        script_path = os.path.join(os.path.dirname(__file__), 'scenario_events', f'events_{scenario_name}.py')
        if not os.path.exists(script_path):
            print(f"[SessionRunner] Skipping scenario '{scenario_name}' because its event file is missing: {script_path}")
            started_at_text = self._now_text()
            run_number = self._record_scenario_start(scenario_name, self.session_state['current_state']['next_scenario_index'])
            self._mark_scenario_skipped(
                scenario_name,
                run_number,
                self.session_state['current_state']['next_scenario_index'],
                started_at_text,
                f'missing events file: {script_path}',
            )
            return

        scenario_index = int(self.session_state['current_state']['next_scenario_index'])
        run_number = self._record_scenario_start(scenario_name, scenario_index)
        started_at_text = self.session_state['scenarios_log'][-1]['started_at']

        rear_view_process = self._run_rear_view()

        manual_control_process = self._run_manual_control(scenario_name, stop_file)
        if self._black_screen_active:
            self._destroy_black_screen()
        events_process = self._run_events_scenario(scenario_name, done_file)

        if events_process is None:
            try:
                rear_view_process.terminate()
            except Exception:
                pass

            self._mark_scenario_skipped(
                scenario_name,
                run_number,
                scenario_index,
                started_at_text,
                f'missing events file: {script_path}',
            )
            try:
                manual_control_process.terminate()
                manual_control_process.wait(timeout=5)
            except Exception:
                pass
            return

        completed = self._monitor_scenario_processes(
            scenario_name,
            scenario_index,
            manual_control_process,
            events_process,
            done_file,
            stop_file,
            run_number,
            started_at_text,
        )
        try:
            if rear_view_process and rear_view_process.poll() is None:
                print("Stopping rear_view.py...")
                rear_view_process.terminate()
                rear_view_process.wait(timeout=3)
        except Exception as e:
            print(f"[Warning] Could not terminate rear_view.py: {e}")

        if completed:
            self._show_black_screen()
            print(f"[SessionRunner] Scenario {scenario_index + 1} completed for {self.participant_id}, start survey. Enter to continue.")
            input()

        for path in (done_file, stop_file):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass

    def _run_single_scenario(self, scenario_name):
        """Run a single scenario once without modifying session state or logs."""
        done_file, stop_file = self._scenario_signal_paths(scenario_name)
        script_path = os.path.join(os.path.dirname(__file__), 'scenario_events', f'events_{scenario_name}.py')
        if not os.path.exists(script_path):
            print(f"[SessionRunner] events file not found for single-run scenario '{scenario_name}': {script_path}")
            return

        rear_view_process = self._run_rear_view()

        manual_control_process = self._run_manual_control(scenario_name, stop_file)
        if self._black_screen_active:
            self._destroy_black_screen()
        events_process = self._run_events_scenario(scenario_name, done_file)

        if events_process is None:
            try:
                if rear_view_process and rear_view_process.poll() is None:
                    rear_view_process.terminate()
            except Exception:
                pass
            try:
                if manual_control_process and manual_control_process.poll() is None:
                    manual_control_process.terminate()
                    manual_control_process.wait(timeout=5)
            except Exception:
                pass
            return

        completed = self._monitor_scenario_processes_no_logging(
            scenario_name,
            manual_control_process,
            events_process,
            done_file,
            stop_file,
        )

        try:
            if rear_view_process and rear_view_process.poll() is None:
                rear_view_process.terminate()
                rear_view_process.wait(timeout=3)
        except Exception:
            pass

        for path in (done_file, stop_file):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass

        if completed:
            print(f"[SessionRunner] Single scenario '{scenario_name}' completed.")

    def run_session(self):
        print("Starting CARLA session runner...")

        if self.target_scenario:
            print(f"Running single scenario: {self.target_scenario}")
            # Ensure a collection participant folder P_00_<timestamp> exists for single-scenario runs
            try:
                pid = f"P_00_{datetime.now().strftime('%Y%m%d_%H%M')}"
                self.participant_id = pid
                participant_dir = os.path.join(self.plog_root, pid)
                os.makedirs(participant_dir, exist_ok=True)
                # initialize a minimal session_state for this collected scenario
                try:
                    state = self._build_new_session_state([self.target_scenario])
                    # mark that it's not started yet
                    state['current_state']['next_scenario_index'] = 0
                    state['current_state']['current_status'] = 'NOT_STARTED'
                    participant_path = os.path.join(participant_dir, 'session_state.json')
                    self._atomic_write_json(participant_path, state)
                except Exception:
                    pass
            except Exception:
                pass
            try:
                self._connect_to_carla()
                self._load_scenario_map_and_weather(self.target_scenario)
                self._run_single_scenario(self.target_scenario)
            except Exception as e:
                print(f"[CRITICAL ERROR] Single scenario run failed: {e}")
            finally:
                self._destroy_black_screen()
                if self.world:
                    self._reset_carla_world()
                if self.background_window_process and self.background_window_process.poll() is None:
                    self.background_window_process.terminate()
                    self.background_window_process.wait(2)
            return

        try:
            self._connect_to_carla()
            
            # Prepare scenario order
            all_scenarios = list(SCENARIO_CONFIGS.keys())
            
            # scenario00 must always come first
            if "scenario00" in all_scenarios:
                all_scenarios.remove("scenario00")
                all_scenarios.remove("scenario02")
                random.shuffle(all_scenarios)
                scenario_order = ["scenario00"] + all_scenarios + ["scenario02"]
            else:
                random.shuffle(all_scenarios)
                scenario_order = all_scenarios

            self._load_or_initialize_session_state(scenario_order)
            print(f"[SessionRunner] Participant ID: {self.participant_id}")
            scenario_order = list(self.session_state.get('scenario_order', scenario_order))
            print(f"Scenario order for this session: {scenario_order}")

            start_index = int(self.session_state['current_state'].get('next_scenario_index', 0))
            if start_index >= len(scenario_order):
                print("[SessionRunner] Session already completed according to state file.")
                return

            for i in range(start_index, len(scenario_order)):
                scenario_name = scenario_order[i]
                config = SCENARIO_CONFIGS.get(scenario_name)
                if not config:
                    print(f"[Error] No configuration found for scenario: {scenario_name}. Skipping setup.")
                    return
                description = config["description"]

                print(f"\n--- Running Scenario {i+1}/{len(scenario_order)}: {scenario_name} ({description}) for {self.participant_id}---")
                
                # Set up the world for the current scenario
                self._load_scenario_map_and_weather(scenario_name)
                
                # Start manual_control first, then the scenario file.
                self._run_scenario_pair(scenario_name)

                if self.session_state['current_state'].get('current_status') == 'FAILED_OR_ABORTED':
                    print(f"[SessionRunner] Scenario '{scenario_name}' failed or aborted. Resume later with the same state file.")
                    break

        except Exception as e:
            print(f"[CRITICAL ERROR] Session runner failed: {e}")
            if self.session_state is not None:
                try:
                    self.session_state['current_state']['current_status'] = 'FAILED_OR_ABORTED'
                    self._save_session_state()
                except Exception:
                    pass
        finally:
            self._destroy_black_screen()
            if self.world:
                self._reset_carla_world() # Clean up at the end
            if self.background_window_process and self.background_window_process.poll() is None:
                self.background_window_process.terminate()
                self.background_window_process.wait(2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CARLA Session Runner')
    parser.add_argument('--host', default='127.0.0.1', help='IP of the host server (default: 127.0.0.1)')
    parser.add_argument('--port', default=2000, type=int, help='TCP port to listen to (default: 2000)')
    parser.add_argument('--participant-id', default=None, help='participant identifier used in the session JSON (auto-generated when omitted)')
    parser.add_argument('--state-file', default=None, help='path to the JSON session state file')
    parser.add_argument('--start-index', default=None, type=int, help='override next_scenario_index for repeat/continue (0-based; 2 starts at the 3rd scenario)')
    parser.add_argument('--fresh-session', '--new-session', '--new', dest='fresh_session', action='store_true', help='force a new participant/session even if an existing state file is present')
    parser.add_argument('--scenario', default=None, help='NEW => "scenario01')
    # --scenario => creates participant P00

    args = parser.parse_args()
    
    runner = SessionRunner(args.host, args.port, args.participant_id, args.state_file, args.start_index, args.fresh_session, args.scenario)
    runner.run_session()

