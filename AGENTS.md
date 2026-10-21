# Repository maintenance

This is a skill/reference library, not a mobile application. Preserve both independently installable skill folders and progressive disclosure. Keep descriptions discriminating and SKILL.md short; do not preload reference trees.

Inspect affected references before editing. Verify version-sensitive API/policy claims against official sources and record what was checked. Preserve useful examples, but clearly label incomplete sketches. Do not invent “latest” versions, numeric performance guarantees, or permission to deploy user applications.

Run `python scripts/validate_skills.py` and `python -m unittest discover -s tests -v` with requirements-dev.txt installed after tooling/content changes. Exercise changed runnable assets as appropriate. Do not claim static validation proves device behavior or live-service integration.
