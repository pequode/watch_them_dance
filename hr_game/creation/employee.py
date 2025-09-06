from pathlib import Path
import random
import string
from typing import Optional

from hr_game.data.employee import Employee
def read_employee_names(path:Path=Path(__file__).parent/"employee_names.txt")->list[str]:
   with open(path,"r") as fp:
      lines = fp.readlines()
   return lines 
def randomize_employee(seed:int =None)->Employee:
  names = ["Alice","Bob","Cthulhu","Deamon","Erebus","Faust","Hanbi","Jesabell","Kroni","Lilly","Matteo"] + read_employee_names()
  letters = string.ascii_lowercase
  if seed is not None:
    random.seed(seed)
  first_name = random.choice(names).capitalize().strip()
  last_letter = random.choice(letters).upper()
  return Employee(
     name=f"{first_name} {last_letter}.",
     age=random.randint(18,65),
     stress=random.randint(10,80),
     greed=random.randint(10,50),
     salary=random.randint(50_000,1_500_000),
     anger=random.randint(10,50),
     horniness=random.randint(10,50),
     happiness=random.randint(10,50),
     productivity=random.randint(10,50),
     health=random.randint(50,100),
    )


### random utility 
def randomly_sub_select_unique_from_file(file_path:Path,k_lines:int,seed:Optional[int]=None)->list[str]:
    if seed is not None: 
       random.seed(int(seed))
    with open(file_path) as fp:
        lines = fp.readlines()
    total_len = len(lines)
    if k_lines*2>total_len:
       raise Exception("This method will not work")
    if len(lines) != len(set(lines)):
       raise Exception("The lines must be unique.")
    for i in range(100):
       sub_lines = random.choices(lines,k=k_lines)
       if len(set(sub_lines)) == k_lines:
          return sub_lines
def sampled_and_create_a_file(in_file_path:Path,out_file_path:Path,k_lines:int,seed:Optional[int]=None):
   lines = randomly_sub_select_unique_from_file(in_file_path,k_lines,seed)
   lines.sort()
   with open(out_file_path,"w") as fp:
      fp.writelines(lines)
