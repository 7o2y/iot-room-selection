#!/usr/bin/env python3
"""
Utility to aggregate mock sensor JSON files into AHPEngine-ready room data.

Usage:
    python scripts/aggregate_sensor_data.py \
        --data-dir "docs/project info&data/Project_sensor_data" \
        --output docs/project info&data/Project_sensor_data/aggregated_rooms.json
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path
from typing import Dict, List, Optional

# Map sensor files to the AHPEngine attribute names
SENSOR_FILES = {
    "temperature_sensor_data.json": "temperature",
    "co2_sensor_data.json": "co2",
    "humidity_sensor_data.json": "humidity",
    "air_quality_sensor_data.json": "air_quality",
    "sound_sensor_data.json": "noise",
    "LightIntensity_sensor_data.json": "light",
    "voc_sensor_data.json": "voc",
}

FACILITIES_FILE = "room_facilities_data.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate mock sensor JSON files into flattened room data."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("docs/project info&data/Project_sensor_data"),
        help="Directory containing the raw sensor JSON files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/project info&data/Project_sensor_data/aggregated_rooms.json"),
        help="Output JSON file that will contain the aggregated rooms.",
    )
    return parser.parse_args()


def _strip_trailing_commas(text: str) -> str:
    """
    Remove trailing commas that make some of the mock files invalid JSON.
    """
    return re.sub(r",(\s*[\]}])", r"\1", text)


def _load_json(path: Path) -> Dict:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        cleaned = _strip_trailing_commas(text)
        return json.loads(cleaned)


def _extract_average(room_entry: Dict) -> Optional[float]:
    values_key = next((k for k in room_entry if k.endswith("_values")), None)
    if not values_key:
        return None
    readings: List[Dict] = room_entry.get(values_key, [])
    if not readings:
        return None
    # Assume the numeric key is everything except timestamp
    value_key = next((k for k in readings[0] if k != "timestamp"), None)
    if not value_key:
        return None
    numeric_values = [entry.get(value_key) for entry in readings]
    numeric_values = [v for v in numeric_values if isinstance(v, (int, float))]
    if not numeric_values:
        return None
    return statistics.mean(numeric_values)


def aggregate_sensor_files(data_dir: Path) -> Dict[str, Dict]:
    rooms: Dict[str, Dict] = {}

    for filename, attr in SENSOR_FILES.items():
        path = data_dir / filename
        if not path.exists():
            continue

        data = _load_json(path)
        for room_entry in data.get("rooms", []):
            name = room_entry.get("name") or room_entry.get("room_id")
            if not name:
                continue

            avg_value = _extract_average(room_entry)
            if avg_value is None:
                continue

            room = rooms.setdefault(
                name,
                {
                    "room_id": room_entry.get("room_id", name),
                    "name": name,
                },
            )
            room[attr] = avg_value

    return rooms


def merge_facilities(rooms: Dict[str, Dict], facilities_path: Path) -> None:
    if not facilities_path.exists():
        return

    data = _load_json(facilities_path)
    for entry in data.get("rooms", []):
        name = entry.get("name")
        if not name:
            continue

        room = rooms.setdefault(
            name,
            {
                "room_id": entry.get("name", name),
                "name": entry.get("name", name),
            },
        )

        facilities = entry.get("facilities", {})
        room["seating_capacity"] = facilities.get(
            "seating_capacity", room.get("seating_capacity", 0)
        )
        room["has_projector"] = facilities.get(
            "videoprojector", room.get("has_projector", False)
        )
        room["computers"] = facilities.get("computers", room.get("computers", 0))
        room["has_robots"] = bool(
            facilities.get("robots_for_training", room.get("has_robots", False))
        )


def main() -> None:
    args = parse_args()
    rooms = aggregate_sensor_files(args.data_dir)
    merge_facilities(rooms, args.data_dir / FACILITIES_FILE)

    sorted_rooms = sorted(rooms.values(), key=lambda r: r["name"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(sorted_rooms, f, indent=2)

    print(f"Wrote {len(sorted_rooms)} rooms to {args.output}")


if __name__ == "__main__":
    main()
