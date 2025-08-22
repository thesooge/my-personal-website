# Personal Site (Django + Tailwind)

A fast, accessible, SEO-friendly personal website for local development.

## Features
- Pages: Home, About, Blog (categories/tags), Projects, Contact (console email)
- Admin: manage posts/projects with images, slugs auto-generate
- Blog: Markdown (sanitized), search, pagination, RSS, sitemap, robots.txt
- Images: uploads with thumbnails (easy-thumbnails)
- API: read-only JSON endpoints via DRF (`/api/...`)
- UI: Django templates + Tailwind, light/dark toggle
- i18n-ready (default `en-us`)
- Quality: ruff, mypy; Tests: pytest with coverage ≥90% on `content`

## Requirements
- Python 3.12+
- Node is not required directly; Tailwind runs via `django-tailwind` app

## Dependencies

### Base Requirements
```bash
pip install -r requirements.txt
```

### Development Requirements
```bash
pip install -r requirements-dev.txt
```

### Production Requirements
```bash
pip install -r requirements-prod.txt
```

### Quick Setup
```bash
# Make the script executable (first time only)
chmod +x install.sh

# Install all dependencies and setup project
./install.sh

# Or install for specific environment
./install.sh dev      # Development environment
./install.sh prod     # Production environment
```

## Environment
Copy `env.example` to `.env` and adjust values:
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- Email backend (console by default)
- Rate limit settings for contact form

## How to run locally
```bash
make setup
make dev
```
- App: http://localhost:8000
- Admin: http://localhost:8000/admin/

If needed, create a superuser:
```bash
source venv/bin/activate
python manage.py createsuperuser
```

Load sample data:
```bash
source venv/bin/activate
python manage.py loaddata sample_data
```

## Common commands
```bash
make test      # run tests with coverage
make lint      # ruff + mypy
make format    # ruff format
make migrate   # apply migrations
```

## Tailwind workflow
Tailwind is provided by `django-tailwind` theme app (`theme/`). `make dev` starts the Django server and Tailwind watcher.

## Troubleshooting
- If Tailwind styles don’t appear, ensure the Tailwind watcher is running: `python manage.py tailwind start`.
- If migrations fail, delete `db.sqlite3` and run `make migrate`.
- If images don’t load in templates, ensure `MEDIA_ROOT` exists and check URLs.

## License
MIT — see `LICENSE`. 