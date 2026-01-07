
import pandas as pd
from disease_mapping import disease_specialist_map

def transform_data():
    """
    Reads disease-symptom datasets, transforms them to doctor-symptom format,
    and saves the result to a new CSV file.
    """
    all_data = []

    # Process DiseaseAndSymptoms.csv
    try:
        df1 = pd.read_csv('new_datasets/DiseaseAndSymptoms.csv')
        df1_melted = df1.melt(id_vars=['Disease'], value_name='Symptom').dropna()
        df1_processed = df1_melted[['Disease', 'Symptom']]
        # Clean up symptom strings
        df1_processed['Symptom'] = df1_processed['Symptom'].str.strip()
        all_data.append(df1_processed)
    except FileNotFoundError:
        print("Warning: new_datasets/DiseaseAndSymptoms.csv not found.")
    except Exception as e:
        print(f"An error occurred while processing new_datasets/DiseaseAndSymptoms.csv: {e}")

    # Process symtoms_df.csv
    try:
        df2 = pd.read_csv('new_datasets/symtoms_df.csv')
        df2_melted = df2.melt(id_vars=['Disease'], value_name='Symptom').dropna()
        df2_processed = df2_melted[['Disease', 'Symptom']]
        # Clean up symptom strings
        df2_processed['Symptom'] = df2_processed['Symptom'].str.strip()
        all_data.append(df2_processed)
    except FileNotFoundError:
        print("Warning: new_datasets/symtoms_df.csv not found.")
    except Exception as e:
        print(f"An error occurred while processing new_datasets/symtoms_df.csv: {e}")


    # Process Training.csv
    try:
        df3 = pd.read_csv('new_datasets/Training.csv')
        # Drop the last empty column if it exists
        df3 = df3.loc[:, ~df3.columns.str.contains('^Unnamed')]
        symptoms = df3.columns[:-1]
        disease_symptom_pairs = []
        for index, row in df3.iterrows():
            disease = row['prognosis']
            for symptom in symptoms:
                if row[symptom] == 1:
                    disease_symptom_pairs.append({'Disease': disease, 'Symptom': symptom.replace('_', ' ').strip()})
        df3_processed = pd.DataFrame(disease_symptom_pairs)
        all_data.append(df3_processed)
    except FileNotFoundError:
        print("Warning: new_datasets/Training.csv not found.")
    except Exception as e:
        print(f"An error occurred while processing new_datasets/Training.csv: {e}")

    if not all_data:
        print("No data to process.")
        return

    # Consolidate all data
    consolidated_df = pd.concat(all_data, ignore_index=True)

    # Clean up disease names to match the mapping keys
    consolidated_df['Disease'] = consolidated_df['Disease'].str.strip()

    # Map diseases to doctors
    consolidated_df['Doctor'] = consolidated_df['Disease'].map(disease_specialist_map)

    # Create the final dataframe
    doctor_symptoms_df = consolidated_df[['Doctor', 'Symptom']].dropna().drop_duplicates()

    # Save to CSV
    output_path = 'doctor_symptoms.csv'
    doctor_symptoms_df.to_csv(output_path, index=False)
    print(f"Successfully created {output_path}")


def validate_output():
    """
    Reads the generated CSV and prints validation information.
    """
    try:
        df = pd.read_csv('doctor_symptoms.csv')
        print("\n--- Validation ---")
        print(f"Shape of the generated file: {df.shape}")
        print(f"Number of unique doctors: {df['Doctor'].nunique()}")
        print("First 10 rows:")
        print(df.head(10))
        print("------------------\n")
    except FileNotFoundError:
        print("Error: The file new_datasets/doctor_symptoms.csv was not found.")
    except Exception as e:
        print(f"An error occurred during validation: {e}")


if __name__ == "__main__":
    transform_data()
    validate_output()
