import asyncio
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from typing import Optional
from hr_game.creation.employee import randomize_employee
from hr_game.data.employee import Employee, bound
from hr_game.llm.utils import get_llm
import numpy as np 
import faiss

def describe_employee(employee:Employee):
    lines = [f"{employee.name}:"]
    for field_name, field_info in Employee.model_fields.items():
        if field_name == "name":
            continue
        # Get the field description if available
        description = field_info.description or "No description"
        value = getattr(employee, field_name)
        lines.append(f"    {field_name} ({description}): {value}")
    return "\n".join(lines)

def generate_prompts(employee:Employee,setting:str)->str:
    employee_description = describe_employee(employee)
    prompt = f"""
    You are role playing as an employee.
    They have a question for HR.
    They work in a {setting}. 
    Please as a random question as the employee. 
    Here is some context about them:
    {employee_description}.
    Please ask a random question but flavor it with the employee state and workplace. 
    Dont say your own name. 
    Dont refer to your stats directly simply infer mood based on their values. 
    Modulate politeness based on stress and anger. Dont be afraid to curse if the situation is to dire. 
    If stress or anger is higher than 80 add an insult or blaming to the person they are talking to. 
    If your desperate speak desperately. If your happy be conversational.
    Dont say HR. Use ambigious pronouns for the person you are talking to.
    Dont say the setting you are working in. 
    """
    return prompt

def get_employee_fields() -> list[str]:
    return list(filter(lambda x: x not in ["name", "context_history", "traits"], Employee.model_fields))

def employee_to_vector(emp: Employee) -> np.ndarray:
    """
    Convert Employee attributes into a numeric vector for FAISS.
    Only include numeric fields that you want similarity on.
    """
    fields = get_employee_fields()
    attrs = [getattr(emp, i)/ (bound(getattr(emp, i),10_000_000,1_000_000)if i=="salary" else 100) for i in fields]
    return np.array(attrs, dtype='float32')


class EmployeeVectorAndMetadataStore:
    def __init__(self, faiss_location: str, md_db_location: str):
        self.faiss_location = faiss_location
        self.md_db_location = md_db_location
        self._create_table()

    def _create_table(self):
        with self.sql_lite as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                idx INTEGER PRIMARY KEY,
                metadata TEXT NOT NULL
            )
            """)
            conn.commit()

    @property
    def sql_lite(self):
        return sqlite3.connect(self.md_db_location)

    @property
    def index(self):
        if not Path(self.faiss_location).exists():
            self._create_index()
        return faiss.read_index(self.faiss_location)

    def _create_index(self):
        d = len(get_employee_fields())
        base_index = faiss.IndexFlatL2(d)
        index = faiss.IndexIDMap(base_index)
        Path(self.faiss_location).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, self.faiss_location)

    def _save_index(self, index):
        faiss.write_index(index, self.faiss_location)

    def set(self, employee: Employee, question: str) -> int:
        metadata = {"question": question, "employee": employee.model_dump()}
        with self.sql_lite as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO metadata (metadata) VALUES (?)", (json.dumps(metadata),))
            conn.commit()
            new_id = cursor.lastrowid

        index = self.index
        index.add_with_ids(
            np.array([employee_to_vector(employee)], dtype=np.float32),
            np.array([new_id], dtype=np.int64)
        )
        self._save_index(index)
        return new_id

    def batch_set(self, employees: list[Employee],questions:list[str]) -> list[int]:
        ids = []
        with self.sql_lite as conn:
            cursor = conn.cursor()
            for employee, question in zip(employees,questions):
                metadata = {"question": question, "employee": employee.model_dump()}
                cursor.execute("INSERT INTO metadata (metadata) VALUES (?)", (json.dumps(metadata),))
                ids.append(cursor.lastrowid)
            conn.commit()

        vectors = np.array([employee_to_vector(emp) for emp in employees], dtype=np.float32)
        index = self.index
        index.add_with_ids(vectors, np.array(ids, dtype=np.int64))
        self._save_index(index)
        return ids

    def get(self, id: int) -> tuple[Employee, str]:
        with self.sql_lite as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT metadata FROM metadata WHERE idx=?", (id,))
            row = cursor.fetchone()
            if not row:
                raise Exception("Record not found")

        meta_dict = json.loads(row[0])
        employee = Employee.model_validate(meta_dict["employee"])
        question = meta_dict["question"]
        return employee, question

    def batch_get(self, ids: list[int]) -> list[tuple[Employee, str]]:
        results = []
        with self.sql_lite as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT idx, metadata FROM metadata WHERE idx IN ({','.join(['?']*len(ids))})",
                ids
            )
            rows = cursor.fetchall()
        for idx, meta in rows:
            meta_dict = json.loads(meta)
            emp = Employee.model_validate(meta_dict["employee"])
            q = meta_dict["question"]
            results.append((emp, q))
        return results

    def vector_search(self, employee: Employee, k: int) -> list[tuple[Employee, str, float]]:
        query_vec = np.array([employee_to_vector(employee)], dtype=np.float32)
        index = self.index
        distances, indices = index.search(query_vec, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for "not found"
                continue
            emp, question = self.get(int(idx))
            results.append((emp, question, float(dist)))
        return results
def weighted_softmax_choice(
    results: list[tuple[Employee, str, float]],
    temperature=0.1,
    seed: Optional[int] = None
) -> tuple[Employee, str, float]:
    """
    results = [(employee, question, distance), ...]
    temperature < 1.0 makes it more greedy toward closest match.
    """
    if seed is not None:
        np.random.seed(seed)
    
    distances = np.array([r[2] for r in results], dtype=np.float64)
    sims = -distances / temperature   # scale distances by temperature
    weights = np.exp(sims - np.max(sims))  # softmax trick
    weights /= weights.sum()
    
    choice = np.random.choice(len(results), p=weights)
    return results[choice]
def test_normal_distribution():
    with TemporaryDirectory() as tmp:
        n = 20 
        random_employees = [randomize_employee(seed=i) for i in range(n)]
        questions = [str(i) for i in range(n)]
        evsm = EmployeeVectorAndMetadataStore(faiss_location=str(Path(tmp)/"faiss.index"),md_db_location=str(Path(tmp)/"md.db"))
        evsm.set(random_employees[0],questions[0])
        ids = evsm.batch_set(random_employees,questions)
        print(evsm.get(ids[3]))
        employee_choices = evsm.vector_search(random_employees[3],5)
        print(list(map(lambda x: (x[0].name,x[2]),employee_choices)))
        heuristic ={}
        for i in range(250):
            choice = weighted_softmax_choice(employee_choices, temperature=0.1)[0].name
            if choice not in heuristic:
                heuristic[choice] = 0 
            heuristic[choice] += 1 

        print(random_employees[3].name,heuristic)
async def batch_generate_questions(batch_size:int,setting:str)->list[str]:
    llm = get_llm()
    employees = [randomize_employee() for i in range(batch_size)]
    question_prompts = [generate_prompts(i,setting=setting) for i in employees]
    return list(zip(employees,[i.content for i in await llm.abatch(question_prompts)]))
async def batch_generate_all(batch_size:int,batch_number:int,setting:str)->list[str]:
    return await asyncio.gather(*[batch_generate_questions(batch_size,setting) for i in range(batch_number)])
def sim_and_score_batches(batch_size:int,batch_number:int,base_path:str,setting:str):
    all_batches = asyncio.run(batch_generate_all(batch_size,batch_number,setting))
    total_response = []
    for batch in all_batches:
        total_response +=batch 
    Path(base_path).mkdir(parents=True,exist_ok=True)
    evsm = EmployeeVectorAndMetadataStore(faiss_location=str(Path(base_path)/"faiss.index"),md_db_location=str(Path(base_path)/"md.db"))
    evsm.batch_set(list(map(lambda x: x[0],total_response)),list(map(lambda x:x[1],total_response)))
    

# sim_and_score_batches(2,2,".data/llm_bakes/employee_questions/","Working in a generic office")