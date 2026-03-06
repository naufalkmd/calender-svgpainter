from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError as exc:
    raise SystemExit("Pillow is required. Install it with: python -m pip install Pillow") from exc

ROOT = Path(__file__).resolve().parents[1]
CANVAS_PATH = ROOT / "painter" / "canvas.json"
OUTPUT_PATH = ROOT / "Assets" / "github-painter-banner.gif"

CELL_SIZE = 30
GAP = 2
PADDING = 6
STEP = CELL_SIZE + GAP
CORNER_RADIUS = 4

COLORS = {
    "1": (13, 68, 41, 255),
    "2": (1, 108, 49, 255),
    "3": (38, 166, 65, 255),
    "4": (57, 211, 83, 255),
}

FRAME_PLAN = [
    ("calm", 120),
    ("calm", 90),
    ("echo", 70),
    ("glitch", 45),
    ("glitch", 55),
    ("calm", 130),
    ("echo", 65),
    ("calm", 85),
    ("glitch", 45),
    ("glitch", 50),
    ("calm", 120),
    ("echo", 60),
    ("glitch", 45),
    ("calm", 140),
]

CANVAS_ROWS = 7
CANVAS_COLUMNS = 53


def normalize_rows(canvas: dict) -> list[str]:
    rows = []
    for row in canvas.get("grid", [])[:CANVAS_ROWS]:
        safe_row = "".join(char if char in ".1234" else "." for char in str(row))
        rows.append(safe_row[:CANVAS_COLUMNS].ljust(CANVAS_COLUMNS, "."))

    while len(rows) < CANVAS_ROWS:
        rows.append("." * CANVAS_COLUMNS)

    return rows


def compute_bounds(rows: list[str]) -> tuple[int, int, int, int]:
    active = [
        (column_index, row_index)
        for row_index, row in enumerate(rows)
        for column_index, symbol in enumerate(row)
        if symbol != "."
    ]
    if not active:
        raise SystemExit("painter/canvas.json does not contain any painted cells.")

    columns = [item[0] for item in active]
    row_indices = [item[1] for item in active]
    return min(columns), max(columns), min(row_indices), max(row_indices)


def build_base(rows: list[str]) -> tuple[Image.Image, list[tuple[int, int, str]], tuple[int, int, int, int]]:
    min_column, max_column, min_row, max_row = compute_bounds(rows)
    render_columns = max_column - min_column + 1
    render_rows = max_row - min_row + 1
    width = render_columns * STEP - GAP + (2 * PADDING)
    height = render_rows * STEP - GAP + (2 * PADDING)

    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    active_cells: list[tuple[int, int, str]] = []

    for row_index in range(min_row, max_row + 1):
        row = rows[row_index]
        for column_index in range(min_column, max_column + 1):
            symbol = row[column_index]
            if symbol == ".":
                continue

            x = PADDING + ((column_index - min_column) * STEP)
            y = PADDING + ((row_index - min_row) * STEP)
            draw.rounded_rectangle(
                (x, y, x + CELL_SIZE - 1, y + CELL_SIZE - 1),
                radius=CORNER_RADIUS,
                fill=COLORS[symbol],
            )
            active_cells.append((x, y, symbol))

    return image, active_cells, (min_column, max_column, min_row, max_row)


def alpha_mask(image: Image.Image, opacity: int) -> Image.Image:
    mask = image.getchannel("A")
    return mask.point(lambda value: (value * opacity) // 255)


def tint_from_alpha(image: Image.Image, color: tuple[int, int, int], opacity: int) -> Image.Image:
    layer = Image.new("RGBA", image.size, color + (0,))
    layer.putalpha(alpha_mask(image, opacity))
    return layer


def overlay_at(base: Image.Image, overlay: Image.Image, x: int, y: int) -> None:
    left = max(0, x)
    top = max(0, y)
    right = min(base.width, x + overlay.width)
    bottom = min(base.height, y + overlay.height)
    if left >= right or top >= bottom:
        return

    cropped = overlay.crop((left - x, top - y, right - x, bottom - y))
    base.alpha_composite(cropped, (left, top))


def shifted_band(frame: Image.Image, y: int, height: int, offset: int) -> Image.Image:
    band = frame.crop((0, y, frame.width, y + height))
    shifted = Image.new("RGBA", (frame.width, height), (0, 0, 0, 0))
    if offset >= 0:
        source_width = frame.width - offset
        if source_width > 0:
            shifted.alpha_composite(band.crop((0, 0, source_width, height)), (offset, 0))
    else:
        source_left = -offset
        if source_left < frame.width:
            shifted.alpha_composite(band.crop((source_left, 0, frame.width, height)), (0, 0))
    return shifted


def add_scanlines(draw: ImageDraw.ImageDraw, rng: random.Random, width: int, height: int) -> None:
    for _ in range(rng.randint(1, 3)):
        y = rng.randint(max(0, PADDING - 1), max(PADDING, height - PADDING - 2))
        alpha = rng.randint(18, 44)
        draw.line((0, y, width, y), fill=(255, 255, 255, alpha), width=1)


def add_sparkles(frame: Image.Image, active_cells: list[tuple[int, int, str]], rng: random.Random) -> None:
    if not active_cells:
        return

    draw = ImageDraw.Draw(frame)
    for x, y, symbol in rng.sample(active_cells, k=min(len(active_cells), rng.randint(2, 6))):
        sparkle_width = max(8, CELL_SIZE // 3)
        sparkle_x = x + rng.randint(2, max(2, CELL_SIZE - sparkle_width - 2))
        sparkle_y = y + rng.randint(2, max(2, CELL_SIZE - 8))
        sparkle_color = (255, 255, 255, 90 if symbol == "4" else 55)
        draw.rounded_rectangle(
            (sparkle_x, sparkle_y, sparkle_x + sparkle_width, sparkle_y + 4),
            radius=2,
            fill=sparkle_color,
        )


def make_frame(
    base: Image.Image,
    active_cells: list[tuple[int, int, str]],
    mode: str,
    frame_index: int,
    seed: int,
) -> Image.Image:
    rng = random.Random(seed + frame_index * 7919)
    frame = base.copy()

    if mode in {"echo", "glitch"}:
        left_echo = tint_from_alpha(base, (140, 255, 180), 72 if mode == "glitch" else 44)
        right_echo = tint_from_alpha(base, (0, 255, 163), 58 if mode == "glitch" else 30)
        overlay_at(frame, left_echo, -rng.randint(1, 4), rng.randint(-1, 1))
        overlay_at(frame, right_echo, rng.randint(1, 4), rng.randint(-1, 1))

    if mode == "glitch":
        glitched = frame.copy()
        for _ in range(rng.randint(2, 4)):
            band_height = rng.randint(max(10, CELL_SIZE // 2), max(12, CELL_SIZE + 6))
            band_y = rng.randint(0, max(0, frame.height - band_height))
            band_offset = rng.choice([-8, -6, -4, 4, 6, 8])
            glitched.paste(shifted_band(frame, band_y, band_height, band_offset), (0, band_y))

        frame = glitched
        draw = ImageDraw.Draw(frame)
        add_scanlines(draw, rng, frame.width, frame.height)
        add_sparkles(frame, active_cells, rng)

        if active_cells:
            for x, y, _ in rng.sample(active_cells, k=min(len(active_cells), rng.randint(1, 3))):
                draw.rounded_rectangle(
                    (x, y, x + CELL_SIZE - 1, y + CELL_SIZE - 1),
                    radius=CORNER_RADIUS,
                    fill=(255, 255, 255, 60),
                )

    return frame


def save_gif(frames: list[Image.Image], durations: list[int], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )


def main() -> None:
    canvas = json.loads(CANVAS_PATH.read_text(encoding="utf-8"))
    rows = normalize_rows(canvas)
    base, active_cells, _ = build_base(rows)

    seed_material = "\n".join(rows).encode("utf-8")
    seed = int(hashlib.sha256(seed_material).hexdigest()[:12], 16)

    frames = []
    durations = []
    for frame_index, (mode, duration) in enumerate(FRAME_PLAN):
        frames.append(make_frame(base, active_cells, mode, frame_index, seed))
        durations.append(duration)

    save_gif(frames, durations, OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
