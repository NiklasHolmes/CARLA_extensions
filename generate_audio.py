"""
Centralized audio management for CARLA extensions
"""

import pygame
import pygame.mixer
import numpy as np
import time
import os
from typing import Optional, List, Dict


class ChannelPool:
    """ Manages a pool of reusable audio channels for efficient memory usage. """
    
    def __init__(self, pool_size: int = 6):
        """
        Initialize channel pool.
        
        Args:
            pool_size (int): Number of channels in the pool (default: 6)
                - Channels will be allocated on-demand when pygame.mixer is initialized
        """
        self.pool_size = pool_size
        self.channels: List[pygame.mixer.Channel] = []
        self._allocated = False
    
    def initialize(self):
        """ Initialize channels from pygame mixer. """
        if self._allocated or not pygame.mixer.get_init():
            return False
        
        try:
            for i in range(self.pool_size):
                self.channels.append(pygame.mixer.Channel(i))
            self._allocated = True
            print(f"[ChannelPool] Initialized {self.pool_size} channels")
            return True
        except Exception as e:
            print(f"[ChannelPool] ERROR initializing channels: {e}")
            return False
    
    def get_channel(self, priority: int = 0) -> Optional[pygame.mixer.Channel]:
        """
        Get an available channel from the pool.
        
        Args:
            priority (int): Channel priority (higher = more reserved for that type)
            
        Returns:
            pygame.mixer.Channel or None if no channels available
        """
        if not pygame.mixer.get_init():
            return None
        
        # Try to get idle channels
        for channel in self.channels:
            if not channel.get_busy():
                return channel
        
        # If all busy => return None
        return None
    
    def release_channel(self, channel: pygame.mixer.Channel):
        """ Mark channel as available (it will auto-stop if needed). """
        # channels are auto-released when finish playing
        pass


class BaseAudioGenerator:
    """ Base class for all sound generators """
    
    def __init__(self, channel_pool: ChannelPool):
        self.channel_pool = channel_pool
        self.current_channel: Optional[pygame.mixer.Channel] = None
        self._sound_loaded = False
        self.base_volume = 1.0
    
    def _load_sound(self, file_path: str, sound_name: str = "sound") -> Optional[pygame.mixer.Sound]:
        """
        Load a sound file with error handling.
        
        Args:
            file_path (str): Path to audio file
            sound_name (str): Name for logging
            
        Returns:
            pygame.mixer.Sound or None if failed
        """
        if not pygame.mixer.get_init():
            print(f"[{sound_name}] ERROR: Mixer not initialized")
            return None
        
        if not os.path.exists(file_path):
            print(f"[{sound_name}] ERROR: File not found: {file_path}")
            return None
        
        try:
            sound = pygame.mixer.Sound(file_path)
            print(f"[{sound_name}] Loaded: {file_path}")
            return sound
        except Exception as e:
            print(f"[{sound_name}] ERROR loading: {e}")
            return None
    
    def stop(self, fadeout_ms: int = 0):
        """Stop the sound with optional fadeout."""
        if self.current_channel is not None:
            if fadeout_ms > 0:
                self.current_channel.fadeout(fadeout_ms)
            else:
                self.current_channel.stop()
            self.current_channel = None
    
    def update(self, *args, **kwargs):
        """Update method - override in subclasses."""
        pass


class EngineAudio(BaseAudioGenerator):
    """ Multi-channel engine audio with smooth RPM transitions """
    
    def __init__(self, channel_pool: ChannelPool, idle_path: str, 
                 mid_path: Optional[str] = None, high_path: Optional[str] = None,
                 base_volume: float = 0.1):
        """
        Initialize engine audio with three RPM levels.
        
        Args:
            channel_pool (ChannelPool): Shared channel pool
            idle_path (str): Engine idle sound (0-33% throttle)
            mid_path (str): Mid RPM sound (33-66% throttle) - optional
            high_path (str): High RPM sound (66-100% throttle) - optional
            base_volume (float): Overall volume multiplier
        """
        super().__init__(channel_pool)
        
        self.idle_path = idle_path
        self.mid_path = mid_path if mid_path else idle_path
        self.high_path = high_path if high_path else self.mid_path
        
        self.base_volume = base_volume
        
        # Three separate channels for each RPM level
        self.idle_channel: Optional[pygame.mixer.Channel] = None
        self.mid_channel: Optional[pygame.mixer.Channel] = None
        self.high_channel: Optional[pygame.mixer.Channel] = None
        
        # Sounds
        self.idle_sound: Optional[pygame.mixer.Sound] = None
        self.mid_sound: Optional[pygame.mixer.Sound] = None
        self.high_sound: Optional[pygame.mixer.Sound] = None
        
        self.playing = False
        self.last_throttle_time = 0.0
        self.fadeout_ms = 1500
        self.stop_delay = 5.0
        
        # Current volumes for smooth fading
        self.idle_volume = 0.0
        self.mid_volume = 0.0
        self.high_volume = 0.0
    
    def _load_sounds(self):
        """ Load all engine sounds (lazy loading). """
        if self._sound_loaded:
            return
        
        if not pygame.mixer.get_init():
            print("[EngineAudio] WARNING: Mixer not initialized yet")
            return
        
        self.idle_sound = self._load_sound(self.idle_path, "EngineAudio_Idle")
        self.mid_sound = self._load_sound(self.mid_path, "EngineAudio_Mid")
        if self.mid_sound is None:
            self.mid_sound = self.idle_sound
        
        self.high_sound = self._load_sound(self.high_path, "EngineAudio_High")
        if self.high_sound is None:
            self.high_sound = self.mid_sound
        
        self._sound_loaded = self.idle_sound is not None
    
    def _ensure_channels(self) -> bool:
        """ Allocate specific channels for engine audio. """
        if not pygame.mixer.get_init():
            return False
        
        try:
            if self.idle_channel is None:
                self.idle_channel = pygame.mixer.Channel(3)
            if self.mid_channel is None:
                self.mid_channel = pygame.mixer.Channel(4)
            if self.high_channel is None:
                self.high_channel = pygame.mixer.Channel(5)
            return True
        except Exception as e:
            print(f"[EngineAudio] ERROR allocating channels: {e}")
            return False
    
    def _start_all_loops(self):
        """ Start all three sound loops (will be controlled by volume). """
        if self.idle_sound is not None and not self.idle_channel.get_busy():
            self.idle_channel.play(self.idle_sound, loops=-1)
        if self.mid_sound is not None and not self.mid_channel.get_busy():
            self.mid_channel.play(self.mid_sound, loops=-1)
        if self.high_sound is not None and not self.high_channel.get_busy():
            self.high_channel.play(self.high_sound, loops=-1)
    
    def update(self, throttle_value: float):
        """
        Update engine audio based on throttle.
        
        Call this EVERY FRAME with throttle_value range [0..1]
        """
        if not self._sound_loaded:
            self._load_sounds()
        
        if not self._ensure_channels() or self.idle_sound is None:
            return
        
        now = time.time()
        
        if throttle_value > 0:
            self.last_throttle_time = now
            
            if not self.playing:
                self._start_all_loops()
                self.playing = True
            
            # Calculate target volumes based on throttle
            if throttle_value < 0.33:
                progress = throttle_value / 0.33
                target_idle = 1.0
                target_mid = progress * 0.5
                target_high = 0.0
            elif throttle_value < 0.66:
                progress = (throttle_value - 0.33) / 0.33
                target_idle = 1.0 - progress * 0.5
                target_mid = 0.5 + progress * 0.5
                target_high = progress * 0.3
            else:
                progress = (throttle_value - 0.66) / 0.34
                target_idle = 0.5 * (1.0 - progress)
                target_mid = 1.0 - progress * 0.7
                target_high = 0.3 + progress * 0.7
            
            # Smooth volume transitions
            smoothing = 0.15
            self.idle_volume = self.idle_volume * smoothing + target_idle * (1.0 - smoothing)
            self.mid_volume = self.mid_volume * smoothing + target_mid * (1.0 - smoothing)
            self.high_volume = self.high_volume * smoothing + target_high * (1.0 - smoothing)
            
            # Scale by throttle for dynamics
            overall_volume = 0.5 + (throttle_value ** 1.5) * 0.5
            
            self.idle_channel.set_volume(self.idle_volume * overall_volume * self.base_volume)
            self.mid_channel.set_volume(self.mid_volume * overall_volume * self.base_volume)
            self.high_channel.set_volume(self.high_volume * overall_volume * self.base_volume)
        
        else:
            # Fadeout if no throttle for stop_delay seconds
            if self.playing and (now - self.last_throttle_time > self.stop_delay):
                self.idle_channel.fadeout(self.fadeout_ms)
                self.mid_channel.fadeout(self.fadeout_ms)
                self.high_channel.fadeout(self.fadeout_ms)
                self.playing = False
                self.idle_volume = 0.0
                self.mid_volume = 0.0
                self.high_volume = 0.0


class HornAudio(BaseAudioGenerator):
    """ Single-shot horn sound with quick response. """
    
    def __init__(self, channel_pool: ChannelPool, horn_path: str, 
                 base_volume: float = 0.9, fadeout_ms: int = 120):
        """
        Initialize horn audio.
        
        Args:
            channel_pool (ChannelPool): Shared channel pool
            horn_path (str): Path to horn sound file
            base_volume (float): Horn volume (0.0-1.0)
            fadeout_ms (int): Fadeout duration in milliseconds
        """
        super().__init__(channel_pool)
        
        self.horn_path = horn_path
        self.base_volume = base_volume
        self.fadeout_ms = fadeout_ms
        
        self.horn_sound: Optional[pygame.mixer.Sound] = None
        self.is_on = False
    
    def _load_sound(self):
        """ Load horn sound (lazy loading). """
        if self._sound_loaded:
            return
        
        if not pygame.mixer.get_init():
            print("[HornAudio] WARNING: Mixer not initialized")
            return
        
        self.horn_sound = super()._load_sound(self.horn_path, "HornAudio")
        if self.horn_sound is not None:
            self.horn_sound.set_volume(self.base_volume)
            self._sound_loaded = True
    
    def play(self):
        """ Start playing horn. """
        if not self._sound_loaded:
            self._load_sound()
        
        if self.horn_sound is None or not pygame.mixer.get_init():
            return
        
        if not self.is_on:
            self.current_channel = self.channel_pool.get_channel()
            if self.current_channel is not None:
                self.current_channel.play(self.horn_sound)
                self.is_on = True
            else:
                print("[HornAudio] WARNING: No channels available")
    
    def stop(self, fadeout_ms: Optional[int] = None):
        """ Stop horn sound. """
        if fadeout_ms is None:
            fadeout_ms = self.fadeout_ms
        
        if self.current_channel is not None:
            if fadeout_ms > 0:
                self.current_channel.fadeout(fadeout_ms)
            else:
                self.current_channel.stop()
            self.current_channel = None
        
        self.is_on = False

class BlinkerAudio(BaseAudioGenerator):
    """Blinker sound"""
    
    def __init__(self, channel_pool: ChannelPool, blinker_path: str, 
                 base_volume: float = 0.9):
        """
        Initialize blinker audio.
        
        Args:
            channel_pool (ChannelPool): Shared channel pool
            blinker_path (str): Path to blinker sound file
            base_volume (float): Blinker volume (0.0-1.0)
        """
        super().__init__(channel_pool)
        
        self.blinker_path = blinker_path
        self.base_volume = base_volume

        self.blinker_sound: Optional[pygame.mixer.Sound] = None
        self.min_interval = 0.1
    
    def _load_sound(self):
        """ Load blinker sound (lazy loading)."""
        if self._sound_loaded:
            return
        
        if not pygame.mixer.get_init():
            print("[BlinkerAudio] WARNING: Mixer not initialized")
            return
        
        self.blinker_sound = super()._load_sound(self.blinker_path, "BlinkerAudio")
        if self.blinker_sound is not None:
            self.blinker_sound.set_volume(self.base_volume)
            self.min_interval = max(self.min_interval, self.blinker_sound.get_length())
            self._sound_loaded = True
    
    def play(self):
        """ Start playing blinker."""
        if not self._sound_loaded:
            self._load_sound()
        
        if self.blinker_sound is None or not pygame.mixer.get_init():
            return

        if self.current_channel is not None and self.current_channel.get_busy():
            return

        if self.current_channel is None:
            self.current_channel = self.channel_pool.get_channel()

        if self.current_channel is not None:
            self.current_channel.play(self.blinker_sound, loops=0)
        else:
            print("[BlinkerAudio] WARNING: No channels available")


class BrakeAudio(BaseAudioGenerator):
    """Brake sound"""
    
    def __init__(self, channel_pool: ChannelPool, brake_path: str, 
                 base_volume: float = 0.3, fadeout_ms: int = 120):
        """
        Initialize brake audio.
        
        Args:
            channel_pool (ChannelPool): Shared channel pool
            brake_path (str): Path to brake sound file
            base_volume (float): Brake volume (0.0-1.0)
            fadeout_ms (int): Fadeout duration in milliseconds
        """
        super().__init__(channel_pool)
        
        self.brake_path = brake_path
        self.base_volume = base_volume
        self.fadeout_ms = fadeout_ms

        self.brake_sound: Optional[pygame.mixer.Sound] = None
        self.is_on = False
        self.last_play_time = 0.0
        self.min_interval = 0.1

        # Brake sound tuning
        self.speed_full_kmh = 60.0
        self.intensity_low = 0.35
        self.intensity_mid = 0.70
        self.volume_low = 0.35
        self.volume_mid = 0.60
        self.volume_high = 1.00
        self.duration_low = 0.40
        self.duration_mid = 0.70
    
    def _load_sound(self):
        """Load brake sound (lazy loading)."""
        if self._sound_loaded:
            return
        
        if not pygame.mixer.get_init():
            print("[BrakeAudio] WARNING: Mixer not initialized")
            return
        
        self.brake_sound = super()._load_sound(self.brake_path, "BrakeAudio")
        if self.brake_sound is not None:
            self.brake_sound.set_volume(self.base_volume)
            self.min_interval = max(self.min_interval, self.brake_sound.get_length())
            self._sound_loaded = True
    
    def _get_brake_profile(self, speed_kmh: float, brake_strength: float) -> Dict[str, float]:
        """Return volume scale and max playback time for the brake sound."""
        speed_factor = min(max(speed_kmh / self.speed_full_kmh, 0.0), 1.0)
        brake_factor = min(max(brake_strength, 0.0), 1.0)
        intensity = 0.6 * brake_factor + 0.4 * speed_factor

        if intensity < self.intensity_low:
            return {"volume": self.volume_low, "duration": self.duration_low}
        if intensity < self.intensity_mid:
            return {"volume": self.volume_mid, "duration": self.duration_mid}
        return {"volume": self.volume_high, "duration": 1.0}

    def play(self, brake_strength: Optional[float] = None, speed_kmh: Optional[float] = None):
        """Start playing brake sound (one-shot)."""
        if not self._sound_loaded:
            self._load_sound()
        
        if self.brake_sound is None or not pygame.mixer.get_init():
            return

        now = time.time()
        sound_len_ms = int(self.brake_sound.get_length() * 1000)
        speed_kmh = max(0.0, speed_kmh or 0.0)
        brake_strength = 1.0 if brake_strength is None else float(brake_strength)
        profile = self._get_brake_profile(speed_kmh, brake_strength)
        volume_scale = profile["volume"]
        duration_scale = profile["duration"]
        maxtime_ms = 0 if duration_scale >= 1.0 else max(80, int(sound_len_ms * duration_scale))
        play_interval = max(0.08, (sound_len_ms if maxtime_ms == 0 else maxtime_ms) / 1000.0)

        if (now - self.last_play_time) < min(self.min_interval, play_interval):
            return

        if self.current_channel is not None and self.current_channel.get_busy():
            return

        if self.current_channel is None:
            self.current_channel = self.channel_pool.get_channel()

        if self.current_channel is not None:
            self.current_channel.set_volume(self.base_volume * volume_scale)
            if maxtime_ms == 0:
                self.current_channel.play(self.brake_sound, loops=0)
            else:
                self.current_channel.play(self.brake_sound, loops=0, maxtime=maxtime_ms)
            self.is_on = True
            self.last_play_time = now
        else:
            print("[BrakeAudio] WARNING: No channels available")

    def stop(self, fadeout_ms: Optional[int] = None):
        """Stop brake sound."""
        if fadeout_ms is None:
            fadeout_ms = self.fadeout_ms

        if self.current_channel is not None:
            if fadeout_ms > 0:
                self.current_channel.fadeout(fadeout_ms)
            else:
                self.current_channel.stop()
        self.is_on = False


class ProximityAlertAudio(BaseAudioGenerator):
    """Proximity alert beeping sound - plays continuously with variable interval"""
    
    def __init__(self, channel_pool: ChannelPool, proximity_path: str, 
                 base_volume: float = 0.1):
        """
        Initialize proximity alert audio.
        
        Args:
            channel_pool (ChannelPool): Shared channel pool
            proximity_path (str): Path to proximity beep sound file
            base_volume (float): Alert volume (0.0-1.0)
        """
        super().__init__(channel_pool)
        
        self.proximity_path = proximity_path
        self.base_volume = base_volume
        
        self.proximity_sound: Optional[pygame.mixer.Sound] = None
        self.is_playing = False
        self.last_beep_time = 0.0
        self.current_interval = 0.0
        self.beep_mode = "off"  # "off", "far", "medium", "close", "critical"
    
    def _load_sound(self):
        """Load proximity alert sound (lazy loading)."""
        if self._sound_loaded:
            return
        
        if not pygame.mixer.get_init():
            print("[ProximityAlertAudio] WARNING: Mixer not initialized")
            return
        
        self.proximity_sound = super()._load_sound(self.proximity_path, "ProximityAlertAudio")
        if self.proximity_sound is not None:
            self.proximity_sound.set_volume(self.base_volume)
            self._sound_loaded = True
    
    def update(self, distance_group: str):
        """
        Update proximity alert based on distance group.
        
        Args:
            distance_group (str): One of "off", "far", "medium", "close", "critical"
        """
        if not self._sound_loaded:
            self._load_sound()
        
        if self.proximity_sound is None or not pygame.mixer.get_init():
            return
        
        # Map distance groups to beep intervals (in seconds)
        interval_map = {
            "off": 0.0,       # No beeping
            "safe": 0.0,      # No beeping (>0.5m from vehicle edge)
            "medium": 1.0,    # 0.25-0.5m: medium beep
            "close": 0.5,     # 0.05-0.25m: fast beep
            "critical": 0.0   # <0.05m: continuous (loop) - actual contact
        }
        
        target_interval = interval_map.get(distance_group, 0.0)
        
        # Handle mode changes
        if distance_group != self.beep_mode:
            self.beep_mode = distance_group
            self.current_interval = target_interval
            
            # Stop current sound if switching modes
            if self.current_channel is not None:
                self.current_channel.stop()
                self.current_channel = None
            
            # Reset timer for immediate beep on mode change
            self.last_beep_time = 0.0
        
        now = time.time()
        
        # Safe mode - stop everything
        if distance_group == "safe":
            if self.current_channel is not None:
                self.current_channel.stop()
                self.current_channel = None
            self.is_playing = False
            return
        
        # Critical mode - continuous loop
        if distance_group == "critical":
            if self.current_channel is None or not self.current_channel.get_busy():
                self.current_channel = self.channel_pool.get_channel()
                if self.current_channel is not None:
                    self.current_channel.play(self.proximity_sound, loops=-1)  # Infinite loop
                    self.is_playing = True
            return
        
        # Beeping modes (far, medium, close)
        if (now - self.last_beep_time) >= self.current_interval:
            if self.current_channel is None:
                self.current_channel = self.channel_pool.get_channel()
            
            if self.current_channel is not None:
                self.current_channel.play(self.proximity_sound, loops=0)  # One-shot beep
                self.last_beep_time = now
                self.is_playing = True
    
    def stop(self):
        """Stop proximity alert."""
        if self.current_channel is not None:
            self.current_channel.stop()
            self.current_channel = None
        self.is_playing = False
        self.beep_mode = "off"


class SongAudio:
    """Single music track playback with offset, fade-in, and scheduled fade-out."""

    def __init__(
        self,
        song_path: str,
        start_seconds: float = 0.0,
        play_seconds: float = 30.0,
        fade_in_ms: int = 3000,
        fade_out_ms: int = 3000,
        volume: float = 0.8,
        channel_index: int = 6,
    ):
        self.song_path = song_path
        self.start_seconds = max(0.0, float(start_seconds))
        self.play_seconds = max(0.0, float(play_seconds))
        self.fade_in_ms = max(0, int(fade_in_ms))
        self.fade_out_ms = max(0, int(fade_out_ms))
        self.volume = max(0.0, min(1.0, float(volume)))
        self.channel_index = int(channel_index)

        self._source_sound: Optional[pygame.mixer.Sound] = None
        self._trimmed_sound: Optional[pygame.mixer.Sound] = None
        self._channel: Optional[pygame.mixer.Channel] = None
        self._sound_loaded = False
        self._play_started = False
        self._fadeout_started = False
        self._finished = False
        self._start_time: Optional[float] = None

    def _resolve_song_path(self) -> str:
        if os.path.isabs(self.song_path):
            return self.song_path

        base_dir = os.path.dirname(__file__)
        return os.path.normpath(os.path.join(base_dir, self.song_path))

    @property
    def is_finished(self) -> bool:
        return self._finished

    def _ensure_mixer(self):
        if pygame.mixer.get_init():
            return True

        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            return True
        except Exception as exc:
            print(f"[SongAudio] ERROR initializing mixer: {exc}")
            return False

    def _ensure_channel(self):
        if not pygame.mixer.get_init():
            return False

        try:
            if pygame.mixer.get_num_channels() <= self.channel_index:
                pygame.mixer.set_num_channels(self.channel_index + 1)
            if self._channel is None:
                self._channel = pygame.mixer.Channel(self.channel_index)
            return True
        except Exception as exc:
            print(f"[SongAudio] ERROR allocating channel {self.channel_index}: {exc}")
            return False

    def _load_sound(self):
        if self._sound_loaded:
            return

        if not self._ensure_mixer():
            return

        resolved_song_path = self._resolve_song_path()

        if not os.path.exists(resolved_song_path):
            print(f"[SongAudio] ERROR: File not found: {resolved_song_path}")
            return

        try:
            self._source_sound = pygame.mixer.Sound(resolved_song_path)
            source_array = pygame.sndarray.array(self._source_sound)
            sample_rate = pygame.mixer.get_init()[0]
            start_sample = int(self.start_seconds * sample_rate)
            segment_seconds = self.play_seconds + (self.fade_out_ms / 1000.0)
            segment_samples = max(1, int(segment_seconds * sample_rate))
            end_sample = start_sample + segment_samples
            trimmed_array = source_array[start_sample:end_sample]

            if trimmed_array.size == 0:
                print(f"[SongAudio] ERROR: Segment is empty after trimming: {self.song_path}")
                return

            self._trimmed_sound = pygame.sndarray.make_sound(np.ascontiguousarray(trimmed_array))
            self._trimmed_sound.set_volume(self.volume)
            self._sound_loaded = True
            print(
                f"[SongAudio] Loaded segment: path={resolved_song_path} start={self.start_seconds:.2f}s "
                f"play={self.play_seconds:.2f}s fade_out={self.fade_out_ms}ms"
            )
        except Exception as exc:
            print(f"[SongAudio] ERROR loading {resolved_song_path}: {exc}")

    def play(self, sim_time: Optional[float] = None):
        if self._finished:
            return False

        if not self._sound_loaded:
            self._load_sound()

        if self._trimmed_sound is None or not self._ensure_channel():
            return False

        if self._channel.get_busy():
            return True

        self._channel.play(self._trimmed_sound, fade_ms=self.fade_in_ms)
        self._channel.set_volume(self.volume)
        self._play_started = True
        self._fadeout_started = False
        self._finished = False
        self._start_time = float(sim_time) if sim_time is not None else time.time()
        print(f"[SongAudio] Playback started on channel {self.channel_index}")
        return True

    def update(self, sim_time: Optional[float] = None):
        if not self._play_started or self._finished:
            return

        if self._start_time is None:
            self._start_time = float(sim_time) if sim_time is not None else time.time()

        now = float(sim_time) if sim_time is not None else time.time()
        elapsed = now - self._start_time

        if (not self._fadeout_started) and elapsed >= self.play_seconds:
            if self._channel is not None:
                self._channel.fadeout(self.fade_out_ms)
            self._fadeout_started = True
            print(f"[SongAudio] Fade-out started after {elapsed:.2f}s")

        if self._fadeout_started and self._channel is not None and not self._channel.get_busy():
            self._finished = True
            print("[SongAudio] Playback finished")

    def stop(self, fadeout_ms: Optional[int] = None):
        if fadeout_ms is None:
            fadeout_ms = self.fade_out_ms

        if self._channel is not None:
            if fadeout_ms > 0:
                self._channel.fadeout(int(fadeout_ms))
            else:
                self._channel.stop()

        self._play_started = False
        self._fadeout_started = False
        self._finished = True

class DummyAudioGenerator:
    """No-op audio generator - does nothing when audio is disabled."""
    def update_engine(self, *args, **kwargs): pass
    def play_horn(self, *args, **kwargs): pass
    def stop_horn(self, *args, **kwargs): pass
    def play_blinker(self, *args, **kwargs): pass
    def play_brake(self, *args, **kwargs): pass
    def update_proximity_alert(self, *args, **kwargs): pass
    def stop_proximity_alert(self, *args, **kwargs): pass
    def quit(self): pass
    def init(self, *args, **kwargs): pass

class AudioGenerator:
    """Main audio manager - initializes and controls all sounds."""
    
    def __init__(self, 
                 engine_idle_path: str,
                 engine_mid_path: Optional[str] = None,
                 engine_high_path: Optional[str] = None,
                 horn_path: Optional[str] = None,
                 blinker_path: Optional[str] = None,
                 brake_path: Optional[str] = None,
                 proximity_alert_path: Optional[str] = None,
                 channel_pool_size: int = 6):
        """
        Initialize all audio generators.
        
        Args:
            engine_idle_path (str): Path to engine idle sound
            engine_mid_path (str): Path to engine mid RPM sound
            engine_high_path (str): Path to engine high RPM sound
            horn_path (str): Path to horn sound
            blinker_path (str): Path to blinker sound
            brake_path (str): Path to brake sound
            proximity_alert_path (str): Path to proximity alert beep sound
            channel_pool_size (int): Size of channel pool
        """
        self.initialized = False
        self.channel_pool = ChannelPool(pool_size=channel_pool_size)
        
        self.engine_audio: Optional[EngineAudio] = None
        self.horn_audio: Optional[HornAudio] = None
        self.blinker_audio: Optional[BlinkerAudio] = None
        self.brake_audio: Optional[BrakeAudio] = None
        self.proximity_alert_audio: Optional[ProximityAlertAudio] = None
        
        # Initialize engines
        if engine_idle_path:
            self.engine_audio = EngineAudio(
                self.channel_pool,
                engine_idle_path,
                engine_mid_path,
                engine_high_path
            )
        
        # Initialize horn
        if horn_path:
            self.horn_audio = HornAudio(self.channel_pool, horn_path)

        # Initialize blinker
        if blinker_path:
            self.blinker_audio = BlinkerAudio(self.channel_pool, blinker_path)

        # Initialize brake
        if brake_path:
            self.brake_audio = BrakeAudio(self.channel_pool, brake_path)
        
        # Initialize proximity alert
        if proximity_alert_path:
            self.proximity_alert_audio = ProximityAlertAudio(self.channel_pool, proximity_alert_path)
    
    def init(self, frequency: int = 44100, channels: int = 2, buffer_size: int = 512):
        """
        Initialize pygame mixer.
        
        Args:
            frequency (int): Sample rate in Hz (default: 44100)
            channels (int): Number of channels (default: 2 - stereo)
            buffer_size (int): Buffer size (default: 512 - low latency)
        """
        try:
            pygame.mixer.init(frequency=frequency, size=-16, channels=channels, buffer=buffer_size)
            self.channel_pool.initialize()
            self.initialized = True
            print("[AudioGenerator] Mixer initialized successfully")
        except Exception as e:
            print(f"[AudioGenerator] ERROR initializing mixer: {e}")
    
    def update_engine(self, throttle_value: float):
        """Update engine audio (call every frame)."""
        if self.engine_audio is not None:
            self.engine_audio.update(throttle_value)
    
    def play_horn(self):
        """Play horn sound."""
        if self.horn_audio is not None:
            self.horn_audio.play()
    
    def stop_horn(self, fadeout_ms: int = 120):
        """Stop horn sound."""
        if self.horn_audio is not None:
            self.horn_audio.stop(fadeout_ms)

    def play_blinker(self):
        """Play blinker sound once."""
        if self.blinker_audio is not None:
            self.blinker_audio.play()
    
    def play_brake(self, brake_strength: Optional[float] = None, speed_kmh: Optional[float] = None):
        """Play brake sound once."""
        if self.brake_audio is not None:
            self.brake_audio.play(brake_strength=brake_strength, speed_kmh=speed_kmh)

    # def stop_brake(self, fadeout_ms: int = 120):
    #     """Stop brake sound."""
    #     if self.brake_audio is not None:
    #         self.brake_audio.stop(fadeout_ms)
    
    def update_proximity_alert(self, distance_group: str):
        """Update proximity alert based on distance group (safe/medium/close/critical)."""
        if self.proximity_alert_audio is not None:
            self.proximity_alert_audio.update(distance_group)
    
    def stop_proximity_alert(self):
        """Stop proximity alert."""
        if self.proximity_alert_audio is not None:
            self.proximity_alert_audio.stop()
    
    def quit(self):
        """Clean up audio resources."""
        try:
            pygame.mixer.stop()
            pygame.mixer.quit()
            self.initialized = False
            print("[AudioGenerator] Audio shutdown complete")
        except Exception as e:
            print(f"[AudioGenerator] ERROR during quit: {e}")
