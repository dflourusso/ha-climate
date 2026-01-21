import logging
from .base import BaseIRTransport

_LOGGER = logging.getLogger(__name__)


class BroadlinkTransport(BaseIRTransport):

    async def send(self, command: str):

        _LOGGER.info(
            "[Broadlink] IR -> %s (controller=%s device=%s)",
            command,
            self.config.get("controller"),
            self.config.get("remote"),
        )

        await self.hass.services.async_call(
            "remote",
            "send_command",
            {
                "entity_id": self.config.get("controller"),
                "device": self.config.get("remote"),
                "command": command,
            },
            blocking=True,
        )
