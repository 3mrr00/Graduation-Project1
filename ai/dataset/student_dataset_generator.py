import pandas as pd
import numpy as np
import os

np.random.seed(42)

# Define 30-minute slots from 08:00 to 13:30 in 24-hour format
time_slots = [f"{hour:02d}:{minute:02d}" for hour in range(8, 14) for minute in [0, 30]]

# Generate student data
n_students = 2000
student_data = {
    'pre_lecs': [],
    'count': [],
    'post_lec_count': np.random.choice([1, 2], n_students, p=[0.7, 0.3]),
    'empty_day': [],
    'empty_slot': [],
    'is_best_appointment': []
}

for _ in range(n_students):
    # Generate pre_lecs (1-2 days, Monday-Thursday, weekday 0-3)
    n_days = np.random.choice([1, 2], p=[0.6, 0.4])
    pre_lecs = np.zeros(4, dtype=int)
    indices = np.random.choice(4, n_days, replace=False)
    pre_lecs[indices] = 1
    pre_lecs_str = ''.join(map(str, pre_lecs))
    student_data['pre_lecs'].append(pre_lecs_str)
    student_data['count'].append(n_days)
    
    # Generate empty_day (inverse of pre_lecs)
    empty_day = ''.join('1' if c == '0' else '0' for c in pre_lecs_str)
    student_data['empty_day'].append(empty_day)
    
    # Generate empty_slot
    empty_slot = np.random.choice(time_slots)
    student_data['empty_slot'].append(empty_slot)
    
    # Preliminary is_best_appointment
    if n_days == 1 and student_data['post_lec_count'][-1] == 1:
        is_best = np.random.choice([0, 1], p=[0.3, 0.7])
    elif n_days <= 2 and student_data['post_lec_count'][-1] <= 2:
        is_best = np.random.choice([0, 1], p=[0.6, 0.4])
    else:
        is_best = 0
    student_data['is_best_appointment'].append(is_best)

# Create DataFrame and save to CSV
student_df = pd.DataFrame(student_data)
output_path = '/kaggle/working/student.csv' if 'KAGGLE_KERNEL_RUN_TYPE' in os.environ else 'student.csv'
student_df.to_csv(output_path, index=False)
print(f"Generated {output_path}")