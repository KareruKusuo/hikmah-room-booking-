from flask import Flask, request, send_from_directory
from datetime import datetime
import threading, time

app = Flask(__name__, static_folder='public', static_url_path='')

room_state = {
    "state": "AVAILABLE",
    "current_user": None,
    "booking_start": None,
    "last_presence": None,
    "queue": [] 
}

GRACE_PERIOD_SEC = 60
INACTIVITY_LIMIT_SEC = 60

@app.route('/')
def serve_index():
    return send_from_directory('public', 'index.html')

@app.route("/status")
def status():
    now = datetime.now()
    remaining = 0
    if room_state["state"] == "AWAITING_CHECKIN" and room_state["booking_start"]:
        elapsed = (now - room_state["booking_start"]).total_seconds()
        remaining = max(0, GRACE_PERIOD_SEC - elapsed)
    elif room_state["state"] == "IN_USE" and room_state["last_presence"]:
        elapsed = (now - room_state["last_presence"]).total_seconds()
        remaining = max(0, INACTIVITY_LIMIT_SEC - elapsed)
    return {"1": {**room_state, "remaining": int(remaining)}}

@app.route("/rfid_scan", methods=["POST"])
def rfid_scan():
    data = request.json
    card_id = data.get("card_id")
    now = datetime.now()

    if room_state["state"] == "AVAILABLE":
        room_state.update({"state": "AWAITING_CHECKIN", "current_user": card_id, "booking_start": now})
        return {"status": "BOOKED", "result": "Booked."}

    elif card_id == room_state["current_user"]:
        if room_state["state"] == "AWAITING_CHECKIN":
            room_state.update({"state": "IN_USE", "last_presence": now})
            return {"status": "SUCCESS", "result": "Checked-in."}
        else:
            process_room_release()
            return {"status": "RELEASED", "result": "Checked-out."}
    
    # Restoring Queue Logic
    else:
        if card_id not in room_state["queue"]:
            room_state["queue"].append(card_id)
            return {"status": "QUEUED", "result": "Added to queue."}
        return {"status": "ALREADY_QUEUED"}

@app.route("/sensor/presence/1", methods=["POST"])
def sensor_presence():
    room_state["last_presence"] = datetime.now()
    if room_state["state"] == "AWAITING_CHECKIN":
        room_state["state"] = "IN_USE"
    return {"state": room_state["state"]}

@app.route("/release/1", methods=["POST"])
def release_manual():
    process_room_release()
    return {"status": "RELEASED"}

@app.route("/reset/1", methods=["POST"])
def reset_manual():
    room_state.update({"state": "AVAILABLE", "current_user": None, "booking_start": None, "last_presence": None, "queue": []})
    return {"status": "RESET"}

def process_room_release():
    if room_state["queue"]:
        next_user = room_state["queue"].pop(0)
        room_state.update({"state": "AWAITING_CHECKIN", "current_user": next_user, "booking_start": datetime.now(), "last_presence": None})
    else:
        room_state.update({"state": "AVAILABLE", "current_user": None, "booking_start": None, "last_presence": None})

def logic_loop():
    while True:
        now = datetime.now()
        if room_state["state"] == "AWAITING_CHECKIN" and room_state["booking_start"]:
            if (now - room_state["booking_start"]).total_seconds() >= GRACE_PERIOD_SEC:
                process_room_release()
        elif room_state["state"] == "IN_USE" and room_state["last_presence"]:
            if (now - room_state["last_presence"]).total_seconds() >= INACTIVITY_LIMIT_SEC:
                process_room_release()
        time.sleep(1)

threading.Thread(target=logic_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)