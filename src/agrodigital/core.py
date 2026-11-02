"""Execution-mode planning and capability reporting."""
from dataclasses import dataclass, asdict
from typing import Iterable

@dataclass(frozen=True)
class CapabilityReport:
    python_version: str
    available_modules: tuple[str, ...]
    missing_modules: tuple[str, ...]
    def to_dict(self) -> dict:
        return asdict(self)

@dataclass(frozen=True)
class ExecutionPlan:
    mode: str
    reason: str
    required_capabilities: tuple[str, ...]
    available_capabilities: tuple[str, ...]
    fallback: str
    def to_dict(self) -> dict:
        return asdict(self)

def inspect_python_capabilities(modules: Iterable[str] = ("numpy", "shapely", "pyproj", "rasterio")) -> CapabilityReport:
    """Inspect optional local Python modules without installing anything."""
    import importlib.util, platform
    available, missing = [], []
    for name in modules:
        (available if importlib.util.find_spec(name) else missing).append(name)
    return CapabilityReport(platform.python_version(), tuple(available), tuple(missing))

def plan_execution(required_capabilities: Iterable[str], available_capabilities: Iterable[str], *, integrated_service_available: bool = False) -> ExecutionPlan:
    """Choose a transparent mode; an integration must be explicitly confirmed."""
    required = tuple(dict.fromkeys(required_capabilities))
    available_set = set(available_capabilities)
    present = tuple(item for item in required if item in available_set)
    missing = tuple(item for item in required if item not in available_set)
    if not missing:
        return ExecutionPlan("DIRECT", "All declared capabilities are available in this runtime.", required, present, "No fallback required.")
    if integrated_service_available:
        return ExecutionPlan("INTEGRATED", "A required local capability is missing; use the explicitly available authorized service.", required, present, "If the service fails, provide an ASSISTED workflow.")
    return ExecutionPlan("ASSISTED", "One or more required capabilities are unavailable in this runtime.", required, present, "Prepare a reproducible workflow for a free external tool such as Python, QGIS, or Colab.")
