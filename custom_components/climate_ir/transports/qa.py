import logging
import json
import os

from .base import BaseIRTransport

_LOGGER = logging.getLogger(__name__)


class QATransport(BaseIRTransport):

    def __init__(self, hass, config):
        super().__init__(hass, config)

        self.profile = config.get("qa_profile")
        self.device = config.get("controlled_device")
        self.entity = config.get("qa_entity")

        self.codes = {}

        self._ensure_folder()
        self._load_profile()

    # --------------------------------------------------
    # PASTA
    # --------------------------------------------------

    def _ensure_folder(self):
        path = self.hass.config.path("climate_ir")

        if not os.path.exists(path):
            _LOGGER.info("Criando pasta %s", path)
            os.makedirs(path, exist_ok=True)

    # --------------------------------------------------
    # LEITURA
    # --------------------------------------------------

    def _load_profile(self):
        if not self.profile:
            _LOGGER.warning("QA sem profile definido")
            return

        path = self.hass.config.path(
            "climate_ir",
            f"{self.profile}.json"
        )

        if not os.path.exists(path):
            _LOGGER.error("Arquivo QA não encontrado: %s", path)
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            commands = data.get("commands", {})

            if self.device not in commands:
                _LOGGER.error(
                    "Device '%s' não encontrado no arquivo %s",
                    self.device,
                    path,
                )
                return

            self.codes = commands[self.device]

            _LOGGER.info(
                "QA profile=%s device=%s carregado com %d comandos",
                self.profile,
                self.device,
                len(self.codes),
            )

        except Exception as e:
            _LOGGER.exception("Erro lendo QA profile: %s", e)

    # --------------------------------------------------
    # ENVIO REAL
    # --------------------------------------------------

    async def send(self, command: str):

        if not self.entity:
            _LOGGER.error("qa_entity não configurada")
            return

        ir = self.codes.get(command)

        if not ir:
            _LOGGER.error(
                "[QA] Comando '%s' não encontrado (device=%s profile=%s)",
                command,
                self.device,
                self.profile,
            )
            return

        _LOGGER.info(
            "[QA] %s → entidade %s",
            command,
            self.entity,
        )

        # 🔥 Integração real com seu hub
        await self.hass.services.async_call(
            "text",
            "set_value",
            {
                "entity_id": self.entity,
                "value": ir,
            },
            blocking=True,
        )
