from pydantic import BaseModel, Field

from hr_game.events.utils import sigmoid
def bound(inp,top,bottom):
  return max(bottom,min(top,inp))

class Trait(BaseModel):
  """Traits modify deltas. The name is the field that its referring to. The effect is how it gets modified"""
  name:str
  effect: float 

class Delta(BaseModel):
  """This is a change in some attribute."""

class EmployeeDelta(Delta):
  stress: int = Field(...,help="The change in stress of the employee.")
  greed: int = Field(...,help="How much this employee's motivation for money has changed (on a scale from -100-100).")
  salary: int = Field(...,help="How much this employee's salary has changed")
  anger: int = Field(...,help="How much angrier the employee is on a scale (from -100-100).")
  happiness:int = Field(...,help="How the happiness of this employee has changed on a scale (from -100-100).")
  health:int = Field(...,help="How the health of this employee has changed on a scale (from -100-100).")
  horniness:int = Field(...,help="The horniness of this employee on a scale from 0-100")
  productivity:int = Field(...,help="The productivity of this employee on a scale from 0-100")
class Employee(BaseModel):
  name:str
  age: int = Field(...,help="The age of the employee")
  stress: int = Field(0,help="The stress of the employee on a scale from 0-100")
  greed: int = Field(20,help="How much this employee is motivated by greed on a scale from 0-100")
  salary: int = Field(80_000,help="How much this employee is paid yearly")
  anger: int = Field(0,help="The anger of this employee on a scale from 0-100")
  horniness: int = Field(0,help="The lobito of this employee on a scale from 0-100")
  happiness:int = Field(50,help="The happiness of this employee on a scale from 0-100")
  productivity:int = Field(10,help="How productive this employee is on a scale from 0-100")
  health: int =Field(75,help="How healthy this employee is on a scale from 0-100")
  context_history:list[str] = Field(default_factory=lambda x: [],help="A list of traits that that employee has.") 
  traits: list[Trait] = Field(default_factory=lambda x: [],help="A list of traits that that employee has.")
  def update(self,other:EmployeeDelta):
    self.stress = bound(other.stress+self.stress,100,0)
    self.greed = bound(other.greed+self.greed,100,0)
    self.salary = bound(other.salary+self.salary,100_000_000,0)
    self.anger = bound(other.anger + self.anger,100,0)
    self.health = bound(other.health + self.health,100,0)
    self.happiness = bound(other.happiness + self.happiness,100,0)
    self.horniness = bound(other.horniness + self.horniness,100,0)
    self.productivity = bound(other.productivity + self.productivity,100,0)
  @property
  def employee_id(self)->str:
    return self.name+ str(hash(self.model_dump()))
class EmployeeRelationshipDelta(BaseModel):
  attraction: float =Field(1.0,help="The change in the attraction multiplier between these two employees.")
  resentment: float =Field(1.0,help="The change in the  multiplier for how much these two make each other angry.")
  synergy: float =Field(1.0,help="The change in the  multiplier for how much these two increase each other productivity.")
  friendship: float =Field(1.0,help="The change in the  multiplier for how much these two increase each others happiness")

class EmployeeRelationship(BaseModel):
  attraction: float =Field(1.0,help="The attraction multiplier between these two employees.")
  resentment: float =Field(1.0,help="The multiplier for how much these two make each other angry.")
  synergy: float =Field(1.0,help="The multiplier for how much these two increase each other productivity.")
  friendship: float =Field(1.0,help="The multiplier for how much these two increase each others happiness")
  def update(self,other:EmployeeRelationshipDelta):
    self.attraction *=sigmoid(other.attraction, top=2,midpoint=1)
    self.resentment *=sigmoid(other.resentment, top=2,midpoint=1)
    self.synergy *=sigmoid(other.synergy, top=2,midpoint=1)
    self.friendship *=sigmoid(other.friendship, top=2,midpoint=1)
  
class EmployeeNetwork(BaseModel):
  employees:dict[str,Employee]
  relationships:list[tuple[str,str,EmployeeRelationship]]

