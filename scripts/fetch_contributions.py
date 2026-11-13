"""Save the latest 365 complete UTC days from the public GitHub calendar."""

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
COUNT = re.compile(r"^(No|[0-9][0-9,]*) contributions? on\b")


class ContributionCalendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.counts = {}
        self.tooltip_for = None
        self.tooltip_text = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "td" and "ContributionCalendar-day" in attrs.get("class", "").split():
            cell_id = attrs["id"]
            day = date.fromisoformat(attrs["data-date"])
            if cell_id in self.cells:
                raise ValueError(f"Duplicate contribution cell for {day}")
            self.cells[cell_id] = day
        if tag == "tool-tip":
            self.tooltip_for = attrs.get("for")
            self.tooltip_text = []

    def handle_data(self, data):
        if self.tooltip_for:
            self.tooltip_text.append(data)

    def handle_endtag(self, tag):
        if tag != "tool-tip":
            return
        match = COUNT.match("".join(self.tooltip_text).strip())
        if match and self.tooltip_for:
            if self.tooltip_for in self.counts:
                raise ValueError(f"Duplicate contribution tooltip for {self.tooltip_for}")
            raw = match[1]
            self.counts[self.tooltip_for] = 0 if raw == "No" else int(raw.replace(",", ""))
        self.tooltip_for = None

    def read(self, document):
        self.feed(document)
        self.close()
        days = {}
        for cell_id, day in self.cells.items():
            if cell_id in self.counts:
                if day in days:
                    raise ValueError(f"Duplicate contribution date: {day}")
                days[day] = self.counts[cell_id]
        return days


def download_year(login, year):
    url = f"https://github.com/users/{login}/contributions?from={year}-01-01&to={year}-12-31"
    request = Request(url, headers={"User-Agent": "github-profile-readme-refresh",
                                    "Accept-Language": "en-US"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def build_snapshot(login, end, load_year=download_year):
    start = end - timedelta(days=364)
    counts = {}
    for year in range(start.year, end.year + 1):
        year_counts = ContributionCalendar().read(load_year(login, year))
        counts.update((day, count) for day, count in year_counts.items() if day.year == year)

    days = {}
    for offset in range(365):
        day = start + timedelta(days=offset)
        if day not in counts:
            raise ValueError(f"GitHub did not supply a contribution count for {day}")
        days[day.isoformat()] = counts[day]
    return {
        "login": login,
        "source": f"https://github.com/{login}",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "days": days,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("login")
    parser.add_argument("--end", type=date.fromisoformat, help="Last complete UTC date")
    parser.add_argument("--output", type=Path, default=ROOT / "data/contributions.json")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", args.login):
        parser.error("Invalid GitHub login")
    yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
    if args.end and args.end > yesterday:
        parser.error("--end must be a complete UTC date")

    try:
        snapshot = build_snapshot(args.login, args.end or yesterday)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.output.parent,
                                delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(snapshot, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary.replace(args.output)
    except (URLError, OSError, KeyError, ValueError) as error:
        sys.exit(f"Could not refresh the public GitHub calendar: {error}")
    print(f"Fetched {len(snapshot['days'])} days through {snapshot['end']} for @{args.login}")


if __name__ == "__main__":
    main()
