import ctypes
import os
from ctypes import wintypes


def _windows_monitor_rects():
    """Return monitor rectangles on Windows as (left, top, right, bottom)."""
    if os.name != 'nt':
        return []

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    rects = []
    monitor_enum_proc = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(RECT),
        wintypes.LPARAM,
    )

    def _callback(_monitor, _hdc, lprc_monitor, _data):
        r = lprc_monitor.contents
        rects.append((int(r.left), int(r.top), int(r.right), int(r.bottom)))
        return 1

    try:
        ctypes.windll.user32.EnumDisplayMonitors(0, 0, monitor_enum_proc(_callback), 0)
    except Exception:
        return []

    return rects


def _leftmost_monitor_rect():
    rects = _windows_monitor_rects()
    if not rects:
        return None
    return min(rects, key=lambda rect: (rect[0], rect[1]))


def prepare_window_start_position_left():
    """Set SDL window start position to the top-left corner of the left-most monitor."""
    if os.name != 'nt':
        return

    rect = _leftmost_monitor_rect()
    if rect is None:
        return

    left, top, _, _ = rect
    os.environ["SDL_VIDEO_WINDOW_POS"] = f"{left},{top}"


def apply_borderless_and_left_position_once(pygame):
    """Enforce borderless style and left-most corner placement once after window creation."""
    if os.name != 'nt':
        return

    try:
        wm_info = pygame.display.get_wm_info()
        hwnd = wm_info.get('window')
        rect = _leftmost_monitor_rect()
        if not hwnd or rect is None:
            return

        left, top, _, _ = rect
        user32 = ctypes.windll.user32

        GWL_STYLE = -16  # Offset for window style bits
        WS_OVERLAPPEDWINDOW = 0x00CF0000  # Standard framed window style
        WS_POPUP = 0x80000000  # Borderless top-level window style
        SWP_NOSIZE = 0x0001  # Keep current window size
        SWP_NOZORDER = 0x0004  # Keep current Z-order
        SWP_NOACTIVATE = 0x0010  # Do not steal input focus
        SWP_FRAMECHANGED = 0x0020  # Apply style change to window frame

        try:
            style = int(user32.GetWindowLongPtrW(int(hwnd), GWL_STYLE))
            user32.SetWindowLongPtrW(int(hwnd), GWL_STYLE, (style & ~WS_OVERLAPPEDWINDOW) | WS_POPUP)
        except AttributeError:
            style = int(user32.GetWindowLongW(int(hwnd), GWL_STYLE))
            user32.SetWindowLongW(int(hwnd), GWL_STYLE, (style & ~WS_OVERLAPPEDWINDOW) | WS_POPUP)

        user32.SetWindowPos(
            int(hwnd),
            0,
            int(left),
            int(top),
            0,
            0,
            SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED,
        )
    except Exception as e:
        print(f"[Window] WARNING: failed to apply startup borderless/position: {e}")
