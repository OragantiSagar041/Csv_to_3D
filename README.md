# NestUp 3D Model Backend

This project implements a Python web app plus backend logic that transforms cabinet CSV input into structured JSON and a working 3D scene for rendering.

## Features

- Web interface for uploading a CSV file
- Interactive 3D visualization using Three.js
- Renders:
  - wall as the base box
  - cabinet positioned relative to the wall
  - planks positioned inside the cabinet
- Parses CSV rows into structured records
- Converts values such as `1362mm` into numeric millimeter values
- Models the domain using `Wall`, `Cabinet`, and `Plank` classes
- Preserves parent-child relationships:
  - cabinets are relative to the wall
  - planks are relative to their cabinet
- Skips invalid rows and records validation logs
- Supports negative positions
- Adds bonus metadata for material-based grouping

## Expected CSV Columns

- `Entity Name`
- `Level`
- `Material`
- `LenX`, `LenY`, `LenZ`
- `X`, `Y`, `Z`
- `plank_id` (optional)

The parser also accepts a few close header variations such as `EntityName`, `Name`, `PositionX`, or `Plank ID`.

## Project Structure

- [app.py](app.py): Flask web entrypoint
- [templates/index.html](templates/index.html): upload page and result view
- [static/styles.css](static/styles.css): page styling
- [src/main.py](src/main.py): interactive CLI entrypoint
- [src/parsers/csv_parser.py](src/parsers/csv_parser.py): CSV parsing logic
- [src/utils/unit_converter.py](src/utils/unit_converter.py): unit normalization
- [src/utils/normalizers.py](src/utils/normalizers.py): header cleanup helpers
- [src/models/entities.py](src/models/entities.py): 3D cabinet object models
- [src/services/model_builder.py](src/services/model_builder.py): hierarchy and validation rules

## Run Website

```bash
pip install -r requirements.txt
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in the browser and upload a CSV file.

Note: The project now includes local copies of **Three.js** and **OrbitControls** in the `/static/` folder, so the 3D viewer is fully **offline-ready**!

## Optional CLI

The CLI is versatile and supports both direct arguments and interactive mode:

```bash
# Run with a specific file:
python -m src.main sample-data.csv

# Or run interactively (it will prompt for a file path or CSV content):
python -m src.main
```

## Output Shape

```json
{
  "wall": {},
  "cabinets": [
    {
      "cabinet": {},
      "planks": []
    }
  ],
  "metadata": {
    "cabinetCount": 0,
    "plankCount": 0,
    "materialGroups": {},
    "validationLogs": []
  }
}
```
