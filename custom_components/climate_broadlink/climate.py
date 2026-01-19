import logging
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACMode,
    ClimateEntityFeature,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
)
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.restore_state import RestoreEntity

_LOGGER = logging.getLogger(__name__)


class ClimateBroadlink(ClimateEntity, RestoreEntity):

    def __init__(self, hass, config):
        self.hass = hass

        # ---------- VARIÁVEIS DO YAML ----------
        self._nome = config.get("name")
        self._controller = config.get("controller")
        self._remote = config.get("remote")
        self._sensor_temp = config.get("temp_sensor")

        if not self._controller or not self._remote:
            _LOGGER.error(
                "ClimateBroadlink [%s] precisa de 'controller' e 'remote' no YAML",
                self._nome
            )

        # ---------- ESTADO INTERNO ----------
        self._hvac_mode = HVACMode.OFF
        self._fan_mode = FAN_LOW
        self._target_temperature = 24

        self._attr_name = self._nome
        self._attr_unique_id = f"climate_broadlink_{self._nome.lower().replace(' ', '_')}"
        self._attr_temperature_unit = TEMP_CELSIUS

        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE |
            ClimateEntityFeature.FAN_MODE
        )

        self._attr_hvac_modes = [
            HVACMode.OFF,
            HVACMode.COOL,
            HVACMode.HEAT,
        ]

        self._attr_fan_modes = [
            FAN_LOW,
            FAN_MEDIUM,
            FAN_HIGH,
        ]

    # ======================================================
    # RESTAURAR ESTADO APÓS REBOOT
    # ======================================================

    async def async_added_to_hass(self):
        last = await self.async_get_last_state()

        if last:
            self._hvac_mode = last.state

            self._target_temperature = last.attributes.get(
                "temperature", 24
            )

            self._fan_mode = last.attributes.get(
                "fan_mode", FAN_LOW
            )

            _LOGGER.info(
                "ClimateBroadlink [%s] restaurado: %s %s° fan:%s",
                self._nome,
                self._hvac_mode,
                self._target_temperature,
                self._fan_mode,
            )

    # ======================================================
    # PROPRIEDADES
    # ======================================================

    @property
    def hvac_mode(self):
        return self._hvac_mode

    @property
    def fan_mode(self):
        return self._fan_mode

    @property
    def target_temperature(self):
        return self._target_temperature

    @property
    def current_temperature(self):
        if not self._sensor_temp:
            return None

        s = self.hass.states.get(self._sensor_temp)
        if s:
            try:
                return float(s.state)
            except Exception:
                return None

    # ======================================================
    # COMANDOS
    # ======================================================

    async def async_set_hvac_mode(self, hvac_mode):
        self._hvac_mode = hvac_mode

        if hvac_mode == HVACMode.OFF:
            await self._enviar("off")
        else:
            await self._enviar_combinado()

        self.async_write_ha_state()

    # ------------------------------------------------------

    async def async_set_temperature(self, **kwargs):
        temp = int(kwargs.get("temperature"))
        self._target_temperature = temp

        await self._enviar_combinado()

        self.async_write_ha_state()

    # ------------------------------------------------------

    async def async_set_fan_mode(self, fan_mode):
        self._fan_mode = fan_mode

        await self._enviar_combinado()

        self.async_write_ha_state()

    # ======================================================
    # LÓGICA DE MONTAGEM DO NOME IR
    # ======================================================

    async def _enviar_combinado(self):
        """
        Monta chave no padrão:
        cool_low_23
        heat_high_22
        """

        if self._hvac_mode == HVACMode.OFF:
            chave = "off"
        else:
            modo = self._hvac_mode

            fan = {
                FAN_LOW: "low",
                FAN_MEDIUM: "medium",
                FAN_HIGH: "high",
            }.get(self._fan_mode, "low")

            chave = f"{modo}_{fan}_{self._target_temperature}"

        await self._enviar(chave)

    # ======================================================
    # ENVIO PARA O BROADLINK
    # ======================================================

    async def _enviar(self, comando):

        if not self._controller:
            _LOGGER.error(
                "ClimateBroadlink [%s] sem controller configurado!",
                self._nome
            )
            return

        _LOGGER.info(
            "ClimateBroadlink [%s] enviando: %s | controller: %s | device: %s",
            self._nome,
            comando,
            self._controller,
            self._remote
        )

        await self.hass.services.async_call(
            "remote",
            "send_command",
            {
                "entity_id": self._controller,
                "device": self._remote,
                "command": comando
            },
            blocking=True,
        )


# ==========================================================

async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):
    async_add_entities([
        ClimateBroadlink(hass, config)
    ])
