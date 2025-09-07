from abc import ABC, abstractmethod
from pydantic import BaseModel
from hr_game.data.employee import Delta, Employee, EmployeeDelta, EmployeeRelationship, EmployeeRelationshipDelta


class Event(ABC):
    @staticmethod
    @abstractmethod
    def pdf(prior: BaseModel, random_var: float) -> Delta:
        """An event is constructed by a probability function characterized by some state.
        This PDF takes in a random variable and returns a delta"""
        pass

    @staticmethod
    @abstractmethod
    def description(result: Delta) -> str:
        """A human readable description of the event"""
        pass


class EmployeeEvent(Event):
    @staticmethod
    @abstractmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        """Employee-specific probability density function"""
        pass

    @staticmethod
    @abstractmethod
    def description(result: EmployeeDelta) -> str:
        """A human readable description of the employee event"""
        pass
    


class EmployeeEffectingEvent(Event):
    @staticmethod
    @abstractmethod
    def pdf(prior: tuple[EmployeeRelationship,Employee], random_var: float) -> EmployeeDelta:
        """Employee-specific probability density function"""
        pass

    @staticmethod
    @abstractmethod
    def description(result: EmployeeDelta) -> str:
        """A human readable description of the employee event"""
        pass
    
class EmployeeRelationshipEvent(Event):
    @staticmethod
    @abstractmethod
    def pdf(prior: tuple[EmployeeRelationship,Employee,Employee], random_var: float) -> EmployeeRelationshipDelta:
        """Employee-specific probability density function"""
        pass

    @staticmethod
    @abstractmethod
    def description(result: EmployeeRelationshipDelta) -> str:
        """A human readable description of the employee event"""
        pass