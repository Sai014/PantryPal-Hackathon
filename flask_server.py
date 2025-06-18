from flask import Flask, request, render_template, redirect, url_for, flash
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import numpy as np
import os
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, template_folder='templates')
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def extract_quantity(value):
    try:
        quantity, unit = value.split(' x ')
        numeric_part = ''.join(filter(str.isdigit, unit))
        unit_part = ''.join(filter(str.isalpha, unit))
        if not numeric_part:
            return 0, unit_part
        return int(quantity) * float(numeric_part), unit_part
    except Exception:
        return 0, ""

def run_prediction(sales_path, menu_path):
    # Load data
    sales_data = pd.read_csv(sales_path)
    menu_data = pd.read_csv(menu_path)
    
    sales_data['date'] = pd.to_datetime(sales_data['date'])
    sales_data['day_of_week'] = sales_data['date'].dt.weekday
    
    label_encoders = {}
    for feature in ['item_name', 'item_type']:
        le = LabelEncoder()
        sales_data[feature] = le.fit_transform(sales_data[feature])
        label_encoders[feature] = le
    
    features = ['item_name', 'item_type', 'day_of_week', 'is_weekend', 'is_festival']
    target = 'quantity'
    
    X = sales_data[features]
    y = sales_data[target]
    
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = keras.Sequential([
        keras.layers.Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    model.fit(X_train, y_train, epochs=10, batch_size=16, validation_data=(X_test, y_test))

    selected_day = 2
    unique_items = sales_data[['item_name', 'item_type']].drop_duplicates()
    day_inputs = unique_items.copy()
    day_inputs['day_of_week'] = selected_day
    day_inputs['is_weekend'] = 1 if selected_day in [5, 6] else 0
    day_inputs['is_festival'] = 0
    day_inputs_scaled = scaler.transform(day_inputs)
    predicted_sales = model.predict(day_inputs_scaled)
    predicted_sales = np.round(predicted_sales).astype(int).flatten()
    day_inputs['item_name'] = label_encoders['item_name'].inverse_transform(day_inputs['item_name'])
    day_inputs['predicted_quantity'] = predicted_sales
    sales_output = day_inputs[['item_name', 'predicted_quantity']]
    
    menu_data.rename(columns={'Food Item': 'item_name'}, inplace=True)
    merged_data = sales_output.merge(menu_data, on='item_name', how='left')
    merged_data['required_raw_material'] = merged_data['predicted_quantity'].astype(str) + ' x ' + merged_data['Quantity']
    
    raw_material_totals = defaultdict(lambda: defaultdict(float))
    for _, row in merged_data.iterrows():
        total_quantity, unit = extract_quantity(row['required_raw_material'])
        if row['Raw Material'] and unit:
            raw_material_totals[row['Raw Material']][unit] += total_quantity

    formatted_totals = []
    for material, unit_data in raw_material_totals.items():
        formatted_totals.append({
            'Raw Material': material,
            'Total Quantity Needed': ', '.join(f"{qty} {unit}" for unit, qty in unit_data.items())
        })
    
    return pd.DataFrame(formatted_totals)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    logging.debug('Accessing home page')
    if request.method == 'POST':
        sales_file = request.files.get('sales')
        menu_file = request.files.get('menu')

        if not sales_file or not menu_file:
            flash('Please upload both CSV files.')
            return redirect(url_for('upload_file'))

        sales_path = os.path.join(app.config['UPLOAD_FOLDER'], sales_file.filename)
        menu_path = os.path.join(app.config['UPLOAD_FOLDER'], menu_file.filename)
        sales_file.save(sales_path)
        menu_file.save(menu_path)

        results = run_prediction(sales_path, menu_path)
        logging.debug('Rendering results')
        return render_template('results.html', tables=[results.to_html(classes='data')], titles=results.columns.values)

    logging.debug('Rendering upload form')
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(port = 5500,debug=True)