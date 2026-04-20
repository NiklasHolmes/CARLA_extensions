# CARLA extensions

Current focus on manual control and dashboard for CARLA simulator.

## Command Line Parameters

- **`--res WIDTHxHEIGHT`**              – Display resolution (default: 1280x720)
- **`--sp FLOAT`**                      – Internal camera resolution scale (0.0-1.0, default: 1.0)
- **`--sp-upscale [smooth|fast]`**      – Upscaling filter for low resolution rendering (default: fast)
- **`--input [keyboard|gamepad]`**      – Input device (default: keyboard)
- **`--profile [simulator|supervisor]`** – Apply preset settings (explicit CLI flags override)
- **`--dashboard-display N`**           – Monitor index for dashboard window (default: 0)

### Examples

```bash
# custom resolution and performance scale
python manual_control.py --res 3840x1080 --sp 0.8

# gamepad (DualShock Controller tested) input with dashboard on second monitor
python manual_control.py --input gamepad --dashboard-display 1

# gamepad (DualShock Controller tested) input with dashboard on second monitor
python manual_control.py --profile simulator
```

## Window & Dashboard Modes
- **Main window**: position and frame can be controlled via `manual_control.py` by:
	- `WINDOW_START_LEFT`: top-left of the left-most monitor on Windows
	- `WINDOW_BORDERLESS`: borderless (hardly movable)

- **Dashboard modes** (set `DASHBOARD_MODE` in `manual_control.py`):

| Mode | Separate window | Size | Placement / behavior | Notes |
| --- | --- | --- | --- | --- |
| none | no | - | - | no dashboard (internal or external) |
| inside | no | auto (scaled from main window) | bottom-left overlay inside main window | no external process; costs client FPS |
| basic | yes | `DASHBOARD_SIZE` | normal framed window | db movable |
| second_screen | yes | fullscreen | borderless fullscreen on monitor `DB_SCREEN_INDEX` | - |
| overlapping | yes | `DASHBOARD_SIZE` | borderless, always-on-top, bottom-left over main window | no focus |

## Profiles
- **simulator** (`--profile simulator`): `USE_SCENE_FINAL=True`, `DASHBOARD_MODE=basic`, `ENABLE_AUDIO=True`, `--res 3840x1080`, `--sp 0.8`, `--input wheel`, `WINDOW_START_LEFT=False`, `WINDOW_BORDERLESS=False`.
- **supervisor** (`--profile supervisor`): `--res 1920x1080`, `--sp 0.6`.
- Explicit CLI flags like `--res`, `--sp`, and `--input` override profile defaults.


## Final Scene Camera

Set `USE_SCENE_FINAL = True` in code to enable final simulator view (first-person perspective from inside the vehicle).


## Audio Settings

To enable audio (engine, horn, blinker, brake, proximity alerts), set `ENABLE_AUDIO = True` in `manual_control.py`.
Default: `ENABLE_AUDIO = False` (uses DummyAudioGenerator for performance)


## Gamepad Controls (PS4/DualShock)

Driving:
- **Left stick** – Steer
- **R2 trigger** – Throttle
- **L2 trigger** – Brake
- **X button** – Hand-brake
- **O button** – Toggle reverse

Lights & signals:
- **L1 button** – Blinker left
- **R1 button** – Blinker right

Vehicle actions:
- **Square button ([ ])** – Horn
- **Triangle button (/\)** – Toggle camera

System:
- **L3 button** – Export performance metrics / turn HUD on/off (press left stick)
- **R3 button** – Respawn vehicle (press right stick)
- **Option button** – Quit
