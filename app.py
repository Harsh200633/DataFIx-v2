from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename
from datetime import datetime
import os, time, sqlite3

from database import init_db, save_to_sql
from processor import DataProcessor

app = Flask(__name__)
app.secret_key = "datafix_creator_key_2026"

UPLOAD_FOLDER = 'static/uploads'
PLOT_FOLDER = 'static/plots'
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PLOT_FOLDER, exist_ok=True)

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    user = session.get('user')

    if request.method == 'POST' and user:
        file = request.files.get('dataset')

        if not file or file.filename == '':
            return "<h3>No file selected</h3><a href='/'>Back</a>"

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            file.save(filepath)

            dp = DataProcessor(filepath)
            df = dp.clean_data()
            dp.save_all_visuals(PLOT_FOLDER)

            save_to_sql(df)

            cleaned_path = os.path.join(UPLOAD_FOLDER, 'cleaned.csv')
            df.to_csv(cleaned_path, index=False)

            stats_html = df.describe().to_html(classes='data-table')

            return render_template(
                'head.html',
                logged_in=True,
                cleaned=True,
                stats=stats_html,
                timestamp=time.time()
            )

        except Exception as e:
            return f"<h1>Error: {str(e)}</h1><a href='/'>Back</a>"

    return render_template('head.html', logged_in=bool(user))

@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('u')
    p = request.form.get('p')
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute("SELECT pw FROM users WHERE id=?", (u,))
    user_record = c.fetchone()

    if user_record:
        if user_record[0] == p:
            session['user'] = u
            c.execute("UPDATE users SET login_time=? WHERE id=?", (now, u))
        else:
            return "<h3>Wrong Password</h3><a href='/'>Back</a>"
    else:
        c.execute("INSERT INTO users (id, pw, login_time) VALUES (?, ?, ?)", (u, p, now))
        session['user'] = u

    conn.commit()
    conn.close()

    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.errorhandler(413)
def too_large(e):
    return "<h3>File too large (Max 20MB)</h3><a href='/'>Back</a>"


if __name__ == '__main__':
    app.run(debug=True)
