from enum import Enum
from typing import Annotated

import typer

from ..async_command import async_command
from ..binds import get_keymap, read_binds


class Status(str, Enum):  # Inherit from str to allow string comparison
    on = "on"
    off = "off"


@async_command("set")
async def set_command(
    name: str,
    power: Annotated[Status | None, typer.Option()] = None,
) -> None:
    binds = read_binds()
    alias2bind_map = get_keymap("alias", binds)
    name2bind_map = get_keymap("name", binds)
    mac2bind_map = get_keymap("mac", binds)

    bind = alias2bind_map.get(name) or name2bind_map.get(name) or mac2bind_map.get(name)
    if bind:
        device = await bind.device()

        if power:
            device.power = power == Status.on

        await device.push_state_update()
