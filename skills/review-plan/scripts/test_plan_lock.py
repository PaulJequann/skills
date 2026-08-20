#!/usr/bin/env python3
"""Tests for plan-lock.py."""

import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from argparse import Namespace


def load_plan_lock_module():
    script_path = os.path.join(os.path.dirname(__file__), "plan-lock.py")
    spec = importlib.util.spec_from_file_location("plan_lock", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_plan():
    return """# Sample Implementation Plan

## Purpose

Validate plan lock generation.

## Research inputs

- `docs/example.md` — sample input

## Locked decisions

### Shape

- Use one slice

## Scope

### In scope

- Lock generation

### Out of scope

- Real import

## Cross-cutting constraints

- Keep the sample small

## Implementation slices

### 1.0 — Example slice

Create the example surface.

Key work:

- Build the example

Acceptance:

- Example task exists

#### Task spec
```yaml
slice_key: example_slice
blockedBy: []
touches:
  - src/example
beads:
  - key: implement_example
    title: Implement example behavior
    type: task
    blockedBy: []
    files:
      - src/example.ts
    verification:
      - src/example.test.ts
    skills:
      - /logging-best-practices
    logging: true
    done_when:
      - Example behavior exists
```

## Suggested task order

1. Example slice

## Deliverables

- A lockfile

## Review checkpoint

- Confirm the lockfile captures provenance
"""


class TestPlanLock(unittest.TestCase):
    def test_default_lockfile_path_uses_repo_local_beads_directory(self):
        plan_lock = load_plan_lock_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, ".git"), exist_ok=True)
            os.makedirs(os.path.join(tmpdir, "docs", "plans"), exist_ok=True)
            markdown_path = os.path.join(tmpdir, "docs", "plans", "sample-plan.md")
            with open(markdown_path, "w") as f:
                f.write(sample_plan())

            output_path = plan_lock.default_lockfile_path(markdown_path)

            self.assertEqual(
                output_path,
                os.path.join(
                    tmpdir, ".beads", "plan-locks", "sample-plan.lock.json"
                ),
            )

    def test_cmd_build_without_output_writes_default_lockfile(self):
        plan_lock = load_plan_lock_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, ".git"), exist_ok=True)
            os.makedirs(os.path.join(tmpdir, "docs", "plans"), exist_ok=True)
            os.makedirs(os.path.join(tmpdir, "src"), exist_ok=True)
            with open(os.path.join(tmpdir, "src", "example.ts"), "w") as f:
                f.write("export const example = true\n")
            with open(os.path.join(tmpdir, "src", "example.test.ts"), "w") as f:
                f.write("test('example', () => {})\n")

            markdown_path = os.path.join(tmpdir, "docs", "plans", "sample-plan.md")
            with open(markdown_path, "w") as f:
                f.write(sample_plan())

            args = Namespace(source=markdown_path, output=None, reviewer="review-plan")
            plan_lock.cmd_build(args)

            expected_lock = os.path.join(
                tmpdir, ".beads", "plan-locks", "sample-plan.lock.json"
            )
            self.assertTrue(os.path.exists(expected_lock))

    def test_default_lockfile_collision_requires_explicit_override(self):
        plan_lock = load_plan_lock_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, ".git"), exist_ok=True)
            os.makedirs(os.path.join(tmpdir, "docs", "plans"), exist_ok=True)
            os.makedirs(os.path.join(tmpdir, "docs", "archive"), exist_ok=True)

            first_path = os.path.join(tmpdir, "docs", "plans", "sample-plan.md")
            second_path = os.path.join(tmpdir, "docs", "archive", "sample-plan.md")
            for path in (first_path, second_path):
                with open(path, "w") as f:
                    f.write(sample_plan())

            plan_lock.cmd_build(
                Namespace(source=first_path, output=None, reviewer="review-plan")
            )

            with self.assertRaises(ValueError):
                plan_lock.cmd_build(
                    Namespace(source=second_path, output=None, reviewer="review-plan")
                )

    def test_build_lock_from_markdown_includes_compiled_plan_and_fingerprints(self):
        plan_lock = load_plan_lock_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = os.path.join(tmpdir, "src")
            os.makedirs(src_dir, exist_ok=True)
            source_file = os.path.join(src_dir, "example.ts")
            with open(source_file, "w") as f:
                f.write("export const example = true\n")

            test_file = os.path.join(src_dir, "example.test.ts")
            with open(test_file, "w") as f:
                f.write("test('example', () => {})\n")

            markdown_path = os.path.join(tmpdir, "sample-plan.md")
            with open(markdown_path, "w") as f:
                f.write(sample_plan())

            lock = plan_lock.build_lock(markdown_path, reviewer="review-plan")

            self.assertEqual(lock["lockfile_version"], 1)
            self.assertEqual(lock["source"]["type"], "markdown")
            self.assertEqual(lock["review"]["passes"][0]["reviewer"], "review-plan")
            self.assertEqual(lock["compiled_plan"]["items"][0]["key"], "example_slice")

            fingerprint_paths = [entry["path"] for entry in lock["fingerprints"]["files"]]
            self.assertIn("src/example.ts", fingerprint_paths)

            file_entry = next(
                entry
                for entry in lock["fingerprints"]["files"]
                if entry["path"] == "src/example.ts"
            )
            self.assertTrue(file_entry["exists"])
            self.assertEqual(file_entry["sha256"], hashlib.sha256(b"export const example = true\n").hexdigest())

    def test_lock_status_detects_source_drift(self):
        plan_lock = load_plan_lock_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "src"), exist_ok=True)
            with open(os.path.join(tmpdir, "src", "example.ts"), "w") as f:
                f.write("export const example = true\n")
            with open(os.path.join(tmpdir, "src", "example.test.ts"), "w") as f:
                f.write("test('example', () => {})\n")

            markdown_path = os.path.join(tmpdir, "sample-plan.md")
            with open(markdown_path, "w") as f:
                f.write(sample_plan())

            lock_path = os.path.join(tmpdir, "plan.lock.json")
            plan_lock.write_lock(
                lock_path,
                plan_lock.build_lock(markdown_path, reviewer="review-plan"),
            )

            with open(markdown_path, "a") as f:
                f.write("\nExtra line.\n")

            status = plan_lock.lock_status(lock_path)

            self.assertEqual(status["status"], "drifted")
            self.assertTrue(status["source_drift"])

    def test_lock_status_detects_referenced_file_drift(self):
        plan_lock = load_plan_lock_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "src"), exist_ok=True)
            source_file = os.path.join(tmpdir, "src", "example.ts")
            with open(source_file, "w") as f:
                f.write("export const example = true\n")
            with open(os.path.join(tmpdir, "src", "example.test.ts"), "w") as f:
                f.write("test('example', () => {})\n")

            markdown_path = os.path.join(tmpdir, "sample-plan.md")
            with open(markdown_path, "w") as f:
                f.write(sample_plan())

            lock_path = os.path.join(tmpdir, "plan.lock.json")
            plan_lock.write_lock(
                lock_path,
                plan_lock.build_lock(markdown_path, reviewer="review-plan"),
            )

            with open(source_file, "w") as f:
                f.write("export const example = false\n")

            status = plan_lock.lock_status(lock_path)

            self.assertEqual(status["status"], "drifted")
            self.assertIn("src/example.ts", status["changed_files"])

    def test_rebuild_preserves_existing_review_passes(self):
        plan_lock = load_plan_lock_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, "src"), exist_ok=True)
            with open(os.path.join(tmpdir, "src", "example.ts"), "w") as f:
                f.write("export const example = true\n")
            with open(os.path.join(tmpdir, "src", "example.test.ts"), "w") as f:
                f.write("test('example', () => {})\n")

            markdown_path = os.path.join(tmpdir, "sample-plan.md")
            with open(markdown_path, "w") as f:
                f.write(sample_plan())

            first = plan_lock.build_lock(markdown_path, reviewer="review-plan-pass-1")
            second = plan_lock.build_lock(
                markdown_path,
                reviewer="review-plan-pass-2",
                existing_lock=first,
            )

            reviewers = [entry["reviewer"] for entry in second["review"]["passes"]]
            self.assertEqual(reviewers, ["review-plan-pass-1", "review-plan-pass-2"])


if __name__ == "__main__":
    unittest.main()
