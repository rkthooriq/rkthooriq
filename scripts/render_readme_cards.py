"""Render the README SVG cards from the saved GitHub contribution calendar."""

import argparse
import json
import os
from collections import Counter
from datetime import date, timedelta
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = os.environ.get("STATIC") == "1"
MONTHS = ("Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des")
HEAT = ("#242e35", "#28554f", "#328473", "#47b69c", "#82e3c0")
STYLE = """
    text { font-family: system-ui, sans-serif; fill: #edf3f1; }
    .mono { font-family: ui-monospace, monospace; letter-spacing: 1.25px; }
    .muted { fill: #a6b5b9; }
    .mint { fill: #82e3c0; }
    .amber { fill: #f3c580; }
    .blue { fill: #a5c9ff; }
"""
MOTION = """
    @media (prefers-reduced-motion: no-preference) {
      .enter { animation: enter 520ms cubic-bezier(.2,.65,.3,1) both; }
      .cell { animation: reveal 420ms ease-out both; }
      .bar { animation: grow 520ms ease-out both; transform-origin: center bottom;
             transform-box: fill-box; }
      @keyframes enter { from { opacity: 0; transform: translateY(8px); } }
      @keyframes reveal { from { opacity: 0; } }
      @keyframes grow { from { transform: scaleY(0); } }
    }
"""


def text(x, y, label, size, *, style="", weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" class="{style}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{escape(str(label))}</text>')


def rect(x, y, width, height, fill, radius=0, stroke="none"):
    return (f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}"/>')


def line(x1, y1, x2, y2, stroke="#303e46"):
    return f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{stroke}"/>'


def animate(content, delay, kind="enter"):
    if STATIC:
        return content
    return f'<g class="{kind}" style="animation-delay:{delay}ms">{content}</g>'


def svg(width, height, title, description, content):
    style = STYLE if STATIC else STYLE + MOTION
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
  <title id="title">{escape(title)}</title>
  <desc id="description">{escape(description)}</desc>
  <style>{style}  </style>
  {rect(0.5, 0.5, width - 1, height - 1, "#12191e", 16, "#303e46")}
  {content}
</svg>
'''


def hero():
    identity = (
        text(34, 40, "CATATAN BELAJAR SISTEM", 13, style="mono mint", weight=700)
        + text(32, 100, "Raditya Kemal", 54, weight=750)
        + text(32, 157, "Thooriq", 54, weight=750)
        + text(35, 197, "Sistem komputer dan praktik Linux", 22, style="muted")
        + text(35, 236, "@rkthooriq", 15, style="mono mint")
    )
    diagram = rect(598, 31, 248, 206, "#171f25", 10, "#334149")
    labels = ("Hardware", "Sistem operasi", "Aplikasi")
    for index, (label, color) in enumerate(zip(labels, (HEAT[4], "#a5c9ff", "#f3c580"))):
        y = 48 + index * 62
        node = (
            rect(620, y, 204, 42, "#202b32", 6)
            + rect(634, y + 17, 8, 8, color, 2)
            + text(654, y + 26, label, 15, style="mono")
        )
        if index < len(labels) - 1:
            node += line(639, y + 42, 639, y + 62, "#667981")
        diagram += animate(node, 180 + index * 110)
    return svg(880, 268, "Raditya Kemal Thooriq", "Catatan belajar sistem komputer dan praktik Linux.",
               animate(identity, 0) + diagram)


def short_date(day):
    return f"{day.day} {MONTHS[day.month - 1]}"


def heatmap(days):
    start = min(days)
    end = max(days)
    start_offset = (start.weekday() + 1) % 7
    total = sum(days.values())
    end_label = f"{short_date(start)} {start.year} – {short_date(end)} {end.year}"
    content = (
        text(34, 38, "KONTRIBUSI GITHUB", 13, style="mono mint", weight=700)
        + text(33, 81, f"{total:,} kontribusi", 37, weight=740)
        + text(846, 79, end_label, 14, style="mono muted", anchor="end")
        + line(34, 101, 846, 101)
    )
    for y, label in ((150, "Sen"), (180, "Rab"), (210, "Jum")):
        content += text(34, y, label, 12, style="mono muted")

    last_label_column = -5
    peak = max(days.values())
    for day, count in days.items():
        week, row = divmod(start_offset + (day - start).days, 7)
        x, y = 80 + week * 14.5, 126 + row * 15
        if (day == start or day.day == 1) and week - last_label_column >= 3:
            content += text(x, 119, MONTHS[day.month - 1], 11, style="mono muted")
            last_label_column = week
        shade = 0 if count == 0 else min(4, (4 * count + peak - 1) // peak)
        content += animate(rect(x, y, 11, 11, HEAT[shade], 2), 420 + week * 11, "cell")

    content += text(678, 257, "Sedikit", 12, style="muted")
    for index, color in enumerate(HEAT):
        content += rect(728 + index * 15, 247, 11, 11, color, 2)
    content += text(847, 257, "Banyak", 12, style="muted", anchor="end")
    return svg(880, 276, "Kalender kontribusi GitHub", f"{total} kontribusi, {end_label} UTC.", content)


def monthly(days):
    totals = Counter()
    streak = longest = active = 0
    peak_day = max(days, key=days.get)
    for day, count in days.items():
        totals[day.replace(day=1)] += count
        active += count > 0
        streak = streak + 1 if count else 0
        longest = max(longest, streak)

    peak_month = max(totals, key=totals.get)
    peak_count = totals[peak_month]
    ceiling = max(peak_count, 1)
    content = (
        text(34, 38, "RINGKASAN AKTIVITAS", 13, style="mono blue", weight=700)
        + text(33, 77, "Kontribusi per bulan", 32, weight=730)
        + text(846, 76, "365 HARI", 13, style="mono muted", anchor="end")
        + line(34, 190, 846, 190)
    )
    for index, (month, count) in enumerate(totals.items()):
        x = 34 + (index + 0.5) * (812 / len(totals))
        height = round(64 * count / ceiling)
        color = "#a5c9ff" if count and month == peak_month else "#547b9b"
        if count:
            content += animate(rect(round(x - 13, 1), 190 - max(height, 2), 26,
                                    max(height, 2), color, 3), 850 + index * 34, "bar")
        if count and month == peak_month:
            content += animate(text(round(x, 1), 181 - max(height, 2), count, 13,
                                    style="mono blue", anchor="middle"), 1230)
        content += text(round(x, 1), 212, MONTHS[month.month - 1], 12, style="mono muted",
                        anchor="middle")
    content += line(34, 233, 846, 233)

    peak = days[peak_day]
    peak_label = f"{short_date(peak_day)} · {peak:,}" if peak else "—"
    metrics = (
        ("Hari aktif", f"{active} hari"),
        ("Rentetan terpanjang", f"{longest} hari"),
        ("Hari tersibuk", peak_label),
    )
    for index, (label, value) in enumerate(metrics):
        x = 34 + index * 270
        content += text(x, 260, label, 14, style="muted")
        content += text(x, 290, value, 25, weight=720)

    return svg(880, 313, "Kontribusi per bulan",
               f"{active} hari aktif. Rentetan terpanjang {longest} hari. "
               f"Hari tersibuk {peak_label}. Bulan di ujung grafik dapat berupa bulan parsial.",
               content)


def project():
    content = (
        text(34, 35, "REPO BELAJAR", 13, style="mono amber", weight=700)
        + text(33, 77, "Computer Systems Fundamentals", 37, weight=730)
        + text(34, 109, "Dari hardware dan sistem operasi hingga jaringan, dengan lab terminal.",
               19, style="muted")
        + text(846, 76, "↗", 32, style="amber", anchor="end")
    )
    return svg(880, 137, "Computer Systems Fundamentals", "Repositori catatan belajar dan lab praktik.",
               animate(content, 1240))


def tile(title, lines, accent, delay):
    content = (
        rect(20, 23, 26, 3, {"mint": HEAT[4], "blue": "#a5c9ff", "amber": "#f3c580"}[accent], 1)
        + text(20, 62, title, 33, weight=730)
        + text(254, 61, "↗", 24, style=accent, anchor="end")
        + text(20, 91, lines[0], 20, style="muted")
        + text(20, 116, lines[1], 20, style="muted")
    )
    return svg(280, 137, title, " ".join(lines), animate(content, delay))


def read_days(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    start = date.fromisoformat(payload["start"])
    end = date.fromisoformat(payload["end"])
    if payload["login"] != "rkthooriq" or end - start != timedelta(days=364):
        raise ValueError("Expected a 365-day calendar for rkthooriq")
    days = {date.fromisoformat(key): value for key, value in payload["days"].items()}
    expected = {start + timedelta(days=index) for index in range(365)}
    if days.keys() != expected or any(type(count) is not int or count < 0 for count in days.values()):
        raise ValueError("The calendar must have one non-negative integer count per day")
    return dict(sorted(days.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data/contributions.json")
    parser.add_argument("--output", type=Path, default=ROOT / "cards")
    args = parser.parse_args()
    days = read_days(args.data)
    cards = {
        "hero": hero(),
        "calendar": heatmap(days),
        "monthly": monthly(days),
        "project": project(),
        "linux": tile("Linux", ("Shell dan izin akses", "Layanan systemd"), "mint", 1360),
        "network": tile("Jaringan", ("TCP/IP dan DNS", "Routing dan socket"), "blue", 1450),
        "labs": tile("Lab terminal", ("Eksperimen sistem", "Catat hasil observasi"), "amber", 1540),
    }
    args.output.mkdir(parents=True, exist_ok=True)
    for name, content in cards.items():
        (args.output / f"{name}.svg").write_text(content, encoding="utf-8")
    print(f"Rendered {len(cards)} {'static' if STATIC else 'animated'} SVG cards to {args.output}")


if __name__ == "__main__":
    main()
