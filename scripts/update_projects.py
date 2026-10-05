#!/usr/bin/env python3
"""
Atualiza a seção "Projects" do README.md do perfil.

Pega os repositórios públicos do usuário com push mais recente e, para
cada um, detecta as tecnologias lendo os arquivos do projeto
(composer.json, package.json, requirements.txt, Dockerfile e
docker-compose). Reescreve o bloco entre os marcadores PROJECTS:START e
PROJECTS:END. Sem dependências externas — só a biblioteca padrão.
"""

import base64
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

USER = os.environ.get("GH_USER", "Santiann")
LIMIT = int(os.environ.get("PROJECTS_LIMIT", "4"))
README = pathlib.Path(os.environ.get("README_PATH", "README.md"))

START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"

# Pacotes (Composer, npm, pip) e imagens do docker-compose que viram
# etiqueta no README, na ordem em que aparecem. O que não está aqui é
# ignorado — senão entrariam faker, mockery, tinker e afins.
TECH_LABELS = {
    # Back-end
    "php": "PHP",
    "python": "Python",
    "laravel/framework": "Laravel",
    "symfony/framework-bundle": "Symfony",
    "livewire/livewire": "Livewire",
    "flask": "Flask",
    "django": "Django",
    "fastapi": "FastAPI",
    "firebase/php-jwt": "JWT",
    "tymon/jwt-auth": "JWT",
    "pyjwt": "JWT",
    "jsonwebtoken": "JWT",
    "webonyx/graphql-php": "GraphQL",
    "nuwave/lighthouse": "GraphQL",
    "graphql": "GraphQL",
    "pestphp/pest": "Pest",
    "phpunit/phpunit": "PHPUnit",
    "pytest": "pytest",
    # Front-end
    "next": "Next.js",
    "react": "React",
    "vue": "Vue.js",
    "@angular/core": "Angular",
    "typescript": "TypeScript",
    "tailwindcss": "Tailwind",
    "bootstrap": "Bootstrap",
    "alpinejs": "Alpine.js",
    "chart.js": "Chart.js",
    "vite": "Vite",
    "jest": "Jest",
    "vitest": "Vitest",
    "@playwright/test": "Playwright",
    # Dados
    "mysql": "MySQL",
    "mariadb": "MariaDB",
    "postgres": "PostgreSQL",
    "mcr.microsoft.com/mssql/server": "SQL Server",
    "mongo": "MongoDB",
    "redis": "Redis",
    # Infra
    "docker": "Docker",
}

COMPOSE_FILES = {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"}
PYTHON_FILES = {"requirements.txt", "pyproject.toml", "Pipfile", "setup.py"}


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


def project_files(repo):
    """(nome, sha) dos arquivos na raiz e um nível abaixo, fora de pastas ocultas."""
    tree = api(
        f"https://api.github.com/repos/{repo['full_name']}"
        f"/git/trees/{repo['default_branch']}?recursive=1"
    )
    files = []
    for entry in tree.get("tree", []):
        parts = entry["path"].split("/")
        if entry["type"] == "blob" and len(parts) <= 2 and not parts[0].startswith("."):
            files.append((parts[-1], entry["sha"]))
    return files


def read(repo, sha):
    blob = api(f"https://api.github.com/repos/{repo['full_name']}/git/blobs/{sha}")
    return base64.b64decode(blob["content"]).decode("utf-8", "replace")


def detect(repo):
    """Chaves de TECH_LABELS encontradas nos arquivos do projeto."""
    found = set()
    for name, sha in project_files(repo):
        if name == "composer.json":
            data = json.loads(read(repo, sha))
            found |= {"php", *data.get("require", {}), *data.get("require-dev", {})}
        elif name == "package.json":
            data = json.loads(read(repo, sha))
            found |= {*data.get("dependencies", {}), *data.get("devDependencies", {})}
        elif name in PYTHON_FILES:
            found.add("python")
            if name == "requirements.txt":
                found |= {
                    pkg.lower()
                    for pkg in re.findall(r"^\s*([A-Za-z0-9_.-]+)", read(repo, sha), re.M)
                }
        elif name == "Dockerfile" or name in COMPOSE_FILES:
            found.add("docker")
            if name in COMPOSE_FILES:
                # "mysql:8.0" -> "mysql"; "bitnami/redis" vale como "redis".
                for image in re.findall(r"^\s*image:\s*[\"']?([^\s\"':]+)", read(repo, sha), re.M):
                    found |= {image, image.rsplit("/", 1)[-1]}
    return found


def tech_line(repo):
    try:
        found = detect(repo)
    except (urllib.error.URLError, ValueError) as err:
        print(f"Aviso: não li os arquivos de {repo['name']}: {err}", file=sys.stderr)
        found = set()
    labels = []
    for key, label in TECH_LABELS.items():
        if key in found and label not in labels:
            labels.append(label)
    if not labels and repo.get("language"):
        labels.append(repo["language"])
    return " · ".join(labels)


def render(repos):
    if not repos:
        return "_Nenhum repositório público ainda._"

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

    # Os de push mais recente, tirando forks, arquivados e o próprio
    # repositório do perfil (que tem o mesmo nome do usuário).
    selected = [
        r for r in repos
        if not r.get("fork")
        and not r.get("archived")
        and r["name"].lower() != USER.lower()
    ]
    selected.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
    selected = selected[:LIMIT]

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
