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
IVORY = "#f1f3ce"
NAVY = "#00293c"
PEACOCK = "#1e656d"
RULE = "#cbd5b6"
HEAT = ("#dce5c8", "#9dbfb0", "#659e97", "#387e80", PEACOCK)
STYLE = f"""
    text {{ font-family: system-ui, sans-serif; fill: {NAVY}; }}
    .serif {{ font-family: Georgia, "Times New Roman", serif; }}
    .italic {{ font-style: italic; }}
    .mono {{ font-family: ui-monospace, monospace; letter-spacing: 1px; }}
    .muted {{ fill: #45605d; }}
    .accent {{ fill: {PEACOCK}; }}
    .light {{ fill: {IVORY}; }}
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


def line(x1, y1, x2, y2, stroke=RULE):
    return f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{stroke}"/>'


def animate(content, delay, kind="enter"):
    if STATIC:
        return content
    return f'<g class="{kind}" style="animation-delay:{delay}ms">{content}</g>'


def svg(width, height, title, description, content, *, background=IVORY):
    style = STYLE if STATIC else STYLE + MOTION
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
  <title id="title">{escape(title)}</title>
  <desc id="description">{escape(description)}</desc>
  <style>{style}  </style>
  {rect(0.5, 0.5, width - 1, height - 1, background, 16)}
  {content}
</svg>
'''


def hero():
    identity = (
        rect(41, 40, 8, 8, PEACOCK, 1)
        + text(62, 49, "CATATAN BELAJAR SISTEM", 12, style="mono muted")
        + text(36, 135, "Raditya Kemal", 76, style="serif")
        + text(38, 216, "Thooriq", 93, style="serif italic")
        + text(42, 267, "Sistem komputer dan praktik Linux.", 22)
        + text(42, 309, "@rkthooriq", 14, style="mono accent")
    )
    rows = (ROOT / "assets/portrait-rows.txt").read_text(encoding="utf-8").splitlines()
    portrait = "".join(
        animate(f'<path d="{escape(row, quote=True)}"/>', 130 + index * 13, "cell")
        for index, row in enumerate(rows)
        if row
    )
    portrait = (
        '<g transform="translate(552 28) scale(2.22)" fill="none" '
        f'stroke="{NAVY}" stroke-width=".64" stroke-linecap="round">'
        + portrait + "</g>"
    )
    return svg(880, 345, "Raditya Kemal Thooriq",
               "Potret dari avatar GitHub dan catatan belajar sistem komputer.",
               animate(identity, 0) + portrait)


def short_date(day):
    return f"{day.day} {MONTHS[day.month - 1]}"


def heatmap(days):
    start = min(days)
    end = max(days)
    start_offset = (start.weekday() + 1) % 7
    total = sum(days.values())
    end_label = f"{short_date(start)} {start.year} – {short_date(end)} {end.year}"
    content = (
        text(39, 54, "Jejak kontribusi", 41, style="serif")
        + text(841, 48, end_label, 12, style="mono muted", anchor="end")
    )

    last_label_column = -5
    peak = max(days.values())
    for day, count in days.items():
        week, row = divmod(start_offset + (day - start).days, 7)
        x, y = 41 + week * 15.15, 84 + row * 14.4
        if (day == start or day.day == 1) and week - last_label_column >= 3:
            content += text(x, 201, MONTHS[day.month - 1], 10, style="mono muted")
            last_label_column = week
        shade = 0 if count == 0 else min(4, (4 * count + peak - 1) // peak)
        content += animate(rect(x, y, 12, 12, HEAT[shade], 2), 420 + week * 11, "cell")

    content += text(669, 226, "Sedikit", 12, style="muted")
    for index, color in enumerate(HEAT):
        content += rect(717 + index * 15, 216, 11, 11, color, 2)
    content += text(841, 226, "Banyak", 12, style="muted", anchor="end")
    return svg(880, 244, "Kalender kontribusi GitHub", f"{total} kontribusi, {end_label} UTC.", content)


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
    total = sum(days.values())
    baseline = 230
    content = (
        text(40, 41, "365 HARI DI GITHUB", 12, style="mono muted")
        + text(38, 91, f"{total:,} kontribusi", 51, style="serif italic")
        + line(40, baseline, 573, baseline)
        + line(606, 38, 606, 270)
    )
    for index, (month, count) in enumerate(totals.items()):
        x = round(40 + (index + 0.5) * (533 / len(totals)), 1)
        height = max(3, round(104 * count / ceiling))
        highlight = count > 0 and month == peak_month
        color = PEACOCK if highlight else NAVY if count else RULE
        content += animate(rect(round(x - 13, 1), baseline - height, 26, height, color, 3),
                           850 + index * 34, "bar")
        if highlight:
            content += animate(text(x, baseline - height - 9, count, 13,
                                    style="mono accent", anchor="middle"), 1230)
        content += text(x, 254, MONTHS[month.month - 1], 11, style="mono muted",
                        anchor="middle")

    peak = days[peak_day]
    peak_label = f"{short_date(peak_day)} · {peak:,}" if peak else "—"
    metrics = (
        ("Hari aktif", f"{active} hari"),
        ("Rentetan terpanjang", f"{longest} hari"),
        ("Hari tersibuk", peak_label),
    )
    for index, (label, value) in enumerate(metrics):
        y = 74 + index * 77
        content += text(633, y, value, 39, style="serif")
        content += text(634, y + 24, label, 14, style="muted")
        if index < len(metrics) - 1:
            content += line(633, y + 38, 840, y + 38)

    return svg(880, 290, "Kontribusi per bulan",
               f"{total} kontribusi dalam 365 hari. {active} hari aktif. "
               f"Rentetan terpanjang {longest} hari. Hari tersibuk {peak_label}. "
               "Bulan di ujung grafik dapat berupa bulan parsial.",
               content)


def project():
    content = (
        rect(39, 30, 8, 8, PEACOCK, 1)
        + text(58, 39, "REPO BELAJAR", 12, style="mono muted")
        + text(38, 79, "Computer Systems Fundamentals", 36, style="serif")
        + text(39, 111, "Dari hardware dan sistem operasi hingga jaringan, dengan lab terminal.",
               19, style="muted")
        + text(841, 77, "↗", 28, style="accent", anchor="end")
    )
    return svg(880, 137, "Computer Systems Fundamentals", "Repositori catatan belajar dan lab praktik.",
               animate(content, 1560))


def tile(title, lines, background, delay):
    content = (
        text(22, 69, title, 38, style="serif italic light")
        + text(254, 35, "↗", 21, style="light", anchor="end")
        + text(23, 105, lines[0], 17, style="light")
        + text(23, 131, lines[1], 17, style="light")
    )
    return svg(280, 157, title, " ".join(lines), animate(content, delay), background=background)


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
    parser.add_argument("--output", type=Path, default=ROOT / "cards" / "ivory")
    args = parser.parse_args()
    days = read_days(args.data)
    cards = {
        "hero": hero(),
        "calendar": heatmap(days),
        "monthly": monthly(days),
        "project": project(),
        "linux": tile("Linux", ("Shell dan izin akses", "Layanan systemd"), NAVY, 1300),
        "network": tile("Jaringan", ("TCP/IP dan DNS", "Routing dan socket"), PEACOCK, 1380),
        "labs": tile("Lab terminal", ("Eksperimen sistem", "Catat hasil observasi"), NAVY, 1460),
    }
    args.output.mkdir(parents=True, exist_ok=True)
    for name, content in cards.items():
        (args.output / f"{name}.svg").write_text(content, encoding="utf-8")
    print(f"Rendered {len(cards)} {'static' if STATIC else 'animated'} SVG cards to {args.output}")


if __name__ == "__main__":
    main()
