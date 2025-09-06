# lets do some employee events: 
from hr_game.data.employee import Employee, EmployeeDelta
from hr_game.events.base import EmployeeEvent

def null_delta_factory()->EmployeeDelta:
    return EmployeeDelta(stress=0,
                happiness=0,
                health=-10,
                greed=20,
                salary=0,
                horniness=-50,
                anger=0)
class HasABaby(EmployeeEvent):
    @staticmethod
    def pdf(prior:Employee,random_var:float)->EmployeeDelta:
        if prior.horniness>50 and 40>prior.age>10 and random_var>0.5:
            return EmployeeDelta(
                stress=10,
                happiness=20,
                health=-10,
                greed=20,
                salary=0,
                horniness=-50,
                anger=0

            )
        return null_delta_factory()
    
    @staticmethod
    def description(result:EmployeeDelta)->str:
        return "They had a kid! Its looks just like them."
class BadDayAtWork(EmployeeEvent):
    @staticmethod
    def pdf(prior:Employee,random_var:float)->EmployeeDelta:
        if random_var>0.8:
            return EmployeeDelta(
                stress=10,
                happiness=-10,
                health=0,
                greed=0,
                salary=0,
                horniness=10,
                anger=10

            )
        return null_delta_factory()
    
    @staticmethod
    def description(result:EmployeeDelta)->str:
        return "Ugh today sucked."
    
class GoodDayAtWork(EmployeeEvent):
    @staticmethod
    def pdf(prior:Employee,random_var:float)->EmployeeDelta:
        if random_var>0.8:
            return EmployeeDelta(
                stress=-10,
                happiness=10,
                health=0,
                greed=0,
                salary=0,
                horniness=-10,
                anger=-10

            )
        return null_delta_factory()
    
    @staticmethod
    def description(result:EmployeeDelta)->str:
        return "Ugh today rocked!."
### gpt contributed 
class CoffeeBreak(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        # If already very stressed, coffee helps more
        stress_relief = min(10, prior.stress // 2)
        if random_var > 0.3:
            return EmployeeDelta(
                stress=-stress_relief,
                happiness=5,
                health=0,
                greed=0,
                salary=0,
                horniness=0,
                anger=0
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "They took a coffee break and feel a bit better."


class OfficeGossip(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        # Gossip affects angry employees more
        anger_increase = 5 + prior.anger // 10
        happiness_loss = 2 + prior.happiness // 20
        if random_var > 0.6:
            return EmployeeDelta(
                stress=2,
                happiness=-happiness_loss,
                health=0,
                greed=0,
                salary=0,
                horniness=0,
                anger=anger_increase
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "They got caught up in office gossip. Drama everywhere!"


class Promotion(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        # If very greedy, promotion feels better
        happiness_boost = 20 + prior.greed // 5
        stress_increase = 5 + prior.stress // 10
        if random_var > 0.9:
            return EmployeeDelta(
                stress=stress_increase,
                happiness=happiness_boost,
                health=0,
                greed=-10,
                salary=20_000,
                horniness=0,
                anger=0
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "Congratulations! They got promoted and their salary increased."


class MissedDeadline(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        # If already stressed, missing a deadline is worse
        stress_increase = 10 + prior.stress // 5
        happiness_loss = 10 + prior.happiness // 10
        if random_var > 0.5:
            return EmployeeDelta(
                stress=stress_increase,
                happiness=-happiness_loss,
                health=-5,
                greed=0,
                salary=0,
                horniness=0,
                anger=10
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "They missed a deadline and feel awful."
# create event for network. 
EMPLOYEE_EVENT_BUS = [HasABaby(),GoodDayAtWork(),BadDayAtWork(),CoffeeBreak(),OfficeGossip(),MissedDeadline(),Promotion(),MissedDeadline()]
