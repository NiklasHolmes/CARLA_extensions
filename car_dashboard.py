"""
Generates a separate dashboard showing information about velocity, rpm (revolutions/minute) and turn signal status. 

use:
python car_dashboard.py --display-index 0

"""

import carla
import pygame
import math
import os
import socket
import threading
import time
import argparse
import ctypes
from common.window_positioning import (
    get_windows_monitor_rects,
    get_pygame_window_hwnd,
    apply_borderless_style_windows,
    set_window_topmost_windows,
    set_window_noactivate_windows,
    is_window_topmost_windows,
    move_window_to_monitor_windows,
    move_window_overlapping_windows,
)

# Switch window size mode:
# - None => fullscreen on selected monitor
# - (width, height) => fixed dashboard window size
DEFAULT_DASHBOARD_SIZE = (960, 540)              # (960, 540)  (1920, 1080) 
DASHBOARD_DEFAULT_OVERLAP_MARGIN = (16, 16)

DASHBOARD_SUPPORTED_MODES = ('basic', 'second_screen', 'overlapping')
DEFAULT_DASHBOARD_MODE = 'basic'

class CarDashboard(threading.Thread):

    def __init__(
        self,
        world,
        window_size=None,
        display_index=0,
        mode=DEFAULT_DASHBOARD_MODE,
        main_window_title="",
        overlap_margin=DASHBOARD_DEFAULT_OVERLAP_MARGIN,
        always_on_top=False,
        no_focus=False,
    ):
        """Initialize dashboard in separate thread.
        
        Args:
            world: CARLA world object to get hero vehicle from
            window_size: None for fullscreen, or (width, height) for fixed size (ignored for second_screen)
            display_index: pygame display index (0-based)
            mode: either 'basic', 'second_screen', or 'overlapping'
            main_window_title: target window caption for overlapping mode
            overlap_margin: (x, y) margin in pixels for overlapping mode
            always_on_top: keep dashboard window above normal windows (auto in overlapping)
            no_focus: prevent dashboard from taking input focus (auto in overlapping)
        """
        # use threading to run dashboard in separate thread and avoid blocking main CARLA loop
        threading.Thread.__init__(self)
        self.daemon = True  # daemon thread
        
        self.world = world
        # If no size is provided, use fullscreen on the selected monitor.
        self._use_fullscreen = window_size is None
        if self._use_fullscreen:
            self.width = None
            self.height = None
        else:
            self.width = int(window_size[0])
            self.height = int(window_size[1])
        self.display_index = max(0, int(display_index))
        normalized_mode = str(mode).strip().lower()
        if normalized_mode not in DASHBOARD_SUPPORTED_MODES:
            normalized_mode = DEFAULT_DASHBOARD_MODE
        self.mode = normalized_mode
        if self.mode == 'second_screen':
            self._use_fullscreen = True
            self.width = None
            self.height = None
        self.main_window_title = str(main_window_title or "")
        self.overlap_margin_x = max(0, int(overlap_margin[0]))
        self.overlap_margin_y = max(0, int(overlap_margin[1]))
        self.always_on_top = bool(always_on_top) or self.mode == 'overlapping'
        self.no_focus = bool(no_focus) or self.mode == 'overlapping'
        self._last_overlap_target = None
        # Re-assert window policy at low rate to survive focus/z-order changes.
        self._window_policy_refresh_interval_sec = 0.10
        self._window_policy_timer_sec = 0.0

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
        self._rpm_activation_started = False # latch first throttle impulse for smooth start

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

        # Turn signal blinking
        self._left_indicator_on = False
        self._right_indicator_on = False
        self._sync_socket = None
        self._blink_interval = 0.3
        self._blink_timer = 0.0
        self._blink_phase_on = True

    def _resolve_display_index(self, requested_index, num_displays):
        """Resolve requested monitor index with support for 0-based and common 1-based input."""
        if num_displays <= 0:
            return max(0, int(requested_index))

        idx = int(requested_index)
        if 0 <= idx < num_displays:
            return idx

        if 1 <= idx <= num_displays:
            resolved = idx - 1
            print(f"[Dashboard] display index {idx} interpreted as 1-based -> using {resolved}")
            return resolved

        clamped = max(0, min(idx, num_displays - 1))
        print(f"[Dashboard] display index {idx} out of range, clamped to {clamped}")
        return clamped

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

    def _apply_window_policy_windows(self, hwnd, resolved_display_index, log_output=False):
        """Apply placement/topmost policy once; can be called periodically at low rate."""
        if os.name != 'nt' or not hwnd:
            return

        if self.mode == 'second_screen':
            moved = move_window_to_monitor_windows(
                hwnd,
                resolved_display_index,
                resolve_display_index=self._resolve_display_index,
            )
            if moved is None:
                if log_output:
                    print("[Dashboard] WARNING: failed to move window to selected monitor")
            elif log_output:
                monitor_idx, left, top = moved
                print(f"[Dashboard] Window moved to monitor index {monitor_idx} at ({left}, {top})")
        elif self.mode == 'overlapping':
            moved = move_window_overlapping_windows(
                hwnd,
                self.main_window_title,
                (self.width, self.height),
                (self.overlap_margin_x, self.overlap_margin_y),
                previous_target=self._last_overlap_target,
                show_window=log_output,
            )
            if moved is None:
                if log_output:
                    print("[Dashboard] WARNING: failed to place overlapping window")
            elif log_output:
                target_x, target_y = moved
                print(
                    f"[Dashboard] overlapping target=({target_x}, {target_y}), "
                    f"main_window='{self.main_window_title.strip()}'"
                )
            if moved is not None:
                self._last_overlap_target = moved

        if self.always_on_top:
            if not is_window_topmost_windows(hwnd):
                if set_window_topmost_windows(hwnd, enabled=True):
                    if log_output:
                        print("[Dashboard] always_on_top enabled")
                elif log_output:
                    print("[Dashboard] WARNING: failed to enable always_on_top")

    def run(self):
        """Main dashboard thread loop."""
        try:
            if os.name == 'nt':
                try:
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass
            pygame.init()

            try:
                num_displays = pygame.display.get_num_video_displays()
            except Exception:
                num_displays = 0
            resolved_display_index = self._resolve_display_index(self.display_index, num_displays)
            print(
                f"[Dashboard] mode={self.mode}, "
                f"requested_display={self.display_index}, "
                f"resolved_display={resolved_display_index}, "
                f"num_displays={num_displays}"
            )

            # Basic mode stays movable with normal window frame
            borderless = (self.mode in ('second_screen', 'overlapping')) or self._use_fullscreen
            window_flags = pygame.NOFRAME if borderless else 0

            if self._use_fullscreen and os.name == 'nt':
                # Fullscreen mode on Windows: use monitor dimensions and borderless window.
                rects = get_windows_monitor_rects()
                if rects:
                    monitor_idx = self._resolve_display_index(resolved_display_index, len(rects))
                    left, top, right, bottom = rects[monitor_idx]
                    self.width = int(right - left)
                    self.height = int(bottom - top)
                    print(
                        f"[Dashboard] monitor_rect=({left}, {top}, {right}, {bottom}), "
                        f"window_size={self.width}x{self.height}, borderless=True"
                    )

            if self.width is None or self.height is None:
                self.width, self.height = DEFAULT_DASHBOARD_SIZE
                print(f"[Dashboard] Using fallback size: {self.width}x{self.height}")

            use_display_kwarg = (
                self.mode == 'second_screen' and
                num_displays > 0
            )
            try:
                if use_display_kwarg:
                    self._display = pygame.display.set_mode(
                        (self.width, self.height),
                        window_flags,
                        display=resolved_display_index,
                    )
                else:
                    self._display = pygame.display.set_mode((self.width, self.height), window_flags)
            except TypeError:
                # Fallback for older pygame signatures without display keyword
                self._display = pygame.display.set_mode((self.width, self.height), window_flags)
            pygame.display.set_caption("Car Dashboard")
            hwnd = get_pygame_window_hwnd(pygame)
            if borderless and hwnd and not apply_borderless_style_windows(hwnd):
                print("[Dashboard] WARNING: failed to enforce borderless style")
            if self.no_focus:
                if hwnd and set_window_noactivate_windows(hwnd, enabled=True):
                    print("[Dashboard] no_focus enabled")
                else:
                    print("[Dashboard] WARNING: failed to enable no_focus")
            self._apply_window_policy_windows(hwnd, resolved_display_index, log_output=True)

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

                if os.name == 'nt' and self.mode == 'overlapping':
                    self._window_policy_timer_sec += dt
                    if self._window_policy_timer_sec >= self._window_policy_refresh_interval_sec:
                        self._window_policy_timer_sec = 0.0
                        if hwnd is None:
                            hwnd = get_pygame_window_hwnd(pygame)
                        self._apply_window_policy_windows(hwnd, resolved_display_index, log_output=False)

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
                        self._rpm_activation_started = True

                    if self._rpm_activation_started:
                        up = self._rpm_decay_up_per_sec * dt
                        self._rpm_display_value = min(self._rpm_display_value + up, self._min_rpm_display)
                        if self._rpm_display_value >= self._min_rpm_display - 1e-6:
                            self._rpm_first_run = False
                    else:
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

            # Smooth visible transition from 0 RPM to minimum RPM marker.
            if self._rpm_first_run:
                if self._rpm_activation_started and self._min_rpm_display > 1e-6:
                    frac_start = min(max(rpm_display / self._min_rpm_display, 0.0), 1.0)
                    rpm_rotation_deg = -(frac_start * self._min_rpm_rotation)
                else:
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
        '--offline', action='store_true',
        help='start dashboard without CARLA server connection')
    argparser.add_argument(
        '--display-index', metavar='N', default=0, type=int,
        help='pygame display index (0-based, default: 0)')
    argparser.add_argument(
        '--mode',
        choices=list(DASHBOARD_SUPPORTED_MODES),
        default=DEFAULT_DASHBOARD_MODE,
        help='dashboard placement mode (default: basic)')
    argparser.add_argument(
        '--size',
        metavar='WIDTHxHEIGHT',
        default=f'{DEFAULT_DASHBOARD_SIZE[0]}x{DEFAULT_DASHBOARD_SIZE[1]}',
        help='dashboard window size, or fullscreen (ignored for second_screen)')
    argparser.add_argument(
        '--main-window-title',
        default='',
        help='manual_control window title used in overlapping mode')
    argparser.add_argument(
        '--overlap-margin',
        metavar='X,Y',
        default=f'{DASHBOARD_DEFAULT_OVERLAP_MARGIN[0]},{DASHBOARD_DEFAULT_OVERLAP_MARGIN[1]}',
        help='margin from bottom-left corner of main window in overlapping mode (default: 16,16)')
    argparser.add_argument(
        '--always-on-top',
        action='store_true',
        help='keep dashboard window above normal windows')
    argparser.add_argument(
        '--no-focus',
        action='store_true',
        help='prevent dashboard window from taking input focus')
    args = argparser.parse_args()

    if str(args.size).strip().lower() == 'fullscreen':
        dashboard_window_size = None
    else:
        try:
            w_str, h_str = str(args.size).lower().split('x', 1)
            dashboard_window_size = (max(64, int(w_str)), max(64, int(h_str)))
        except Exception:
            dashboard_window_size = DEFAULT_DASHBOARD_SIZE
            print(f"[Dashboard] WARNING: invalid --size '{args.size}', using {dashboard_window_size[0]}x{dashboard_window_size[1]}")

    try:
        margin_x_str, margin_y_str = str(args.overlap_margin).split(',', 1)
        overlap_margin = (max(0, int(margin_x_str)), max(0, int(margin_y_str)))
    except Exception:
        overlap_margin = (16, 16)
        print(f"[Dashboard] WARNING: invalid --overlap-margin '{args.overlap_margin}', using 16,16")

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
        nonlocal_dashboard = CarDashboard(
            WorldWrapper(player),
            window_size=dashboard_window_size,
            display_index=args.display_index,
            mode=args.mode,
            main_window_title=args.main_window_title,
            overlap_margin=overlap_margin,
            always_on_top=args.always_on_top,
            no_focus=args.no_focus,
        )
        nonlocal_dashboard.start()
        if args.mode == 'second_screen':
            size_label = "fullscreen"
        else:
            size_label = "fullscreen" if dashboard_window_size is None else f"{dashboard_window_size[0]}x{dashboard_window_size[1]}"
        print(
            f"[Dashboard] Started ({size_label}, mode={args.mode}, display={args.display_index}, "
            f"always_on_top={nonlocal_dashboard.always_on_top}, "
            f"no_focus={nonlocal_dashboard.no_focus}) "
            f"in {mode_label} mode. Press Ctrl+C to exit."
        )
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

