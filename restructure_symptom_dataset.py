#!/usr/bin/env python3
"""
Script to restructure symptom-disease-test-dataset.csv
- Removes the 'label' column
- Keeps only 'text' and 'doctor' columns
- Remaps doctors to only the 12 allowed types with correct symptom mappings
"""

import csv
import re


class SymptomDoctorMapper:
    """Maps symptoms to the 12 allowed doctor types."""
    
    ALLOWED_DOCTORS = [
        'General Physician',
        'Gynecologist',
        'Orthopedic',
        'ENT',
        'Ophthalmologist',
        'Dentist',
        'Neurologist',
        'Cardiologist',
        'Gastroenterologist',
        'Pulmonologist',
        'Dermatologist',
        'Psychiatrist'
    ]
    
    def __init__(self):
        """Initialize symptom patterns for each doctor type."""
        self.doctor_rules = {
            'Gastroenterologist': {
                'keywords': [
                    'vomiting', 'abdominal_pain', 'diarrhoea', 'diarrhea', 'constipation',
                    'yellowish_skin', 'nausea', 'loss_of_appetite', 'yellowing_of_eyes',
                    'stomach_pain', 'indigestion', 'acidity', 'ulcers', 'bloody_stool',
                    'internal_itching', 'passage_of_gases', 'fluid_overload',
                    'distention_of_abdomen', 'swelling_of_stomach', 'toxic_look',
                    'belly_pain', 'dark_urine', 'dehydration', 'sunken_eyes',
                    'history_of_alcohol_consumption', 'acute_liver_failure',
                    'stomach_bleeding', 'pain_during_bowel_movements',
                    'pain_in_anal_region', 'irritation_in_anus', 'liver',
                    'digestive', 'bowel', 'burning_micturition', 'bladder_discomfort',
                    'foul_smell_of_urine', 'continuous_feel_of_urine', 'urinary', 'urine'
                ],
                'priority': 3
            },
            'Cardiologist': {
                'keywords': [
                    'chest_pain', 'palpitations', 'fast_heart_rate', 'heart'
                ],
                'combined_required': [
                    ['chest_pain', 'breathlessness'],
                    ['chest_pain', 'sweating'],
                    ['sweating', 'chest_pain']
                ],
                'priority': 1
            },
            'Neurologist': {
                'keywords': [
                    'headache', 'altered_sensorium', 'weakness_of_one_body_side',
                    'spinning_movements', 'loss_of_balance', 'unsteadiness',
                    'dizziness', 'lack_of_concentration', 'visual_disturbances',
                    'blurred_and_distorted_vision',
                    'slurred_speech', 'coma', 'seizures',
                    'alzheimer', 'memory', 'brain'
                ],
                'priority': 2
            },
            'Dermatologist': {
                'keywords': [
                    'skin_rash', 'itching', 'pus_filled_pimples', 'blackheads',
                    'scurring', 'blister', 'red_sore_around_nose', 'yellow_crust_ooze',
                    'skin_peeling', 'dischromic__patches', 'nodal_skin_eruptions',
                    'silver_like_dusting', 'inflammatory_nails', 'small_dents_in_nails',
                    'red_spots_over_body', 'skin', 'rash', 'mosquito', 'bites', 'hive'
                ],
                'priority': 5
            },
            'Pulmonologist': {
                'keywords': [
                    'cough', 'breathlessness', 'phlegm', 'blood_in_sputum',
                    'mucoid_sputum', 'rusty_sputum', 'malaise', 'family_history',
                    'respiratory', 'lung', 'mucus', 'wheezing'
                ],
                'priority': 2
            },
            'Orthopedic': {
                'keywords': [
                    'joint_pain', 'neck_pain', 'knee_pain', 'hip_joint_pain',
                    'swelling_joints', 'painful_walking', 'stiff_neck',
                    'movement_stiffness', 'muscle_weakness', 'back_pain',
                    'weakness_in_limbs', 'muscle_wasting', 'hip_pain'
                ],
                'priority': 6
            },
            'ENT': {
                'keywords': [
                    'continuous_sneezing', 'watering_from_eyes', 'throat_irritation',
                    'sinus_pressure', 'runny_nose', 'congestion', 'loss_of_smell',
                    'patches_in_throat', 'redness_of_eyes',
                    'muscle_wasting', 'extra_marital_contacts', 'throat', 'sinus'
                ],
                'priority': 7
            },
            'General Physician': {
                'keywords': [
                    'fatigue', 'fever', 'high_fever', 'mild_fever', 'chills',
                    'weight_loss', 'restlessness', 'lethargy', 'malaise',
                    'swelled_lymph_nodes', 'muscle_pain', 'weakness',
                    'obesity', 'polyuria', 'excessive_hunger', 'increased_appetite',
                    'irregular_sugar_level', 'cold_hands', 'enlarged_thyroid',
                    'diabetes', 'thyroid', 'varicose', 'veins', 'swollen',
                    'shivering', 'sweating', 'mood_swings', 'depression', 
                    'irritability', 'anxiety', 'legs', 'protruding', 'calf'
                ],
                'priority': 10
            },
            'Gynecologist': {
                'keywords': [
                    'abnormal_menstruation', 'irregular_periods', 'menstruation',
                    'pelvic_pain', 'vaginal'
                ],
                'priority': 4
            },
            'Ophthalmologist': {
                'keywords': [
                    'eye_redness', 'eye_pain', 'vision_problems', 'blurred_vision',
                    'visual_disturbances'
                ],
                'priority': 8
            },
            'Dentist': {
                'keywords': [
                    'ulcers_on_tongue', 'tooth_pain', 'gum', 'mouth_ulcers', 'dental'
                ],
                'priority': 9
            },
            'Psychiatrist': {
                'keywords': [
                    'severe_depression', 'severe_anxiety', 'mood_swings',
                    'mental', 'psychological'
                ],
                'priority': 11
            }
        }
    
    def normalize_text(self, text):
        """Normalize text for matching."""
        text = text.lower()
        text = re.sub(r'[_]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_symptoms(self, text):
        """Extract symptoms from text."""
        text = text.strip('"\'')
        normalized = self.normalize_text(text)
        
        # If comma-separated, return list
        if ',' in text and not any(char in text for char in '.!?'):
            return [s.strip() for s in text.split(',')]
        
        # For natural language, return the whole text
        return [text]
    
    def check_combined_symptoms(self, text_lower, combined_patterns):
        """Check if text contains required combined symptoms."""
        for pattern_set in combined_patterns:
            if all(self.normalize_text(keyword) in text_lower for keyword in pattern_set):
                return True
        return False
    
    def assign_doctor(self, symptom_text):
        """Assign the appropriate doctor based on symptoms."""
        text_lower = self.normalize_text(symptom_text)
        symptoms = self.extract_symptoms(symptom_text)
        
        # PRIORITY RULE 1: Cough + phlegm/sputum + respiratory = Pulmonologist (must check first!)
        if 'cough' in text_lower and \
           ('phlegm' in text_lower or 'sputum' in text_lower or 'blood in sputum' in text_lower or 'blood_in_sputum' in text_lower or 'rusty sputum' in text_lower or 'rusty_sputum' in text_lower or 'mucoid sputum' in text_lower or 'mucoid_sputum' in text_lower):
            return 'Pulmonologist'
        
        # PRIORITY RULE 2: Chest pain + breathlessness/sweating = Cardiologist
        if ('chest pain' in text_lower or 'chest_pain' in text_lower) and \
           ('breathlessness' in text_lower or 'sweating' in text_lower):
            # But not if there's strong respiratory symptoms (cough + sputum)
            if not ('cough' in text_lower and ('phlegm' in text_lower or 'sputum' in text_lower)):
                return 'Cardiologist'
        
        # PRIORITY RULE 3: Yellowish skin + abdominal = Gastroenterologist (liver)
        if ('yellowish skin' in text_lower or 'yellowing of eyes' in text_lower or 'yellowish_skin' in text_lower or 'yellowing_of_eyes' in text_lower) and \
           ('abdominal' in text_lower or 'stomach' in text_lower or 'vomiting' in text_lower or 'nausea' in text_lower):
            return 'Gastroenterologist'
        
        # PRIORITY RULE 4: Cough + phlegm/sputum + breathlessness = Pulmonologist (catch other cases)
        if 'cough' in text_lower and 'breathlessness' in text_lower:
            return 'Pulmonologist'
        
        # PRIORITY RULE 5: Headache + weakness of one body side = Neurologist (stroke)
        if 'headache' in text_lower and \
           ('weakness of one body side' in text_lower or 'weakness_of_one_body_side' in text_lower or 'altered sensorium' in text_lower or 'altered_sensorium' in text_lower):
            return 'Neurologist'
        
        # PRIORITY RULE 5: Continuous sneezing + watering eyes = ENT
        if ('continuous sneezing' in text_lower or 'continuous_sneezing' in text_lower) and \
           ('watering from eyes' in text_lower or 'watering_from_eyes' in text_lower):
            return 'ENT'
        
        # PRIORITY RULE 6: Joint pain + neck pain + stiffness = Orthopedic
        if ('joint pain' in text_lower or 'joint_pain' in text_lower) and \
           (('neck pain' in text_lower or 'neck_pain' in text_lower) or ('stiff' in text_lower)):
            return 'Orthopedic'
        
        # PRIORITY RULE 7: Burning micturition + bladder = Gastroenterologist (urinary)
        if ('burning micturition' in text_lower or 'burning_micturition' in text_lower) and \
           ('bladder' in text_lower or 'urine' in text_lower):
            return 'Gastroenterologist'
        
        # PRIORITY RULE 8: Irregular sugar + polyuria + hunger = General Physician (diabetes)
        if ('irregular sugar' in text_lower or 'irregular_sugar_level' in text_lower) and \
           ('polyuria' in text_lower or 'excessive hunger' in text_lower or 'excessive_hunger' in text_lower):
            return 'General Physician'
        
        # PRIORITY RULE 9: Abnormal menstruation = Gynecologist
        if 'abnormal menstruation' in text_lower or 'abnormal_menstruation' in text_lower:
            return 'Gynecologist'
        
        # PRIORITY RULE 10: Ulcers on tongue + stomach = Gastroenterologist
        if ('ulcers on tongue' in text_lower or 'ulcers_on_tongue' in text_lower) and \
           ('stomach' in text_lower or 'abdominal' in text_lower or 'acidity' in text_lower or 'vomiting' in text_lower):
            return 'Gastroenterologist'
        
        # PRIORITY RULE 12: High fever + skin rash/red spots = Dermatologist
        if ('high fever' in text_lower or 'high_fever' in text_lower) and \
           ('skin rash' in text_lower or 'skin_rash' in text_lower or 'red spots' in text_lower or 'red_spots_over_body' in text_lower or 'blister' in text_lower):
            return 'Dermatologist'
        
        # Varicose veins + swollen legs = General Physician
        if ('veins' in text_lower or 'varicose' in text_lower) and \
           ('swollen' in text_lower or 'legs' in text_lower or 'protruding' in text_lower):
            return 'General Physician'
        
        # PRIORITY RULE 13: Vomiting/diarrhoea/nausea with fever/headache (but no respiratory/cardiac) = likely Gastroenterologist
        if ('vomiting' in text_lower or 'diarrhoea' in text_lower or 'nausea' in text_lower) and \
           ('fever' in text_lower or 'headache' in text_lower) and \
           not ('cough' in text_lower or 'phlegm' in text_lower or 'sputum' in text_lower):
            # But if there's altered_sensorium or spinning, keep Neurologist
            if not ('altered sensorium' in text_lower or 'altered_sensorium' in text_lower or 
                    'spinning' in text_lower or 'weakness of one body side' in text_lower or
                    'weakness_of_one_body_side' in text_lower):
                return 'Gastroenterologist'
        
        # Score each doctor for remaining cases
        doctor_scores = {}
        
        for doctor, rules in self.doctor_rules.items():
            score = 0
            match_count = 0
            
            # Check for combined symptoms (required for Cardiologist)
            combined_patterns = rules.get('combined_required', [])
            if combined_patterns:
                if self.check_combined_symptoms(text_lower, combined_patterns):
                    score += 200  # High weight for combined symptoms
                    match_count += 3
                else:
                    # Cardiologist requires combined symptoms
                    if doctor == 'Cardiologist':
                        continue
            
            # Check individual keywords
            for keyword in rules['keywords']:
                keyword_normalized = self.normalize_text(keyword)
                if keyword_normalized in text_lower:
                    score += 10
                    match_count += 1
            
            # Apply priority weight
            if match_count > 0:
                priority_weight = 1000 - (rules['priority'] * 50)
                final_score = score + priority_weight
                doctor_scores[doctor] = (final_score, match_count)
        
        # Return best match
        if doctor_scores:
            best_doctor = max(doctor_scores.items(), key=lambda x: (x[1][0], x[1][1]))
            return best_doctor[0]
        
        return 'General Physician'


def restructure_csv(input_file, output_file):
    """Restructure the CSV file."""
    mapper = SymptomDoctorMapper()
    
    rows_processed = 0
    rows = []
    
    print(f"Reading {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                symptom_text = row['text']
                doctor = mapper.assign_doctor(symptom_text)
                
                rows.append({
                    'text': symptom_text,
                    'doctor': doctor
                })
                rows_processed += 1
        
        print(f"Processed {rows_processed} rows")
        
        # Write output
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['text', 'doctor'])
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"Output saved to {output_file}")
        print(f"Total rows (excluding header): {len(rows)}")
        
        # Show doctor distribution
        doctor_counts = {}
        for row in rows:
            doctor = row['doctor']
            doctor_counts[doctor] = doctor_counts.get(doctor, 0) + 1
        
        print("\nDoctor assignment distribution:")
        for doctor in sorted(doctor_counts.keys()):
            print(f"  {doctor}: {doctor_counts[doctor]}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    input_file = '/home/runner/work/datasets/datasets/symptom-disease-test-dataset.csv'
    output_file = '/home/runner/work/datasets/datasets/symptom-disease-test-dataset.csv'
    
    restructure_csv(input_file, output_file)
