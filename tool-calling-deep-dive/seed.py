"""
Seed the database with product catalog.
Run this once after starting the database: uv run python seed.py
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    user=os.getenv("DB_USER", "catalog_user"),
    password=os.getenv("DB_PASSWORD", "catalog_pass"),
    dbname=os.getenv("DB_NAME", "catalog_db"),
)
cur = conn.cursor()

# Create table
cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        currency TEXT DEFAULT 'INR',
        availability TEXT NOT NULL,
        rating REAL NOT NULL,
        category TEXT NOT NULL
    )
""")

# Clear existing data
cur.execute("DELETE FROM products")

# Insert products
products = [
    ("Samsung Galaxy S24", 74999, "INR", "In Stock", 4.5, "smartphone"),
    ("iPhone 16", 79900, "INR", "In Stock", 4.6, "smartphone"),
    ("OnePlus 12", 64999, "INR", "Out of Stock", 4.4, "smartphone"),
    ("Google Pixel 9", 79999, "INR", "In Stock", 4.3, "smartphone"),
    ("MacBook Air M3", 114900, "INR", "In Stock", 4.8, "laptop"),
    ("Dell XPS 15", 149990, "INR", "In Stock", 4.5, "laptop"),
    ("Sony WH-1000XM5", 29990, "INR", "In Stock", 4.7, "headphones"),
    ("AirPods Pro 2", 24900, "INR", "Out of Stock", 4.6, "headphones"),
]

cur.executemany(
    "INSERT INTO products (name, price, currency, availability, rating, category) VALUES (%s, %s, %s, %s, %s, %s)",
    products,
)

conn.commit()
cur.close()
conn.close()

print(f"Seeded {len(products)} products into the database.")
