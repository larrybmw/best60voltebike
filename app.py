from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

FIELDNAMES = [
    'Model', 'Category', 'Voltage', 'Peak_Watts', 'Torque_Nm', 
    'Battery_Wh', 'Cooling', 'Tire_Spec', 'Waterproofing', 
    'Uphill_Climbing_Limit', 'Support_QC_Rating', 'Price', 'Manufacturer_URL'
]

def load_csv(filename):
    data = []
    if os.path.exists(filename):
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    return data

@app.route('/')
def home():
    fleet = load_csv('master_fleet_db.csv')
    inbox = load_csv('staging_inbox.csv')
    return render_template('index.html', fleet=fleet, inbox=inbox)

@app.route('/add', methods=['POST'])
def add_bike():
    new_bike = {field: request.form.get(field) for field in FIELDNAMES}
    with open('master_fleet_db.csv', mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(new_bike)
    return redirect(url_for('home'))

@app.route('/approve/<int:index>', methods=['POST'])
def approve_bike(index):
    inbox = load_csv('staging_inbox.csv')
    if 0 <= index < len(inbox):
        approved = inbox.pop(index)
        
        with open('master_fleet_db.csv', mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writerow(approved)
            
        with open('staging_inbox.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(inbox)
            
    return redirect(url_for('home'))

@app.route('/discard/<int:index>', methods=['POST'])
def discard_bike(index):
    inbox = load_csv('staging_inbox.csv')
    if 0 <= index < len(inbox):
        inbox.pop(index)
        with open('staging_inbox.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(inbox)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)