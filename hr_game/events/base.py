
from abc import ABC, abstractmethod, abstractstaticmethod
from typing import Callable

from pydantic import BaseModel

from hr_game.data.employee import Delta, Employee, EmployeeDelta


class Event(ABC):
  @abstractmethod  
  @staticmethod
  def pdf( prior: BaseModel, random_var:float)->Delta:
    """An event is constructed by a probability function characterized by some state. 
    This PDF takes in a random variable and returns a delta"""
    pass
  @abstractmethod  
  @staticmethod
  def description(result:Delta)->str:
    "A human readable description of the event"
    pass 
  

class EmployeeEvent(Event):
  @abstractmethod  
  @staticmethod
  def pdf(self,prior:Employee,random_var:float)->EmployeeDelta:
    pass
  @abstractmethod  
  @staticmethod
  def description(result:Delta)->str:
    pass 
  
class CompanyEvent(Event):
  @abstractmethod  
  @staticmethod
  def pdf(self,prior:Company,random_var:float)->CompanyDelta:
    pass
  
  @abstractmethod  
  @staticmethod
  def description(result:Delta)->str:
    pass 