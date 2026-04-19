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
