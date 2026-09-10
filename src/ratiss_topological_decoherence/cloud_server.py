"""Local-first RATISS Quantum Topology Studio Cloud application server.

The same app can run on a personal machine for development or on a chosen
powerful host later. It does not require an external cloud API at runtime.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import argparse
import json

from flask import Flask, jsonify, request, send_from_directory

from .studio_import import run_studio_document


WEB_ROOT = Path(__file__).resolve().parents[2] / "web"
EXAMPLE_PATH = Path(__file__).resolve().parents[2] / "examples" / "transmon-microcell.studio.json"
ARTIFACT_ROOT = Path(__file__).resolve().parents[2] / "artifacts"


def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(WEB_ROOT), static_url_path="")

    @app.get("/")
    def index() -> Any:
        return send_from_directory(WEB_ROOT, "index.html")

    @app.get("/api/health")
    def health() -> Any:
        return jsonify({"service": "ratiss-quantum-topology-studio-cloud", "mode": "local_or_self_hosted", "external_cloud_required": False})

    @app.get("/api/studio/example")
    def example() -> Any:
        return jsonify(json.loads(EXAMPLE_PATH.read_text(encoding="utf-8")))

    @app.get("/artifacts/<path:artifact_path>")
    def artifact(artifact_path: str) -> Any:
        """Serve only versioned local artifacts for the interactive documentation demos."""
        return send_from_directory(ARTIFACT_ROOT, artifact_path)

    @app.post("/api/simulate/studio")
    def simulate_studio() -> Any:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Expected a Quantum Circuit Studio JSON document."}), 400
        try:
            timeline = run_studio_document(payload)
        except (TypeError, ValueError) as error:
            return jsonify({"error": str(error)}), 400
        return jsonify(timeline)

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local-first RATISS Quantum Topology Studio Cloud.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind interface; use a private-network address only when intended.")
    parser.add_argument("--port", default=8765, type=int, help="Listening port.")
    args = parser.parse_args()
    create_app().run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
