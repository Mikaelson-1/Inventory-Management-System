import sqlite3
from datetime import datetime
import random
import time

DB_NAME = "Jimohigbayilolatraffic.db"

# Nigerian cities list
NIGERIAN_CITIES = [
    "Lagos", "Abuja", "Kano", "Port Harcourt", "Ibadan",
    "Benin City", "Enugu", "Maiduguri", "Jos", "Akure",
    "Abeokuta", "Owerri", "Calabar", "Kaduna", "Ilorin",
    "Zaria", "Uyo", "Warri", "Bauchi", "Makurdi",
    "Yola", "Sokoto", "Gombe", "Onitsha", "Asaba",
    "Ado-Ekiti", "Osogbo", "Lokoja", "Minna", "Katsina",
    "Jalingo", "Damaturu", "Gusau", "Birnin Kebbi", "Ikeja",
    "Eket", "Ikot Ekpene", "Okene", "Nsukka", "Ife",
    "Ijebu Ode", "Owo", "Kontagora", "Bida", "Keffi",
    "Funtua", "Oshogbo", "Sapele", "Gboko", "Mubi", "iworoko"
]


# Create table if not exists
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            city TEXT,
            temperature REAL,
            rain_chance REAL
        )
    ''')
    conn.commit()
    conn.close()

# Simulate scraping: generate random weather data for each city
def scrape_and_save():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    for city in NIGERIAN_CITIES:
        temp = round(random.uniform(24, 34), 2)  # °C
        rain_chance = round(random.uniform(0, 100), 2)  # %
        
        c.execute("INSERT INTO weather (timestamp, city, temperature, rain_chance) VALUES (?, ?, ?, ?)",
                  (timestamp, city, temp, rain_chance))
        print(f"Saved {city} at {timestamp}: Temp={temp}°C, Rain chance={rain_chance}%")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    while True:
        scrape_and_save()
        time.sleep(120)  # every 2 minutes