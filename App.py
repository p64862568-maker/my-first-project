from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Простая база данных прямо в файле, чтобы Render не ругался на отсутствие Postgres
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    notes = db.relationship('Note', backref='category', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

@app.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json() or {}
    new_note = Note(
        title=data.get("title", "Untitled"),
        content=data.get("content", ""),
        category_id=data.get("category_id")
    )
    db.session.add(new_note)
    db.session.commit()
    return jsonify({"status": "created"}), 201

@app.route("/notes", methods=["GET"])
def get_notes():
    cat_id = request.args.get("category_id")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    
    query = db.session.query(Note).outerjoin(Category)
    if cat_id:
        query = query.filter(Note.category_id == cat_id)
        
    paginated_query = query.paginate(page=page, per_page=per_page, error_out=False)
    
    notes_list = []
    for note in paginated_query.items:
        cat_name = note.category.name if note.category else "No category"
        notes_list.append({
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "category": cat_name
        })
    return jsonify(notes_list)

@app.route("/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.get_json() or {}
    note = Note.query.get(note_id)
    if not note:
        return jsonify({"error": "Not found"}), 404
    note.title = data.get("title", note.title)
    note.content = data.get("content", note.content)
    db.session.commit()
    return jsonify({"status": "updated"})

@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    note = Note.query.get(note_id)
    if not note:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(note)
    db.session.commit()
    return jsonify({"status": "deleted"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
