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
        
        # Dashboard dimensions: 1/3 of screen width, positioned bottom-left
        self.dashboard_width = display_width // 3
        self.dashboard_height = display_height // 2  # Proportional height
        self.dashboard_x = 0
        self.dashboard_y = display_height - self.dashboard_height + 100
        
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
        """Render dashboard to display surface.
        
        Args:
            display: pygame display surface
        """
        # Transparent surface keeps the PNG half-circle shape without a rectangular fill.
        dashboard_surface = pygame.Surface((self.dashboard_width, self.dashboard_height), pygame.SRCALPHA)
        
        # Blit background image if available
        if self._background:
            dashboard_surface.blit(self._background, (0, 0))
        
        # Get current velocity
        velocity_kmh = self._get_velocity()
        
        # Mirror the external dashboard layout formulas as closely as possible.
        center_y = self.dashboard_height // 2
        inward_shift = int(self.dashboard_width * 0.03)
        left_center_x = self.dashboard_width // 4 + inward_shift
        center_x = self.dashboard_width * 3 // 4 - inward_shift
        
        # Render RPM gauge (left half)
        if self._rpm_circle and self._rpm_pointer:
            rpm_circle_rect = self._rpm_circle.get_rect(center=(left_center_x, center_y))
            dashboard_surface.blit(self._rpm_circle, rpm_circle_rect)
            
            # RPM pointer rotation
            if self._rpm_first_run:
                if self._rpm_activation_started and self._min_rpm_display > 1e-6:
                    # Smooth visible transition from 0 RPM to minimum RPM marker.
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
            rotated_rpm_pointer = pygame.transform.rotozoom(self._rpm_pointer, rpm_rotation_deg, 1.0)
            rpm_pointer_rect = rotated_rpm_pointer.get_rect(center=(left_center_x, center_y))
            dashboard_surface.blit(rotated_rpm_pointer, rpm_pointer_rect)
        
        # Render velocity gauge (right half)
        if self._velocity_circle and self._velocity_pointer:
            circle_rect = self._velocity_circle.get_rect(center=(center_x, center_y))
            dashboard_surface.blit(self._velocity_circle, circle_rect)
            
            # Velocity pointer rotation (1:1 ratio)
            speed_clamped = min(max(velocity_kmh, 0.0), self._max_speed)
            rotation_deg = -(speed_clamped / self._max_speed) * 100.0
            rotated_pointer = pygame.transform.rotozoom(self._velocity_pointer, rotation_deg, 1.0)
            pointer_rect = rotated_pointer.get_rect(center=(center_x, center_y))
            dashboard_surface.blit(rotated_pointer, pointer_rect)

        # Center car image (same placement rule as external dashboard).
        if self._center_car_image:
            car_center_x = self.dashboard_width // 2
            car_center_y = int(self.dashboard_height * 0.30)
            car_rect = self._center_car_image.get_rect(center=(car_center_x, car_center_y))
            dashboard_surface.blit(self._center_car_image, car_rect)
        
        # Render turn signal arrows
        if self._ts_arrow_left_grey and self._velocity_circle:
            gauge_radius = self._velocity_circle.get_height() // 2
            ts_y = center_y - int(gauge_radius * 1.1)
            left_x = (self.dashboard_width // 4 + self.dashboard_width // 2) // 2
            right_x = (self.dashboard_width * 3 // 4 + self.dashboard_width // 2) // 2
            
            left_active = self._left_indicator_on and self._blink_phase_on
            right_active = self._right_indicator_on and self._blink_phase_on
            
            left_img = self._ts_arrow_left_green if left_active else self._ts_arrow_left_grey
            right_img = self._ts_arrow_right_green if right_active else self._ts_arrow_right_grey
            
            dashboard_surface.blit(left_img, left_img.get_rect(center=(left_x, ts_y)))
            dashboard_surface.blit(right_img, right_img.get_rect(center=(right_x, ts_y)))
        
        # Blit dashboard to main display at bottom-left corner
        display.blit(dashboard_surface, (self.dashboard_x, self.dashboard_y))
    
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
