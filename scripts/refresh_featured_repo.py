"""Refresh the latest public project and its detected languages."""

import hashlib
import json
from html import escape
from textwrap import shorten
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from render_readme_cards import ROOT, project_card

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


def latest_public_repo(owner):
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
                return repo
        if len(repos) < 100:
            return None
        page += 1


def top_languages(repo):
    name = quote(repo["name"], safe="")
    sizes = github_json(f"/repos/{OWNER}/{name}/languages")
    return sorted(sizes, key=lambda language: (-sizes[language], language.casefold()))[:5]


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
    repo = latest_public_repo(OWNER)
    languages = top_languages(repo) if repo else []
    update_readme(ROOT / "README.md", ROOT / "cards/ivory", repo, languages)
    print(f"Latest public project: {repo['name']}" if repo else "No public project found.")


if __name__ == "__main__":
    main()
