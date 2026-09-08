"""Render a simple static HTML site listing all people and their CV variants.

Usage: python scripts/generate_site.py
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from common import ROOT, TEMPLATES_DIR, build_variant_context, list_people, load_config

DIST_SITE = ROOT / "dist" / "site"


def main() -> int:
    config = load_config()
    site_config = config.get("site", {})

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

    DIST_SITE.mkdir(parents=True, exist_ok=True)
    shutil.copy(TEMPLATES_DIR / "minimalist" / "style.css", DIST_SITE / "style.css")

    pdf_src = ROOT / "dist" / "pdf"
    pdf_dst = DIST_SITE / "pdf"
    if pdf_src.exists():
        if pdf_dst.exists():
            shutil.rmtree(pdf_dst)
        shutil.copytree(pdf_src, pdf_dst)

    people = list_people()
    index_lines = [
        "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>",
        f"<title>{site_config.get('title', 'CVs')}</title>",
        "<link rel='stylesheet' href='style.css'></head><body><main class='cv'>",
        f"<h1>{site_config.get('title', 'CVs')}</h1>",
        f"<p>{site_config.get('description', '')}</p><ul>",
    ]

    for person in people:
        slug = person["slug"]
        profile = person["profile"]
        variants = person["variants"] or {"default": {"name": "default"}}
        person_dir = DIST_SITE / slug
        person_dir.mkdir(parents=True, exist_ok=True)

        for variant_name, variant in variants.items():
            context = build_variant_context(person, variant)
            context["site_root"] = "../"
            pdf_path = ROOT / "dist" / "pdf" / slug / f"{variant_name}.pdf"
            context["pdf_url"] = f"../pdf/{slug}/{variant_name}.pdf" if pdf_path.exists() else None
            template = env.get_template("minimalist/index.html.jinja")
            html = template.render(**context)
            (person_dir / f"{variant_name}.html").write_text(html, encoding="utf-8")
            index_lines.append(
                f"<li><a href='{slug}/{variant_name}.html'>{profile.get('full_name', slug)} "
                f"— {variant_name}</a></li>"
            )

    index_lines.append("</ul></main></body></html>")
    (DIST_SITE / "index.html").write_text("\n".join(index_lines), encoding="utf-8")
    print(f"Site generated at {DIST_SITE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
