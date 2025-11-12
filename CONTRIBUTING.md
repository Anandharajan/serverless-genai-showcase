# Contributing

1. Fork or clone the repo and create a feature branch.
2. Install dependencies with `pip install -e .[dev]`.
3. Run `codex lint` + `codex test` before opening a PR.
4. Update documentation (README, docs/) when behavior changes.
5. PRs must pass CI and receive at least one review from CODEOWNERS.

## Commit conventions
- Use present tense (`add endpoint`, not `added endpoint`).
- Reference issues or work items in the description.
- Keep commits scoped (infra, services, docs).
