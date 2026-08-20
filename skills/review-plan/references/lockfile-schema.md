# Plan lockfile schema

Use this reference when building or inspecting `.beads/plan-locks/*.lock.json` files.

## Purpose

The lockfile is the compiled, reviewed companion to a markdown or JSON plan. It preserves:

- source provenance
- normalized task graph
- referenced-file fingerprints
- accumulated review passes

It is not the human-readable source of truth. The plan document remains that.

## Default location

Store lockfiles in:

```text
.beads/plan-locks/<plan-stem>.lock.json
```

Do not store them next to the markdown plan by default. Keep markdown plans human-facing and keep lockfiles in the repo-local machine-artifact area.

## Shape

```json
{
  "lockfile_version": 1,
  "source": {
    "path": "docs/plans/example-implementation-plan.md",
    "type": "markdown",
    "sha256": "<source hash>"
  },
  "compiled_plan": {
    "source": "docs/plans/example-implementation-plan.md",
    "items": []
  },
  "compiled_plan_sha256": "<compiled json hash>",
  "fingerprints": {
    "root": "/absolute/project/root",
    "files": [
      {
        "path": "src/example.ts",
        "exists": true,
        "sha256": "<file hash>"
      }
    ]
  },
  "review": {
    "status": "reviewed",
    "passes": [
      {
        "reviewer": "review-plan",
        "source_sha256": "<source hash>",
        "compiled_plan_sha256": "<compiled json hash>",
        "accepted_findings": [],
        "skipped_findings": [],
        "unresolved_findings": []
      }
    ]
  }
}
```

## Drift model

The lockfile is considered drifted when:

- the source plan hash changes
- a fingerprinted referenced file changes or disappears

Use:

```bash
python3 scripts/plan-lock.py status <lockfile>
```

to inspect drift.

## Compounding review

Subsequent review passes should update the existing lockfile instead of replacing it from scratch. A later pass can:

- trust previously normalized structure
- inspect earlier review passes
- focus on unresolved findings
- detect source or codebase drift before spending effort

## Relationship to Beads JSON

The lockfile is not the Beads import payload.

Preferred workflow:

1. review markdown plan
2. write or update `.beads/plan-locks/<stem>.lock.json`
3. materialize `.beads/plans/<stem>.json`
4. validate, dry-run, and import the materialized JSON

Never hand-edit the materialized JSON. Regenerate it from the lockfile.
