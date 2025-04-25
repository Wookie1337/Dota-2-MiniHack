from typing import TypedDict, Literal


class SignatureEntry(TypedDict, total=False):
    pattern: str
    module: Literal[
        "client.dll",
        "engine2.dll",
        "panorama.dll",
        "particles.dll"
    ]
    sig_offset: int
    offset: int
    size: int


DATA: dict[str, SignatureEntry] = {
    "dotaCamera": {
        "pattern": (
            "F3 0F 11 05 ? ? ? ? 48 8D 0D ? ? ? ? E8 ? ? ? ? "
            "F3 0F 11 05 ? ? ? ? 48 8D 0D ? ? ? ? 0F 28 05 ? ? ? ? "
            "0F 11 05 ? ? ? ? E8 ? ? ? ? EB 90"
        ),
        "module": "client.dll",
        "sig_offset": 0,
        "offset": 4,
        "size": 8
    },
    "cl_weather": {
        "pattern": (
            "48 8B 05 ? ? ? ? 48 8B 40 08 "
            "83 38 00 74 29 BA FF FF FF FF"
        ),
        "module": "client.dll",
        "sig_offset": 0,
        "offset": 3,
        "size": 7
    },
    "teleports": {
        "pattern": "80 A6 ? ? ? ? ? 41 0F B6 C4",
        "module": "particles.dll",
        "sig_offset": 0
    }
}
