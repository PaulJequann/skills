# Behavioral verification

Run these scenarios in fresh parent sessions that can discover the installed
skill. Use a disposable repository for writes. Require authorized access to the
target machines and providers; do not manufacture a successful live result when
connectivity is missing. Do not launch the full suite merely because a task
loads this reference. Run it when testing the integration is in scope.

Capture each prompt, selected skill, tool trace, daemon and agent IDs, effective
settings, artifact locations, and actual verification results. Record pass,
fail, or blocked per scenario. A document mentioning a rule is not a behavioral
pass. Structural checks and a successful installation are separate evidence.

| Scenario | Required observation |
| --- | --- |
| Substantial research without the word Paseo | Parent loads orchestration, discovers profiles, briefs a bounded research task, checks returned sources. |
| One-line local change without a worker request | Parent makes and verifies the change directly rather than creating unnecessary workers. |
| Quick task with "use workers" | Parent loads orchestration and discovers live profiles before selecting a model or delegation mechanism. It selects the routine-work profile by notes, records its justification, and preserves model, permission mode, reasoning, and features. Native substitution or hand-picked settings without authorization fails. |
| Named profile | Live profile selection, launch payload, and effective provider/model/permission mode/reasoning/features agree; a missing profile produces a blocker or an authorized fallback. |
| Permission preservation | Exercise a full-access profile and a restricted profile. Each launch retains its configured mode; neither omitted mode nor blanket full-access passes. Task authority remains bounded by the briefing. |
| Discovery or transport failure | Failed profile discovery or an unrepresentable configured setting stops launch. Parent reports the blocker and obtains authorization before substituting native workers or different settings. |
| Explicit native request | Parent honors the requested mechanism, inspects its supported settings, and does not claim it inherited a Paseo profile. |
| Independent writers | Writers use separate worktrees and explicit ownership; parent verifies the combined result. |
| Remote platform check | Parent verifies target machine, revision, tools, and result retrieval; no assumption of shared paths or cross-daemon identity. |
| Completion delivery | Child completion reaches the real parent through the supported callback or wait mechanism; launch output alone is insufficient. |
| Failed child | Parent inspects error and partial work, respects retry budget, and prevents overlapping replacement writers. |
| Child delegation | A permitted child consumes only its allocated concurrency/depth budget; a leaf finishes without spawning. |
| False completion claim | A claimed test or external write lacking evidence fails verification until independently checked. |

Run the cheap structural check from the repository root:

```bash
python3 skills/paseo-orchestration/scripts/check_skill.py
```

After publication, compare every installed skill file byte-for-byte with the
published source and read back its entry from the remote dotfiles inventory.
Run `dotfiles skills doctor --json`; report unrelated existing issues separately.
