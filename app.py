import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

CSV_PATH = os.path.join('data', 'master_fleet_db.csv')

ADMIN_IPS = ['127.0.0.1', '::1', 'YOUR_PUBLIC_IP_HERE']

def load_db():
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame(columns=['id', 'brand', 'model', 'voltage', 'peak_watts', 'top_speed_mph', 'price', 'category', 'status', 'source_url'])
    return pd.read_csv(CSV_PATH)

def save_db(df):
    df.to_csv(CSV_PATH, index=False)

def is_admin():
    if session.get('is_admin') == True:
        return True
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if client_ip in ADMIN_IPS:
        return True
    return False

@app.route('/')
def index():
    df = load_db()
    public_df = df[df['status'] != 'Staging Review'] if 'status' in df.columns else df
    
    search_query = request.args.get('q', '').lower()
    category_filter = request.args.get('cat', 'All')
    
    if search_query:
        public_df = public_df[
            public_df['brand'].str.lower().str.contains(search_query, na=False) |
            public_df['model'].str.lower().str.contains(search_query, na=False)
        ]
        
    if category_filter != 'All':
        public_df = public_df[public_df['category'] == category_filter]
        
    bikes = public_df.to_dict(orient='records')
    return render_template('index.html', bikes=bikes, search_query=search_query, category_filter=category_filter)

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
            new_id = int(df['id'].max() + 1) if not df.empty else 1
            new_bike = {
                'id': new_id,
                'brand': request.form.get('brand'),
                'model': request.form.get('model'),
                'voltage': int(request.form.get('voltage', 60)),
                'peak_watts': int(request.form.get('peak_watts', 3000)),
                'top_speed_mph': int(request.form.get('top_speed_mph', 40)),
                'price': float(request.form.get('price', 2500)),
                'category': request.form.get('category', 'E-Bike'),
                'status': 'Active',
                'source_url': request.form.get('source_url', '')
            }
            df = pd.concat([df, pd.DataFrame([new_bike])], ignore_index=True)
            save_db(df)
            return redirect(url_for('admin_dashboard'))
            
        elif action == 'approve_staging':
            bike_id = int(request.form.get('bike_id'))
            df.loc[df['id'] == bike_id, 'status'] = 'Active'
            save_db(df)
            return redirect(url_for('admin_dashboard'))
            
        elif action == 'delete_bike':
            bike_id = int(request.form.get('bike_id'))
            df = df[df['id'] != bike_id]
            save_db(df)
            return redirect(url_for('admin_dashboard'))

    bikes = df.to_dict(orient='records')
    return render_template('admin.html', bikes=bikes, client_ip=request.headers.get('X-Forwarded-For', request.remote_addr))

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)