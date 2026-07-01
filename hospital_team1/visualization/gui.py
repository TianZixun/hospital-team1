from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, abort, render_template, send_from_directory, url_for

from .dashboard_data import get_dashboard_context


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    project_root = Path(__file__).resolve().parents[2]
    allowed_artifacts = {
        "performance_comparison.png",
        "performance_results.csv",
        "datasets/patients_dataset.csv",
        "require.rtf",
    }

    @app.get("/")
    def dashboard() -> str:
        context = get_dashboard_context()
        if context["performance_chart_available"]:
            context["performance_chart_url"] = url_for(
                "artifact_file", filename="performance_comparison.png"
            )
        else:
            context["performance_chart_url"] = None
        if context["performance_csv_available"]:
            context["performance_csv_url"] = url_for(
                "artifact_file", filename="performance_results.csv"
            )
        else:
            context["performance_csv_url"] = None
        context["dataset_download_url"] = url_for(
            "artifact_file", filename="datasets/patients_dataset.csv"
        )
        context["requirements_url"] = url_for("artifact_file", filename="require.rtf")
        return render_template("dashboard.html", **context)

    @app.get("/artifacts/<path:filename>")
    def artifact_file(filename: str):
        normalized = filename.replace("\\", "/")
        if normalized not in allowed_artifacts:
            abort(404)
        return send_from_directory(project_root, filename)

    @app.get("/healthz")
    def healthcheck() -> tuple[str, int]:
        return "ok", 200

    return app


def launch_gui() -> None:
    app = create_app()
    port = int(
        os.environ.get("HOSPITAL_TEAM1_PORT", os.environ.get("PORT", "5055"))
    )
    host = os.environ.get("HOSPITAL_TEAM1_HOST", "127.0.0.1")
    app.run(host=host, port=port, debug=False)
