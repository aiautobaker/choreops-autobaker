# Builder handoff: Claim mode hard fork implementation

## Scope and constraints (locked)

- Hard fork: no legacy compatibility path, no alias constants.
- Keep existing centralized claim logic path (`can_claim`) as the action gate.
- Add explicit actionable mode for steal window: `steal_available`.
- Keep `can_claim_error` unchanged in this release.
- Do not include dashboard template work in this initiative.

## Current code surfaces to change (exact)

### Core contract/constants

- [custom_components/choreops/const.py](../../custom_components/choreops/const.py#L1867-L1913)
  - Remove `CHORE_BLOCK_REASON_*`, `CHORE_BLOCK_REASONS`, `CHORE_CTX_BLOCK_REASON`.
  - Add `CHORE_CLAIM_MODE_*`, `CHORE_CLAIM_MODES`, `CHORE_CTX_CLAIM_MODE`.
- [custom_components/choreops/const.py](../../custom_components/choreops/const.py#L2494)
  - Replace `ATTR_CHORE_BLOCK_REASON` with `ATTR_CHORE_CLAIM_MODE`.

### Status context derivation

- [custom_components/choreops/managers/chore_manager.py](../../custom_components/choreops/managers/chore_manager.py#L3598-L3751)
  - Replace `claim_error_to_block_reason` map with `claim_error_to_claim_mode`.
  - Set `claim_mode` for both blocked and actionable paths.
  - Keep `CHORE_CTX_CAN_CLAIM_ERROR` unchanged.
  - Update `available_at` to be keyed off `claim_mode == blocked_waiting_window`.

### Sensor attribute contract

- [custom_components/choreops/sensor.py](../../custom_components/choreops/sensor.py#L1015-L1050)
  - Replace `block_reason` read/publication with `claim_mode` read/publication.

### Translations (entity attribute states)

- [custom_components/choreops/translations/en.json](../../custom_components/choreops/translations/en.json#L3317-L3330)
  - Rename `block_reason` state attribute definition to `claim_mode`.
  - Replace state values with canonical mode keys.

### Tests currently asserting `block_reason`

- [tests/test_rotation_fsm_states.py](../../tests/test_rotation_fsm_states.py#L111-L516)
- [tests/test_rotation_services.py](../../tests/test_rotation_services.py#L191)
- [tests/test_workflow_chores.py](../../tests/test_workflow_chores.py#L357-L2726)
- [tests/test_chore_scheduling.py](../../tests/test_chore_scheduling.py#L2975-L3195)
- [tests/test_workflow_notifications.py](../../tests/test_workflow_notifications.py#L1128)

## Canonical mode mapping (implementation target)

### A) Blocked mapping (existing logic reuse)

Map from current `claim_error` translation keys in status-context builder:

- `TRANS_KEY_ERROR_CHORE_PENDING_CLAIM` → `blocked_pending_claim`
- `TRANS_KEY_ERROR_CHORE_ALREADY_APPROVED` → `blocked_already_approved`
- `TRANS_KEY_ERROR_CHORE_COMPLETED_BY_OTHER` → `blocked_completed_by_other`
- `TRANS_KEY_ERROR_CHORE_WAITING` → `blocked_waiting_window`
- `TRANS_KEY_ERROR_CHORE_NOT_MY_TURN` → `blocked_not_my_turn`
- `TRANS_KEY_ERROR_CHORE_MISSED_LOCKED` → `blocked_missed_locked`

### B) Actionable mapping

- `can_claim=True` default → `claimable`
- `can_claim=True` + steal window condition → `steal_available`

### C) Steal window condition (minimal additive logic)

Set `steal_available` only when all are true in status-context builder:

1. chore is rotation mode
2. assignee is not current turn holder
3. overdue handling is `OVERDUE_HANDLING_AT_DUE_DATE_ALLOW_STEAL`
4. derived/display state is overdue and claim is allowed (`can_claim=True`)

This preserves existing action logic and only normalizes interaction labeling.

## Implementation sequence for builder (single branch)

### Step 1 — Contract constants and keys

- Edit [custom_components/choreops/const.py](../../custom_components/choreops/const.py#L1867-L1913).
- Edit [custom_components/choreops/const.py](../../custom_components/choreops/const.py#L2494).
- Acceptance:
  - No `CHORE_BLOCK_REASON_*` constants remain.
  - `CHORE_CTX_CLAIM_MODE` and `ATTR_CHORE_CLAIM_MODE` exist.

### Step 2 — Status context derivation

- Edit [custom_components/choreops/managers/chore_manager.py](../../custom_components/choreops/managers/chore_manager.py#L3598-L3751).
- Acceptance:
  - Context returns `claim_mode` instead of `block_reason`.
  - `can_claim_error` remains present and unchanged.
  - `available_at` is present only for waiting mode.

### Step 3 — Sensor publication

- Edit [custom_components/choreops/sensor.py](../../custom_components/choreops/sensor.py#L1015-L1050).
- Acceptance:
  - Chore sensor attributes include `claim_mode`.
  - `block_reason` attribute no longer emitted.

### Step 4 — Translation attribute schema

- Edit [custom_components/choreops/translations/en.json](../../custom_components/choreops/translations/en.json#L3317-L3330).
- Acceptance:
  - State attribute key is `claim_mode`.
  - State map includes all canonical modes.

### Step 5 — Test migration

- Update only affected tests listed above.
- Convert assertions:
  - `attributes.get("block_reason")` → `attributes.get("claim_mode")`
  - `status_ctx["block_reason"]` → `status_ctx["claim_mode"]`
  - `ATTR_CHORE_BLOCK_REASON` → `ATTR_CHORE_CLAIM_MODE` (or explicit attr key if test style requires)
- Add/adjust steal test assertions:
  - When allow-steal unlocks non-turn assignee claimability, assert `claim_mode == "steal_available"`.
- Acceptance:
  - No test assertions on `block_reason` remain.

### Step 6 — Docs alignment (in-repo only)

- Update references in:
  - [docs/ARCHITECTURE.md](../ARCHITECTURE.md)
  - [docs/DEVELOPMENT_STANDARDS.md](../DEVELOPMENT_STANDARDS.md)
- Acceptance:
  - Interaction lane documented as `claim_mode` + `can_claim`.

## Verification commands for builder

Run in order:

1. `./utils/quick_lint.sh --fix`
2. `mypy custom_components/choreops/`
3. `python -m pytest tests/ -v --tb=line`
4. `mypy tests/`

## Baseline status

- Pre-change baseline is already confirmed passing by owner.
- Builder validation should confirm no regressions after contract migration.

## Risk watch list (targeted)

- `available_at` should only exist for waiting-window blocked mode.
- Rotation non-turn holder before due remains blocked (`blocked_not_my_turn`).
- Rotation allow-steal after due becomes actionable with `steal_available`.
- Completed-by-other logic remains blocked and unchanged behaviorally.
