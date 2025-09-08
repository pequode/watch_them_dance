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
    base_employee.skills = skills
    base_employee.tenure_months = random.randint(1, 36)

    return base_employee


def generate_employees_batch_llm(
    company: Company, employee_list: list[Employee], llm
) -> list[Employee]:
    """Generate backstories, values, and goals for a batch of employees with a single LLM call"""

    if not employee_list:
        return employee_list

    try:
        batch_prompt = f"""Create employee profiles for {company.name} ({company.industry} company with {company.culture} culture).

For each employee below, provide:
1. A brief 2-3 sentence backstory
2. 2-3 core values (comma-separated)  
3. 2-3 current goals (comma-separated)

Format your response exactly like this:

EMPLOYEE 1:
Backstory: [backstory here]
Values: value1, value2, value3
Goals: goal1, goal2, goal3

EMPLOYEE 2:
Backstory: [backstory here]
Values: value1, value2, value3
Goals: goal1, goal2, goal3

Here are the employees:

"""

        for i, emp in enumerate(employee_list, 1):
            roles = {
                "L1": "Junior",
                "L2": "Mid-level",
                "L3": "Senior",
                "L4": "Staff",
                "L5": "Principal",
            }
            role_desc = roles.get(emp.level, "Mid-level")

            batch_prompt += f"""EMPLOYEE {i}:
- Name: {emp.name}
- Age: {emp.age}
- Role: {role_desc} {emp.role} in {emp.department}
- Personality: stress={emp.stress}, happiness={emp.happiness}, greed={emp.greed}

"""

        response = llm.invoke(batch_prompt).content.strip()

        # Parse the response
        employee_blocks = []
        current_block = []

        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("EMPLOYEE ") and current_block:
                employee_blocks.append("\n".join(current_block))
                current_block = []
            if line:
                current_block.append(line)

        if current_block:
            employee_blocks.append("\n".join(current_block))

        # Apply parsed data to employees
        for i, (emp, block) in enumerate(zip(employee_list, employee_blocks)):
            backstory = ""
            values = ["teamwork", "growth"]
            goals = ["do good work", "advance career"]

            try:
                lines = block.split("\n")
                for line in lines:
                    if line.startswith("Backstory:"):
                        backstory = line[10:].strip()
                    elif line.startswith("Values:"):
                        values_text = line[7:].strip()
                        values = [v.strip() for v in values_text.split(",")][:3]
                    elif line.startswith("Goals:"):
                        goals_text = line[6:].strip()
                        goals = [g.strip() for g in goals_text.split(",")][:3]

                if not backstory:
                    backstory = f"A {emp.level} {emp.role} in {emp.department} who joined {company.name} recently."

            except Exception:
                backstory = f"A {emp.level} {emp.role} in {emp.department} who joined {company.name} recently."

            emp.backstory = backstory
            emp.values = values
            emp.goals = goals

    except Exception:
        # Fallback to simple backstories if LLM call fails
        for emp in employee_list:
            emp.backstory = f"A {emp.level} {emp.role} in {emp.department} who joined {company.name} recently."
            emp.values = ["teamwork", "growth"]
            emp.goals = ["do good work", "advance career"]

    return employee_list


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
