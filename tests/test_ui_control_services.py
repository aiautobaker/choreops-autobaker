"""Tests for the `manage_ui_control` service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import HomeAssistantError
import pytest

from custom_components.choreops import const
from tests.helpers import SetupResult, setup_from_yaml

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


@pytest.fixture
async def scenario_full(
    hass: HomeAssistant,
    mock_hass_users: dict[str, Any],
) -> SetupResult:
    """Load full scenario for UI control service testing."""
    return await setup_from_yaml(
        hass,
        mock_hass_users,
        "tests/scenarios/scenario_full.yaml",
    )


def _get_helper_ui_control(hass: HomeAssistant, assignee_slug: str) -> dict[str, Any]:
    """Return the dashboard helper `ui_control` payload for one user."""
    helper_state = hass.states.get(
        f"sensor.{assignee_slug}_choreops_ui_dashboard_helper"
    )
    assert helper_state is not None

    ui_control = helper_state.attributes.get(const.ATTR_UI_CONTROL)
    assert isinstance(ui_control, dict)
    return ui_control


class TestManageUiControlService:
    """Service tests for durable per-user UI controls."""

    @pytest.mark.asyncio
    async def test_create_updates_helper_and_returns_response(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
    ) -> None:
        """Create should persist the control and refresh the helper payload."""
        user_id = scenario_full.assignee_ids["Zoë"]

        response = await hass.services.async_call(
            const.DOMAIN,
            const.SERVICE_MANAGE_UI_CONTROL,
            {
                const.SERVICE_FIELD_CONFIG_ENTRY_ID: scenario_full.config_entry.entry_id,
                const.SERVICE_FIELD_USER_NAME: "Zoë",
                const.SERVICE_FIELD_UI_CONTROL_ACTION: const.UI_CONTROL_ACTION_CREATE,
                const.SERVICE_FIELD_UI_CONTROL_KEY: (
                    const.UI_CONTROL_PATH_GAMIFICATION_REWARDS_HEADER_COLLAPSE
                ),
                const.SERVICE_FIELD_UI_CONTROL_VALUE: True,
            },
            blocking=True,
            return_response=True,
        )

        await hass.async_block_till_done()

        assert response == {
            const.SERVICE_FIELD_USER_ID: user_id,
            const.SERVICE_FIELD_UI_CONTROL_ACTION: const.UI_CONTROL_ACTION_CREATE,
            const.SERVICE_FIELD_UI_CONTROL_KEY: (
                const.UI_CONTROL_PATH_GAMIFICATION_REWARDS_HEADER_COLLAPSE
            ),
            "cleared_all": False,
            "user_name": "Zoë",
        }
        assert (
            _get_helper_ui_control(hass, "zoe")["gamification"]["rewards"][
                "header_collapse"
            ]
            is True
        )

    @pytest.mark.asyncio
    async def test_update_overwrites_existing_value(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
    ) -> None:
        """Update should overwrite an existing persisted value."""
        user_id = scenario_full.assignee_ids["Zoë"]

        await hass.services.async_call(
            const.DOMAIN,
            const.SERVICE_MANAGE_UI_CONTROL,
            {
                const.SERVICE_FIELD_USER_ID: user_id,
                const.SERVICE_FIELD_UI_CONTROL_ACTION: const.UI_CONTROL_ACTION_CREATE,
                const.SERVICE_FIELD_UI_CONTROL_KEY: (
                    const.UI_CONTROL_PATH_GAMIFICATION_REWARDS_HEADER_COLLAPSE
                ),
                const.SERVICE_FIELD_UI_CONTROL_VALUE: True,
            },
            blocking=True,
            return_response=True,
        )

        response = await hass.services.async_call(
            const.DOMAIN,
            const.SERVICE_MANAGE_UI_CONTROL,
            {
                const.SERVICE_FIELD_USER_ID: user_id,
                const.SERVICE_FIELD_UI_CONTROL_ACTION: const.UI_CONTROL_ACTION_UPDATE,
                const.SERVICE_FIELD_UI_CONTROL_KEY: (
                    const.UI_CONTROL_PATH_GAMIFICATION_REWARDS_HEADER_COLLAPSE
                ),
                const.SERVICE_FIELD_UI_CONTROL_VALUE: False,
            },
            blocking=True,
            return_response=True,
        )

        await hass.async_block_till_done()

        user_record = scenario_full.coordinator.assignees_data[user_id]
        assert response[const.SERVICE_FIELD_UI_CONTROL_ACTION] == (
            const.UI_CONTROL_ACTION_UPDATE
        )
        assert (
            user_record[const.DATA_USER_UI_PREFERENCES]["gamification"]["rewards"][
                "header_collapse"
            ]
            is False
        )
        assert (
            _get_helper_ui_control(hass, "zoe")["gamification"]["rewards"][
                "header_collapse"
            ]
            is False
        )

    @pytest.mark.asyncio
    async def test_remove_empty_key_clears_all_preferences(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
    ) -> None:
        """Remove with an empty key should clear the full user preference bucket."""
        user_id = scenario_full.assignee_ids["Zoë"]

        await hass.services.async_call(
            const.DOMAIN,
            const.SERVICE_MANAGE_UI_CONTROL,
            {
                const.SERVICE_FIELD_USER_ID: user_id,
                const.SERVICE_FIELD_UI_CONTROL_ACTION: const.UI_CONTROL_ACTION_CREATE,
                const.SERVICE_FIELD_UI_CONTROL_KEY: (
                    const.UI_CONTROL_PATH_GAMIFICATION_REWARDS_HEADER_COLLAPSE
                ),
                const.SERVICE_FIELD_UI_CONTROL_VALUE: True,
            },
            blocking=True,
            return_response=True,
        )

        response = await hass.services.async_call(
            const.DOMAIN,
            const.SERVICE_MANAGE_UI_CONTROL,
            {
                const.SERVICE_FIELD_USER_ID: user_id,
                const.SERVICE_FIELD_UI_CONTROL_ACTION: const.UI_CONTROL_ACTION_REMOVE,
            },
            blocking=True,
            return_response=True,
        )

        await hass.async_block_till_done()

        assert response["cleared_all"] is True
        assert response[const.SERVICE_FIELD_UI_CONTROL_KEY] == ""
        assert (
            scenario_full.coordinator.assignees_data[user_id][
                const.DATA_USER_UI_PREFERENCES
            ]
            == {}
        )
        assert (
            _get_helper_ui_control(hass, "zoe")["gamification"]["rewards"][
                "header_collapse"
            ]
            is False
        )

    @pytest.mark.asyncio
    async def test_remove_key_clears_targeted_preference(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
    ) -> None:
        """Remove with a key should clear only the targeted preference path."""
        user_id = scenario_full.assignee_ids["Zoë"]

        await hass.services.async_call(
            const.DOMAIN,
            const.SERVICE_MANAGE_UI_CONTROL,
            {
                const.SERVICE_FIELD_USER_ID: user_id,
                const.SERVICE_FIELD_UI_CONTROL_ACTION: const.UI_CONTROL_ACTION_CREATE,
                const.SERVICE_FIELD_UI_CONTROL_KEY: (
                    const.UI_CONTROL_PATH_GAMIFICATION_REWARDS_HEADER_COLLAPSE
                ),
                const.SERVICE_FIELD_UI_CONTROL_VALUE: True,
            },
            blocking=True,
            return_response=True,
        )

        response = await hass.services.async_call(
            const.DOMAIN,
            const.SERVICE_MANAGE_UI_CONTROL,
            {
                const.SERVICE_FIELD_USER_ID: user_id,
                const.SERVICE_FIELD_UI_CONTROL_ACTION: const.UI_CONTROL_ACTION_REMOVE,
                const.SERVICE_FIELD_UI_CONTROL_KEY: (
                    const.UI_CONTROL_PATH_GAMIFICATION_REWARDS_HEADER_COLLAPSE
                ),
            },
            blocking=True,
            return_response=True,
        )

        await hass.async_block_till_done()

        assert response["cleared_all"] is False
        assert response[const.SERVICE_FIELD_UI_CONTROL_KEY] == (
            const.UI_CONTROL_PATH_GAMIFICATION_REWARDS_HEADER_COLLAPSE
        )
        assert (
            scenario_full.coordinator.assignees_data[user_id][
                const.DATA_USER_UI_PREFERENCES
            ]
            == {}
        )
        assert (
            _get_helper_ui_control(hass, "zoe")["gamification"]["rewards"][
                "header_collapse"
            ]
            is False
        )

    @pytest.mark.asyncio
    async def test_requires_user_target(
        self,
        hass: HomeAssistant,
        scenario_full: SetupResult,
    ) -> None:
        """Service should reject calls without a target user."""
        with pytest.raises(HomeAssistantError):
            await hass.services.async_call(
                const.DOMAIN,
                const.SERVICE_MANAGE_UI_CONTROL,
                {
                    const.SERVICE_FIELD_UI_CONTROL_ACTION: const.UI_CONTROL_ACTION_CREATE,
                    const.SERVICE_FIELD_UI_CONTROL_KEY: (
                        const.UI_CONTROL_PATH_GAMIFICATION_REWARDS_HEADER_COLLAPSE
                    ),
                    const.SERVICE_FIELD_UI_CONTROL_VALUE: True,
                },
                blocking=True,
                return_response=True,
            )
