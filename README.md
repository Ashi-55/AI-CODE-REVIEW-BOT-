# AI Code Review Bot (aicr)

AI-powered code review for Git repositories. Analyzes Git diffs or pull requests to surface bugs, security vulnerabilities, performance issues, code smells, and style violations. Combines static analyzers (pylint, bandit, radon) with optional LLM feedback for professional-grade review output.

## Features
- Review unified Git diff files or compare two refs (base..head)
- Review GitHub Pull Requests via API
- Findings across: Bugs, Security, Performance, Code Smells, Style
- Structured outputs: Rich terminal table, Markdown summary, JSON
- Optional LLM analysis (OpenAI) for deeper insights
- Severity threshold to fail CI builds
- GitHub Actions job summary integration

## Requirements
- Python 3.9+
- Dependencies listed in `requirements.txt` or `pyproject.toml`

## Installation
Option A (local dev):
```
pip install -r requirements.txt
```
Option B (package install):
```
pip install .
```
Run as a module:
```
python -m aicr
```
Installed script (after `pip install .`):
```
aicr
```

## Environment Variables
- `OPENAI_API_KEY` (optional): Enables LLM analysis. If not set, LLM is skipped.
- `AICR_MODEL` (optional): OpenAI model name (default: `gpt-4o-mini`).
- `GITHUB_STEP_SUMMARY` (auto by GitHub Actions): When present, the Markdown summary is written to the job summary.

## CLI Overview
Top-level command: `aicr review`

Subcommands:
- `diff-file` — Review a unified diff file.
- `git` — Review changes between two refs in a local repo.
- `pr` — Review a GitHub Pull Request via API.

Common Options:
- `--output <path>`: Write JSON report to file
- `--markdown <path>`: Write Markdown summary to file
- `--github-summary`: Also write Markdown summary to GitHub Actions job summary
- `--fail-on-severity [low|medium|high]`: Exit non-zero if any finding meets/exceeds threshold

## Quick Start Examples
Review a diff file:
```
git diff origin/main...HEAD > changes.diff

# With LLM (if OPENAI_API_KEY is set) and CI-friendly options
 aicr review diff-file changes.diff \
   --markdown review.md \
   --github-summary \
   --fail-on-severity high
```

Review local repo changes between base and head:
```
aicr review git --base origin/main --head HEAD \
  --markdown review.md \
  --github-summary \
  --fail-on-severity medium
```

Review a GitHub Pull Request via API:
```
aicr review pr --repo owner/repo --pr 123 --token $GITHUB_TOKEN \
  --github-summary \
  --markdown review.md \
  --fail-on-severity medium
```

## Output Formats
- Terminal: Rich table showing Severity, Category, Title, Location, Suggestion
- Markdown: Detailed section per finding with description and suggestion
- JSON: Structured report for programmatic use

## GitHub Actions Integration
Example workflow (PR events):
```yaml
name: AI Code Review
on:
  pull_request:
    types: [opened, synchronize, reopened]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install
        run: |
          pip install .
      - name: Run AI Code Review (git refs)
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}  # optional
        run: |
          aicr review git \
            --base ${{ github.event.pull_request.base.sha }} \
            --head ${{ github.event.pull_request.head.sha }} \
            --github-summary \
            --markdown review.md \
            --fail-on-severity medium
      # Alternative: use PR API (requires token)
      # - name: Run AI Code Review (PR API)
      #   env:
      #     GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      #     OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}  # optional
      #   run: |
      #     aicr review pr \
      #       --repo ${{ github.repository }} \
      #       --pr ${{ github.event.pull_request.number }} \
      #       --github-summary \
      #       --markdown review.md
```

## How It Works
- Diff parsing: Unified diff files are parsed to determine changed files and line ranges.
- Static analyzers:
  - `pylint`: style and basic errors
  - `bandit`: security issues
  - `radon`: cyclomatic complexity and code smell signals
- LLM review: Summarized diff is sent to an OpenAI model to propose structured findings.
- Reporting: Findings merged into a single report with counts by category and severity.

## Configuration Tips
- LLM is optional: omit `OPENAI_API_KEY` to run only static analysis.
- Use `--fail-on-severity` to control CI behavior (e.g., fail on `medium` or `high`).
- Use `--markdown` and `--github-summary` to get readable reports in PR checks.

## Extending
- Add more analyzers in `aicr/core/analyzers.py`.
- Enhance formatting in `aicr/core/formatter.py`.
- Adjust LLM prompt/model in `aicr/core/llm.py`.

## Troubleshooting
- Missing OpenAI key: LLM analysis is skipped automatically.
- Tools not found (pylint/bandit/radon): Ensure they are installed (pip install . or requirements.txt).
- Git errors: Ensure the repository exists and refs are valid for `aicr review git`.
- PR API errors: Pass a valid `--token` or set `GITHUB_TOKEN`.

## License
Copyright © 2025. All rights reserved.
