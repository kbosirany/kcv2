"""Validate all people's CV data against the pydantic models in models.py.

Usage: python scripts/validate.py
Exits with a non-zero status if any file fails validation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError

from models import (
    Certification,
    EducationItem,
    ExperienceItem,
    PersonalInfo,
    Profile,
    Project,
    Publication,
    SkillCategory,
    Variant,
)

ROOT = Path(__file__).resolve().parent.parent
PEOPLE_DIR = ROOT / "people"

# data/<name>.yml -> model used to validate each item (list files) or the
# whole document (single-object files).
LIST_DATA_MODELS: dict[str, type[BaseModel]] = {
    "education": EducationItem,
    "experience": ExperienceItem,
    "skills": SkillCategory,
    "projects": Project,
    "publications": Publication,
    "certifications": Certification,
}
SINGLE_DATA_MODELS: dict[str, type[BaseModel]] = {
    "personal": PersonalInfo,
}


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return {} if data is None else data


def validate_person(person_dir: Path) -> list[str]:
    errors: list[str] = []
    slug = person_dir.name

    profile_path = person_dir / "profile.yml"
    if not profile_path.exists():
        return [f"{slug}: missing profile.yml"]
    try:
        Profile.model_validate(load_yaml(profile_path))
    except ValidationError as e:
        errors.append(f"{slug}/profile.yml: {e}")

    data_dir = person_dir / "data"
    for name, model in SINGLE_DATA_MODELS.items():
        path = data_dir / f"{name}.yml"
        if not path.exists():
            errors.append(f"{slug}: missing data/{name}.yml")
            continue
        try:
            model.model_validate(load_yaml(path))
        except ValidationError as e:
            errors.append(f"{slug}/data/{name}.yml: {e}")

    for name, model in LIST_DATA_MODELS.items():
        path = data_dir / f"{name}.yml"
        if not path.exists():
            errors.append(f"{slug}: missing data/{name}.yml")
            continue
        items = load_yaml(path)
        if items is None:
            items = []
        if not isinstance(items, list):
            errors.append(f"{slug}/data/{name}.yml: expected a list")
            continue
        for i, item in enumerate(items):
            try:
                model.model_validate(item)
            except ValidationError as e:
                errors.append(f"{slug}/data/{name}.yml[{i}]: {e}")

    variants_dir = person_dir / "variants"
    if variants_dir.exists():
        for variant_path in sorted(variants_dir.glob("*.yml")):
            try:
                Variant.model_validate(load_yaml(variant_path))
            except ValidationError as e:
                errors.append(f"{slug}/variants/{variant_path.name}: {e}")

    return errors


def main() -> int:
    if not PEOPLE_DIR.exists():
        print(f"No people/ directory found at {PEOPLE_DIR}")
        return 1

    all_errors: list[str] = []
    for person_dir in sorted(PEOPLE_DIR.iterdir()):
        if not person_dir.is_dir():
            continue
        all_errors.extend(validate_person(person_dir))

    if all_errors:
        print("Validation failed:\n")
        for err in all_errors:
            print(f"  - {err}")
        print(f"\n{len(all_errors)} error(s).")
        return 1

    print("All CV data is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
