import logging
from typing import Optional

from memory.memory import Memory
from data.signatures import DATA

logger = logging.getLogger("dota_minihack")


class DotaCamera:
    def __init__(self, memory: Memory) -> None:
        self.memory = memory
        self.signature = DATA["dotaCamera"]
        self.camera_address: Optional[int] = self._resolve_camera_address()

        if not self.camera_address:
            logger.error("[X] Failed to initialize camera.")
            raise RuntimeError("Camera base address not found.")

        logger.info(
            f"[✓] Camera initialized at address 0x{self.camera_address:X}"
        )

    def _resolve_camera_address(self) -> Optional[int]:
        """
        Scans memory to resolve the camera base address.
        """
        base = self.memory.aob_scan_module(
            pattern=self.signature["pattern"], module=self.signature["module"]
        )
        if not base:
            logger.error("[X] Camera pattern not found in module.")
            return None

        try:
            absolute = self.memory.get_absolute_address(
                instr_ptr=base + self.signature["sig_offset"],
                offset=self.signature["offset"],
                size=self.signature["size"],
            )
            return absolute
        except Exception:
            logger.exception("[!] Failed to resolve absolute camera address.")
            return None

    @Memory.check_write
    def set_distance(self, distance: float = 1200.0) -> bool:
        """
        Sets camera distance.
        """
        # logger.debug(f"Setting camera distance: {distance}")
        return self.memory.process.write_float(self.camera_address, distance)

    @Memory.check_write
    def set_fov(self, fov: float = 70.0) -> bool:
        """
        Sets field of view (FOV).
        """
        # logger.debug(f"Setting FOV: {fov}")
        return self.memory.process.write_float(
            address=self.camera_address + 0x4,
            value=fov
        )

    @Memory.check_write
    def set_fog_enable(self, enable: bool = True) -> bool:
        """
        Enables or disables fog rendering.
        """
        value = -1.0 if enable else 0.0
        # logger.debug(f"Setting fog enabled: {enable}")
        return self.memory.process.write_float(
            address=self.camera_address + 0xC,
            value=value
        )

    @Memory.check_write
    def set_farz(self, farz: float = -1.0) -> bool:
        """
        Sets far clipping plane.
        """
        # logger.debug(f"Setting FarZ: {farz}")
        return self.memory.process.write_float(
            address=self.camera_address + 0x14,
            value=farz
        )
