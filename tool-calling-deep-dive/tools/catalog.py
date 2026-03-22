"""
Product catalog — connected to a real PostgreSQL database.
The tools query the database, not a Python dict.
"""

import json
import psycopg2
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from tools.web_search import web_search, WEB_SEARCH_TOOLS


def _get_connection():
    """Get a database connection using credentials from config."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
    )


def _query(sql, params=None):
    """Run a query and return results as list of dicts."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        columns = [desc[0] for desc in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]
        cur.close()
        return rows
    finally:
        conn.close()


# --- Tool functions (run on YOUR machine, query the database) ---

def search_product(product_name: str) -> str:
    """Search the database by product name."""
    try:
        rows = _query(
            "SELECT name, price, currency, availability, rating, category FROM products WHERE name ILIKE %s",
            [f"%{product_name}%"],
        )
        if rows:
            return json.dumps(rows[0])
        return json.dumps({"error": f"Product '{product_name}' not found in catalog"})
    except Exception as e:
        return json.dumps({"error": f"Database error: {str(e)}"})


def compare_products(product_a: str, product_b: str) -> str:
    """Compare two products side by side."""
    result_a = json.loads(search_product(product_a))
    result_b = json.loads(search_product(product_b))
    return json.dumps({"product_a": result_a, "product_b": result_b})


def check_availability(product_name: str) -> str:
    """Check if a specific product is in stock."""
    try:
        rows = _query(
            "SELECT name, price, availability FROM products WHERE name ILIKE %s",
            [f"%{product_name}%"],
        )
        if rows:
            return json.dumps(rows[0])
        return json.dumps({"error": f"Product '{product_name}' not found"})
    except Exception as e:
        return json.dumps({"error": f"Database error: {str(e)}"})


def get_recommendations(category: str = None, max_budget: float = None) -> str:
    """Get product recommendations filtered by category and/or budget."""
    try:
        sql = "SELECT name, price, currency, availability, rating, category FROM products WHERE availability = 'In Stock'"
        params = []

        if category:
            sql += " AND category = %s"
            params.append(category.lower())

        if max_budget:
            sql += " AND price <= %s"
            params.append(max_budget)

        rows = _query(sql, params)
        if not rows:
            return json.dumps({"message": "No products found matching your criteria"})
        return json.dumps(rows)
    except Exception as e:
        return json.dumps({"error": f"Database error: {str(e)}"})


# --- Tool registry ---

TOOL_FUNCTIONS = {
    "search_product": search_product,
    "compare_products": compare_products,
    "check_availability": check_availability,
    "get_recommendations": get_recommendations,
    "web_search": web_search,
}


def execute_tool(function_name: str, arguments: dict) -> str:
    """Run any tool by name. This is the dispatcher."""
    func = TOOL_FUNCTIONS.get(function_name)
    if func:
        try:
            return func(**arguments)
        except Exception as e:
            return json.dumps({"error": f"Tool '{function_name}' failed: {str(e)}"})
    return json.dumps({"error": f"Unknown tool: {function_name}"})


# --- Tool definitions (sent to LLM in the prompt) ---

# Single tool — used in exercises 02, 03, 04
PRODUCT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_product",
            "description": "Search for a product by name and get its full details including price, availability, and rating",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name of the product to search for",
                    }
                },
                "required": ["product_name"],
            },
        },
    }
]

# All tools — used in exercises 05, 06, 07
ALL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_product",
            "description": "Search for a product by name and get its full details including price, availability, and rating",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name of the product to search for",
                    }
                },
                "required": ["product_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_products",
            "description": "Compare two products side by side to see their prices, ratings, and availability",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_a": {
                        "type": "string",
                        "description": "Name of the first product",
                    },
                    "product_b": {
                        "type": "string",
                        "description": "Name of the second product",
                    },
                },
                "required": ["product_a", "product_b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check if a specific product is currently in stock",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name of the product to check stock for",
                    }
                },
                "required": ["product_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recommendations",
            "description": "Get product recommendations filtered by category (smartphone, laptop, headphones) and/or maximum budget in INR",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Product category: smartphone, laptop, or headphones",
                    },
                    "max_budget": {
                        "type": "number",
                        "description": "Maximum budget in INR",
                    },
                },
                "required": [],
            },
        },
    },
] + WEB_SEARCH_TOOLS
