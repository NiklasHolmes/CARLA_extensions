"""
Generates a dashboard inside main window, showing information about velocity, rpm (revolutions/minute) and turn signal status. 

"""

import os
import math
import pygame
import carla


class DashboardRenderer:
    def __init__(self, display_width, display_height, world=None):
        """Initialize dashboard renderer.
        
        Args:
            display_width: Main display width
            display_height: Main display height
            world: CARLA world object to get hero vehicle from (optional)
        """
        self.display_width = display_width
        self.display_height = display_height
        self.world = world
        
        # Dashboard layout/performance test settings.
        self._dashboard_scale = 0.85  # < 1.0 renders a smaller dashboard
        self._opaque_mode = False      # True: draw as opaque rectangle for cheaper blending
        self._opaque_fill_color = (10, 20, 34)
        self._render_pointers = True  # test mode: disable RPM/speed pointers
 
        # Dashboard dimensions: scaled variant of previous 1/3 x 1/2 layout, bottom-left.
        self.dashboard_width = max(320, int((display_width // 3) * self._dashboard_scale))
        self.dashboard_height = max(220, int((display_height // 2) * self._dashboard_scale))
        self.dashboard_x = 0
        self.dashboard_y = display_height - self.dashboard_height + 100

        # Precompute shared layout positions once.
        self._center_y = self.dashboard_height // 2
        self._inward_shift = int(self.dashboard_width * 0.03)
        self._left_center_x = self.dashboard_width // 4 + self._inward_shift
        self._right_center_x = self.dashboard_width * 3 // 4 - self._inward_shift
        
        # Speed display settings
        self._max_speed = 100  # km/h
        
        # RPM display settings (throttle 0..1 maps to 0..3 + pointer rotates 0...90 degrees)
        self._max_rpm_display = 3.0
        self._max_rpm_rotation = 90.0
        self._min_rpm_display = 0.7          # 700 RPM
        self._min_rpm_rotation = 20.0        # degrees for 700 RPM
        self._rpm_decay_down_per_sec = 0.7   # slower decay down (display units/sec)
        self._rpm_decay_up_per_sec = 1.5     # smooth up (display units/sec)
        self._rpm_display_value = 0.0        # persistent pointer state
        self._rpm_first_run = True           # for initial pointer behavior
        self._rpm_activation_started = False # latch first throttle impulse for smooth start
        
        # Turn signal blinking
        self._left_indicator_on = False
        self._right_indicator_on = False
        self._blink_interval = 0.3
        self._blink_timer = 0.0
        self._blink_phase_on = True
        
        # Load images
        self._background = None
        self._velocity_circle = None
        self._velocity_pointer = None
        self._rpm_circle = None
        self._rpm_pointer = None
        self._ts_arrow_left_grey = None
        self._ts_arrow_left_green = None
        self._ts_arrow_right_grey = None
        self._ts_arrow_right_green = None
        self._center_car_image = None
        
        self._load_images()
        
        # Performance optimization: Caching and offscreen rendering
        self._rpm_pointer_cache = {}      # Cache for rotated RPM pointer: angle_key -> surface
        self._velocity_pointer_cache = {} # Cache for rotated velocity pointer: angle_key -> surface
        self._rpm_angle_tolerance = 0.5
        self._velocity_angle_tolerance = 0.25
        self._offscreen_layer = None      # Cached offscreen surface for static elements
        self._dashboard_frame = None      # Cached composited frame blitted each client frame
        self._ts_left_center = (0, 0)
        self._ts_right_center = (0, 0)
        self._create_offscreen_layer()    # Create the initial offscreen layer
        self._compose_dashboard_frame()
    
    def _load_images(self):
        """Load dashboard images."""
        img_dir = os.path.join(os.path.dirname(__file__), 'images')
        
        # Background image
        bg_path = os.path.join(img_dir, 'dashboard_background.png')
        if os.path.exists(bg_path):
            raw_bg = pygame.image.load(bg_path).convert_alpha()
            self._background = pygame.transform.smoothscale(
                raw_bg, (self.dashboard_width, self.dashboard_height)
            )
        else:
            print("[DashboardRenderer] WARNING: dashboard_background.png not found")
        
        # Base size for dashboard assets
        base_size = int(min(self.dashboard_height, self.dashboard_width) * 0.7)
        # Circle size
        circle_size = int(base_size * 0.85)
        
        # Velocity circle and pointer
        velocity_circle_path = os.path.join(img_dir, 'dashboard_velocity_circle.png')
        velocity_pointer_path = os.path.join(img_dir, 'dashboard_velocity_pointer.png')
        if os.path.exists(velocity_circle_path) and os.path.exists(velocity_pointer_path):
            raw_circle = pygame.image.load(velocity_circle_path).convert_alpha()
            raw_pointer = pygame.image.load(velocity_pointer_path).convert_alpha()
            self._velocity_circle = pygame.transform.smoothscale(raw_circle, (circle_size, circle_size))
            self._velocity_pointer = pygame.transform.smoothscale(raw_pointer, (circle_size, circle_size))
        else:
            print("[DashboardRenderer] WARNING: velocity gauge images not found")
        
        # RPM circle and pointer
        rpm_circle_path = os.path.join(img_dir, 'dashboard_rpm_circle.png')
        rpm_pointer_path = os.path.join(img_dir, 'dashboard_rpm_pointer.png')
        if os.path.exists(rpm_circle_path) and os.path.exists(rpm_pointer_path):
            raw_rpm_circle = pygame.image.load(rpm_circle_path).convert_alpha()
            raw_rpm_pointer = pygame.image.load(rpm_pointer_path).convert_alpha()
            self._rpm_circle = pygame.transform.smoothscale(raw_rpm_circle, (circle_size, circle_size))
            self._rpm_pointer = pygame.transform.smoothscale(raw_rpm_pointer, (circle_size, circle_size))
        else:
            print("[DashboardRenderer] WARNING: RPM gauge images not found")
        
        # Turn signal arrows
        ts_green_path = os.path.join(img_dir, 'dashboard_ts_green.png')
        ts_grey_path = os.path.join(img_dir, 'dashboard_ts_grey.png')
        if os.path.exists(ts_green_path) and os.path.exists(ts_grey_path):
            raw_ts_green = pygame.image.load(ts_green_path).convert_alpha()
            raw_ts_grey = pygame.image.load(ts_grey_path).convert_alpha()
            ts_w = int(base_size * 0.15)
            ts_h = int(ts_w * raw_ts_green.get_height() / raw_ts_green.get_width())
            
            self._ts_arrow_left_green = pygame.transform.smoothscale(raw_ts_green, (ts_w, ts_h))
            self._ts_arrow_left_grey = pygame.transform.smoothscale(raw_ts_grey, (ts_w, ts_h))
            self._ts_arrow_right_green = pygame.transform.flip(self._ts_arrow_left_green, True, False)
            self._ts_arrow_right_grey = pygame.transform.flip(self._ts_arrow_left_grey, True, False)
        else:
            print("[DashboardRenderer] WARNING: turn signal images not found")

        # Center car image
        center_car_path = os.path.join(img_dir, 'dashboard_center_car.png')
        if os.path.exists(center_car_path):
            raw_center_car = pygame.image.load(center_car_path).convert_alpha()
            car_w = int(base_size * 0.42)
            car_h = int(car_w * raw_center_car.get_height() / raw_center_car.get_width())
            self._center_car_image = pygame.transform.smoothscale(raw_center_car, (car_w, car_h))
        else:
            print("[DashboardRenderer] WARNING: center car image not found")
    
    def _create_offscreen_layer(self):
        """ Create cached offscreen layer with all static elements.
        """
        # Create static layer (opaque mode avoids per-pixel alpha blending cost).
        layer_flags = 0 if self._opaque_mode else pygame.SRCALPHA
        self._offscreen_layer = pygame.Surface((self.dashboard_width, self.dashboard_height), layer_flags)
        if self._opaque_mode:
            self._offscreen_layer.fill(self._opaque_fill_color)
        
        # Blit background image if available
        if self._background:
            self._offscreen_layer.blit(self._background, (0, 0))
        
        # Render static gauge circles
        if self._rpm_circle:
            rpm_circle_rect = self._rpm_circle.get_rect(center=(self._left_center_x, self._center_y))
            self._offscreen_layer.blit(self._rpm_circle, rpm_circle_rect)
        
        if self._velocity_circle:
            circle_rect = self._velocity_circle.get_rect(center=(self._right_center_x, self._center_y))
            self._offscreen_layer.blit(self._velocity_circle, circle_rect)
        
        # Render center car image
        if self._center_car_image:
            car_center_x = self.dashboard_width // 2
            car_center_y = int(self.dashboard_height * 0.30)
            car_rect = self._center_car_image.get_rect(center=(car_center_x, car_center_y))
            self._offscreen_layer.blit(self._center_car_image, car_rect)

        # Render grey turn signal arrows as static baseline.
        if self._ts_arrow_left_grey and self._velocity_circle:
            gauge_radius = self._velocity_circle.get_height() // 2
            ts_y = self._center_y - int(gauge_radius * 1.1)
            left_x = (self.dashboard_width // 4 + self.dashboard_width // 2) // 2
            right_x = (self.dashboard_width * 3 // 4 + self.dashboard_width // 2) // 2
            self._ts_left_center = (left_x, ts_y)
            self._ts_right_center = (right_x, ts_y)

            self._offscreen_layer.blit(
                self._ts_arrow_left_grey,
                self._ts_arrow_left_grey.get_rect(center=self._ts_left_center)
            )
            self._offscreen_layer.blit(
                self._ts_arrow_right_grey,
                self._ts_arrow_right_grey.get_rect(center=self._ts_right_center)
            )

        # Allocate frame surface with same pixel mode as static layer.
        frame_flags = 0 if self._opaque_mode else pygame.SRCALPHA
        self._dashboard_frame = pygame.Surface((self.dashboard_width, self.dashboard_height), frame_flags)
        if self._opaque_mode:
            self._dashboard_frame.fill(self._opaque_fill_color)
    
    def _get_cached_rotated_pointer(self, pointer_image, rotation_deg, cache_dict, angle_tolerance):
        """Get a rotated pointer image from cache or create and cache it.
        
        Args:
            pointer_image: The original pointer image (pygame.Surface)
            rotation_deg: Rotation angle in degrees
            cache_dict: Cache dictionary to use (RPM or velocity cache)
        
        Returns:
            Rotated pointer surface (pygame.Surface)
        """
        # Round angle to tolerance level to reduce cache misses
        angle_key = round(rotation_deg / angle_tolerance) * angle_tolerance
        
        if angle_key not in cache_dict:
            # Not in cache, create and cache it
            rotated = pygame.transform.rotozoom(pointer_image, angle_key, 1.0)
            cache_dict[angle_key] = rotated
            # Limit cache size to 120 entries per pointer (covers full rotation at ~3° granularity)
            if len(cache_dict) > 120:
                # Remove oldest entry (simple FIFO, could use OrderedDict for LRU)
                cache_dict.pop(next(iter(cache_dict)))
        
        return cache_dict[angle_key]
    
    def _get_velocity(self):
        """Get velocity in km/h."""
        try:
            if self.world and self.world.player:
                v = self.world.player.get_velocity()
                return 3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)
        except Exception:
            pass
        return 0.0

    def _get_throttle(self):
        """Get throttle in range [0.0, 1.0]."""
        try:
            if self.world and self.world.player:
                control = self.world.player.get_control()
                return min(max(control.throttle, 0.0), 1.0)
        except Exception:
            pass
        return 0.0

    def _compose_dashboard_frame(self):
        """Compose one dashboard frame in local coordinates.
        """
        if self._dashboard_frame is None or self._offscreen_layer is None:
            return

        self._dashboard_frame.blit(self._offscreen_layer, (0, 0))

        # RPM pointer
        if self._render_pointers and self._rpm_pointer:
            if self._rpm_first_run:
                if self._rpm_activation_started and self._min_rpm_display > 1e-6:
                    frac_start = min(max(self._rpm_display_value / self._min_rpm_display, 0.0), 1.0)
                    rpm_rotation_deg = -(frac_start * self._min_rpm_rotation)
                else:
                    rpm_rotation_deg = 0.0
            else:
                rpm_val = min(max(self._rpm_display_value, self._min_rpm_display), self._max_rpm_display)
                frac = (rpm_val - self._min_rpm_display) / (self._max_rpm_display - self._min_rpm_display)
                rpm_rotation_deg = -(
                    self._min_rpm_rotation + frac * (self._max_rpm_rotation - self._min_rpm_rotation)
                )

            rotated_rpm_pointer = self._get_cached_rotated_pointer(
                self._rpm_pointer,
                rpm_rotation_deg,
                self._rpm_pointer_cache,
                self._rpm_angle_tolerance,
            )
            rpm_pointer_rect = rotated_rpm_pointer.get_rect(center=(self._left_center_x, self._center_y))
            self._dashboard_frame.blit(rotated_rpm_pointer, rpm_pointer_rect)

        # Velocity pointer
        if self._render_pointers and self._velocity_pointer:
            speed_clamped = min(max(self._get_velocity(), 0.0), self._max_speed)
            rotation_deg = -(speed_clamped / self._max_speed) * 100.0

            rotated_velocity_pointer = self._get_cached_rotated_pointer(
                self._velocity_pointer,
                rotation_deg,
                self._velocity_pointer_cache,
                self._velocity_angle_tolerance,
            )
            pointer_rect = rotated_velocity_pointer.get_rect(center=(self._right_center_x, self._center_y))
            self._dashboard_frame.blit(rotated_velocity_pointer, pointer_rect)

        # Active green blinkers only; grey ones are in static layer.
        if self._left_indicator_on and self._blink_phase_on and self._ts_arrow_left_green:
            self._dashboard_frame.blit(
                self._ts_arrow_left_green,
                self._ts_arrow_left_green.get_rect(center=self._ts_left_center)
            )
        if self._right_indicator_on and self._blink_phase_on and self._ts_arrow_right_green:
            self._dashboard_frame.blit(
                self._ts_arrow_right_green,
                self._ts_arrow_right_green.get_rect(center=self._ts_right_center)
            )
    
    def update(self, dt):
        """Update dashboard state based on delta time.
        
        Args:
            dt: Delta time in seconds
        """
        throttle = self._get_throttle()
        self._update_blinkers_from_vehicle_lights()
        
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
                # pointer increase (smooth)
                up = self._rpm_decay_up_per_sec * dt
                self._rpm_display_value = min(self._rpm_display_value + up, target_rpm)
            elif target_rpm < self._rpm_display_value:
                # pointer decrease (smooth)
                down = self._rpm_decay_down_per_sec * dt
                self._rpm_display_value = max(self._rpm_display_value - down, max(target_rpm, min_rpm))
        
        # Turn signal blinking
        if self._left_indicator_on or self._right_indicator_on:
            self._blink_timer += dt
            while self._blink_timer >= self._blink_interval:
                self._blink_timer -= self._blink_interval
                self._blink_phase_on = not self._blink_phase_on
        else:
            self._blink_timer = 0.0
            self._blink_phase_on = True

        # Compose dashboard every update tick.
        self._compose_dashboard_frame()

    def _update_blinkers_from_vehicle_lights(self):
        """Mirror left/right indicator state from CARLA vehicle light state."""
        try:
            if not self.world or not self.world.player:
                return

            light_state = self.world.player.get_light_state()
            state_value = int(light_state)
            left_on = bool(state_value & int(carla.VehicleLightState.LeftBlinker))
            right_on = bool(state_value & int(carla.VehicleLightState.RightBlinker))

            if left_on != self._left_indicator_on:
                self._blink_timer = 0.0
                self._blink_phase_on = True
            if right_on != self._right_indicator_on:
                self._blink_timer = 0.0
                self._blink_phase_on = True

            self._left_indicator_on = left_on
            self._right_indicator_on = right_on
        except Exception:
            pass
    
    def render(self, display):
        """Render dashboard to display surface using cached layers and pointers.
        
        Args:
            display: pygame display surface
        """
        # Reuse latest frame composed in update().
        if self._dashboard_frame is None:
            self._compose_dashboard_frame()
        if self._dashboard_frame is not None:
            display.blit(self._dashboard_frame, (self.dashboard_x, self.dashboard_y))
    
    def set_left_indicator(self, enabled):
        """Set left turn indicator state."""
        self._left_indicator_on = enabled
        self._blink_timer = 0.0
        self._blink_phase_on = True
    
    def set_right_indicator(self, enabled):
        """Set right turn indicator state."""
        self._right_indicator_on = enabled
        self._blink_timer = 0.0
        self._blink_phase_on = True
