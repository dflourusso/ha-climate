import logging
from .base import BaseIRTransport

_LOGGER = logging.getLogger(__name__)


class QATransport(BaseIRTransport):

    async def send(self, command: str):

        _LOGGER.info(
            "[QA] IR -> %s (device=%s)",
            command,
            self.config.get("remote"),
        )

        # Aqui entra depois:
        # - HTTP
        # - MQTT
        # - SDK do seu hub QA
        pass
