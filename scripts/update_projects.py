#!/usr/bin/env python3
"""
Atualiza a seção "Projects" do README.md do perfil.

Lê os repositórios públicos do usuário, filtra os que têm o tópico
"portfolio" e reescreve o bloco entre os marcadores PROJECTS:START e
PROJECTS:END. Sem dependências externas — só a biblioteca padrão.
"""

import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

USER = os.environ.get("GH_USER", "Santiann")
TOPIC = os.environ.get("GH_TOPIC", "portfolio")
README = pathlib.Path(os.environ.get("README_PATH", "README.md"))

START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"

# Tópicos que descrevem a stack e viram etiqueta no README.
# Qualquer outro tópico do repositório é ignorado.
TECH_LABELS = {
    "php": "PHP",
    "laravel": "Laravel",
    "livewire": "Livewire",
    "zend": "Zend",
    "pest": "Pest",
    "phpunit": "PHPUnit",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "sqlite": "SQLite",
    "sqlserver": "SQL Server",
    "mongodb": "MongoDB",
    "docker": "Docker",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "nextjs": "Next.js",
    "vue": "Vue.js",
    "vite": "Vite",
    "tailwind": "Tailwind",
    "tailwindcss": "Tailwind",
    "bootstrap": "Bootstrap",
    "alpinejs": "Alpine.js",
    "rest-api": "REST API",
    "graphql": "GraphQL",
    "jwt": "JWT",
    "python": "Python",
    "java": "Java",
}


def api(url):
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": f"{USER}-profile-updater",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_repos():
    repos, page = [], 1
    while True:
        batch = api(
            f"https://api.github.com/users/{USER}/repos"
            f"?per_page=100&page={page}&sort=pushed"
        )
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def tech_line(repo):
    labels = []
    for topic in repo.get("topics") or []:
        label = TECH_LABELS.get(topic)
        if label and label not in labels:
            labels.append(label)
    if not labels and repo.get("language"):
        labels.append(repo["language"])
    return " · ".join(labels)


def render(repos):
    if not repos:
        return (
            "_Nenhum repositório com o tópico "
            f"`{TOPIC}` ainda. Adicione o tópico no \"About\" do repositório._"
        )

    lines = []
    for repo in repos:
        desc = (repo.get("description") or "").strip()
        tech = tech_line(repo)

        lines.append(f"### [{repo['name']}]({repo['html_url']})")
        if desc:
            lines.append("")
            lines.append(desc)
        if tech:
            lines.append("")
            lines.append(f"`{tech}`")
        lines.append("")
    return "\n".join(lines).rstrip()


def main():
    if not README.exists():
        sys.exit(f"README não encontrado: {README}")

    content = README.read_text(encoding="utf-8")
    if START not in content or END not in content:
        sys.exit(f"Marcadores {START} / {END} ausentes no README.")

    try:
        repos = fetch_repos()
    except urllib.error.HTTPError as err:
        sys.exit(f"GitHub API respondeu {err.code}: {err.reason}")

    selected = [
        r for r in repos
        if TOPIC in (r.get("topics") or [])
        and not r.get("fork")
        and not r.get("archived")
    ]
    selected.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)

    block = f"{START}\n\n{render(selected)}\n\n{END}"
    updated = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        lambda _: block,
        content,
        flags=re.DOTALL,
    )

    if updated == content:
        print("Nada mudou.")
        return

    README.write_text(updated, encoding="utf-8")
    print(f"README atualizado com {len(selected)} projeto(s).")


if __name__ == "__main__":
    main()
