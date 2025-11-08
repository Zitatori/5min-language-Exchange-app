from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3
from uuid import uuid4
from datetime import datetime, timedelta

DB_PATH = "five_min_talk.db"

app = FastAPI()

# ===== DB =====
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            speak_langs TEXT,
            learn_lang TEXT,
            points INTEGER DEFAULT 5,
            online INTEGER DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS blocked_pairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT NOT NULL,
            student_id INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            active INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()

@app.on_event("startup")
def on_startup():
    init_db()

# ===== 共通 =====
def get_current_user_id(request: Request):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    try:
        return int(user_id)
    except ValueError:
        return None

def html_head(title="5min Talk"):
    return f"""
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    </head>
    """

# ===== ページ =====
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user_id = get_current_user_id(request)
    if user_id:
        return RedirectResponse("/dashboard")
    html = f"""
    <html>
    {html_head("5min Talk")}
    <body class="bg-light">
        <div class="container py-5">
            <div class="card shadow p-4 mx-auto" style="max-width:600px;">
                <h1 class="text-center mb-3 text-primary">🗣️ 5min Talk</h1>
                <p class="text-center text-muted">
                    5分だけビデオ通話で言語練習。<br>
                    出会いなし・安心・ライト。
                </p>
                <div class="text-center mt-4">
                    <a href="/register" class="btn btn-primary btn-lg">はじめる</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html)

@app.get("/register", response_class=HTMLResponse)
async def register_form():
    html = f"""
    <html>
    {html_head("登録")}
    <body class="bg-light">
        <div class="container py-5">
            <div class="card shadow p-4 mx-auto" style="max-width:600px;">
                <h2 class="text-center mb-4">ユーザー登録</h2>
                <form action="/register" method="post" id="regForm">
                    <div class="mb-3">
                        <label class="form-label">名前</label>
                        <input type="text" class="form-control" name="name" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">ロール</label>
                        <select name="role" id="role" class="form-select" onchange="toggleLanguageSelectors()">
                            <option value="student">生徒</option>
                            <option value="teacher">先生</option>
                        </select>
                    </div>

                    <!-- 先生用: 複数選択 -->
                    <div id="teacherLangs" class="mb-3" style="display:none;">
                        <label class="form-label">話せる言語（複数選択可）</label><br>
                        <div class="btn-group w-100" role="group">
                            <input type="checkbox" class="btn-check" id="teach_jp" name="speak_langs" value="ja">
                            <label class="btn btn-outline-primary" for="teach_jp">🇯🇵 日本語</label>

                            <input type="checkbox" class="btn-check" id="teach_en" name="speak_langs" value="en">
                            <label class="btn btn-outline-primary" for="teach_en">🇬🇧 英語</label>

                            <input type="checkbox" class="btn-check" id="teach_es" name="speak_langs" value="es">
                            <label class="btn btn-outline-primary" for="teach_es">🇪🇸 スペイン語</label>

                            <input type="checkbox" class="btn-check" id="teach_fr" name="speak_langs" value="fr">
                            <label class="btn btn-outline-primary" for="teach_fr">🇫🇷 フランス語</label>
                        </div>
                    </div>

                    <!-- 生徒用: 単一選択 -->
                    <div id="studentLang" class="mb-3">
                        <label class="form-label">学びたい言語</label><br>
                        <div class="btn-group w-100" role="group">
                            <input type="radio" class="btn-check" id="learn_jp" name="learn_lang" value="ja" required>
                            <label class="btn btn-outline-success" for="learn_jp">🇯🇵 日本語</label>

                            <input type="radio" class="btn-check" id="learn_en" name="learn_lang" value="en">
                            <label class="btn btn-outline-success" for="learn_en">🇬🇧 英語</label>

                            <input type="radio" class="btn-check" id="learn_es" name="learn_lang" value="es">
                            <label class="btn btn-outline-success" for="learn_es">🇪🇸 スペイン語</label>

                            <input type="radio" class="btn-check" id="learn_fr" name="learn_lang" value="fr">
                            <label class="btn btn-outline-success" for="learn_fr">🇫🇷 フランス語</label>
                        </div>
                    </div>

                    <div class="text-center mt-4">
                        <button type="submit" class="btn btn-success btn-lg">登録</button>
                    </div>
                </form>
            </div>
        </div>

        <script>
        function toggleLanguageSelectors() {{
            const role = document.getElementById('role').value;
            document.getElementById('teacherLangs').style.display = role === 'teacher' ? 'block' : 'none';
            document.getElementById('studentLang').style.display = role === 'student' ? 'block' : 'none';
        }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html)

@app.post("/register")
async def register(request: Request):
    form = await request.form()
    name = form.get("name")
    role = form.get("role")
    speak_langs = ",".join(form.getlist("speak_langs")) if role == "teacher" else ""
    learn_lang = form.get("learn_lang", "")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, role, speak_langs, learn_lang) VALUES (?, ?, ?, ?)",
                (name, role, speak_langs.strip(), learn_lang.strip()))
    user_id = cur.lastrowid
    conn.commit()
    conn.close()

    resp = RedirectResponse("/dashboard", status_code=302)
    resp.set_cookie("user_id", str(user_id))
    return resp

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user_id = get_current_user_id(request)
    if not user_id:
        return RedirectResponse("/")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()

    if not user:
        resp = RedirectResponse("/register", status_code=302)
        resp.delete_cookie("user_id")
        return resp

    if user["role"] == "teacher":
        body = f"""
        <h2 class="text-center mb-3 text-primary">先生ダッシュボード</h2>
        <p class="text-center">ようこそ <b>{user['name']}</b> さん</p>
        <p class="text-center text-muted">話せる言語: {user['speak_langs']}</p>
        <div class="text-center">
            <a href="/room/{uuid4().hex}?as=teacher" class="btn btn-success btn-lg mt-3">ルームを開く（仮）</a>
        </div>
        """
    else:
        body = f"""
        <h2 class="text-center mb-3 text-primary">生徒ダッシュボード</h2>
        <p class="text-center">こんにちは <b>{user['name']}</b> さん</p>
        <p class="text-center text-muted">学びたい言語: {user['learn_lang'] or '(未設定)'} / 残ポイント: {user['points']}</p>
        <div class="text-center">
            <a href="/room/{uuid4().hex}?as=student" class="btn btn-primary btn-lg mt-3">5分トークを開始</a>
        </div>
        """

    html = f"""
    <html>
    {html_head("Dashboard")}
    <body class="bg-light">
        <div class="container py-5">
            <div class="card shadow p-4 mx-auto" style="max-width:600px;">
                {body}
                <div class="text-center mt-4">
                    <a href="/logout" class="btn btn-outline-danger">ログアウト</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html)

@app.get("/logout")
async def logout():
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie("user_id")
    return resp

@app.get("/room/{room_id}", response_class=HTMLResponse)
async def room_page(request: Request, room_id: str):
    role = request.query_params.get("as", "student")
    html = f"""
    <html>
    {html_head("5分トークルーム")}
    <body class="bg-light">
        <div class="container py-5">
            <div class="card shadow-lg p-4 mx-auto" style="max-width:800px;">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h3 class="text-primary mb-0">🗣️ 5分トークルーム</h3>
                    <span class="badge bg-secondary text-uppercase">{role}</span>
                </div>

                <div class="row">
                    <div class="col-md-6 text-center">
                        <div class="border rounded bg-dark text-white d-flex align-items-center justify-content-center" style="height:240px;">
                            <span class="text-muted">あなたのカメラ（仮）</span>
                        </div>
                    </div>
                    <div class="col-md-6 text-center">
                        <div class="border rounded bg-dark text-white d-flex align-items-center justify-content-center" style="height:240px;">
                            <span class="text-muted">相手の映像（仮）</span>
                        </div>
                    </div>
                </div>

                <div class="text-center mt-4">
                    <h5 class="mb-3">⏱️ 残り時間</h5>
                    <div id="timer" class="display-5 fw-bold text-danger">05:00</div>
                    <button class="btn btn-danger btn-lg mt-4" onclick="leaveRoom()">退出</button>
                </div>
            </div>
        </div>

        <script>
        let remaining = 5 * 60;
        const timerEl = document.getElementById("timer");
        const countdown = setInterval(() => {{
            remaining -= 1;
            if (remaining <= 0) {{
                clearInterval(countdown);
                timerEl.textContent = "終了";
                timerEl.classList.remove("text-danger");
                timerEl.classList.add("text-muted");
            }} else {{
                const m = String(Math.floor(remaining / 60)).padStart(2, '0');
                const s = String(remaining % 60).padStart(2, '0');
                timerEl.textContent = `${{m}}:${{s}}`;
            }}
        }}, 1000);

        function leaveRoom() {{
            window.location.href = '/dashboard';
        }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html)
