import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.components.climate.const import HVACMode, FAN_LOW, FAN_MEDIUM, FAN_HIGH, FAN_AUTO, FAN_FOCUS

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

            vol.Required("hvac_modes", default=[
                HVACMode.COOL,
                HVACMode.HEAT,
            ]): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        HVACMode.COOL,
                        HVACMode.HEAT,
                        HVACMode.DRY,
                        HVACMode.FAN_ONLY,
                        HVACMode.AUTO,
                    ],
                    multiple=True,
                    mode="dropdown",
                )
            ),
  
            vol.Required("fan_modes", default=[
                FAN_LOW,
                FAN_MEDIUM,
                FAN_HIGH,
            ]): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        FAN_LOW,
                        FAN_MEDIUM,
                        FAN_HIGH,
                        FAN_AUTO,
                        FAN_FOCUS,
                    ],
                    multiple=True,
                    mode="dropdown",
                )
            ),

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
