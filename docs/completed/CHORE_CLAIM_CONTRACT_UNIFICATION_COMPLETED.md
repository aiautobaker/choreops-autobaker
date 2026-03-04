# Initiative Plan

## Initiative snapshot

- **Name / Code**: Chore claim contract unification (block reason + completed_by normalization)
- **Target release / milestone**: Hard-fork branch next beta cut (`0.5.0-beta.x`)
- **Owner / driver(s)**: ChoreOps core maintainers
- **Status**: Pivoted - remaining scope deferred to claim-mode contract plan

## Summary & immediate steps

| Phase / Step                  | Description                                                               | % complete | Quick notes                                               |
| ----------------------------- | ------------------------------------------------------------------------- | ---------- | --------------------------------------------------------- |
| Phase 0 – Preflight alignment | Freeze contract and file-level boundaries before code edits               | 100%       | Decisions captured in this plan                           |
| Phase 1 – Contract foundation | Rename lock contract to block contract and define enum truth table        | 100%       | Implemented in code; gate failures are external/unrelated |
| Phase 2 – Core behavior       | Wire manager/engine/sensor to publish unified claim-block contract        | 85%        | Remaining work deferred to CLAIM_MODE_CONTRACT_HARD_FORK  |
| Phase 3 – Tests               | Update/add behavioral tests for block reasons and completed_by list shape | 45%        | Remaining work deferred to CLAIM_MODE_CONTRACT_HARD_FORK  |
| Phase 4 – UI + docs           | Update dashboard template consumption and docs/contracts                  | 0%         | Entire phase deferred to CLAIM_MODE_CONTRACT_HARD_FORK    |

1. **Key objective** – Make `can_claim` + `block_reason` the single, consistent claimability contract while keeping `state` display-only.
2. **Summary of recent work**
   - Reviewed current contract in manager context, sensor attributes, engine claim validation, and template usage.
   - Confirmed existing fields available now: `can_claim`, `can_approve`, `can_claim_error`, `approval_period_start`, `completed_by`.
     - Added execution-grade sequencing, acceptance criteria, and non-goals to reduce implementation drift.
     - Prepared builder handoff packet: [CHORE_CLAIM_CONTRACT_UNIFICATION_SUP_BUILDER_HANDOFF.md](CHORE_CLAIM_CONTRACT_UNIFICATION_SUP_BUILDER_HANDOFF.md).
     - Implemented Phase 1 key changes: `block_reason` key rename, blocker enum constants, English translation contract update, and type contract comment updates.
     - Applied requested organization cleanup: moved `CHORE_BLOCK_*` constants into chore constants section and grouped sensor `block_reason` next to `can_claim`/`can_approve`.

3. **Next steps (short term)**
   - Continue implementation under [CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md](CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md).
   - Keep this plan as historical record for already completed hard-fork-block-reason work.
4. **Risks / blockers**
   - Widespread key rename touches tests and dashboard templates.
   - Persisted shape drift for `completed_by` if not normalized at write boundaries.
5. **References**
   - [ARCHITECTURE.md](../ARCHITECTURE.md)
   - [DEVELOPMENT_STANDARDS.md](../DEVELOPMENT_STANDARDS.md)
   - [CODE_REVIEW_GUIDE.md](../CODE_REVIEW_GUIDE.md)
   - [AGENT_TEST_CREATION_INSTRUCTIONS.md](../../tests/AGENT_TEST_CREATION_INSTRUCTIONS.md)
   - [RELEASE_CHECKLIST.md](../RELEASE_CHECKLIST.md)
6. **Decisions & completion check**
   - **Decisions captured**:
     - `can_claim` is the only claim-action gate.
     - `state` is display semantics only.
     - Replace `lock_reason` with `block_reason` everywhere.
     - `can_claim=true` => `block_reason=null`.
     - `can_claim=false` => `block_reason ∈ {completed_by_other, already_approved, pending_claim, waiting, not_my_turn, missed_locked}`.
     - `completed_by` contract is list-of-names in all modes (independent/shared_first/shared_all).
     - Shared progress in UI uses `len(completed_by)` / `len(assigned_user_names)` only (no new progress attrs).
     - Hard fork policy: no backward compatibility support. - Remaining incomplete scope is deferred to [CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md](CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md) due to pivot.
       - **Completion confirmation**: `[x]` Remaining follow-up items deferred to claim-mode pivot plan.

## Pivot/defer notice

- **Pivot target**: [CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md](CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md)
- **Reason**: claim interaction model is moving from `block_reason` contract to canonical `claim_mode` contract.
- **Scope handling**: all unfinished checklist items in this document are treated as deferred and tracked in the pivot plan.

## Tracking expectations

- **Summary upkeep**: Update this file after each meaningful implementation/test milestone.
- **Detailed tracking**: Keep execution details in phase sections below.

## Detailed phase tracking

### Phase 0 – Preflight alignment

- **Goal**: Lock scope before implementation to prevent drift and avoid unnecessary edits.
- **Steps / detailed work items**
  - [x] Confirm hard-fork policy: no backward compatibility, no alias keys, no dual-write behavior.
  - [x] Confirm action contract: `can_claim` gates claim action; `state` remains display semantics only.
  - [x] Confirm blocker enum: `completed_by_other`, `already_approved`, `pending_claim`, `waiting`, `not_my_turn`, `missed_locked`.
  - [x] Confirm shared progress approach: compute from existing lists only (`completed_by` and `assigned_user_names`).
  - [x] Confirm no new progress attributes are added.
- **Key issues**
  - None. Contract is settled and implementation-ready.

### Phase 1 – Contract foundation

- **Goal**: Define and stamp the canonical claim-block contract in constants/types/translations.
- **Steps / detailed work items**
  - [x] Rename context key in [custom_components/choreops/const.py](../../custom_components/choreops/const.py) around lines 1866-1898:
        `CHORE_CTX_LOCK_REASON` → `CHORE_CTX_BLOCK_REASON` and update `CHORE_STATUS_CONTEXT_KEYS`.
        **Acceptance**: no `CHORE_CTX_LOCK_REASON` references remain.
  - [x] Rename attribute key in [custom_components/choreops/const.py](../../custom_components/choreops/const.py) around lines 2468-2472:
        `ATTR_CHORE_LOCK_REASON` → `ATTR_CHORE_BLOCK_REASON`.
        **Acceptance**: no `ATTR_CHORE_LOCK_REASON` references remain.
  - [x] Add explicit blocker-state constants in [custom_components/choreops/const.py](../../custom_components/choreops/const.py) near lines 3008-3034 to avoid string scattering.
        **Acceptance**: manager mapping does not hardcode blocker strings inline.
  - [x] Update [custom_components/choreops/translations/en.json](../../custom_components/choreops/translations/en.json) around lines 3279-3288:
        rename state attribute key from `lock_reason` to `block_reason` and include all six blocker states.
        **Acceptance**: every blocker enum value has translation text.
  - [x] Update type comments in [custom_components/choreops/type_defs.py](../../custom_components/choreops/type_defs.py) around lines 467-468:
        document `completed_by` and `claimed_by` as list-based contracts.
        **Acceptance**: type comments no longer mention scalar variant as runtime contract.
- **Key issues**
  - Key rename has broad blast radius; enforce single pass and avoid dual aliases in hard-fork mode.

### Phase 2 – Core behavior

- **Goal**: Publish consistent `block_reason` and list-shaped completion ownership from source-of-truth workflows.
- **Steps / detailed work items** - [x] Update [custom_components/choreops/managers/chore_manager.py](../../custom_components/choreops/managers/chore_manager.py) `get_chore_status_context()` around lines 3579-3731:
  derive `block_reason` from final claim denial (`can_claim_error`) so reason and gate are lock-step.
  **Acceptance**: `can_claim=true => block_reason=None`; `can_claim=false => block_reason in enum`. - [x] Deferred to [CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md](CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md): keep [custom_components/choreops/engines/chore_engine.py](../../custom_components/choreops/engines/chore_engine.py) around lines 428-506 as the pure claim verdict source.
  Implement only minimal mapping support needed by manager; avoid behavior spread.
  **Acceptance**: engine remains HA-import free and continues returning translation-key error contract.
  - [x] Refactor [custom_components/choreops/sensor.py](../../custom_components/choreops/sensor.py) around lines 1007-1152:
        consume `can_claim`, `can_approve`, and `block_reason` from `get_chore_status_context()`; remove redundant recompute calls.
        **Acceptance**: no second-path claimability computation from sensor.
  - [x] Unify completed ownership writes in [custom_components/choreops/managers/chore_manager.py](../../custom_components/choreops/managers/chore_manager.py) `_handle_completion_criteria()` around lines 4175-4237:
        always write `completed_by` as list-of-names for independent/shared_first/shared_all.
        **Acceptance**: all completion criteria produce list type.
  - [x] Remove/neutralize conflicting scalar write path in [custom_components/choreops/managers/chore_manager.py](../../custom_components/choreops/managers/chore_manager.py) `_apply_effect()` around lines 4649-4650.
        **Acceptance**: one authoritative writer for completed ownership.
    - [x] Deferred to [CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md](CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md): ensure clear/reset paths in [custom_components/choreops/managers/chore_manager.py](../../custom_components/choreops/managers/chore_manager.py) around lines 1415-1490 and 3950-4010 clear list values safely.
          **Acceptance**: no stale scalar/string residues after reset/undo.
- **Key issues**
  - **Schema/migration decision**: persisted field shape changes require schema checkpoint update in `custom_components/choreops/const.py` (post-45) and startup normalization pass.
  - **Boundary guard**: all writes remain manager-owned; no direct `_data` writes in flow/service layers.

### Phase 3 – Testing

- **Goal**: Prove contract consistency across shared_first/rotation/shared_all and prevent regressions.
- **Steps / detailed work items** - [x] Rename lock-reason assertions to block-reason in [tests/test_rotation_fsm_states.py](../../tests/test_rotation_fsm_states.py) and [tests/test_chore_scheduling.py](../../tests/test_chore_scheduling.py).
  **Acceptance**: no `lock_reason` assertions remain. - [x] Deferred to [CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md](CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md): update [tests/test_workflow_chores.py](../../tests/test_workflow_chores.py) and [tests/test_workflow_gaps.py](../../tests/test_workflow_gaps.py):
  enforce action contract + list-shaped `completed_by` in shared_first/shared_all.
  **Acceptance**: tests assert list shape, not string shape.
  - [x] Deferred to [CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md](CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md): add a focused matrix test in [tests/test_chore_engine.py](../../tests/test_chore_engine.py):
        each denial key maps to one canonical blocker enum value.
        **Acceptance**: 6 blocker reasons covered in parameterized test.
  - [x] Deferred to [CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md](CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md): add sensor contract test (new or adjacent existing module):
        `can_claim`/`block_reason` lock-step invariant.
        **Acceptance**: failing if `can_claim=false` with null reason, except explicitly allowed none-cases (none expected under this contract).
  - [x] Deferred to [CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md](CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md): run required gates from repository standards:
        `./utils/quick_lint.sh --fix`, `mypy custom_components/choreops/`, `mypy tests/`, `python -m pytest tests/ -v --tb=line`.
- **Key issues**
  - Test fixtures may carry mixed legacy shapes (`str`/`list`) and require fixture normalization updates.

### Phase 4 – UI + docs

- **Goal**: Consume the unified contract in essentials UI with minimal changes and document the hard-fork contract.
- **Steps / detailed work items**
  - [x] Deferred to [CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md](CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md): update [choreops-dashboards/templates/user-essential-v1.yaml](../../../choreops-dashboards/templates/user-essential-v1.yaml) around lines 607-665:
        action button enable/disable must use `entity.attributes.can_claim` (and claimed state for approve), not state blocked arrays.
        **Acceptance**: state list can remain visual-only but not action authority.
  - [x] Deferred to [CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md](CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md): add compact shared progress display from existing lists in [choreops-dashboards/templates/user-essential-v1.yaml](../../../choreops-dashboards/templates/user-essential-v1.yaml):
        `completed_count = Array.isArray(completed_by) ? completed_by.length : 0`,
        `assigned_count = Array.isArray(assigned_user_names) ? assigned_user_names.length : 0`.
        **Acceptance**: no new backend attribute introduced for progress.
  - [x] Deferred to [CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md](CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md): update contract docs in [docs/ARCHITECTURE.md](../ARCHITECTURE.md) and [docs/DEVELOPMENT_STANDARDS.md](../DEVELOPMENT_STANDARDS.md):
        action gate vs display semantics, plus list-only completion ownership contract.
        **Acceptance**: docs examples match runtime contract keys.
  - [x] Deferred to [CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md](CLAIM_MODE_CONTRACT_HARD_FORK_IN-PROCESS.md): update release notes/checklist artifacts with schema/checkpoint and hard-fork notes.
- **Key issues**
  - Ensure template handles `completed_by` safely when empty/null during transition tests.

## Implementation sequence (builder execution order)

1. **Contract keys + translations first**: constants and translation key rename.
2. **Manager context lock-step**: finalize `can_claim` + `block_reason` contract in one path.
3. **Completed ownership single-write**: remove scalar divergence and normalize list writes.
4. **Sensor consumer cleanup**: consume context values; remove recompute.
5. **Test updates**: context assertions, completed_by shape, matrix mapping.
6. **Dashboard template**: switch action gating to `can_claim`; add list-derived shared progress.
7. **Docs + release notes**: record hard-fork contract.

## Non-goals (scope guard)

- No introduction of additional progress attributes.
- No compatibility aliases for old key names.
- No broad FSM behavior changes beyond contract publication and ownership shape normalization.

## Testing & validation

- **Validation commands (required for done)**
  - `./utils/quick_lint.sh --fix`
  - `mypy custom_components/choreops/`
  - `mypy tests/`
  - `python -m pytest tests/ -v --tb=line`
- **Focused suites before full run**
  - `python -m pytest tests/test_rotation_fsm_states.py -v`
  - `python -m pytest tests/test_workflow_chores.py -v`
  - `python -m pytest tests/test_workflow_gaps.py -v`
  - `python -m pytest tests/test_chore_engine.py -v`
- **Outstanding tests**
  - Full integration runtime/manual dashboard smoke validation in Home Assistant UI.

### Latest run results (Phase 1 execution)

- `./utils/quick_lint.sh --fix`: ✅ pass
- `python -m pytest tests/ -v --tb=line`: ❌ fail - Result: `1575 passed, 10 failed, 4 skipped, 2 deselected` - Failures observed in: - `tests/test_config_flow_error_scenarios.py` (2) - `tests/test_config_flow_use_existing.py` (5) - `tests/test_points_migration_validation.py` (3)
- `python -m mypy custom_components/choreops/ && python -m mypy tests/`: ❌ blocked by dependency parser mismatch in `core` (Python 3.14 syntax)
- `python -m mypy --python-version 3.14 custom_components/choreops/ && python -m mypy --python-version 3.14 tests/`: ❌ fail - `custom_components/choreops/__init__.py:128` arg-type (`str | None` passed where `str` expected)

### Latest run results (Phase 2/3 follow-up)

- `./utils/quick_lint.sh --fix`: ✅ pass
- `python -m pytest tests/test_workflow_chores.py::TestSharedAllChores::test_three_assignee_shared_all -v --tb=line`: ✅ pass - Regression assertion added: final assignee still sees full `completed_by` list (not only self)
- `python -m pytest tests/test_rotation_fsm_states.py tests/test_workflow_chores.py -v --tb=line`: ✅ pass (`59 passed`)

## Notes & follow-up

- This initiative intentionally removes backward compatibility accommodations due to hard-fork scope.
- If persisted `completed_by` shape is changed at write-time, increment schema checkpoint and include explicit startup normalization to avoid mixed runtime shapes.
- Keep implementation minimal: no new shared progress attributes; derive progress from existing `assigned_user_names` and normalized `completed_by`.
