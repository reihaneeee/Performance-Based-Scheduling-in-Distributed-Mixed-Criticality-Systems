import math

class Task:
    def __init__ (self, task_id, criticality, c_low, c_high, period, flag=0):
        self.id = task_id
        self.criticality = criticality
        self.c_low = c_low
        self.c_high = c_high
        self.period = period
        # Di = Pi
        self.deadline = period
        self.flag = flag 

        self.ap = 0.1 * c_low           # AP = 10% of C_LOW
        self.rp = 0.1 * c_low           # RP = 10% of C_HIGH

        # Utilization calculation
        self.u_low = self.c_low / self.period
        self.u_high = self.c_high / self.period
    
    def __represent__ (self):
        return (f"Task(ID={self.id}, X={self.criticality}, "
                f"C_LOW={self.c_low:0.2f}, C_HIGH={self.c_high:.2f}, "
                f"T={self.period}, F={self.flag})")
    
    # serialize task for CSV
    def to_dict(self):
        return {
            "ID": self.id,
            "Criticality": self.criticality,
            "C_LOW": self.c_low,
            "C_HIGH": self.c_high,
            "Period": self.period,
            "Deadline": self.deadline,
            "AP": self.ap,
            "RP": self.rp,
            "Flag": self.flag,
            "U_LOW": self.u_low,
            "U_HIGH": self.u_high
        }