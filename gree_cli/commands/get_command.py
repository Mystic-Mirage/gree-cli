from typing import Annotated

import typer

from ..async_command import async_command
from ..binds import search_bind

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

    if bind := search_bind(name):
        device = await bind.device()
        await device.update()

        if power:
            typer.echo(STATE_MAP[device.power])
        elif current_temperature:
            typer.echo(device.current_temperature)
