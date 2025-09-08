# lets do some employee events:
from hr_game.data.employee import (
    Employee,
    EmployeeDelta,
    EmployeeRelationship,
    EmployeeRelationshipDelta,
)
from hr_game.events.base import (
    EmployeeEffectingEvent,
    EmployeeEvent,
    EmployeeRelationshipEvent,
)


def null_delta_factory() -> EmployeeDelta:
    return EmployeeDelta(
        stress=0,
        happiness=0,
        health=-10,
        greed=20,
        salary=0,
        horniness=-50,
        anger=0,
        productivity=0,
    )


def null_relationship_delta_factory() -> EmployeeRelationshipDelta:
    return EmployeeRelationshipDelta(
        attraction=1,
        resentment=1,
        synergy=1,
        friendship=1,
    )


class HasABaby(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        if prior.horniness > 50 and 40 > prior.age > 10 and random_var > 0.5:
            return EmployeeDelta(
                stress=10,
                happiness=20,
                health=-10,
                greed=20,
                salary=0,
                horniness=-50,
                anger=0,
                productivity=-10,
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "They had a kid! Its looks just like them."


class BadDayAtWork(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        if random_var > 0.8:
            return EmployeeDelta(
                stress=10,
                happiness=-10,
                health=0,
                greed=0,
                salary=0,
                horniness=10,
                anger=10,
                productivity=-5,
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "Ugh today sucked."


class GoodDayAtWork(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        if random_var > 0.8:
            return EmployeeDelta(
                stress=-10,
                happiness=10,
                health=0,
                greed=0,
                salary=0,
                horniness=-10,
                anger=-10,
                productivity=0,
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "Ugh today rocked!."


### gpt contributed
class CoffeeBreak(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        # If already very stressed, coffee helps more
        stress_relief = min(10, prior.stress // 2)
        if random_var > 0.3:
            return EmployeeDelta(
                stress=-stress_relief,
                happiness=5,
                health=0,
                greed=0,
                salary=0,
                horniness=0,
                anger=0,
                productivity=5,
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "They took a coffee break and feel a bit better."


class OfficeGossip(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        # Gossip affects angry employees more
        anger_increase = 5 + prior.anger // 10
        happiness_loss = 2 + prior.happiness // 20
        if random_var > 0.6:
            return EmployeeDelta(
                stress=2,
                happiness=-happiness_loss,
                health=0,
                greed=0,
                salary=0,
                horniness=0,
                anger=anger_increase,
                productivity=0,
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "They got caught up in office gossip. Drama everywhere!"


class Promotion(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        # If very greedy, promotion feels better
        happiness_boost = 20 + prior.greed // 5
        stress_increase = 5 + prior.stress // 10
        if random_var > 0.9:
            return EmployeeDelta(
                stress=stress_increase,
                happiness=happiness_boost,
                health=0,
                greed=-10,
                salary=20_000,
                horniness=0,
                anger=0,
                productivity=10,
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "Congratulations! They got promoted and their salary increased."


class MissedDeadline(EmployeeEvent):
    @staticmethod
    def pdf(prior: Employee, random_var: float) -> EmployeeDelta:
        # If already stressed, missing a deadline is worse
        stress_increase = 10 + prior.stress // 5
        happiness_loss = 10 + prior.happiness // 10
        if random_var > 0.5:
            return EmployeeDelta(
                stress=stress_increase,
                happiness=-happiness_loss,
                health=-5,
                greed=0,
                salary=0,
                horniness=0,
                anger=10,
                productivity=-10,
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "They missed a deadline and feel awful."


# create event for network.


class EnteringFlowState(EmployeeEffectingEvent):
    @staticmethod
    def pdf(
        prior: tuple[EmployeeRelationship, Employee], random_var: float
    ) -> EmployeeDelta:
        relationship, employee = prior
        productivity_increase = int(1 + relationship.synergy) * 10
        stress_decrease = -int((relationship.synergy) * employee.stress / 100)
        return EmployeeDelta(
            stress=stress_decrease,
            greed=0,
            salary=0,
            anger=0,
            happiness=0,
            health=0,
            horniness=0,
            productivity=productivity_increase,
        )

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        pick = ""
        val = result.productivity
        if val > 15:
            pick = "super productive."
        elif val > 10:
            pick = "somewhat productive."
        elif val > 5:
            pick = "disappointingly productive"
        else:
            pick = "unproductive"
        return f"Entered a {pick} flow state!"


class PickAFight(EmployeeEffectingEvent):
    @staticmethod
    def pdf(
        prior: tuple[EmployeeRelationship, Employee], random_var: float
    ) -> EmployeeDelta:
        relationship, employee = prior
        if relationship.resentment * employee.anger > 100 * random_var:
            return EmployeeDelta(
                stress=10,
                greed=0,
                salary=0,
                anger=5,
                happiness=-10,
                health=0,
                horniness=0,
                productivity=-5,
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "They picked a fight with a co-worker. Not good for their heart."


class HaveAnAffair(EmployeeEffectingEvent):
    @staticmethod
    def pdf(
        prior: tuple[EmployeeRelationship, Employee], random_var: float
    ) -> EmployeeDelta:
        relationship, employee = prior
        if employee.horniness * (1 + relationship.attraction) > (100 * random_var):
            return EmployeeDelta(
                stress=10,
                greed=0,
                salary=0,
                anger=10,
                happiness=-20,
                health=0,
                horniness=-5,
                productivity=-10,
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "They are ruining their life. They decided to have an affair but left their location on. Their partner is suspicious."


class PlaySomeGolf(EmployeeEffectingEvent):
    @staticmethod
    def pdf(
        prior: tuple[EmployeeRelationship, Employee], random_var: float
    ) -> EmployeeDelta:
        relationship, employee = prior
        if relationship.friendship > random_var:
            return EmployeeDelta(
                stress=-10,
                greed=0,
                salary=int(10_000 * random_var),
                anger=-10,
                happiness=10,
                health=0,
                horniness=-5,
                productivity=5,
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "Played a round of golf. Woah! This is really good for their career!"


class SecretRivalry(EmployeeEffectingEvent):
    @staticmethod
    def pdf(
        prior: tuple[EmployeeRelationship, Employee], random_var: float
    ) -> EmployeeDelta:
        relationship, employee = prior
        if (
            relationship.resentment > random_var
            and relationship.friendship < random_var
            and employee.stress < 80
        ):
            return EmployeeDelta(
                stress=10,
                greed=10,
                salary=0,
                anger=5,
                happiness=-5,
                health=0,
                horniness=-5,
                productivity=10,
            )
        return null_delta_factory()

    @staticmethod
    def description(result: EmployeeDelta) -> str:
        return "They started a one sided rivalry with a co-worker. Just you wait..."


## relationship effecting events
class RomanticLunch(EmployeeRelationshipEvent):
    @staticmethod
    def pdf(
        prior: tuple[EmployeeRelationship, Employee, Employee], random_var: float
    ) -> EmployeeRelationshipDelta:
        relationship, employee1, employee2 = prior
        return EmployeeRelationshipDelta(
            attraction=(float(relationship.attraction > 0.5) + 0.5)
            * (employee1.horniness + employee2.horniness)
            / 100,
            resentment=0.75,
            synergy=1,
            friendship=1.25,
        )

    @staticmethod
    def description(result: EmployeeRelationshipDelta) -> str:
        if result.attraction > 0.5:
            return "Things are getting complicated between these two..."
        return "Some people can just be platonic."


class OverheadGossip(EmployeeRelationshipEvent):
    @staticmethod
    def pdf(
        prior: tuple[EmployeeRelationship, Employee, Employee], random_var: float
    ) -> EmployeeRelationshipDelta:
        relationship, employee1, employee2 = prior
        return EmployeeRelationshipDelta(
            attraction=1,
            resentment=0.75,
            synergy=1,
            friendship=1,
        )

    @staticmethod
    def description(result: EmployeeRelationshipDelta) -> str:
        return "They overheard someone talking about them..."


class BrainstormingSession(EmployeeRelationshipEvent):
    @staticmethod
    def pdf(
        prior: tuple[EmployeeRelationship, Employee, Employee], random_var: float
    ) -> EmployeeRelationshipDelta:
        relationship, e1, e2 = prior
        if (
            relationship.synergy > 0.5 and (e1.stress + e2.stress) < 100
        ) and random_var > 0.3:
            return EmployeeRelationshipDelta(
                attraction=1, resentment=-0.5, synergy=1.5, friendship=1.2
            )
        else:
            return EmployeeRelationshipDelta(
                attraction=1, resentment=1.0, synergy=0.8, friendship=0.9
            )

    @staticmethod
    def description(result: EmployeeRelationshipDelta) -> str:
        if result.synergy > 1:
            return "The brainstorming session sparked some great ideas!"
        return "The brainstorming session went nowhere and tensions rose."


class RiskyJoke(EmployeeRelationshipEvent):
    @staticmethod
    def pdf(
        prior: tuple[EmployeeRelationship, Employee, Employee], random_var: float
    ) -> EmployeeRelationshipDelta:
        relationship, e1, e2 = prior
        if relationship.friendship > relationship.resentment and random_var > 0.4:
            return EmployeeRelationshipDelta(
                attraction=1, resentment=0.5, synergy=1.5, friendship=1.5
            )
        else:
            return EmployeeRelationshipDelta(
                attraction=0.75, resentment=1.5, synergy=0.8, friendship=0.8
            )

    @staticmethod
    def description(result: EmployeeRelationshipDelta) -> str:
        if result.friendship > 1:
            return "The risky joke landed perfectly — everyone laughed!"
        return "The risky joke fell flat and created awkward tension."


EMPLOYEE_EVENT_BUS = [
    HasABaby(),
    GoodDayAtWork(),
    BadDayAtWork(),
    CoffeeBreak(),
    OfficeGossip(),
    MissedDeadline(),
    Promotion(),
    MissedDeadline(),
]
EMPLOYEE_EFFECTING_EVENT_BUS = [
    EnteringFlowState(),
    PickAFight(),
    HaveAnAffair(),
    PlaySomeGolf(),
    SecretRivalry(),
]
EMPLOYEE_RELATIONSHIP_EVENT_BUS = [
    RomanticLunch(),
    OverheadGossip(),
    BrainstormingSession(),
    RiskyJoke(),
]
