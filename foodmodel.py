import pandas as pd
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import numpy as np
import os
from collections import defaultdict

# Function to get valid file path from user
def get_csv_path(prompt_text):
    while True:
        file_path = input(prompt_text).strip().strip('"')  # Remove any accidental quotes
        if os.path.exists(file_path) and file_path.lower().endswith('.csv'):
            return file_path
        print("Invalid file path! Please enter a valid CSV file.")

# Get file paths dynamically
sales_data_path = get_csv_path("Enter the path for the sales data CSV file: ")
menu_data_path = get_csv_path("Enter the path for the menu data CSV file: ")

# Load datasets
sales_data = pd.read_csv(sales_data_path)
menu_data = pd.read_csv(menu_data_path)

# Convert date column to datetime and extract day of the week
sales_data['date'] = pd.to_datetime(sales_data['date'])
sales_data['day_of_week'] = sales_data['date'].dt.weekday  # Monday=0, Sunday=6

# Encode categorical variables
label_encoders = {}
for feature in ['item_name', 'item_type']:
    le = LabelEncoder()
    sales_data[feature] = le.fit_transform(sales_data[feature])
    label_encoders[feature] = le

# Select features and target
features = ['item_name', 'item_type', 'day_of_week', 'is_weekend', 'is_festival']
target = 'quantity'

X = sales_data[features]
y = sales_data[target]

# Normalize data
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build TensorFlow model
model = keras.Sequential([
    keras.layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(1)  # Regression output
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# Train model
model.fit(X_train, y_train, epochs=100, batch_size=16, validation_data=(X_test, y_test))

# ---- PREDICT SALES FOR A SPECIFIC DAY ---- #

# Choose a specific day (0 = Monday, 6 = Sunday)
selected_day = 2  # Example: 2 = Wednesday (Change as needed)

# Get unique items and types from dataset
unique_items = sales_data[['item_name', 'item_type']].drop_duplicates()

# Create input data for prediction (all items for the selected day)
day_inputs = unique_items.copy()
day_inputs['day_of_week'] = selected_day
day_inputs['is_weekend'] = 1 if selected_day in [5, 6] else 0
day_inputs['is_festival'] = 0  # Default (can be modified based on your dataset)

# Normalize input data
day_inputs_scaled = scaler.transform(day_inputs)

# Predict sales
predicted_sales = model.predict(day_inputs_scaled)
predicted_sales = np.round(predicted_sales).astype(int).flatten()

# Decode item names
day_inputs['item_name'] = label_encoders['item_name'].inverse_transform(day_inputs['item_name'])

# Prepare sales prediction output
day_inputs['predicted_quantity'] = predicted_sales
sales_output = day_inputs[['item_name', 'predicted_quantity']]

# ---- MAP PREDICTED SALES TO RAW MATERIALS ---- #

# Ensure 'Food Item' in menu matches 'item_name' in sales data
menu_data.rename(columns={'Food Item': 'item_name'}, inplace=True)

# Merge predicted sales with menu data
merged_data = sales_output.merge(menu_data, on='item_name', how='left')

# Calculate required raw materials
merged_data['required_raw_material'] = merged_data['predicted_quantity'].astype(str) + ' x ' + merged_data['Quantity']

# Function to extract numeric value and unit
def extract_quantity(value):
    try:
        quantity, unit = value.split(' x ')
        numeric_part = ''.join(filter(str.isdigit, unit))  # Extract numeric part (e.g., '30' from '30g')
        unit_part = ''.join(filter(str.isalpha, unit))  # Extract unit (e.g., 'g' from '30g')

        if not numeric_part:
            return 0, unit_part  # If no numeric value is found, return 0

        return int(quantity) * float(numeric_part), unit_part  # Multiply predicted quantity
    except Exception as e:
        return 0, ""

# Extract total raw material quantities with units
raw_material_totals = defaultdict(lambda: defaultdict(float))

for index, row in merged_data.iterrows():
    total_quantity, unit = extract_quantity(row['required_raw_material'])
    
    if row['Raw Material'] and unit:
        raw_material_totals[row['Raw Material']][unit] += total_quantity

# Format final output
formatted_totals = []
for material, unit_data in raw_material_totals.items():
    formatted_totals.append({
        'Raw Material': material,
        'Total Quantity Needed': ', '.join(f"{qty} {unit}" for unit, qty in unit_data.items())
    })

# Convert to DataFrame
total_raw_materials = pd.DataFrame(formatted_totals)

# Final output
print(f"\nTotal Raw Material Requirements for day {selected_day} (0=Monday, 6=Sunday):\n")
print(total_raw_materials.to_string(index=False))

