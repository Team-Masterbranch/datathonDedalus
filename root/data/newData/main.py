#Systematically generates a new dataset evolved for team Master Branch
import os
import subprocess

def run_script(script_name):
    print(f"Running {script_name}...")
    subprocess.run(['python', script_name], check=True)

def main():
    print("Starting the data generation process...")
    # Step 1: Generate initial patient data
    run_script('generators/generateInitial.py')

    # Step 2: Generate allergies data
    run_script('generators/generateAllergies.py')

    # Step 3: Generate conditions data
    run_script('generators/generateConditions.py')

    # Step 4: Filter patients
    run_script('generators/filterPacientes.py')

    # Step 5: Replace original patients file with filtered one
    os.remove('pacientes.csv')
    os.rename('pacientes_filtrados.csv', 'pacientes.csv')

    # Step 6: Generate encounters
    run_script('generators/generate_encounters.py')

    # Step 7: Generate procedures
    run_script('generators/generate_procedures.py')

if __name__ == '__main__':
    # Change to the script's directory to ensure relative paths work correctly
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()