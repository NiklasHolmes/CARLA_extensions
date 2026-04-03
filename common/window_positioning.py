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


def get_windows_monitor_rects():
    """Public wrapper for monitor rectangles on Windows."""
    return _windows_monitor_rects()


def get_pygame_window_hwnd(pygame):
    """Return native HWND for current pygame window on Windows, else None."""
    if os.name != 'nt':
        return None

    try:
        wm_info = pygame.display.get_wm_info()
        hwnd = wm_info.get('window')
        if not hwnd:
            return None
        return int(hwnd)
    except Exception:
        return None


def apply_borderless_style_windows(hwnd):
    """Apply borderless (popup) style to a window handle on Windows."""
    if os.name != 'nt' or not hwnd:
        return False

    try:
        user32 = ctypes.windll.user32

        GWL_STYLE = -16
        WS_OVERLAPPEDWINDOW = 0x00CF0000
        WS_POPUP = 0x80000000
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOZORDER = 0x0004
        SWP_NOACTIVATE = 0x0010
        SWP_FRAMECHANGED = 0x0020

        try:
            style = int(user32.GetWindowLongPtrW(int(hwnd), GWL_STYLE))
            user32.SetWindowLongPtrW(int(hwnd), GWL_STYLE, (style & ~WS_OVERLAPPEDWINDOW) | WS_POPUP)
        except AttributeError:
            style = int(user32.GetWindowLongW(int(hwnd), GWL_STYLE))
            user32.SetWindowLongW(int(hwnd), GWL_STYLE, (style & ~WS_OVERLAPPEDWINDOW) | WS_POPUP)

        user32.SetWindowPos(
            int(hwnd),
            0,
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED,
        )
        return True
    except Exception:
        return False


def set_window_topmost_windows(hwnd, enabled=True):
    """Set window topmost state on Windows without moving/resizing it."""
    if os.name != 'nt' or not hwnd:
        return False

    try:
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        user32.SetWindowPos.argtypes = [
            wintypes.HWND,
            wintypes.HWND,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint,
        ]
        user32.SetWindowPos.restype = wintypes.BOOL

        HWND_TOPMOST = wintypes.HWND(-1)
        HWND_NOTOPMOST = wintypes.HWND(-2)
        HWND_TOP = wintypes.HWND(0)
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOACTIVATE = 0x0010
        SWP_SHOWWINDOW = 0x0040

        insert_after = HWND_TOPMOST if enabled else HWND_NOTOPMOST
        ok = user32.SetWindowPos(
            wintypes.HWND(int(hwnd)),
            insert_after,
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW,
        )
        if ok:
            return True

        # Fallback: bring to top of normal windows if TOPMOST fails.
        if enabled:
            ok = user32.SetWindowPos(
                wintypes.HWND(int(hwnd)),
                HWND_TOP,
                0,
                0,
                0,
                0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW,
            )
            return bool(ok)

        return False
    except Exception:
        return False


def is_window_topmost_windows(hwnd):
    """Return True if the window has WS_EX_TOPMOST set on Windows."""
    if os.name != 'nt' or not hwnd:
        return False

    try:
        user32 = ctypes.windll.user32
        GWL_EXSTYLE = -20
        WS_EX_TOPMOST = 0x00000008
        try:
            style = int(user32.GetWindowLongPtrW(int(hwnd), GWL_EXSTYLE))
        except AttributeError:
            style = int(user32.GetWindowLongW(int(hwnd), GWL_EXSTYLE))
        return bool(style & WS_EX_TOPMOST)
    except Exception:
        return False


def set_window_noactivate_windows(hwnd, enabled=True):
    """Toggle WS_EX_NOACTIVATE for a window so it cannot take focus on click."""
    if os.name != 'nt' or not hwnd:
        return False

    try:
        user32 = ctypes.windll.user32
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOZORDER = 0x0004
        SWP_NOACTIVATE = 0x0010
        SWP_FRAMECHANGED = 0x0020

        try:
            style = int(user32.GetWindowLongPtrW(int(hwnd), GWL_EXSTYLE))
            new_style = (style | WS_EX_NOACTIVATE) if enabled else (style & ~WS_EX_NOACTIVATE)
            user32.SetWindowLongPtrW(int(hwnd), GWL_EXSTYLE, int(new_style))
        except AttributeError:
            style = int(user32.GetWindowLongW(int(hwnd), GWL_EXSTYLE))
            new_style = (style | WS_EX_NOACTIVATE) if enabled else (style & ~WS_EX_NOACTIVATE)
            user32.SetWindowLongW(int(hwnd), GWL_EXSTYLE, int(new_style))

        ok = user32.SetWindowPos(
            int(hwnd),
            0,
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE | SWP_FRAMECHANGED,
        )
        return bool(ok)
    except Exception:
        return False


def move_window_to_monitor_windows(hwnd, requested_index, resolve_display_index=None):
    """Move window to monitor top-left. Returns (monitor_idx, left, top) or None."""
    if os.name != 'nt' or not hwnd:
        return None

    rects = _windows_monitor_rects()
    if not rects:
        return None

    if resolve_display_index is not None:
        monitor_idx = int(resolve_display_index(requested_index, len(rects)))
    else:
        idx = int(requested_index)
        monitor_idx = max(0, min(idx, len(rects) - 1))

    left, top, _, _ = rects[monitor_idx]

    try:
        SWP_NOSIZE = 0x0001
        SWP_NOZORDER = 0x0004
        SWP_NOACTIVATE = 0x0010

        ctypes.windll.user32.SetWindowPos(
            int(hwnd),
            0,
            int(left),
            int(top),
            0,
            0,
            SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE,
        )
        return (monitor_idx, int(left), int(top))
    except Exception:
        return None


def move_window_overlapping_windows(
    hwnd,
    main_window_title,
    window_size,
    overlap_margin=(16, 16),
    previous_target=None,
    min_delta=1,
    show_window=True,
):
    """Place a window at bottom-left of another window and above it. Returns (x, y) or None."""
    if os.name != 'nt' or not hwnd:
        return None

    title = str(main_window_title or '').strip()
    if not title:
        return None

    try:
        user32 = ctypes.windll.user32
        main_hwnd = int(user32.FindWindowW(None, title))
        if not main_hwnd:
            return None

        rect = wintypes.RECT()
        if not user32.GetWindowRect(main_hwnd, ctypes.byref(rect)):
            return None

        width = int(window_size[0])
        height = int(window_size[1])
        margin_x = max(0, int(overlap_margin[0]))
        margin_y = max(0, int(overlap_margin[1]))

        target_x = int(rect.left + margin_x)
        target_y = int(rect.bottom - height - margin_y)

        rects = _windows_monitor_rects()
        for left, top, right, bottom in rects:
            if left <= rect.left < right and top <= rect.top < bottom:
                target_x = max(left, min(target_x, right - width))
                target_y = max(top, min(target_y, bottom - height))
                break

        if previous_target is not None:
            prev_x, prev_y = previous_target
            if abs(target_x - prev_x) <= min_delta and abs(target_y - prev_y) <= min_delta:
                return (int(target_x), int(target_y))

        SWP_NOSIZE = 0x0001
        SWP_NOACTIVATE = 0x0010
        SWP_SHOWWINDOW = 0x0040
        flags = SWP_NOSIZE | SWP_NOACTIVATE
        if show_window:
            flags |= SWP_SHOWWINDOW
        user32.SetWindowPos(
            int(hwnd),
            int(main_hwnd),
            int(target_x),
            int(target_y),
            0,
            0,
            flags,
        )
        return (int(target_x), int(target_y))
    except Exception:
        return None


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
        hwnd = get_pygame_window_hwnd(pygame)
        rect = _leftmost_monitor_rect()
        if not hwnd or rect is None:
            return

        left, top, _, _ = rect
        apply_borderless_style_windows(hwnd)

        SWP_NOSIZE = 0x0001                 # Keep current window size
        SWP_NOZORDER = 0x0004               # Keep current Z-order
        SWP_NOACTIVATE = 0x0010             # Do not steal input focus

        ctypes.windll.user32.SetWindowPos(
            int(hwnd),
            0,
            int(left),
            int(top),
            0,
            0,
            SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE,
        )
    except Exception as e:
        print(f"[Window] WARNING: failed to apply startup borderless/position: {e}")
