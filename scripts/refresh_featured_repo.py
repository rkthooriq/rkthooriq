"""Refresh the latest public project and its detected languages."""

import hashlib
import json
from collections import Counter
from html import escape
from textwrap import shorten
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from render_readme_cards import (HEAT, NAVY, PEACOCK, ROOT, animate, line,
                                 project_card, read_days, rect, svg, text)

OWNER = "rkthooriq"
API = "https://api.github.com"
START = "<!-- featured-repo:start -->\n"
END = "<!-- featured-repo:end -->"
CARD_PATTERN = "latest-project-*.svg"


def github_json(path):
    request = Request(
        API + path,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-readme-refresh"},
    )
    with urlopen(request, timeout=15) as response:
        return json.load(response)


def public_projects(owner):
    page = 1
    while True:
        query = urlencode({"type": "owner", "sort": "pushed", "direction": "desc",
                           "per_page": 100, "page": page})
        repos = github_json(f"/users/{owner}/repos?{query}")
        for repo in repos:
            if (repo["private"] is False and repo["visibility"] == "public"
                    and repo["owner"]["login"].casefold() == owner.casefold()
                    and repo["name"].casefold() != owner.casefold()
                    and not repo["fork"] and not repo["archived"]):
                yield repo
        if len(repos) < 100:
            return
        page += 1


def repository_languages(repo):
    name = quote(repo["name"], safe="")
    return github_json(f"/repos/{OWNER}/{name}/languages")


def ranked_languages(sizes):
    return sorted((name for name in sizes if sizes[name] > 0),
                  key=lambda name: (-sizes[name], name.casefold()))


def stats_card(repos, days):
    metrics = (
        ("Kontribusi · 365 hari", sum(days.values())),
        ("Hari aktif · 365 hari", sum(count > 0 for count in days.values())),
        ("Repo proyek publik", len(repos)),
        ("Bintang di repo proyek", sum(repo["stargazers_count"] for repo in repos)),
    )
    content = text(26, 51, "GitHub Stats", 36, style="serif")
    for index, (label, value) in enumerate(metrics):
        y = 93 + index * 36
        content += text(27, y, label, 17, style="muted")
        content += text(400, y, f"{value:,}", 22, style="serif", anchor="end")
        if index < len(metrics) - 1:
            content += line(27, y + 12, 400, y + 12)
    description = ". ".join(f"{label}: {value}" for label, value in metrics)
    return svg(426, 230, "GitHub Stats", description, animate(content, 150))


def languages_card(sizes):
    names = ranked_languages(sizes)
    top = [(name, sizes[name]) for name in names[:5]]
    other = sum(sizes[name] for name in names[5:])
    if other:
        top.append(("Lainnya", other))

    content = text(26, 51, "Most Used Languages", 34, style="serif")
    description = "GitHub belum mendeteksi bahasa."
    if top:
        total = sum(count for _, count in top)
        palette = (NAVY, PEACOCK, HEAT[3], HEAT[2], HEAT[1], HEAT[0])
        x = 27
        legend = []
        for index, (name, count) in enumerate(top):
            color = palette[index]
            width = 372 * count / total
            content += rect(round(x, 2), 70, round(width, 2), 12, color)
            x += width
            y = 110 + index * 18
            percent = f"{100 * count / total:.1f}%"
            content += rect(27, y - 10, 9, 9, color, 2)
            content += text(45, y, shorten(name, width=33, placeholder="…"), 14)
            content += text(399, y, percent, 14, style="mono", anchor="end")
            legend.append(f"{name} {percent}")
        description = "Persentase byte kode pada repo proyek publik. " + ", ".join(legend)
    else:
        content += text(27, 104, description, 16, style="muted")
    return svg(426, 230, "Most Used Languages", description, animate(content, 240))


def update_readme(readme_path, card_dir, repo, languages):
    readme = readme_path.read_text(encoding="utf-8")
    if readme.count(START) != 1 or readme.count(END) != 1 or readme.index(START) > readme.index(END):
        raise ValueError("README must contain one ordered pair of featured repository markers")
    before, _, rest = readme.partition(START)
    _, _, after = rest.partition(END)

    active_card = None
    block = ""
    if repo:
        name = repo["name"]
        title = shorten(name, width=35, placeholder="…")
        description = shorten(repo.get("description") or "Lihat proyek di GitHub.",
                              width=65, placeholder="…")
        svg = project_card(title, description, "PUSH TERBARU").encode("utf-8")
        digest = hashlib.sha256(svg).hexdigest()[:16]
        active_card = card_dir / f"latest-project-{digest}.svg"
        card_dir.mkdir(parents=True, exist_ok=True)
        active_card.write_bytes(svg)

        image = f"./{active_card.relative_to(readme_path.parent).as_posix()}"
        link = f"https://github.com/{OWNER}/{quote(name, safe='')}"
        alt = escape(f"{name} — {description}", quote=True)
        stack = " · ".join(f"<code>{escape(language)}</code>" for language in languages)
        if not stack:
            stack = "GitHub belum mendeteksi bahasa pada repo ini."
        block = (
            "\n## Repo publik terbaru\n\n"
            f'<a href="{link}"><img src="{image}" width="100%" alt="{alt}" /></a>\n\n'
            f"## Tech stack\n\n{stack}\n\n"
        )

    updated = before + START + block + END + after
    if updated != readme:
        readme_path.write_text(updated, encoding="utf-8")
    for old_card in card_dir.glob(CARD_PATTERN):
        if old_card != active_card:
            old_card.unlink()


def main():
    repos = list(public_projects(OWNER))
    repo = repos[0] if repos else None
    project_sizes = [repository_languages(project) for project in repos]
    languages = ranked_languages(project_sizes[0])[:5] if project_sizes else []
    total_sizes = Counter()
    for sizes in project_sizes:
        total_sizes.update(sizes)

    cards = ROOT / "cards/ivory"
    days = read_days(ROOT / "data/contributions.json")
    update_readme(ROOT / "README.md", cards, repo, languages)
    cards.mkdir(parents=True, exist_ok=True)
    (cards / "github-stats.svg").write_text(stats_card(repos, days), encoding="utf-8")
    (cards / "most-used-languages.svg").write_text(languages_card(total_sizes), encoding="utf-8")
    print(f"Latest public project: {repo['name']}" if repo else "No public project found.")


if __name__ == "__main__":
    main()
