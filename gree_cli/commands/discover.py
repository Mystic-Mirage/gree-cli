from contextlib import suppress

import typer
from greeclimate.device import Device
from greeclimate.discovery import Discovery
from greeclimate.exceptions import DeviceNotBoundError, DeviceTimeoutError

from ..async_command import async_command
from ..binds import write_binds


@async_command()
async def discover(wait: int = 5, bind: bool = False) -> None:
    discovery = Discovery()

    devices = sorted(await discovery.scan(wait_for=wait), key=lambda d: d.mac)

    for device_info in devices:
        typer.echo(f"Discovered: {device_info}")

    if bind:
        binds = []

        for device_info in devices:
            typer.echo(f"Binding: {device_info}")
            device = Device(device_info)
            with suppress(DeviceNotBoundError, DeviceTimeoutError):
                await device.bind()
                binds.append(device)

        write_binds(binds)
