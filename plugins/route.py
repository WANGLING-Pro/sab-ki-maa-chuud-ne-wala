import time
import secrets
from aiohttp import web

routes = web.RouteTableDef()

# token -> {"url": real_url, "created": timestamp}
_verify_store = {}
_TOKEN_TTL = 300     # token 5 min me expire
_MIN_DELAY = 2        # kam se kam itne second rukna zaroori


def create_verify_token(real_url: str) -> str:
    token = secrets.token_urlsafe(16)
    _verify_store[token] = {"url": real_url, "created": time.time()}
    return token


def _cleanup_expired():
    now = time.time()
    expired = [t for t, d in _verify_store.items() if now - d["created"] > _TOKEN_TTL]
    for t in expired:
        _verify_store.pop(t, None)


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("Wangling FileStore")


@routes.get("/verify")
async def verify_page(request):
    token = request.query.get("u")
    if not token or token not in _verify_store:
        return web.Response(
            text="<h3 style='font-family:sans-serif;text-align:center;margin-top:40px;'>⚠️ Invalid or expired link.</h3>",
            content_type="text/html",
            status=400
        )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Human Verification</title>
    <style>
        body {{
            background:#0f0f1a; color:#fff; font-family:sans-serif;
            display:flex; align-items:center; justify-content:center;
            height:100vh; margin:0; text-align:center;
        }}
        .box {{
            background:#1b1b2f; padding:40px 30px; border-radius:16px;
            box-shadow:0 0 30px rgba(120,90,255,0.3); max-width:340px;
        }}
        .shield {{ font-size:48px; margin-bottom:10px; }}
        button {{
            background:linear-gradient(90deg,#6a5cff,#a15cff);
            border:none; color:#fff; padding:14px 26px; border-radius:10px;
            font-size:16px; cursor:pointer; margin-top:20px;
        }}
        button:disabled {{ opacity:0.6; }}
        .status {{ margin-top:14px; font-size:13px; color:#9a9ac0; }}
    </style>
    </head>
    <body>
        <div class="box">
            <div class="shield">🛡️</div>
            <h2>Human Verification</h2>
            <p>Click the button below to continue</p>
            <button id="btn" onclick="verify()" disabled>👆 Click to Continue</button>
            <div class="status" id="status">Please wait a moment...</div>
        </div>

        <script>
            const token = "{token}";
            const btn = document.getElementById("btn");
            const status = document.getElementById("status");

            setTimeout(() => {{
                btn.disabled = false;
                status.innerText = "Ready — click to continue";
            }}, {_MIN_DELAY * 1000});

            async function verify() {{
                if (btn.disabled) return;
                btn.disabled = true;
                btn.innerText = "✓ Verifying...";
                status.innerText = "Verifying...";
                try {{
                    const res = await fetch("/resolve?u=" + token);
                    const data = await res.json();
                    if (data.url) {{
                        btn.innerText = "✓ Verified!";
                        status.innerText = "Redirecting...";
                        setTimeout(() => {{ window.location.href = data.url; }}, 800);
                    }} else {{
                        status.innerText = "❌ Link expired, go back and try again.";
                    }}
                }} catch (e) {{
                    status.innerText = "❌ Something went wrong.";
                }}
            }}
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type="text/html")


@routes.get("/resolve")
async def resolve_link(request):
    token = request.query.get("u")
    _cleanup_expired()
    data = _verify_store.get(token)

    if not data:
        return web.json_response({"error": "invalid or expired"}, status=400)

    if time.time() - data["created"] < _MIN_DELAY:
        return web.json_response({"error": "too fast"}, status=400)

    # one-time use
    _verify_store.pop(token, None)
    return web.json_response({"url": data["url"]})