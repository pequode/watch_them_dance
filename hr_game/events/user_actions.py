from hr_game.data.employee import Employee, EmployeeDelta
from hr_game.events.base import EmployeeEvent


class PromoteEmployee(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        return EmployeeDelta(
            stress=5,
            happiness=25,
            health=0,
            greed=-5,
            salary=15_000,
            horniness=0,
            anger=-5,
            productivity=10,
        )

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "Promoted! They're thrilled about the new role and salary bump."


class ReprimandEmployee(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        return EmployeeDelta(
            stress=15,
            happiness=-20,
            health=-5,
            greed=5,
            salary=0,
            horniness=0,
            anger=15,
            productivity=-10,
        )

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "Reprimanded. They're upset and demotivated by the criticism."


class GiveRaise(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        raise_amount = max(5_000, int(prior.salary * 0.1))
        return EmployeeDelta(
            stress=-5,
            happiness=15,
            health=0,
            greed=-10,
            salary=raise_amount,
            horniness=0,
            anger=-5,
            productivity=5,
        )

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return f"Got a raise of ${result.salary:,}! They're feeling appreciated."


class TransferDepartment(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        stress_change = 10 if random_var > 0.5 else -5
        happiness_change = 5 if random_var > 0.5 else -10
        return EmployeeDelta(
            stress=stress_change,
            happiness=happiness_change,
            health=0,
            greed=0,
            salary=0,
            horniness=0,
            anger=0,
            productivity=0,
        )

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        if result.happiness > 0:
            return "Transferred to new department. They're excited for the fresh start."
        return "Transferred to new department. They're anxious about the change."


class FireEmployee(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        return EmployeeDelta(
            stress=50,
            happiness=-50,
            health=-20,
            greed=20,
            salary=-prior.salary,
            horniness=0,
            anger=50,
            productivity=-50,
        )

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "Fired. They're devastated and furious."


class GivePTO(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        return EmployeeDelta(
            stress=-20,
            happiness=20,
            health=10,
            greed=0,
            salary=0,
            horniness=0,
            anger=-10,
            productivity=5,
        )

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "Approved for time off. They're refreshed and grateful."
