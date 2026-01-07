# Symptom to Doctor Transformation

This project transforms various disease-symptom datasets into a unified doctor-symptom format.

## Datasets

The raw datasets are included as a Git submodule. To fetch the data, run the following command after cloning the repository:

```bash
git submodule update --init
```

## Usage

To run the transformation script, execute the following command:

```bash
python transform_data.py
```

This will generate a `doctor_symptoms.csv` file in the root of the project, which contains the mapping of medical specialists to symptoms.
