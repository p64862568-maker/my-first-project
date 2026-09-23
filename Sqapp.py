from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)

# Простой HTML-шаблон со стилями прямо внутри кода (чтобы не создавать лишних папок)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Мои Заметки</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        form { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
        input, textarea { padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        textarea { resize: vertical; height: 80px; }
        button { background: #007bff; color: white; border: none; padding: 10px; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        .note-card { background: #f8f9fa; border: 1px solid #e9ecef; padding: 15px; border-radius: 6px; margin-bottom: 10px; position: relative; }
        .note-title { font-weight: bold; font-size: 18px; margin-bottom: 5px; color: #222; }
        .note-content { color: #555; white-space: pre-wrap; }
        .actions { margin-top: 10px; display: flex; gap: 10px; }
        .btn-delete { background: #dc3545; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 12px; }
        .btn-delete:hover { background: #bd2130; }
        .btn-edit { background: #ffc107; color: #212529; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 12px; }
        .btn-edit:hover { background: #e0a800; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 Сервис заметок</h1>
        
        <!-- Форма для добавления или редактирования -->
        <form action="{{ url_for('save_note') }}" method="POST">
            <input type="hidden" name="note_id" value="{{ edit_note.id if edit_note else '' }}">
            <input type="text" name="title" placeholder="Заголовок заметки" value="{{ edit_note.title if edit_note else '' }}" required>
            <textarea name="content" placeholder="Текст заметки..." required>{{ edit_note.content if edit_note else '' }}</textarea>
            <button type="submit">{{ 'Сохранить изменения' if edit_note else 'Добавить заметку' }}</button>
            {% if edit_note %}
                <a href="{{ url_for('index') }}" style="text-align:center; color:#6c757d; font-size:14px; text-decoration:none;">Отмена</a>
            {% endif %}
        </form>

        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">

        <!-- Список заметок -->
        <h2>Ваши записи:</h2>
        {% if not notes %}
            <p style="color: #888; text-align: center;">Заметок пока нет. Добавьте первую!</p>
        {% endif %}
        {% for note in notes %}
            <div class="note-card">
                <div class="note-title">{{ note.title }}</div>
                <div class="note-content">{{ note.content }}</div>
                <div class="actions">
                    <a href="{{ url_for('index', edit=note.id) }}" class="btn-edit">Редактировать</a>
                    <a href="{{ url_for('delete_note_ui', note_id=note.id) }}" class="btn-delete">Удалить</a>
                </div>
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

# Главная страница (Показ всех заметок + режим редактирования)
@app.route("/", methods=["GET"])
def index():
    notes = Note.query.order_by(Note.id.desc()).all()
    edit_id = request.args.get("edit")
    edit_note = Note.query.get(edit_id) if edit_id else None
    return render_template_string(HTML_TEMPLATE, notes=notes, edit_note=edit_note)

# Обработчик формы: создание (INSERT) или обновление (UPDATE)
@app.route("/ui/save", methods=["POST"])
def save_note():
    note_id = request.form.get("note_id")
    title = request.form.get("title")
    content = request.form.get("content")
    
    if note_id: # Если ID есть — это РЕДАКТИРОВАНИЕ
        note = Note.query.get(note_id)
        if note:
            note.title = title
            note.content = content
    else: # Если ID пустого — это СОЗДАНИЕ
        new_note = Note(title=title, content=content)
        db.session.add(new_note)
        
    db.session.commit()
    return redirect(url_for("index"))

# Обработчик кнопки: удаление (DELETE)
@app.route("/ui/delete/<int:note_id>", methods=["GET"])
def delete_note_ui(note_id):
    note = Note.query.get(note_id)
    if note:
        db.session.delete(note)
        db.session.commit()
    return redirect(url_for("index"))

# Старые API-методы (для проверки преподом через тесты/Postman)
@app.route("/notes", methods=["GET"])
def get_notes():
    notes = Note.query.all()
    return jsonify([{"id": n.id, "title": n.title, "content": n.content} for n in notes])

@app.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json() or {}
    new_note = Note(title=data.get("title", "Untitled"), content=data.get("content", ""))
    db.session.add(new_note)
    db.session.commit()
    return jsonify({"status": "created"}), 201

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=10000)

