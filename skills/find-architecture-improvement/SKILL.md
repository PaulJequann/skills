---
name: find-architecture-improvement
description: Find and capture one strong codebase architecture improvement.
---

# Find an architecture improvement

Run a read-only architecture scan, select the strongest untracked deepening
candidate, publish its evidence as a self-contained Stashbox report, and create
one Linear investigation issue containing the report URL.

Invoking this skill authorizes two external writes after a candidate passes all
gates: one new Stashbox artifact and one new Linear issue. Create neither when
no candidate passes. Never modify the repository.

Finish in exactly one state:

- `Captured`: the Stashbox report and verified Linear issue both exist.
- `Already tracked`: a matching Linear issue exists; nothing was published.
- `No strong candidate`: the scan completed without an eligible candidate.
- `Blocked`: routing, access, or artifact delivery prevented capture.
- `Partial`: Stashbox succeeded but Linear creation or verification failed.

## Architecture lens

A **module** has an **interface**, everything a caller must know to use it
correctly, and an **implementation** hidden behind that interface. A module is
**deep** when a small interface exposes substantial behavior. It is **shallow**
when callers must understand nearly as much as the implementation contains.

A **seam** is where behavior can vary without editing the caller. An
**adapter** satisfies an interface at a seam. Depth creates **leverage** for
callers and **locality** for maintainers by concentrating behavior, decisions,
and verification.

Use the deletion test on a suspected shallow module. Imagine deleting it. If
complexity merely spreads back across its callers, the module may earn its
keep. If little disappears and callers become simpler when responsibilities
are regrouped, it is a stronger deepening candidate.

Treat the interface as the test surface. Prefer candidates whose behavior can
be tested through the proposed interface without exposing internal seams.
Require two justified adapters before proposing an adapter seam, normally a
production adapter and a meaningful test adapter.

## 1. Establish the baseline

Read applicable repository instructions. Resolve and record:

- repository and Git remote;
- branch and exact revision;
- dirty paths;
- root and area-specific `CONTEXT.md` files;
- relevant ADRs and design documents;
- recent history and recurring change areas; and
- the configured Linear team and exact repository label.

Use recent history to choose promising search areas. Give more weight to code
that changes repeatedly because deepening pays back through future changes. If
history has no clear hot spot, widen the scan.

Preserve dirty work. Compare a dirty candidate area with `HEAD` and exclude it
when the apparent friction may disappear with the uncommitted work.

Complete this step when each selected search area has a named domain behavior,
relevant decisions, and evidence that it is part of the committed baseline.

## 2. Investigate candidates

Trace real behavior from callers to observable outcomes. Inspect production
code and its tests together. Explore where understanding one domain behavior
requires crossing many modules, where callers repeat implementation knowledge,
where decisions leak across seams, and where tests must reach past the current
interface.

Develop up to four candidate packets. A run may find fewer. Each packet must
contain:

- the domain behavior involved;
- exact files, symbols, callers, and tests;
- the current interface callers must understand;
- implementation knowledge leaking across the seam;
- evidence from history, duplicated decisions, or scattered verification;
- the current test surface and its loss of locality;
- a deepening direction without a final interface design;
- relevant ADRs or ownership constraints;
- the strongest evidence against the candidate; and
- the smallest local alternative that might solve the same problem.

Reject candidates based only on file size, naming, style, generic duplication,
missing abstraction, or a hypothetical future adapter.

Complete this step when every retained candidate has evidence from current
callers and tests, or when the repository cannot support a credible packet.

## 3. Compare and select

Rate each candidate `Strong`, `Medium`, or `Weak` on:

| Dimension | Question |
| --- | --- |
| Evidence | Do callers, tests, and history demonstrate the friction? |
| Depth | Would a smaller interface hide substantial behavior? |
| Locality | Would decisions and verification move into one module? |
| Testability | Could tests exercise behavior through the new interface? |
| Scope | Is one investigation issue enough to bound the work? |
| Timing | Is the area active enough for the change to pay back? |
| Risk | Could an ADR, ownership rule, or active change invalidate it? |

A candidate is eligible only when Evidence, Depth, and Locality are `Strong`,
Scope and Testability are no worse than `Medium`, and Risk has a concrete
answer. Rank eligible candidates by Evidence, then Locality and Depth, then
Scope, then Timing. Compare the winner with creating no issue.

Try to disprove the winner before proceeding:

1. State the strongest reason it may be wrong.
2. Recheck the relevant callers, tests, history, and decisions.
3. State what the current modules already own correctly.
4. Check whether the direction invents a seam with only one real adapter.
5. Check whether the smallest local alternative produces the same payoff.
6. Check whether active work is already removing the friction.

Remove a candidate that fails this challenge and evaluate the next one. Finish
with `No strong candidate` when none survive.

## 4. Backtest the architecture

Test the selected candidate against changes that actually happened. Find three
to five independent commits that changed the candidate's domain behavior.
Prefer behavior changes over mechanical renames, formatting, generated output,
or broad commits whose intent cannot be isolated.

For each commit, inspect the diff and its parent, then record:

- the behavior that changed;
- the modules, callers, and tests that changed with it;
- the interface facts callers had to learn or repeat;
- which changes the proposed deep module would have absorbed;
- which changes would still have crossed its interface;
- any new interface facts the proposal would have introduced; and
- a verdict of `Compressed`, `Unchanged`, or `Worse`.

Judge **change compression** by reduced caller knowledge and fewer places that
encode the same decision. A lower file count or line count is not evidence by
itself. The counterfactual must preserve the behavior and constraints present
at that historical revision rather than assuming today's code existed then.

The candidate passes only when at least two independent commits are
`Compressed` and none shows that the proposal moves equal or greater complexity
into callers or a wider interface. If fewer than two relevant commits exist,
the backtest cannot establish a strong candidate.

Remove a candidate that fails and backtest the next eligible candidate. Finish
with `No strong candidate` when none pass.

Complete this step only when the selected candidate has an auditable table of
historical commits and a passing change-compression verdict.

## 5. Exclude prior work

Search open, completed, and canceled Linear issues in the configured team and
repository. Search with domain concepts, behavior, filenames, and ownership,
not only the proposed title.

If a likely duplicate exists, remove that candidate and evaluate the next
eligible candidate. Finish with `Already tracked` when the existing issue is
the selected work and no other candidate is stronger enough to capture. Return
the existing issue identifier and URL.

Complete this step only when the selected candidate has no likely duplicate.

## 6. Build the HTML report

Create the report only for the selected candidate. Resolve the operating
system's temporary directory and write:

`architecture-candidate-<repository>-<timestamp>.html`

The report must be one portable file. Use inline CSS and inline SVG. Include no
sibling assets, external fonts, CDN scripts, or required network resources.
Escape repository-derived text before inserting it into HTML.

Use an editorial document layout with generous whitespace, restrained color,
and diagrams that carry the architectural explanation. Include:

- repository, branch, exact revision, and scan date;
- candidate name and recommendation strength;
- domain behavior and current ownership;
- exact files, symbols, callers, and tests;
- the current interface and leaked implementation knowledge;
- evidence from recent history;
- the architecture backtest timeline and change-compression table;
- a side-by-side before and after diagram;
- locality, leverage, and testability gains;
- the candidate comparison table and why this candidate won;
- the strongest counterargument and the smallest alternative;
- relevant ADRs and ownership constraints; and
- open questions and scope boundaries.

Keep the proposed interface conceptual. This report supports an investigation;
it does not settle the design or authorize implementation.

Inspect the completed file. Confirm that it opens as standalone HTML, diagrams
render without JavaScript, every path and symbol matches the recorded revision,
and the file contains no credentials, personal data, or sensitive payloads.

Complete this step only when the report passes that inspection.

## 7. Publish to Stashbox

Load and follow `stashbox-artifacts`. Upload the completed HTML as a new stash.
Do not reuse a previous architecture report's viewer URL. Treat the returned
stable viewer URL as the delivered report.

If publication fails, preserve the local HTML, create no Linear issue, and
finish with `Blocked`. Report the upload error and local path.

Complete this step only when Stashbox reports success with a stable viewer URL.

## 8. Create the Linear issue

Load and follow `capture-linear-issue`, including its routing, duplicate search,
template, and verification rules. Create exactly one issue with:

- status `Backlog`;
- readiness `Needs investigation`;
- priority unset;
- the exact repository label; and
- the scanned branch and revision.

Frame the issue as an ownership or investigation problem. Do not claim that the
final interface, migration, or implementation plan has been decided.

Under the issue's `Evidence` heading, include the exact stable viewer URL as a
Markdown link labeled `Architecture candidate report`. Also include the key
files, callers, tests, and history evidence needed to understand why the report
exists. Summarize the architecture backtest and cite the commits that passed or
challenged the change-compression claim.

Re-read the created issue. Verify its title, body, status, labels, readiness,
and that the `Evidence` section contains the exact Stashbox viewer URL.

If creation or verification fails after Stashbox succeeds, do not upload a
replacement report and do not create a replacement issue. Finish with
`Partial`, returning the viewer URL and the exact Linear failure.

Complete this step only when the issue readback contains the exact viewer URL.

## 9. Report the run

Return:

- terminal state;
- repository, branch, and revision;
- selected candidate and why it survived;
- architecture backtest verdict and supporting commits;
- runner-ups and why they lost;
- Stashbox viewer URL when published;
- Linear identifier and URL when created, or the existing duplicate; and
- confirmation that the repository was unchanged.
