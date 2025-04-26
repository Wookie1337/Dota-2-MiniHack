import time
import logging
from typing import Optional, Callable, Union
from utils.helpers import is_admin

import pymem
import pymem.process
import psutil

logger = logging.getLogger("dota_minihack")


class Memory:
    def __init__(self, exe_name: str) -> None:
        self.process: Optional[pymem.Pymem] = None
        self.pid: Optional[int] = None
        self.phandle: Optional[int] = None
        self.modules: dict[str, pymem.process.Module] = {}

        if not self._initialize(exe_name):
            raise RuntimeError(
                f"Failed to initialize memory for process: {exe_name}"
            )

    def _initialize(self, exe_name: str) -> bool:
        self._connect_to_process(exe_name)
        if self.process is None:
            logger.critical(f"[X] Process {exe_name} not found.")
            return False

        self.pid = self.process.process_id
        self.phandle = self.process.process_handle
        self._load_modules()
        logger.info("[✓] Memory interface initialized.")
        return True

    def _connect_to_process(self, exe_name: str) -> None:
        logger.debug(f"Searching for process: {exe_name}")

        while self.process is None:
            for proc in psutil.process_iter(["name"]):
                if proc.info["name"] == exe_name:
                    try:
                        self.process = pymem.Pymem(exe_name)
                        logger.info(
                            f"[+] Connected to {exe_name} "
                            f"(PID: {self.process.process_id})"
                        )
                        return
                    except Exception as e:
                        if not is_admin():
                            logger.exception(
                                "Run the program as an administrator!"
                            )
                        else:
                            logger.exception(
                                f"[!] Error attaching to process: {e}"
                            )
            time.sleep(1)

    def _load_modules(self) -> None:
        required_modules = [
            "client.dll",
            "engine2.dll",
            "panorama.dll",
            "particles.dll",
        ]

        logger.debug("[*] Loading process modules...")

        for name in required_modules:
            while True:
                module = pymem.process.module_from_name(self.phandle, name)
                self.modules[name] = module
                if module is None:
                    time.sleep(1)
                    continue
                logger.debug(f"[✓] Loaded module: {name}")
                break

    @staticmethod
    def check_write(func: Callable) -> Callable:
        def wrapper(self, *args, **kwargs) -> bool:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger.exception(f"[X] Memory write failed: {e}")
                return False

        return wrapper

    def get_absolute_address(
        self, instr_ptr: int, offset: int = 3, size: int = 7
    ) -> int:
        """
        Computes absolute address from relative offset in instruction.
        """
        try:
            value = self.process.read_uint(instr_ptr + offset)
            return instr_ptr + value + size
        except Exception as e:
            logger.exception(f"[X] Failed to compute absolute address: {e}")
            raise

    def _normalize_bytes(self, pattern: str) -> bytes:
        return bytes(
            "".join(
                "\\x" + b if b not in {"??", "?"} else "." for b in pattern.split()
            ),
            encoding="latin-1",
        )

    def aob_scan_module(
        self, pattern: Union[str, list[str]], module: str
    ) -> Optional[int]:
        """
        Scans a module for the given pattern(s).
        """
        if module not in self.modules:
            logger.error(f"[X] Module {module} not found.")
            return None

        patterns = [pattern] if isinstance(pattern, str) else pattern
        for pat in patterns:
            try:
                result = self.process.pattern_scan_module(
                    self._normalize_bytes(pat), self.modules[module]
                )
                if result:
                    logger.debug(
                        f"[✓] Pattern found in {module} at 0x{result:X}"
                    )
                    return result
            except Exception as e:
                logger.exception(
                    f"[!] Pattern scan error: {e}"
                )

        logger.warning(f"[!] Pattern not found in {module}.")
        return None

    def patch(self, address: int, patch_bytes: bytes) -> None:
        """
        Writes patch bytes to a given memory address.
        """
        if not address:
            logger.warning("[!] Patch skipped: null address.")
            return
        try:
            self.process.write_bytes(
                address=address,
                value=patch_bytes,
                lenght=len(patch_bytes))
            logger.debug(f"[+] Memory patched at 0x{address:X}")
        except Exception as e:
            logger.exception(f"[X] Patch failed at 0x{address:X}: {e}")

    def read_pointer(self, base: Union[str, int], offsets: list[int]) -> Optional[int]:
        """
        Follows pointer chain from base with given offsets.
        """
        try:
            if isinstance(base, str):
                base = self.modules[base].lpBaseOfDll

            for offset in offsets[:-1]:
                base = self.process.read_longlong(base + offset)

            final_address = base + offsets[-1]
            logger.debug(f"[+] Pointer resolved to: 0x{final_address:X}")
            return final_address
        except Exception as e:
            logger.exception(f"[X] Failed to resolve pointer: {e}")
            return None
