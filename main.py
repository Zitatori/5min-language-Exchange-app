from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# --- FastAPI setup ---
app = FastAPI()

# --- Static folder for images ---
app.mount("/image", StaticFiles(directory="image"), name="image")

LANGUAGES = ["Japanese", "English", "Spanish", "French"]


# =======================
#   DASHBOARD
# =======================
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(role: str = None):
    languages_html = "".join(
        [
            f"""
            <button onclick="selectLanguage('{lang}')"
                class='px-4 py-2 rounded-xl border border-indigo-400 text-indigo-600
                       hover:bg-indigo-50 active:scale-95 transition w-full mb-2'>
                {lang}
            </button>
            """
            for lang in LANGUAGES
        ]
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>5min Talk</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>

    <body class="bg-gradient-to-b from-indigo-100 to-white min-h-screen flex items-center justify-center px-6">

        <div class="bg-white shadow-xl rounded-3xl p-8 w-full max-w-sm text-center border border-indigo-50">

            <h1 class="text-3xl font-bold text-indigo-600 mb-6">🗣️ 5min Talk</h1>

            <div class="space-y-4">
                <a href="/dashboard?role=student"
                    class="block w-full bg-indigo-500 text-white py-3 rounded-xl hover:bg-indigo-600 active:scale-95 transition">
                    🎓 I'm a Student
                </a>

                <a href="/dashboard?role=teacher"
                    class="block w-full border border-indigo-500 text-indigo-500 py-3 rounded-xl hover:bg-indigo-50 active:scale-95 transition">
                    👩‍🏫 I'm a Teacher
                </a>
            </div>

        </div>

        <script>
        const urlParams = new URLSearchParams(window.location.search);
        const role = urlParams.get("role");

        if (role === "student" || role === "teacher") {{
            document.body.innerHTML = `
            <div class='bg-white shadow-xl rounded-3xl p-8 w-full max-w-sm text-center border border-indigo-50 mt-6 mx-auto'>
                <h2 class='text-2xl font-bold text-indigo-600 mb-1'>Choose Language</h2>
                <p class='text-gray-500 mb-4 text-sm'>${{role === "student" ? "Pick 1 language" : "Choose all you can teach"}}</p>

                <div id='langButtons' class='space-y-2'>
                    {languages_html}
                </div>

                <button id='startBtn'
                    onclick="goRoom()"
                    class='mt-4 w-full bg-indigo-500 text-white py-3 rounded-xl opacity-50 cursor-not-allowed transition'>
                    Start
                </button>
            </div>
            `;

            let selected = role === "student" ? null : [];

            window.selectLanguage = function(lang) {{
                if (role === "student") {{
                    selected = lang;
                    enableStart();
                }} else {{
                    if (selected.includes(lang)) {{
                        selected = selected.filter(l => l !== lang);
                    }} else {{
                        selected.push(lang);
                    }}
                    enableStart();
                }}
            }}

            function enableStart() {{
                const btn = document.getElementById("startBtn");
                const ok = role === "student" ? selected !== null : selected.length > 0;

                if (ok) {{
                    btn.classList.remove("opacity-50", "cursor-not-allowed");
                }} else {{
                    btn.classList.add("opacity-50", "cursor-not-allowed");
                }}
            }}

            window.goRoom = function() {{
                if (role === "student") {{
                    window.location.href = `/room?role=student&lang=${{selected}}`;
                }} else {{
                    window.location.href = `/room?role=teacher&langs=${{selected.join(",")}}`;
                }}
            }}
        }}
        </script>
    </body>
    </html>
    """


# =======================
#   ROOM PAGE
# =======================
@app.get("/room", response_class=HTMLResponse)
async def room(role: str = "student", lang: str = None, langs: str = None):

    lang_display = lang if role == "student" else langs.replace(",", ", ")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>5min Talk Room</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>

    <body class="bg-gradient-to-b from-white to-indigo-100 min-h-screen px-4 py-6">

        <div class="max-w-md mx-auto bg-white/80 backdrop-blur-md border border-indigo-100
                    shadow-xl rounded-3xl p-6 mt-4">

            <h2 class="text-xl font-bold text-indigo-600 text-center mb-1">5-Minute Session</h2>
            <p class="text-center text-gray-500 text-sm mb-1">Role: <b>{role}</b></p>
            <p class="text-center text-gray-600 text-sm mb-3">Language: <b>{lang_display}</b></p>

            <!-- VIDEO AREA -->
            <div class="relative w-full h-64 rounded-2xl overflow-hidden shadow-inner mb-4 bg-black">

                <!-- 相手のダミー画像 -->
                <img src="/image/partner_dummy.png"
                     id="remotePlaceholder"
                     class="absolute inset-0 w-full h-full object-cover opacity-90">

                <!-- 相手の映像（WebRTC用） -->
                <video id="remoteVideo"
                       class="absolute inset-0 w-full h-full object-cover hidden"
                       autoplay playsinline>
                </video>

                <!-- 自分の映像（右下小） -->
                <video id="localVideo"
                       class="absolute bottom-3 right-3 w-28 h-20 object-cover rounded-xl border-2 border-white shadow-lg"
                       autoplay muted playsinline>
                </video>
            </div>

            <div id="timer" class="text-4xl font-bold text-center text-red-500 mb-4">05:00</div>

            <div class="flex justify-center gap-4 mb-6">
                <button id="toggleCam"
                    class="px-4 py-2 bg-indigo-500 text-white rounded-xl shadow hover:bg-indigo-600 transition active:scale-95">
                    📷 Camera Off
                </button>

                <button onclick="window.location.href='/dashboard'"
                    class="px-4 py-2 border border-red-500 text-red-500 rounded-xl hover:bg-red-50 transition active:scale-95">
                    Leave
                </button>
            </div>
        </div>

        <script>
        // ====== CAMERA ======
        let localStream;
        const localVideo = document.getElementById("localVideo");

        async function startCamera() {{
            try {{
                localStream = await navigator.mediaDevices.getUserMedia({{ video: true }});
                localVideo.srcObject = localStream;
            }} catch (err) {{
                alert("Camera access denied.");
            }}
        }}
        startCamera();

        // ====== CAMERA TOGGLE ======
        const camBtn = document.getElementById("toggleCam");
        camBtn.addEventListener("click", () => {{
            const track = localStream.getVideoTracks()[0];
            track.enabled = !track.enabled;
            camBtn.textContent = track.enabled ? "📷 Camera Off" : "📷 Camera On";
        }});

        // ====== TIMER ======
        let remaining = 5 * 60;
        const timerEl = document.getElementById("timer");

        const countdown = setInterval(() => {{
            remaining--;

            if (remaining <= 0) {{
                clearInterval(countdown);
                timerEl.textContent = "Time's up!";
                timerEl.classList.add("text-gray-500");

                setTimeout(() => {{ window.location.href="/dashboard"; }}, 1500);
            }} else {{
                const m = String(Math.floor(remaining / 60)).padStart(2, '0');
                const s = String(remaining % 60).padStart(2, '0');
                timerEl.textContent = `${{m}}:${{s}}`;
            }}
        }}, 1000);
        </script>

    </body>
    </html>
    """


# =======================
#   ROOT REDIRECT
# =======================
@app.get("/", response_class=HTMLResponse)
async def root():
    return """<meta http-equiv="refresh" content="0; URL=/dashboard" />"""
