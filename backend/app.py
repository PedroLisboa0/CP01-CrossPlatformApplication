import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PLAYLIST_FILE = os.path.join(os.path.dirname(__file__), "playlist.json")
EXPECTED_KEYS = {"name", "artist", "floor"}


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
    floor = request.args.get("floor", "all") # 'Floor' vem com parametro do GET, caso não venha, a resposta vai ser a playlist com todos os andares.
    playlist = _load_playlist()
    if floor == "all":
        return jsonify(playlist), 200
    else:
        response = {"songs":[]}
        for song in playlist["songs"]:
            if song["floor"] == int(floor):
                response["songs"].append(song)
        return jsonify(response), 200


@app.route("/songs/add_song", methods=["POST"])
def add_song():
    song = request.json or {}
    if not EXPECTED_KEYS.issubset(song.keys()):
        return jsonify({"error": f"Required keys: {EXPECTED_KEYS}"}), 400

    playlist = _load_playlist()

    new_song = {k: song[k] for k in EXPECTED_KEYS}
    new_song["likes"] = 0
    playlist["songs"].append(new_song)
    _save_playlist(playlist)
    return jsonify(new_song), 201


@app.route("/songs/like", methods=["PUT"])
def like_song():
    name = request.args.get("name", False) # 'Name' vem como parametro do request.
    if not name:
        return jsonify({"error": "Nenhuma música fornecida"}), 400
    
    playlist = _load_playlist()
    for song in playlist["songs"]:
        if song["name"] == name:
            song["likes"] += 1
            _save_playlist(playlist)
            return jsonify(song), 200

    return jsonify({"error": "Música não encontrada"}), 404


@app.route("/songs/restart", methods=["DELETE"])
def restart_playlist():
    floor = request.args.get("floor", "all")
    playlist = _load_playlist()
    if floor == "all":
        playlist["songs"] = []
        _save_playlist(playlist)
        return jsonify(playlist), 200
    else:
        songs_to_delete = []
        for index, song in enumerate(playlist["songs"]):
            if song["floor"] == int(floor):
                songs_to_delete.append(index)
        songs_to_delete = set(songs_to_delete)
        playlist["songs"] = [value for index, value in enumerate(playlist["songs"]) if index not in songs_to_delete]
        _save_playlist(playlist)
        return jsonify(playlist), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)

