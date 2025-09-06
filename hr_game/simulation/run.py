# so in our simulated game the employees interact with each other 
# on each step an employee interacts with every other employee. 
# they interact via Relationship events
# Relationship events look at a an employee stats and the relationship 
# stats of the employee network and then give a pdf for an update that we then sample from with a random var 
# these samples return employee deltas and relationship deltas and we store these delta with the employee. 
# for efficiency we pack the Null deltas with their count number. 

import random
from hr_game.creation.employee import randomize_employee
from hr_game.data.employee import Employee
from hr_game.events.base import EmployeeEvent
from hr_game.events.example import EMPLOYEE_EVENT_BUS, null_delta_factory


def simulate_employee(employee:Employee,cycles:int,verbose:True,events:list[EmployeeEvent])->Employee:
    null_delta = null_delta_factory()
    for i in range(cycles):
        if verbose and i%10 ==0:
            print("It is now day:",i, "and this is the employee\n",str(employee))
        sampled_events = random.sample(events,int(len(events)*0.8)) # only pick from 4/5 of events each cycle. 
        for i in sampled_events:
            random_var = random.random()
            delta = i.pdf(employee,random_var=random_var)
            employee.update(delta)
            if null_delta == delta: 
                continue 
            if verbose:
                print("--",i.description(delta))
    
simulate_employee(randomize_employee(),100,events=EMPLOYEE_EVENT_BUS,verbose=True)