# Initiative Plan: Claim mode contract hard fork

## Initiative snapshot

- **Name / Code**: Claim Mode Contract Hard Fork (`CLAIM_MODE_V1`)
- **Target release / milestone**: `0.5.0-beta.5` follow-up (or next beta cut)
- **Owner / driver(s)**: ChoreOps maintainers
- **Status**: Complete

## Summary & immediate steps

| Phase / Step                         | Description                                                                | % complete | Quick notes                                                     |
| ------------------------------------ | -------------------------------------------------------------------------- | ---------- | --------------------------------------------------------------- |
| Phase 1 – Contract foundation        | Replace blocker enum contract with canonical claim mode enum               | 100%       | Constants/contract migrated; validation gates passed            |
| Phase 2 – Backend contract adoption  | Publish `claim_mode` in status context and sensor attributes               | 100%       | Context + sensor + translations migrated; can_claim gate intact |
| Phase 3 – Test matrix migration      | Convert assertions from `block_reason` to `claim_mode` matrix expectations | 100%       | Claim-mode assertions centralized; targeted regression green    |
| Phase 4 – Docs and release readiness | Update docs/changelog and complete release checklist                       | 100%       | Architecture/standards/release checklist updated                |

1. **Key objective** – Make `claim_mode` the single interaction contract for claim UX, with `can_claim` as derived convenience only.
2. **Summary of recent work** – Research completed for constants, status context, sensor attributes, translation keys, and test usage hotspots.

- Deferred unfinished scope from [CHORE_CLAIM_CONTRACT_UNIFICATION_IN-PROCESS.md](CHORE_CLAIM_CONTRACT_UNIFICATION_IN-PROCESS.md) is now tracked here.

3. **Next steps (short term)** – Execute contract rename/mapping in core files, preserving existing claim flow and adding explicit `steal_available` mapping.
4. **Risks / blockers** – Rotation edge paths (`allow_steal`, `not_my_turn`, `waiting`) require focused regression coverage.
5. **References**
   - [ARCHITECTURE.md](../ARCHITECTURE.md)
   - [DEVELOPMENT_STANDARDS.md](../DEVELOPMENT_STANDARDS.md)
   - [CODE_REVIEW_GUIDE.md](../CODE_REVIEW_GUIDE.md)
   - [AGENT_TEST_CREATION_INSTRUCTIONS.md](../../tests/AGENT_TEST_CREATION_INSTRUCTIONS.md)
   - [RELEASE_CHECKLIST.md](../RELEASE_CHECKLIST.md)
6. **Decisions & completion check**

- **Decisions captured**: Hard fork confirmed; no legacy compatibility path; `claim_mode` normalization follows existing centralized claim logic with explicit `steal_available` additive mapping.
- **Completion confirmation**: `[x]` All follow-up items completed (architecture updates, cleanup, documentation, tests) before owner approval.

## Tracking expectations

- **Summary upkeep**: Update this file after each implementation PR lands (backend contract, tests, docs).
- **Detailed tracking**: Keep mode taxonomy and migration edge cases in the phase sections below.

## Detailed phase tracking

### Phase 1 – Contract foundation

- **Goal**: Define and freeze the canonical claim interaction contract (`claim_mode`) and replace block-reason-centric contract primitives.
- **Steps / detailed work items**
  - [x] Add canonical `claim_mode` constants and set in [custom_components/choreops/const.py](../../custom_components/choreops/const.py#L1867-L1919) (replace `CHORE_BLOCK_REASON_*` and `CHORE_CTX_BLOCK_REASON` usage contract with `CHORE_CLAIM_MODE_*` and `CHORE_CTX_CLAIM_MODE`).
  - [x] Add/rename entity attribute constant in [custom_components/choreops/const.py](../../custom_components/choreops/const.py#L2494) from `ATTR_CHORE_BLOCK_REASON` to `ATTR_CHORE_CLAIM_MODE`.
  - [x] Update status-context contract documentation in [custom_components/choreops/managers/chore_manager.py](../../custom_components/choreops/managers/chore_manager.py#L3598-L3623) to list `claim_mode` and remove `block_reason` references.
  - [x] Define explicit mapping table in code comments/docstring for actionable vs blocked modes near [custom_components/choreops/managers/chore_manager.py](../../custom_components/choreops/managers/chore_manager.py#L3722-L3751) (including `steal_available`).
  - [x] Add translation key constants for any new labels/messages in [custom_components/choreops/const.py](../../custom_components/choreops/const.py#L3035-L3050), reusing existing `TRANS_KEY_ERROR_CHORE_*` when semantics match.
  - [x] Keep `CHORE_CTX_CAN_CLAIM_ERROR` as-is for this hard fork and document revisit criteria for later simplification.
- **Key issues**
  - Hard fork means immediate contract switch; downstream templates/tests must migrate in the same release branch.

### Phase 2 – Backend contract adoption

- **Goal**: Publish `claim_mode` as the primary interaction signal in integration entities and context contracts.
- **Steps / detailed work items**
  - [x] Replace error→block mapping logic in [custom_components/choreops/managers/chore_manager.py](../../custom_components/choreops/managers/chore_manager.py#L3722-L3751) with mode resolution (`claimable`, `steal_available`, blocked modes).
  - [x] Update `available_at` derivation to key off waiting mode in [custom_components/choreops/managers/chore_manager.py](../../custom_components/choreops/managers/chore_manager.py#L3734-L3738).
  - [x] Publish `claim_mode` attribute in [custom_components/choreops/sensor.py](../../custom_components/choreops/sensor.py#L1015-L1050) and remove `block_reason` emission.
  - [x] Update translation attribute section in [custom_components/choreops/translations/en.json](../../custom_components/choreops/translations/en.json#L3317-L3330) from `block_reason` state map to `claim_mode` state map.
  - [x] Keep `can_claim` as the single action gate (`True/False`), derived from mode with no alternate behavior path.
  - [x] Implement `steal_available` as a small additive mapping on top of existing logic (no claim path divergence).
- **Key issues**
  - Avoid logic diversion: prioritize rename/normalization + minimal mapping changes over behavior rewrites.

### Phase 3 – Test matrix migration

- **Goal**: Convert and extend tests to validate `claim_mode` as canonical contract and preserve behavior parity.
- **Steps / detailed work items**
  - [x] Replace `block_reason` assertions with `claim_mode` assertions in rotation FSM tests at [tests/test_rotation_fsm_states.py](../../tests/test_rotation_fsm_states.py#L56-L170).
  - [x] Update due-window/availability tests in [tests/test_chore_scheduling.py](../../tests/test_chore_scheduling.py#L3061-L3214) to assert waiting via `claim_mode` and verify `available_at` only for waiting mode.
  - [x] Update rotation steal-window behavior tests in [tests/test_workflow_chores.py](../../tests/test_workflow_chores.py#L1258-L1337) to assert `steal_available` mode when claim unlocks for non-turn assignees.
  - [x] Add focused manager-context unit assertions around [custom_components/choreops/managers/chore_manager.py](../../custom_components/choreops/managers/chore_manager.py#L3598-L3751) for each canonical mode.
  - [x] Ensure helper constants consumed by tests are updated (tests import from `tests.helpers`, not integration const directly) per [AGENT_TEST_CREATION_INSTRUCTIONS.md](../../tests/AGENT_TEST_CREATION_INSTRUCTIONS.md).
  - [x] Validate no remaining direct expectation of `block_reason` in tests.
- **Key issues**
  - Highest regression risk is rotation + overdue + turn-holder interactions where mode can become actionable (`steal_available`).

### Phase 4 – Docs and release readiness

- **Goal**: Finalize documentation, migration notes, and release checks for the hard fork.
- **Steps / detailed work items**
  - [x] Add architecture note in [docs/ARCHITECTURE.md](../ARCHITECTURE.md) clarifying channel separation: `state`/`global_state` (display lane) vs `claim_mode` (interaction lane).
  - [x] Update coding contract references in [docs/DEVELOPMENT_STANDARDS.md](../DEVELOPMENT_STANDARDS.md) to remove `block_reason` guidance.
  - [x] Record hard-fork migration note in changelog/release notes and [docs/RELEASE_CHECKLIST.md](../RELEASE_CHECKLIST.md).
  - [x] Confirm schema impact: **No storage schema bump needed** because change is derived runtime context/attributes only (no `.storage/choreops/choreops_data` structural change).
  - [x] Close initiative after ChoreOps docs/tests/release checks are complete.
- **Key issues**
  - Contract wording must stay precise so downstream consumers can adopt without ambiguity.

## Testing & validation

- Planned validation commands for implementation handoff:
  - `./utils/quick_lint.sh --fix`
  - `mypy custom_components/choreops/`
  - `python -m pytest tests/ -v --tb=line`
  - `mypy tests/`
- Baseline status (owner-confirmed): full test suite was run and passing before this change set.
- Strategy mode note: Phase 3 used lint + targeted tests only per owner direction.
- Targeted validation result: `tests/test_rotation_fsm_states.py`, `tests/test_rotation_services.py`, `tests/test_workflow_chores.py`, `tests/test_chore_scheduling.py`, and `tests/test_workflow_notifications.py` passed (158 passed, 0 failed).

## Notes & follow-up

- Canonical claim mode taxonomy proposed for v1:
  - `claimable`
  - `steal_available`
  - `blocked_not_my_turn`
  - `blocked_waiting_window`
  - `blocked_pending_claim`
  - `blocked_already_approved`
  - `blocked_completed_by_other`
  - `blocked_missed_locked`
- Recommended derivation rule: `can_claim = claim_mode in {claimable, steal_available}`.
- Transitional compatibility is intentionally omitted per hard-fork requirement.
- Normalization principle: preserve existing claim/error behavior and implement `claim_mode` as a canonical naming/mapping layer with minimal logic changes.

## Locked decisions (owner confirmed)

- [x] Use explicit blocked mode naming (`blocked_*`) plus actionable `claimable` and `steal_available`.
- [x] Keep `CHORE_CTX_CAN_CLAIM_ERROR` for now (current wiring stays intact for this release).
- [x] Treat `steal_available` as the primary reason for this change and implement as explicit actionable mode.
- [x] Remove `CHORE_BLOCK_REASON_*` contract immediately (hard fork, no legacy alias path).
- [x] Use single-path derivation centered on existing `can_claim` flow and current centralized mapping logic.

## Focused follow-up: `can_claim_error` revisit criteria

- Keep `can_claim_error` in this release because service-layer/user-facing error messaging already consumes translation keys directly.
- Revisit only after `claim_mode` rollout is stable and tests prove no regressions across rotation/waiting/steal cases.
- Revisit trigger checklist:
  - [ ] `claim_mode` values fully replace interaction decisions in status context and sensor attributes.
  - [ ] No service path relies on bespoke error semantics beyond mode-derived outcomes.
  - [ ] Translation mapping from mode-to-error can be made 1:1 without special-case branches.
  - [x] Test matrix passes with mode-first assertions and unchanged claim action behavior.
