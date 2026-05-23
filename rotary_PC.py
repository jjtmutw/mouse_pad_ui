# pip install paho-mqtt pyautogui

import json
import re
import sys
from pathlib import Path

import pyautogui
import paho.mqtt.client as mqtt

DEFAULT_CONFIG = {
    "mqtt": {
        "broker": "broker.emqx.io",
        "port": 1883,
        "topic": "JJ/mouse/pad/cmd",
    }
}
CONFIG_FILE = "mouse_pad_config.js"
EDGE_PADDING = 4

pyautogui.FAILSAFE = True

def app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

def read_config_file(path):
    raw = path.read_text(encoding="utf-8")
    match = re.search(r"window\.MOUSE_PAD_CONFIG\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S)
    if not match:
        return json.loads(raw)
    return json.loads(match.group(1))

def load_config():
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    search_dirs = []
    for path in [app_dir(), app_dir().parent, Path.cwd()]:
        if path not in search_dirs:
            search_dirs.append(path)
    config_path = next((path / CONFIG_FILE for path in search_dirs if (path / CONFIG_FILE).exists()), search_dirs[0] / CONFIG_FILE)

    if config_path.exists():
        try:
            loaded = read_config_file(config_path)
            config["mqtt"].update(loaded.get("mqtt", loaded))
            print("Loaded config:", config_path)
        except Exception as error:
            print(f"Config load failed ({config_path}): {error}")
            print("Using default MQTT settings.")
    else:
        print("Config not found, using defaults:", config_path)

    return config

CONFIG = load_config()
MQTT_CONFIG = CONFIG["mqtt"]
BROKER = str(MQTT_CONFIG.get("broker") or DEFAULT_CONFIG["mqtt"]["broker"])
PORT = int(MQTT_CONFIG.get("port") or DEFAULT_CONFIG["mqtt"]["port"])
TOPIC = str(MQTT_CONFIG.get("topic") or DEFAULT_CONFIG["mqtt"]["topic"])
HOTKEYS = {
    "window_close": ("alt", "f4"),
    "window_maximize": ("win", "up"),
    "window_minimize": ("win", "down"),
    "tab_switch": ("ctrl", "tab"),
    "tab_prev": ("ctrl", "shift", "tab"),
    "tab_close": ("ctrl", "w"),
    "reload": ("ctrl", "r"),
    "tab_new": ("ctrl", "t"),
}

def limit(v, min_v=-800, max_v=800):
    return max(min_v, min(max_v, int(v)))

def safe_mouse_move(dx, dy):
    width, height = pyautogui.size()
    x, y = pyautogui.position()
    target_x = limit(x + dx, EDGE_PADDING, width - EDGE_PADDING - 1)
    target_y = limit(y + dy, EDGE_PADDING, height - EDGE_PADDING - 1)

    # Move away from fail-safe corners without leaving the receiver process.
    original_failsafe = pyautogui.FAILSAFE
    pyautogui.FAILSAFE = False
    try:
        pyautogui.moveTo(target_x, target_y, duration=0)
    finally:
        pyautogui.FAILSAFE = original_failsafe

def safe_action(action):
    try:
        action()
    except pyautogui.FailSafeException:
        print("PyAutoGUI fail-safe touched. Move the pointer away from the corner or use the touch pad again.")

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("MQTT connected:", reason_code)
    client.subscribe(TOPIC)
    print("Subscribed:", TOPIC)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))
    except Exception:
        return

    if data.get("target") != "pc_mouse":
        return

    cmd_type = data.get("type")

    if cmd_type == "move":
        dx = limit(data.get("dx", 0))
        dy = limit(data.get("dy", 0))
        safe_action(lambda: safe_mouse_move(dx, dy))

    elif cmd_type == "click":
        button = data.get("button", "left")
        if button in ["left", "right", "middle"]:
            safe_action(lambda: pyautogui.click(button=button))

    elif cmd_type == "scroll":
        dy = limit(data.get("dy", 0), -400, 400)
        safe_action(lambda: pyautogui.scroll(dy))

    elif cmd_type == "page":
        direction = data.get("direction")
        if direction == "up":
            safe_action(lambda: pyautogui.press("pageup"))
        elif direction == "down":
            safe_action(lambda: pyautogui.press("pagedown"))

    elif cmd_type == "hotkey":
        action = data.get("action")
        keys = HOTKEYS.get(action)
        if keys:
            safe_action(lambda: pyautogui.hotkey(*keys))

    elif cmd_type == "stop":
        pass

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="JJ_PC_Mouse_Receiver"
)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
