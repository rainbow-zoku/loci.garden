#!/usr/bin/env python3
"""Regenerate llms-full.txt from a checkout of the loci kit repo.

    python3 llms_full.py ../loci            # build from the kit's origin/main
    python3 llms_full.py ../loci --check    # exit 1 if llms-full.txt is stale

Reads files with `git show <ref>:<path>`, so the kit's working tree and
current branch do not matter. Fetch the kit first.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "llms-full.txt"

# Top-level kit docs, in reading order. Every templates/*.md at the top of
# templates/ follows, sorted. A listed file that is missing stops the build.
DOCS = [
    "README.md",
    "PALACE-METHODOLOGY.md",
    "CHANGELOG.md",
    "FIRST-SESSION.md",
    "SETUP-GUIDE.md",
    "AGENT-SETUP.md",
    "PALACE-UPDATE.md",
    "CONTRIBUTING.md",
]


def git(kit, *args):
    r = subprocess.run(["git", "-C", str(kit), *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def build(kit, ref):
    sha = git(kit, "rev-parse", "--short", ref).strip()
    tag = subprocess.run(["git", "-C", str(kit), "describe", "--tags", "--exact-match", ref],
                         capture_output=True, text=True).stdout.strip()
    templates = sorted(
        p for p in git(kit, "ls-tree", "--name-only", ref, "templates/").split()
        if p.endswith(".md") and p.count("/") == 1
    )
    files = DOCS + templates

    method = git(kit, "show", f"{ref}:PALACE-METHODOLOGY.md")
    stable = re.search(r"^> stable: (.+)$", method, re.M)
    cand = re.search(r"^> loci-core version: (.+)$", method, re.M)
    version = f"loci-core {stable.group(1).strip()} stable" if stable else "loci-core"
    if cand and stable and cand.group(1).strip() != stable.group(1).strip():
        version += f", {cand.group(1).strip()} next"

    head = [
        "# loci.garden - full context declaration",
        "# Proactive context management for human-AI collaboration",
        "# Built by Hux x Vesper · 2026 · MIT",
        "",
        "> This is the full context declaration. For the concise version, see: https://loci.garden/llms.txt",
        "",
        "> **What is Loci?** A methodology for persistent AI collaboration. Your AI gets memory "
        "(crystals), character (soul files), and ideas that grow (the garden). No database. "
        "No vendor lock-in. Just markdown files.",
        "",
        "**Website**: https://loci.garden",
        "**GitHub**: https://github.com/huximaxi/loci",
        f"**Palace methodology version**: {version}",
        f"**Kit snapshot**: {tag + ' ' if tag else ''}({sha}). The files below are copied from the "
        "kit repo at that commit; the repo is the source of truth.",
        "",
        "---",
        "",
        "## Kit files below",
        "",
        "---",
        "",
    ]
    out = "\n".join(head)
    for f in files:
        body = git(kit, "show", f"{ref}:{f}").rstrip("\n")
        out += f"\n---\n## FILE: {f}\n---\n\n{body}\n\n"
    return out, sha, len(files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kit", help="path to a checkout of github.com/huximaxi/loci")
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    text, sha, n = build(Path(a.kit), a.ref)
    if a.check:
        same = OUT.exists() and OUT.read_text() == text
        print(f"llms-full.txt {'current' if same else 'STALE'} against kit {sha}")
        sys.exit(0 if same else 1)
    OUT.write_text(text)
    print(f"llms-full.txt: {n} files from kit {sha}, {len(text) // 1024} KB")


if __name__ == "__main__":
    main()
