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


class ClimateBroadlinkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    # --------------------------------------------------
    # FLUXO DE CRIAÇÃO
    # --------------------------------------------------

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            data = user_input.copy()

            # 🔥 Conversão final – é aqui que a mágica acontece
            data["temp_sensor"] = data.get("temp_sensor") or None
            data["power_sensor"] = data.get("power_sensor") or None

            return self.async_create_entry(
                title=data["name"],
                data=data,
            )

        schema = vol.Schema({
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

            # ✅ Sem allow_none, sem Any – padrão suportado
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
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        return ClimateBroadlinkOptionsFlow(entry)


# ------------------------------------------------------
# OPTIONS FLOW – EDIÇÃO COMPLETA
# ------------------------------------------------------

class ClimateBroadlinkOptionsFlow(config_entries.OptionsFlow):

    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            data = user_input.copy()

            # 🔥 Conversão crítica
            data["temp_sensor"] = data.get("temp_sensor") or None
            data["power_sensor"] = data.get("power_sensor") or None

            return self.async_create_entry(title="", data=data)

        # Merge do que já existe
        options = {**self.entry.data, **self.entry.options}

        schema = vol.Schema({

            # 🆕 Agora editáveis
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

            vol.Optional(
                "fan_modes",
                default=options.get("fan_modes", []),
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

            # 🔥 PONTO CENTRAL: default "" → vira None no submit
            vol.Optional(
                "temp_sensor",
                default=options.get("temp_sensor") or "",
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor")
            ),

            vol.Optional(
                "power_sensor",
                default=options.get("power_sensor") or "",
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="binary_sensor")
            ),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
