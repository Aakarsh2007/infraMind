from .memory_leak import MemoryLeakScenario
from .db_deadlock import DbDeadlockScenario
from .cascade_failure import CascadeFailureScenario
from .cpu_spike import CpuSpikeScenario
from .auth_bypass import AuthBypassScenario
from .custom import CustomScenario

SCENARIOS = {
    "memory_leak": MemoryLeakScenario,
    "db_deadlock": DbDeadlockScenario,
    "cascade_failure": CascadeFailureScenario,
    "cpu_spike": CpuSpikeScenario,
    "auth_bypass": AuthBypassScenario,
}
