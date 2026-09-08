# CV Manager

A monorepo for managing CVs for multiple people (family/friends) from structured
YAML data, rendered into PDF (LaTeX) and a static site (GitHub Pages).

> ⚠️ **This repository is public.** Do not commit real personal data (address,
> phone number, date of birth, photos, etc.) unless you are comfortable with it
> being publicly visible. Use placeholder/example data, or fork this structure
> into a private repo for real use.

## Structure

```
people/<slug>/profile.yml        # identity + which template/variants to build
people/<slug>/data/*.yml         # raw CV data (personal, education, experience, ...)
people/<slug>/variants/*.yml     # per-variant overrides/filters (e.g. "engineer")
people/<slug>/assets/            # photos etc. (gitignored by default, see .gitignore)

templates/                       # rendering templates (LaTeX + HTML)
schemas/                         # JSON Schemas for editor autocompletion/validation
scripts/                         # build.py, generate_site.py, validate.py, models.py
config/project.yml               # global site/build settings
dist/                            # build output (gitignored)
```

## How it works

1. Each person's data lives under `people/<slug>/data/*.yml`, split by concern.
2. `profile.yml` declares the person's name, default template, and the list of
   variants to build (a variant can filter/reorder sections, e.g. "academic"
   vs "engineer").
3. `scripts/validate.py` validates every YAML file against the pydantic models
   in `scripts/models.py` (the JSON Schemas in `schemas/` mirror these models
   and are referenced from the YAML files for editor autocompletion only).
4. `scripts/build.py` renders each person/variant through a Jinja LaTeX
   template and compiles it to PDF (best-effort — skipped if no LaTeX
   toolchain is available).
5. `scripts/generate_site.py` renders a simple static HTML site listing all
   people and their CV variants, published to GitHub Pages.

## Local usage

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python scripts/validate.py
python scripts/build.py          # renders + (best-effort) compiles PDFs to dist/pdf
python scripts/generate_site.py  # renders static site to dist/site
```

## Adding a new person

1. Copy an existing folder under `people/` (e.g. `people/vivi`) to
   `people/<new-slug>/`.
2. Edit `profile.yml` and the files under `data/`.
3. Run `python scripts/validate.py` to check your data.

## CI

- `.github/workflows/build.yml` validates all data and builds PDFs on every
  push/PR.
- `.github/workflows/pages.yml` builds the static site and deploys it to
  GitHub Pages on pushes to `main`.
