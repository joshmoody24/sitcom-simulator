from flask import Flask, request, redirect, jsonify, send_file
from flask_cors import CORS
import sqlite3
import os
import re

app = Flask(__name__)
CORS(app)
@app.route('/api/submit-prompt', methods=['POST'])
def submit_prompt():
    # handle the POST request
    if(request.method == 'POST'):
        print("here")
        prompt = request.form.get('prompt')
        style = request.form.get('style')
        print(request)
        print("form",request.form)
        conn = sqlite3.connect("sitcomcli.sqlite3", timeout=10)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Videos (Prompt, Style) VALUES (?, ?)", [prompt, style])
        conn.commit()
        conn.close()
        return "success"

@app.route('/api/sitcom-queue', methods=["GET"])
def sitcom_queue():
    conn = sqlite3.connect("sitcomcli.sqlite3", timeout=10)
    cursor = conn.cursor()
    enqueued = cursor.execute("SELECT QueueId, Prompt, Style FROM Videos WHERE Finished = 0").fetchall()
    sitcoms = []
    for row in enqueued:
        sitcoms.append({
            'id': row[0],
            'prompt': row[1],
            'style': row[2]
        })
    return jsonify(sitcoms)

@app.route('/api/video-list', methods=["GET"])
def video_list():
    conn = sqlite3.connect("sitcomcli.sqlite3", timeout=10)
    cursor = conn.cursor()
    videos = []
    query = cursor.execute("SELECT QueueId, Prompt, Style FROM Videos WHERE Finished = 1").fetchall()
    for row in query:
        description_path = os.path.abspath(os.path.join(f"renders/{row[1]}", "description.txt"))
        lines = []
        with open(description_path) as f:
            lines = f.readlines()
        videos.append({
            'id': row[0],
            'prompt': row[1],
            'style': row[2],
            'description': '\n'.join(lines),
            'thumbnail': f'/thumbnail/{row[1]}'
        })
    conn.close()
    return jsonify(videos)


@app.route("/api/video/<title>", methods=["GET"])
def video(title):
    video_path = os.path.abspath(os.path.join(f"renders/{title}", f"{title}.mp4"))
    size = os.stat(video_path)
    size = size.st_size

    headers = {
        "Content-Type": "video/mp4",
    }

    return send_file(video_path)

@app.route("/api/thumbnail/<title>", methods=["GET"])
def thumbnail(title):
    print("hmmm")
    video_path = os.path.abspath(os.path.join(f"renders/{title}", f"thumbnail.png"))
    size = os.stat(video_path)
    size = size.st_size

    headers = {
        "Content-Type": "video/mp4",
    }

    return send_file(video_path)
#    return current_app.response_class(get_chunk(video_path, start, end), 206, headers)

@app.route('/api/character-list', methods=["GET"])
def characters():
    conn = sqlite3.connect("sitcomcli.sqlite3", timeout=10)
    cursor = conn.cursor()
    query = cursor.execute("SELECT FullName FROM Characters").fetchall()
    chars = [row[0] for row in query]
    return jsonify(chars)


app.run(debug = True)