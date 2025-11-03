# ===================================================================================== #

from flask import Blueprint, redirect, request
import requests

redirector = Blueprint("redirector", __name__)

@redirector.route("/go")
def go():
    target = request.args.get("url")
    if not target:
        return "Missing URL parameter!", 400

    try:
        test = requests.head(target, timeout=5)
    except Exception:
        return "Target site not reachable!", 502

    return redirect(target, code=302)

# ================================ The End =============================== #
