from pydantic import BaseModel, Field
from typing import Literal
from hr_game.data.employee import EmployeeNetwork


class Company(BaseModel):
    name: str
    motto: str
    industry: str
    size: Literal["startup", "mid", "enterprise"]
    culture: Literal["toxic", "collaborative", "competitive", "laid_back"]
    org_structure: Literal["flat", "hierarchical", "matrix"]
    profitability: int = Field(50, help="Company financial health 0-100")
    budget: int = Field(1_000_000, help="Available budget for decisions")


class CrisisEvent(BaseModel):
    title: str
    description: str
    options: list[dict[str, str]]  # {"choice": "Fire them", "consequence": "..."}
    days_remaining: int = 3
    severity: Literal["low", "medium", "high", "critical"] = "medium"


class GameState(BaseModel):
    company: Company
    network: EmployeeNetwork
    day: int = 0
    crisis_events: list[CrisisEvent] = Field(default_factory=list)
    completed_crises: list[str] = Field(default_factory=list)
    game_over: bool = False
    game_over_reason: str = ""
