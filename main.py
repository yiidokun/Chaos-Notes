from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os, re

app = Flask(__name__)
socketio = SocketIO(app)

NOTES_FILE = "messages.txt"

def load_notes():
    notes = []
    if not os.path.exists(NOTES_FILE):
        return notes

    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "|" in line:
                nid, text = line.split("|", 1)
                real_text = text.replace("\\n", "\n")
                notes.append({"id": nid, "text": real_text})
    return notes

def save_notes(notes):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        for n in notes:
            flat_text = n['text'].replace("\n", "\\n")
            f.write(f"{n['id']}|{flat_text}\n")

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("add_note")
def on_add(note_text):
    note_text = note_text.strip()
    # Check if the < and > characters are present in the text
    if not re.search(r'<[^>]+>', note_text):
        note_text = note_text.replace("\n", "<br/>")
    if not note_text:
        return

    notes = load_notes()

    new_id = str(max([int(n["id"]) for n in notes], default=0) + 1)

    new_note = {"id": new_id, "text": note_text}
    notes.append(new_note)
    save_notes(notes)

    emit("note_added", new_note, broadcast=True)

@socketio.on("delete_note")
def on_delete(note_id):
    notes = load_notes()
    notes = [n for n in notes if n["id"] != note_id]
    save_notes(notes)

    emit("note_deleted", note_id, broadcast=True)

@socketio.on("request_notes")
def on_request_notes():
    notes = load_notes()
    for note in notes:
        emit("note_added", note)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
