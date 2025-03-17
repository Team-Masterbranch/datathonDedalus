import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict

# ========== CONFIGURATION ==========
ENCOUNTER_PROBABILITIES = {
    "Hospitalización": {
        "Enfermedad respiratoria crónica": 0.20,
        "Enfermedad cardiovascular": 0.25,
        "Neoplasmas": 0.15,
        "Trastornos mentales": 0.10,
        "Enfermedad de Alzheimer": 0.05,
        "Fracturas": 0.10,
        "Luxaciones": 0.05,
        "Esguinces": 0.03,
        "Contusiones": 0.02,
        "Roturas de ligamentos y tendones": 0.02,
        "Infección respiratoria aguda": 0.05,
        "Gastroenteritis aguda": 0.03,
        "Infarto agudo de miocardio": 0.05,
        "Accidente cerebrovascular agudo": 0.05,
        "Apendicitis aguda": 0.02,
        "Bronquitis aguda": 0.03,
        "Pancreatitis aguda": 0.02,
        "Otitis media aguda": 0.01,
        "Sinusitis aguda": 0.01,
        "Faringitis aguda": 0.01,
        "Meningitis aguda": 0.01,
        "Neumonía aguda": 0.02,
        "Cistitis aguda": 0.01,
        "Celulitis aguda": 0.01,
        "Hepatitis aguda": 0.01
    },
    "Atención Primaria": {
        "Enfermedad respiratoria crónica": 0.30,
        "Enfermedad cardiovascular": 0.20,
        "Neoplasmas": 0.10,
        "Trastornos mentales": 0.20,
        "Enfermedad de Alzheimer": 0.05,
        "Fracturas": 0.05,
        "Luxaciones": 0.03,
        "Esguinces": 0.02,
        "Contusiones": 0.02,
        "Roturas de ligamentos y tendones": 0.02,
        "Infección respiratoria aguda": 0.10,
        "Gastroenteritis aguda": 0.05,
        "Bronquitis aguda": 0.05,
        "Otitis media aguda": 0.03,
        "Sinusitis aguda": 0.03,
        "Faringitis aguda": 0.03,
        "Neumonía aguda": 0.02,
        "Cistitis aguda": 0.02,
        "Celulitis aguda": 0.01,
        "Hepatitis aguda": 0.01
    },
    "Urgencias": {
        "Enfermedad respiratoria crónica": 0.15,
        "Enfermedad cardiovascular": 0.20,
        "Neoplasmas": 0.05,
        "Trastornos mentales": 0.10,
        "Enfermedad de Alzheimer": 0.05,
        "Fracturas": 0.20,
        "Luxaciones": 0.10,
        "Esguinces": 0.05,
        "Contusiones": 0.05,
        "Roturas de ligamentos y tendones": 0.05,
        "Infección respiratoria aguda": 0.05,
        "Gastroenteritis aguda": 0.03,
        "Infarto agudo de miocardio": 0.05,
        "Accidente cerebrovascular agudo": 0.05,
        "Apendicitis aguda": 0.03,
        "Bronquitis aguda": 0.03,
        "Pancreatitis aguda": 0.02,
        "Otitis media aguda": 0.02,
        "Sinusitis aguda": 0.02,
        "Faringitis aguda": 0.02,
        "Meningitis aguda": 0.01,
        "Neumonía aguda": 0.02,
        "Cistitis aguda": 0.01,
        "Celulitis aguda": 0.01,
        "Hepatitis aguda": 0.01
    },
    "Consultas Especializadas": {
        "Enfermedad respiratoria crónica": 0.25,
        "Enfermedad cardiovascular": 0.25,
        "Neoplasmas": 0.20,
        "Trastornos mentales": 0.15,
        "Enfermedad de Alzheimer": 0.10,
        "Fracturas": 0.05,
        "Luxaciones": 0.03,
        "Esguinces": 0.02,
        "Contusiones": 0.02,
        "Roturas de ligamentos y tendones": 0.02,
        "Pancreatitis aguda": 0.05,
        "Otitis media aguda": 0.03,
        "Sinusitis aguda": 0.03,
        "Faringitis aguda": 0.03,
        "Neumonía aguda": 0.02,
        "Cistitis aguda": 0.02,
        "Celulitis aguda": 0.01,
        "Hepatitis aguda": 0.01
    },
    "Cirugía Ambulatoria": {
        "Fracturas": 0.30,
        "Luxaciones": 0.20,
        "Esguinces": 0.10,
        "Roturas de ligamentos y tendones": 0.10,
        "Apendicitis aguda": 0.10,
        "Otitis media aguda": 0.05,
        "Sinusitis aguda": 0.05,
        "Faringitis aguda": 0.05
    }
}

CONDITION_TO_ENCOUNTERS = {
    condition: [enc_type for enc_type, enc_data in ENCOUNTER_PROBABILITIES.items() if condition in enc_data]
    for enc_type in ENCOUNTER_PROBABILITIES
    for condition in ENCOUNTER_PROBABILITIES[enc_type]
}

# ========== MAIN SCRIPT ==========
# Load conditions data
conditions_data = defaultdict(list)
with open('condiciones_pacientes.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        conditions_data[row['Patient ID']].append({
            'condition': row['Nombre de la condición'],
            'start_date': datetime.strptime(row['Fecha inicio'], '%Y-%m-%d'),
            'end_date': datetime.strptime(row['Fecha fin'], '%Y-%m-%d') if row['Fecha fin'] else None
        })

# Generate encounters
encounters = []
for patient_id, conditions in conditions_data.items():
    for condition in conditions:
        # Get possible encounter types for this condition
        possible_encounters = CONDITION_TO_ENCOUNTERS.get(condition['condition'], [])
        if not possible_encounters:
            continue
            
        # Select encounter type based on probabilities
        weights = [ENCOUNTER_PROBABILITIES[enc_type][condition['condition']] for enc_type in possible_encounters]
        selected_encounter = random.choices(possible_encounters, weights=weights, k=1)[0]
        
        # Calculate dates
        start_date = condition['start_date']
        if selected_encounter == "Hospitalización":
            end_date = start_date + timedelta(days=random.randint(1, 7))
        else:
            end_date = start_date
            
        # Add main encounter
        encounters.append({
            'Patient ID': patient_id,
            'Tipo de encuentro': selected_encounter,
            'Fecha inicio': start_date.strftime('%Y-%m-%d'),
            'Fecha fin': end_date.strftime('%Y-%m-%d')
        })
        
        # 10% chance for follow-up
        if random.random() < 0.1:
            followup_date = start_date + timedelta(days=random.randint(14, 365))
            encounters.append({
                'Patient ID': patient_id,
                'Tipo de encuentro': selected_encounter,
                'Fecha inicio': followup_date.strftime('%Y-%m-%d'),
                'Fecha fin': followup_date.strftime('%Y-%m-%d')
            })

# Write to CSV
with open('encuentros_hospitalarios.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Patient ID', 'Tipo de encuentro', 'Fecha inicio', 'Fecha fin'])
    writer.writeheader()
    writer.writerows(encounters)

print(f"Generated {len(encounters)} hospital encounters in 'encuentros_hospitalarios.csv'")