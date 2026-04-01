#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

# Allows controlling a vehicle with a keyboard. For a simpler and more
# documented example, please take a look at tutorial.py.

"""
Welcome to CARLA manual control.

Use ARROWS or WASD keys for control.

    W            : throttle
    S            : brake
    A/D          : steer left/right
    Q            : toggle reverse
    Space        : hand-brake
    P            : toggle autopilot
    M            : toggle manual transmission
    ,/.          : gear up/down
    CTRL + W     : toggle constant velocity mode at 60 km/h

    L            : toggle next light type
    SHIFT + L    : toggle high beam
    Z/X          : toggle right/left blinker
    I            : toggle interior light

    TAB          : change sensor position
    ` or N       : next sensor
    [1-9]        : change to sensor [1-9]
    G            : toggle radar visualization
    C            : change weather (Shift+C reverse)
    Backspace    : change vehicle

    O            : open/close all doors of vehicle
    T            : toggle vehicle's telemetry

    V            : Select next map layer (Shift+V reverse)
    B            : Load current selected map layer (Shift+B to unload)
    Y            : export current performance row for Excel (overwrite file)

    R            : toggle recording images to disk

    CTRL + R     : toggle recording of simulation (replacing any previous)
    CTRL + P     : start replaying last recorded simulation
    CTRL + +     : increments the start time of the replay by 1 second (+SHIFT = 10 seconds)
    CTRL + -     : decrements the start time of the replay by 1 second (+SHIFT = 10 seconds)

    F1           : toggle HUD
    F2           : toggle camera resolution (100% <-> --sp)
    H/?          : toggle help
    ESC          : quit
"""

from __future__ import print_function


# ==============================================================================
# -- find carla module ---------------------------------------------------------
# ==============================================================================


import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================


import carla

from carla import ColorConverter as cc

import argparse
import collections
from collections import deque
import datetime
import logging
import math
import random
import re
import subprocess
import time
import weakref

os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
os.environ["SDL_GAMECONTROLLER_ALLOW_BACKGROUND_EVENTS"] = "1"

try:
    import pygame.mixer
    import pygame
    from pygame.locals import KMOD_CTRL
    from pygame.locals import KMOD_SHIFT
    from pygame.locals import K_0
    from pygame.locals import K_9
    from pygame.locals import K_BACKQUOTE
    from pygame.locals import K_BACKSPACE
    from pygame.locals import K_COMMA
    from pygame.locals import K_DOWN
    from pygame.locals import K_ESCAPE
    from pygame.locals import K_F1
    from pygame.locals import K_F2
    from pygame.locals import K_LEFT
    from pygame.locals import K_PERIOD
    from pygame.locals import K_RIGHT
    from pygame.locals import K_SLASH
    from pygame.locals import K_SPACE
    from pygame.locals import K_TAB
    from pygame.locals import K_UP
    from pygame.locals import K_a
    from pygame.locals import K_b
    from pygame.locals import K_c
    from pygame.locals import K_d
    from pygame.locals import K_f
    from pygame.locals import K_g
    from pygame.locals import K_h
    from pygame.locals import K_i
    from pygame.locals import K_l
    from pygame.locals import K_m
    from pygame.locals import K_n
    from pygame.locals import K_o
    from pygame.locals import K_p
    from pygame.locals import K_q
    from pygame.locals import K_r
    from pygame.locals import K_s
    from pygame.locals import K_t
    from pygame.locals import K_v
    from pygame.locals import K_w
    from pygame.locals import K_x
    from pygame.locals import K_y
    from pygame.locals import K_z
    from pygame.locals import K_MINUS
    from pygame.locals import K_EQUALS


except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed')

from typing import Optional
from generate_audio import AudioGenerator, DummyAudioGenerator
from dashboard_renderer import DashboardRenderer
from event_sync import EventSync

# ==============================================================================
# -- Audio Setup  --------------------------------------------------------------
# ==============================================================================

# Audio paths
_ENGINE_IDLE = r".\audio\car_engine_idle.wav"
_ENGINE_MID = r".\audio\car_engine_mid.wav"
_ENGINE_HIGH = r".\audio\car_engine_high.wav"
_HORN_PATH = r".\audio\car_horn1_elevenlabs.wav"
_BLINKER_PATH = r".\audio\car_blinker.wav"
_BRAKE_PATH = r".\audio\car_break.wav"
_PROXIMITY_ALERT_PATH = r".\audio\car_proximityAlert.wav"

# Central audio manager
audio_manager: Optional[AudioGenerator] = None
dashboard_process: Optional[subprocess.Popen] = None

# Camera selection
USE_SCENE_FINAL_CAMERA = False

# Performance export filename
PERF_EXPORT_FILENAME = 'perf_export_row.tsv'

# Audio enable/disable flag
ENABLE_AUDIO = False

# Dashboard inside main window (bottom-left corner)
ENABLE_INSIDE_DASHBOARD = True

def _audio_init():
    """Initialize audio generator."""
    global audio_manager
    if not ENABLE_AUDIO:
        audio_manager = DummyAudioGenerator()
        return
    
    try:
        audio_manager = AudioGenerator(
            engine_idle_path=_ENGINE_IDLE,
            engine_mid_path=_ENGINE_MID,
            engine_high_path=_ENGINE_HIGH,
            horn_path=_HORN_PATH,
            blinker_path=_BLINKER_PATH,
            brake_path=_BRAKE_PATH,
            proximity_alert_path=_PROXIMITY_ALERT_PATH,
        )
        audio_manager.init(frequency=44100, channels=2, buffer_size=512)
        print("[Audio] Initialized successfully")
    except Exception as e:
        print(f"[Audio] ERROR initializing: {e}")
        audio_manager = DummyAudioGenerator()

def _audio_quit():
    """Clean up audio resources."""
    global audio_manager
    if audio_manager is not None:
        audio_manager.quit()
        audio_manager = None

def _start_dashboard_process(host: str, port: int, display_index: Optional[int] = None):
    """Start dashboard in a separate process to avoid pygame display conflicts."""
    global dashboard_process
    try:
        if dashboard_process is not None and dashboard_process.poll() is None:
            return

        script_dir = os.path.dirname(os.path.abspath(__file__))
        dashboard_script = os.path.join(script_dir, 'car_dashboard.py')
        cmd = [sys.executable, dashboard_script, '--host', host, '--port', str(port)]
        if display_index is not None and display_index >= 0:
            cmd.extend(['--display-index', str(display_index)])
        dashboard_process = subprocess.Popen(cmd, cwd=script_dir)
        print("[Dashboard] External process started")
    except Exception as e:
        dashboard_process = None
        print(f"[Dashboard] WARNING: failed to start external process: {e}")

def _stop_dashboard_process():
    """Stop dashboard process if running."""
    global dashboard_process
    if dashboard_process is None:
        return

    try:
        if dashboard_process.poll() is None:
            dashboard_process.terminate()
            dashboard_process.wait(timeout=2)
    except Exception:
        try:
            if dashboard_process.poll() is None:
                dashboard_process.kill()
        except Exception:
            pass
    finally:
        dashboard_process = None


# ==============================================================================
# -- Global functions ----------------------------------------------------------
# ==============================================================================


def find_weather_presets():
    rgx = re.compile('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')
    name = lambda x: ' '.join(m.group(0) for m in rgx.finditer(x))
    presets = [x for x in dir(carla.WeatherParameters) if re.match('[A-Z].+', x)]
    return [(getattr(carla.WeatherParameters, x), name(x)) for x in presets]


def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name

def get_actor_blueprints(world, filter, generation):
    bps = world.get_blueprint_library().filter(filter)

    if generation.lower() == "all":
        return bps

    # If the filter returns only one bp, we assume that this one needed
    # and therefore, we ignore the generation
    if len(bps) == 1:
        return bps

    try:
        int_generation = int(generation)
        # Check if generation is in available generations
        if int_generation in [1, 2, 3]:
            bps = [x for x in bps if int(x.get_attribute('generation')) == int_generation]
            return bps
        else:
            print("   Warning! Actor Generation is not valid. No actor will be spawned.")
            return []
    except:
        print("   Warning! Actor Generation is not valid. No actor will be spawned.")
        return []

def _export_performance_metrics(world):
    """
    Export current performance metrics tsv file (for Excel)
    File is overwritten on each call.
    """
    try:
        hud = world.hud
        server_avg, server_std, server_1pct = hud._compute_fps_stats(hud.server_fps_window) if len(hud.server_fps_window) > 0 else (0.0, 0.0, 0.0)
        client_avg, client_std, client_1pct = hud._compute_fps_stats(hud.client_fps_window) if len(hud.client_fps_window) > 0 else (0.0, 0.0, 0.0)

        values = [
            server_avg,
            server_std,
            server_1pct,
            client_avg,
            client_std,
            client_1pct,
            hud.real_time_factor,
            hud.server_frame_ms,
            hud.client_frame_ms,
        ]

        out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), PERF_EXPORT_FILENAME)
        with open(out_path, 'w', encoding='utf-8', newline='') as f:
            f.write('\t'.join(('%.3f' % v).replace('.', ',') for v in values) + '\n')

        print("[Performance] Perf export written: %s" % os.path.basename(out_path))
    except Exception as e:
        print("[Performance] ERROR: Perf export failed: %s" % e)

# ==============================================================================
# -- World ---------------------------------------------------------------------
# ==============================================================================

class World(object):
    def __init__(self, carla_world, hud, args):
        self.world = carla_world
        self.sync = args.sync
        self.actor_role_name = args.rolename
        self._screen_percentage = args.sp
        self._sp_upscale = args.sp_upscale
        self.event_sync: Optional[EventSync] = None
        try:
            self.map = self.world.get_map()
        except RuntimeError as error:
            print('RuntimeError: {}'.format(error))
            print('  The server could not send the OpenDRIVE (.xodr) file:')
            print('  Make sure it exists, has the same name of your town, and is correct.')
            sys.exit(1)
        self.hud = hud
        self.player = None
        self.collision_sensor = None
        self.lane_invasion_sensor = None
        self.gnss_sensor = None
        self.imu_sensor = None
        self.radar_sensor = None
        self.camera_manager = None
        self.rear_camera = None                     # rear camera for rear_view.py
        self.obstacle_sensor = None                 # Proximity alert sensor
        self.dashboard_renderer = None              # Dashboard renderer (optional)
        self._weather_presets = find_weather_presets()
        self._weather_index = 0
        self._actor_filter = args.filter
        self._actor_generation = args.generation
        self._gamma = args.gamma
        self.restart()
        self.world.on_tick(hud.on_world_tick)
        self.recording_enabled = False
        self.recording_start = 0
        self.constant_velocity_enabled = False
        self.show_vehicle_telemetry = False
        self.doors_are_open = False
        self.current_map_layer = 0
        self.map_layer_names = [
            carla.MapLayer.NONE,
            carla.MapLayer.Buildings,
            carla.MapLayer.Decals,
            carla.MapLayer.Foliage,
            carla.MapLayer.Ground,
            carla.MapLayer.ParkedVehicles,
            carla.MapLayer.Particles,
            carla.MapLayer.Props,
            carla.MapLayer.StreetLights,
            carla.MapLayer.Walls,
            carla.MapLayer.All
        ]

    def restart(self):
        self.player_max_speed = 1.589
        self.player_max_speed_fast = 3.713
        # Keep same camera config if the camera manager exists.
        cam_index = self.camera_manager.index if self.camera_manager is not None else 0
        cam_pos_index = self.camera_manager.transform_index if self.camera_manager is not None else 0
        if USE_SCENE_FINAL_CAMERA:
            cam_index = 0
            cam_pos_index = 0
        # Get a random blueprint.
        blueprint_list = get_actor_blueprints(self.world, self._actor_filter, self._actor_generation)
        if not blueprint_list:
            raise ValueError("Couldn't find any blueprints with the specified filters")
        # blueprint = random.choice(blueprint_list)
        # SET CAR TYPE
        blueprint = self.world.get_blueprint_library().find('vehicle.lincoln.mkz_2020')
        
        blueprint.set_attribute('role_name', self.actor_role_name)
        if blueprint.has_attribute('terramechanics'):
            blueprint.set_attribute('terramechanics', 'true')
        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        if blueprint.has_attribute('driver_id'):
            driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
            blueprint.set_attribute('driver_id', driver_id)
        if blueprint.has_attribute('is_invincible'):
            blueprint.set_attribute('is_invincible', 'true')
        # set the max speed
        if blueprint.has_attribute('speed'):
            self.player_max_speed = float(blueprint.get_attribute('speed').recommended_values[1])
            self.player_max_speed_fast = float(blueprint.get_attribute('speed').recommended_values[2])

        # Spawn the player.
        if self.player is not None:
            spawn_point = self.player.get_transform()
            spawn_point.location.z += 2.0
            spawn_point.rotation.roll = 0.0
            spawn_point.rotation.pitch = 0.0
            self.destroy()
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
            self.show_vehicle_telemetry = False
            self.modify_vehicle_physics(self.player)
        while self.player is None:
            if not self.map.get_spawn_points():
                print('There are no spawn points available in your map/town.')
                print('Please add some Vehicle Spawn Point to your UE4 scene.')
                sys.exit(1)
            spawn_points = self.map.get_spawn_points()
            #spawn_point = random.choice(spawn_points) if spawn_points else carla.Transform()

            # STARTING POINT                                => coordinates from UE must be divided by 100
            spawn_point = carla.Transform(
                carla.Location(x=59.6000293, y=306.420, z=0.50),
                carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0)
            )
            self.player = self.world.try_spawn_actor(blueprint, spawn_point)
            self.show_vehicle_telemetry = False
            self.modify_vehicle_physics(self.player)


        # SET WEATHER:
        # https://carla.org/Doxygen/html/db/ddb/classcarla_1_1rpc_1_1WeatherParameters.html
        self.world.set_weather(carla.WeatherParameters.Default)      #CloudyNoon

        # Set up the sensors.
        self.collision_sensor = CollisionSensor(self.player, self.hud)
        self.lane_invasion_sensor = LaneInvasionSensor(self.player, self.hud)
        self.gnss_sensor = GnssSensor(self.player)
        self.imu_sensor = IMUSensor(self.player)
        self.camera_manager = CameraManager(
            self.player,
            self.hud,
            self._gamma,
            screen_percentage=self._screen_percentage,
            upscale_filter=self._sp_upscale,
            use_scene_final=USE_SCENE_FINAL_CAMERA
        )
        self.camera_manager.transform_index = cam_pos_index
        self.camera_manager.set_sensor(cam_index, notify=False)
        actor_type = get_actor_display_name(self.player)
        self.hud.notification(actor_type)

        # --- Spawn rear camera for rear_view.py ---
        self.rear_camera = RearCamera(self.player)
        #print("Rear Camera spawned with ID:", self.rear_camera.sensor.id)
        
        # --- Spawn obstacle detection sensor for proximity alerts ---
        if isinstance(self.player, carla.Vehicle):
            self.obstacle_sensor = ObstacleDetectionSensor(self.player)

        if self.sync:
            self.world.tick()
        else:
            self.world.wait_for_tick()

    # def next_weather(self, reverse=False):
    #     self._weather_index += -1 if reverse else 1
    #     self._weather_index %= len(self._weather_presets)
    #     preset = self._weather_presets[self._weather_index]
    #     self.hud.notification('Weather: %s' % preset[1])
    #     self.player.get_world().set_weather(preset[0])

    def next_map_layer(self, reverse=False):
        self.current_map_layer += -1 if reverse else 1
        self.current_map_layer %= len(self.map_layer_names)
        selected = self.map_layer_names[self.current_map_layer]
        self.hud.notification('LayerMap selected: %s' % selected)

    def load_map_layer(self, unload=False):
        selected = self.map_layer_names[self.current_map_layer]
        if unload:
            self.hud.notification('Unloading map layer: %s' % selected)
            self.world.unload_map_layer(selected)
        else:
            self.hud.notification('Loading map layer: %s' % selected)
            self.world.load_map_layer(selected)

    def toggle_radar(self):
        if self.radar_sensor is None:
            self.radar_sensor = RadarSensor(self.player)
        elif self.radar_sensor.sensor is not None:
            self.radar_sensor.sensor.destroy()
            self.radar_sensor = None

    def modify_vehicle_physics(self, actor):
        #If actor is not a vehicle, we cannot use the physics control
        try:
            physics_control = actor.get_physics_control()
            physics_control.use_sweep_wheel_collision = True
            actor.apply_physics_control(physics_control)
        except Exception:
            pass

    def tick(self, clock):
        self.hud.tick(self, clock)
        # Update dashboard renderer if enabled
        if self.dashboard_renderer is not None:
            dt = clock.get_time() / 1000.0  # Convert ms to seconds
            self.dashboard_renderer.update(dt)

    def render(self, display):
        self.camera_manager.render(display)
        # Render HUD or dashboard based on flag
        if ENABLE_INSIDE_DASHBOARD:
            if self.dashboard_renderer is not None:
                self.dashboard_renderer.render(display)
        else:
            self.hud.render(display)

    def destroy_sensors(self):
        self.camera_manager.sensor.destroy()
        self.camera_manager.sensor = None
        self.camera_manager.index = None

    def destroy(self):
        if self.radar_sensor is not None:
            self.toggle_radar()
        sensors = [
            self.camera_manager.sensor,
            self.collision_sensor.sensor,
            self.lane_invasion_sensor.sensor,
            self.gnss_sensor.sensor,
            self.imu_sensor.sensor]
        
        # Add obstacle sensors to cleanup
        if self.obstacle_sensor is not None:
            if self.obstacle_sensor.sensor_front is not None:
                sensors.append(self.obstacle_sensor.sensor_front)
            if self.obstacle_sensor.sensor_rear is not None:
                sensors.append(self.obstacle_sensor.sensor_rear)
        
        for sensor in sensors:
            if sensor is not None:
                sensor.stop()
                sensor.destroy()
        if self.player is not None:
            self.player.destroy()


# ==============================================================================
# -- KeyboardControl -----------------------------------------------------------
# ==============================================================================

class KeyboardControl(object):
    """Class that handles keyboard input."""
    def __init__(self, world, start_in_autopilot):
        self._autopilot_enabled = start_in_autopilot
        self._ackermann_enabled = False
        self._ackermann_reverse = 1
        if isinstance(world.player, carla.Vehicle):
            self._control = carla.VehicleControl()
            self._ackermann_control = carla.VehicleAckermannControl()
            self._lights = carla.VehicleLightState.NONE
            world.player.set_autopilot(self._autopilot_enabled)
            world.player.set_light_state(self._lights)
        elif isinstance(world.player, carla.Walker):
            self._control = carla.WalkerControl()
            self._autopilot_enabled = False
            self._rotation = world.player.get_transform().rotation
        else:
            raise NotImplementedError("Actor type not supported")
        self._steer_cache = 0.0
        self._prev_brake = False
        self._left_blinker_until = 0.0
        self._right_blinker_until = 0.0
        world.hud.notification("Press 'H' or '?' for help.", seconds=4.0)

    def _get_blinker_duration(self, world):
        if world is None or world.event_sync is None:
            raise RuntimeError("Blinker duration not found: world.event_sync is None")

        try:
            duration = float(world.event_sync.default_blink_duration)
        except Exception as exc:
            raise RuntimeError("Blinker duration not found: invalid world.event_sync.default_blink_duration") from exc

        return max(0.1, duration)

    def parse_events(self, client, world, clock, sync_mode):
        if isinstance(self._control, carla.VehicleControl):
            current_lights = self._lights
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            
            if event.type == pygame.KEYDOWN:

                if event.key == K_h:
                    # Horn: play while held down
                    if audio_manager is not None:
                        audio_manager.play_horn()

            elif event.type == pygame.KEYUP:

                if self._is_quit_shortcut(event.key):
                    return True
                elif event.key == K_BACKSPACE:
                    if self._autopilot_enabled:
                        world.player.set_autopilot(False)
                        world.restart()
                        world.player.set_autopilot(True)
                    else:
                        world.restart()
                elif event.key == K_F1:
                    world.hud.toggle_info()
                elif event.key == K_F2:
                    world.camera_manager.toggle_screen_percentage()
                elif event.key == K_v and pygame.key.get_mods() & KMOD_SHIFT:
                    world.next_map_layer(reverse=True)
                elif event.key == K_v:
                    world.next_map_layer()
                elif event.key == K_b and pygame.key.get_mods() & KMOD_SHIFT:
                    world.load_map_layer(unload=True)
                elif event.key == K_b:
                    world.load_map_layer()
                elif event.key == K_SLASH and (pygame.key.get_mods() & KMOD_SHIFT):        #K_h or 
                    world.hud.help.toggle()
                elif event.key == K_TAB:
                    world.camera_manager.toggle_camera()
                elif event.key == K_c and pygame.key.get_mods() & KMOD_SHIFT:
                    world.next_weather(reverse=True)
                elif event.key == K_c:
                    world.next_weather()
                elif event.key == K_g:
                    world.toggle_radar()
                elif event.key == K_BACKQUOTE:
                    world.camera_manager.next_sensor()
                elif event.key == K_n:
                    world.camera_manager.next_sensor()
                elif event.key == K_w and (pygame.key.get_mods() & KMOD_CTRL):
                    if world.constant_velocity_enabled:
                        world.player.disable_constant_velocity()
                        world.constant_velocity_enabled = False
                        world.hud.notification("Disabled Constant Velocity Mode")
                    else:
                        world.player.enable_constant_velocity(carla.Vector3D(17, 0, 0))
                        world.constant_velocity_enabled = True
                        world.hud.notification("Enabled Constant Velocity Mode at 60 km/h")
                elif event.key == K_o:
                    try:
                        if world.doors_are_open:
                            world.hud.notification("Closing Doors")
                            world.doors_are_open = False
                            world.player.close_door(carla.VehicleDoor.All)
                        else:
                            world.hud.notification("Opening doors")
                            world.doors_are_open = True
                            world.player.open_door(carla.VehicleDoor.All)
                    except Exception:
                        pass
                elif event.key == K_t:
                    if world.show_vehicle_telemetry:
                        world.player.show_debug_telemetry(False)
                        world.show_vehicle_telemetry = False
                        world.hud.notification("Disabled Vehicle Telemetry")
                    else:
                        try:
                            world.player.show_debug_telemetry(True)
                            world.show_vehicle_telemetry = True
                            world.hud.notification("Enabled Vehicle Telemetry")
                        except Exception:
                            pass
                elif event.key == K_y:
                    _export_performance_metrics(world)
                elif event.key > K_0 and event.key <= K_9:
                    index_ctrl = 0
                    if pygame.key.get_mods() & KMOD_CTRL:
                        index_ctrl = 9
                    world.camera_manager.set_sensor(event.key - 1 - K_0 + index_ctrl)
                elif event.key == K_r and not (pygame.key.get_mods() & KMOD_CTRL):
                    world.camera_manager.toggle_recording()
                elif event.key == K_r and (pygame.key.get_mods() & KMOD_CTRL):
                    if (world.recording_enabled):
                        client.stop_recorder()
                        world.recording_enabled = False
                        world.hud.notification("Recorder is OFF")
                    else:
                        client.start_recorder("manual_recording.rec")
                        world.recording_enabled = True
                        world.hud.notification("Recorder is ON")
                elif event.key == K_p and (pygame.key.get_mods() & KMOD_CTRL):
                    # stop recorder
                    client.stop_recorder()
                    world.recording_enabled = False
                    # work around to fix camera at start of replaying
                    current_index = world.camera_manager.index
                    world.destroy_sensors()
                    # disable autopilot
                    self._autopilot_enabled = False
                    world.player.set_autopilot(self._autopilot_enabled)
                    world.hud.notification("Replaying file 'manual_recording.rec'")
                    # replayer
                    client.replay_file("manual_recording.rec", world.recording_start, 0, 0)
                    world.camera_manager.set_sensor(current_index)
                elif event.key == K_MINUS and (pygame.key.get_mods() & KMOD_CTRL):
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        world.recording_start -= 10
                    else:
                        world.recording_start -= 1
                    world.hud.notification("Recording start time is %d" % (world.recording_start))
                elif event.key == K_EQUALS and (pygame.key.get_mods() & KMOD_CTRL):
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        world.recording_start += 10
                    else:
                        world.recording_start += 1
                    world.hud.notification("Recording start time is %d" % (world.recording_start))

                # Horn control: stop horn when key is released
                elif event.key == K_h:
                    if audio_manager is not None:
                        audio_manager.stop_horn(fadeout_ms=120)

                if isinstance(self._control, carla.VehicleControl):
                    if event.key == K_f:
                        # Toggle ackermann controller
                        self._ackermann_enabled = not self._ackermann_enabled
                        world.hud.show_ackermann_info(self._ackermann_enabled)
                        world.hud.notification("Ackermann Controller %s" %
                                               ("Enabled" if self._ackermann_enabled else "Disabled"))
                    if event.key == K_q:
                        if not self._ackermann_enabled:
                            self._control.gear = 1 if self._control.reverse else -1
                        else:
                            self._ackermann_reverse *= -1
                            # Reset ackermann control
                            self._ackermann_control = carla.VehicleAckermannControl()
                    elif event.key == K_m:
                        self._control.manual_gear_shift = not self._control.manual_gear_shift
                        self._control.gear = world.player.get_control().gear
                        world.hud.notification('%s Transmission' %
                                               ('Manual' if self._control.manual_gear_shift else 'Automatic'))
                    elif self._control.manual_gear_shift and event.key == K_COMMA:
                        self._control.gear = max(-1, self._control.gear - 1)
                    elif self._control.manual_gear_shift and event.key == K_PERIOD:
                        self._control.gear = self._control.gear + 1
                    elif event.key == K_p and not pygame.key.get_mods() & KMOD_CTRL:
                        if not self._autopilot_enabled and not sync_mode:
                            print("WARNING: You are currently in asynchronous mode and could "
                                  "experience some issues with the traffic simulation")
                        self._autopilot_enabled = not self._autopilot_enabled
                        world.player.set_autopilot(self._autopilot_enabled)
                        world.hud.notification(
                            'Autopilot %s' % ('On' if self._autopilot_enabled else 'Off'))
                    elif event.key == K_l and pygame.key.get_mods() & KMOD_CTRL:
                        current_lights ^= carla.VehicleLightState.Special1
                    elif event.key == K_l and pygame.key.get_mods() & KMOD_SHIFT:
                        current_lights ^= carla.VehicleLightState.HighBeam
                    elif event.key == K_l:
                        # Use 'L' key to switch between lights:
                        # closed -> position -> low beam -> fog
                        if not self._lights & carla.VehicleLightState.Position:
                            world.hud.notification("Position lights")
                            current_lights |= carla.VehicleLightState.Position
                        else:
                            world.hud.notification("Low beam lights")
                            current_lights |= carla.VehicleLightState.LowBeam
                        if self._lights & carla.VehicleLightState.LowBeam:
                            world.hud.notification("Fog lights")
                            current_lights |= carla.VehicleLightState.Fog
                        if self._lights & carla.VehicleLightState.Fog:
                            world.hud.notification("Lights off")
                            current_lights ^= carla.VehicleLightState.Position
                            current_lights ^= carla.VehicleLightState.LowBeam
                            current_lights ^= carla.VehicleLightState.Fog
                    elif event.key == K_i:
                        current_lights ^= carla.VehicleLightState.Interior
                    elif event.key == K_z:
                        if self._lights & carla.VehicleLightState.LeftBlinker:
                            current_lights &= ~carla.VehicleLightState.LeftBlinker
                            self._left_blinker_until = 0.0
                        else:
                            current_lights |= carla.VehicleLightState.LeftBlinker
                            self._left_blinker_until = time.time() + self._get_blinker_duration(world)
                            if world.event_sync is not None:
                                world.event_sync.trigger_blinker_left()
                    elif event.key == K_x:
                        if self._lights & carla.VehicleLightState.RightBlinker:
                            current_lights &= ~carla.VehicleLightState.RightBlinker
                            self._right_blinker_until = 0.0
                        else:
                            current_lights |= carla.VehicleLightState.RightBlinker
                            self._right_blinker_until = time.time() + self._get_blinker_duration(world)
                            if world.event_sync is not None:
                                world.event_sync.trigger_blinker_right()

        # Auto-stop blinkers
        if isinstance(self._control, carla.VehicleControl):
            now = time.time()
            if self._left_blinker_until > 0.0 and now >= self._left_blinker_until:
                current_lights &= ~carla.VehicleLightState.LeftBlinker
                self._left_blinker_until = 0.0
            if self._right_blinker_until > 0.0 and now >= self._right_blinker_until:
                current_lights &= ~carla.VehicleLightState.RightBlinker
                self._right_blinker_until = 0.0

        if not self._autopilot_enabled:
            if isinstance(self._control, carla.VehicleControl):
                self._parse_vehicle_keys(pygame.key.get_pressed(), clock.get_time(), world)
                self._control.reverse = self._control.gear < 0
                # Set automatic control-related vehicle lights
                if self._control.brake:
                    current_lights |= carla.VehicleLightState.Brake
                else: # Remove the Brake flag
                    current_lights &= ~carla.VehicleLightState.Brake
                if self._control.reverse:
                    current_lights |= carla.VehicleLightState.Reverse
                else: # Remove the Reverse flag
                    current_lights &= ~carla.VehicleLightState.Reverse
                if current_lights != self._lights: # Change the light state only if necessary
                    self._lights = current_lights
                    world.player.set_light_state(carla.VehicleLightState(self._lights))
                # Apply control
                if not self._ackermann_enabled:
                    world.player.apply_control(self._control)
                else:
                    world.player.apply_ackermann_control(self._ackermann_control)
                    # Update control to the last one applied by the ackermann controller.
                    self._control = world.player.get_control()
                    # Update hud with the newest ackermann control
                    world.hud.update_ackermann_control(self._ackermann_control)
                
                # --- ENGINE AUDIO (KEYBOARD) ---
                try:
                    if audio_manager is not None and audio_manager.engine_audio is not None:
                        audio_manager.update_engine(self._control.throttle)
                except:
                    pass

            elif isinstance(self._control, carla.WalkerControl):
                self._parse_walker_keys(pygame.key.get_pressed(), clock.get_time(), world)
                world.player.apply_control(self._control)

    def _parse_vehicle_keys(self, keys, milliseconds, world):
        if keys[K_UP] or keys[K_w]:
            if not self._ackermann_enabled:
                self._control.throttle = min(self._control.throttle + 0.1, 1.00)
            else:
                self._ackermann_control.speed += round(milliseconds * 0.005, 2) * self._ackermann_reverse
        else:
            if not self._ackermann_enabled:
                self._control.throttle = 0.0

        speed_kmh = 0.0
        try:
            if world is not None and isinstance(world.player, carla.Vehicle):
                v = world.player.get_velocity()
                speed_kmh = 3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)
        except Exception:
            speed_kmh = 0.0

        if keys[K_DOWN] or keys[K_s]:
            if not self._ackermann_enabled:
                # Brake audio - play once on press (0 -> 1 transition)
                next_brake = min(self._control.brake + 0.2, 1)
                current_braking = next_brake > 0.1
                if audio_manager is not None and not self._prev_brake and current_braking:
                    audio_manager.play_brake(brake_strength=next_brake, speed_kmh=speed_kmh)
                self._prev_brake = current_braking
                
                self._control.brake = next_brake
            else:
                self._ackermann_control.speed -= min(abs(self._ackermann_control.speed), round(milliseconds * 0.005, 2)) * self._ackermann_reverse
                self._ackermann_control.speed = max(0, abs(self._ackermann_control.speed)) * self._ackermann_reverse
        else:
            if not self._ackermann_enabled:
                self._prev_brake = False
                self._control.brake = 0

        steer_increment = 5e-4 * milliseconds
        if keys[K_LEFT] or keys[K_a]:
            if self._steer_cache > 0:
                self._steer_cache = 0
            else:
                self._steer_cache -= steer_increment
        elif keys[K_RIGHT] or keys[K_d]:
            if self._steer_cache < 0:
                self._steer_cache = 0
            else:
                self._steer_cache += steer_increment
        else:
            self._steer_cache = 0.0
        self._steer_cache = min(0.7, max(-0.7, self._steer_cache))
        if not self._ackermann_enabled:
            self._control.steer = round(self._steer_cache, 1)
            self._control.hand_brake = keys[K_SPACE]
        else:
            self._ackermann_control.steer = round(self._steer_cache, 1)

    def _parse_walker_keys(self, keys, milliseconds, world):
        self._control.speed = 0.0
        if keys[K_DOWN] or keys[K_s]:
            self._control.speed = 0.0
        if keys[K_LEFT] or keys[K_a]:
            self._control.speed = .01
            self._rotation.yaw -= 0.08 * milliseconds
        if keys[K_RIGHT] or keys[K_d]:
            self._control.speed = .01
            self._rotation.yaw += 0.08 * milliseconds
        if keys[K_UP] or keys[K_w]:
            self._control.speed = world.player_max_speed_fast if pygame.key.get_mods() & KMOD_SHIFT else world.player_max_speed
        self._control.jump = keys[K_SPACE]
        self._rotation.yaw = round(self._rotation.yaw, 1)
        self._control.direction = self._rotation.get_forward_vector()

    @staticmethod
    def _is_quit_shortcut(key):
        return (key == K_ESCAPE) or (key == K_q and pygame.key.get_mods() & KMOD_CTRL)


# ==============================================================================
# -- Gamepad controller (DualShock/PS4) ----------------------------------------
# ==============================================================================

class GamepadControl(object):
    """
    Control a vehicle using a game controller via pygame.joystick.
    - Left stick    :   steer
    - R2            :   throttle
    - L2            :   brake
    - Cross (X)     :   hand-brake
    - Circle (O)    :   toggle reverse
    - Square ([])   :   honk while held down
    - Triangle (/\) :   export performance data
    - L1            :   blinker left
    - R1            :   blinker right
    - Option        :   quit

    """

    def __init__(self, world, start_in_autopilot, deadzone=0.08, steer_sensitivity=1.0):
        import pygame

        joystick_id = 0
        self._autopilot_enabled = start_in_autopilot
        self._control = carla.VehicleControl()
        self._reverse_toggle_state = False
        self._deadzone = deadzone
        self._steer_gain = steer_sensitivity
        self._prev_brake = False

        pygame.joystick.init()
        count = pygame.joystick.get_count()
        if count == 0:
            raise RuntimeError("No game controller detected. Plug in a controller or use --input keyboard.")
        if joystick_id < 0 or joystick_id >= count:
            raise RuntimeError(f"Requested joystick_id={joystick_id}, but only {count} controller(s) available.")

        self.joy = pygame.joystick.Joystick(joystick_id)
        self.joy.init()

        world.player.set_autopilot(self._autopilot_enabled)
        world.hud.notification(f"Gamepad control on joystick #{joystick_id} active.")

    def _apply_deadzone(self, v):
        return 0.0 if abs(v) < self._deadzone else v

    def parse_events(self, client, world, clock, sync_mode):
        import pygame

        # pump events to update joystick state (also if window not focused)
        pygame.event.pump()

        for event in pygame.event.get(pygame.QUIT):
            if event.type == pygame.QUIT:
                return True
        
        if self.joy.get_button(6):  # close window with "options" button 
            return True
        
        # only polling, no pygame.event.get()
        steer_axis = self._apply_deadzone(self.joy.get_axis(0))
        l2 = self.joy.get_axis(4)
        r2 = self.joy.get_axis(5)

        brake    = max(0.0, (l2 + 1.0) / 2.0)
        throttle = max(0.0, (r2 + 1.0) / 2.0)       # => convert from [-1, 1] to [0, 1]

        speed_kmh = 0.0
        try:
            v = world.player.get_velocity()
            speed_kmh = 3.6 * math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)
        except Exception:
            speed_kmh = 0.0

        # Brake audio - play once on L2 press (0 => 1 transition)
        current_braking = brake > 0.1
        if audio_manager is not None and not self._prev_brake and current_braking:
            audio_manager.play_brake(brake_strength=brake, speed_kmh=speed_kmh)
        self._prev_brake = current_braking

        self._control.steer    = float(max(-1.0, min(1.0, steer_axis * self._steer_gain)))
        self._control.throttle = float(max(0.0, min(1.0, throttle)))
        self._control.brake    = float(max(0.0, min(1.0, brake)))

        btn_cross  = self.joy.get_button(0)     # X
        btn_circle = self.joy.get_button(1)     # O
        btn_square = self.joy.get_button(2)     # []
        btn_triangle = self.joy.get_button(3)   # /\
        btn_L1 = self.joy.get_button(9)         # L1
        btn_R1 = self.joy.get_button(10)        # R1
        btn_L3 = self.joy.get_button(7)         # L3
        # 7+8 => Left/Right stick (L3/R3)
        self._control.hand_brake = bool(btn_cross)

        if btn_circle and not getattr(self, "_prev_circle", False):
            self._reverse_toggle_state = not self._reverse_toggle_state
        self._prev_circle = btn_circle
        self._control.reverse = self._reverse_toggle_state

        world.player.apply_control(self._control)

        prev_square = getattr(self, "_prev_square", False)
        if btn_square and not prev_square:
            # Horn: play while held down
            if audio_manager is not None:
                audio_manager.play_horn()
        # Horn control: stop horn when key is released
        elif not btn_square and prev_square:
            if audio_manager is not None:
                audio_manager.stop_horn(fadeout_ms=120)
        self._prev_square = btn_square

        prev_L1 = getattr(self, "_prev_L1", False)
        if btn_L1 and not prev_L1:
            if world.event_sync is not None:
                world.event_sync.trigger_blinker_left()
        self._prev_L1 = btn_L1
        prev_R1 = getattr(self, "_prev_R1", False)
        if btn_R1 and not prev_R1:
            if world.event_sync is not None:
                world.event_sync.trigger_blinker_right()
        self._prev_R1 = btn_R1

        prev_L3 = getattr(self, "_prev_L3", False)
        if btn_L3 and not prev_L3:
            _export_performance_metrics(world)
        self._prev_L3 = btn_L3

        # --- ENGINE AUDIO (GAMEPAD) ---
        try:
            if audio_manager is not None and audio_manager.engine_audio is not None:
                audio_manager.update_engine(self._control.throttle)
        except:
            pass

        return False


# ==============================================================================
# -- HUD -----------------------------------------------------------------------
# ==============================================================================


class HUD(object):
    def __init__(self, width, height):
        self.dim = (width, height)
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        font_name = 'courier' if os.name == 'nt' else 'mono'
        fonts = [x for x in pygame.font.get_fonts() if font_name in x]
        default_font = 'ubuntumono'
        mono = default_font if default_font in fonts else fonts[0]
        mono = pygame.font.match_font(mono)
        self._font_mono = pygame.font.Font(mono, 12 if os.name == 'nt' else 14)
        self._notifications = FadingText(font, (width, 40), (0, height - 40))
        self.help = HelpText(pygame.font.Font(mono, 16), width, height)
        self.server_fps = 0
        self.client_fps = 0                     # new attribute to store client FPS
        self.server_fps_window = deque(maxlen=1800)    # ~30s at ~60 FPS
        self.client_fps_window = deque(maxlen=1800)    # ~30s at ~60 FPS
        self.frame = 0
        self.simulation_time = 0
        self.wall_elapsed = 0.0
        self.real_time_factor = 0.0
        self.server_frame_ms = 0.0
        self.client_frame_ms = 0.0
        self._wall_start = time.perf_counter()
        self._show_info = True
        self._info_text = []
        self._server_clock = pygame.time.Clock()

        self._show_ackermann_info = False
        self._ackermann_control = carla.VehicleAckermannControl()

    def on_world_tick(self, timestamp):
        # self._server_clock.tick()
        # self.server_fps = self._server_clock.get_fps()
        # self.frame = timestamp.frame
        # self.simulation_time = timestamp.elapsed_seconds
        try:
            self.server_fps = 1.0 / timestamp.delta_seconds
        except ZeroDivisionError:
            self.server_fps = 0.0
        self.server_frame_ms = max(0.0, timestamp.delta_seconds * 1000.0)

        self.server_fps_window.append(self.server_fps)

        self.frame = timestamp.frame
        self.simulation_time = timestamp.elapsed_seconds


    def tick(self, world, clock):
        self._notifications.tick(world, clock)
        if not self._show_info:
            return
        t = world.player.get_transform()
        v = world.player.get_velocity()
        c = world.player.get_control()
        compass = world.imu_sensor.compass
        heading = 'N' if compass > 270.5 or compass < 89.5 else ''
        heading += 'S' if 90.5 < compass < 269.5 else ''
        heading += 'E' if 0.5 < compass < 179.5 else ''
        heading += 'W' if 180.5 < compass < 359.5 else ''
        colhist = world.collision_sensor.get_collision_history()
        collision = [colhist[x + self.frame - 200] for x in range(0, 200)]
        max_col = max(1.0, max(collision))
        collision = [x / max_col for x in collision]
        vehicles = world.world.get_actors().filter('vehicle.*')
        current_client_fps = clock.get_fps()
        self.client_fps = current_client_fps
        self.client_fps_window.append(current_client_fps)
        self.client_frame_ms = float(clock.get_time())
        self.wall_elapsed = max(0.0, time.perf_counter() - self._wall_start)
        if self.wall_elapsed > 1e-6:
            self.real_time_factor = self.simulation_time / self.wall_elapsed
        else:
            self.real_time_factor = 0.0

        self._info_text = [
            'Server:  % 16.0f FPS' % self.server_fps,
            #'Client:  % 16.0f FPS' % clock.get_fps(),
            'Client:  % 16.0f FPS' % current_client_fps,
            '',
            'Vehicle: % 20s' % get_actor_display_name(world.player, truncate=20),
            'Map:     % 20s' % world.map.name.split('/')[-1],
            'Simulation time: % 12s' % datetime.timedelta(seconds=int(self.simulation_time)),
            'Runtime: % 16s' % datetime.timedelta(seconds=int(self.wall_elapsed)),
            'RT factor: % 10.2f' % self.real_time_factor,                       # real-time factor
            'Server frame: % 7.1f ms' % self.server_frame_ms,                   # calculate server frame time in ms
            'Client frame: % 7.1f ms' % self.client_frame_ms,
            '',
            'Speed:   % 15.0f km/h' % (3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)),
            u'Compass:% 17.0f\N{DEGREE SIGN} % 2s' % (compass, heading),
            'Accelero: (%5.1f,%5.1f,%5.1f)' % (world.imu_sensor.accelerometer),
            'Gyroscop: (%5.1f,%5.1f,%5.1f)' % (world.imu_sensor.gyroscope),
            'Location:% 20s' % ('(% 5.1f, % 5.1f)' % (t.location.x, t.location.y)),
            'GNSS:% 24s' % ('(% 2.6f, % 3.6f)' % (world.gnss_sensor.lat, world.gnss_sensor.lon)),
            'Height:  % 18.0f m' % t.location.z,
            '']
        # FPS statistics over ~30s for server and client separately
        if len(self.server_fps_window) > 0:
            avg_fps, std_fps, fps_1pct_low = self._compute_fps_stats(self.server_fps_window)
            self._info_text += [
                'Server avg (30s): %5.1f' % avg_fps,
                'Server std (30s): %5.1f' % std_fps,
                'Server 1%% low:    %5.1f' % fps_1pct_low,
            ]

        if len(self.client_fps_window) > 0:
            avg_fps, std_fps, fps_1pct_low = self._compute_fps_stats(self.client_fps_window)
            self._info_text += [
                'Client avg (30s): %5.1f' % avg_fps,
                'Client std (30s): %5.1f' % std_fps,
                'Client 1%% low:    %5.1f' % fps_1pct_low,
            ]

        if isinstance(c, carla.VehicleControl):
            self._info_text += [
                ('Throttle:', c.throttle, 0.0, 1.0),
                ('Steer:', c.steer, -1.0, 1.0),
                ('Brake:', c.brake, 0.0, 1.0),
                ('Reverse:', c.reverse),
                ('Hand brake:', c.hand_brake),
                ('Manual:', c.manual_gear_shift),
                'Gear:        %s' % {-1: 'R', 0: 'N'}.get(c.gear, c.gear)]
            if self._show_ackermann_info:
                self._info_text += [
                    '',
                    'Ackermann Controller:',
                    '  Target speed: % 8.0f km/h' % (3.6*self._ackermann_control.speed),
                ]
        elif isinstance(c, carla.WalkerControl):
            self._info_text += [
                ('Speed:', c.speed, 0.0, 5.556),
                ('Jump:', c.jump)]
        self._info_text += [
            '',
            'Collision:',
            collision,
            '',
            'Number of vehicles: % 8d' % len(vehicles)]
        if len(vehicles) > 1:
            self._info_text += ['Nearby vehicles:']
            distance = lambda l: math.sqrt((l.x - t.location.x)**2 + (l.y - t.location.y)**2 + (l.z - t.location.z)**2)
            vehicles = [(distance(x.get_location()), x) for x in vehicles if x.id != world.player.id]
            for d, vehicle in sorted(vehicles, key=lambda vehicles: vehicles[0]):
                if d > 200.0:
                    break
                vehicle_type = get_actor_display_name(vehicle, truncate=22)
                self._info_text.append('% 4dm %s' % (d, vehicle_type))

    def show_ackermann_info(self, enabled):
        self._show_ackermann_info = enabled

    @staticmethod
    def _compute_fps_stats(samples):
        avg_fps = sum(samples) / len(samples)
        var = sum((f - avg_fps) ** 2 for f in samples) / len(samples)
        std_fps = var ** 0.5
        sorted_fps = sorted(samples)
        index_1pct = max(0, int(len(sorted_fps) * 0.01) - 1)
        fps_1pct_low = sorted_fps[index_1pct]
        return avg_fps, std_fps, fps_1pct_low



    def update_ackermann_control(self, ackermann_control):
        self._ackermann_control = ackermann_control

    def toggle_info(self):
        self._show_info = not self._show_info

    def notification(self, text, seconds=2.0):
        self._notifications.set_text(text, seconds=seconds)

    def error(self, text):
        self._notifications.set_text('Error: %s' % text, (255, 0, 0))

    def render(self, display):
        if self._show_info:
            info_surface = pygame.Surface((220, self.dim[1]))
            info_surface.set_alpha(100)
            display.blit(info_surface, (0, 0))
            v_offset = 4
            bar_h_offset = 100
            bar_width = 106
            for item in self._info_text:
                if v_offset + 18 > self.dim[1]:
                    break
                if isinstance(item, list):
                    if len(item) > 1:
                        points = [(x + 8, v_offset + 8 + (1.0 - y) * 30) for x, y in enumerate(item)]
                        pygame.draw.lines(display, (255, 136, 0), False, points, 2)
                    item = None
                    v_offset += 18
                elif isinstance(item, tuple):
                    if isinstance(item[1], bool):
                        rect = pygame.Rect((bar_h_offset, v_offset + 8), (6, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect, 0 if item[1] else 1)
                    else:
                        rect_border = pygame.Rect((bar_h_offset, v_offset + 8), (bar_width, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect_border, 1)
                        f = (item[1] - item[2]) / (item[3] - item[2])
                        if item[2] < 0.0:
                            rect = pygame.Rect((bar_h_offset + f * (bar_width - 6), v_offset + 8), (6, 6))
                        else:
                            rect = pygame.Rect((bar_h_offset, v_offset + 8), (f * bar_width, 6))
                        pygame.draw.rect(display, (255, 255, 255), rect)
                    item = item[0]
                if item:  # At this point has to be a str.
                    surface = self._font_mono.render(item, True, (255, 255, 255))
                    display.blit(surface, (8, v_offset))
                v_offset += 18
        self._notifications.render(display)
        self.help.render(display)


# ==============================================================================
# -- FadingText ----------------------------------------------------------------
# ==============================================================================


class FadingText(object):
    def __init__(self, font, dim, pos):
        self.font = font
        self.dim = dim
        self.pos = pos
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)

    def set_text(self, text, color=(255, 255, 255), seconds=2.0):
        text_texture = self.font.render(text, True, color)
        self.surface = pygame.Surface(self.dim)
        self.seconds_left = seconds
        self.surface.fill((0, 0, 0, 0))
        self.surface.blit(text_texture, (10, 11))

    def tick(self, _, clock):
        delta_seconds = 1e-3 * clock.get_time()
        self.seconds_left = max(0.0, self.seconds_left - delta_seconds)
        self.surface.set_alpha(500.0 * self.seconds_left)

    def render(self, display):
        display.blit(self.surface, self.pos)


# ==============================================================================
# -- HelpText ------------------------------------------------------------------
# ==============================================================================


class HelpText(object):
    """Helper class to handle text output using pygame"""
    def __init__(self, font, width, height):
        lines = __doc__.split('\n')
        self.font = font
        self.line_space = 18
        self.dim = (780, len(lines) * self.line_space + 12)
        self.pos = (0.5 * width - 0.5 * self.dim[0], 0.5 * height - 0.5 * self.dim[1])
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)
        self.surface.fill((0, 0, 0, 0))
        for n, line in enumerate(lines):
            text_texture = self.font.render(line, True, (255, 255, 255))
            self.surface.blit(text_texture, (22, n * self.line_space))
            self._render = False
        self.surface.set_alpha(220)

    def toggle(self):
        self._render = not self._render

    def render(self, display):
        if self._render:
            display.blit(self.surface, self.pos)


# ==============================================================================
# -- CollisionSensor -----------------------------------------------------------
# ==============================================================================


class CollisionSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self.history = []
        self._parent = parent_actor
        self.hud = hud
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.collision')
        self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: CollisionSensor._on_collision(weak_self, event))

    def get_collision_history(self):
        history = collections.defaultdict(int)
        for frame, intensity in self.history:
            history[frame] += intensity
        return history

    @staticmethod
    def _on_collision(weak_self, event):
        self = weak_self()
        if not self:
            return
        actor_type = get_actor_display_name(event.other_actor)
        self.hud.notification('Collision with %r' % actor_type)
        impulse = event.normal_impulse
        intensity = math.sqrt(impulse.x**2 + impulse.y**2 + impulse.z**2)
        self.history.append((event.frame, intensity))
        if len(self.history) > 4000:
            self.history.pop(0)


# ==============================================================================
# -- LaneInvasionSensor --------------------------------------------------------
# ==============================================================================


class LaneInvasionSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None

        # If the spawn object is not a vehicle, we cannot use the Lane Invasion Sensor
        if parent_actor.type_id.startswith("vehicle."):
            self._parent = parent_actor
            self.hud = hud
            world = self._parent.get_world()
            bp = world.get_blueprint_library().find('sensor.other.lane_invasion')
            self.sensor = world.spawn_actor(bp, carla.Transform(), attach_to=self._parent)
            # We need to pass the lambda a weak reference to self to avoid circular
            # reference.
            weak_self = weakref.ref(self)
            self.sensor.listen(lambda event: LaneInvasionSensor._on_invasion(weak_self, event))

    @staticmethod
    def _on_invasion(weak_self, event):
        self = weak_self()
        if not self:
            return
        lane_types = set(x.type for x in event.crossed_lane_markings)
        text = ['%r' % str(x).split()[-1] for x in lane_types]
        self.hud.notification('Crossed line %s' % ' and '.join(text))


# ==============================================================================
# -- ObstacleDetectionSensor ---------------------------------------------------
# ==============================================================================


class ObstacleDetectionSensor(object):
    """Detects obstacles in front and behind the vehicle for proximity alerts."""
    
    def __init__(self, parent_actor):
        self.sensor_front = None
        self.sensor_rear = None
        self._parent = parent_actor
        
        # Distance state tracking
        self.front_distance = float('inf')
        self.rear_distance = float('inf')
        self.front_last_seen = 0.0
        self.rear_last_seen = 0.0
        self.stale_timeout = 1.0
        self.last_update_time = 0.0
        self.update_interval = 0.5  # Update every 0.5 seconds for efficiency
        
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.obstacle')
        
        # Configure sensor parameters (reduced max distance)
        bp.set_attribute('distance', '1.5')  # Max detection range in meters
        bp.set_attribute('hit_radius', '0.3')
        bp.set_attribute('only_dynamics', 'false')  # Detect static and dynamic objects
        
        # Get vehicle bounds for sensor placement
        bound_x = 0.5 + self._parent.bounding_box.extent.x
        bound_z = 0.5 + self._parent.bounding_box.extent.z
        
        # Position sensors INSIDE the bounding box to compensate for visual model being smaller
        # Bounding box is typically 0.2-0.4m larger than the visible car mesh
        sensor_offset = 0.3  # Move sensor 0.3m inward from bounding box edge
        
        # Front sensor - positioned INSIDE the front edge
        front_transform = carla.Transform(
            carla.Location(x=bound_x - sensor_offset, z=bound_z * 0.5),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0)
        )
        self.sensor_front = world.spawn_actor(bp, front_transform, attach_to=self._parent)
        
        # Rear sensor - positioned INSIDE the rear edge
        rear_transform = carla.Transform(
            carla.Location(x=-bound_x + sensor_offset, z=bound_z * 0.5),
            carla.Rotation(pitch=0.0, yaw=180.0, roll=0.0)
        )
        self.sensor_rear = world.spawn_actor(bp, rear_transform, attach_to=self._parent)
        
        # Set up callbacks
        weak_self = weakref.ref(self)
        self.sensor_front.listen(lambda event: ObstacleDetectionSensor._on_obstacle_front(weak_self, event))
        self.sensor_rear.listen(lambda event: ObstacleDetectionSensor._on_obstacle_rear(weak_self, event))
        
        print("[ObstacleDetectionSensor] Front and rear sensors initialized")
    
    @staticmethod
    def _on_obstacle_front(weak_self, event):
        """Callback for front obstacle detection."""
        self = weak_self()
        if not self:
            return
        import time
        self.front_distance = event.distance
        self.front_last_seen = time.time()
        #print(f"[Front] Distance: {event.distance:.10f}m")
    
    @staticmethod
    def _on_obstacle_rear(weak_self, event):
        """Callback for rear obstacle detection."""
        self = weak_self()
        if not self:
            return
        import time
        self.rear_distance = event.distance
        self.rear_last_seen = time.time()
        #print(f"[Rear] Distance: {event.distance:.10f}m")
    
    def get_distance_group(self):
        """
        Get the current distance group for audio alerts.
        
        Returns:
            str: One of "safe", "medium", "close", "critical"
        """
        # Take the minimum distance (closest obstacle from front or rear)
        import time
        now = time.time()
        if (now - self.front_last_seen) > self.stale_timeout:
            self.front_distance = float('inf')
        if (now - self.rear_last_seen) > self.stale_timeout:
            self.rear_distance = float('inf')
        min_distance = min(self.front_distance, self.rear_distance)
        
        # Map distance to groups - adjusted for actual collision point
        # Sensor is now 0.3m inside bounding box to match visual model
        if min_distance > 0.5:
            return "safe"           # >0.5m: safe, no beeping
        elif min_distance > 0.25:
            return "medium"         # 0.25-0.5m: medium beep (1.0s interval)
        elif min_distance > 0.05:
            return "close"          # 0.05-0.25m: fast beep (0.5s interval)
        else:
            return "critical"       # <0.05m: continuous (actual contact!)
    
    def should_update_audio(self):
        """
        Check if enough time has passed to update audio (throttling).
        
        Returns:
            bool: True if audio should be updated
        """
        import time
        now = time.time()
        if (now - self.last_update_time) >= self.update_interval:
            self.last_update_time = now
            return True
        return False


# ==============================================================================
# -- GnssSensor ----------------------------------------------------------------
# ==============================================================================


class GnssSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        self.lat = 0.0
        self.lon = 0.0
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.gnss')
        self.sensor = world.spawn_actor(bp, carla.Transform(carla.Location(x=1.0, z=2.8)), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(lambda event: GnssSensor._on_gnss_event(weak_self, event))

    @staticmethod
    def _on_gnss_event(weak_self, event):
        self = weak_self()
        if not self:
            return
        self.lat = event.latitude
        self.lon = event.longitude


# ==============================================================================
# -- IMUSensor -----------------------------------------------------------------
# ==============================================================================


class IMUSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        self.accelerometer = (0.0, 0.0, 0.0)
        self.gyroscope = (0.0, 0.0, 0.0)
        self.compass = 0.0
        world = self._parent.get_world()
        bp = world.get_blueprint_library().find('sensor.other.imu')
        self.sensor = world.spawn_actor(
            bp, carla.Transform(), attach_to=self._parent)
        # We need to pass the lambda a weak reference to self to avoid circular
        # reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(
            lambda sensor_data: IMUSensor._IMU_callback(weak_self, sensor_data))

    @staticmethod
    def _IMU_callback(weak_self, sensor_data):
        self = weak_self()
        if not self:
            return
        limits = (-99.9, 99.9)
        self.accelerometer = (
            max(limits[0], min(limits[1], sensor_data.accelerometer.x)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.y)),
            max(limits[0], min(limits[1], sensor_data.accelerometer.z)))
        self.gyroscope = (
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.x))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.y))),
            max(limits[0], min(limits[1], math.degrees(sensor_data.gyroscope.z))))
        self.compass = math.degrees(sensor_data.compass)


# ==============================================================================
# -- RadarSensor ---------------------------------------------------------------
# ==============================================================================


class RadarSensor(object):
    def __init__(self, parent_actor):
        self.sensor = None
        self._parent = parent_actor
        bound_x = 0.5 + self._parent.bounding_box.extent.x
        bound_y = 0.5 + self._parent.bounding_box.extent.y
        bound_z = 0.5 + self._parent.bounding_box.extent.z

        self.velocity_range = 7.5 # m/s
        world = self._parent.get_world()
        self.debug = world.debug
        bp = world.get_blueprint_library().find('sensor.other.radar')
        bp.set_attribute('horizontal_fov', str(35))
        bp.set_attribute('vertical_fov', str(20))
        self.sensor = world.spawn_actor(
            bp,
            carla.Transform(
                carla.Location(x=bound_x + 0.05, z=bound_z+0.05),
                carla.Rotation(pitch=5)),
            attach_to=self._parent)
        # We need a weak reference to self to avoid circular reference.
        weak_self = weakref.ref(self)
        self.sensor.listen(
            lambda radar_data: RadarSensor._Radar_callback(weak_self, radar_data))

    @staticmethod
    def _Radar_callback(weak_self, radar_data):
        self = weak_self()
        if not self:
            return
        # To get a numpy [[vel, altitude, azimuth, depth],...[,,,]]:
        # points = np.frombuffer(radar_data.raw_data, dtype=np.dtype('f4'))
        # points = np.reshape(points, (len(radar_data), 4))

        current_rot = radar_data.transform.rotation
        for detect in radar_data:
            azi = math.degrees(detect.azimuth)
            alt = math.degrees(detect.altitude)
            # The 0.25 adjusts a bit the distance so the dots can
            # be properly seen
            fw_vec = carla.Vector3D(x=detect.depth - 0.25)
            carla.Transform(
                carla.Location(),
                carla.Rotation(
                    pitch=current_rot.pitch + alt,
                    yaw=current_rot.yaw + azi,
                    roll=current_rot.roll)).transform(fw_vec)

            def clamp(min_v, max_v, value):
                return max(min_v, min(value, max_v))

            norm_velocity = detect.velocity / self.velocity_range # range [-1, 1]
            r = int(clamp(0.0, 1.0, 1.0 - norm_velocity) * 255.0)
            g = int(clamp(0.0, 1.0, 1.0 - abs(norm_velocity)) * 255.0)
            b = int(abs(clamp(- 1.0, 0.0, - 1.0 - norm_velocity)) * 255.0)
            self.debug.draw_point(
                radar_data.transform.location + fw_vec,
                size=0.075,
                life_time=0.06,
                persistent_lines=False,
                color=carla.Color(r, g, b))

class RearCamera(object):
    def __init__(self, parent_actor, width=1920, height=1080, fps=10):
        self.sensor = None
        self._parent = parent_actor

        world = parent_actor.get_world()
        bp = world.get_blueprint_library().find('sensor.camera.rgb')

        bp.set_attribute('image_size_x', str(width))
        bp.set_attribute('image_size_y', str(height))
        bp.set_attribute('sensor_tick', str(1.0 / fps))
        bp.set_attribute('gamma', '2.2')

        bound_x = 0.5 + parent_actor.bounding_box.extent.x
        bound_z = 0.5 + parent_actor.bounding_box.extent.z

        transform = carla.Transform(
            carla.Location(x=-1.5 * bound_x, z=1.2 * bound_z),
            carla.Rotation(yaw=180)
        )

        self.sensor = world.spawn_actor(
            bp, transform,
            attach_to=parent_actor,
            attachment_type=carla.AttachmentType.Rigid
        )

        # VERY IMPORTANT:
        # Kamera NICHT starten → rear_view.py übernimmt die Frames!
        self.sensor.stop()

    def destroy(self):
        if self.sensor:
            self.sensor.stop()
            self.sensor.destroy()


# ==============================================================================
# -- CameraManager -------------------------------------------------------------
# ==============================================================================


class CameraManager(object):
    def __init__(self, parent_actor, hud, gamma_correction, screen_percentage=1.0, upscale_filter='fast', use_scene_final=False):
        self.sensor = None
        self.surface = None
        self._scaled_surface = None
        self._parent = parent_actor
        self.hud = hud
        self.recording = False
        self.use_scene_final = use_scene_final
        self.lock_camera = use_scene_final
        self._upscale_filter = upscale_filter
        self._use_smooth_upscale = (upscale_filter == 'smooth')
        self._full_screen_percentage = 1.0
        self._reduced_screen_percentage = max(0.01, min(1.0, float(screen_percentage)))
        self._current_screen_percentage = self._reduced_screen_percentage
        self.sensor_dim = self._compute_sensor_dim(self._current_screen_percentage)
        bound_x = 0.5 + self._parent.bounding_box.extent.x
        bound_y = 0.5 + self._parent.bounding_box.extent.y
        bound_z = 0.5 + self._parent.bounding_box.extent.z
        Attachment = carla.AttachmentType

        if self.use_scene_final:
            self._camera_transforms = [
                (carla.Transform(
                    carla.Location(x=0.80, y=0.0, z=1.40),              # CHANGE camera position in scene final
                    carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0)
                ), Attachment.Rigid)
            ]
        elif not self._parent.type_id.startswith("walker.pedestrian"):
            self._camera_transforms = [
                (carla.Transform(carla.Location(x=-2.0*bound_x, y=+0.0*bound_y, z=2.0*bound_z), carla.Rotation(pitch=8.0)), Attachment.SpringArmGhost),
                (carla.Transform(carla.Location(x=+0.8*bound_x, y=+0.0*bound_y, z=1.3*bound_z)), Attachment.Rigid),
                (carla.Transform(carla.Location(x=+1.9*bound_x, y=+1.0*bound_y, z=1.2*bound_z)), Attachment.SpringArmGhost),
                (carla.Transform(carla.Location(x=-2.8*bound_x, y=+0.0*bound_y, z=4.6*bound_z), carla.Rotation(pitch=6.0)), Attachment.SpringArmGhost),
                (carla.Transform(carla.Location(x=-1.0, y=-1.0*bound_y, z=0.4*bound_z)), Attachment.Rigid)]
        else:
            self._camera_transforms = [
                (carla.Transform(carla.Location(x=-2.5, z=0.0), carla.Rotation(pitch=-8.0)), Attachment.SpringArmGhost),
                (carla.Transform(carla.Location(x=1.6, z=1.7)), Attachment.Rigid),
                (carla.Transform(carla.Location(x=2.5, y=0.5, z=0.0), carla.Rotation(pitch=-8.0)), Attachment.SpringArmGhost),
                (carla.Transform(carla.Location(x=-4.0, z=2.0), carla.Rotation(pitch=6.0)), Attachment.SpringArmGhost),
                (carla.Transform(carla.Location(x=0, y=-2.5, z=-0.0), carla.Rotation(yaw=90.0)), Attachment.Rigid)]

        if self.use_scene_final:
            self.transform_index = 0
            self.sensors = [
                ['sensor.camera.rgb', cc.Raw, 'Camera RGB (SceneFinal)',
                    {'fov': '90.0', 'post_processing': 'SceneFinal'}],
            ]
        else:
            self.transform_index = 1
            self.sensors = [
                ['sensor.camera.rgb', cc.Raw, 'Camera RGB', {}],
                ['sensor.camera.depth', cc.Raw, 'Camera Depth (Raw)', {}],
                ['sensor.camera.depth', cc.Depth, 'Camera Depth (Gray Scale)', {}],
                ['sensor.camera.depth', cc.LogarithmicDepth, 'Camera Depth (Logarithmic Gray Scale)', {}],
                ['sensor.camera.semantic_segmentation', cc.Raw, 'Camera Semantic Segmentation (Raw)', {}],
                ['sensor.camera.semantic_segmentation', cc.CityScapesPalette, 'Camera Semantic Segmentation (CityScapes Palette)', {}],
                ['sensor.camera.instance_segmentation', cc.CityScapesPalette, 'Camera Instance Segmentation (CityScapes Palette)', {}],
                ['sensor.camera.instance_segmentation', cc.Raw, 'Camera Instance Segmentation (Raw)', {}],
                ['sensor.lidar.ray_cast', None, 'Lidar (Ray-Cast)', {'range': '50'}],
                ['sensor.camera.dvs', cc.Raw, 'Dynamic Vision Sensor', {}],
                ['sensor.camera.rgb', cc.Raw, 'Camera RGB Distorted',
                    {'lens_circle_multiplier': '3.0',
                    'lens_circle_falloff': '3.0',
                    'chromatic_aberration_intensity': '0.5',
                    'chromatic_aberration_offset': '0'}],
                ['sensor.camera.optical_flow', cc.Raw, 'Optical Flow', {}],
                ['sensor.camera.normals', cc.Raw, 'Camera Normals', {}],
            ]
        world = self._parent.get_world()
        bp_library = world.get_blueprint_library()
        for item in self.sensors:
            bp = bp_library.find(item[0])
            if item[0].startswith('sensor.camera'):
                bp.set_attribute('image_size_x', str(self.sensor_dim[0]))
                bp.set_attribute('image_size_y', str(self.sensor_dim[1]))
                if bp.has_attribute('gamma'):
                    bp.set_attribute('gamma', str(gamma_correction))
                for attr_name, attr_value in item[3].items():
                    if bp.has_attribute(attr_name):
                        bp.set_attribute(attr_name, attr_value)
            elif item[0].startswith('sensor.lidar'):
                self.lidar_range = 50

                for attr_name, attr_value in item[3].items():
                    bp.set_attribute(attr_name, attr_value)
                    if attr_name == 'range':
                        self.lidar_range = float(attr_value)

            item.append(bp)
        self.index = None

    def _compute_sensor_dim(self, screen_percentage):
        return (
            max(1, int(self.hud.dim[0] * screen_percentage)),
            max(1, int(self.hud.dim[1] * screen_percentage)),
        )

    def _set_camera_blueprint_resolution(self):
        for item in self.sensors:
            if item[0].startswith('sensor.camera'):
                bp = item[-1]
                bp.set_attribute('image_size_x', str(self.sensor_dim[0]))
                bp.set_attribute('image_size_y', str(self.sensor_dim[1]))

    def toggle_screen_percentage(self):
        if abs(self._reduced_screen_percentage - 1.0) < 1e-6:
            self.hud.notification('Render scale fixed at 100% (set --sp < 1.0 to enable toggle)')
            return

        if abs(self._current_screen_percentage - self._full_screen_percentage) < 1e-6:
            self._current_screen_percentage = self._reduced_screen_percentage
        else:
            self._current_screen_percentage = self._full_screen_percentage

        self.sensor_dim = self._compute_sensor_dim(self._current_screen_percentage)
        self._set_camera_blueprint_resolution()

        if self.index is not None and self.sensors[self.index][0].startswith('sensor.camera'):
            self.set_sensor(self.index, notify=False, force_respawn=True)

        self.hud.notification(
            'Render scale: %d%% (%dx%d), upscale=%s' % (
                int(round(self._current_screen_percentage * 100.0)),
                self.sensor_dim[0],
                self.sensor_dim[1],
                self._upscale_filter,
            )
        )

    def toggle_camera(self):
        if self.lock_camera:
            return
        self.transform_index = (self.transform_index + 1) % len(self._camera_transforms)
        self.set_sensor(self.index, notify=False, force_respawn=True)

    def set_sensor(self, index, notify=True, force_respawn=False):
        index = index % len(self.sensors)
        if self.lock_camera and self.index is not None and index != self.index:
            return
        needs_respawn = True if self.index is None else \
            (force_respawn or (self.sensors[index][2] != self.sensors[self.index][2]))
        if needs_respawn:
            if self.sensor is not None:
                self.sensor.destroy()
                self.surface = None
            self.sensor = self._parent.get_world().spawn_actor(
                self.sensors[index][-1],
                self._camera_transforms[self.transform_index][0],
                attach_to=self._parent,
                attachment_type=self._camera_transforms[self.transform_index][1])
            # We need to pass the lambda a weak reference to self to avoid
            # circular reference.
            weak_self = weakref.ref(self)
            self.sensor.listen(lambda image: CameraManager._parse_image(weak_self, image))
        if notify:
            self.hud.notification(self.sensors[index][2])
        self.index = index

    def next_sensor(self):
        if self.lock_camera:
            return
        self.set_sensor(self.index + 1)

    def toggle_recording(self):
        self.recording = not self.recording
        self.hud.notification('Recording %s' % ('On' if self.recording else 'Off'))

    def render(self, display):
        if self.surface is not None:
            if self.surface.get_size() != self.hud.dim:
                if self._scaled_surface is None or self._scaled_surface.get_size() != self.hud.dim:
                    self._scaled_surface = pygame.Surface(self.hud.dim)
                if self._use_smooth_upscale:
                    pygame.transform.smoothscale(self.surface, self.hud.dim, self._scaled_surface)
                else:
                    pygame.transform.scale(self.surface, self.hud.dim, self._scaled_surface)
                display.blit(self._scaled_surface, (0, 0))
            else:
                display.blit(self.surface, (0, 0))

    @staticmethod
    def _parse_image(weak_self, image):
        self = weak_self()
        if not self:
            return
        if self.sensors[self.index][0].startswith('sensor.lidar'):
            print(f"Using Lidar!")
            points = np.frombuffer(image.raw_data, dtype=np.dtype('f4'))
            points = np.reshape(points, (int(points.shape[0] / 4), 4))
            lidar_data = np.array(points[:, :2])
            lidar_data *= min(self.hud.dim) / (2.0 * self.lidar_range)
            lidar_data += (0.5 * self.hud.dim[0], 0.5 * self.hud.dim[1])
            lidar_data = np.fabs(lidar_data)  # pylint: disable=E1111
            lidar_data = lidar_data.astype(np.int32)
            lidar_data = np.reshape(lidar_data, (-1, 2))
            lidar_img_size = (self.hud.dim[0], self.hud.dim[1], 3)
            lidar_img = np.zeros((lidar_img_size), dtype=np.uint8)
            lidar_img[tuple(lidar_data.T)] = (255, 255, 255)
            self.surface = pygame.surfarray.make_surface(lidar_img)
        elif self.sensors[self.index][0].startswith('sensor.camera.dvs'):
            # Example of converting the raw_data from a carla.DVSEventArray
            # sensor into a NumPy array and using it as an image
            dvs_events = np.frombuffer(image.raw_data, dtype=np.dtype([
                ('x', np.uint16), ('y', np.uint16), ('t', np.int64), ('pol', np.bool)]))
            dvs_img = np.zeros((image.height, image.width, 3), dtype=np.uint8)
            # Blue is positive, red is negative
            dvs_img[dvs_events[:]['y'], dvs_events[:]['x'], dvs_events[:]['pol'] * 2] = 255
            self.surface = pygame.surfarray.make_surface(dvs_img.swapaxes(0, 1))
        elif self.sensors[self.index][0].startswith('sensor.camera.optical_flow'):
            image = image.get_color_coded_flow()
            array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]
            array = array[:, :, ::-1]
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        else:
            image.convert(self.sensors[self.index][1])
            array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (image.height, image.width, 4))
            array = array[:, :, :3]
            array = array[:, :, ::-1]
            self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        if self.recording:
            image.save_to_disk('_out/%08d' % image.frame)


# ==============================================================================
# -- game_loop() ---------------------------------------------------------------
# ==============================================================================

def game_loop(args):
    pygame.init()
    pygame.font.init()
    world = None
    original_settings = None
    event_sync = None

    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(2000.0)

        sim_world = client.get_world()
        if args.sync:
            original_settings = sim_world.get_settings()
            settings = sim_world.get_settings()
            if not settings.synchronous_mode:
                settings.synchronous_mode = True
                settings.fixed_delta_seconds = 0.05
            sim_world.apply_settings(settings)

            traffic_manager = client.get_trafficmanager()
            traffic_manager.set_synchronous_mode(True)

        if args.autopilot and not sim_world.get_settings().synchronous_mode:
            print("WARNING: You are currently in asynchronous mode and could "
                  "experience some issues with the traffic simulation")

        pygame.display.set_caption(f"CARLA Manual Control [{args.input}] (joy #0)")
        display = pygame.display.set_mode(
            (args.width, args.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF)
        display.fill((0,0,0))
        pygame.display.flip()

        _audio_init()

        hud = HUD(args.width, args.height)
        world = World(sim_world, hud, args)
        
        # Initialize inside dashboard if enabled
        if ENABLE_INSIDE_DASHBOARD:
            world.dashboard_renderer = DashboardRenderer(args.width, args.height, world)
            print(f"[Dashboard] Inside dashboard enabled ({args.width}x{args.height})")
        else:
            _start_dashboard_process(args.host, args.port, args.dashboard_display)
        event_sync = EventSync(audio_manager=audio_manager, default_blink_duration=4.0)
        world.event_sync = event_sync
        
        if args.input == 'gamepad':
            controller = GamepadControl(world, args.autopilot)
        else:
            controller = KeyboardControl(world, args.autopilot)

        if args.sync:
            sim_world.tick()
        else:
            sim_world.wait_for_tick()

        clock = pygame.time.Clock()
        while True:
            if args.sync:
                sim_world.tick()
            clock.tick_busy_loop(60)
            if controller.parse_events(client, world, clock, args.sync):
                return
            if event_sync is not None:
                event_sync.update()
            world.tick(clock)
            world.render(display)
            
            # Update proximity alert audio (throttled internally to 0.5s)
            if audio_manager is not None and world.obstacle_sensor is not None:
                if world.obstacle_sensor.should_update_audio():
                    distance_group = world.obstacle_sensor.get_distance_group()
                    audio_manager.update_proximity_alert(distance_group)
            
            pygame.display.flip()

    finally:

        if original_settings:
            sim_world.apply_settings(original_settings)

        if (world and world.recording_enabled):
            client.stop_recorder()

        if event_sync is not None:
            event_sync.shutdown()
            event_sync = None

        if world is not None:
            world.event_sync = None

        _stop_dashboard_process()

        if world is not None:
            world.destroy()

        _audio_quit()
        pygame.quit()


# ==============================================================================
# -- main() --------------------------------------------------------------------
# ==============================================================================


def main():
    argparser = argparse.ArgumentParser(
        description='CARLA Manual Control Client')
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-a', '--autopilot',
        action='store_true',
        help='enable autopilot')
    argparser.add_argument(                             # SET RESOLUTION
        '--res',
        metavar='WIDTHxHEIGHT',
        default='1280x720',
        help='window resolution (default: 1280x720)')
    argparser.add_argument(                             # SET screen percentage for internal camera resolution
        '--sp',
        metavar='FLOAT',
        default=1.0,
        type=float,
        help='internal camera screen percentage in (0.0, 1.0], e.g. 0.7 (default: 1.0)')
    argparser.add_argument(                             # SET upscale factor (smooth/fast)
        '--sp-upscale',
        choices=['smooth', 'fast'],
        default='fast',
        help='upscaling filter for low internal camera resolution (default: fast)')
    argparser.add_argument(
        '--filter',
        metavar='PATTERN',
        default='vehicle.*',
        help='actor filter (default: "vehicle.*")')
    argparser.add_argument(
        '--generation',
        metavar='G',
        default='2',
        help='restrict to certain actor generation (values: "1","2","All" - default: "2")')
    argparser.add_argument(
        '--rolename',
        metavar='NAME',
        default='hero',
        help='actor role name (default: "hero")')
    argparser.add_argument(
        '--gamma',
        default=2.2,
        type=float,
        help='Gamma correction of the camera (default: 2.2)')
    argparser.add_argument(
        '--sync',
        action='store_true',
        help='Activate synchronous mode execution')
    argparser.add_argument(                             # keyboard vs. gamepad input
        '--input',
        choices=['keyboard', 'gamepad'],
        default='keyboard',
        help='Select input device for this window (default: keyboard)'
    )
    argparser.add_argument(
        '--dashboard-display',
        metavar='N',
        type=int,
        default=0,                                      # dashbaord display SCREEN
        help='pygame display index for external dashboard (default: 0 for screen 1)'
    )
    args = argparser.parse_args()

    args.width, args.height = [int(x) for x in args.res.split('x')]
    if not (0.0 < args.sp <= 1.0):
        argparser.error('--sp must be > 0.0 and <= 1.0')
    internal_width = max(1, int(args.width * args.sp))
    internal_height = max(1, int(args.height * args.sp))

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('listening to server %s:%s', args.host, args.port)
    logging.info('window=%dx%d internal_camera=%dx%d (sp=%.2f)',
                 args.width, args.height, internal_width, internal_height, args.sp)
    logging.info('upscale_filter=%s', args.sp_upscale)

    print(__doc__)

    try:

        game_loop(args)

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


if __name__ == '__main__':

    main()