import json
import random
from hr_game.engine.game_loop import GameEngine
from hr_game.events.crisis import apply_crisis_resolution


def get_company_setup():
    """Get company setup from user input"""
    print("🏢 Welcome to Corporate Chaos Simulator!")
    print("=" * 50)

    with open("hr_game/creation/companys.json", "r") as f:
        companies = json.load(f)

    print("\nChoose a company or create your own:")
    for i, (name, motto) in enumerate(companies):
        print(f"{i+1}. {name} - '{motto}'")
    print(f"{len(companies)+1}. Create custom company")

    while True:
        try:
            choice = int(input(f"\nChoice (1-{len(companies)+1}): "))
            if 1 <= choice <= len(companies):
                name, motto = companies[choice - 1]
                break
            elif choice == len(companies) + 1:
                name = input("Company name: ")
                motto = input("Company motto: ")
                break
        except ValueError:
            print("Please enter a number.")

    print(f"\nIndustry options:")
    industries = [
        "Technology",
        "Finance",
        "Healthcare",
        "Retail",
        "Manufacturing",
        "Consulting",
    ]
    for i, industry in enumerate(industries):
        print(f"{i+1}. {industry}")

    while True:
        try:
            choice = int(input(f"Choose industry (1-{len(industries)}): "))
            if 1 <= choice <= len(industries):
                industry = industries[choice - 1]
                break
        except ValueError:
            print("Please enter a number.")

    print(f"\nCompany size:")
    sizes = [
        ("startup", "10-15 employees"),
        ("mid", "30-40 employees"),
        ("enterprise", "80+ employees"),
    ]
    for i, (size, desc) in enumerate(sizes):
        print(f"{i+1}. {size.title()} ({desc})")

    while True:
        try:
            choice = int(input(f"Choose size (1-{len(sizes)}): "))
            if 1 <= choice <= len(sizes):
                size = sizes[choice - 1][0]
                break
        except ValueError:
            print("Please enter a number.")

    print(f"\nCompany culture:")
    cultures = ["collaborative", "competitive", "laid_back", "toxic"]
    for i, culture in enumerate(cultures):
        print(f"{i+1}. {culture.title()}")

    while True:
        try:
            choice = int(input(f"Choose culture (1-{len(cultures)}): "))
            if 1 <= choice <= len(cultures):
                culture = cultures[choice - 1]
                break
        except ValueError:
            print("Please enter a number.")

    print(f"\nOrganization structure:")
    structures = ["flat", "hierarchical", "matrix"]
    for i, structure in enumerate(structures):
        print(f"{i+1}. {structure.title()}")

    while True:
        try:
            choice = int(input(f"Choose structure (1-{len(structures)}): "))
            if 1 <= choice <= len(structures):
                org_structure = structures[choice - 1]
                break
        except ValueError:
            print("Please enter a number.")

    return {
        "name": name,
        "motto": motto,
        "industry": industry,
        "size": size,
        "culture": culture,
        "org_structure": org_structure,
    }


def display_daily_summary(game_state, engine):
    """Display daily company status"""
    metrics = engine.get_company_metrics(game_state)

    print(f"\n📅 Day {metrics['day']} at {game_state.company.name}")
    print("=" * 50)
    print(f"👥 Employees: {metrics['employee_count']}")
    print(f"😊 Avg Happiness: {metrics['avg_happiness']:.1f}/100")
    print(f"😰 Avg Stress: {metrics['avg_stress']:.1f}/100")
    print(f"⚡ Avg Productivity: {metrics['avg_productivity']:.1f}/100")
    print(f"💰 Budget: ${metrics['budget']:,}")
    print(f"⚠️  High Risk Employees: {metrics['high_risk_employees']}")

    if game_state.crisis_events:
        print(f"\n🚨 ACTIVE CRISES: {len(game_state.crisis_events)}")


def handle_crisis_events(game_state):
    """Handle any active crisis events"""
    for crisis in game_state.crisis_events[:]:
        print(f"\n🚨 CRISIS: {crisis.title}")
        print("=" * 50)
        print(crisis.description)
        print(f"\n⏰ Time remaining: {crisis.days_remaining} days")
        print("\nYour options:")

        for i, option in enumerate(crisis.options):
            print(f"{i+1}. {option['choice']}")

        while True:
            try:
                choice = int(input(f"\nChoose option (1-{len(crisis.options)}): "))
                if 1 <= choice <= len(crisis.options):
                    apply_crisis_resolution(game_state, crisis, choice - 1)
                    print(f"\n✅ Decision made: {crisis.options[choice-1]['choice']}")
                    game_state.crisis_events.remove(crisis)
                    break
            except ValueError:
                print("Please enter a number.")


def list_employees(game_state):
    """List all employees with key stats"""
    employees = list(game_state.network.employees.values())

    print("\n👥 Employee Roster:")
    print("=" * 80)
    print(
        f"{'Name':<15} {'Dept':<12} {'Role':<10} {'Level':<5} {'Happy':<6} {'Stress':<7} {'Anger':<6}"
    )
    print("-" * 80)

    for emp in employees:
        print(
            f"{emp.name:<15} {emp.department:<12} {emp.role:<10} {emp.level:<5} {emp.happiness:<6} {emp.stress:<7} {emp.anger:<6}"
        )


def employee_interaction_menu(game_state, engine):
    """Handle employee interactions"""
    employees = list(game_state.network.employees.values())

    print("\n🗣️  Employee Interactions:")
    print("1. List all employees")
    print("2. Talk to specific employee")
    print("3. Take action on employee")
    print("4. Back to main menu")

    choice = input("\nChoice: ")

    if choice == "1":
        list_employees(game_state)
        return True

    elif choice == "2":
        print("\nChoose employee to talk to:")
        for i, emp in enumerate(employees):
            print(f"{i+1}. {emp.name} ({emp.department}, {emp.role})")

        try:
            emp_choice = int(input(f"\nEmployee (1-{len(employees)}): "))
            if 1 <= emp_choice <= len(employees):
                employee = employees[emp_choice - 1]

                print(f"\n💬 Talking to {employee.name}")
                print(f"Background: {employee.backstory}")
                print(f"Values: {', '.join(employee.values)}")
                print(
                    f"Recent: {', '.join(employee.mem_short[-2:]) if employee.mem_short else 'Nothing notable'}"
                )

                user_message = input(f"\nWhat do you want to say to {employee.name}? ")
                response = engine.conduct_employee_meeting(employee, user_message)
                print(f"\n{employee.name}: {response}")
        except ValueError:
            print("Invalid choice.")
        return True

    elif choice == "3":
        print("\nChoose employee for action:")
        for i, emp in enumerate(employees):
            risk = "⚠️ " if emp.happiness < 30 and emp.anger > 60 else ""
            print(
                f"{i+1}. {risk}{emp.name} ({emp.department}, happiness: {emp.happiness}, stress: {emp.stress})"
            )

        try:
            emp_choice = int(input(f"\nEmployee (1-{len(employees)}): "))
            if 1 <= emp_choice <= len(employees):
                employee = employees[emp_choice - 1]

                print(f"\nActions for {employee.name}:")
                print("1. Promote")
                print("2. Give raise")
                print("3. Reprimand")
                print("4. Give PTO")
                print("5. Fire")
                print("6. Cancel")

                action_choice = input("\nAction: ")
                actions = {
                    "1": "promote",
                    "2": "give_raise",
                    "3": "reprimand",
                    "4": "give_pto",
                    "5": "fire",
                }

                if action_choice in actions:
                    if action_choice == "5":
                        confirm = input(
                            f"Are you sure you want to fire {employee.name}? (yes/no): "
                        )
                        if confirm.lower() != "yes":
                            print("Action cancelled.")
                            return True

                    result = engine.apply_user_action(
                        game_state, actions[action_choice], employee.employee_id
                    )
                    print(f"\n✅ {result}")
        except ValueError:
            print("Invalid choice.")
        return True

    elif choice == "4":
        return False

    return True


def main():
    print("🎮 Starting Corporate Chaos Simulator...")

    setup = get_company_setup()
    engine = GameEngine()
    game_state = engine.create_company_from_setup(setup)

    print(f"\n🎉 Welcome to {game_state.company.name}!")
    print(f"Motto: '{game_state.company.motto}'")
    print(
        f"You are the CEO/HR Director. Your job is to keep the company running and employees happy."
    )
    print(f"Good luck! 🍀")

    while not game_state.game_over:
        display_daily_summary(game_state, engine)

        if game_state.crisis_events:
            handle_crisis_events(game_state)
            continue

        print(f"\n🎯 Daily Actions:")
        print("1. Employee interactions")
        print("2. Advance to next day")
        print("3. View detailed employee list")
        print("4. Quit game")

        choice = input("\nWhat would you like to do? ")

        if choice == "1":
            in_employee_menu = True
            while in_employee_menu:
                in_employee_menu = employee_interaction_menu(game_state, engine)

        elif choice == "2":
            print("\n⏰ Advancing to next day...")
            game_state = engine.step_day(game_state)

            if game_state.day % 7 == 0:
                print(f"\n📊 Weekly Report (Day {game_state.day}):")
                metrics = engine.get_company_metrics(game_state)
                if metrics["avg_happiness"] > 70:
                    print("🎉 Morale is excellent!")
                elif metrics["avg_happiness"] > 50:
                    print("😊 Employees seem content.")
                elif metrics["avg_happiness"] > 30:
                    print("😐 Some employees are struggling.")
                else:
                    print("😞 Company morale is very low.")

        elif choice == "3":
            list_employees(game_state)

        elif choice == "4":
            print("Thanks for playing! 👋")
            break

        else:
            print("Invalid choice. Please try again.")

    if game_state.game_over:
        print(f"\n💀 GAME OVER!")
        print(f"Reason: {game_state.game_over_reason}")
        print(f"You lasted {game_state.day} days as CEO of {game_state.company.name}")

        metrics = engine.get_company_metrics(game_state)
        if not "error" in metrics:
            print(f"Final stats:")
            print(f"- Employees remaining: {metrics['employee_count']}")
            print(f"- Final morale: {metrics['avg_happiness']:.1f}/100")
            print(f"- Budget remaining: ${metrics['budget']:,}")


if __name__ == "__main__":
    main()
