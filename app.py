from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel ,Field,computed_field,field_validator
from typing import Literal,Annotated
import pickle
import pandas as pd

# importig model
with open ("model.pkl","rb") as f:
    model=pickle.load(f)

app = FastAPI()

tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]

# pydantic model to validate the incoming data
class Userinput(BaseModel):
    age:Annotated[int,Field(...,gt=0,lt=120,description="Age of the user")]
    weight:Annotated[float,Field(...,gt=0,description="weight of the user")]
    height:Annotated[float,Field(...,gt=0,lt=2.5,description="height of the user")]
    income:Annotated[float,Field(...,description="salary of the user")]
    smoker:Annotated[bool,Field(...,gt=0,lt=120,description="smoker or not")]
    city:Annotated[str,Field(...,description="city of the user")]
    occupation:Annotated[Literal["retired","freelancer","student","government_job","bussiness_owner","unemployed","private_job"],Field(...,description="occupation of the user")]

    @field_validator("city")
    @classmethod
    def city_valid(cls,v:str)->str:
        v=v.strip().title()
        return v

    @computed_field
    @property
    def bmi(self)->float:
        return self.weight/(self.height**2)

    @computed_field
    @property
    def lifestyle_risk(self)->str:
        if self.smoker and self.bmi>30:
            return "high"
        elif self.smoker or self.bmi>27:
            return "medium"
        else:
             return "low"

    @computed_field
    @property
    def age_group(self)->str:
        if self.age <25:
            return "young"
        elif self.age <45:
            return "adult"
        elif self.age <60:
            return "middle_aged"
        return "senior"

    @computed_field
    @property
    def city_tier(self)->int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3

@app.post('/predict')
def predict_premium(data:Userinput):
    input_df=pd.DataFrame([{
        "bmi":data.bmi,
        "age_group":data.age_group,
        "lifestyle_risk":data.lifestyle_risk,
        "city_tier":data.city_tier,
        "income_lpa":data.income,
        "occupation":data.occupation
    }])

    prediction = model.predict(input_df)[0]

    return JSONResponse(status_code=200,content={'Predicted_category':prediction})