import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

CSV_PATH = os.path.join('data', 'master_fleet_db.csv')
ROOT_CSV_PATH = 'master_fleet_db.csv'

ADMIN_IPS = ['127.0.0.1', '::1', 'YOUR_PUBLIC_IP_HERE']

def load_db():
    path = CSV_PATH if os.path.exists(CSV_PATH) else ROOT_CSV_PATH
    if not os.path.exists(path):
        return pd.DataFrame(columns=['Model', 'Category', 'Voltage', 'Peak_Watts', 'Torque_Nm', 'Battery_Wh', 'Cooling', 'Tire_Spec', 'Waterproofing', 'Uphill_Climbing_Limit', 'Support_QC_Rating', 'Price', 'Manufacturer_URL'])
    df = pd.read_csv(path)
    for col in ['Voltage', 'Peak_Watts', 'Torque_Nm', 'Battery_Wh', 'Price']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce').fillna(0)
    return df

def save_db(df):
    if os.path.exists('data'):
        df.to_csv(CSV_PATH, index=False)
    df.to_csv(ROOT_CSV_PATH, index=False)

def is_admin():
    if session.get('is_admin') == True:
        return True
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if client_ip in ADMIN_IPS:
        return True
    return False

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
        return f"Internal Application Error: {str(e)}", 500

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
    if not is_admin():
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
                'Torque_Nm': float(request.form.get('Torque_Nm', 300)),
                'Battery_Wh': float(request.form.get('Battery_Wh', 3000)),
                'Cooling': request.form.get('Cooling', 'Air/Standard'),
                'Tire_Spec': request.form.get('Tire_Spec', 'Puncture-Resistant'),
                'Waterproofing': request.form.get('Waterproofing', 'IP65'),
                'Uphill_Climbing_Limit': request.form.get('Uphill_Climbing_Limit', 'Strong Climbing'),
                'Support_QC_Rating': request.form.get('Support_QC_Rating', 'Good'),
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
    return render_template('admin.html', bikes=bikes, client_ip=request.headers.get('X-Forwarded-For', request.remote_addr))

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)