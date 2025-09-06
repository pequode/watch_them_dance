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
    def pdf(self,prior:Employee,random_var:float)->EmployeeDelta:
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
    def pdf(self,prior:Employee,random_var:float)->EmployeeDelta:
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
    def pdf(self,prior:Employee,random_var:float)->EmployeeDelta:
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