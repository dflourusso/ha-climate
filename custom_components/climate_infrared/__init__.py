from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})

    await hass.config_entries.async_forward_entry_setups(entry, ["climate"])

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.info("climate_infrared carregado: %s", entry.title)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    return await hass.config_entries.async_forward_entry_unload(entry, "climate")


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info("Recarregando climate_infrared: %s", entry.title)

    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
