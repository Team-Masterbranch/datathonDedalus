import csv
import random
from config import TOTAL_PATIENTS as num_patients

# Define the number of patients
#num_patients = 1_000_000

# Define gender probabilities
gender_probabilities = {'M': 0.49, 'F': 0.51}

# Define age group probabilities
age_group_probabilities = {
    '0-14': {'M': 0.0425, 'F': 0.0401},
    '15-64': {'M': 0.1610, 'F': 0.1610},
    '65+': {'M': 0.0441, 'F': 0.0512}
}

# Define province probabilities
province_probabilities = {
    'Sevilla': 0.232,
    'Málaga': 0.178,
    'Cádiz': 0.154,
    'Granada': 0.118,
    'Córdoba': 0.102,
    'Almería': 0.086,
    'Jaén': 0.079,
    'Huelva': 0.051
}

# Function to generate a random gender based on probabilities
def generate_gender():
    return random.choices(list(gender_probabilities.keys()), weights=list(gender_probabilities.values()), k=1)[0]

# Function to generate a random age based on gender and age group probabilities
def generate_age(gender):
    age_group = random.choices(list(age_group_probabilities.keys()), 
                               weights=[age_group_probabilities[group][gender] for group in age_group_probabilities], 
                               k=1)[0]
    if age_group == '0-14':
        return random.randint(0, 14)
    elif age_group == '15-64':
        return random.randint(15, 64)
    else:
        return random.randint(65, 100)

# Function to generate a random province based on probabilities
def generate_province():
    return random.choices(list(province_probabilities.keys()), 
                          weights=list(province_probabilities.values()), 
                          k=1)[0]

# Generate the CSV file
with open('pacientes.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Patient ID', 'Gender', 'Age', 'Province'])
    
    for patient_id in range(1, num_patients + 1):
        gender = generate_gender()
        age = generate_age(gender)
        province = generate_province()
        writer.writerow([patient_id, gender, age, province])

print("CSV file generated successfully.")
