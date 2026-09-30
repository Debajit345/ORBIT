"""CPU/GPU detection and VRAM-aware model placement."""

from dataclasses import dataclass
import importlib.util


@dataclass(frozen=True)
class ComputeDevice:
    """Available compute target."""

    name: str
    kind: str
    memory_gib: float | None
    runtime: str


@dataclass(frozen=True)
class ModelRequirement:
    """Approximate model resource requirement."""

    name: str
    memory_gib: float


class ComputeScheduler:
    """Choose a safe compute target with CPU fallback."""

    def __init__(self, devices: list[ComputeDevice] | None = None) -> None:
        self.devices = devices or self.detect()

    @staticmethod
    def detect() -> list[ComputeDevice]:
        devices = [
            ComputeDevice(
                name="cpu",
                kind="cpu",
                memory_gib=None,
                runtime="python",
            )
        ]

        if importlib.util.find_spec("torch") is None:
            return devices

        try:
            import torch
        except ImportError:
            return devices

        if not torch.cuda.is_available():
            return devices

        runtime = "rocm" if getattr(torch.version, "hip", None) else "cuda"
        for index in range(torch.cuda.device_count()):
            properties = torch.cuda.get_device_properties(index)
            devices.append(
                ComputeDevice(
                    name=torch.cuda.get_device_name(index),
                    kind="gpu",
                    memory_gib=properties.total_memory / 2**30,
                    runtime=runtime,
                )
            )

        return devices

    def select(
        self,
        requirement: ModelRequirement,
        *,
        prefer_gpu: bool = True,
    ) -> ComputeDevice:
        """Select a device that can fit the model, falling back to CPU."""

        if prefer_gpu:
            for device in self.devices:
                if (
                    device.kind == "gpu"
                    and device.memory_gib is not None
                    and device.memory_gib >= requirement.memory_gib
                ):
                    return device

        return next(device for device in self.devices if device.kind == "cpu")