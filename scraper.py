import os
import pandas as pd
from datetime import datetime

CSV_PATH = os.path.join('data', 'master_fleet_db.csv')

def run_fleet_scraper():
    print(f"[{datetime.now()}] Running high-voltage fleet discovery scan...")
    
    new_finds = [
        {
            "id": 99,
            "brand": "Stellar",
            "model": "Apex 72V Pro",
            "voltage": 72,
            "peak_watts": 9000,
            "top_speed_mph": 60,
            "price": 3899,
            "category": "E-Moto",
            "status": "Staging Review",
            "source_url": "https://example.com/stellar-apex"
        }
    ]
    
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        existing_models = df['model'].values
        
        for bike in new_finds:
            if bike['model'] not in existing_models:
                new_row = pd.DataFrame([bike])
                df = pd.concat([df, new_row], ignore_index=True)
                print(f"Discovered new machine: {bike['brand']} {bike['model']}! Added to Staging Inbox.")
        
        df.to_csv(CSV_PATH, index=False)
    else:
        print("Master fleet database not found.")

if __name__ == '__main__':
    run_fleet_scraper()