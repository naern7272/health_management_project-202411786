import json
import csv
import os
import pickle
from dataclasses import dataclass, asdict

@dataclass
class Patient_Information:
    id: str
    name: str
    birth_year: int
    gender: str
    height: float
    weight: float
    bmi: float
    status: str

