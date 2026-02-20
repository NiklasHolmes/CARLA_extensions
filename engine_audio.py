import pygame
import time
import os
import pygame.mixer

class EngineAudio:
    def __init__(self, idle_path, mid_path=None, high_path=None, base_volume=0.75):
        """
        Engine audio with smooth RPM transitions using multiple channels.
        Each RPM level plays on its own channel and fades in/out for smooth transitions.
        
        - idle_path: Engine idle sound (0-33% throttle)
        - mid_path: Mid RPM sound (33-66% throttle) - optional
        - high_path: High RPM sound (66-100% throttle) - optional
        """
        self.idle_path = idle_path
        self.mid_path = mid_path if mid_path else idle_path
        self.high_path = high_path if high_path else self.mid_path
        
        self.base_volume = base_volume
        
        # Use separate channels for each RPM level (3, 4, 5)
        self.idle_channel = None
        self.mid_channel = None
        self.high_channel = None
        
        self.playing = False
        self.last_throttle_time = 0.0
        self.fadeout_ms = 1500
        self.stop_delay = 5.0  # seconds without throttle
        self._sound_loaded = False
        
        # Track current volumes for smooth fading
        self.idle_volume = 0.0
        self.mid_volume = 0.0
        self.high_volume = 0.0

    def _load_sounds(self):
        """Load sounds only when mixer is initialized."""
        if self._sound_loaded:
            return
        
        if not pygame.mixer.get_init():
            print("[EngineAudio] WARNING: Mixer not initialized yet. Sounds will be loaded later.")
            return
        
        try:
            if os.path.exists(self.idle_path):
                self.idle_sound = pygame.mixer.Sound(self.idle_path)
                print("[EngineAudio] Idle sound loaded")
            else:
                print("[EngineAudio] ERROR: Idle sound not found:", self.idle_path)
                return
            
            if os.path.exists(self.mid_path):
                self.mid_sound = pygame.mixer.Sound(self.mid_path)
                print("[EngineAudio] Mid RPM sound loaded")
            else:
                print("[EngineAudio] WARNING: Mid RPM sound not found, using idle")
                self.mid_sound = self.idle_sound
            
            if os.path.exists(self.high_path):
                self.high_sound = pygame.mixer.Sound(self.high_path)
                print("[EngineAudio] High RPM sound loaded")
            else:
                print("[EngineAudio] WARNING: High RPM sound not found, using mid")
                self.high_sound = self.mid_sound
            
            self._sound_loaded = True
            print("[EngineAudio] All engine sounds loaded successfully")
        except Exception as e:
            print(f"[EngineAudio] ERROR loading sounds: {e}")

    def _ensure_channels(self):
        """Ensure all three channels exist."""
        if not pygame.mixer.get_init():
            return False
        
        if self.idle_channel is None:
            self.idle_channel = pygame.mixer.Channel(3)
        if self.mid_channel is None:
            self.mid_channel = pygame.mixer.Channel(4)
        if self.high_channel is None:
            self.high_channel = pygame.mixer.Channel(5)
        
        return True

    def _start_all_loops(self):
        """Start all sound loops (they'll be controlled by volume)."""
        if self.idle_sound is not None and not self.idle_channel.get_busy():
            self.idle_channel.play(self.idle_sound, loops=-1)
        if self.mid_sound is not None and not self.mid_channel.get_busy():
            self.mid_channel.play(self.mid_sound, loops=-1)
        if self.high_sound is not None and not self.high_channel.get_busy():
            self.high_channel.play(self.high_sound, loops=-1)

    def update(self, throttle_value):
        """Call this EVERY FRAME — throttle_value ∈ [0..1]."""
        # Try to load sounds if not already loaded
        if not self._sound_loaded:
            self._load_sounds()
        
        if not self._ensure_channels() or self.idle_sound is None:
            return
        
        now = time.time()

        if throttle_value > 0:
            # Mark time of last throttle
            self.last_throttle_time = now

            # Start all loops if not playing
            if not self.playing:
                self._start_all_loops()
                self.playing = True
            
            # Calculate target volumes for each RPM level
            # Smooth crossfade between idle/mid/high
            if throttle_value < 0.33:
                # Idle zone: 0-33%
                progress = throttle_value / 0.33  # 0 to 1
                target_idle = 1.0
                target_mid = progress * 0.5
                target_high = 0.0
            elif throttle_value < 0.66:
                # Mid zone: 33-66%
                progress = (throttle_value - 0.33) / 0.33  # 0 to 1
                target_idle = 1.0 - progress * 0.5
                target_mid = 0.5 + progress * 0.5
                target_high = progress * 0.3
            else:
                # High zone: 66-100%
                progress = (throttle_value - 0.66) / 0.34  # 0 to 1
                target_idle = 0.5 * (1.0 - progress)
                target_mid = 1.0 - progress * 0.7
                target_high = 0.3 + progress * 0.7

            # Smooth volume transitions (exponential smoothing)
            smoothing = 0.15  # 0 = instant, 1 = no change
            self.idle_volume = self.idle_volume * smoothing + target_idle * (1.0 - smoothing)
            self.mid_volume = self.mid_volume * smoothing + target_mid * (1.0 - smoothing)
            self.high_volume = self.high_volume * smoothing + target_high * (1.0 - smoothing)

            # Also scale by overall throttle for dynamics
            overall_volume = 0.5 + (throttle_value ** 1.5) * 0.5
            
            # Apply volumes to channels
            self.idle_channel.set_volume(self.idle_volume * overall_volume)
            self.mid_channel.set_volume(self.mid_volume * overall_volume)
            self.high_channel.set_volume(self.high_volume * overall_volume)

        else:
            # Check if engine should fade out
            if self.playing and (now - self.last_throttle_time > self.stop_delay):
                self.idle_channel.fadeout(self.fadeout_ms)
                self.mid_channel.fadeout(self.fadeout_ms)
                self.high_channel.fadeout(self.fadeout_ms)
                self.playing = False
                self.idle_volume = 0.0
                self.mid_volume = 0.0
                self.high_volume = 0.0
