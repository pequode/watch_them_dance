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
    

def create_fully_connected_network(seed:Optional[int],employees:list[Employee])->EmployeeNetwork:
    nodes = {i.employee_id:i for i in employees}
    edges = []
    for i in employees:
        for j in employees:
            if i.employee_id==j.employee_id:
                continue
            edges.append()
    pass 