# Future Changes

Ideas under consideration. None of these are implemented yet, and plans may change. Suggestions are welcome on [GitHub Issues](https://github.com/Lusan-sapkota/smart-shell/issues).

## Context-aware multi-step runs

Today a plan is generated once and run as a single `&&` chain. A future mode could run steps one at a time and feed a short, sanitized summary of each result (for example "step 2: success") back to the model, so later steps can adapt. Raw output, environment variables and file contents would not be sent.

## Safety

- Optional local audit log of safety decisions.
- Context-aware rules (for example treating `rm -r` inside a fresh temp directory differently from one in `$HOME`).

## Configuration

- Named profiles (for example work and personal) with different providers and models.

