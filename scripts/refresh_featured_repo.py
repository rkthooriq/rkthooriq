"""Show one configured repository after GitHub confirms it is public."""

import json
import os
import re
from html import escape
from textwrap import shorten
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from render_readme_cards import ROOT, project_card

START = "<!-- featured-repo:start -->\n"
END = "<!-- featured-repo:end -->"


def public_repository(owner, name):
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", name) or name in (".", ".."):
        raise ValueError("FEATURED_REPOSITORY must contain only the repository name")
    request = Request(
        f"https://api.github.com/repos/{owner}/{name}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-readme-refresh"},
    )
    try:
        with urlopen(request, timeout=15) as response:
            repo = json.load(response)
    except HTTPError as error:
        if error.code == 404:
            return None
        raise
    if repo["private"] is not False or repo["visibility"] != "public":
        return None
    if repo["full_name"].casefold() != f"{owner}/{name}".casefold():
        raise ValueError("GitHub returned a different repository. Check FEATURED_REPOSITORY.")
    return repo


def update_featured_repo(readme_path, card_path, repo):
    readme = readme_path.read_text(encoding="utf-8")
    if readme.count(START) != 1 or readme.count(END) != 1 or readme.index(START) > readme.index(END):
        raise ValueError("README must contain one ordered pair of featured repository markers")
    before, _, rest = readme.partition(START)
    _, _, after = rest.partition(END)

    block = ""
    if repo:
        name = repo["name"]
        title = shorten(name, width=35, placeholder="…")
        description = shorten(repo.get("description") or "Lihat proyek di GitHub.",
                              width=65, placeholder="…")
        image = f"./{card_path.relative_to(readme_path.parent).as_posix()}"
        link = escape(f"https://github.com/{repo['full_name']}", quote=True)
        alt = escape(f"{name} — {description}", quote=True)
        block = f'\n<a href="{link}"><img src="{image}" width="100%" alt="{alt}" /></a>\n\n'
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(project_card(title, description, "PROYEK GITHUB"), encoding="utf-8")
    else:
        card_path.unlink(missing_ok=True)

    updated = before + START + block + END + after
    if updated != readme:
        readme_path.write_text(updated, encoding="utf-8")


def main():
    name = os.environ.get("FEATURED_REPOSITORY", "").strip()
    repo = public_repository("rkthooriq", name) if name else None
    update_featured_repo(ROOT / "README.md", ROOT / "cards/ivory/featured.svg", repo)


if __name__ == "__main__":
    main()
