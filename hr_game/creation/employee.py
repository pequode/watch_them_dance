from pathlib import Path
import random
import string
from typing import Optional

from hr_game.data.employee import Employee
from hr_game.data.company import Company


def read_employee_names(
    path: Path = Path(__file__).parent / "employee_names.txt",
) -> list[str]:
    with open(path, "r") as fp:
        lines = fp.readlines()
    return lines


def randomize_employee(seed: int = None) -> Employee:
    names = [
        "Alice",
        "Bob",
        "Cthulhu",
        "Deamon",
        "Erebus",
        "Faust",
        "Hanbi",
        "Jesabell",
        "Kroni",
        "Lilly",
        "Matteo",
    ] + read_employee_names()
    letters = string.ascii_lowercase
    if seed is not None:
        random.seed(seed)
    first_name = random.choice(names).capitalize().strip()
    last_letter = random.choice(letters).upper()
    return Employee(
        name=f"{first_name} {last_letter}.",
        age=random.randint(18, 65),
        stress=random.randint(10, 80),
        greed=random.randint(10, 50),
        salary=random.randint(50_000, 1_500_000),
        anger=random.randint(10, 50),
        horniness=random.randint(10, 50),
        happiness=random.randint(10, 50),
        productivity=random.randint(10, 50),
        health=random.randint(50, 100),
    )


def generate_employee_for_company(
    company: Company, role: str, department: str, level: str, llm, seed: int = None
) -> Employee:
    base_employee = randomize_employee(seed)

    departments = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"]
    if department not in departments:
        department = random.choice(departments)

    levels = ["L1", "L2", "L3", "L4", "L5"]
    if level not in levels:
        level = random.choice(levels)

    roles = {
        "L1": "Junior",
        "L2": "Mid-level",
        "L3": "Senior",
        "L4": "Staff",
        "L5": "Principal",
    }

    base_salary = {
        "Engineering": {
            "L1": 85000,
            "L2": 120000,
            "L3": 160000,
            "L4": 220000,
            "L5": 300000,
        },
        "Sales": {"L1": 55000, "L2": 75000, "L3": 110000, "L4": 150000, "L5": 200000},
        "Marketing": {
            "L1": 60000,
            "L2": 80000,
            "L3": 120000,
            "L4": 160000,
            "L5": 220000,
        },
        "HR": {"L1": 50000, "L2": 70000, "L3": 100000, "L4": 140000, "L5": 180000},
        "Finance": {"L1": 65000, "L2": 90000, "L3": 130000, "L4": 180000, "L5": 250000},
        "Operations": {
            "L1": 55000,
            "L2": 75000,
            "L3": 110000,
            "L4": 150000,
            "L5": 200000,
        },
    }

    salary = base_salary.get(department, base_salary["Engineering"]).get(level, 80000)
    salary += random.randint(-10000, 15000)

    try:
        backstory_prompt = f"""Create a brief 2-3 sentence backstory for an employee at {company.name} ({company.industry} company with {company.culture} culture). 

Employee details:
- Name: {base_employee.name}
- Age: {base_employee.age}
- Role: {roles[level]} {role} in {department}
- Personality hints: stress={base_employee.stress}, happiness={base_employee.happiness}, greed={base_employee.greed}

Write a concise, realistic backstory that explains their background and current situation."""

        backstory = llm.invoke(backstory_prompt).content.strip()

        values_prompt = f"""Based on this employee: {backstory}
List 2-3 core values that drive their decisions (like 'work-life balance', 'career growth', 'financial security', 'creativity', 'teamwork'). 
Respond with just a comma-separated list."""

        values_text = llm.invoke(values_prompt).content.strip()
        values = [v.strip() for v in values_text.split(",")][:3]

        goals_prompt = f"""Based on this employee: {backstory}
List 2-3 current goals they might have (like 'get promoted', 'learn new skills', 'buy a house', 'find work-life balance').
Respond with just a comma-separated list."""

        goals_text = llm.invoke(goals_prompt).content.strip()
        goals = [g.strip() for g in goals_text.split(",")][:3]

    except Exception:
        backstory = (
            f"A {level} {role} in {department} who joined {company.name} recently."
        )
        values = ["teamwork", "growth"]
        goals = ["do good work", "advance career"]

    skills = {}
    if department == "Engineering":
        skills = {
            "python": random.randint(30, 90),
            "communication": random.randint(20, 80),
            "problem_solving": random.randint(40, 90),
        }
    elif department == "Sales":
        skills = {
            "communication": random.randint(50, 95),
            "negotiation": random.randint(40, 90),
            "customer_relations": random.randint(45, 90),
        }
    elif department == "Marketing":
        skills = {
            "creativity": random.randint(40, 90),
            "communication": random.randint(40, 85),
            "analytics": random.randint(30, 80),
        }
    else:
        skills = {
            "communication": random.randint(30, 80),
            "organization": random.randint(35, 85),
            "analysis": random.randint(25, 75),
        }

    base_employee.role = role
    base_employee.department = department
    base_employee.level = level
    base_employee.salary = salary
    base_employee.backstory = backstory
    base_employee.values = values
    base_employee.goals = goals
    base_employee.skills = skills
    base_employee.tenure_months = random.randint(1, 36)

    return base_employee


### random utility
def randomly_sub_select_unique_from_file(
    file_path: Path, k_lines: int, seed: Optional[int] = None
) -> list[str]:
    if seed is not None:
        random.seed(int(seed))
    with open(file_path) as fp:
        lines = fp.readlines()
    total_len = len(lines)
    if k_lines * 2 > total_len:
        raise Exception("This method will not work")
    if len(lines) != len(set(lines)):
        raise Exception("The lines must be unique.")
    for i in range(100):
        sub_lines = random.choices(lines, k=k_lines)
        if len(set(sub_lines)) == k_lines:
            return sub_lines


def sampled_and_create_a_file(
    in_file_path: Path, out_file_path: Path, k_lines: int, seed: Optional[int] = None
):
    lines = randomly_sub_select_unique_from_file(in_file_path, k_lines, seed)
    lines.sort()
    with open(out_file_path, "w") as fp:
        fp.writelines(lines)
