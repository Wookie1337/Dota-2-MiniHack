import logging
from typing import Optional

from memory.memory import Memory
from data.signatures import DATA

logger = logging.getLogger("dota_minihack")


class DotaOther:
    def __init__(self, memory: Memory) -> None:
        self.memory = memory
        self._teleport_address: Optional[int] = None
        self._data = {"weather": None, "teleports": None}

    def _resolve_cl_weather_address(self) -> Optional[int]:
        """
        Resolves address for controlling weather.
        """
        base = self.memory.aob_scan_module(
            pattern=DATA["cl_weather"]["pattern"],
            module=DATA["cl_weather"]["module"]
        )
        if not base:
            logger.error("[X] cl_weather pattern not found.")
            return None

        try:
            absolute = self.memory.get_absolute_address(
                instr_ptr=base + DATA["cl_weather"]["sig_offset"],
                offset=DATA["cl_weather"]["offset"],
                size=DATA["cl_weather"]["size"],
            )
            address = self.memory.process.read_ulonglong(absolute) + 0x40
            logger.debug(
                msg=f"[✓] Weather control address resolved: 0x{address:X}"
            )
            return address
        except Exception:
            logger.exception(
                msg="[!] Failed to resolve weather address."
            )
            return None

    def _resolve_teleport_address(self) -> Optional[int]:
        """
        Resolves address for teleport toggling.
        """
        if self._teleport_address:
            return self._teleport_address

        base = self.memory.aob_scan_module(
            pattern=DATA["teleports"]["pattern"],
            module=DATA["teleports"]["module"]
        )
        if base:
            self._teleport_address = base
            logger.debug(f"[✓] Teleport control address resolved: 0x{base:X}")
            return base
        else:
            logger.error("[X] Teleport pattern not found.")
            return None

    @Memory.check_write
    def set_weather(self, weather_id: int = 0) -> bool:
        """
        Sets the weather type.
        """
        if self._data["weather"] is None:
            address = self._resolve_cl_weather_address()
            self._data["weather"] = address
            if not address:
                return False

        # logger.debug(f"Setting weather to ID: {weather_id}")
        return self.memory.process.write_int(self._data["weather"], weather_id)

    @Memory.check_write
    def show_teleports(self, enabled: bool = False) -> bool:
        """
        Toggles teleport effects.
        """
        if self._data["teleports"] is None:
            address = self._resolve_teleport_address()
            self._data["teleports"] = address
            if not address:
                return False

        value = 0x8E80 if enabled else 0xA680
        # logger.debug(
        #     f"Setting show teleports "
        #     "{'enabled' if enabled else 'disabled'} "
        #     "(value: 0x{value:X})"
        # )
        return self.memory.process.write_short(self._data["teleports"], value)
