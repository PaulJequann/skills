---
name: effect-adoption-review
description: Review code for worthwhile Effect, Schema, and Atom adoption that removes duplicated infrastructure or recurring failure modes. Use for architecture and simplification reviews, including code that does not yet use Effect.
---

# Effect adoption review

Identify small adoption steps that remove demonstrated complexity. Use Effect 4.1 capabilities as a reference. When Effect is installed, check API recommendations against the project's version.

## Review procedure

1. Read the requested code and its callers. Identify repeated infrastructure, unclear ownership, or a concrete failure that the current design makes difficult to prevent.
2. Compare an Effect-based solution with the smallest ordinary TypeScript or existing-library solution. Account for guarantees already supplied by the framework.
3. Establish which code or state the adoption would eliminate and whether the remaining design is simpler.

Review without editing or adding dependencies. Keep recommendations within the requested scope. Missing Effect imports alone are not a problem.

## Look for useful adoption boundaries

| Existing burden | Candidate | Check before recommending |
| --- | --- | --- |
| Repeated error classification and recovery around I/O | Typed errors and handlers | Would a tagged result at one boundary suffice? |
| Abort trees, listener cleanup, and task registries | Scopes and structured concurrency | Does the framework already own cancellation correctly? |
| Duplicated retry, deadline, and polling logic | Schedule and Effect interruption | Are writes idempotent, and who already owns retries? |
| Asserted JSON and separately maintained validators/types | Schema | Is validation already guaranteed upstream? |
| Global dependencies and elaborate module mocks | Services and layers | Would a function parameter provide the seam? |
| In-flight maps, TTL timers, and cache coordination | Cache and request batching | Can they preserve keys, invalidation, and failure semantics? |
| Conflicting shared state or repeated async UI plumbing | Runtime-backed and derived Atoms | Is an existing store or query cache already authoritative? |
| Manual event buffering and subscription fan-out | Stream, Queue, PubSub, or SubscriptionRef | What ordering, backpressure, and shutdown behavior is required? |

## Evaluate the tradeoff

Describe one migration boundary and its adapter to the existing code. Preserve cancellation, transaction ownership, error mapping, and idempotency. Ordinary fibers and scopes govern in-process work. Durable execution requires an explicitly configured workflow engine and storage; remote-write idempotency and database isolation still need their own guarantees.

Explain what can be deleted and what new runtime, dependency, bundle, and maintenance costs appear. A hand-written loop can be appropriate when it carries state across separate triggers. A pure function, local form state, or working framework lifecycle rarely benefits from an Effect wrapper merely for consistency.

Schema-only adoption or one Effect-owned workflow may be enough. Avoid expanding a local improvement into an application rewrite. Separate the immediate fix for a bug from optional migration work; do not report the same root cause twice.

## Recommendations

Use the requested output format. For each recommendation, give concrete code locations, the existing cost or failure, the smallest adoption step, the simpler alternative, and how to verify preserved behavior. Distinguish an adoption opportunity from a correctness defect. Omit speculative or cosmetic proposals, and say when no adoption step earns its cost.
