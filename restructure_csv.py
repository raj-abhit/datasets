#!/usr/bin/env python3
"""
Script to restructure symptom-disease-test-dataset.csv:
- Remove the 'label' column
- Keep only 'text' and 'doctor' columns
- Correct doctor mappings based on medical guidelines
"""

import csv
import re


class DoctorRecommender:
    """Recommends medical specialists based on symptoms."""
    
    def __init__(self):
        # Define symptom patterns for each specialist
        # Priority: lower number = higher importance
        
        self.specialist_rules = {
            'Cardiologist': {
                'symptoms': [
                    'chest_pain', 'chest pain', 'breathlessness',
                    'palpitations', 'irregular_heartbeat', 'irregular heartbeat',
                    'fast_heart_rate', 'fast heart rate', 'sweating'
                ],
                'priority': 1,  # Highest priority - life-threatening
                'combined_symptoms': [
                    ['chest_pain', 'breathlessness'],
                    ['chest_pain', 'sweating'],
                    ['chest pain', 'breathlessness'],
                    ['chest pain', 'sweating'],
                    ['breathlessness', 'sweating', 'chest'],
                    ['vomiting', 'breathlessness', 'sweating', 'chest_pain']
                ],
                'required_combined': True  # Must have combined symptoms
            },
            'Neurologist': {
                'symptoms': [
                    'headache', 'altered_sensorium', 'loss_of_balance',
                    'spinning_movements', 'dizziness', 'seizures',
                    'weakness_of_one_body_side', 'unsteadiness',
                    'slurred_speech', 'coma', 'altered sensorium',
                    'loss of balance', 'weakness of one body side',
                    'memory', 'memory_loss', 'alzheimer', 'dementia',
                    'tremors', 'visual_disturbances'
                ],
                'priority': 2,
                'combined_symptoms': [
                    ['headache', 'altered_sensorium'],
                    ['weakness', 'altered_sensorium'],
                    ['weakness_of_one_body_side'],
                    ['spinning_movements', 'loss_of_balance'],
                    ['vomiting', 'headache', 'altered_sensorium'],
                    ['vomiting', 'headache', 'weakness_of_one_body_side']
                ]
            },
            'Pulmonologist': {
                'symptoms': [
                    'cough', 'mucoid_sputum', 'rusty_sputum', 'blood_in_sputum',
                    'phlegm', 'mucoid sputum', 'rusty sputum', 'blood in sputum',
                    'mucus', 'respiratory', 'breathlessness with cough'
                ],
                'priority': 2,  # High priority for respiratory with blood/sputum
                'combined_symptoms': [
                    ['blood_in_sputum', 'cough'],
                    ['rusty_sputum', 'cough'],
                    ['phlegm', 'cough'],
                    ['breathlessness', 'cough'],
                    ['high_fever', 'cough', 'phlegm'],
                    ['cough', 'chest_pain', 'phlegm'],
                    ['family_history', 'cough'],
                    ['mucoid_sputum', 'cough']
                ]
            },
            'Gastroenterologist': {
                'symptoms': [
                    'vomiting', 'diarrhea', 'diarrhoea', 'constipation',
                    'abdominal_pain', 'stomach_pain', 'acidity', 'indigestion',
                    'bloody_stool', 'loss_of_appetite', 'nausea',
                    'yellowing_of_eyes', 'yellowish_skin', 'dark_urine',
                    'swelling_of_stomach', 'distention_of_abdomen',
                    'fluid_overload', 'abdominal pain', 'stomach pain',
                    'bloody stool', 'loss of appetite', 'yellowing of eyes',
                    'yellowish skin', 'dark urine', 'dehydration', 'sunken_eyes',
                    'history_of_alcohol_consumption', 'acute_liver_failure',
                    'stomach_bleeding', 'pain_during_bowel_movements',
                    'pain_in_anal_region', 'irritation_in_anus', 'ulcers_on_tongue',
                    'internal_itching', 'passage_of_gases', 'gastritis',
                    'gnawing', 'belly_pain', 'toxic_look_(typhos)'
                ],
                'priority': 4,
                'combined_symptoms': [
                    ['vomiting', 'diarrhea'],
                    ['vomiting', 'diarrhoea'],
                    ['abdominal_pain', 'vomiting'],
                    ['stomach_pain', 'acidity'],
                    ['stomach_pain', 'vomiting'],
                    ['yellowish_skin', 'abdominal_pain'],
                    ['yellowish_skin', 'yellowing_of_eyes'],
                    ['constipation', 'pain_during_bowel_movements']
                ]
            },
            'Dermatologist': {
                'symptoms': [
                    'skin_rash', 'itching', 'skin_discoloration',
                    'pus_filled_pimples', 'blackheads', 'skin_peeling',
                    'nodal_skin_eruptions', 'dischromic__patches',
                    'blister', 'red_sore_around_nose', 'yellow_crust_ooze',
                    'scurring',  # Note: spelling from source data
                    'red_spots_over_body', 'skin rash',
                    'pus filled pimples', 'skin peeling',
                    'small_dents_in_nails', 'inflammatory_nails',
                    'mosquito', 'bites', 'hive'
                ],
                'priority': 7,
                'combined_symptoms': [
                    ['skin_rash', 'joint_pain']  # Psoriatic conditions
                ]
            },
            'ENT': {
                'symptoms': [
                    'continuous_sneezing', 'watering_from_eyes',
                    'throat_irritation', 'sinus_pressure', 'runny_nose',
                    'congestion', 'loss_of_smell', 'patches_in_throat',
                    'shivering', 'continuous sneezing', 'watering from eyes',
                    'throat irritation', 'sinus pressure', 'runny nose',
                    'loss of smell', 'patches in throat', 'chills with sneezing'
                ],
                'priority': 8,
                'combined_symptoms': [
                    ['continuous_sneezing', 'watering_from_eyes'],
                    ['continuous_sneezing', 'chills']
                ]
            },
            'Orthopedic': {
                'symptoms': [
                    'joint_pain', 'neck_pain', 'knee_pain', 'hip_pain',
                    'stiff_neck', 'muscle_weakness', 'swelling_joints',
                    'back_pain', 'painful_walking', 'muscle_wasting',
                    'movement_stiffness', 'joint pain', 'neck pain',
                    'knee pain', 'hip pain', 'stiff neck', 'muscle weakness',
                    'swelling joints', 'back pain', 'painful walking'
                ],
                'priority': 9,
                'combined_symptoms': [
                    ['joint_pain', 'stiff_neck'],
                    ['muscle_wasting']
                ]
            },
            'Endocrinologist': {
                'symptoms': [
                    'excessive_hunger', 'polyuria', 'increased_appetite',
                    'irregular_sugar_level', 'weight_gain', 'cold_hands',
                    'enlarged_thyroid', 'obesity', 'restlessness', 'lethargy',
                    'excessive hunger', 'increased appetite',
                    'irregular sugar level', 'weight gain', 'cold hands',
                    'enlarged thyroid', 'diabetes', 'thyroid',
                    'fast_heart_rate', 'irritability', 'abnormal_menstruation',
                    'swollen', 'brittle', 'varicose'
                ],
                'priority': 3,  # Higher priority for endocrine emergencies
                'combined_symptoms': [
                    ['excessive_hunger', 'polyuria'],
                    ['excessive_hunger', 'increased_appetite'],
                    ['irregular_sugar_level', 'polyuria'],
                    ['fast_heart_rate', 'excessive_hunger', 'restlessness'],
                    ['fast_heart_rate', 'excessive_hunger', 'irritability'],
                    ['restlessness', 'sweating', 'diarrhoea', 'fast_heart_rate'],
                    ['weight_loss', 'fast_heart_rate', 'excessive_hunger']
                ]
            },
            'Urologist': {
                'symptoms': [
                    'burning_micturition', 'bladder_discomfort',
                    'foul_smell_of_urine', 'continuous_feel_of_urine',
                    'burning micturition', 'bladder discomfort',
                    'foul smell of urine', 'continuous feel of urine',
                    'urine', 'urinary', 'kidney', 'spotting__urination'
                ],
                'priority': 5,
                'combined_symptoms': [
                    ['burning_micturition', 'bladder_discomfort'],
                    ['spotting__urination', 'burning_micturition']
                ]
            },
            'Psychiatrist': {
                'symptoms': [
                    'anxiety', 'depression', 'mood_swings',
                    'loss of interest', 'social withdrawal', 'delusions'
                ],
                'priority': 11,
                'combined_symptoms': []
            },
            'General Physician': {
                'symptoms': [
                    'fever', 'fatigue', 'malaise', 'weight_loss',
                    'high_fever', 'mild_fever', 'chills',
                    'weight loss', 'high fever', 'mild fever',
                    'swelled_lymph_nodes', 'muscle_pain', 'weakness',
                    'blurred_and_distorted_vision', 'drying_and_tingling_lips',
                    'extra_marital_contacts', 'pain_behind_the_eyes',
                    'varicose veins', 'swollen legs', 'protruding'
                ],
                'priority': 12,  # Lowest priority - general symptoms
                'combined_symptoms': []
            }
        }
    
    def normalize_text(self, text):
        """Normalize text for matching: lowercase and clean."""
        text = text.lower()
        text = re.sub(r'[_]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_symptoms(self, text):
        """Extract symptoms from text (handles both formats)."""
        # Remove quotes
        text = text.strip('"\'')
        
        # Check if it's comma-separated format
        if ',' in text and not any(char in text for char in '.!?'):
            symptoms = [s.strip() for s in text.split(',')]
        else:
            # Natural language - extract key medical terms
            text_lower = text.lower()
            symptoms = []
            
            # Look for specific medical terms in the text
            for specialist, rules in self.specialist_rules.items():
                for symptom in rules['symptoms']:
                    symptom_pattern = symptom.replace('_', ' ')
                    if symptom_pattern in text_lower:
                        symptoms.append(symptom)
        
        return symptoms
    
    def has_combined_symptoms(self, symptoms, combined_list):
        """Check if the symptoms contain any of the combined symptom patterns."""
        normalized_symptoms = [self.normalize_text(s) for s in symptoms]
        
        for combo in combined_list:
            normalized_combo = [self.normalize_text(c) for c in combo]
            if all(any(nc in ns or ns in nc for ns in normalized_symptoms) 
                   for nc in normalized_combo):
                return True
        return False
    
    def match_symptoms_to_specialist(self, symptoms):
        """Match symptoms to the most appropriate specialist."""
        if not symptoms:
            return 'General Physician'
        
        normalized_symptoms = [self.normalize_text(s) for s in symptoms]
        
        # Score each specialist
        specialist_scores = {}
        
        for specialist, rules in self.specialist_rules.items():
            score = 0
            match_count = 0
            has_combined = False
            
            # Check for combined symptoms (higher weight)
            if self.has_combined_symptoms(symptoms, rules['combined_symptoms']):
                score += 100
                match_count += 2
                has_combined = True
            
            # Skip if this specialist requires combined symptoms and we don't have them
            if rules.get('required_combined', False) and not has_combined:
                continue
            
            # Check individual symptoms
            for symptom_pattern in rules['symptoms']:
                normalized_pattern = self.normalize_text(symptom_pattern)
                for norm_symptom in normalized_symptoms:
                    if normalized_pattern in norm_symptom or norm_symptom in normalized_pattern:
                        score += 10
                        match_count += 1
                        # Special high-priority symptoms
                        if 'blood in sputum' in normalized_pattern or 'rusty sputum' in normalized_pattern:
                            score += 150
                        if 'weakness of one body side' in normalized_pattern:
                            score += 150
                        if 'altered sensorium' in normalized_pattern:
                            score += 100
                        break
            
            if match_count > 0:
                # Adjust score based on priority (lower priority number = higher importance)
                priority_weight = 1000 - (rules['priority'] * 50)
                final_score = score + priority_weight
                specialist_scores[specialist] = (final_score, match_count)
        
        # Return specialist with highest score
        if specialist_scores:
            best_specialist = max(specialist_scores.items(), 
                                 key=lambda x: (x[1][0], x[1][1]))
            return best_specialist[0]
        
        return 'General Physician'
    
    def recommend_doctor(self, symptom_text):
        """Recommend a doctor based on symptom text."""
        symptoms = self.extract_symptoms(symptom_text)
        return self.match_symptoms_to_specialist(symptoms)


def restructure_csv(input_file, output_file):
    """
    Restructure the CSV file:
    - Remove 'label' column
    - Keep only 'text' and 'doctor' columns
    - Correct doctor mappings
    """
    recommender = DoctorRecommender()
    
    # Read the input CSV
    rows = []
    input_row_count = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate required columns exist
            if 'text' not in reader.fieldnames:
                raise ValueError("CSV must contain 'text' column")
            
            for row in reader:
                input_row_count += 1
                symptom_text = row['text']
                doctor = recommender.recommend_doctor(symptom_text)
                
                # Create new row with only text and doctor
                new_row = {
                    'text': symptom_text,
                    'doctor': doctor
                }
                rows.append(new_row)
                
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        return False
    except Exception as e:
        print(f"Error reading input file: {e}")
        return False
    
    # Write to output CSV with only text,doctor columns
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['text', 'doctor']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(rows)
            
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False
    
    output_row_count = len(rows)
    
    print(f"Successfully restructured CSV file!")
    print(f"Input rows:  {input_row_count}")
    print(f"Output rows: {output_row_count}")
    print(f"Columns changed from 'text,label,doctor' to 'text,doctor'")
    
    if input_row_count == output_row_count:
        print("✓ All rows preserved")
    else:
        print(f"⚠ Warning: Row count mismatch!")
    
    return True


if __name__ == '__main__':
    input_file = 'symptom-disease-test-dataset.csv'
    output_file = 'symptom-disease-test-dataset.csv'
    
    restructure_csv(input_file, output_file)
