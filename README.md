# Mouse Pad UI

A touch-friendly browser control panel that publishes MQTT mouse commands, plus a small Python receiver that turns those commands into PC mouse movement, clicks, and scrolling.

## Files

- `mouse_pad_ui.html` - mobile/desktop touch UI for sending MQTT commands.
- `rotary_PC.py` - Python MQTT receiver for controlling the local mouse.
- `mouse_pad_config.js` - shared MQTT settings for both the UI and receiver.

## Run the Receiver

Create a local virtual environment and install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start the receiver:

```bash
.\.venv\Scripts\python.exe rotary_PC.py
```

Then open `mouse_pad_ui.html` in a browser and use the touch controls.

## Controls

The UI is split into two fullscreen landscape pages:

- Settings page: MQTT broker, topic, movement speed, send interval, scroll speed, connect, and disconnect.
- Control page: touch pad, left/right click, page up/down, scroll wheel, window controls, and browser tab controls.

The extra control buttons send keyboard shortcuts from the receiver PC:

- Close window: `Alt+F4`
- Maximize window: `Win+Up`
- Minimize window: `Win+Down`
- Switch tab: `Ctrl+Tab`
- Previous tab: `Ctrl+Shift+Tab`
- Close tab: `Ctrl+W`
- Reload: `Ctrl+R`
- New tab: `Ctrl+T`

## Build the EXE

Regenerate the Windows receiver executable:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_rotary_exe.ps1
```

The output is written to `dist\rotary_PC.exe`.

## MQTT

Edit `mouse_pad_config.js` to make the browser UI and Python receiver use the same MQTT settings:

```js
window.MOUSE_PAD_CONFIG = {
  "mqtt": {
    "broker": "broker.emqx.io",
    "port": 1883,
    "websocketUrl": "wss://broker.emqx.io:8084/mqtt",
    "topic": "JJ/mouse/pad/cmd"
  }
};
```

The Python receiver reads `broker`, `port`, and `topic`. The browser UI reads `websocketUrl` and `topic`.

You can still temporarily override the browser values with URL parameters, for example `mouse_pad_ui.html?topic=your/topic`.
