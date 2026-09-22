#!/usr/bin/env python3
"""Copy generated chart artifacts into a type-oriented library.

The original files are never moved or modified. The destination keeps each
artifact's source path so files with the same name cannot overwrite each other.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
from collections import Counter
from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".svg", ".jpg", ".jpeg", ".webp"}
NEWSLETTER_WEEK = re.compile(r"^\d{4}_\d+주차$")
SOURCE_DIRECTORIES = (
    Path("outputs/charts"),
    Path("tradeXYZ_Inforgraphic_retouch"),
)
EXTRA_SOURCE_GLOBS = ("*9-15*",)

CATEGORY_LABELS = {
    "line": "Line charts",
    "area": "Area charts",
    "bar": "Bar charts",
    "stacked": "Stacked bar and area charts",
    "pie-donut": "Pie and donut charts",
    "scatter": "Scatter and bubble charts",
    "heatmap": "Heatmaps and matrix charts",
    "sankey-flow": "Sankey, flow, and network charts",
    "table-scorecard": "Tables, rankings, and scorecards",
    "diagram": "Diagrams, funnels, and timelines",
    "combo": "Mixed chart types",
    "other": "Unclassified or custom charts",
}

NEWSLETTER_EXPORT_TYPES = {
    1: "combo",
    2: "line",
    3: "stacked",
    4: "combo",
    5: "combo",
    6: "line",
    7: "line",
    8: "bar",
    9: "bar",
    10: "stacked",
    11: "stacked",
    12: "line",
    13: "bar",
    14: "bar",
    15: "bar",
    16: "stacked",
    17: "stacked",
}


def iter_artifacts(root: Path) -> list[Path]:
    artifacts: list[Path] = []
    for relative_dir in SOURCE_DIRECTORIES:
        source_dir = root / relative_dir
        if not source_dir.exists():
            continue
        artifacts.extend(
            path
            for path in source_dir.rglob("*")
            if path.is_file()
            and path.suffix.lower() in IMAGE_EXTENSIONS
            and not any(NEWSLETTER_WEEK.match(part) for part in path.relative_to(root).parts)
        )

    for pattern in EXTRA_SOURCE_GLOBS:
        for source_dir in root.glob(pattern):
            if not source_dir.is_dir():
                continue
            artifacts.extend(
                path
                for path in source_dir.rglob("*")
                if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
            )

    artifacts.extend(
        path
        for path in root.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    return sorted(set(artifacts), key=lambda path: path.as_posix())


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def load_chart_scripts(root: Path) -> list[tuple[Path, str, str, str]]:
    scripts = []
    for path in sorted((root / "charts").glob("*.py")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        scripts.append((path, normalized(path.stem), lowered, normalized(lowered)))
    return scripts


def related_script(
    artifact: Path, scripts: list[tuple[Path, str, str, str]]
) -> tuple[Path | None, str]:
    stem = normalized(artifact.stem)
    stem_without_variant = re.sub(
        r"_(?:wide|tall|square|full|panel|legend|ko|en|dark|light|final|v\d+|\d+x\d+)$",
        "",
        stem,
    )
    best: tuple[int, Path, str] | None = None
    for path, script_stem, text, normalized_text in scripts:
        score = 0
        if script_stem == stem or script_stem == stem_without_variant:
            score = 100
        elif stem.startswith(script_stem + "_") or script_stem.startswith(stem_without_variant + "_"):
            score = 80
        elif stem in normalized_text or stem_without_variant in normalized_text:
            score = 60
        if score and (best is None or score > best[0]):
            best = (score, path, text)
    return (best[1], best[2]) if best else (None, "")


def classify(artifact: Path, script_text: str) -> tuple[str, str]:
    name = normalized(artifact.stem)
    combined = f"{name}\n{script_text}"

    if artifact.parent.name == "export":
        match = re.match(r"(\d+)_", artifact.name)
        if match and int(match.group(1)) in NEWSLETTER_EXPORT_TYPES:
            return NEWSLETTER_EXPORT_TYPES[int(match.group(1))], "newsletter export slot mapping"

    keyword_rules = (
        ("sankey-flow", r"sankey|networkx|alluvial|chord_diagram"),
        ("heatmap", r"heatmap|pcolormesh|\.imshow\("),
        ("pie-donut", r"donut|pie_chart|\.pie\("),
        ("scatter", r"bubble_chart|\.scatter\("),
        ("table-scorecard", r"scorecard|maturation_table|pipeline_table|\.table\("),
        ("diagram", r"lifecycle|funnel|flowchart|diagram|deployer_timeline"),
    )
    for category, pattern in keyword_rules:
        if re.search(pattern, combined):
            return category, f"matched {pattern}"

    has_bar = bool(re.search(r"\.barh?\(", script_text))
    has_area = bool(re.search(r"fill_between|stackplot", script_text))
    has_line = bool(re.search(r"(?:plt|ax\w*)\.plot\(", script_text))
    has_scatter = bool(re.search(r"\.scatter\(", script_text))
    primitives = sum((has_bar, has_area, has_line, has_scatter))

    if (has_bar and (has_line or has_scatter)) or primitives >= 3:
        return "combo", "script uses multiple plotting primitives"
    if has_bar and ("stacked" in combined or re.search(r"\bbottom\s*=", script_text)):
        return "stacked", "script uses stacked bars"
    if has_area and ("stacked" in combined or "stackplot" in script_text):
        return "stacked", "script uses a stacked area"
    if has_bar:
        return "bar", "script uses bar/barh"
    if has_area:
        return "area", "script uses fill_between"
    if has_line:
        return "line", "script uses plot"

    filename_rules = (
        ("pie-donut", r"donut|pie"),
        ("heatmap", r"heatmap|matrix"),
        ("sankey-flow", r"sankey|flow"),
        ("table-scorecard", r"table|scorecard|ranking"),
        ("stacked", r"stacked|composition|breakdown|share"),
        ("area", r"area"),
        ("bar", r"bar|histogram"),
        ("line", r"trend|price|tvl|volume|revenue|growth|supply|fees|ratio|rate|daily|weekly|monthly"),
        ("diagram", r"diagram|timeline|funnel|lifecycle"),
    )
    for category, pattern in filename_rules:
        if re.search(pattern, name):
            return category, f"filename matched {pattern}"
    return "other", "no reliable type signal"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_readme(destination: Path, counts: Counter[str], total_bytes: int) -> None:
    rows = "\n".join(
        f"| `{category}` | {CATEGORY_LABELS[category]} | {counts[category]:,} |"
        for category in CATEGORY_LABELS
    )
    destination.joinpath("README.md").write_text(
        "# Chart Library\n\n"
        "Generated chart artifacts copied from this repository and grouped by visual type. "
        "Original files remain in place. Nested paths under each type preserve provenance and "
        "prevent filename collisions.\n\n"
        f"Total: **{sum(counts.values()):,} files**, **{total_bytes / 1024 / 1024:.1f} MiB**.\n\n"
        "| Directory | Type | Files |\n"
        "|---|---|---:|\n"
        f"{rows}\n\n"
        "See `manifest.csv` for the source path, inferred type, matching chart script, file size, "
        "and SHA-256 digest. Rebuild the library with "
        "`python3 scripts/organize_chart_library.py`.\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--destination", type=Path, default=Path("chart-library"))
    args = parser.parse_args()

    root = args.root.resolve()
    destination = args.destination
    if not destination.is_absolute():
        destination = root / destination
    type_root = destination / "by-type"
    if type_root.exists():
        shutil.rmtree(type_root)
    type_root.mkdir(parents=True, exist_ok=True)

    scripts = load_chart_scripts(root)
    artifacts = iter_artifacts(root)
    counts: Counter[str] = Counter()
    manifest_rows = []
    total_bytes = 0

    for source in artifacts:
        script_path, script_text = related_script(source, scripts)
        category, reason = classify(source, script_text)
        relative_source = source.relative_to(root)
        generated_root = Path("outputs/charts")
        if relative_source.is_relative_to(generated_root):
            library_relative = Path("generated") / relative_source.relative_to(generated_root)
        elif relative_source.parent == Path("."):
            library_relative = Path("root") / relative_source
        else:
            library_relative = relative_source
        target = type_root / category / library_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        size = source.stat().st_size
        counts[category] += 1
        total_bytes += size
        manifest_rows.append(
            {
                "type": category,
                "source_path": relative_source.as_posix(),
                "library_path": target.relative_to(root).as_posix(),
                "matched_script": script_path.relative_to(root).as_posix() if script_path else "",
                "classification_reason": reason,
                "format": source.suffix.lower().lstrip("."),
                "bytes": size,
                "sha256": sha256(source),
            }
        )

    with destination.joinpath("manifest.csv").open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=manifest_rows[0].keys())
        writer.writeheader()
        writer.writerows(manifest_rows)
    write_readme(destination, counts, total_bytes)
    print(f"Copied {len(manifest_rows):,} chart artifacts ({total_bytes / 1024 / 1024:.1f} MiB).")
    for category in CATEGORY_LABELS:
        print(f"  {category:16} {counts[category]:5}")


if __name__ == "__main__":
    main()
