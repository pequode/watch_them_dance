import random
from typing import Optional

from hr_game.data.employee import Employee, EmployeeNetwork, EmployeeRelationship
def randomize_relationship(seed:Optional[int]=None)->EmployeeRelationship:
    if seed is not None:
        random.seed(seed)
    return EmployeeRelationship(attraction=random.random(),
                                resentment=random.random(),
                                synergy=random.random(),
                                friendship=random.random(),
                                )
    

def create_fully_connected_network(employees:list[Employee],seed:Optional[int]=None)->EmployeeNetwork:
    nodes = {}
    edges = []
    for i in employees:
        nodes[i.employee_id] = i
        for j in employees:
            if j.employee_id in nodes: # filters out both self and already initialized edges. 
                continue 
            edges.append((i.employee_id,j.employee_id,randomize_relationship(seed)))
    return EmployeeNetwork(employees=nodes,relationships=edges)