from enum import Enum

from greeclimate.device import Mode as DeviceMode

from ..app import app
from ..binds import search_bind


class Status(str, Enum):
    ON = "on"
    OFF = "off"


class Mode(str, Enum):
    AUTO = "auto"
    COOL = "cool"
    DRY = "dry"
    FAN = "fan"
    HEAT = "heat"


MODE_MAP = {
    Mode.AUTO: DeviceMode.Auto,
    Mode.COOL: DeviceMode.Cool,
    Mode.DRY: DeviceMode.Dry,
    Mode.FAN: DeviceMode.Fan,
    Mode.HEAT: DeviceMode.Heat,
}


@app.command(name="set")
async def set_command(
    name: str,
    /,
    power: Status | None = None,
    mode: Mode | None = None,
    target_temperature: int | None = None,
    light: Status | None = None,
    power_save: Status | None = None,
) -> None:
    if bind := search_bind(name):
        device = await bind.device()

        if power:
            device.power = power == Status.ON
        if mode:
            device.mode = MODE_MAP[mode]
        if target_temperature is not None:
            await device.update()
            device.target_temperature = target_temperature
        if light:
            device.light = light == Status.ON
        if power_save:
            device.power_save = power_save == Status.ON

        await device.push_state_update()
