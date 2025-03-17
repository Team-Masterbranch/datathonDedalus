import csv
import random
from datetime import datetime, timedelta

# Define allergy probabilities by age group
allergy_probabilities = {
    "Alergia al polen": {
        "SNOMED": "418689005",
        "0-14": 0.10,
        "15-24": 0.20,
        "25-64": 0.30,
        "65+": 0.15
    },
    "Alergia a los alimentos": {
        "SNOMED": "91934008",
        "0-14": 0.0523,
        "15-24": 0.04,
        "25-64": 0.0465,
        "65+": 0.02
    },
    "Alergia a los ácaros del polvo": {
        "SNOMED": "232347008",
        "0-14": 0.08,
        "15-24": 0.10,
        "25-64": 0.12,
        "65+": 0.10
    },
    "Alergia a la caspa de animales": {
        "SNOMED": "232350009",
        "0-14": 0.06,
        "15-24": 0.08,
        "25-64": 0.10,
        "65+": 0.05
    },
    "Alergia al moho": {
        "SNOMED": "232349003",
        "0-14": 0.05,
        "15-24": 0.07,
        "25-64": 0.09,
        "65+": 0.06
    },
    "Alergia a las picaduras de insectos": {
        "SNOMED": "91936005",
        "0-14": 0.02,
        "15-24": 0.03,
        "25-64": 0.03,
        "65+": 0.02
    }
}

# Function to determine the age group based on age
def get_age_group(age):
    if age <= 14:
        return "0-14"
    elif 15 <= age <= 24:
        return "15-24"
    elif 25 <= age <= 64:
        return "25-64"
    else:
        return "65+"

# Function to diagnose allergies based on age group and probabilities
def diagnose_allergies(age_group):
    allergies = []
    for allergy, data in allergy_probabilities.items():
        probability = data[age_group]
        if random.random() < probability:
            allergies.append({
                "Tipo de Alergia": allergy,
                "Código SNOMED": data["SNOMED"],
                "Fecha de Diagnóstico": datetime(2016, 1, 1) + timedelta(days=random.randint(0, 3285))  # 9 years range
            })
    return allergies

# Read the pacientes.csv file and diagnose allergies
with open('pacientes.csv', mode='r') as infile, open('pacientes_con_alergias.csv', mode='w', newline='') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=['Patient ID', 'Tipo de Alergia', 'Código SNOMED', 'Fecha de Diagnóstico'])
    writer.writeheader()

    for row in reader:
        patient_id = row['Patient ID']
        age = int(row['Age'])
        age_group = get_age_group(age)
        allergies = diagnose_allergies(age_group)

        for allergy in allergies:
            writer.writerow({
                'Patient ID': patient_id,
                'Tipo de Alergia': allergy['Tipo de Alergia'],
                'Código SNOMED': allergy['Código SNOMED'],
                'Fecha de Diagnóstico': allergy['Fecha de Diagnóstico'].strftime('%Y-%m-%d')
            })

print("CSV file 'pacientes_con_alergias.csv' generated successfully.")