from __future__ import annotations

import json

from flask import Flask, jsonify, redirect, render_template, request, url_for

from src.parsers.csv_parser import parse_csv
from src.services.model_builder import build_model


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

    @app.get("/")
    def index():
        return render_template("index.html")

    def _convert_request_to_model():
        uploaded_file = request.files.get("csv_file")
        pasted_csv = request.form.get("csv_text", "").strip()

        if uploaded_file and uploaded_file.filename:
            csv_text = uploaded_file.read().decode("utf-8")
            source_name = uploaded_file.filename
        elif pasted_csv:
            csv_text = pasted_csv
            source_name = "Pasted CSV"
        else:
            raise ValueError("Upload a CSV file or paste CSV content before converting.")

        rows = parse_csv(csv_text)
        model = build_model(rows)
        return {
            "sourceName": source_name,
            "rowCount": len(rows),
            "model": model,
            "modelJson": json.dumps(model, indent=2),
        }

    @app.route("/convert", methods=["GET", "POST"])
    def convert():
        if request.method == "GET":
            return redirect(url_for("index"))

        try:
            payload = _convert_request_to_model()
            return render_template("index.html", result=payload)
        except UnicodeDecodeError:
            return render_template(
                "index.html",
                error="The uploaded file could not be decoded as UTF-8 CSV.",
            ), 400
        except ValueError as error:
            return render_template("index.html", error=str(error)), 400
        except Exception as error:  # pragma: no cover
            return render_template(
                "index.html",
                error=f"Failed to convert the CSV: {error}",
            ), 500

    @app.post("/api/convert")
    def api_convert():
        try:
            payload = _convert_request_to_model()
            return jsonify(payload)
        except UnicodeDecodeError:
            return jsonify({"error": "The uploaded file could not be decoded as UTF-8 CSV."}), 400
        except ValueError as error:
            return jsonify({"error": str(error)}), 400
        except Exception as error:  # pragma: no cover
            return jsonify({"error": f"Failed to convert the CSV: {error}"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
