#!/usr/bin/env python3
"""Regenerate llms-full.txt from a checkout of the loci kit repo.

    python3 llms_full.py ../loci            # build from the kit's latest release tag
    python3 llms_full.py ../loci --check    # exit 1 if llms-full.txt is stale
    python3 llms_full.py ../loci --ref v0.8.0-beta

The site copies a RELEASE of the kit, never unreleased main. The default ref is
the newest v* tag; a ref that is not exactly a tag stops the build. Every file
published is named below, so a new kit template is a deliberate edit here and a
removed one fails loudly. File text is copied as is, except trailing
whitespace is stripped from each line. Reads with `git show <ref>:<path>`, so the kit's
working tree and branch do not matter. Fetch the kit (with tags) first.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "llms-full.txt"

# Top-level kit docs, in reading order.
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

# Every templates/*.md at the top of templates/ is either published or
# deliberately left out. The build stops if the kit has a template in neither
# list, or if a listed one is gone.
TEMPLATES = [
    "templates/CLAUDE-master.md",
    "templates/SOUL.md",
    "templates/_PALACE_CONTEXT.md",
    "templates/crystals-guide.md",
    "templates/entanglement-template.md",
    "templates/eval-framework.md",
    "templates/feature-helper.md",
    "templates/first-session-protocol.md",
    "templates/garden-file-template.md",
    "templates/garden-health-template.md",
    "templates/garden-template.md",
    "templates/git-log-incident.md",
    "templates/handover-template.md",
    "templates/local-map-template.md",
    "templates/memory-lifecycle.md",
    "templates/obsidian-mindmap-starter.md",
    "templates/okf-interop.md",
    "templates/output-primitive.md",
    "templates/palace-audit-process.md",
    "templates/peer-card-template.md",
    "templates/persona-template.md",
    "templates/retrieval-hierarchy.md",
    "templates/room-template.md",
    "templates/scheduled-task-template.md",
    "templates/synthesis-automation.md",
]
LEFT_OUT = []


def git(kit, *args, strict=True):
    r = subprocess.run(["git", "-C", str(kit), *args], capture_output=True, text=True, encoding="utf-8")
    if r.returncode and strict:
        sys.exit(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout if not r.returncode else None


def build(kit, ref):
    # Resolve to the commit: an annotated tag's own id is not the commit's.
    sha = git(kit, "rev-parse", "--short", f"{ref}^{{commit}}").strip()
    tag = (git(kit, "describe", "--tags", "--exact-match", f"{ref}^{{commit}}", strict=False) or "").strip()
    if not tag:
        sys.exit(f"{ref} ({sha}) is not exactly a release tag; the site copies releases only.")

    listed = git(kit, "ls-tree", "-z", "--name-only", f"{ref}^{{commit}}", "templates/").split("\0")
    present = sorted(p for p in listed if p.endswith(".md") and p.count("/") == 1)
    known = set(TEMPLATES) | set(LEFT_OUT)
    new = [p for p in present if p not in known]
    gone = [p for p in TEMPLATES if p not in present]
    if new or gone:
        sys.exit(
            "template list out of step with the kit at "
            f"{tag}:\n  new, not yet decided: {new or '-'}\n  listed but missing: {gone or '-'}\n"
            "Edit TEMPLATES or LEFT_OUT in llms_full.py, then rebuild."
        )
    files = DOCS + TEMPLATES

    method = git(kit, "show", f"{ref}^{{commit}}:PALACE-METHODOLOGY.md")
    stable = re.search(r"^> stable: (.+)$", method, re.M)
    cand = re.search(r"^> loci-core version: (.+)$", method, re.M)
    version = f"loci-core {stable.group(1).strip()} stable" if stable else "loci-core"
    if cand and stable and cand.group(1).strip() != stable.group(1).strip():
        version += f" ({cand.group(1).strip()} in this release)"

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
        f"**Kit release**: {tag} ({sha}). The files below are copied from the kit repo at that "
        "release; the repo is the source of truth.",
        "",
        "---",
        "",
        "## Kit files below",
        "",
        "Relative links inside these files point into the kit repo: https://github.com/huximaxi/loci",
        "",
    ]
    out = "\n".join(head)
    for f in files:
        body = git(kit, "show", f"{ref}^{{commit}}:{f}")
        body = "\n".join(ln.rstrip() for ln in body.split("\n")).rstrip("\n")
        out += f"\n---\n## FILE: {f}\n---\n\n{body}\n\n"
    return out, tag, sha, len(files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kit", help="path to a checkout of github.com/huximaxi/loci")
    ap.add_argument("--ref", help="release tag to copy (default: newest v* tag)")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    kit = Path(a.kit)
    ref = a.ref or (git(kit, "tag", "--list", "v[0-9]*", "--sort=-v:refname").split() or [""])[0]
    if not ref:
        sys.exit("no v* release tag found in the kit checkout; fetch it with tags")
    text, tag, sha, n = build(kit, ref)
    if a.check:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print(f"llms-full.txt {'current' if same else 'STALE'} against kit {tag} ({sha})")
        sys.exit(0 if same else 1)
    OUT.write_text(text, encoding="utf-8")
    print(f"llms-full.txt: {n} files from kit {tag} ({sha}), {len(text) // 1024} KB")


if __name__ == "__main__":
    main()
