"""
Generates a separate dashboard showing information about velocity, rpm (revolutions/minute) and turn signal status. 

"""

import carla
import pygame
import math
import os
import socket
import threading
import sys
import time
import argparse

class CarDashboard(threading.Thread):

    def __init__(self, world, width=960, height=540):
        """Initialize dashboard in separate thread.
        
        Args:
            world: CARLA world object to get hero vehicle from
            width: Dashboard window width (default 960)
            height: Dashboard window height (default 540)
        """
        # use threading to run dashboard in separate thread and avoid blocking main CARLA loop
        threading.Thread.__init__(self)
        self.daemon = True  # daemon thread
        
        self.world = world
        self.width = width
        self.height = height

        # maximum speed the pointer can display (degrees = km/h == 1:1 ratio)
        self._max_speed = 100
        
        # RPM: throttle 0..1 maps to 0..3 + pointer rotates 0...90 degrees
        self._max_rpm_display = 3.0
        self._max_rpm_rotation = 90.0
        self._min_rpm_display = 0.7         # 700 RPM
        self._min_rpm_rotation = 20.0       # degrees for 700 RPM
        self._rpm_decay_down_per_sec = 0.7  # slower decay down (display units/sec)
        self._rpm_decay_up_per_sec = 1.5    # smooth up (display units/sec)
        self._rpm_display_value = 0.0       # persistent pointer state
        self._rpm_first_run = True          # for initial pointer behavior

        # thread control
        self.running = True
        self._display = None
        self._velocity_circle = None
        self._velocity_pointer = None
        self._rpm_circle = None
        self._rpm_pointer = None
        self._center_car_image = None
        self._ts_arrow_right_grey = None
        self._ts_arrow_right_green = None
        self._ts_arrow_left_grey = None
        self._ts_arrow_left_green = None

        self._left_indicator_on = False
        self._right_indicator_on = False
        self._sync_socket = None
        self._blink_interval = 0.3
        self._blink_timer = 0.0
        self._blink_phase_on = True

    # SOCKET: 
    def _init_sync_socket(self):
        """Receive EventSync commands via localhost UDP."""
        try:
            self._sync_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._sync_socket.bind(("127.0.0.1", 39841))
            self._sync_socket.setblocking(False)
        except Exception as e:
            self._sync_socket = None
            print(f"[Dashboard] WARNING: sync socket init failed: {e}")

    def _poll_sync_commands(self):
        if self._sync_socket is None:
            return
        while True:
            try:
                data, _addr = self._sync_socket.recvfrom(128)
            except BlockingIOError:
                break
            except Exception:
                break

            try:
                cmd = data.decode("ascii", errors="ignore").strip().upper()
            except Exception:
                continue

            if cmd == "LEFT_ON":
                self._left_indicator_on = True
                self._blink_timer = 0.0
                self._blink_phase_on = True
            elif cmd == "LEFT_OFF":
                self._left_indicator_on = False
            elif cmd == "RIGHT_ON":
                self._right_indicator_on = True
                self._blink_timer = 0.0
                self._blink_phase_on = True
            elif cmd == "RIGHT_OFF":
                self._right_indicator_on = False

    def run(self):
        """Main dashboard thread loop."""
        try:
            pygame.init()
            self._display = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Car Dashboard")

            # scale speedometer images
            img_dir = os.path.join(os.path.dirname(__file__), 'images')
            panel_size = int(min(self.height, self.width // 2) * 0.82)

            raw_circle = pygame.image.load(
                os.path.join(img_dir, 'dashboard_velocity_circle.png')
            ).convert_alpha()
            raw_pointer = pygame.image.load(
                os.path.join(img_dir, 'dashboard_velocity_pointer.png')
            ).convert_alpha()

            self._velocity_circle = pygame.transform.smoothscale(
                raw_circle, (panel_size, panel_size)
            )
            self._velocity_pointer = pygame.transform.smoothscale(
                raw_pointer, (panel_size, panel_size)
            )

            rpm_circle_path = os.path.join(img_dir, 'dashboard_rpm_circle.png')
            rpm_pointer_path = os.path.join(img_dir, 'dashboard_rpm_pointer.png')
            if os.path.exists(rpm_circle_path) and os.path.exists(rpm_pointer_path):
                raw_rpm_circle = pygame.image.load(rpm_circle_path).convert_alpha()
                raw_rpm_pointer = pygame.image.load(rpm_pointer_path).convert_alpha()
                self._rpm_circle = pygame.transform.smoothscale(
                    raw_rpm_circle, (panel_size, panel_size)
                )
                self._rpm_pointer = pygame.transform.smoothscale(
                    raw_rpm_pointer, (panel_size, panel_size)
                )
            else:
                print("[Dashboard] RPM images not found. Expected dashboard_rpm_circle.png and dashboard_rpm_pointer.png")

            center_car_path = os.path.join(img_dir, 'dashboard_center_car.png')
            if os.path.exists(center_car_path):
                raw_center_car = pygame.image.load(center_car_path).convert_alpha()
                center_car_w = int(panel_size * 0.40)                                   # scale car
                center_car_h = int(center_car_w * raw_center_car.get_height() / raw_center_car.get_width())
                self._center_car_image = pygame.transform.smoothscale(
                    raw_center_car, (center_car_w, center_car_h)
                )
            else:
                print("[Dashboard] Center image not found. Expected dashboard_center_car.png")

            ts_green_path = os.path.join(img_dir, 'dashboard_ts_green.png')
            ts_grey_path = os.path.join(img_dir, 'dashboard_ts_grey.png')
            if os.path.exists(ts_green_path) and os.path.exists(ts_grey_path):
                raw_ts_green = pygame.image.load(ts_green_path).convert_alpha()
                raw_ts_grey = pygame.image.load(ts_grey_path).convert_alpha()
                ts_w = int(panel_size * 0.15)                                               # scale turn signal
                ts_h = int(ts_w * raw_ts_green.get_height() / raw_ts_green.get_width())
                
                self._ts_arrow_left_green = pygame.transform.smoothscale(raw_ts_green, (ts_w, ts_h))
                self._ts_arrow_left_grey = pygame.transform.smoothscale(raw_ts_grey, (ts_w, ts_h))
                self._ts_arrow_right_green = pygame.transform.flip(self._ts_arrow_left_green, True, False)
                self._ts_arrow_right_grey = pygame.transform.flip(self._ts_arrow_left_grey, True, False)
            else:
                print("[Dashboard] Turn signal images not found. Expected dashboard_ts_green.png and dashboard_ts_grey.png")

            self._init_sync_socket()

            clock = pygame.time.Clock()

            # main dashboard loop
            while self.running:
                dt = clock.tick(30) / 1000.0  # limit FPS + frame delta in one call
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                self._poll_sync_commands()

                if self._left_indicator_on or self._right_indicator_on:
                    self._blink_timer += dt
                    while self._blink_timer >= self._blink_interval:
                        self._blink_timer -= self._blink_interval
                        self._blink_phase_on = not self._blink_phase_on
                else:
                    self._blink_timer = 0.0
                    self._blink_phase_on = True

                velocity_kmh = self._get_velocity()
                throttle = self._get_throttle()

                # RPM decay logic
                if self._rpm_first_run:
                    if throttle > 0.01:
                        self._rpm_first_run = False
                    self._rpm_display_value = 0.0
                else:
                    target_rpm = throttle * self._max_rpm_display
                    min_rpm = self._min_rpm_display
                    if target_rpm > self._rpm_display_value:
                        # pointer increase (slow)
                        up = self._rpm_decay_up_per_sec * dt
                        self._rpm_display_value = min(self._rpm_display_value + up, target_rpm)
                    elif target_rpm < self._rpm_display_value:
                        # pointer decrease (slow)
                        down = self._rpm_decay_down_per_sec * dt
                        self._rpm_display_value = max(self._rpm_display_value - down, max(target_rpm, min_rpm))

                self._render(velocity_kmh, self._rpm_display_value)

        except Exception as e:
            print(f"Dashboard error: {e}")
        finally:
            if self._sync_socket is not None:
                try:
                    self._sync_socket.close()
                except Exception:
                    pass
            if self._display is not None:
                pygame.quit()
    
    def _get_velocity(self):
        """ Get velocity in km/h """
        try:
            if self.world and self.world.player:
                v = self.world.player.get_velocity()
                return 3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)
        except:
            pass
        return 0.0

    def _get_throttle(self):
        """ Get throttle in range [0.0, 1.0]."""
        try:
            if self.world and self.world.player:
                control = self.world.player.get_control()
                return min(max(control.throttle, 0.0), 1.0)
        except:
            pass
        return 0.0

    def _render(self, velocity_kmh, rpm_display):
        """ Render dashboard """
        self._display.fill((7, 21, 41))  # background colour # 071529

        center_y = self.height // 2

        # left half: RPM
        left_center_x = self.width // 4
        if self._rpm_circle and self._rpm_pointer:
            rpm_circle_rect = self._rpm_circle.get_rect(center=(left_center_x, center_y))
            self._display.blit(self._rpm_circle, rpm_circle_rect)

            # initial state = 0 degrees => after first activation minimum (RPM 700)
            if self._rpm_first_run and rpm_display <= 0.0:
                rpm_rotation_deg = 0.0
            else:
                rpm_val = min(max(rpm_display, self._min_rpm_display), self._max_rpm_display)
                frac = (rpm_val - self._min_rpm_display) / (self._max_rpm_display - self._min_rpm_display)
                rpm_rotation_deg = -(
                    self._min_rpm_rotation + frac * (self._max_rpm_rotation - self._min_rpm_rotation)
                )
            rotated_rpm_pointer = pygame.transform.rotozoom(self._rpm_pointer, rpm_rotation_deg, 1.0)
            rpm_pointer_rect = rotated_rpm_pointer.get_rect(center=(left_center_x, center_y))
            self._display.blit(rotated_rpm_pointer, rpm_pointer_rect)

        # right half: speedometer centred horizontally and vertically
        center_x = self.width * 3 // 4

        # static velocity circle
        circle_rect = self._velocity_circle.get_rect(center=(center_x, center_y))
        self._display.blit(self._velocity_circle, circle_rect)

        # rotate pointer (1:1 ratio)
        speed_clamped = min(max(velocity_kmh, 0.0), self._max_speed)
        rotation_deg = -(speed_clamped / self._max_speed) * 100.0
        rotated_pointer = pygame.transform.rotozoom(self._velocity_pointer, rotation_deg, 1.0) # rotozoom rotates counter-clockwise => negate
        pointer_rect = rotated_pointer.get_rect(center=(center_x, center_y))
        self._display.blit(rotated_pointer, pointer_rect)

        # center car image:
        if self._center_car_image:
            car_center_x = self.width // 2
            car_center_y = int(self.height * 0.30)      # car position (0.0 = oben, 1.0 = unten)
            car_rect = self._center_car_image.get_rect(center=(car_center_x, car_center_y))
            self._display.blit(self._center_car_image, car_rect)

        # turn signal arrows
        if self._ts_arrow_left_grey and self._velocity_circle:
            gauge_radius = self._velocity_circle.get_height() // 2
            ts_y = center_y - int(gauge_radius * 1.1)               # position above center

            left_x = (self.width // 4 + self.width // 2) // 2
            right_x = (self.width * 3 // 4 + self.width // 2) // 2

            left_active = self._left_indicator_on and self._blink_phase_on
            right_active = self._right_indicator_on and self._blink_phase_on

            left_img = self._ts_arrow_left_green if left_active else self._ts_arrow_left_grey
            right_img = self._ts_arrow_right_green if right_active else self._ts_arrow_right_grey
            self._display.blit(left_img, left_img.get_rect(center=(left_x, ts_y)))
            self._display.blit(right_img, right_img.get_rect(center=(right_x, ts_y)))

        pygame.display.flip()
    
    def close(self):
        """ Close the dashboard window """
        self.running = False
        self.join(timeout=2)


def find_hero_vehicle(world):
    """ Find hero vehicle """
    for actor in world.get_actors():
        if actor.attributes.get('role_name') == 'hero':
            return actor
    return None

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='CARLA Car Dashboard')
    argparser.add_argument(
        '--host', metavar='H', default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port', metavar='P', default=2000, type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '--res', metavar='WIDTHxHEIGHT', default='960x540',
        help='window resolution (default: 960x540)')
    argparser.add_argument(
        '--offline', action='store_true',
        help='start dashboard without CARLA server connection')
    args = argparser.parse_args()
    args.width, args.height = [int(x) for x in args.res.split('x')]
    dashboard = None

    class DummyVelocity:
        def __init__(self):
            self.x = 0.0
            self.y = 0.0
            self.z = 0.0
    class DummyControl:
        def __init__(self):
            self.throttle = 0.0
    class DummyPlayer:
        type_id = 'offline.dummy.player'
        def get_velocity(self):
            return DummyVelocity()
        def get_control(self):
            return DummyControl()

    class WorldWrapper:
        def __init__(self, player):
            self.player = player

    def start_dashboard_with_player(player, mode_label):
        nonlocal_dashboard = CarDashboard(WorldWrapper(player), width=args.width, height=args.height)
        nonlocal_dashboard.start()
        print(f"[Dashboard] Started ({args.res}) in {mode_label} mode. Press Ctrl+C to exit.")
        return nonlocal_dashboard
    
    try:
        if args.offline:
            print("[Dashboard] Offline mode enabled (--offline).")
            dashboard = start_dashboard_with_player(DummyPlayer(), mode_label='offline')
        else:
            try:
                # connect to CARLA
                client = carla.Client(args.host, args.port)
                client.set_timeout(10.0)
                world = client.get_world()
                print(f"[Dashboard] Connected to CARLA at {args.host}:{args.port}")

                # find hero vehicle
                hero = find_hero_vehicle(world)
                if hero is None:
                    print("[Dashboard] Hero vehicle not found. Falling back to offline mode.")
                    dashboard = start_dashboard_with_player(DummyPlayer(), mode_label='offline-fallback')
                else:
                    print(f"[Dashboard] Found hero: {hero.type_id}")
                    dashboard = start_dashboard_with_player(hero, mode_label='online')
            except Exception as connect_error:
                print(f"[Dashboard] Could not connect to CARLA ({connect_error}). Falling back to offline mode.")
                dashboard = start_dashboard_with_player(DummyPlayer(), mode_label='offline-fallback')
        
        while dashboard.running:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n[Dashboard] Shutting down...")
    except Exception as e:
        print(f"[Dashboard] ERROR: {e}")
    finally:
        if dashboard is not None:
            dashboard.close()
        print("[Dashboard] Closed.")

