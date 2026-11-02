import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

CSV_PATH = os.path.join('data', 'master_fleet_db.csv')

def load_db():
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame(columns=['Model', 'Category', 'Voltage', 'Peak_Watts', 'Battery_Wh', 'Range_Miles', 'Tire_Spec', 'Charge_Time', 'Waterproofing', 'Thermal_Management', 'Uphill_Climbing', 'Reliability_QC', 'Price', 'Manufacturer_URL'])
    df = pd.read_csv(CSV_PATH)
    for col in ['Voltage', 'Peak_Watts', 'Battery_Wh', 'Price']:
        if col in df.columns:
            df.loc[:, col] = pd.to_numeric(df[col].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce').fillna(0)
    return df

def save_db(df):
    df.to_csv(CSV_PATH, index=False)

@app.route('/')
def index():
    try:
        df = load_db()
        search_query = request.args.get('q', '').lower()
        if search_query:
            df = df[
                df['Model'].astype(str).str.lower().str.contains(search_query, na=False) |
                df['Category'].astype(str).str.lower().str.contains(search_query, na=False)
            ]
        bikes = df.to_dict(orient='records')
        return render_template('index.html', bikes=bikes, search_query=search_query)
    except Exception as e:
        return f"Internal Error: {str(e)}", 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        passcode = request.form.get('passcode')
        if passcode == 'Best60VAdmin2026!':
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid Master Passcode')
    return render_template('admin_login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    df = load_db()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_bike':
            new_bike = {
                'Model': request.form.get('Model', ''),
                'Category': request.form.get('Category', 'E-Bike'),
                'Voltage': float(request.form.get('Voltage', 72)),
                'Peak_Watts': float(request.form.get('Peak_Watts', 8000)),
                'Battery_Wh': float(request.form.get('Battery_Wh', 3000)),
                'Range_Miles': request.form.get('Range_Miles', '40-60 mi'),
                'Tire_Spec': request.form.get('Tire_Spec', 'Tubeless Puncture-Resistant'),
                'Charge_Time': request.form.get('Charge_Time', '5 Hours'),
                'Waterproofing': request.form.get('Waterproofing', 'IP65 Weather-Sealed'),
                'Thermal_Management': request.form.get('Thermal_Management', 'Air/Standard'),
                'Uphill_Climbing': request.form.get('Uphill_Climbing', 'Strong Climbing'),
                'Reliability_QC': request.form.get('Reliability_QC', 'Good'),
                'Price': float(request.form.get('Price', 2999)),
                'Manufacturer_URL': request.form.get('Manufacturer_URL', '')
            }
            df = pd.concat([df, pd.DataFrame([new_bike])], ignore_index=True)
            save_db(df)
            return redirect(url_for('admin_dashboard'))
        elif action == 'delete_bike':
            model_name = request.form.get('model_name')
            df = df[df['Model'] != model_name]
            save_db(df)
            return redirect(url_for('admin_dashboard'))
            
    bikes = df.to_dict(orient='records')
    return render_template('admin.html', bikes=bikes, client_ip=request.remote_addr)

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
