# Contribution rules

- Create a feature branch and pull request for every change. Do not push directly to `main`.
- Before merging, verify that `validate` and `Browser smoke · visitor preview` both completed successfully on the exact current PR head commit. Missing, pending, skipped, cancelled or failing checks are not passing checks.
- Refresh PR state before merging, supply its expected head SHA, and preserve concurrent contributions. Verify checks on the merged `main` commit before reporting it green.
- Fix the cause of failed checks; do not disable checks or weaken their guarantees to merge.
- Keep the canonical source repository private. Preserve the visitor-only export and explicit story-review approval gate. A passing build does not authorize publication or a visibility change.
- Preserve confirmed, uncertain, negative and unanswered interview states distinctly; reservation evidence is not proof of attendance or an exact visit date.
- Keep Culture, Work, Adventures and Life Map independently maintained. Link related experiences instead of duplicating their canonical datasets.

These are contributor instructions, not GitHub-enforced branch protection.
