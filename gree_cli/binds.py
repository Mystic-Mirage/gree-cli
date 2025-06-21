from configparser import ConfigParser
from pathlib import Path

from greeclimate.cipher import CipherBase, CipherV1, CipherV2
from greeclimate.device import Device
from greeclimate.deviceinfo import DeviceInfo
from pydantic import BaseModel, TypeAdapter, field_validator


class Bind(BaseModel):
    mac: str
    ip: str
    port: int
    name: str
    brand: str
    model: str
    version: str
    key: str
    cipher: CipherV1 | CipherV2
    alias: str = ""

    model_config = {"arbitrary_types_allowed": True}

    # noinspection PyNestedDecorators
    @field_validator("cipher", mode="plain")
    @classmethod
    def resolve_cipher(cls, value: str) -> type[CipherBase]:
        return next(
            cipher for cipher in CipherBase.__subclasses__() if cipher.__name__ == value
        )

    async def device(self) -> Device:
        device_info = DeviceInfo(
            ip=self.ip,
            port=self.port,
            mac=self.mac,
            name=self.name,
            brand=self.brand,
            model=self.model,
            version=self.version,
        )
        device = Device(device_info=device_info)
        await device.bind(key=self.key, cipher=self.cipher())
        if device._transport is None:
            device._transport, _ = await device._loop.create_datagram_endpoint(
                lambda: device,
                remote_addr=(device.device_info.ip, device.device_info.port),
            )
        return device


def read_binds(path: str = "gree_binds.ini") -> list[Bind]:
    config = ConfigParser()
    config.read(path)

    data = [{"mac": section, **config[section]} for section in config.sections()]
    binds = TypeAdapter(list[Bind]).validate_python(data)
    return binds


def get_keymap(key: str, binds: list[Bind]) -> dict[str, Bind]:
    return {getattr(bind, key): bind for bind in binds}


def write_binds(binds: list[Device], path: str = "gree_binds.ini") -> None:
    config = ConfigParser()

    old_binds = read_binds(path)
    mac2bind_map = get_keymap("mac", old_binds)

    for device in binds:
        mac = device.device_info.mac
        config.add_section(mac)
        config.set(mac, "alias", bind.alias if (bind := mac2bind_map.get(mac)) else "")
        config.set(mac, "ip", device.device_info.ip)
        config.set(mac, "port", str(device.device_info.port))
        config.set(mac, "name", device.device_info.name)
        config.set(mac, "brand", device.device_info.brand)
        config.set(mac, "model", device.device_info.model)
        config.set(mac, "version", device.device_info.version)
        config.set(mac, "key", device.device_cipher.key)
        config.set(mac, "cipher", device.device_cipher.__class__.__name__)

    with Path(path).open("w") as f:
        config.write(f)
