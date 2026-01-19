import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import DOMAIN


class ClimateBroadlinkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input["name"],
                data=user_input
            )

        schema = vol.Schema({
            vol.Required("name"): str,

            vol.Required("controller"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="remote")
            ),

            vol.Required("remote"): str,

            vol.Optional("temp_sensor"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),

             vol.Optional("power_sensor"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="binary_sensor")
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )
