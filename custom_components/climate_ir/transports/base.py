class BaseIRTransport:
    """Interface comum para qualquer backend IR."""

    def __init__(self, hass, config):
        self.hass = hass
        self.config = config

    async def send(self, command: str):
        raise NotImplementedError("Transport not implemented send()")
