from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import sqlite3
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id TEXT,
            filename TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        
        if file:
            unique_id = str(uuid.uuid4())
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_id)

            file.save(filepath)

            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO files VALUES (?,?)",(unique_id,file.filename))
            conn.commit()
            conn.close()

            return f"File uploaded! Share link: http://127.0.0.1:5000/file/{unique_id}"

    return render_template('upload.html')

@app.route('/file/<id>')
def file(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT filename FROM files WHERE id=?",(id,))
    result = c.fetchone()
    conn.close()

    if result:
        return send_from_directory(app.config['UPLOAD_FOLDER'], id, as_attachment=True, download_name=result[0])

    return "File not found"

if __name__ == '__main__':
    app.run(debug=True)
