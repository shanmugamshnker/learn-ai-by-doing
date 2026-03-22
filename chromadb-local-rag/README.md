# ChromaDB Food Search - Learning Semantic Search

A hands-on learning project demonstrating ChromaDB's vector database and semantic search capabilities using a nutrition dataset with 2,225 food items.

## What This Project Does

This project teaches ChromaDB fundamentals through practical examples:
- Load 2,225 food items with nutritional data into ChromaDB
- Perform semantic search (find similar foods by meaning, not just keywords)
- Understand how embeddings work under the hood
- See the complete workflow from query to vector to results

## Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/shanmugamshnker/learn-ai-by-doing.git
cd learn-ai-by-doing/chromadb-local-rag

# Install dependencies (uv will handle everything)
uv sync
```

### Usage

**Step 1: Load the data**
```bash
uv run load_food_data.py
```
This loads all food items into ChromaDB and creates embeddings.

**Step 2: Interactive search**
```bash
uv run query_foods.py
```
Try queries like:
- "healthy low calorie breakfast"
- "high protein foods"
- "chocolate desserts"

**Step 3: Understand the workflow (optional)**
```bash
uv run trace_workflow.py
```
See exactly how ChromaDB converts your query to embeddings and finds results!

## Project Structure

```
chromadb-local-rag/
├── data/                      # Nutrition datasets
│   ├── calories.csv          # 2,225 food items with calories
│   ├── calorie_database.txt  # Text format of food data
│   └── questions_output.txt  # Nutrition Q&A dataset
├── load_food_data.py         # Load data into ChromaDB
├── query_foods.py            # Interactive semantic search
├── trace_workflow.py         # Detailed workflow tracer
└── chroma_db/                # ChromaDB storage (generated)
```

## What You'll Learn

1. **Vector Databases**: How ChromaDB stores and searches embeddings
2. **Semantic Search**: Finding similar items by meaning, not keywords
3. **Embeddings**: How text is converted to 384-dimensional vectors
4. **Distance Metrics**: How similarity is calculated using Euclidean distance
5. **Real-world Application**: Building a searchable food nutrition database

## Example Queries

```python
Query: "high protein breakfast"
Results:
1. Egg White - 52 cal (Protein-rich)
2. Greek Yogurt - 59 cal (Dairy)
3. Turkey Bacon - 120 cal (Meat)

Query: "chocolate dessert"
Results:
1. Chocolate Cake - 371 cal (Dessert)
2. Chocolate Ice Cream - 216 cal (Frozen)
3. Chocolate Brownies - 466 cal (Baked Goods)
```

## Dataset

- **Source**: [Calories in Food Items per 100 grams](https://www.kaggle.com/datasets/kkhandekar/calories-in-food-items-per-100-grams)
- **License**: CC0 Public Domain
- **Size**: 2,225 food items
- **Format**: CSV with categories, calories, and kilojoules

## Technologies

- **ChromaDB**: Vector database for AI applications
- **all-MiniLM-L6-v2**: Sentence transformer embedding model
- **uv**: Fast Python package manager
- **ruff**: Python linter and formatter

## Learning Resources

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Understanding Embeddings](https://www.pinecone.io/learn/vector-embeddings/)
- [Semantic Search Explained](https://www.sbert.net/examples/applications/semantic-search/README.html)

## Contributing

This is a learning project! Feel free to:
- Add more datasets
- Implement filtering by categories
- Add visualization of embeddings
- Create a web interface

## License

MIT License - Feel free to use this for learning!

## Acknowledgments

- Nutrition dataset from Kaggle
- ChromaDB team for the excellent vector database
- Sentence Transformers for the embedding model
