"""Tests for user profile UI control normalization."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.choreops import const, data_builders as db
from custom_components.choreops.managers.user_manager import UserManager


def test_build_user_profile_defaults_ui_preferences_to_empty_dict() -> None:
    """User profile builder should always emit a ui_preferences mapping."""
    user_profile = db.build_user_profile(
        {
            const.CFOF_USERS_INPUT_NAME: "Alice",
        }
    )

    assert user_profile[const.DATA_USER_UI_PREFERENCES] == {}


def test_build_user_assignment_profile_preserves_ui_preferences() -> None:
    """Assignment profile builder should preserve nested UI control payloads."""
    ui_preferences = {
        "gamification": {
            "rewards": {
                "header_collapse": True,
            }
        }
    }

    assignment_profile = db.build_user_assignment_profile(
        {
            const.CFOF_USERS_INPUT_NAME: "Zoë",
            const.DATA_USER_UI_PREFERENCES: ui_preferences,
        }
    )

    assert assignment_profile[const.DATA_USER_UI_PREFERENCES] == ui_preferences


def test_normalize_user_record_preserves_ui_preferences_for_assignable_user() -> None:
    """Assignable user normalization should keep durable UI preferences."""
    coordinator = MagicMock()
    coordinator.config_entry.entry_id = "entry-123"
    manager = UserManager(MagicMock(), coordinator)
    ui_preferences = {
        "gamification": {
            "rewards": {
                "header_collapse": True,
            }
        }
    }

    normalized = manager._normalize_user_record(
        {
            const.CFOF_USERS_INPUT_NAME: "Zoë",
            const.CFOF_USERS_INPUT_CAN_BE_ASSIGNED: True,
            const.CFOF_USERS_INPUT_ENABLE_CHORE_WORKFLOW: True,
            const.CFOF_USERS_INPUT_ENABLE_GAMIFICATION: True,
            const.DATA_USER_UI_PREFERENCES: ui_preferences,
        },
        existing={
            const.DATA_USER_ASSOCIATED_USER_IDS: ["approver-1"],
        },
    )

    assert normalized[const.DATA_USER_UI_PREFERENCES] == ui_preferences
    assert normalized[const.DATA_USER_ASSOCIATED_USER_IDS] == ["approver-1"]
