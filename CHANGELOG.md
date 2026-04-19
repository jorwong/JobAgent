# Changelog

## 2026-04-18

**Project kickoff — architecture plan and project scaffold**

- Reviewed PRD (`ProjectPrd.md`) and master resume (`master-resume.tex`)
- Designed full implementation plan covering TUI, resume tailoring, job scraping, auto-apply, and plugin system
- Saved approved plan to `.claude/plans/fuzzy-hatching-matsumoto.md`
- Created `pyproject.toml` with dependencies: textual, anthropic, playwright, httpx, beautifulsoup4, lxml, pydantic
- Scaffolded project directory structure under `src/jobagent/` with packages: core, scrapers, appliers, plugins, tui (screens + widgets)
- Created `applied/` directory for application tracking
- Created `plugins/` directory for user-defined external plugins

## 2026-04-19

**LinkedIn scraper, resume tailoring pipeline, and cover letter generation**

- Built LinkedIn public job scraper (`src/jobagent/scrapers/linkedin.py`) — scrapes job listings without login
- Added `search_jobs.py` runner to search multiple keywords and display results
- Added `fetch_details.py` to fetch full JDs and apply links for all listings in parallel
- Created `src/jobagent/core/latex_compiler.py` — compiles `.tex` to PDF via tectonic, auto-patches pdflatex-only commands
- Created `src/jobagent/core/resume_tailor.py` — sets up `applied/<company>/<role>/` directory, copies master resume and saves JD; `compile` subcommand compiles resume + cover letter to PDF
- Created `src/jobagent/core/cover_letter.py` — compiles plain-text cover letter to PDF via LaTeX template
- Created `src/jobagent/core/cover_letter_template.tex` — LaTeX template for cover letters
- Registered `tailor-resume`, `compile-resume`, `cover-letter` CLI entry points in `pyproject.toml`
- Tailored resume for Evernote/Bending Spoons Graduate SWE role and compiled to one-page PDF
- Wrote cover letter for Evernote/Bending Spoons and compiled to PDF
- Added `.gitignore` — excludes `applied/`, `master-resume.tex`, `jobs_scraped.json`, Python cache, `.DS_Store`
- Untracked `applied/`, `master-resume.tex`, and `jobs_scraped.json` from git history
- Installed `tectonic` (via Homebrew) as the LaTeX compiler
