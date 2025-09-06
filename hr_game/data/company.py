from pydantic import BaseModel


class Company(BaseModel):
  name:str 
  moto:str 
  profitability:int 