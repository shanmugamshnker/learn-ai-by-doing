import chromadb
import csv

print("=" * 60)
print("Loading Real Food Data into ChromaDB")
print("=" * 60 + "\n")

# Step 1: Create ChromaDB client
print("Step 1: Creating ChromaDB client...")
client = chromadb.PersistentClient(path="./chroma_db")
print("✓ Client created!\n")

# Step 2: Create collection for food data
print("Step 2: Creating collection...")
collection = client.get_or_create_collection(
    name="nutrition_foods", metadata={"description": "Food calorie database"}
)
print("✓ Collection 'nutrition_foods' ready!")
print(f"✓ Current documents: {collection.count()}\n")

# Step 3: Read the CSV file
print("Step 3: Reading calories.csv file...")
csv_path = "./data/calories.csv"

documents = []
metadatas = []
ids = []

with open(csv_path, "r") as file:
    csv_reader = csv.DictReader(file)
    for idx, row in enumerate(csv_reader):
        # Create a text description for each food
        food_text = f"{row['FoodItem']} is a {row['FoodCategory']} with {row['Cals_per100grams']} per 100 grams"

        documents.append(food_text)
        metadatas.append(
            {
                "food": row["FoodItem"],
                "category": row["FoodCategory"],
                "calories": row["Cals_per100grams"],
                "kilojoules": row["KJ_per100grams"],
            }
        )
        ids.append(f"food_{idx:04d}")

print(f"✓ Read {len(documents)} food items from CSV\n")

# Step 4: Add all documents to ChromaDB
print("Step 4: Adding food items to ChromaDB...")
print("(This might take a moment as ChromaDB generates embeddings...)")

# Add in batches for better performance
batch_size = 100
for i in range(0, len(documents), batch_size):
    batch_docs = documents[i : i + batch_size]
    batch_meta = metadatas[i : i + batch_size]
    batch_ids = ids[i : i + batch_size]

    collection.add(documents=batch_docs, metadatas=batch_meta, ids=batch_ids)
    print(f"  Added {min(i + batch_size, len(documents))}/{len(documents)} items...")

print("\n✓ All food items added!")
print(f"✓ Total documents in collection: {collection.count()}\n")

print("=" * 60)
print("SUCCESS! Your food database is ready in ChromaDB!")
print("=" * 60)
