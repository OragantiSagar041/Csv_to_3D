# NestUp 3D Cabinet Viewer: Technical Walkthrough

This document explains the "How" and "Why" behind the technical decisions made in this project.

## 🏗️ 1. Handling the Hierarchy (Level 0 → 1 → 2)

**The Challenge:** CSV data is flat, but cabinets are hierarchical. A plank's position is usually relative to the cabinet, and a cabinet is relative to a wall.

**The Solution:** 
- We use a **Stateful Builder Pattern** in `src/services/model_builder.py`.
- As the parser iterates through rows:
    - **Level 0 (Wall)**: Becomes the global anchor. We only allow one wall.
    - **Level 1 (Cabinet)**: We look for the active wall and set it as the parent. The cabinet becomes the "current" parent for any subsequent planks.
    - **Level 2 (Plank)**: We look for the active cabinet. If a plank appears before a cabinet is defined, it is caught as a validation error.
- **Why?** This ensures that if the CSV rows are out of order (e.g., a plank listed before its cabinet), the system either handles it or provides a clear error instead of crashing with a "null pointer."
- **Traceability**: Every object in the hierarchy stores its `sourceRow` index, allowing you to point to any plank and say exactly which line it came from.

## 📏 2. Coordinate & Unit Processing

**The Challenge:** Input data often contains strings like `1200mm` or `1.2m`, while 3D engines (Three.js) require raw numbers.

**The Solution:**
- `src/utils/unit_converter.py` uses a **Regular Expression** (`r"(-?\d+(?:\.\d+)?)(mm)?"`) to strip units and convert them to floats.
- **Why?** RegEx is more robust than simple string slicing because it handles optional units, negative numbers, and decimals in one go.

## 🛡️ 3. Handling Edge Cases & Invalid Data

We thought about these scenarios without being prompted:

| Scenario | Handling Strategy | Why? |
| :--- | :--- | :--- |
| **Negative Positions** | Fully Supported | In 3D space, an object might be offset behind the origin. We don't block these. |
| **Zero/Negative Dimensions** | Row Skipped + Logged | A plank with `0mm` width is physically impossible. We skip the row and log a "Warning." |
| **Missing Headers** | Fuzzy Normalization | We use `src/utils/normalizers.py` to match `LenX`, `LengthX`, or `width` to the same data field. |
| **No Wall Found** | Error Logged | A cabinet cannot exist in "void." We flag this as a critical error in the UI. |

## ✨ 4. Beyond the Brief (The "WOW" Factors)

- **Offline-Ready 3D**: We vendored `three.js` locally into the `/static/` folder so the demo works even without internet.
- **Material Grouping**: The `metadata` section of the JSON automatically groups parts by material (Plywood vs. HDF), making it ready for a manufacturing "Cut List."
- **Interactive Labels**: Every 3D part has a floating text label generated via `CanvasTexture`, so you can identify parts instantly.
- **Interactive CLI**: The Python script isn't just for the web; run `python -m src.main` for a modern, interactive terminal experience.

## 📋 5. Final Checklist Support

- **Visibility**: Wall is Blue-Grey, Cabinets are Wood-toned, and Planks are Green for clear visual separation.
- **Hierarchy Reflection**: The frontend handles coordinate offsets (`parentPosition.x + position.x`) to accurately reflect nested 3D positions.
- **Clean Code Check**: We have distinct files for models, parsers, and services. It's clean, modular, and easy to read.
