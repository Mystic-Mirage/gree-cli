import sys
from typing import Annotated

from cyclopts import Parameter

from ..app import app
from ..binds import search_bind

STATE_MAP = {
    False: "off",
    True: "on",
}


@app.command(name="get")
async def get_command(
    name: str,
    /,
    power: Annotated[bool, Parameter("--power", negative="")] = False,
    current_temperature: Annotated[
        bool, Parameter("--current-temperature", negative="")
    ] = False,
) -> None:

    commands = [
        power,
        current_temperature,
    ]
    if not any(commands):
        print("At least one option must be specified")
        sys.exit(1)
    elif sum(commands) > 1:
        print("Only a single option can be specified")
        sys.exit(1)

    if bind := search_bind(name):
        device = await bind.device()
        await device.update()

        if power:
            print(STATE_MAP[device.power])
        elif current_temperature:
            print(device.current_temperature)
