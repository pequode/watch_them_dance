# so in our simulated game the employees interact with each other 
# on each step an employee interacts with every other employee. 
# they interact via Relationship events
# Relationship events look at a an employee stats and the relationship 
# stats of the employee network and then give a pdf for an update that we then sample from with a random var 
# these samples return employee deltas and relationship deltas and we store these delta with the employee. 
# for efficiency we pack the Null deltas with their count number. 

import random
from hr_game.creation.employee import randomize_employee
from hr_game.creation.network import create_fully_connected_network
from hr_game.data.employee import Employee, EmployeeNetwork, EmployeeRelationship
from hr_game.events.base import EmployeeEffectingEvent, EmployeeEvent, EmployeeRelationshipEvent
from hr_game.events.example import EMPLOYEE_EFFECTING_EVENT_BUS, EMPLOYEE_EVENT_BUS, EMPLOYEE_RELATIONSHIP_EVENT_BUS, null_delta_factory, null_relationship_delta_factory


def employee_update(employee:Employee,verbose:bool,events:list[EmployeeEvent]):
    null_delta = null_delta_factory()
    sampled_events = random.sample(events,int(len(events)*0.8)) # only pick from 4/5 of events each cycle. 
    for i in sampled_events:
        random_var = random.random()
        delta = i.pdf(employee,random_var=random_var)
        employee.update(delta)
        if null_delta == delta: 
            continue 
        if verbose:
            print("--",i.description(delta))
    return employee
def simulate_employee(employee:Employee,cycles:int,verbose:bool,events:list[EmployeeEvent])->Employee:
    employee_copy = employee.model_copy()
    for i in range(cycles):
        if verbose and i%10 ==0:
            print("It is now day:",i, "and this is the employee\n",str(employee_copy))
        employee_update(employee_copy,verbose,events=events)

    
def relationship_update(e:Employee,e2:Employee,relationship:EmployeeRelationship,verbose:bool,events:list[EmployeeRelationshipEvent])->EmployeeRelationship:
    nr = relationship.model_copy()
    sampled_events = random.sample(events,int(len(events)*0.8)) # only pick from 4/5 of events each cycle. 
    null_delta = null_relationship_delta_factory()
    for i in sampled_events:
        random_var = random.random()
        delta = i.pdf((nr,e,e2),random_var=random_var)
        nr.update(delta)
        if null_delta == delta: 
            continue 
        if verbose:
            print(f"the relationship between {e.name} and {e2.name} changed--",i.description(delta))
    return nr
     
def employee_updates_from_rel(employee:Employee,relationship:EmployeeRelationship,verbose:bool,events:list[EmployeeEffectingEvent])->Employee:
    ne = employee.model_copy()
    sampled_events = random.sample(events,int(len(events)*0.8)) # only pick from 4/5 of events each cycle. 
    null_delta = null_delta_factory()
    for i in sampled_events:
        random_var = random.random()
        delta = i.pdf((relationship,ne),random_var=random_var)
        ne.update(delta)
        if null_delta == delta: 
            continue 
        if verbose:
            print("--",i.description(delta))
    return ne
def simulate_office(
        office_network:EmployeeNetwork,
        cycles:int,
        verbose:bool,
        employee_events:list[EmployeeEvent],
        relationship_events:list[EmployeeRelationshipEvent],
        relation_ship_update_event:list[EmployeeEffectingEvent]
    )->EmployeeNetwork:
    for i in range(cycles):
        should_print = verbose and i%10 ==0
        if should_print:
            print("It is now day:",i)
        # update relationships first. 
        for ridx in range(len(office_network.relationships)):
            eid1,eid2,rel = office_network.relationships[ridx]
            emp1 = office_network.employees[eid1]
            emp2 = office_network.employees[eid2]
            new_rel = relationship_update(emp1,emp2,rel,should_print,relationship_events)
            office_network.relationships[ridx] = eid1,eid2,new_rel
        # then update employees. 
        for e in list(office_network.employees.keys()):
            old_employee = office_network.employees[e]
            if should_print:
                print(f"\nUpdating Events for :{old_employee.name}\n")
            ne = employee_update(old_employee,should_print,events=employee_events)
            office_network.employees[e] = ne 
        # finally trigger relationship affecting changes. 
        for e in list(office_network.employees.keys()):
            old_employee = office_network.employees[e]
            for relation_ship in office_network.relationships:
                e1,e2,r = relation_ship
                if e==e1 or e==e2:
                    old_employee = employee_updates_from_rel(old_employee,r,should_print,relation_ship_update_event)
            office_network.employees[e]=old_employee

simulate_employee(randomize_employee(),100,events=EMPLOYEE_EVENT_BUS,verbose=True)
simulate_office(
    office_network=create_fully_connected_network([randomize_employee() for i in range(10)]),
    cycles=100,
    verbose=True, 
    employee_events=EMPLOYEE_EVENT_BUS,
    relation_ship_update_event=EMPLOYEE_EFFECTING_EVENT_BUS,
    relationship_events=EMPLOYEE_RELATIONSHIP_EVENT_BUS
    )