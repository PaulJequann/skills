---
name: effect-atom-review
description: Review Effect Atom and React integrations for state ownership, identity isolation, retention, and async command races. Use when changes touch Atoms or UI state connected to Effect services.
---

# Effect Atom review

Review Atom state and React bindings, with Effect 4.1 as the API baseline. Check unfamiliar behavior against the project's Atom and React binding sources.

## Review procedure

1. Read the diff, applicable state conventions, and affected consumers. Identify who writes each value and how long it must survive.
2. Trace atom creation, registry ownership, service connections, and command completion. Follow identity changes and unmounts as well as the normal render path.
3. Report only concrete state failures or material ownership problems. Check ancestor providers, existing stores, and service state publications before proposing a new owner.

Review without editing. Stay within the requested scope.

## State ownership

- Keep one authority for each fact. Independently writable copies in a service, atom, context, and component can diverge. A one-way subscription into React is an adapter, not automatically another authority.
- Services can own business transitions and external events; atoms can project service state and invoke commands. Atoms can also directly own shared drafts, filters, and selections without a wrapper service.
- Local React state fits disposable presentation state owned by one component. Examine shared, retained, externally updated, or synchronized state for ownership gaps. An existing route loader or query cache may already supply the right owner.
- Keep related facts together when they must survive together. Retaining a draft while losing its editing mode on unmount can change the meaning of the saved value.

## Identity and lifetime

- Check construction sites. Recreating atoms during render can reset state or repeat work; creating a factory once can capture stale props. Trace memoization and keyed ancestor remounts before reporting either.
- Verify isolation across users, tenants, queries, and server requests. Identity changes must dispose, reset, or separate protected state. A process-global registry must not share user data across requests.
- `Atom.family` compares keys structurally with Effect `Equal`, so equal plain objects and arrays return the same atom even with different references. Include every input that determines the result in the key. Mutable keys or changing values captured outside the key can defeat otherwise correct keying.
- When the last subscriber and dependent leave, removal is scheduled subject to retention and idle-TTL settings. `Atom.keepAlive` returns a copy that stays cached and mounted; it does not persist data or start work before the first read, and the returned copy must be the atom consumers use.
- Follow registry disposal, runtime disposal, and subscription cleanup. Work meant to survive navigation needs an owner beyond the screen; work belonging to an obsolete session must end with that session.
- Check actual resource acquisition before alleging duplicate runtimes. Multiple runtime atoms wrapping an already-owned service do not necessarily create multiple connections.

## Reads and commands

- Read reactive dependencies through the tracking mechanism. Captured snapshots and untracked reads can leave derived state stale. Check writes during render or derived reads for feedback loops and repeated side effects.
- Preserve meaningful initial, failure, success, and refresh states. A stale success while refreshing can be intentional. An empty fallback is misleading when it hides actionable failure or claims authoritative emptiness.
- `Atom.fn` interrupts the previous run on a new write by default; check `concurrent` and interruption settings before relying on that behavior. Loading flags and reservations need interruption-safe settlement, and an old finalizer must not reset a newer command's state.
- Trace out-of-order completions. Older requests must not overwrite newer results, clear newer drafts, or publish into a changed identity. React setters in `promise` or `promiseExit` mode observe the atom's next settled result, not necessarily that write's result. Distinguish a tap, command acceptance, and committed success.
- Check invalidation and optimistic updates against the affected identities. Failed commands should preserve recoverable input and expose failure through the owning state or result channel.
- Prefer focused subscriptions when a concrete dependency path shows unnecessary recomputation. Avoid speculative performance findings.

## Findings

Use the requested output format. For each finding, name the location, event sequence, incorrect state, and smallest ownership or lifetime correction. Identify a focused check such as identity switching, unmount/remount, failed refresh, cancellation, or out-of-order completion. Distinguish source reasoning from reproduced behavior and consolidate symptoms with one root cause. Do not recommend Atoms solely for uniformity.
