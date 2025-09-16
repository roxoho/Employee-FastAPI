from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List, Optional
from dotenv import load_dotenv
import os

load_dotenv()

connection_string = os.getenv("MONGODB_URI")

client = MongoClient(connection_string)
db = client['assessment_db']
collection = db['employees']

collection.create_index("employee_id", unique=True)

class Employee(BaseModel):
    employee_id: str
    name: str
    department: str
    salary: int
    joining_date: str
    skills: List[str]

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[int] = None
    joining_date: Optional[str] = None
    skills: Optional[List[str]] = None

app = FastAPI()

# API Endpoints
@app.post("/employees")
async def create_employee(employee: Employee):
    if collection.find_one({"employee_id": employee.employee_id}):
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    collection.insert_one(employee.dict())
    return {"message": "Employee created successfully"}

@app.get("/employees/salary/avg-salary")
async def average_salary_by_department():
    pipeline = [
        {"$group": {"_id": "$department", "avg_salary": {"$avg": "$salary"}}}
    ]
    results = list(collection.aggregate(pipeline))
    if not results:
        raise HTTPException(status_code=404, detail="No departments found")
    return [{"department": r["_id"], "avg_salary": round(r["avg_salary"], 2)} for r in results]

@app.get("/employees/search", response_model=List[Employee])
async def search_employees_by_skill(skill: str = Query(...)):
    cursor = collection.find({"skills": {"$in": [skill]}})
    employees = [emp for emp in cursor]
    for emp in employees:
        del emp["_id"]
    if not employees:
        raise HTTPException(status_code=404, detail=f"No employees found with skill: {skill}")
    return employees

@app.get("/employees", response_model=List[Employee])
async def list_employees_by_department(
    department: str = Query(...),
):
    cursor = collection.find({"department": department}).sort("joining_date", -1)
    employees = [emp for emp in cursor]
    for emp in employees:
        del emp["_id"]
    if not employees:
        raise HTTPException(status_code=404, detail="No employees found for the specified department")
    return employees

@app.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str):
    employee = collection.find_one({"employee_id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    del employee["_id"]
    return employee

@app.put("/employees/{employee_id}")
async def update_employee(employee_id: str, update: EmployeeUpdate):
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    result = collection.update_one({"employee_id": employee_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee updated successfully"}

@app.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str):
    result = collection.delete_one({"employee_id": employee_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}