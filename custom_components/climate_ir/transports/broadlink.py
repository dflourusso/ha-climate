import logging
from .base import BaseIRTransport

_LOGGER = logging.getLogger(__name__)


class BroadlinkTransport(BaseIRTransport):

    async def send(self, command: str):

        _LOGGER.info(
            "[Broadlink] IR -> %s (controller=%s device=%s)",
            command,
            self.config.get("controller"),
            self.config.get("controlled_device"),
        )

        await self.hass.services.async_call(
            "remote",
            "send_command",
            {
                "entity_id": self.config.get("controller"),
                "device": self.config.get("controlled_device"),
                "command": command,
            },
            blocking=True,
        )
