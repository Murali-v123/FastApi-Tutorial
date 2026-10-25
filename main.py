from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel ,Field,computed_field
from typing import Annotated ,Literal,Optional
import json

app = FastAPI()


class Patient(BaseModel):
    id:Annotated[str,Field(...,description="Enter ID of the patient",example='P001')]
    name:Annotated[str,Field(...,description="Enter name of the patient")]
    city:Annotated[str,Field(...,description="Enter city name of the patient")]
    age:Annotated[int,Field(...,description="Enter age of the patient")]
    gender:Annotated[Literal['male','female','others'],Field(...,description="Enter gender of the patient")]
    height:Annotated[float,Field(...,description="Enter height of the patient in mtrs")]
    weight:Annotated[float,Field(...,description="Enter weight of the patient in kg")]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2))
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi<18.5:
            return 'underweight'
        elif self.bmi<25:
            return 'normal'
        elif self.bmi<30:
            return 'overweight'
        else:
            return 'obese'

class updatepatient(BaseModel):
    name:Annotated[Optional[str],Field(default=None)]
    city:Annotated[Optional[str],Field(default=None)]
    age:Annotated[Optional[int],Field(default=None,gt=0)]
    gender:Annotated[Optional[Literal["male","female","others"]],Field(default=None)]
    height:Annotated[Optional[float],Field(default=None)]
    weight:Annotated[Optional[float],Field(default=None)]
    

def load_data():
    try:
        with open('patients.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {} 

def save_data(data):
    with open('patients.json' , 'w') as f:
        json.dump(data ,f)


@app.get("/")
def hello():
    return "hello broo"

@app.get("/about")
def about():
    return "hello broo"

@app.get("/view")
def view():
    data=load_data()

    return data

@app.get('/patient/{patient_id}')
def view_pateient(patient_id:str =Path(...,description='Id of the patient in the DB',examples=['P001'])):
    data = load_data()
    if patient_id in data:
        patient_data = dict(data[patient_id])
        patient_data['id'] = patient_id
        return patient_data
    raise HTTPException(status_code=404,detail='patient data not found')


@app.get('/sort')
def sort_patient(sort_by:str=Query(..., description='sort on the basis of height,weight,name,bmi,age'),
                 order: str = Query(..., description='sort in asc or desc order',examples=['asc'])
                 ):

    valid_field=['height','weight','bmi','name','age']

    if sort_by not in valid_field:
        raise HTTPException(status_code=400,detail=f'ivalid field select from {valid_field}')

    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail='ivalid field select from asc or desc')

    data =load_data()

    sort_order=True if order=='desc' else False

    data_list = [{'id': k, **v} for k, v in data.items()]
    # Missing sort values go to the end
    sorted_data = sorted(
        data_list,
        key=lambda x: (x.get(sort_by) is None, x.get(sort_by, 0)),
        reverse=sort_order
    )

    return sorted_data

@app.post('/create')
def create(patient:Patient):
    #load the data
    data = load_data()

    #checking patient exist or not
    if patient.id in data:
        raise HTTPException(status_code=400,detail='patient already exists')

    #add new patient
    data[patient.id]=patient.model_dump(exclude=['id'])

    save_data(data)

    return JSONResponse(status_code=201,content={'message':'Patient data saved sucessfully'})

@app.post("/edit/{patient_id}")
def udpdate(patient_id:str,patient_update:updatepatient):
    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail="Patient not found")

    existing_data=data[patient_id]
    updated_info=patient_update.model_dump(exclude_unset=True)

    for key,value in updated_info.items():
        existing_data[key]=value

    existing_data['id']=patient_id
    patient_pydantic_obj=Patient(**existing_data)

    existing_data=patient_pydantic_obj.model_dump(exclude='id')
    data[patient_id]=existing_data

    save_data(data)

    return JSONResponse(status_code=200,content={"message":"update success"})


@app.delete("/delete/{patient_id}")
def delete(patient_id:str):
    data=load_data()

    if patient_id not in data:
            raise HTTPException(status_code=404,detail="Patient not found")

    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200,content={"message":"successful"})
