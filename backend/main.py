import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PLAYLIST_FILE = os.path.join(os.path.dirname(__file__), "playlist.json")
EXPECTED_KEYS = {"music_name", "artist", "floor", "num_of_likes"}


def _load_playlist():
    if not os.path.exists(PLAYLIST_FILE):
        return []
    with open(PLAYLIST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_playlist(data):
    with open(PLAYLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/songs", methods=["GET"])
def get_songs():
    return jsonify(_load_playlist()), 200


@app.route("/songs", methods=["POST"])
def add_song():
    song = request.json or {}
    if not EXPECTED_KEYS.issubset(song.keys()):
        return jsonify({"error": f"Required keys: {EXPECTED_KEYS}"}), 400

    playlist = _load_playlist()
    if any(s["music_name"] == song["music_name"] for s in playlist):
        return jsonify({"error": "music_name já existe"}), 409

    new_song = {k: str(song[k]).strip() for k in EXPECTED_KEYS}
    playlist.append(new_song)
    _save_playlist(playlist)
    return jsonify(new_song), 201


@app.route("/songs/<music_name>", methods=["PUT"])
def update_song(music_name):
    updates = request.json or {}
    if not updates:
        return jsonify({"error": "Nenhuma atualização fornecida"}), 400

    if not EXPECTED_KEYS.intersection(updates.keys()):
        return jsonify({"error": f"Pelo menos uma das chaves: {EXPECTED_KEYS}"}), 400

    playlist = _load_playlist()
    for song in playlist:
        if song.get("music_name") == music_name:
            for k in EXPECTED_KEYS:
                if k in updates:
                    song[k] = str(updates[k]).strip()
            _save_playlist(playlist)
            return jsonify(song), 200

    return jsonify({"error": "Música não encontrada"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)

