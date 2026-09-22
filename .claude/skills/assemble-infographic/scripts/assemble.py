#!/usr/bin/env python3
"""Assemble a transparent chart SVG into the Four Pillars 1920x1080 template."""

from __future__ import annotations

import argparse
import copy
import math
import re
import shutil
import subprocess
import sys
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
SVG = f"{{{SVG_NS}}}"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = SKILL_DIR / "assets" / "four-pillars-graph-h-1080.svg"
FONT_FAMILY = "Pretendard"

BASE_CHART_SLOT = (160.0, 290.0, 1600.0, 640.0)
BOTTOM_CHART_SLOT = (160.0, 290.0, 1600.0, 540.0)
LEGEND_LEFT = 160.0
LEGEND_TOP = 850.0
LEGEND_WIDTH = 1600.0
RIGHT_CHART_LEFT = 160.0
RIGHT_CHART_TOP = 300.0
RIGHT_CHART_MAX_WIDTH = 1320.0
RIGHT_CHART_MAX_HEIGHT = 630.0
RIGHT_LEGEND_GAP = 30.0
MAX_LEGEND_ITEMS = 6
BOTTOM_LEGEND_RATIO = 1.8
LEGEND_FONT_SIZE = 28.0
LEGEND_SQUARE_SIZE = 24.0
LEGEND_LINE_WIDTH = 48.0
LEGEND_LINE_HEIGHT = 8.0
LEGEND_DASH_STROKE = 10.0
# Pretendard cap height is 1448 units on a 2048 UPM em. Position labels with
# an explicit alphabetic baseline so Figma and SVG renderers agree; Figma does
# not reliably preserve dominant-baseline when importing SVG text.
PRETENDARD_CAP_HEIGHT_RATIO = 1448 / 2048
SOURCE_VALUE_POSITION = (203.0, 1034.0)
DATE_VALUE_POSITION = (1205.0, 1034.0)
NOTE_VALUE_POSITION = (203.0, 995.0)


@dataclass(frozen=True)
class LegendItem:
    label: str
    color: str
    style: str


def uppercase_word_initials(text: str) -> str:
    """Uppercase each word initial without lowercasing brand-internal text."""
    return re.sub(
        r"(?<![A-Za-z0-9])([A-Za-z])",
        lambda match: match.group(1).upper(),
        text,
    )


def balanced_wrap(text: str, max_chars: int) -> list[str]:
    """Wrap text into the fewest possible, visually balanced lines."""
    words = text.split()
    if not words:
        return [""]

    greedy_lines = textwrap.wrap(
        text,
        width=max_chars,
        break_long_words=True,
        break_on_hyphens=False,
    ) or [""]
    line_count = len(greedy_lines)
    if line_count == 1:
        return greedy_lines

    # Once wrapping is necessary, avoid a nearly full first line followed by
    # an orphaned word. Choose word-boundary breaks whose line lengths are as
    # even as possible while retaining the minimum number of lines.
    target = (sum(map(len, words)) + len(words) - line_count) / line_count
    no_line_end = {
        "a", "an", "the", "and", "or", "but", "as", "at", "by", "for",
        "from", "in", "into", "of", "on", "per", "than", "to", "via",
        "vs", "with", "without",
    }

    def break_penalty(end: int, line: str) -> float:
        penalty = 0.0
        if len(line.split()) == 1 and len(words) > line_count:
            penalty += 10_000.0
        if end < len(words):
            # Do not strand a preposition, article, or conjunction at a line
            # ending. Keep it attached to the phrase that follows.
            if words[end - 1].rstrip(".,:;!?").casefold() in no_line_end:
                penalty += 1_000_000.0
            # Keep calendar expressions such as "Aug 2026" together.
            if re.fullmatch(
                r"(?i:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
                r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|"
                r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?,?",
                words[end - 1],
            ) and re.fullmatch(r"\d{4}", words[end]):
                penalty += 1_000_000.0
        return penalty

    states: dict[tuple[int, int], tuple[float, list[str]]] = {(0, 0): (0.0, [])}
    for used_lines in range(line_count):
        for start in range(len(words)):
            state = states.get((used_lines, start))
            if state is None:
                continue
            cost, lines = state
            for end in range(start + 1, len(words) + 1):
                line = " ".join(words[start:end])
                if len(line) > max_chars and end > start + 1:
                    break
                remaining_words = len(words) - end
                remaining_lines = line_count - used_lines - 1
                if remaining_words < remaining_lines:
                    continue
                if remaining_lines == 0 and remaining_words:
                    continue
                new_cost = cost + math.pow(len(line) - target, 2) + break_penalty(end, line)
                key = (used_lines + 1, end)
                if key not in states or new_cost < states[key][0]:
                    states[key] = (new_cost, [*lines, line])

    return states.get((line_count, len(words)), (0.0, greedy_lines))[1]


def by_id(root: ET.Element, element_id: str) -> ET.Element | None:
    return next((el for el in root.iter() if el.get("id") == element_id), None)


def parent_map(root: ET.Element) -> dict[ET.Element, ET.Element]:
    return {child: parent for parent in root.iter() for child in parent}


def remove_id(root: ET.Element, element_id: str) -> None:
    element = by_id(root, element_id)
    if element is None:
        return
    parent = parent_map(root).get(element)
    if parent is not None:
        parent.remove(element)


def prefix_chart_ids(root: ET.Element, prefix: str = "embedded_chart_") -> None:
    id_map: dict[str, str] = {}
    for element in root.iter():
        old = element.get("id")
        if old:
            new = prefix + old
            id_map[old] = new
            element.set("id", new)

    for element in root.iter():
        for key, value in list(element.attrib.items()):
            for old, new in id_map.items():
                value = value.replace(f"url(#{old})", f"url(#{new})")
                if value == f"#{old}":
                    value = f"#{new}"
            element.set(key, value)
        if element.text and "url(#" in element.text:
            for old, new in id_map.items():
                element.text = element.text.replace(f"url(#{old})", f"url(#{new})")


def add_multiline_text(
    parent: ET.Element,
    *,
    element_id: str,
    text: str,
    x: float,
    y: float,
    size: float,
    max_width: float,
    color: str,
    weight: int,
    anchor: str,
    line_height: float | None = None,
) -> ET.Element:
    max_chars = max(1, int(max_width / (size * 0.52)))
    try:  # 실제 Pretendard 폭으로 계산 (상수 0.52는 넓게 잡혀 한 줄짜리 제목이 꺾인다)
        from PIL import ImageFont
        font_file = {700: "Pretendard-Bold.ttf", 600: "Pretendard-SemiBold.ttf"}.get(weight, "Pretendard-Medium.ttf")
        font = ImageFont.truetype(str(Path("assets/font/Pretendard") / font_file), int(size))
        avg = font.getlength(text) / max(1, len(text))
        max_chars = max(1, int(max_width / avg))
    except Exception:
        pass
    lines: list[str] = []
    for paragraph in text.splitlines() or [text]:
        lines.extend(balanced_wrap(paragraph, max_chars))
    line_height = line_height or size * 1.2
    start_y = y - (len(lines) - 1) * line_height / 2

    group = ET.SubElement(parent, SVG + "g", {"id": element_id})
    text_el = ET.SubElement(
        group,
        SVG + "text",
        {
            "x": f"{x:g}",
            "y": f"{start_y:g}",
            "fill": color,
            "font-family": FONT_FAMILY,
            "font-size": f"{size:.2f}",
            "font-weight": str(weight),
            "text-anchor": anchor,
        },
    )
    for index, line in enumerate(lines):
        tspan = ET.SubElement(
            text_el,
            SVG + "tspan",
            {
                "x": f"{x:g}",
                "dy": "0" if index == 0 else f"{line_height:.2f}",
            },
        )
        tspan.text = line
    return group


def replace_footer_value(
    root: ET.Element,
    *,
    group_id: str,
    placeholder_id: str,
    element_id: str,
    value: str,
    x: float,
    y: float,
    width: float,
) -> None:
    """Replace only a footer value while preserving fixed template assets."""
    group = by_id(root, group_id)
    placeholder = by_id(root, placeholder_id)
    if group is None or placeholder is None or placeholder not in set(group.iter()):
        raise ValueError(
            f"template is missing footer placeholder {placeholder_id!r} "
            f"inside {group_id!r}"
        )
    parent = parent_map(root).get(placeholder)
    if parent is None:
        raise ValueError(f"footer placeholder {placeholder_id!r} has no parent")
    index = list(parent).index(placeholder)
    parent.remove(placeholder)
    value_group = add_multiline_text(
        ET.Element("placeholder"),
        element_id=element_id,
        text=value,
        x=x,
        y=y,
        size=28,
        max_width=width,
        color="#777B80",
        weight=500,
        anchor="start",
    )
    parent.insert(index, value_group)


def parse_legend_items(specs: list[str], allow_many: bool = False) -> list[LegendItem]:
    items: list[LegendItem] = []
    for spec in specs:
        try:
            label, color, style = (part.strip() for part in spec.rsplit("|", 2))
        except ValueError as exc:
            raise ValueError(
                f"invalid legend {spec!r}; use LABEL|#RRGGBB|STYLE"
            ) from exc
        style = style.lower()
        if not label:
            raise ValueError("legend label must not be empty")
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
            raise ValueError(f"invalid legend color {color!r}; use #RRGGBB")
        if style not in {"line", "dashed", "square"}:
            raise ValueError(
                f"invalid legend style {style!r}; use line, dashed, or square"
            )
        items.append(
            LegendItem(
                label=uppercase_word_initials(label),
                color=color.upper(),
                style=style,
            )
        )
    if allow_many:  # 합산 불가 지표(수수료 등)에서 사용자가 시리즈를 직접 고른 경우
        return items
    if len(items) > MAX_LEGEND_ITEMS:
        raise ValueError("legend supports at most five series plus Others")
    if len(items) == MAX_LEGEND_ITEMS and not any(
        item.label.casefold() == "others" for item in (items[0], items[-1])
    ):
        raise ValueError(
            "a six-item legend must put Others at one edge of the legend order"
        )
    return items


def legend_item_size(item: LegendItem) -> tuple[float, float]:
    text_width = max(40.0, len(item.label) * LEGEND_FONT_SIZE * 0.56)
    if item.style == "square":
        return 43.0 + text_width, max(LEGEND_SQUARE_SIZE, LEGEND_FONT_SIZE)
    return max(53.0, text_width), 54.0


def add_legend_item(
    parent: ET.Element,
    item: LegendItem,
    *,
    x: float,
    y: float,
    side_layout: bool,
) -> None:
    item_center_y = max(LEGEND_SQUARE_SIZE, LEGEND_FONT_SIZE) / 2
    centered_text_baseline_y = (
        item_center_y + LEGEND_FONT_SIZE * PRETENDARD_CAP_HEIGHT_RATIO / 2
    )
    item_group = ET.SubElement(
        parent,
        SVG + "g",
        {"aria-label": item.label, "transform": f"translate({x:g} {y:g})"},
    )
    if item.style == "square":
        square_y = item_center_y - LEGEND_SQUARE_SIZE / 2
        ET.SubElement(
            item_group,
            SVG + "rect",
            {
                "y": f"{square_y:g}",
                "width": f"{LEGEND_SQUARE_SIZE:g}",
                "height": f"{LEGEND_SQUARE_SIZE:g}",
                "rx": "6",
                "fill": item.color,
            },
        )
        text_x, text_y = 43.0, centered_text_baseline_y
    elif item.style == "dashed":
        line_y = item_center_y if side_layout else 5.0
        ET.SubElement(
            item_group,
            SVG + "path",
            {
                "d": f"M6 {line_y:g}H53",
                "fill": "none",
                "stroke": item.color,
                "stroke-width": f"{LEGEND_DASH_STROKE:g}",
                "stroke-linecap": "round",
                "stroke-dasharray": "8 11",
            },
        )
        text_x, text_y = (
            (70.0, centered_text_baseline_y)
            if side_layout
            else (1.0, 53.0)
        )
    else:
        line_y = item_center_y - LEGEND_LINE_HEIGHT / 2 if side_layout else 1.0
        ET.SubElement(
            item_group,
            SVG + "rect",
            {
                "x": "1",
                "y": f"{line_y:g}",
                "width": f"{LEGEND_LINE_WIDTH:g}",
                "height": f"{LEGEND_LINE_HEIGHT:g}",
                "rx": "4",
                "fill": item.color,
            },
        )
        text_x, text_y = (
            (70.0, centered_text_baseline_y)
            if side_layout
            else (1.0, 53.0)
        )
    text_attributes = {
        "x": f"{text_x:g}",
        "y": f"{text_y:g}",
        "fill": "#D1D5DB",
        "font-family": FONT_FAMILY,
        "font-size": f"{LEGEND_FONT_SIZE:g}",
        "font-weight": "500",
    }
    label = ET.SubElement(item_group, SVG + "text", text_attributes)
    label.text = item.label


def make_bottom_legend(items: list[LegendItem]) -> tuple[ET.Element, float]:
    if not items:
        raise ValueError("bottom legend requires at least one item")

    item_gap = 50.0  # 오른쪽형과 동일 간격
    row_gap = 14.0
    rows: list[list[tuple[LegendItem, float, float]]] = []
    row: list[tuple[LegendItem, float, float]] = []
    row_width = 0.0
    for item in items:
        width, height = legend_item_size(item)
        next_width = width if not row else row_width + item_gap + width
        if row and next_width > LEGEND_WIDTH:
            rows.append(row)
            row = []
            row_width = 0.0
        row.append((item, width, height))
        row_width = width if len(row) == 1 else row_width + item_gap + width
    if row:
        rows.append(row)

    group = ET.Element(SVG + "g", {"id": "Dynamic Legend"})
    y = LEGEND_TOP
    for row_items in rows:
        row_width = sum(width for _, width, _ in row_items) + item_gap * (len(row_items) - 1)
        row_height = max(height for _, _, height in row_items)
        x = LEGEND_LEFT + (LEGEND_WIDTH - row_width) / 2
        for item, width, height in row_items:
            item_y = y + (row_height - height) / 2
            add_legend_item(group, item, x=x, y=item_y, side_layout=False)
            x += width + item_gap
        y += row_height + row_gap
    return group, y - row_gap


def make_right_legend(
    items: list[LegendItem],
    *,
    legend_x: float,
    plot_top: float,
    plot_height: float,
) -> ET.Element:
    if not items:
        raise ValueError("right legend requires at least one item")
    item_height = max(LEGEND_SQUARE_SIZE, LEGEND_FONT_SIZE)
    if len(items) == MAX_LEGEND_ITEMS:
        step = (plot_height - item_height) / (len(items) - 1)
    else:
        step = item_height + 50.0

    group = ET.Element(
        SVG + "g",
        {"id": "Dynamic Legend", "data-position": "right"},
    )
    for index, item in enumerate(items):
        add_legend_item(
            group,
            item,
            x=legend_x,
            y=plot_top + index * step,
            side_layout=True,
        )
    return group


def chart_geometry(chart_path: Path) -> tuple[float, float, float, float]:
    root = ET.parse(chart_path).getroot()
    view_box = root.get("viewBox")
    if not view_box:
        raise ValueError(f"{chart_path}: chart SVG has no viewBox")
    parts = view_box.replace(",", " ").split()
    if len(parts) != 4:
        raise ValueError(f"{chart_path}: invalid viewBox {view_box!r}")
    width, height = float(parts[2]), float(parts[3])
    if width <= 0 or height <= 0:
        raise ValueError(f"{chart_path}: viewBox width and height must be positive")

    clip_rects: list[tuple[float, float, float, float]] = []
    for clip_path in root.iter(SVG + "clipPath"):
        for rect in clip_path.iter(SVG + "rect"):
            try:
                rect_x = float(rect.get("x", "0"))
                rect_y = float(rect.get("y", "0"))
                rect_width = float(rect.get("width", "0"))
                rect_height = float(rect.get("height", "0"))
            except ValueError:
                continue
            if rect_width > 0 and rect_height > 0:
                clip_rects.append((rect_x, rect_y, rect_width, rect_height))

    if clip_rects:
        _, plot_y, _, plot_height = max(
            clip_rects,
            key=lambda rect: rect[2] * rect[3],
        )
    else:
        plot_y, plot_height = 0.0, height
    return width, height, plot_y, plot_height


def chart_y_label_left(chart_path: Path) -> float:
    root = ET.parse(chart_path).getroot()
    candidates: list[float] = []
    for tick in root.iter():
        tick_id = tick.get("id", "")
        if not tick_id.startswith("ytick_"):
            continue
        for element in tick.iter():
            transform = element.get("transform", "")
            match = re.search(r"translate\(\s*([-+0-9.eE]+)[ ,]", transform)
            if match:
                candidates.append(float(match.group(1)))
    return min(candidates, default=0.0)


def chart_coordinate_x(
    chart_path: Path,
    chart_slot: tuple[float, float, float, float],
    source_x: float,
) -> float:
    view_width, view_height, _, _ = chart_geometry(chart_path)
    slot_x, _, slot_width, slot_height = chart_slot
    scale = min(slot_width / view_width, slot_height / view_height)
    rendered_width = view_width * scale
    horizontal_offset = (slot_width - rendered_width) / 2
    return slot_x + horizontal_offset + source_x * scale


def right_chart_layout(
    chart_path: Path,
) -> tuple[tuple[float, float, float, float], float, float, float]:
    view_width, view_height, plot_y, plot_height = chart_geometry(chart_path)
    scale = min(
        RIGHT_CHART_MAX_WIDTH / view_width,
        RIGHT_CHART_MAX_HEIGHT / view_height,
    )
    chart_width = view_width * scale
    chart_height = view_height * scale
    chart_slot = (RIGHT_CHART_LEFT, RIGHT_CHART_TOP, chart_width, chart_height)
    legend_x = RIGHT_CHART_LEFT + chart_width + RIGHT_LEGEND_GAP
    plot_top = RIGHT_CHART_TOP + plot_y * scale
    return chart_slot, legend_x, plot_top, plot_height * scale


def embed_chart(
    main: ET.Element,
    chart_path: Path,
    chart_slot: tuple[float, float, float, float],
) -> ET.Element:
    chart_root = ET.parse(chart_path).getroot()
    view_box = chart_root.get("viewBox")
    if not view_box:
        raise ValueError(f"{chart_path}: chart SVG has no viewBox")
    parts = view_box.replace(",", " ").split()
    if len(parts) != 4:
        raise ValueError(f"{chart_path}: invalid viewBox {view_box!r}")

    prefix_chart_ids(chart_root)
    x, y, width, height = chart_slot
    nested = ET.Element(
        SVG + "svg",
        {
            "id": "Embedded Chart",
            "x": f"{x:g}",
            "y": f"{y:g}",
            "width": f"{width:g}",
            "height": f"{height:g}",
            "viewBox": " ".join(parts),
            "preserveAspectRatio": "xMidYMid meet",
            "overflow": "hidden",
        },
    )
    for child in chart_root:
        nested.append(copy.deepcopy(child))

    children = list(main)
    bg_index = next(
        (index for index, child in enumerate(children) if child.get("id") == "Bg Image"),
        0,
    )
    main.insert(bg_index + 1, nested)
    return nested


def assemble(args: argparse.Namespace) -> tuple[Path, Path]:
    template = args.template.resolve()
    chart = args.chart.resolve()
    output = args.output.resolve()

    for path, kind in ((template, "template"), (chart, "chart")):
        if not path.is_file():
            raise FileNotFoundError(f"{kind} SVG not found: {path}")
    if not args.source.strip():
        raise ValueError("source is required and must not be guessed")
    if not args.date.strip():
        raise ValueError("date is required and must come from the chart data")
    if re.search(r"\s(?:~|–|—|to)\s", args.date, flags=re.IGNORECASE):
        raise ValueError("Date as of must contain only the data end date, not a range")

    tree = ET.parse(template)
    root = tree.getroot()
    main = by_id(root, "Inforgraphic Template for Graph_H:1080px")
    footer = by_id(root, "Footer Info")
    if main is None or footer is None:
        raise ValueError("template is missing its main or footer group")
    logo = by_id(root, "Group 1991501008")
    if logo is None:
        raise ValueError("template is missing its fixed Four Pillars logo group")
    original_logo = ET.tostring(logo)

    remove_id(root, "Title_1 line")
    remove_id(root, "Title 1 line_2")
    if not args.note:
        remove_id(root, "Note")

    legend_items = parse_legend_items(args.legend, allow_many=args.allow_many_legend)
    legend_position = args.legend_position
    if legend_items and legend_position == "auto":
        view_width, view_height, _, _ = chart_geometry(chart)
        legend_position = (
            "bottom"
            if view_width / view_height >= BOTTOM_LEGEND_RATIO
            else "right"
        )

    legend_group: ET.Element | None = None
    chart_slot = BASE_CHART_SLOT
    if legend_items and legend_position == "bottom":
        legend_group, legend_bottom = make_bottom_legend(legend_items)
        if legend_bottom > 940.0:
            raise ValueError(
                "bottom legend is too tall; shorten labels or use right placement"
            )
        chart_slot = BOTTOM_CHART_SLOT
        if not args.subtitle:  # 부제목 없으면 비는 영역만큼 차트를 위로 키운다
            x0, y0, w, h = chart_slot
            chart_slot = (x0, 220.0, w, h + y0 - 220.0)
        legend_group.set("data-position", "bottom")
    elif legend_items and legend_position == "right":
        chart_slot, legend_x, plot_top, plot_height = right_chart_layout(chart)
        legend_group = make_right_legend(
            legend_items,
            legend_x=legend_x,
            plot_top=plot_top,
            plot_height=plot_height,
        )

    if args.chart_size:  # 슬롯에 맞춰 확대하지 않고 지정 px 크기로 (왼쪽 정렬, 세로 가운데)
        x0, y0, w, h = chart_slot
        cw, ch = args.chart_size
        chart_slot = (x0, y0 + (h - ch) / 2, cw, ch)

    subtitle_x = chart_coordinate_x(chart, chart_slot, chart_y_label_left(chart))

    embed_chart(main, chart, chart_slot)

    footer_index = list(main).index(footer)
    title_group = add_multiline_text(
        ET.Element("placeholder"),
        element_id="Dynamic Title",
        text=uppercase_word_initials(args.title),
        x=960,
        y=123,
        size=50,
        max_width=1500,
        color="#E6E6E6",
        weight=700,
        anchor="middle",
    )
    main.insert(footer_index, title_group)
    footer_index += 1
    subtitle_group = None if not args.subtitle else add_multiline_text(
        ET.Element("placeholder"),
        element_id="Dynamic Subtitle",
        text=uppercase_word_initials(args.subtitle),
        x=subtitle_x,
        y=257,
        size=38,
        max_width=1450,
        color="#CBCBCB",
        weight=500,
        anchor="start",
    )
    if subtitle_group is not None:
        main.insert(footer_index, subtitle_group)
        footer_index += 1
    if legend_group is not None:
        main.insert(footer_index, legend_group)

    replace_footer_value(
        root,
        group_id="Source",
        placeholder_id="Chainlink, Four Pillars",
        element_id="Dynamic Source Value",
        value=args.source,
        x=SOURCE_VALUE_POSITION[0],
        y=SOURCE_VALUE_POSITION[1],
        width=800,
    )
    replace_footer_value(
        root,
        group_id="Data as of",
        placeholder_id="jan 01, 2025 ~",
        element_id="Dynamic Date Value",
        value=args.date,
        x=DATE_VALUE_POSITION[0],
        y=DATE_VALUE_POSITION[1],
        width=350,
    )
    if args.note:
        replace_footer_value(
            root,
            group_id="Note",
            placeholder_id="Title 1 line",
            element_id="Dynamic Note Value",
            value=args.note,
            x=NOTE_VALUE_POSITION[0],
            y=NOTE_VALUE_POSITION[1],
            width=1100,
        )

    if ET.tostring(by_id(root, "Group 1991501008")) != original_logo:
        raise ValueError("fixed Four Pillars logo position or geometry changed")

    output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output, encoding="utf-8", xml_declaration=True)

    renderer = shutil.which("rsvg-convert")
    if not renderer:
        raise RuntimeError("rsvg-convert is required to render the PNG preview")
    png = output.with_suffix(".png")
    subprocess.run(
        [renderer, "-w", str(args.preview_width), "-o", str(png), str(output)],
        check=True,
    )
    return output, png


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chart", type=Path, help="transparent chart SVG")
    parser.add_argument("output", type=Path, help="final infographic SVG")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--source", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--note")
    parser.add_argument("--allow-many-legend", action="store_true",
                        help="상위5+Others 규칙 대신 전달된 시리즈를 그대로 범례로 사용")
    parser.add_argument("--chart-size", type=float, nargs=2, metavar=("W", "H"),
                        help="차트를 슬롯에 맞춰 키우지 않고 이 px 크기로 배치")
    parser.add_argument(
        "--legend",
        action="append",
        default=[],
        metavar="LABEL|#RRGGBB|STYLE",
        help="repeat per series; STYLE is line, dashed, or square",
    )
    parser.add_argument(
        "--legend-position",
        choices=("auto", "right", "bottom"),
        default="auto",
        help="auto puts wide, shallow charts below and uses the right side otherwise",
    )
    parser.add_argument("--preview-width", type=int, default=1920)
    return parser.parse_args()


def main() -> int:
    try:
        output, png = assemble(parse_args())
    except (ET.ParseError, OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ASSEMBLY_FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"SVG: {output}")
    print(f"PNG: {png}")
    print("STATUS: RENDERED, visual QA required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
