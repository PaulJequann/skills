#!/usr/bin/env python3
"""Build and inspect plan lockfiles."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path


def load_beads_batch_module():
    script_path = (
        Path(__file__).resolve().parents[2]
        / "beads-batch"
        / "scripts"
        / "beads-batch.py"
    )
    spec = importlib.util.spec_from_file_location("beads_batch", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bb = load_beads_batch_module()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    with open(path, "rb") as f:
        return sha256_bytes(f.read())


def sha256_json(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256_bytes(payload)


def find_project_root(source_path):
    current = Path(source_path).resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return str(candidate)
    return str(current)


def normalize_source_path(path, root):
    return os.path.relpath(os.path.abspath(path), root)


def default_lockfile_path(source_path):
    resolved = os.path.abspath(source_path)
    root = find_project_root(resolved)
    filename = f"{Path(resolved).stem}.lock.json"
    return os.path.join(root, ".beads", "plan-locks", filename)


def load_source_plan(source_path):
    if source_path.endswith((".md", ".markdown")):
        compiled = bb.extract_markdown_plan(source_path)
        compiled.pop("_warnings", None)
        return compiled, "markdown"
    if source_path.endswith(".json"):
        return bb.load_plan_file(source_path), "json"
    raise ValueError(f"Unsupported plan source: {source_path}")


def extract_referenced_paths(source_path, compiled_plan, source_type):
    if source_type == "markdown":
        with open(source_path) as f:
            text = f.read()
        slices = bb._parse_markdown_task_specs(text)
        paths = []
        for slice_data in slices:
            spec = slice_data.get("task_spec") or {}
            for bead in spec.get("beads", []):
                paths.extend(_concrete_paths(bead.get("files", [])))
                paths.extend(_concrete_paths(bead.get("verification", [])))
        return sorted(set(paths))

    paths = []
    for item in compiled_plan.get("items", []):
        description = item.get("description", "")
        paths.extend(_extract_paths_from_description_section(description, "Files:"))
        paths.extend(
            _extract_paths_from_description_section(description, "Verification:")
        )
    return sorted(set(paths))


def _concrete_paths(values):
    concrete = []
    for value in values:
        if not isinstance(value, str):
            continue
        if any(token in value for token in "*?[]"):
            continue
        if _looks_like_path(value):
            concrete.append(value)
    return concrete


def _extract_paths_from_description_section(description, heading):
    lines = description.splitlines()
    in_section = False
    values = []
    for line in lines:
        stripped = line.strip()
        if stripped == heading:
            in_section = True
            continue
        if in_section and stripped.endswith(":") and not stripped.startswith("- "):
            break
        if in_section and stripped.startswith("- "):
            candidate = stripped[2:].strip()
            if _looks_like_path(candidate) and not any(
                token in candidate for token in "*?[]"
            ):
                values.append(candidate)
    return values


def _looks_like_path(value):
    return "/" in value or value.endswith((".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".md", ".json", ".yaml", ".yml"))


def fingerprint_files(root, paths):
    fingerprints = []
    for rel_path in paths:
        abs_path = os.path.join(root, rel_path)
        exists = os.path.exists(abs_path)
        fingerprints.append(
            {
                "path": rel_path,
                "exists": exists,
                "sha256": sha256_file(abs_path) if exists else None,
            }
        )
    return fingerprints


def build_lock(source_path, reviewer="review-plan", existing_lock=None):
    resolved = os.path.abspath(source_path)
    root = find_project_root(resolved)
    compiled_plan, source_type = load_source_plan(resolved)
    source_rel = normalize_source_path(resolved, root)
    source_hash = sha256_file(resolved)
    compiled_plan_hash = sha256_json(compiled_plan)

    referenced_paths = extract_referenced_paths(resolved, compiled_plan, source_type)
    fingerprints = fingerprint_files(root, referenced_paths)

    existing_passes = []
    if existing_lock:
        existing_passes = list(existing_lock.get("review", {}).get("passes", []))

    review_pass = {
        "reviewer": reviewer,
        "source_sha256": source_hash,
        "compiled_plan_sha256": compiled_plan_hash,
        "accepted_findings": [],
        "skipped_findings": [],
        "unresolved_findings": [],
    }

    return {
        "lockfile_version": 1,
        "source": {
            "path": source_rel,
            "type": source_type,
            "sha256": source_hash,
        },
        "compiled_plan": compiled_plan,
        "compiled_plan_sha256": compiled_plan_hash,
        "fingerprints": {
            "root": root,
            "files": fingerprints,
        },
        "review": {
            "status": "reviewed",
            "passes": existing_passes + [review_pass],
        },
    }


def write_lock(lock_path, lock):
    os.makedirs(os.path.dirname(os.path.abspath(lock_path)), exist_ok=True)
    with open(lock_path, "w") as f:
        json.dump(lock, f, indent=2)
        f.write("\n")


def load_lock(lock_path):
    with open(lock_path) as f:
        return json.load(f)


def lock_status(lock_path):
    lock = load_lock(lock_path) if isinstance(lock_path, str) else lock_path
    root = lock["fingerprints"]["root"]
    source_abs = os.path.join(root, lock["source"]["path"])
    source_exists = os.path.exists(source_abs)
    current_source_hash = sha256_file(source_abs) if source_exists else None
    source_drift = (
        not source_exists or current_source_hash != lock["source"]["sha256"]
    )

    changed_files = []
    for entry in lock["fingerprints"]["files"]:
        abs_path = os.path.join(root, entry["path"])
        exists = os.path.exists(abs_path)
        current_hash = sha256_file(abs_path) if exists else None
        if exists != entry["exists"] or current_hash != entry["sha256"]:
            changed_files.append(entry["path"])

    return {
        "status": "drifted" if source_drift or changed_files else "ready",
        "source_drift": source_drift,
        "changed_files": changed_files,
    }


def cmd_build(args):
    output_path = (
        os.path.abspath(args.output)
        if args.output
        else default_lockfile_path(args.source)
    )
    existing = None
    if os.path.exists(output_path):
        existing = load_lock(output_path)
        if not args.output:
            current_root = find_project_root(args.source)
            current_source_rel = normalize_source_path(args.source, current_root)
            existing_source_rel = existing.get("source", {}).get("path")
            if existing_source_rel != current_source_rel:
                raise ValueError(
                    "Default lockfile path collision detected; use -o to choose an explicit lockfile path"
                )
    lock = build_lock(args.source, reviewer=args.reviewer, existing_lock=existing)
    if getattr(args, "stdout", False):
        print(json.dumps(lock, indent=2))
        return
    write_lock(output_path, lock)
    print(output_path)


def cmd_status(args):
    print(json.dumps(lock_status(args.lockfile), indent=2))


def main():
    parser = argparse.ArgumentParser(
        prog="plan-lock", description="Build and inspect implementation-plan lockfiles"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_build = subparsers.add_parser("build", help="Build or update a plan lockfile")
    p_build.add_argument("source", help="Path to a markdown or JSON plan")
    p_build.add_argument(
        "-o", "--output", help="Where to write the lockfile (default: .beads/plan-locks/<source-stem>.lock.json)"
    )
    p_build.add_argument(
        "--stdout", action="store_true", help="Print lockfile JSON instead of writing it"
    )
    p_build.add_argument(
        "--reviewer", default="review-plan", help="Reviewer label for this pass"
    )

    p_status = subparsers.add_parser("status", help="Check drift for a lockfile")
    p_status.add_argument("lockfile", help="Path to plan.lock.json")

    args = parser.parse_args()
    try:
        if args.command == "build":
            cmd_build(args)
        elif args.command == "status":
            cmd_status(args)
    except ValueError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
