"""Render each person/variant through the moderncv LaTeX template and, if a
LaTeX toolchain is available, compile it to PDF.

Usage: python scripts/build.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from common import ROOT, TEMPLATES_DIR, build_variant_context, list_people, load_config

DIST_PDF = ROOT / "dist" / "pdf"


def render_tex(env: Environment, template_name: str, context: dict) -> str:
    template = env.get_template(template_name)
    return template.render(**context)


def compile_pdf(tex_path: Path) -> bool:
    """Compile a .tex file to PDF with latexmk, if available. Returns success."""
    if not shutil.which("latexmk"):
        print(f"  latexmk not found, skipping PDF compilation for {tex_path.name}")
        return False
    # -interaction=nonstopmode + -halt-on-error avoid TeX-level prompts, but a
    # package manager (e.g. MiKTeX) can still block waiting for an
    # install-on-the-fly confirmation, so also guard with a hard timeout.
    env = {**os.environ, "MIKTEX_ENABLEINSTALLER": "0"}
    try:
        result = subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", tex_path.name],
            cwd=tex_path.parent,
            capture_output=True,
            text=True,
            env=env,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        print(f"  LaTeX compilation timed out for {tex_path.name}, skipping")
        return False
    if result.returncode != 0:
        print(f"  LaTeX compilation failed for {tex_path.name}:\n{result.stdout[-2000:]}")
        return False
    return True


def main() -> int:
    config = load_config()
    default_template = config.get("build", {}).get("default_template", "moderncv")

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

    for person in list_people():
        slug = person["slug"]
        profile = person["profile"]
        variants = person["variants"] or {"default": {"name": "default"}}
        template_name = profile.get("default_template", default_template)

        out_dir = DIST_PDF / slug
        out_dir.mkdir(parents=True, exist_ok=True)

        for variant_name, variant in variants.items():
            template = variant.get("template", template_name)
            template_path = f"{template}/main.tex.jinja"

            context = build_variant_context(person, variant)
            print(f"Rendering {slug}/{variant_name} with template '{template}'...")
            tex_content = render_tex(env, template_path, context)

            tex_path = out_dir / f"{variant_name}.tex"
            tex_path.write_text(tex_content, encoding="utf-8")
            compile_pdf(tex_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
