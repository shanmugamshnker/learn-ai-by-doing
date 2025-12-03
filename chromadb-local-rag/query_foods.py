import chromadb

print("=" * 60)
print("Interactive Food Search with ChromaDB")
print("=" * 60 + "\n")

# Connect to existing database
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="nutrition_foods")

print(f"✓ Connected to database with {collection.count()} food items\n")

# SEMANTIC SEARCH - This is the magic of ChromaDB!
# It finds similar items based on MEANING, not just keywords

print("Example queries you can try:")
print("  • 'healthy low calorie breakfast'")
print("  • 'high protein foods for muscle building'")
print("  • 'sweet dessert with chocolate'")
print("  • 'foods for weight loss'")
print("  • 'energy boosting snacks'")
print("  • 'vegetarian protein sources'\n")

# Interactive query loop
while True:
    print("=" * 60)
    query = input("🔍 Enter your search query (or 'quit' to exit): ").strip()

    if query.lower() in ["quit", "exit", "q"]:
        print("\n👋 Goodbye!")
        break

    if not query:
        print("❌ Please enter a search query!\n")
        continue

    # Ask how many results they want
    try:
        num_results = input("   How many results? (press Enter for 5): ").strip()
        num_results = int(num_results) if num_results else 5
    except ValueError:
        num_results = 5

    print(f"\n📊 Searching for: '{query}' (top {num_results} results)")
    print("-" * 60)

    # Query ChromaDB
    results = collection.query(query_texts=[query], n_results=num_results)

    # Display results
    for i, (doc, meta, distance) in enumerate(
        zip(results["documents"][0], results["metadatas"][0], results["distances"][0]),
        1,
    ):
        print(f"\n{i}. {meta['food']}")
        print(f"   Category: {meta['category']}")
        print(f"   Calories: {meta['calories']}")
        print(f"   Similarity: {distance:.3f} (lower = more similar)")

    print()
