import random
from typing import Dict, Any
from hr_game.data.company import GameState, Company, CrisisEvent
from hr_game.data.employee import Employee, EmployeeDelta, EmployeeNetwork
from hr_game.creation.employee import (
    generate_employee_for_company,
    generate_employees_batch_llm,
)
from hr_game.creation.network import create_fully_connected_network
from hr_game.events.example import (
    EMPLOYEE_EVENT_BUS,
    EMPLOYEE_EFFECTING_EVENT_BUS,
    EMPLOYEE_RELATIONSHIP_EVENT_BUS,
)
from hr_game.events.crisis import generate_crisis_events, apply_crisis_resolution
from hr_game.events.user_actions import *
from hr_game.llm.utils import get_llm
from hr_game.llm.scoring import score_delta


class GameEngine:
    def __init__(self):
        self.llm = get_llm()

    def create_company_from_setup(self, setup: Dict[str, Any]) -> GameState:
        """Create a full company with employees based on user setup"""
        company = Company(
            name=setup["name"],
            motto=setup["motto"],
            industry=setup["industry"],
            size=setup["size"],
            culture=setup["culture"],
            org_structure=setup["org_structure"],
        )

        employee_count = {"startup": 12, "mid": 35, "enterprise": 85}[company.size]
        departments = [
            "Engineering",
            "Sales",
            "Marketing",
            "HR",
            "Finance",
            "Operations",
        ]

        employees = []
        print(f"\n🏗️  Creating {employee_count} employees for {company.name}...")

        batch_size = 8  # Process employees in batches to avoid too long prompts

        for batch_start in range(0, employee_count, batch_size):
            batch_end = min(batch_start + batch_size, employee_count)
            batch_employees = []

            print(
                f"  Creating employees {batch_start+1}-{batch_end}/{employee_count}..."
            )

            # Create base employees without LLM calls
            for i in range(batch_start, batch_end):
                dept = random.choice(departments)
                level = random.choice(["L1", "L2", "L3", "L4", "L5"])
                role = "Engineer" if dept == "Engineering" else f"{dept} Specialist"

                employee = generate_employee_for_company(
                    company, role, dept, level, self.llm, seed=i
                )
                batch_employees.append(employee)

            # Generate backstories/values/goals for the batch with single LLM call
            if batch_employees:
                print(f"  Generating personalities for batch...")
                batch_employees = generate_employees_batch_llm(
                    company, batch_employees, self.llm
                )

            employees.extend(batch_employees)

        if company.org_structure == "hierarchical":
            managers = [e for e in employees if e.level in ["L4", "L5"]]
            for emp in employees:
                if emp.level in ["L1", "L2", "L3"]:
                    possible_managers = [
                        m
                        for m in managers
                        if m.department == emp.department and m != emp
                    ]
                    if possible_managers:
                        emp.manager_id = random.choice(possible_managers).employee_id

        network = create_fully_connected_network(employees)

        return GameState(company=company, network=network)

    def step_day(self, game_state: GameState) -> GameState:
        """Advance the game by one day"""
        game_state.day += 1

        employees = game_state.network.employees
        relationships = game_state.network.relationships

        for emp in employees.values():
            sampled_events = random.sample(
                EMPLOYEE_EVENT_BUS, min(3, len(EMPLOYEE_EVENT_BUS))
            )
            for event in sampled_events:
                if random.random() > 0.7:
                    delta = event.pdf(emp, random.random())
                    emp.update(delta)

        for i, (e1_id, e2_id, rel) in enumerate(relationships):
            if e1_id in employees and e2_id in employees:
                e1, e2 = employees[e1_id], employees[e2_id]

                rel_events = random.sample(
                    EMPLOYEE_RELATIONSHIP_EVENT_BUS,
                    min(2, len(EMPLOYEE_RELATIONSHIP_EVENT_BUS)),
                )
                for event in rel_events:
                    if random.random() > 0.8:
                        rel_delta = event.pdf((rel, e1, e2), random.random())
                        rel.update(rel_delta)

                eff_events = random.sample(
                    EMPLOYEE_EFFECTING_EVENT_BUS,
                    min(2, len(EMPLOYEE_EFFECTING_EVENT_BUS)),
                )
                for event in eff_events:
                    if random.random() > 0.8:
                        e1_delta = event.pdf((rel, e1), random.random())
                        e1.update(e1_delta)
                        e2_delta = event.pdf((rel, e2), random.random())
                        e2.update(e2_delta)

        if game_state.day % 7 == 0:
            new_crises = generate_crisis_events(game_state)
            game_state.crisis_events.extend(new_crises)

        for crisis in game_state.crisis_events:
            crisis.days_remaining -= 1

        game_state.crisis_events = [
            c for c in game_state.crisis_events if c.days_remaining > 0
        ]

        self.check_game_over_conditions(game_state)

        return game_state

    def conduct_employee_meeting(self, employee: Employee, user_message: str) -> str:
        """Have a conversation with an employee and return their response"""
        persona = f"""You are {employee.name}, a {employee.level} {employee.role} in {employee.department}.

        Background: {employee.backstory}
        Values: {', '.join(employee.values)}
        Goals: {', '.join(employee.goals)}
        Recent events: {', '.join(employee.mem_short[-3:]) if employee.mem_short else 'None'}

        Current state:
        - Happiness: {employee.happiness}/100
        - Stress: {employee.stress}/100  
        - Anger: {employee.anger}/100
        - Health: {employee.health}/100

        You're meeting with your HR/CEO. Respond naturally based on your personality and current state. Keep responses to 2-3 sentences."""

        try:
            response = self.llm.invoke(
                f"{persona}\n\nHR/CEO says: {user_message}\n\nYour response:"
            ).content.strip()

            conversation = f"HR: {user_message}\n{employee.name}: {response}"
            delta = score_delta(self.llm, conversation)
            employee.update(delta)

            employee.mem_short.append(
                f"Meeting with leadership: {user_message[:50]}..."
            )
            if len(employee.mem_short) > 10:
                employee.mem_short = employee.mem_short[-10:]

            return response
        except Exception as e:
            return f"I... I'm not sure what to say. ({str(e)})"

    def apply_user_action(
        self, game_state: GameState, action: str, target_employee_id: str = None
    ):
        """Apply a user action to the game state"""
        if (
            not target_employee_id
            or target_employee_id not in game_state.network.employees
        ):
            return "Employee not found."

        employee = game_state.network.employees[target_employee_id]

        if action == "promote":
            event = PromoteEmployee()
            delta = event.pdf(employee, 0.5)
            employee.update(delta)

            levels = ["L1", "L2", "L3", "L4", "L5"]
            if (
                employee.level in levels
                and levels.index(employee.level) < len(levels) - 1
            ):
                employee.level = levels[levels.index(employee.level) + 1]

            employee.mem_short.append("Got promoted by leadership")
            return f"Promoted {employee.name}. {event.description(delta)}"

        elif action == "reprimand":
            event = ReprimandEmployee()
            delta = event.pdf(employee, 0.5)
            employee.update(delta)
            employee.mem_short.append("Was reprimanded by leadership")
            return f"Reprimanded {employee.name}. {event.description(delta)}"

        elif action == "give_raise":
            event = GiveRaise()
            delta = event.pdf(employee, 0.5)
            employee.update(delta)
            employee.mem_short.append("Got a raise from leadership")
            game_state.company.budget -= delta.salary
            return f"Gave {employee.name} a raise. {event.description(delta)}"

        elif action == "give_pto":
            event = GivePTO()
            delta = event.pdf(employee, 0.5)
            employee.update(delta)
            employee.mem_short.append("Got approved time off")
            return f"Approved PTO for {employee.name}. {event.description(delta)}"

        elif action == "fire":
            event = FireEmployee()
            delta = event.pdf(employee, 0.5)

            del game_state.network.employees[target_employee_id]

            game_state.network.relationships = [
                (e1, e2, rel)
                for e1, e2, rel in game_state.network.relationships
                if e1 != target_employee_id and e2 != target_employee_id
            ]

            for emp in game_state.network.employees.values():
                emp_delta = EmployeeDelta(
                    stress=5,
                    happiness=-5,
                    health=0,
                    greed=5,
                    salary=0,
                    horniness=0,
                    anger=5,
                    productivity=-5,
                )
                emp.update(emp_delta)
                emp.mem_short.append(f"Witnessed {employee.name} get fired")

            return f"Fired {employee.name}. {event.description(delta)}"

        return "Unknown action."

    def check_game_over_conditions(self, game_state: GameState):
        """Check if the game should end"""
        employees = list(game_state.network.employees.values())

        if len(employees) == 0:
            game_state.game_over = True
            game_state.game_over_reason = "All employees have left the company!"
            return

        if game_state.company.budget < -500000:
            game_state.game_over = True
            game_state.game_over_reason = "Company has gone bankrupt!"
            return

        avg_happiness = sum(e.happiness for e in employees) / len(employees)
        if avg_happiness < 10 and game_state.day > 30:
            game_state.game_over = True
            game_state.game_over_reason = "Company culture has completely collapsed!"
            return

        high_anger_count = len([e for e in employees if e.anger > 80])
        if high_anger_count > len(employees) * 0.7:
            game_state.game_over = True
            game_state.game_over_reason = (
                "Workplace has become too toxic - mass resignation!"
            )
            return

    def get_company_metrics(self, game_state: GameState) -> Dict[str, Any]:
        """Get current company performance metrics"""
        employees = list(game_state.network.employees.values())

        if not employees:
            return {"error": "No employees"}

        return {
            "employee_count": len(employees),
            "avg_happiness": sum(e.happiness for e in employees) / len(employees),
            "avg_stress": sum(e.stress for e in employees) / len(employees),
            "avg_productivity": sum(e.productivity for e in employees) / len(employees),
            "budget": game_state.company.budget,
            "high_risk_employees": len(
                [e for e in employees if e.happiness < 30 and e.anger > 60]
            ),
            "day": game_state.day,
        }
