from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request, send_from_directory, url_for

from .dashboard_data import (
    add_runtime_patient,
    complete_runtime_patient,
    get_dashboard_context,
)


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    project_root = Path(__file__).resolve().parents[2]
    allowed_artifacts = {
        "performance_comparison.png",
        "performance_results.csv",
        "datasets/patients_dataset.csv",
        "require.rtf",
    }

    def _artifact_mtime(filename: str) -> int | None:
        artifact_path = project_root / filename
        if artifact_path.exists():
            return int(artifact_path.stat().st_mtime)
        return None

    def _parse_snapshot_offset() -> int:
        raw_value = request.args.get("snapshot_offset", "0")
        try:
            return max(0, int(raw_value))
        except ValueError:
            return 0

    def _parse_queue_mode() -> str:
        raw_value = request.args.get("queue_mode", "heap")
        if raw_value in {"heap", "ordered_list"}:
            return raw_value
        return "heap"

    @app.get("/")
    def dashboard() -> str:
        snapshot_offset = _parse_snapshot_offset()
        queue_mode = _parse_queue_mode()
        context = get_dashboard_context(
            snapshot_offset_minutes=snapshot_offset,
            queue_mode=queue_mode,
        )
        if context["performance_chart_available"]:
            context["performance_chart_url"] = url_for(
                "artifact_file",
                filename="performance_comparison.png",
                v=_artifact_mtime("performance_comparison.png"),
            )
        else:
            context["performance_chart_url"] = None
        if context["performance_csv_available"]:
            context["performance_csv_url"] = url_for(
                "artifact_file",
                filename="performance_results.csv",
                v=_artifact_mtime("performance_results.csv"),
            )
        else:
            context["performance_csv_url"] = None
        context["dataset_download_url"] = url_for(
            "artifact_file",
            filename="datasets/patients_dataset.csv",
            v=_artifact_mtime("datasets/patients_dataset.csv"),
        )
        context["requirements_url"] = url_for("artifact_file", filename="require.rtf")
        context["run_simulation_url"] = url_for(
            "run_simulation_action",
            snapshot_offset=snapshot_offset,
            queue_mode=queue_mode,
        )
        context["add_patient_url"] = url_for(
            "add_patient_action",
            snapshot_offset=snapshot_offset,
            queue_mode=queue_mode,
        )
        context["complete_patient_url_template"] = url_for(
            "complete_patient_action",
            patient_id="__PATIENT_ID__",
            snapshot_offset=snapshot_offset,
            queue_mode=queue_mode,
        )
        return render_template("dashboard.html", **context)

    @app.get("/api/actions/run-simulation")
    def run_simulation_action():
        snapshot_offset = _parse_snapshot_offset()
        queue_mode = _parse_queue_mode()
        context = get_dashboard_context(
            snapshot_offset_minutes=snapshot_offset,
            queue_mode=queue_mode,
        )
        summary = context["simulation_summary"]
        return jsonify(
            {
                "message": (
                    f"Simulation completed at {summary['snapshot_time']}. "
                    f"Treated {summary['treated_patients']} patients, "
                    f"compliance {summary['compliance_rate']:.1f}%, "
                    f"max wait {summary['max_wait_minutes']:.1f} min."
                ),
                "summary": summary,
            }
        )

    @app.post("/api/actions/add-patient")
    def add_patient_action():
        snapshot_offset = _parse_snapshot_offset()
        patient = add_runtime_patient(snapshot_offset_minutes=snapshot_offset)
        return jsonify(
            {
                "message": (
                    f"{patient['patient_id']} added from the CSV-based template. "
                    "The queue and charts will refresh now."
                ),
                "patient": patient,
            }
        )

    @app.post("/api/actions/complete-patient/<patient_id>")
    def complete_patient_action(patient_id: str):
        snapshot_offset = _parse_snapshot_offset()
        result = complete_runtime_patient(
            patient_id=patient_id,
            snapshot_offset_minutes=snapshot_offset,
        )
        status_code = 200 if result["ok"] else 404
        return jsonify(result), status_code

    @app.get("/artifacts/<path:filename>")
    def artifact_file(filename: str):
        normalized = filename.replace("\\", "/")
        if normalized not in allowed_artifacts:
            abort(404)
        return send_from_directory(project_root, filename)

    @app.get("/favicon.ico")
    def favicon() -> tuple[object, int] | object:
        static_root = Path(app.static_folder or "")
        favicon_path = static_root / "favicon.svg"
        if not favicon_path.exists():
            abort(404)
        return send_from_directory(static_root, "favicon.svg", mimetype="image/svg+xml")

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
