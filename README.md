# MQTT Rotary Touch UI

A touch-friendly browser control panel that publishes MQTT mouse commands, plus a small Python receiver that turns those commands into PC mouse movement, clicks, and scrolling.

## Files

- `rotary_knob_touch_ui.html` - mobile/desktop touch UI for sending MQTT commands.
- `rotary_PC.py` - Python MQTT receiver for controlling the local mouse.

## Run the Receiver

Install dependencies:

```bash
pip install paho-mqtt pyautogui
```

Start the receiver:

```bash
python rotary_PC.py
```

Then open `rotary_knob_touch_ui.html` in a browser and use the touch controls.

## MQTT

Default broker:

```text
broker.emqx.io:1883
```

Default topic:

```text
JJ/mouse/pad/cmd
```
