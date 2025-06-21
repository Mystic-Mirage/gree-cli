import asyncio
from typing import Annotated

import typer

from ..async_command import async_command
from ..binds import get_keymap, read_binds

STATE_MAP = {
    False: "off",
    True: "on",
}


@async_command("get")
async def get_command(
    name: str,
    power: Annotated[bool, typer.Option("--power")] = False,
    current_temperature: Annotated[bool, typer.Option("--current-temperature")] = False,
) -> None:

    commands = [
        power,
        current_temperature,
    ]
    if sum(commands) > 1:
        typer.echo("Only a single option can be specified")
        raise typer.Exit(1)

    binds = read_binds()
    alias2bind_map = get_keymap("alias", binds)
    name2bind_map = get_keymap("name", binds)
    mac2bind_map = get_keymap("mac", binds)

    bind = alias2bind_map.get(name) or name2bind_map.get(name) or mac2bind_map.get(name)
    if bind:
        device = await bind.device()

        await device.update_state()
        while device.temperature_units is None:
            await asyncio.sleep(0.1)

        if power:
            typer.echo(STATE_MAP[device.power])
        elif current_temperature:
            typer.echo(device.current_temperature)
