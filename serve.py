from __future__ import annotations

import os

from hospital_team1.visualization.gui import create_app

try:
    from waitress import serve as waitress_serve
except ModuleNotFoundError:
    waitress_serve = None


app = create_app()


def main() -> None:
    host = os.environ.get("HOSPITAL_TEAM1_HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", os.environ.get("HOSPITAL_TEAM1_PORT", "5055")))
    if waitress_serve is not None:
        waitress_serve(app, host=host, port=port)
        return

    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
