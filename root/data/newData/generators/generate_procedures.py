import csv
import random
from datetime import datetime
from collections import defaultdict

# ========== PROCEDURE MAPPING ==========
PROCEDURE_PROBABILITIES = {
    # Condiciones Crónicas
    "Enfermedad respiratoria crónica": [
        ("Terapia con broncodilatadores", 30.77),
        ("Rehabilitación pulmonar", 20.51),
        ("Oxigenoterapia", 15.38),
        ("Pruebas de función pulmonar", 33.33)
    ],
    "Enfermedad cardiovascular": [
        ("Angiografía coronaria", 25.00),
        ("Intervención coronaria percutánea (ICP)", 18.75),
        ("Cirugía de bypass coronario", 12.50),
        ("Ecocardiograma", 31.25)
    ],
    "Neoplasmas": [
        ("Quimioterapia", 25.00),
        ("Radioterapia", 20.00),
        ("Resección quirúrgica", 15.00),
        ("Biopsia", 30.00)
    ],
    "Trastornos mentales": [
        ("Psicoterapia", 25.00),
        ("Manejo de medicación", 30.00),
        ("Terapia electroconvulsiva (TEC)", 5.00),
        ("Terapia cognitivo-conductual (TCC)", 20.00)
    ],
    "Enfermedad de Alzheimer": [
        ("Terapia de estimulación cognitiva", 25.00),
        ("Manejo de medicación", 31.25),
        ("Terapia ocupacional", 18.75),
        ("Clínicas de memoria", 12.50)
    ],

    # Condiciones Agudas
    "Fracturas": [
        ("Yeso o férula", 41.18),
        ("Fijación quirúrgica", 17.65),
        ("Fisioterapia", 29.41)
    ],
    "Luxaciones": [
        ("Reducción (manual o quirúrgica)", 42.11),
        ("Inmovilización", 31.58),
        ("Fisioterapia", 21.05)
    ],
    "Esguinces": [
        ("Protocolo RICE (Reposo, Hielo, Compresión, Elevación)", 42.11),
        ("Fisioterapia", 26.32),
        ("Ortesis o férula", 15.79)
    ],
    "Contusiones": [
        ("Reposo y crioterapia", 47.37),
        ("Manejo del dolor", 26.32),
        ("Fisioterapia", 10.53)
    ],
    "Roturas de ligamentos y tendones": [
        ("Reparación quirúrgica", 26.32),
        ("Fisioterapia", 36.84),
        ("Ortesis o férula", 21.05)
    ],
    "Infección respiratoria aguda": [
        ("Antibioticoterapia", 42.86),
        ("Terapia con broncodilatadores", 21.43),
        ("Oxigenoterapia", 14.29)
    ],
    "Gastroenteritis aguda": [
        ("Hidratación parenteral", 47.06),
        ("Antibioticoterapia", 11.76),
        ("Terapia antiemética", 17.65)
    ],
    "Infarto agudo de miocardio": [
        ("Intervención coronaria percutánea (ICP)", 42.86),
        ("Terapia trombolítica", 28.57),
        ("Cirugía de bypass coronario", 14.29)
    ],
    "Accidente cerebrovascular agudo": [
        ("Terapia trombolítica", 35.71),
        ("Trombectomía mecánica", 21.43),
        ("Rehabilitación", 42.86)
    ],
    "Apendicitis aguda": [
        ("Apendicectomía", 81.82),
        ("Antibioticoterapia", 9.09)
    ],
    "Bronquitis aguda": [
        ("Antibioticoterapia", 35.71),
        ("Terapia con broncodilatadores", 21.43),
        ("Antitusígenos", 28.57)
    ],
    "Pancreatitis aguda": [
        ("Hidratación intravenosa", 41.18),
        ("Manejo del dolor", 35.29),
        ("Soporte nutricional", 23.53)
    ],
    "Otitis media aguda": [
        ("Antibioticoterapia", 47.37),
        ("Manejo del dolor", 26.32),
        ("Miringotomía", 5.26)
    ],
    "Sinusitis aguda": [
        ("Antibioticoterapia", 37.50),
        ("Descongestionantes nasales", 31.25),
        ("Irrigación nasal", 25.00)
    ],
    "Faringitis aguda": [
        ("Antibioticoterapia", 35.71),
        ("Manejo del dolor", 28.57),
        ("Pastillas para la garganta", 21.43)
    ],
    "Meningitis aguda": [
        ("Antibioticoterapia", 47.06),
        ("Terapia antiviral", 11.76),
        ("Corticosteroides", 17.65)
    ],
    "Neumonía aguda": [
        ("Antibioticoterapia", 41.18),
        ("Oxigenoterapia", 23.53),
        ("Terapia con broncodilatadores", 17.65)
    ],
    "Cistitis aguda": [
        ("Antibioticoterapia", 47.06),
        ("Manejo del dolor", 17.65),
        ("Hidratación intravenosa", 29.41)
    ],
    "Celulitis aguda": [
        ("Antibioticoterapia", 47.06),
        ("Manejo del dolor", 23.53),
        ("Cuidado de heridas", 17.65)
    ],
    "Hepatitis aguda": [
        ("Terapia antiviral", 29.41),
        ("Cuidados de soporte", 35.29),
        ("Soporte nutricional", 23.53)
    ]
}
# ========== MAIN SCRIPT ==========
# Load conditions data
patient_conditions = defaultdict(list)
with open('condiciones_pacientes.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        pid = row['Patient ID']
        start_date = datetime.strptime(row['Fecha inicio'], '%Y-%m-%d').date()
        patient_conditions[pid].append({
            'condition': row['Nombre de la condición'],
            'start_date': start_date
        })

# Load encounters data
encounters = []
with open('encuentros_hospitalarios.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        encounters.append({
            'Patient ID': row['Patient ID'],
            'start_date': datetime.strptime(row['Fecha inicio'], '%Y-%m-%d').date()
        })

# Generate procedures
procedures = []
for encounter in encounters:
    pid = encounter['Patient ID']
    enc_date = encounter['start_date']
    
    # Find matching condition
    conditions = patient_conditions.get(pid, [])
    if not conditions:
        continue
        
    # Find most relevant condition (nearest date before encounter)
    matching_conds = [c for c in conditions if c['start_date'] <= enc_date]
    if not matching_conds:
        continue
        
    # Select most recent condition
    condition = max(matching_conds, key=lambda x: x['start_date'])
    
    # Get possible procedures
    procedures_list = PROCEDURE_PROBABILITIES.get(condition['condition'], [])
    if not procedures_list:
        continue
        
    # Select procedure
    procs, weights = zip(*procedures_list)
    selected_procedure = random.choices(procs, weights=weights, k=1)[0]
    
    procedures.append({
        'Patient ID': pid,
        'Nombre del procedimiento': selected_procedure,
        'Fecha': enc_date.strftime('%Y-%m-%d')
    })

# Write to CSV
with open('procedimientos.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Patient ID', 'Nombre del procedimiento', 'Fecha'])
    writer.writeheader()
    writer.writerows(procedures)

print(f"Generated {len(procedures)} medical procedures in 'procedimientos.csv'")