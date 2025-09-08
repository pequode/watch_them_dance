import random
from hr_game.data.company import CrisisEvent, GameState
from hr_game.data.employee import Employee, EmployeeDelta


def generate_crisis_events(game_state: GameState) -> list[CrisisEvent]:
    """Generate crisis events based on current game state"""
    crises = []
    employees = list(game_state.network.employees.values())

    if not employees:
        return crises

    avg_satisfaction = sum(e.happiness for e in employees) / len(employees)
    avg_stress = sum(e.stress for e in employees) / len(employees)
    high_anger_count = len([e for e in employees if e.anger > 70])
    low_happiness_count = len([e for e in employees if e.happiness < 30])

    if avg_satisfaction < 30 and random.random() > 0.7:
        crises.append(
            CrisisEvent(
                title="Employee Revolt",
                description="Multiple employees are organizing to demand better working conditions. Morale is at an all-time low and productivity has plummeted. You need to act fast.",
                options=[
                    {
                        "choice": "Meet with employee representatives and negotiate",
                        "consequence": "boost_morale",
                    },
                    {
                        "choice": "Ignore the complaints and crack down harder",
                        "consequence": "anger_increase",
                    },
                    {
                        "choice": "Give everyone a small raise",
                        "consequence": "budget_hit_morale_boost",
                    },
                    {
                        "choice": "Fire the ringleaders",
                        "consequence": "fear_and_resentment",
                    },
                ],
                severity="critical",
            )
        )

    unhappy_employees = [e for e in employees if e.happiness < 20 and e.anger > 60]
    if unhappy_employees and random.random() > 0.6:
        employee = random.choice(unhappy_employees)
        crises.append(
            CrisisEvent(
                title=f"{employee.name} Threatens to Quit",
                description=f"{employee.name} is one of your key {employee.department} employees, but they're extremely unhappy. They've submitted their resignation letter and are giving you one chance to change their mind.",
                options=[
                    {
                        "choice": "Promote them immediately",
                        "consequence": "retain_promote",
                    },
                    {
                        "choice": "Give them a substantial raise",
                        "consequence": "retain_raise",
                    },
                    {
                        "choice": "Have a heart-to-heart conversation",
                        "consequence": "retain_talk",
                    },
                    {"choice": "Let them go", "consequence": "lose_employee"},
                ],
                severity="high",
            )
        )

    if high_anger_count >= 3 and random.random() > 0.8:
        crises.append(
            CrisisEvent(
                title="Workplace Harassment Complaint",
                description="An employee has filed a formal harassment complaint against a colleague. The situation is tense and other employees are watching how you handle it.",
                options=[
                    {
                        "choice": "Launch full investigation",
                        "consequence": "investigation",
                    },
                    {
                        "choice": "Try to mediate between them",
                        "consequence": "mediation",
                    },
                    {
                        "choice": "Move one employee to different department",
                        "consequence": "transfer",
                    },
                    {
                        "choice": "Dismiss the complaint as office drama",
                        "consequence": "ignore_complaint",
                    },
                ],
                severity="high",
            )
        )

    if avg_stress > 70 and random.random() > 0.75:
        crises.append(
            CrisisEvent(
                title="Burnout Epidemic",
                description="Multiple employees are showing signs of severe burnout. Sick days are up 300% and productivity is down. The team is at a breaking point.",
                options=[
                    {
                        "choice": "Mandate company-wide mental health week",
                        "consequence": "mental_health_week",
                    },
                    {
                        "choice": "Hire additional staff to reduce workload",
                        "consequence": "hire_more_staff",
                    },
                    {
                        "choice": "Implement flexible work arrangements",
                        "consequence": "flexible_work",
                    },
                    {
                        "choice": "Push through - they'll adapt",
                        "consequence": "ignore_burnout",
                    },
                ],
                severity="medium",
            )
        )

    if game_state.company.profitability < 20 and random.random() > 0.6:
        crises.append(
            CrisisEvent(
                title="Budget Crisis - Layoffs Required",
                description="The company is in financial trouble. The board is demanding 20% workforce reduction to cut costs. You need to decide how to handle this.",
                options=[
                    {
                        "choice": "Lay off lowest performers",
                        "consequence": "layoff_performance",
                    },
                    {
                        "choice": "Lay off newest employees (LIFO)",
                        "consequence": "layoff_tenure",
                    },
                    {
                        "choice": "Cut everyone's salary by 15%",
                        "consequence": "salary_cuts",
                    },
                    {
                        "choice": "Try to negotiate with the board",
                        "consequence": "negotiate_board",
                    },
                ],
                severity="critical",
            )
        )

    return crises


def apply_crisis_resolution(
    game_state: GameState, crisis: CrisisEvent, choice_idx: int
):
    """Apply the consequences of a crisis resolution"""
    if choice_idx >= len(crisis.options):
        return

    consequence = crisis.options[choice_idx]["consequence"]
    employees = game_state.network.employees

    if consequence == "boost_morale":
        for emp in employees.values():
            delta = EmployeeDelta(
                stress=-10,
                happiness=15,
                health=0,
                greed=0,
                salary=0,
                horniness=0,
                anger=-10,
                productivity=5,
            )
            emp.update(delta)
            emp.mem_short.append("Management listened to our concerns")

    elif consequence == "anger_increase":
        for emp in employees.values():
            delta = EmployeeDelta(
                stress=15,
                happiness=-15,
                health=0,
                greed=0,
                salary=0,
                horniness=0,
                anger=20,
                productivity=-10,
            )
            emp.update(delta)
            emp.mem_short.append("Management ignored our concerns")

    elif consequence == "budget_hit_morale_boost":
        game_state.company.budget -= 50000 * len(employees)
        for emp in employees.values():
            delta = EmployeeDelta(
                stress=-5,
                happiness=10,
                health=0,
                greed=-5,
                salary=2000,
                horniness=0,
                anger=-5,
                productivity=5,
            )
            emp.update(delta)
            emp.mem_short.append("Got a small raise during difficult times")

    elif consequence == "fear_and_resentment":
        # Remove some employees and make others fearful
        employee_ids = list(employees.keys())
        fired_count = min(3, len(employee_ids) // 4)
        fired_ids = random.sample(employee_ids, fired_count)

        for emp_id in fired_ids:
            del employees[emp_id]

        for emp in employees.values():
            delta = EmployeeDelta(
                stress=20,
                happiness=-25,
                health=0,
                greed=10,
                salary=0,
                horniness=0,
                anger=15,
                productivity=-15,
            )
            emp.update(delta)
            emp.mem_short.append("Witnessed colleagues get fired for speaking up")

    elif consequence == "retain_promote":
        target_name = crisis.title.split()[0]
        for emp in employees.values():
            if emp.name.startswith(target_name):
                delta = EmployeeDelta(
                    stress=-10,
                    happiness=30,
                    health=0,
                    greed=-10,
                    salary=20000,
                    horniness=0,
                    anger=-20,
                    productivity=15,
                )
                emp.update(delta)
                emp.mem_short.append("Got promoted after threatening to quit")
                break

    elif consequence == "retain_raise":
        target_name = crisis.title.split()[0]
        for emp in employees.values():
            if emp.name.startswith(target_name):
                delta = EmployeeDelta(
                    stress=-5,
                    happiness=20,
                    health=0,
                    greed=-15,
                    salary=15000,
                    horniness=0,
                    anger=-15,
                    productivity=10,
                )
                emp.update(delta)
                emp.mem_short.append("Got substantial raise after threatening to quit")
                break
        game_state.company.budget -= 15000

    elif consequence == "retain_talk":
        target_name = crisis.title.split()[0]
        for emp in employees.values():
            if emp.name.startswith(target_name):
                delta = EmployeeDelta(
                    stress=-10,
                    happiness=15,
                    health=0,
                    greed=0,
                    salary=0,
                    horniness=0,
                    anger=-10,
                    productivity=5,
                )
                emp.update(delta)
                emp.mem_short.append("Had meaningful conversation with leadership")
                break

    elif consequence == "lose_employee":
        target_name = crisis.title.split()[0]
        for emp_id, emp in list(employees.items()):
            if emp.name.startswith(target_name):
                del employees[emp_id]
                break

        for emp in employees.values():
            delta = EmployeeDelta(
                stress=5,
                happiness=-5,
                health=0,
                greed=5,
                salary=0,
                horniness=0,
                anger=5,
                productivity=-5,
            )
            emp.update(delta)
            emp.mem_short.append("Key colleague quit - management did nothing")

    elif consequence == "mental_health_week":
        for emp in employees.values():
            delta = EmployeeDelta(
                stress=-25,
                happiness=20,
                health=15,
                greed=0,
                salary=0,
                horniness=0,
                anger=-10,
                productivity=10,
            )
            emp.update(delta)
            emp.mem_short.append("Company gave us mental health week")
        game_state.company.budget -= 100000

    elif consequence == "hire_more_staff":
        for emp in employees.values():
            delta = EmployeeDelta(
                stress=-15,
                happiness=10,
                health=0,
                greed=0,
                salary=0,
                horniness=0,
                anger=-5,
                productivity=15,
            )
            emp.update(delta)
            emp.mem_short.append("Company hired more people to help with workload")
        game_state.company.budget -= 200000

    elif consequence == "flexible_work":
        for emp in employees.values():
            delta = EmployeeDelta(
                stress=-10,
                happiness=15,
                health=5,
                greed=0,
                salary=0,
                horniness=0,
                anger=-5,
                productivity=5,
            )
            emp.update(delta)
            emp.mem_short.append("Got flexible work arrangements")

    elif consequence == "ignore_burnout":
        for emp in employees.values():
            delta = EmployeeDelta(
                stress=10,
                happiness=-15,
                health=-10,
                greed=0,
                salary=0,
                horniness=0,
                anger=15,
                productivity=-20,
            )
            emp.update(delta)
            emp.mem_short.append("Management ignored our burnout")

    elif consequence == "layoff_performance":
        employee_list = list(employees.values())
        employee_list.sort(key=lambda e: e.productivity)
        layoff_count = max(1, len(employee_list) // 5)

        for i in range(layoff_count):
            if i < len(employee_list):
                emp = employee_list[i]
                del employees[emp.employee_id]

        for emp in employees.values():
            delta = EmployeeDelta(
                stress=15,
                happiness=-10,
                health=0,
                greed=10,
                salary=0,
                horniness=0,
                anger=10,
                productivity=-5,
            )
            emp.update(delta)
            emp.mem_short.append("Company laid off low performers")

    elif consequence == "layoff_tenure":
        employee_list = list(employees.values())
        employee_list.sort(key=lambda e: e.tenure_months)
        layoff_count = max(1, len(employee_list) // 5)

        for i in range(layoff_count):
            if i < len(employee_list):
                emp = employee_list[i]
                del employees[emp.employee_id]

        for emp in employees.values():
            delta = EmployeeDelta(
                stress=10,
                happiness=-15,
                health=0,
                greed=5,
                salary=0,
                horniness=0,
                anger=15,
                productivity=-10,
            )
            emp.update(delta)
            emp.mem_short.append("Company laid off newest employees")

    elif consequence == "salary_cuts":
        for emp in employees.values():
            cut_amount = int(emp.salary * 0.15)
            delta = EmployeeDelta(
                stress=20,
                happiness=-20,
                health=0,
                greed=15,
                salary=-cut_amount,
                horniness=0,
                anger=20,
                productivity=-15,
            )
            emp.update(delta)
            emp.mem_short.append("Salary cut by 15% due to budget crisis")
        game_state.company.budget += 50000 * len(employees)

    game_state.completed_crises.append(crisis.title)
