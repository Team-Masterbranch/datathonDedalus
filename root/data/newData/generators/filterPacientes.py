import csv

# Read patient IDs with allergies
allergy_patients = set()
with open('pacientes_con_alergias.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        allergy_patients.add(row['Patient ID'])

# Read patient IDs with conditions
condition_patients = set()
with open('condiciones_pacientes.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        condition_patients.add(row['Patient ID'])

# Combine both sets
relevant_patients = allergy_patients.union(condition_patients)

# Filter original pacientes.csv
with open('pacientes.csv', 'r') as infile, \
     open('pacientes_filtrados.csv', 'w', newline='') as outfile:

    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        if row['Patient ID'] in relevant_patients:
            writer.writerow(row)

print("Filtered file created: pacientes_filtrados.csv")