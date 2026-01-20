import logging
import asyncio
from datetime import datetime

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACMode,
    ClimateEntityFeature,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
    FAN_AUTO,
    FAN_FOCUS,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.event import async_track_state_change_event, async_call_later

_LOGGER = logging.getLogger(__name__)


class ClimateBroadlink(ClimateEntity, RestoreEntity):

    def __init__(self, hass, config):
        self.hass = hass

        self._name = config.get("name")
        self._controller = config.get("controller")
        self._remote = config.get("remote")
        self._sensor_temp = config.get("temp_sensor")
        self._sensor_power = config.get("power_sensor")

        self._hvac_mode = HVACMode.OFF
        self._fan_mode = FAN_LOW
        self._target_temperature = 24

        # 🧠 Proteções contra loop
        self._booting = True
        self._updating_from_sensor = False

        # 🆕 debounce inteligente
        self._pending_sync_unsub = None

        self._attr_name = self._name
        self._attr_unique_id = f"climate_broadlink_{self._name}"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS

        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE |
            ClimateEntityFeature.FAN_MODE
        )

        self._attr_hvac_modes = config.get("hvac_modes", [])
        self._attr_fan_modes = config.get("fan_modes", [])

    # --------------------------------------------------
    # RESTORE + LISTENERS
    # --------------------------------------------------

    async def async_added_to_hass(self):
        last = await self.async_get_last_state()

        if last:
            try:
                self._hvac_mode = HVACMode(last.state)
                self._target_temperature = last.attributes.get("temperature", 24)
                self._fan_mode = last.attributes.get("fan_mode", FAN_LOW)
            except Exception:
                self._hvac_mode = HVACMode.OFF

        # Esperar HA estabilizar
        await asyncio.sleep(2)
        self._booting = False

        # --- MONITOR POWER SENSOR ---
        if self._sensor_power:

            async def sensor_changed(event):
                await self._schedule_sensor_sync()

            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    [self._sensor_power],
                    sensor_changed,
                )
            )

            await self._schedule_sensor_sync()

        # --- MONITOR TEMPERATURE SENSOR ---
        if self._sensor_temp:

            async def temp_changed(event):
                self.async_write_ha_state()

            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    [self._sensor_temp],
                    temp_changed,
                )
            )

    # --------------------------------------------------
    # PROPRIEDADES
    # --------------------------------------------------

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
    def target_temperature_step(self):
        return 1

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

    # --------------------------------------------------
    # 🧠 DEBOUNCE INTELIGENTE
    # --------------------------------------------------

    async def _schedule_sensor_sync(self):
        """Agenda sincronização, sempre mantendo apenas a última."""
        if self._booting:
            return

        # Cancela sync pendente se existir
        if self._pending_sync_unsub:
            self._pending_sync_unsub()
            self._pending_sync_unsub = None

        # Agenda para daqui 1 segundo
        self._pending_sync_unsub = async_call_later(
            self.hass,
            1.0,
            lambda _now: asyncio.create_task(self._safe_sensor_sync())
        )

    async def _safe_sensor_sync(self):
        if self._updating_from_sensor:
            return

        try:
            self._updating_from_sensor = True
            await self._sync_from_sensor()
        finally:
            self._updating_from_sensor = False
            self._pending_sync_unsub = None

    # --------------------------------------------------
    # SINCRONIZAÇÃO REAL
    # --------------------------------------------------

    async def _sync_from_sensor(self):
        s = self.hass.states.get(self._sensor_power)
        if not s:
            return

        aberto = s.state in ["on", "true", "ligado"]
        modo_atual = self._hvac_mode

        novo = None

        # 1) Ar ligado no HA e sensor FECHOU → DESLIGAR
        if modo_atual != HVACMode.OFF and not aberto:
            novo = HVACMode.OFF

        # 2) Ar desligado no HA e sensor ABRIU → LIGAR COMO COOL
        elif modo_atual == HVACMode.OFF and aberto:
            novo = HVACMode.COOL

        if novo and novo != self._hvac_mode:
            _LOGGER.info("[%s] Sync sensor → %s", self._name, novo)
            self._hvac_mode = novo
            self.async_write_ha_state()

    # --------------------------------------------------
    # COMANDOS
    # --------------------------------------------------

    async def async_set_hvac_mode(self, hvac_mode):
        if hvac_mode == self._hvac_mode:
            return

        self._hvac_mode = hvac_mode

        if hvac_mode == HVACMode.OFF:
            await self._send("off")
        else:
            await self._send_combined()

        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs):
        temp = int(kwargs.get("temperature"))

        if temp == self._target_temperature:
            return

        self._target_temperature = temp

        await self._send_combined()
        self.async_write_ha_state()

    async def async_set_fan_mode(self, fan_mode):
        if fan_mode == self._fan_mode:
            return

        self._fan_mode = fan_mode

        await self._send_combined()
        self.async_write_ha_state()

    # --------------------------------------------------
    # MONTAGEM IR
    # --------------------------------------------------

    async def _send_combined(self):
        if self._hvac_mode == HVACMode.OFF:
            key = "off"
        else:
            fan = {
                FAN_LOW: "low",
                FAN_MEDIUM: "medium",
                FAN_HIGH: "high",
                FAN_AUTO: "auto",
                FAN_FOCUS: "focus",
            }.get(self._fan_mode, "auto")

            mode = str(self._hvac_mode).lower()
            key = f"{mode}_{fan}_{self._target_temperature}"

        await self._send(key)

    # --------------------------------------------------
    # ENVIO BROADLINK
    # --------------------------------------------------

    async def _send(self, command):

        if self._sensor_power:
            s = self.hass.states.get(self._sensor_power)
            if s and command == "off" and s.state == "off":
                return

        _LOGGER.info(
            "[%s] IR -> %s (controller=%s device=%s)",
            self._name,
            command,
            self._controller,
            self._remote,
        )

        await self.hass.services.async_call(
