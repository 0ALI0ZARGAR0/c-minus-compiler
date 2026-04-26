#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Dict


ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "README.md"
IDENTITIES_PATH = ROOT / "scripts" / "contributor_identities.json"
START_MARKER = "<!-- contributor-overview:start -->"
END_MARKER = "<!-- contributor-overview:end -->"
SHORTLOG_RE = re.compile(r"^\s*(\d+)\s+(.*?)\s+<(.+)>$")


def load_identity_map() -> Dict[str, dict]:
    data = json.loads(IDENTITIES_PATH.read_text(encoding="utf-8"))
    identity_map: Dict[str, dict] = {}
    for contributor in data["contributors"]:
        identity_map[contributor["name"]] = contributor
        for email in contributor.get("emails", []):
            identity_map[email.lower()] = contributor
        for alias in contributor.get("aliases", []):
            identity_map[alias.lower()] = contributor
    return identity_map


def collect_commit_counts(identity_map: Dict[str, dict]) -> Counter:
    result = subprocess.run(
        ["git", "shortlog", "-sne", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    counts: Counter = Counter()
    for line in result.stdout.splitlines():
        match = SHORTLOG_RE.match(line)
        if not match:
            continue

        commit_count = int(match.group(1))
        raw_name = match.group(2).strip()
        raw_email = match.group(3).strip().lower()

        contributor = identity_map.get(raw_email) or identity_map.get(raw_name.lower())
        if contributor is None:
            contributor = {"name": raw_name}
        counts[contributor["name"]] += commit_count

    return counts


def repository_graph_url() -> str | None:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        return None

    remote_url = result.stdout.strip()
    if remote_url.startswith("git@github.com:"):
        remote_url = remote_url.replace("git@github.com:", "https://github.com/")
    if remote_url.endswith(".git"):
        remote_url = remote_url[:-4]
    if remote_url.startswith("https://github.com/"):
        return f"{remote_url}/graphs/contributors"
    return None


def contributor_label(contributor: dict) -> str:
    github_user = contributor.get("github")
    if github_user:
        return f"[{contributor['name']}](https://github.com/{github_user})"
    return contributor["name"]


def build_overview_block(counts: Counter, identity_map: Dict[str, dict]) -> str:
    total_commits = sum(counts.values())
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0].lower()))
    contributor_rows = []
    pie_rows = []

    for name, commit_count in ordered:
        contributor = identity_map.get(name, {"name": name})
        share = (commit_count / total_commits) * 100 if total_commits else 0.0
        contributor_rows.append(
            f"| {contributor_label(contributor)} | {share:.1f}% |"
        )
        pie_rows.append(f'    "{name}" : {share:.1f}')

    lines = [
        START_MARKER,
        "Auto-generated from current branch history.",
        "",
        "| Contributor | Share |",
        "| --- | ---: |",
        *contributor_rows,
        "",
        "```mermaid",
        "pie",
        "    title Relative Contribution Share",
        *pie_rows,
        "```",
    ]

    graph_url = repository_graph_url()
    if graph_url:
        lines.extend(["", f"[Open GitHub contributors graph]({graph_url})"])

    lines.append(END_MARKER)
    return "\n".join(lines)


def replace_block(readme_text: str, new_block: str) -> str:
    start_index = readme_text.index(START_MARKER)
    end_index = readme_text.index(END_MARKER) + len(END_MARKER)
    return readme_text[:start_index] + new_block + readme_text[end_index:]


def main() -> int:
    identity_map = load_identity_map()
    counts = collect_commit_counts(identity_map)
    new_block = build_overview_block(counts, identity_map)
    readme_text = README_PATH.read_text(encoding="utf-8")
    updated_text = replace_block(readme_text, new_block)
    README_PATH.write_text(updated_text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
