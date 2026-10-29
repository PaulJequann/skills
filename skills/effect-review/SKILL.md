---
name: effect-review
description: Review Effect code and Schema boundaries for error handling, resource safety, concurrency, and dependency ownership. Use for pre-commit reviews or focused audits of Effect applications.
---

# Effect review

Review modern Effect code, with Effect 4.1 as the API baseline. Check unfamiliar APIs against the project's package source and shipped guidance.

## Review procedure

1. Read the diff and applicable project guidance. Follow affected callers, service composition, and tests until you can identify the inputs, runtime owner, and observable result.
2. Apply the relevant checks below to each changed behavior. Trace failure and interruption paths as carefully as success paths.
3. Check whether surrounding code already supplies the guarantee you think is missing. Discard candidates that do not survive that check.

Review without editing. Stay within the requested scope; use unchanged code to establish consequences rather than collect unrelated debt. Treat repository conventions as local requirements, not universal Effect rules.

## Execution and services

- Keep side effects inside execution. A Promise started before an effect is constructed escapes its retry and interruption policies; wrapping that Promise later does not make the operation lazy or repeatable.
- Check that intended work is yielded, composed, or run. Constructing an effect and discarding it, or returning it as a success value, does not execute that work.
- Inspect runtime execution inside services. Nested `runPromise`, `runFork`, or a new runtime can lose the caller's services, scope, or cancellation. Framework callbacks and application entry points legitimately run effects.
- Trace layer construction and memoization. Within a shared memo map, layers memoize by object reference; creating distinct layer instances can duplicate acquisition, while `Layer.fresh` bypasses sharing deliberately. `Layer.succeed` can legitimately expose an already-owned service.
- Check that dependencies come from the intended layer. Captured globals can bypass request-specific or test services.
- Keep layer acquisition finite. Start long-lived work under its owning scope rather than blocking layer construction forever. Dispose owned runtimes at shutdown.

## Failures and recovery

- Match effect constructors to the failure contract. `Effect.promise` treats rejection as a defect; `Effect.tryPromise` can map expected rejection into the typed error channel. Likewise, exceptions thrown inside `Effect.sync` are defects, not declared domain failures.
- Preserve distinctions callers act on. Flattening errors into strings or erasing the error type can break recovery, retry, and UI decisions. Prefer typed handlers when they preserve those distinctions; an exhaustive switch is not inherently wrong.
- Distinguish expected failures, defects, and interruption. Broad cause recovery must not silently convert cancellation or a programming defect into ordinary success.
- Follow what happens after a catch. A failed write or cleanup must not authorize later work that assumes it succeeded. An empty catch can be legitimate when another state channel already reports failure or the operation is explicitly best-effort.
- Inspect success values too. `Effect.asVoid` preserves failures but discards statuses that may distinguish completion from refusal or partial success.
- Check retry eligibility, delay, bounds, and total deadline. Retrying does not make remote writes idempotent. Account for retries already owned by an SDK or workflow platform. An interruptible reconnect loop can intentionally run indefinitely.
- Preserve useful diagnostic causes internally and safe errors externally. Schema issues and serialized errors can contain credentials or payloads; typed errors are not automatically safe to expose.

## Lifetimes and concurrency

- Follow acquisition through success, failure, interruption, and partial initialization. A finalizer must belong to the resource's useful lifetime. Attaching a per-operation resource to an application scope can retain it long after use.
- Inspect flags, reservations, and in-flight entries set before suspension. Typed-error handlers do not settle interruption. Cleanup must run when needed and must not clear a newer operation's state.
- Give background fibers an owner, shutdown path, and deliberate failure policy. Detached work needs an application-level owner, not merely a way around a scope requirement.
- Follow cancellation through Promise and callback adapters. Check abort-signal propagation and listener cleanup. `Effect.promise` and `Effect.tryPromise` hand the signal only to a thunk that declares it as an ordinary parameter; rest or defaulted parameters receive `undefined`, and an operation that never reads the signal keeps running after interruption. Cancellation cannot undo a remote side effect that already committed.
- Check read-modify-write sequences across yields. A `Ref` containing a mutable object does not make arbitrary mutation atomic. Inspect lock duration and interruption, especially when locks span I/O.
- Bound parallel work according to resource capacity. A small fixed fan-out can be safe; dependent operations may require sequencing.
- Trace stream consumption, backpressure, and shutdown. Queues can strand producers when consumers stop. Creating a stream does not consume it.
- Check cache keys, invalidation, and scope against the values that determine the result, including tenant or user identity. `Cache` stores failed lookup results too; verify that the TTL and invalidation policy do not keep serving a transient failure after recovery.

## Schema boundaries

- Decode untrusted input before treating it as a domain value. Assertions, generic JSON return types, and branded casts do not validate input.
- Validate the invariant needed by the next action. A partial schema can accept an object without proving it is complete enough to authorize deletion, persistence, or another sensitive transition.
- Pass the decoded value onward. Validating a projection does not protect a later write that spreads the original unknown object. Check excess-property handling against the write policy.
- Match the producer's contract, including legal nulls, missing keys, scalar variants, and identifiers. Choose per-item recovery or whole-batch rejection according to consistency requirements.
- Keep encoded and decoded forms distinct. Check transformation direction, outbound encoding, and round trips for persisted values. Missing keys, explicit `undefined`, and `null` are different contracts.
- Reuse schemas for the same meaning. Duplicated types, literals, and validation rules can drift. Internal validated values do not need repeated decoding; distinct projections can have distinct contracts.
- Use brands to prevent meaningful identifier confusion, not as a substitute for format validation or authorization.
- Check compatibility fallbacks against data actual writers produce. Permissive decoding must not silently turn corruption into valid state.

## Verification and findings

For a suspected lifecycle or ordering bug, identify a focused check that interrupts, fails, or reorders the affected operation. Prefer test layers and controlled time over mocking Effect internals or waiting arbitrary durations.

Report findings in impact order using the requested format. Each finding needs a location, concrete failure or material maintenance consequence, supporting trace, and smallest remedy. Include a discriminating test when useful. Separate project-convention violations from correctness bugs, consolidate shared root causes, and state when a conclusion depends on evidence you could not verify. If nothing meets that bar, say so.
