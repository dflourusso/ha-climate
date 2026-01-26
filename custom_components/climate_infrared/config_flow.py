import voluptuous as vol
from voluptuous import UNDEFINED

from homeassistant import config_entries
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


class ClimateInfraredConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            data = user_input.copy()

            # Normalize optional sensors
            for k in ("temp_sensor", "power_sensor"):
                if not data.get(k):
                    data[k] = None

            return self.async_create_entry(
                title=data["name"],
                data=data,
            )

        schema = vol.Schema(
            {
                vol.Required("name"): str,

                vol.Required("controller"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="remote")
                ),

                vol.Required("remote"): str,

                vol.Required(
                    "hvac_modes",
                    default=[HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT],
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            HVACMode.OFF,
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

                vol.Required(
                    "fan_modes",
                    default=[FAN_LOW, FAN_MEDIUM, FAN_HIGH],
                ): selector.SelectSelector(
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

                # Optional sensors
                vol.Optional(
                    "temp_sensor",
                    default=UNDEFINED,
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="sensor")
                ),

                vol.Optional(
                    "power_sensor",
                    default=UNDEFINED,
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="binary_sensor")
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema)
