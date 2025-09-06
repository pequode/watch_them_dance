from pydantic import BaseModel, Field

class Trait(BaseModel):
  """Traits modify deltas. The name is the field that its referring to. The effect is how it gets modified"""
  name:str
  effect: float 

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
  traits: list[Trait] = Field(default_factory=lambda x: [],help="A list of traits that that employee has.")
class EmployeeDelta(BaseModel):
  stress: int = Field(...,help="The change in stress of the employee.")
  greed: int = Field(...,help="How much this employee's motivation for money has changed (on a scale from 0-100).")
  salary: int = Field(...,help="How much this employee's salary has changed")
  anger: int = Field(...,help="How much angrier the employee is on a scale (from 0-100).")
  happiness:int = Field(...,help="The happiness of this employee has changed on a scale (from 0-100).")

class EmployeeRelationship(BaseModel):
  attraction: float =Field(1.0,help="The attraction multiplier between these two employees.")
  resentment: float =Field(1.0,help="The multiplier for how much these two make each other angry.")
  synergy: float =Field(1.0,help="The multiplier for how much these two increase each other productivity.")
  friendship: float =Field(1.0,help="The multiplier for how much these two increase each others happiness")
