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
| One-line local change | Parent makes and verifies the change directly rather than creating unnecessary workers. |
| Named profile | Live profile selection and effective provider/model/reasoning/features agree; missing profile produces an explicit fallback or blocker. |
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
