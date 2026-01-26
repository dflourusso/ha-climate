import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.components.climate.const import (
    HVACMode,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
    FAN_AUTO,
    FAN_FOCUS,
)

from .const import DOMAIN


HVAC_OPTIONS = [m.value for m in [
    HVACMode.OFF,
    HVACMode.COOL,
    HVACMode.HEAT,
    HVACMode.DRY,
    HVACMode.FAN_ONLY,
    HVACMode.AUTO,
]]

FAN_OPTIONS = [
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
    FAN_AUTO,
    FAN_FOCUS,
]


class ClimateInfraredConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            data = user_input.copy()
            data["temp_sensor"] = data.get("temp_sensor") or None
            data["power_sensor"] = data.get("power_sensor") or None

            return self.async_create_entry(title=data["name"], data=data)

        schema = vol.Schema({
            vol.Required("name"): str,

            vol.Required("controller"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="remote")
            ),

            vol.Required("remote"): str,

            vol.Required(
                "hvac_modes",
                default=["off", "cool", "heat"],
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=HVAC_OPTIONS,
                    multiple=True,
                    mode="dropdown",
                )
            ),

            vol.Required(
                "fan_modes",
                default=[FAN_LOW, FAN_MEDIUM, FAN_HIGH],
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=FAN_OPTIONS,
                    multiple=True,
                    mode="dropdown",
                )
            ),

            vol.Optional("temp_sensor"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", allow_none=True)
            ),

            vol.Optional("power_sensor"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="binary_sensor", allow_none=True)
            ),
        })

        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        return ClimateInfraredOptionsFlow(entry)


# ------------------------------------------------------
# OPTIONS FLOW
# ------------------------------------------------------

class ClimateInfraredOptionsFlow(config_entries.OptionsFlow):

    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            data = user_input.copy()
            data["temp_sensor"] = data.get("temp_sensor") or None
            data["power_sensor"] = data.get("power_sensor") or None
            return self.async_create_entry(title="", data=data)

        options = {**self.entry.data, **self.entry.options}

        schema = vol.Schema({
            vol.Optional(
                "controller",
                default=options.get("controller"),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="remote")
            ),

            vol.Optional(
                "remote",
                default=options.get("remote"),
            ): str,

            vol.Optional(
                "hvac_modes",
                default=options.get("hvac_modes", []),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=HVAC_OPTIONS,
                    multiple=True,
                    mode="dropdown",
                )
            ),

            vol.Optional(
                "fan_modes",
                default=options.get("fan_modes", []),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=FAN_OPTIONS,
                    multiple=True,
                    mode="dropdown",
                )
            ),

            vol.Optional(
                "temp_sensor",
                default=options.get("temp_sensor"),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", allow_none=True)
            ),

            vol.Optional(
                "power_sensor",
                default=options.get("power_sensor"),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="binary_sensor", allow_none=True)
            ),
        })

        return self.async_show_form(step_id="init", data_schema=schema)
