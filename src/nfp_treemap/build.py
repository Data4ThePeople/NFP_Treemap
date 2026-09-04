"""Render the self-contained treemap page.

    python -m nfp_treemap.build [-o dist/index.html]
"""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import (
    CANONICAL_URL,
    META_DESCRIPTION,
    DIST_DIR,
    LOGO_DIR,
    LOGO_SUFFIXES,
    ROBOTS,
    ROOT,
)
from .transform import build_payload

TITLE = "U.S. Employment Data Treemap"
TEMPLATES = Path(__file__).parent / "templates"
STATIC = Path(__file__).parent / "static"

# The hosted page routes exports through window.claude.downloads.save(), which
# asks the viewer to confirm before writing anything.
ARTIFACT_EXPORT_NOTE = (
    " CSV and PNG exports ask for your confirmation before saving."
)


MIME = {
    ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg", ".webp": "image/webp",
}


def logo_data_uri() -> str:
    """First image in logo/, inlined. Empty string when there is none.

    Inlined rather than linked because the published page cannot fetch external
    assets, and because a single self-contained file is the whole delivery
    model here. Drop a replacement into logo/ and rebuild.
    """
    if not LOGO_DIR.is_dir():
        return ""
    files = sorted(
        p for p in LOGO_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in LOGO_SUFFIXES
    )
    if not files:
        return ""
    path = files[0]
    encoded = base64.b64encode(path.read_bytes()).decode()
    return f"data:{MIME[path.suffix.lower()]};base64,{encoded}"


def render(output: Path | None = None, artifact: bool = False) -> Path:
    if output is None:
        output = DIST_DIR / ("artifact.html" if artifact else "index.html")
    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(enabled_extensions=()),
    )
    template = env.get_template(
        "artifact.html.j2" if artifact else "treemap.html.j2"
    )
    html = template.render(
        title=TITLE,
        canonical="" if artifact else CANONICAL_URL,
        description="" if artifact else META_DESCRIPTION,
        robots="" if artifact else ROBOTS,
        css=(STATIC / "treemap.css").read_text(),
        js=(STATIC / "treemap.js").read_text(),
        export_note=ARTIFACT_EXPORT_NOTE if artifact else "",
        logo=logo_data_uri(),
        # Injected into a <script> block, so </script> inside a NAICS
        # description would terminate it early.
        payload=json.dumps(build_payload(), separators=(",", ":")).replace(
            "</", "<\\/"
        ),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", type=Path, default=None)
    parser.add_argument(
        "--artifact",
        action="store_true",
        help="emit page content only (no doctype/html/head/body) for hosts "
             "that supply their own document skeleton",
    )
    args = parser.parse_args()
    path = render(args.output, artifact=args.artifact)
    size = path.stat().st_size / 1e6
    print(f"wrote {path.relative_to(ROOT)}  ({size:.2f} MB)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
