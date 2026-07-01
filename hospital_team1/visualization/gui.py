from __future__ import annotations

import os

from flask import Flask, render_template

from .dashboard_data import get_dashboard_context


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    @app.get("/")
    def dashboard() -> str:
        return render_template("dashboard.html", **get_dashboard_context())

    return app


def launch_gui() -> None:
    app = create_app()
    port = int(os.environ.get("HOSPITAL_TEAM1_PORT", "5055"))
    app.run(host="127.0.0.1", port=port, debug=False)
