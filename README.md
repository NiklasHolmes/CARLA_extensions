# CARLA extensions

Current focus on manual control and dashboard for CARLA simulator.

## Command Line Parameters

- **`--res WIDTHxHEIGHT`**              – Display resolution (default: 1280x720)
- **`--sp FLOAT`**                      – Internal camera resolution scale (0.0-1.0, default: 1.0)
- **`--sp-upscale [smooth|fast]`**      – Upscaling filter for low resolution rendering (default: fast)
- **`--input [keyboard|gamepad]`**      – Input device (default: keyboard)
- **`--dashboard-display N`**           – Monitor index for dashboard window (default: 0)

examples: 
python manual_control.py --res 3840x1080 --sp 0.8
python manual_control.py --input gamepad --dashboard-display 1


## Final Scene Camera

Set `USE_SCENE_FINAL_CAMERA = True` in code to enable final simulator view (first-person perspective from inside the vehicle).

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
- **L3 button** – Export performance metrics (press left stick)

System:
- **Option button** – Quit
