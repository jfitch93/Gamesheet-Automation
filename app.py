"""
WRHL Gamesheet Processor — Flask Dashboard
"""

import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from mock_pipeline import FAKE_EMAILS, SCHEDULE, run_pipeline

_base = os.path.dirname(os.path.abspath(__file__))
_tmpl = "templates" if os.path.isdir(os.path.join(_base, "templates")) else "template"

app = Flask(__name__, template_folder=_tmpl)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload limit

UPLOAD_FOLDER = "/tmp/wrhl_uploads" if os.path.exists("/tmp") else os.path.join(_base, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def _render(**kwargs):
    try:
        return render_template("index.html", **kwargs)
    except Exception:
        return render_template("index", **kwargs)


@app.route("/static/wrhl-logo.png")
def serve_logo():
    static_dir = os.path.join(_base, "static")
    name = "wrhl-logo.png" if os.path.exists(os.path.join(static_dir, "wrhl-logo.png")) else "logo"
    return send_from_directory(static_dir, name)


def get_dashboard_data():
    results = run_pipeline(FAKE_EMAILS)
    counts = {"gs-verified": 0, "gs-needs-review": 0, "gs-disciplinary": 0}
    gamesheets = []

    for r in results:
        p = r["parsed"]
        issues = r["issues"]
        tag = r["tag"]
        counts[tag] += 1
        all_issues = (
            issues["unregistered"] + issues["suspended"] + issues["number_mismatch"]
        )
        gamesheets.append({
            "id": p["id"],
            "subject": p["subject"],
            "date": p["date"],
            "home_team": p["home_team"],
            "away_team": p["away_team"],
            "score": p["score"],
            "sent_by": p["from"],
            "tag": tag,
            "players": p["players"],
            "penalties": p["penalties"],
            "issues": all_issues,
        })

    return {
        "total": len(results),
        "verified": counts["gs-verified"],
        "needs_review": counts["gs-needs-review"],
        "disciplinary": counts["gs-disciplinary"],
        "gamesheets": gamesheets,
    }


def mock_analyse(digital_name, photo_name):
    return {
        "digital_file": digital_name,
        "photo_file": photo_name,
        "status": "needs-review",
        "summary": "2 discrepancies found between the digital file and the physical gamesheet photo.",
        "digital": {
            "home_team": "Ice Dragons",
            "away_team": "Saracens",
            "date": "July 9, 2025",
            "score": "Ice Dragons 4 – Saracens 2",
            "players": 16,
            "penalties": 2,
        },
        "photo": {
            "home_team": "Ice Dragons",
            "away_team": "Saracens",
            "date": "July 9, 2025",
            "score": "Ice Dragons 4 – Saracens 2",
            "players": 16,
            "penalties": 2,
        },
        "discrepancies": [
            {
                "type": "Player Name Mismatch",
                "severity": "warning",
                "detail": "Digital file lists #44 as 'Sam Firth' — physical sheet reads 'Sam Furth'.",
            },
            {
                "type": "Penalty Missing",
                "severity": "error",
                "detail": "Physical sheet shows a 2-min Roughing on #14 Connor Walsh that does not appear in the digital file.",
            },
        ],
    }


@app.route("/")
def index():
    data = get_dashboard_data()
    submitted = sum(1 for g in SCHEDULE if g["submitted"])
    missing   = sum(1 for g in SCHEDULE if not g["submitted"])
    return _render(
        data=data,
        analysis=None,
        upload_errors=[],
        schedule=SCHEDULE,
        schedule_submitted=submitted,
        schedule_missing=missing,
        bulk_results=[],
    )


@app.route("/analyse", methods=["POST"])
def analyse():
    digital = request.files.get("digital_file")
    photo   = request.files.get("photo_file")

    errors = []
    if not digital or digital.filename == "":
        errors.append("Please upload a digital gamesheet file.")
    if not photo or photo.filename == "":
        errors.append("Please upload a physical gamesheet photo.")

    if errors:
        data = get_dashboard_data()
        submitted = sum(1 for g in SCHEDULE if g["submitted"])
        missing   = sum(1 for g in SCHEDULE if not g["submitted"])
        return _render(
            data=data,
            analysis=None,
            upload_errors=errors,
            schedule=SCHEDULE,
            schedule_submitted=submitted,
            schedule_missing=missing,
            bulk_results=[],
        )

    digital.save(os.path.join(UPLOAD_FOLDER, digital.filename))
    photo.save(os.path.join(UPLOAD_FOLDER, photo.filename))
    result = mock_analyse(digital.filename, photo.filename)

    data = get_dashboard_data()
    submitted = sum(1 for g in SCHEDULE if g["submitted"])
    missing   = sum(1 for g in SCHEDULE if not g["submitted"])
    return _render(
        data=data,
        analysis=result,
        upload_errors=[],
        schedule=SCHEDULE,
        schedule_submitted=submitted,
        schedule_missing=missing,
        bulk_results=[],
    )


@app.route("/bulk", methods=["POST"])
def bulk():
    processed = []
    for game in SCHEDULE:
        gid     = game["game_id"]
        digital = request.files.get(f"digital_{gid}")
        photo   = request.files.get(f"photo_{gid}")
        if digital and digital.filename and photo and photo.filename:
            digital.save(os.path.join(UPLOAD_FOLDER, digital.filename))
            photo.save(os.path.join(UPLOAD_FOLDER, photo.filename))
            result = mock_analyse(digital.filename, photo.filename)
            result["game_id"] = gid
            result["matchup"] = f"{game['home_team']} vs {game['away_team']}"
            result["date"]    = game["date"]
            result["referee"] = game["referee"]
            processed.append(result)

    data = get_dashboard_data()
    submitted = sum(1 for g in SCHEDULE if g["submitted"])
    missing   = sum(1 for g in SCHEDULE if not g["submitted"])
    return _render(
        data=data,
        analysis=None,
        upload_errors=[],
        schedule=SCHEDULE,
        schedule_submitted=submitted,
        schedule_missing=missing,
        bulk_results=processed,
    )


@app.route("/process", methods=["POST"])
def process():
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=True, port=port)
