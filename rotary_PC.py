# pip install paho-mqtt pyautogui

import json
import pyautogui
import paho.mqtt.client as mqtt

BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "JJ/mouse/pad/cmd"
EDGE_PADDING = 4

pyautogui.FAILSAFE = True

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
