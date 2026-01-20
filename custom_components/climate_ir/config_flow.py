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


class ClimateIRConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    # ----------------------------------------------
    # PASSO 1 – escolher backend
    # ----------------------------------------------

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self.context["backend"] = user_input["ir_backend"]

            if user_input["ir_backend"] == "broadlink":
                return await self.async_step_broadlink()

            return await self.async_step_qa()

        schema = vol.Schema({
            vol.Required("name"): str,

            vol.Required("ir_backend"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=["broadlink", "qa"],
                    mode="dropdown",
                )
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )

    # ----------------------------------------------
    # PASSO 2A – BROADLINK
    # ----------------------------------------------

    async def async_step_broadlink(self, user_input=None):
        if user_input is not None:
            self.context["backend_data"] = user_input
            return await self.async_step_common()

        schema = vol.Schema({
            vol.Required("controller"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="remote")
            ),

            vol.Required("controlled_device"): str,
        })

        return self.async_show_form(
            step_id="broadlink",
            data_schema=schema,
        )

    # ----------------------------------------------
    # PASSO 2B – QA
    # ----------------------------------------------

    async def async_step_qa(self, user_input=None):
        if user_input is not None:
            self.context["backend_data"] = user_input
            return await self.async_step_common()

        schema = vol.Schema({
            vol.Required("qa_profile"): str,

            vol.Required("controlled_device"): str,

            vol.Required("qa_entity"): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="text")
            ),
        })

        return self.async_show_form(
            step_id="qa",
            data_schema=schema,
        )

    # ----------------------------------------------
    # PASSO 3 – COMUM
    # ----------------------------------------------

    async def async_step_common(self, user_input=None):
        if user_input is not None:

            data = {
                "name": self.context["title_placeholders"]["name"]
                if "title_placeholders" in self.context
                else "IR Climate",

                "ir_backend": self.context["backend"],
            }

            data.update(self.context["backend_data"])
            data.update(user_input)

            return self.async_create_entry(
                title=data["name"],
                data=data,
            )

        schema = vol.Schema({

            vol.Required(
                "hvac_modes",
                default=[HVACMode.OFF, HVACMode.COOL],
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
            step_id="common",
            data_schema=schema,
        )

    # ----------------------------------------------
    # OPTIONS FLOW – edição sem trocar backend
    # ----------------------------------------------

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        return ClimateIROptionsFlow(entry)


class ClimateIROptionsFlow(config_entries.OptionsFlow):

    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {**self.entry.data, **self.entry.options}

        schema = vol.Schema({

            vol.Optional(
                "controlled_device",
                default=options.get("controlled_device"),
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
                )
            ),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
