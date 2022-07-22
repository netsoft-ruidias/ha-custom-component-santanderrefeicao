"""Config flow for Santander Refeição integration."""
from __future__ import annotations

import logging
import voluptuous as vol
import async_timeout


from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD
)

from .api import SantanderRefeicaoAPI
from .const import (
    DOMAIN,
    TITLE
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Santander config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user interface."""
        _LOGGER.debug("Starting async_step_user...")
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
            self._abort_if_unique_id_configured()

            if await self._test_credentials(user_input):
                _LOGGER.debug("Config is valid!")
                return self.async_create_entry(
                    title=f"{TITLE} {user_input[CONF_USERNAME]}",
                    data = user_input
                ) 
            else:
                errors = {"base": "auth"}

        return self.async_show_form(
            step_id="user", 
            data_schema=DATA_SCHEMA, 
            errors=errors,
        )

    async def _test_credentials(self, user_input):
        """Return true if credentials is valid."""
        session = async_get_clientsession(self.hass, True)
        async with async_timeout.timeout(10):
            try:
                api = SantanderRefeicaoAPI(session)
                return await api.login(user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
            except Exception as exception:
                _LOGGER.error(exception)
                return False