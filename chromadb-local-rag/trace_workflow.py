"""
DETAILED CHROMADB WORKFLOW TRACER
This script shows exactly how ChromaDB converts queries to embeddings and finds results
"""

import chromadb
import numpy as np
from chromadb.utils import embedding_functions

print("=" * 80)
print("CHROMADB WORKFLOW TRACER - See How It Works Under The Hood")
print("=" * 80 + "\n")

# Step 1: Connect to database
print("STEP 1: Connecting to ChromaDB")
print("-" * 80)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="nutrition_foods")
print(f"✓ Connected to collection: {collection.name}")
print(f"✓ Total documents: {collection.count()}")
print()

# Step 2: Get the embedding function that ChromaDB uses
print("STEP 2: Getting the Embedding Function")
print("-" * 80)
# ChromaDB uses this default embedding function
default_ef = embedding_functions.DefaultEmbeddingFunction()
print("✓ Model: all-MiniLM-L6-v2 (sentence transformer)")
print("✓ Embedding dimension: 384 (each text becomes 384 numbers)")
print()

# Step 3: Get user query
print("STEP 3: Enter Your Query")
print("-" * 80)
query_text = input("🔍 Enter your search query: ").strip()
if not query_text:
    query_text = "pizza"
    print(f"Using default query: '{query_text}'")
print()

# Step 4: Convert query to embedding
print("STEP 4: Converting Query to Embedding (Vector)")
print("-" * 80)
print(f"Query text: '{query_text}'")
print("Converting to embedding vector...")
query_embedding = default_ef([query_text])[0]  # Returns a list, we take first
print("✓ Embedding created!")
print(f"✓ Vector dimension: {len(query_embedding)}")
print(f"✓ First 10 numbers of the embedding: {query_embedding[:10]}")
print(f"✓ Data type: {type(query_embedding)}")
print()

# Step 5: Query ChromaDB
print("STEP 5: Searching Database for Similar Embeddings")
print("-" * 80)
print("ChromaDB will:")
print("  1. Compare your query embedding with ALL 2225 food embeddings")
print("  2. Calculate distance (similarity) for each")
print("  3. Return the closest matches")
print("\nSearching...")
results = collection.query(
    query_texts=[query_text],
    n_results=3,
    include=[
        "documents",
        "metadatas",
        "distances",
        "embeddings",
    ],  # Include embeddings!
)
print("✓ Search complete!")
print()

# Step 6: Show detailed results
print("STEP 6: Analyzing Results")
print("-" * 80)
print("Found top 3 most similar items:\n")

for i, (doc, meta, distance, embedding) in enumerate(
    zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
        results["embeddings"][0],
    ),
    1,
):
    print(f"{'=' * 80}")
    print(f"RESULT #{i}")
    print(f"{'=' * 80}")
    print(f"Food: {meta['food']}")
    print(f"Category: {meta['category']}")
    print(f"Calories: {meta['calories']}")
    print(f"Full document: {doc}")
    print()
    print(f"Distance Score: {distance:.6f}")
    print("  → Lower = more similar (0 = identical)")
    print(
        "  → This measures how 'far apart' the embeddings are in 384-dimensional space"
    )
    print()
    print("Embedding details:")
    print(f"  • Dimension: {len(embedding)}")
    print(f"  • First 10 values: {embedding[:10]}")
    print()

# Step 7: Manual distance calculation (show the math!)
print("=" * 80)
print("STEP 7: Understanding Distance Calculation")
print("=" * 80)
print("ChromaDB uses 'Euclidean Distance' (like measuring straight-line distance)")
print()

# Get the first result's embedding
result_embedding = results["embeddings"][0][0]
reported_distance = results["distances"][0][0]

# Calculate distance manually
query_vec = np.array(query_embedding)
result_vec = np.array(result_embedding)

# Euclidean distance formula: sqrt(sum((a - b)^2))
manual_distance = np.sqrt(np.sum((query_vec - result_vec) ** 2))

print(f"Query embedding: {len(query_vec)} numbers")
print(f"Result embedding: {len(result_vec)} numbers")
print()
print("Distance calculation:")
print("  1. Subtract each number: query[i] - result[i]")
print("  2. Square each difference: (query[i] - result[i])²")
print("  3. Sum all squares: Σ((query[i] - result[i])²)")
print("  4. Take square root: √(sum)")
print()
print(f"ChromaDB reported distance: {reported_distance:.6f}")
print(f"Manually calculated distance: {manual_distance:.6f}")
print(
    f"Match: {'✓ Yes!' if abs(reported_distance - manual_distance) < 0.01 else '✗ No'}"
)
print()

# Step 8: Summary
print("=" * 80)
print("WORKFLOW SUMMARY")
print("=" * 80)
print(f"1. Your query '{query_text}' → Converted to 384 numbers (embedding)")
print(f"2. ChromaDB compared with {collection.count()} food embeddings")
print("3. Calculated distance for each using Euclidean distance formula")
print("4. Sorted by distance (lowest = most similar)")
print("5. Returned top 3 results")
print()
print("This is why 'pizza' finds pizza even if you don't type the exact word!")
print("The embeddings capture MEANING, not just keywords.")
print("=" * 80)
