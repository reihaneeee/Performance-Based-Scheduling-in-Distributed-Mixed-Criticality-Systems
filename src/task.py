from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Literal, Dict, Any

Criticality = Literal["HI", "LO"]

@dataclass
class Task:
    """
    Mixed-criticality periodic task.
    Notation follows the paper as much as possible.

    Fields:
      - c_lo: WCET in low-criticality mode (C_i^LO)
      - c_hi: WCET in high-criticality mode (C_i^HI) (0 for LO tasks)
      - period: P_i (also deadline D_i = P_i)
      - flag: interference flag F_i (same flag => interfering tasks)
    """
    task_id: int
    criticality: Criticality
    c_lo: float
    c_hi: float
    period: int
    flag: int = 1

    @property
    def deadline(self) -> int:
        return self.period

    # Acquisition/Replication "counts" (paper uses 10% of WCET)
    @property
    def ac_lo(self) -> float:
        return 0.1 * self.c_lo

    @property
    def rp_lo(self) -> float:
        return 0.1 * self.c_lo

    @property
    def ac_hi(self) -> float:
        return 0.1 * self.c_hi

    @property
    def rp_hi(self) -> float:
        return 0.1 * self.c_hi

    @property
    def u_lo(self) -> float:
        return self.c_lo / self.period if self.period else 0.0

    @property
    def u_hi(self) -> float:
        return self.c_hi / self.period if self.period else 0.0

    def __repr__(self) -> str:
        return (
            f"Task(id={self.task_id}, X={self.criticality}, "
            f"C_LO={self.c_lo:.3f}, C_HI={self.c_hi:.3f}, "
            f"P={self.period}, F={self.flag})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Row representation for CSV."""
        return {
            "ID": self.task_id,
            "Criticality": self.criticality,
            "C_LO": self.c_lo,
            "C_HI": self.c_hi,
            "Period": self.period,
            "Deadline": self.deadline,
            "AC_LO": self.ac_lo,
            "RP_LO": self.rp_lo,
            "AC_HI": self.ac_hi,
            "RP_HI": self.rp_hi,
            "Flag": self.flag,
            "U_LO": self.u_lo,
            "U_HI": self.u_hi,
        }

    @staticmethod
    def from_any_dict(d: Dict[str, Any]) -> "Task":
        """Load from old/new CSV schemas (compat with Reihaneh's fields)."""
        crit = str(d.get("Criticality", d.get("criticality", "LO"))).upper()
        if crit in ["HIGH", "HI", "H"]:
            crit2: Criticality = "HI"
        else:
            crit2 = "LO"

        c_lo = float(d.get("C_LO", d.get("C_LOW", d.get("c_low", 0.0))))
        c_hi = float(d.get("C_HI", d.get("C_HIGH", d.get("c_high", 0.0))))
        # For LO tasks, force C_HI=0 to match Table 1 model in the paper
        if crit2 == "LO":
            c_hi = 0.0

        period = int(float(d.get("Period", d.get("period", 0))))
        flag = int(float(d.get("Flag", d.get("flag", 1))))
        task_id = int(float(d.get("ID", d.get("task_id", 0))))
        return Task(task_id=task_id, criticality=crit2, c_lo=c_lo, c_hi=c_hi, period=period, flag=flag)
