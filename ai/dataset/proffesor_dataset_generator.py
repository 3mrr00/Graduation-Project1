import pandas as pd
import numpy as np
import os

np.random.seed(42)

# Define 30-minute slots from 08:00 to 13:30 in 24-hour format
time_slots = [f"{hour:02d}:{minute:02d}" for hour in range(8, 14) for minute in [0, 30]]

# Generate professor data
n_professors = 200
professor_data = {
    'availability_day': [],
    'availability_slots': []
}

for _ in range(n_professors):
    # Generate availability_day (2-4 days, Monday-Thursday)
    n_days = np.random.randint(2, 5)
    avail_day = np.zeros(4, dtype=int)
    indices = np.random.choice(4, n_days, replace=False)
    avail_day[indices] = 1
    professor_data['availability_day'].append(''.join(map(str, avail_day)))
    
    # Generate availability_slots (2-4 slots)
    n_slots = np.random.randint(2, 5)
    slots = np.random.choice(time_slots, n_slots, replace=False)
    professor_data['availability_slots'].append(','.join(slots))

# Create DataFrame and save to CSV
professor_df = pd.DataFrame(professor_data)
output_path = '/kaggle/working/professor.csv' if 'KAGGLE_KERNEL_RUN_TYPE' in os.environ else 'professor.csv'
professor_df.to_csv(output_path, index=False)
print(f"Generated {output_path}")
