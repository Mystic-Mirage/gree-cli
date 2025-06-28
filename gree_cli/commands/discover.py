from contextlib import suppress
from typing import Annotated

from cyclopts import Parameter
from greeclimate.device import Device
from greeclimate.discovery import Discovery
from greeclimate.exceptions import DeviceNotBoundError, DeviceTimeoutError

from ..app import app
from ..binds import write_binds


@app.command
async def discover(
    *,
    wait: int = 5,
    bind: Annotated[bool, Parameter(negative="", show_default=False)] = False,
) -> None:
    discovery = Discovery()

    devices = sorted(await discovery.scan(wait_for=wait), key=lambda d: d.mac)

    for device_info in devices:
        print(f"Discovered: {device_info}")

    if bind:
        binds = []

        for device_info in devices:
            print(f"Binding: {device_info}")
            device = Device(device_info)
            with suppress(DeviceNotBoundError, DeviceTimeoutError):
                await device.bind()
                binds.append(device)

        write_binds(binds)
