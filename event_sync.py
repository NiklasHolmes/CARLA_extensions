"""
Synchronization trigger which use both audio and dashboard. 
"""

import socket
import time


class EventSync:
    """ coordinates connected audio + dahsboard events"""

    def __init__(self, audio_manager=None, default_blink_duration: float = 3.5,
                 dashboard_host: str = "127.0.0.1", dashboard_port: int = 39841):
        self.audio_manager = audio_manager
        self.default_blink_duration = max(0.1, float(default_blink_duration))
        self.dashboard_addr = (dashboard_host, int(dashboard_port))

        self._last_blinker_trigger = 0.0
        self._left_active_until = 0.0
        self._right_active_until = 0.0

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def set_audio_manager(self, audio_manager):
        self.audio_manager = audio_manager

    def _blinker_cooldown(self) -> float:
        """ cooldown = no overlap of blinker audio """
        try:
            if self.audio_manager is not None and self.audio_manager.blinker_audio is not None:
                interval = float(self.audio_manager.blinker_audio.min_interval)
                if interval > 0.0:
                    return interval
        except Exception:
            pass
        return self.default_blink_duration

    def _send_dashboard(self, message: str):
        try:
            self._socket.sendto(message.encode("ascii"), self.dashboard_addr)
        except Exception:
            pass

    def _trigger_blinker(self, side: str) -> bool:
        now = time.time()
        if (now - self._last_blinker_trigger) < self._blinker_cooldown():
            return False

        if self.audio_manager is not None:
            self.audio_manager.play_blinker()

        if side == "L":
            self._left_active_until = now + self.default_blink_duration
            self._send_dashboard("LEFT_ON")
        elif side == "R":
            self._right_active_until = now + self.default_blink_duration
            self._send_dashboard("RIGHT_ON")

        self._last_blinker_trigger = now
        return True

    def trigger_blinker_left(self) -> bool:
        return self._trigger_blinker("L")

    def trigger_blinker_right(self) -> bool:
        return self._trigger_blinker("R")

    def update(self):
        """ called regularly from main loop """
        now = time.time()

        if self._left_active_until > 0.0 and now >= self._left_active_until:
            self._left_active_until = 0.0
            self._send_dashboard("LEFT_OFF")

        if self._right_active_until > 0.0 and now >= self._right_active_until:
            self._right_active_until = 0.0
            self._send_dashboard("RIGHT_OFF")

    def shutdown(self):
        self._send_dashboard("LEFT_OFF")
        self._send_dashboard("RIGHT_OFF")
        try:
            self._socket.close()
        except Exception:
            pass
