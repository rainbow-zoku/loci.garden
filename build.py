#!/usr/bin/env python3
"""
loci.garden static site include processor.

Walks .html files under landing/, replaces sentinel comment blocks with
the corresponding partial from landing/partials/_*.html, and writes the
result back in place. Source files are committed with substitutions
already applied, so the deploy path stays a plain git pull.

Sentinel format:
    <!-- #include partials/_nav.html -->
    ...existing content (anything here is replaced on next build)...
    <!-- /include -->

Idempotent: re-running after a partial edit re-substitutes cleanly.

Usage:
    python3 build.py            # process every page
    python3 build.py --check    # exit 1 if anything would change (CI guard)
    python3 build.py path/...   # process specific files

Adds .nav-link.active to the matching nav anchor based on a page's
<body data-page="X"> attribute, so each page highlights its own entry.
"""
from __future__ import annotations

import argparse
import html as html_lib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTIALS = ROOT / "partials"

INCLUDE_RE = re.compile(
    r"<!--\s*#include\s+(?P<path>partials/[A-Za-z0-9_./-]+\.html)\s*-->"
    r".*?"
    r"<!--\s*/include\s*-->",
    re.DOTALL,
)

# #include-md generates the check-in Part screens from a markdown source. The
# generated HTML is committed between the sentinels (same convention as #include),
# so re-running after a markdown edit re-substitutes cleanly.
INCLUDE_MD_RE = re.compile(
    r"<!--\s*#include-md\s+(?P<path>[A-Za-z0-9_./-]+\.md)\s*-->"
    r".*?"
    r"<!--\s*/include-md\s*-->",
    re.DOTALL,
)

PART_HEADER_RE = re.compile(r"^##\s+Part\s+(?P<n>\d+):\s*(?P<title>.+?)\s*$")


def _inline_md(text: str) -> str:
    """Escape, then render **bold** and `code` inline. No other markdown."""
    s = html_lib.escape(text)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+?)`", r"<code>\1</code>", s)
    return s


def _render_part(n: int, title: str, body: list[str]) -> str:
    """One `## Part N: Title` block -> a stepped <section>. Contract: intro
    paragraphs, an optional fenced code block (-> read-only snippet helper),
    and `- ` bullets (each -> one labeled textarea). Stops at a `---` rule."""
    out = [
        f'<section class="screen" data-step="p{n}">',
        f'<div class="eyebrow">Part {n} of 7</div>',
        f"<h2>{_inline_md(title)}</h2>",
    ]
    para: list[str] = []

    def flush() -> None:
        if para:
            out.append(f'<p>{_inline_md(" ".join(para).strip())}</p>')
            para.clear()

    i = 0
    while i < len(body):
        s = body[i].strip()
        if s == "---":
            break
        if s.startswith("```"):
            flush()
            code: list[str] = []
            i += 1
            while i < len(body) and not body[i].strip().startswith("```"):
                code.append(body[i])
                i += 1
            i += 1  # closing fence
            snippet = html_lib.escape("\n".join(code))
            out.append(
                "<details open><summary>show the one-liner "
                "(read-only, structure only)</summary>"
                f"<pre>{snippet}</pre></details>"
            )
            continue
        if s.startswith("- "):
            flush()
            out.append(f'<p class="prompt">{_inline_md(s[2:].strip())}</p>')
            out.append('<textarea rows="3" placeholder="optional"></textarea>')
            i += 1
            continue
        if s == "":
            flush()
            i += 1
            continue
        para.append(s)
        i += 1
    flush()

    out.append(
        '<div class="nav"><button class="btn btn-ghost" data-back>Back</button>'
        '<div class="nav-fwd"><button class="skip" data-next>skip</button>'
        '<button class="btn btn-primary" data-next>Next</button></div></div>'
    )
    out.append("</section>")
    return "\n".join(out)


def render_checkin_parts(md_text: str) -> str:
    """Generate all `## Part N:` sections from the check-in markdown source."""
    parts: list[tuple[int, str, list[str]]] = []
    n: int | None = None
    title = ""
    body: list[str] = []
    for line in md_text.splitlines():
        m = PART_HEADER_RE.match(line)
        if m:
            if n is not None:
                parts.append((n, title, body))
            n, title, body = int(m.group("n")), m.group("title"), []
        elif n is not None:
            body.append(line)
    if n is not None:
        parts.append((n, title, body))
    return "\n\n".join(_render_part(pn, pt, pb) for pn, pt, pb in parts)

BODY_DATA_PAGE_RE = re.compile(r'<body[^>]*\bdata-page="(?P<page>[^"]+)"')


def load_partial(rel_path: str) -> str:
    """Read a partial file. Cached per-run."""
    p = ROOT / rel_path
    if not p.exists():
        raise FileNotFoundError(f"partial not found: {p}")
    return p.read_text(encoding="utf-8").rstrip("\n")


def apply_active(nav_html: str, page_key: str | None) -> str:
    """Add .active class to the nav anchor whose data-page matches."""
    if not page_key:
        return nav_html
    pattern = re.compile(
        r'(<a\b[^>]*\bdata-page="' + re.escape(page_key) + r'"[^>]*\bclass=")([^"]*)(")'
    )
    return pattern.sub(
        lambda m: m.group(1) + (m.group(2) + " active").strip() + m.group(3),
        nav_html,
        count=1,
    )


def process(html_text: str) -> str:
    """Substitute all #include sentinels in a single HTML string."""
    page_key_match = BODY_DATA_PAGE_RE.search(html_text)
    page_key = page_key_match.group("page") if page_key_match else None

    def sub(m: re.Match) -> str:
        partial_path = m.group("path")
        partial_text = load_partial(partial_path)
        if partial_path.endswith("_nav.html"):
            partial_text = apply_active(partial_text, page_key)
        return (
            f"<!-- #include {partial_path} -->\n"
            f"{partial_text}\n"
            f"<!-- /include -->"
        )

    def sub_md(m: re.Match) -> str:
        md_path = m.group("path")
        md_file = ROOT / md_path
        if not md_file.exists():
            raise FileNotFoundError(f"include-md source not found: {md_file}")
        parts_html = render_checkin_parts(md_file.read_text(encoding="utf-8"))
        return (
            f"<!-- #include-md {md_path} -->\n"
            f"{parts_html}\n"
            f"<!-- /include-md -->"
        )

    html_text = INCLUDE_RE.sub(sub, html_text)
    return INCLUDE_MD_RE.sub(sub_md, html_text)


def iter_html(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for p in (p.resolve() for p in paths):
        if p.is_dir():
            out.extend(sorted(p.rglob("*.html")))
        elif p.suffix == ".html":
            out.append(p)
    return [p for p in out if "/partials/" not in str(p)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "paths",
        nargs="*",
        default=[str(ROOT)],
        help="files or directories to process (default: landing/)",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if any file would change (no writes)",
    )
    args = ap.parse_args()

    changed = 0
    seen = 0
    for path in iter_html([Path(p) for p in args.paths]):
        seen += 1
        src = path.read_text(encoding="utf-8")
        out = process(src)
        if out != src:
            changed += 1
            if args.check:
                print(f"would change: {path.relative_to(ROOT)}")
            else:
                path.write_text(out, encoding="utf-8")
                print(f"updated: {path.relative_to(ROOT)}")

    if args.check:
        print(f"\n{changed}/{seen} files would change")
        return 1 if changed else 0

    print(f"\n{changed}/{seen} files updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
