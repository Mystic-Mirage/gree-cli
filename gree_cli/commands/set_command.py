import asyncio
from enum import Enum
from typing import Annotated

import typer
from greeclimate.device import Mode as DeviceMode

from ..async_command import async_command
from ..binds import get_keymap, read_binds


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


@async_command("set")
async def set_command(
    name: str,
    power: Annotated[Status | None, typer.Option()] = None,
    mode: Annotated[Mode | None, typer.Option()] = None,
    target_temperature: Annotated[int | None, typer.Option()] = None,
    light: Annotated[Status | None, typer.Option()] = None,
    power_save: Annotated[Status | None, typer.Option()] = None,
) -> None:
    binds = read_binds()
    alias2bind_map = get_keymap("alias", binds)
    name2bind_map = get_keymap("name", binds)
    mac2bind_map = get_keymap("mac", binds)

    bind = alias2bind_map.get(name) or name2bind_map.get(name) or mac2bind_map.get(name)
    if bind:
        device = await bind.device()

        if power:
            device.power = power == Status.ON
        if mode:
            device.mode = MODE_MAP[mode]
        if target_temperature is not None:
            await device.update_state()
            while device.temperature_units is None:
                await asyncio.sleep(0.1)
            device.target_temperature = target_temperature
        if light:
            device.light = light == Status.ON
        if power_save:
            device.power_save = power_save == Status.ON

        await device.push_state_update()
