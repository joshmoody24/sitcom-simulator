from flask import Flask, request, redirect, jsonify, send_file
from flask_cors import CORS
import sqlite3
import os
import re

app = Flask(__name__)
CORS(app)
@app.route('/submit-prompt', methods=['POST'])
def submit_prompt():
    # handle the POST request
    if(request.method == 'POST'):
        print("here")
        prompt = request.form.get('prompt')
        print(request)
        print("form",request.form)
        conn = sqlite3.connect("sitcomcli.sqlite3", timeout=10)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Videos (Prompt) VALUES (?)", [prompt])
        conn.commit()
        conn.close()
        return "success"

@app.route('/sitcom-queue', methods=["GET"])
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

@app.route('/video-list', methods=["GET"])
def video_list():
    conn = sqlite3.connect("sitcomcli.sqlite3", timeout=10)
    cursor = conn.cursor()
    videos = []
    query = cursor.execute("SELECT QueueId, Prompt, Style FROM Videos WHERE Finished = 1").fetchall()
    for row in query:
        videos.append({
            'id': row[0],
            'prompt': row[1],
            'style': row[2]
        })
    conn.close()
    return jsonify(videos)


@app.route("/video/<title>", methods=["GET"])
def video(title):
    video_path = os.path.abspath(os.path.join("renders", f"{title}.mp4"))
    size = os.stat(video_path)
    size = size.st_size

    headers = {
        "Content-Type": "video/mp4",
    }

    return send_file(video_path)
#    return current_app.response_class(get_chunk(video_path, start, end), 206, headers)


app.run(debug = True)