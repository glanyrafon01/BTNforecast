# AGENTS.md

Purpose: guidance for agentic coding in this repo.
Current state: Python simulation with CLI and FastAPI web UI.

Section 1: Build, Lint, Test
No build tooling is present yet.
Do NOT invent commands; verify via files.
Discovery checklist:
- `package.json` for npm/yarn/pnpm
- `pyproject.toml`, `setup.cfg`, `requirements.txt` for Python
- `Cargo.toml` for Rust
- `go.mod` for Go
- `pom.xml` or `build.gradle` for Java
- `Makefile` or `justfile` for custom tasks
- `README.md` for project-specific commands

When tooling exists, prefer these conventions:
- Build: use the project’s default build command.
- Lint: use the repo’s configured linter.
- Test: run the smallest relevant scope.

Single-test guidance (examples only; confirm first):
- JavaScript: `npm test -- <pattern>` or `pnpm vitest <file>`
- Jest: `npx jest <test-file> -t "name"`
- Vitest: `npx vitest <test-file> -t "name"`
- Pytest: `pytest <path>::<test_name>`
- Go: `go test ./pkg -run TestName`
- Rust: `cargo test test_name`
- JUnit: `mvn -Dtest=Class#method test`

If no single-test support exists, add it to tooling and document here.

Section 2: Code Style
Primary rule: follow existing conventions in the codebase.
Since there is no code yet, follow language defaults and document them.

Imports:
- Prefer absolute imports when the language ecosystem expects them.
- Group imports: stdlib, third-party, local.
- Keep import order stable via formatter/linter.
- Avoid unused imports.

Formatting:
- Use the language’s standard formatter where available.
- Do not introduce a formatter if the project does not use one.
- Keep line length reasonable (prefer 80–100 unless configured).
- Use 2 spaces for JS/TS if Prettier config exists; otherwise follow file style.

Types:
- If the codebase uses static typing, keep types explicit at public boundaries.
- Avoid `any`/dynamic types unless already common.
- Use narrow types and prefer named types for complex shapes.

Naming:
- Use clear, intention-revealing names.
- Prefer `camelCase` for variables/functions, `PascalCase` for types/classes.
- Use `SCREAMING_SNAKE_CASE` for constants when language favors it.
- Avoid abbreviations unless already established.

Error handling:
- Prefer explicit error returns/throws over silent failures.
- Add context to errors (input, operation, or ids).
- Do not swallow errors; log or propagate.
- For user-facing errors, keep messages stable and actionable.

Logging:
- Use existing logging utilities if present.
- Avoid noisy logs in hot paths or tests.
- Do not log secrets or PII.

Testing style:
- Name tests after behavior.
- Keep tests deterministic; avoid sleeps.
- Use fixtures/builders already in the project.
- Prefer smallest scope: unit over integration when possible.

Documentation:
- Update docs when changing public behavior.
- Keep README instructions accurate.
- Add inline comments only for non-obvious logic.

Config files:
- Respect project configs for tooling and formatting.
- Do not change config defaults unless requested.

Dependency management:
- Use existing package manager.
- Keep versions aligned with lockfiles.
- Avoid adding new dependencies unless necessary.

Security:
- Never commit secrets.
- Validate external inputs.
- Avoid shelling out with untrusted input.

Performance:
- Prefer clarity first; optimize only when needed.
- Be mindful of allocations in tight loops.

Front-end (if added later):
- Preserve existing design system.
- Keep accessibility in mind (contrast, labels, focus).
- Ensure responsive behavior.

Backend (if added later):
- Use structured errors.
- Keep API responses consistent.
- Validate request payloads.

Git hygiene:
- Keep commits focused.
- Include tests in CI if present.
- Do not rewrite history without explicit instruction.

Repository rules:
- No Cursor rules detected (.cursor/rules/ or .cursorrules).
- No Copilot rules detected (.github/copilot-instructions.md).
If those files appear later, mirror their guidance here.

Agent workflow:
- Inspect the repo before making assumptions.
- Prefer minimal, targeted changes.
- Update this file when new tooling is introduced.

Operational defaults:
- Keep changes small and reversible.
- Avoid speculative refactors.
- Ask for clarification only when blocked.

Placeholders to fill when code exists:
- Build command: none
- Lint command: none
- Test command: none
- Single-test command: none
- Format command: none
- Typecheck command: none

Run commands:
- CLI simulation: `python -m btnforecast simulate --config forecast.yaml --out outputs`
- Plotting: `python -m btnforecast plot --input outputs/seat_probs.csv --out outputs`
- Web app: `uvicorn app:app --reload --host 0.0.0.0 --port 8000`

Add project-specific conventions here once they are known.
Examples: module boundaries, directory layout, API versioning.

Line-ending preference: follow existing files.
Encoding: UTF-8 unless files specify otherwise.
License: respect project license headers if added.

This document should stay short and accurate.
Keep it updated as the codebase evolves.

End.
