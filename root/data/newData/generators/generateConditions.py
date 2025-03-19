import csv
import random
import datetime
from collections import defaultdict
from config import TOTAL_PATIENTS

# Configuration
#TOTAL_PATIENTS = 1_000_000
CHRONIC_PROB = 0.60  # 60% of all patients
ACUTE_PROB = 0.20    # 20% of all patients
MULTI_COND_PROB = 0.15

# Chronic diseases configuration
CHRONIC_DISEASES = {
    # Allergy-related respiratory diseases
    "Alergia al polen": {
        "name": "Enfermedad respiratoria crónica",
        "snomed": "31387002",
        "age_groups": {"0-14": 0.10, "15-24": 0.20, "25-64": 0.30, "65+": 0.15}
    },
    "Alergia a los ácaros del polvo": {
        "name": "Enfermedad respiratoria crónica",
        "snomed": "31387002",
        "age_groups": {"0-14": 0.08, "15-24": 0.10, "25-64": 0.12, "65+": 0.10}
    },
    "Alergia a la caspa de animales": {
        "name": "Enfermedad respiratoria crónica",
        "snomed": "31387002",
        "age_groups": {"0-14": 0.06, "15-24": 0.08, "25-64": 0.10, "65+": 0.05}
    },
    "Alergia al moho": {
        "name": "Enfermedad respiratoria crónica",
        "snomed": "31387002",
        "age_groups": {"0-14": 0.05, "15-24": 0.07, "25-64": 0.09, "65+": 0.06}
    },
    "Alergia a las picaduras de insectos": {
        "name": "Enfermedad respiratoria crónica",
        "snomed": "31387002",
        "age_groups": {"0-14": 0.02, "15-24": 0.03, "25-64": 0.03, "65+": 0.02}
    },
    
    # Non-allergy chronic diseases
    "Cardiovascular": {
        "name": "Enfermedad cardiovascular",
        "snomed": "49601007",
        "age_groups": {"25-64": 0.33}
    },
    "Neoplasms": {
        "name": "Neoplasmas",
        "snomed": "363346000",
        "age_groups": {"25-64": 0.15}
    },
    "Mental": {
        "name": "Trastornos mentales",
        "snomed": "74732009",
        "age_groups": {"25-64": 0.075}
    },
    "Alzheimer": {
        "name": "Enfermedad de Alzheimer",
        "snomed": "26929004",
        "age_groups": {"65+": 0.80}
    }
}

# Acute conditions configuration
ACUTE_CONDITIONS = [
    ("Fracturas", "125605004"),
    ("Luxaciones", "23974007"),
    ("Esguinces", "23924001"),
    ("Contusiones", "40917007"),
    ("Roturas de ligamentos y tendones", "312646001"),
    ("Infección respiratoria aguda", "54150009"),
    ("Gastroenteritis aguda", "445441000124101"),
    ("Infarto agudo de miocardio", "57054005"),
    ("Accidente cerebrovascular agudo", "230690007"),
    ("Apendicitis aguda", "74400008"),
    ("Bronquitis aguda", "32398004"),
    ("Pancreatitis aguda", "235595009"),
    ("Otitis media aguda", "65363002"),
    ("Sinusitis aguda", "444814009"),
    ("Faringitis aguda", "444814009"),
    ("Meningitis aguda", "7180009"),
    ("Neumonía aguda", "233604007"),
    ("Cistitis aguda", "19732008"),
    ("Celulitis aguda", "128045006"),
    ("Hepatitis aguda", "235856003")
]

def get_age_group(age):
    if age < 15: return "0-14"
    if age < 25: return "15-24"
    if age < 65: return "25-64"
    return "65+"

def random_date(start_year, end_year):
    start = datetime.date(start_year, 1, 1)
    end = datetime.date(end_year, 12, 31)
    return start + datetime.timedelta(days=random.randint(0, (end - start).days))

# Load patient data
patients = {}
with open('pacientes.csv', mode='r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        patients[row['Patient ID']] = {
            'age': int(row['Age']),
            'province': row['Province']
        }

# Load allergy data
allergies = defaultdict(list)
with open('pacientes_con_alergias.csv', mode='r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        allergies[row['Patient ID']].append(row['Tipo de Alergia'])

# Generate medical conditions
output = []
patient_ids = list(patients.keys())
random.shuffle(patient_ids)

for pid in patient_ids:
    conditions = []
    age = patients[pid]['age']
    age_group = get_age_group(age)
    
    # Generate chronic conditions (60% of all patients)
    if random.random() < CHRONIC_PROB:
        # Allergy-related chronic conditions
        for allergy in allergies.get(pid, []):
            if allergy in CHRONIC_DISEASES:
                data = CHRONIC_DISEASES[allergy]
                prob = data["age_groups"].get(age_group, 0)
                if random.random() < prob:
                    conditions.append({
                        'type': 'crónica',
                        'name': data["name"],
                        'snomed': data["snomed"],
                        'start': random_date(2010, 2023).strftime('%Y-%m-%d'),
                        'end': None
                    })
        
        # Non-allergy chronic conditions
        if age_group == "25-64":
            # Cardiovascular disease (33% of adults)
            if random.random() < 0.33:
                conditions.append({
                    'type': 'crónica',
                    'name': "Enfermedad cardiovascular",
                    'snomed': "49601007",
                    'start': random_date(2010, 2023).strftime('%Y-%m-%d'),
                    'end': None
                })
            
            # Cancer (15% of adults)
            if random.random() < 0.15:
                conditions.append({
                    'type': 'crónica',
                    'name': "Neoplasmas",
                    'snomed': "363346000",
                    'start': random_date(2010, 2023).strftime('%Y-%m-%d'),
                    'end': None
                })
            
            # Mental disorders (7.5% of adults)
            if random.random() < 0.075:
                conditions.append({
                    'type': 'crónica',
                    'name': "Trastornos mentales",
                    'snomed': "74732009",
                    'start': random_date(2010, 2023).strftime('%Y-%m-%d'),
                    'end': None
                })
        
        if age_group == "65+":
            # Alzheimer's (80% of seniors)
            if random.random() < 0.80:
                conditions.append({
                    'type': 'crónica',
                    'name': "Enfermedad de Alzheimer",
                    'snomed': "26929004",
                    'start': random_date(2010, 2023).strftime('%Y-%m-%d'),
                    'end': None
                })

    # Generate acute conditions (20% of all patients)
    if random.random() < ACUTE_PROB:
        cond, snomed = random.choice(ACUTE_CONDITIONS)
        start_date = random_date(2016, 2023)
        end_date = start_date + datetime.timedelta(days=random.randint(1, 730))
        conditions.append({
            'type': 'aguda',
            'name': cond,
            'snomed': snomed,
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        })

    # Handle multiple conditions (15% of patients with conditions)
    if conditions and random.random() < MULTI_COND_PROB:
        # Add additional chronic condition
        if random.random() < 0.5 and age_group == "25-64":
            conditions.append({
                'type': 'crónica',
                'name': "Enfermedad cardiovascular",
                'snomed': "49601007",
                'start': random_date(2010, 2023).strftime('%Y-%m-%d'),
                'end': None
            })
        else:
            # Add additional acute condition
            cond, snomed = random.choice(ACUTE_CONDITIONS)
            start_date = random_date(2016, 2023)
            end_date = start_date + datetime.timedelta(days=random.randint(1, 730))
            conditions.append({
                'type': 'aguda',
                'name': cond,
                'snomed': snomed,
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            })

    # Add to output
    for condition in conditions:
        output.append({
            'Patient ID': pid,
            'Tipo de condición': condition['type'],
            'Nombre de la condición': condition['name'],
            'Código SNOMED': condition['snomed'],
            'Fecha inicio': condition['start'],
            'Fecha fin': condition['end'] if condition['end'] else ""
        })

# Write to CSV
with open('condiciones_pacientes.csv', mode='w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'Patient ID', 'Tipo de condición', 'Nombre de la condición',
        'Código SNOMED', 'Fecha inicio', 'Fecha fin'
    ])
    writer.writeheader()
    writer.writerows(output)

print("Archivo generado exitosamente: condiciones_pacientes.csv")