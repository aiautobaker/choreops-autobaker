---
handoff_target: ChoreOps Builder
initiative: CHORE_CLAIM_CONTRACT_UNIFICATION
status: ready_for_implementation
branch_context: release/0.5.0-beta.5-prep
---

# Builder handoff: Chore claim contract unification

## Mission

Implement the approved hard-fork contract with minimal architecture-safe changes:

- `can_claim` is claim-action truth.
- `state` is display semantics only.
- `lock_reason` is replaced by `block_reason`.
- `completed_by` is list-of-names in all completion modes.
- Shared progress is derived in UI from existing lists only.

## Required implementation boundaries

- Allowed code scope:
  - `custom_components/choreops/const.py`
  - `custom_components/choreops/managers/chore_manager.py`
  - `custom_components/choreops/engines/chore_engine.py` (minimal mapping support only)
  - `custom_components/choreops/sensor.py`
  - `custom_components/choreops/translations/en.json`
  - `custom_components/choreops/type_defs.py` (contract comments/types)
  - `tests/` files listed in execution checklist
  - `choreops-dashboards/templates/user-essential-v1.yaml`
- Do not add new progress attributes.
- Do not add compatibility aliases for old keys.
- Keep writes manager-owned and signal-first architecture intact.

## Execution checklist

### A) Constants + translation contract

- [ ] Rename context key: `CHORE_CTX_LOCK_REASON` → `CHORE_CTX_BLOCK_REASON`.
- [ ] Rename sensor attr key: `ATTR_CHORE_LOCK_REASON` → `ATTR_CHORE_BLOCK_REASON`.
- [ ] Define canonical blocker enum constants.
- [ ] Update translation state-attribute section key from `lock_reason` to `block_reason` with all blocker states.

### B) Single-path action contract

- [ ] In `get_chore_status_context()`, derive `block_reason` from final claim verdict (`can_claim` + denial key), not from display state.
- [ ] Ensure lock-step invariant:
  - `can_claim = true` => `block_reason = None`
  - `can_claim = false` => `block_reason in enum`
- [ ] Keep engine as pure decision source; avoid moving orchestration logic out of manager.

### C) Completed ownership normalization

- [ ] Make `_handle_completion_criteria()` authoritative for `completed_by` writes.
- [ ] Persist list-of-names for independent/shared_first/shared_all.
- [ ] Remove/confine conflicting scalar write path in `_apply_effect()` for `set_completed_by`.
- [ ] Verify clear/reset/undo paths remove list ownership cleanly.

### D) Sensor consumer cleanup

- [ ] Use `get_chore_status_context()` as single read path for `can_claim`, `can_approve`, and `block_reason`.
- [ ] Remove second-path recomputation calls in sensor attributes.
- [ ] Expose `completed_by` as list-compatible output for UI consumers.

### E) Dashboard template behavior

- [ ] Update action button gating logic to rely on `entity.attributes.can_claim` (and claimed-state approve flow), not blocked-state arrays.
- [ ] Keep visual state styling (optional) but decouple from action authority.
- [ ] Add shared progress text derived from existing lists:
  - completed_count = length(`completed_by` list)
  - assigned_count = length(`assigned_user_names` list)

### F) Tests and quality gates

- [ ] Update lock_reason assertions to block_reason in rotation/scheduling/workflow tests.
- [ ] Add/adjust tests for list-shaped `completed_by` across shared_first/shared_all/independent.
- [ ] Add blocker mapping matrix test.
- [ ] Run gates:
  - `./utils/quick_lint.sh --fix`
  - `mypy custom_components/choreops/`
  - `mypy tests/`
  - `python -m pytest tests/ -v --tb=line`

## Acceptance criteria (must all pass)

1. No runtime references to `lock_reason` remain in chore context or sensor attrs.
2. No scalar `completed_by` persisted/written in manager paths.
3. Chore sensor never recomputes claimability separately from manager context.
4. Dashboard action enablement follows `can_claim` contract.
5. Shared progress is displayed using existing list fields only.
6. All lint/type/tests pass at platinum gates.

## Known risks and mitigations

- **Risk**: stale fixtures with old lock_reason key.
  - **Mitigation**: update tests in same PR slice as key rename.
- **Risk**: mixed persisted data shape for `completed_by` during local testing.
  - **Mitigation**: add normalization at manager write boundary and optional startup cleanup in same implementation.
- **Risk**: UI regressions from template action gate changes.
  - **Mitigation**: targeted workflow tests + manual smoke check for one independent, shared_first, and shared_all chore.

## Suggested PR slicing

1. **PR-1**: constants/translations + manager context lock-step + sensor read-path cleanup.
2. **PR-2**: completed_by write unification + shape tests.
3. **PR-3**: dashboard template action gating + shared progress rendering + docs updates.
