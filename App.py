from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/notes", methods=["GET"])
def get_notes():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content FROM notes")
    rows = cursor.fetchall()
    conn.close()
    
    notes_list = []
    for row in rows:
        notes_list.append({"id": row[0], "title": row[1], "content": row[2]})
    return jsonify(notes_list)

@app.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Note created"}), 201

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
