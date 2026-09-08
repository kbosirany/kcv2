"""Shared helpers for build.py and generate_site.py."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PEOPLE_DIR = ROOT / "people"
TEMPLATES_DIR = ROOT / "templates"
CONFIG_PATH = ROOT / "config" / "project.yml"

DATA_FILES = [
    "personal",
    "education",
    "experience",
    "skills",
    "projects",
    "publications",
    "certifications",
]


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return {} if data is None else data


def load_config() -> dict:
    return load_yaml(CONFIG_PATH)


def load_person(person_dir: Path) -> dict:
    """Load a person's profile + all data files into a single context dict."""
    context: dict = {"slug": person_dir.name}
    context["profile"] = load_yaml(person_dir / "profile.yml")

    data_dir = person_dir / "data"
    for name in DATA_FILES:
        path = data_dir / f"{name}.yml"
        context[name] = load_yaml(path) if path.exists() else ([] if name != "personal" else {})

    variants: dict[str, dict] = {}
    variants_dir = person_dir / "variants"
    if variants_dir.exists():
        for path in sorted(variants_dir.glob("*.yml")):
            variant = load_yaml(path)
            variants[variant.get("name", path.stem)] = variant
    context["variants"] = variants
    return context


def list_people() -> list[dict]:
    return [
        load_person(p)
        for p in sorted(PEOPLE_DIR.iterdir())
        if p.is_dir() and (p / "profile.yml").exists()
    ]


def build_variant_context(person: dict, variant: dict) -> dict:
    """Filter a person's data down to what a given variant should show."""
    sections = variant.get(
        "include_sections",
        ["personal", "education", "experience", "skills", "projects", "publications", "certifications"],
    )
    tags_filter = set(variant.get("tags_filter") or [])

    def keep(item: dict) -> bool:
        if not tags_filter:
            return True
        return bool(tags_filter.intersection(item.get("tags", [])))

    ctx = {"slug": person["slug"], "profile": person["profile"], "variant": variant}
    for section in sections:
        data = person.get(section, [])
        if section in ("experience", "projects") and isinstance(data, list):
            data = [item for item in data if keep(item)]
        ctx[section] = data
    return ctx
