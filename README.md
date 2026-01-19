# Climate Broadlink - Home Assistant

Integração para transformar códigos Broadlink em entidade Climate real.

## Configuração

```yaml
climate:
  - platform: climate_broadlink
    name: Sala
    controller: remote.broadlink_sala
    remote: remote.climate.sala
    temp_sensor: sensor.temp_sala

