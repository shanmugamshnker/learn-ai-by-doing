"""
Exercise 03: Why Structured Output Matters
=============================================
Same question, two approaches. See why tool calling needs structured output.

Run: uv run python 03_why_structured_output.py
"""

import json
from config import client, MODEL
from tools.catalog import PRODUCT_TOOLS

QUESTION = "Find the price of Samsung Galaxy S24"


def without_tools():
    """Ask the LLM to give product info as text, then try to use it in code."""
    print("\n--- APPROACH 1: Without Tools (plain text) ---\n")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Be concise."},
            {"role": "user", "content": QUESTION},
        ],
    )

    raw_text = response.choices[0].message.content
    print(f"  LLM returned: {raw_text}\n")

    # Now try to extract the price from this text in code
    print("  Now let's try to use this in code...")
    print("  How do we extract the product name? the price? the availability?")
    print("  We'd have to parse free text — fragile and unreliable.\n")

    try:
        data = json.loads(raw_text)
        print(f"  json.loads() worked: {data}")
    except (json.JSONDecodeError, TypeError):
        print(f"  json.loads(response) → FAILED. It's not valid JSON.")
        print(f"  Your code can't reliably work with this.")


def with_tools():
    """Ask the same question but with a tool definition."""
    print("\n--- APPROACH 2: With Tools (structured output) ---\n")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Be concise."},
            {"role": "user", "content": QUESTION},
        ],
        tools=PRODUCT_TOOLS,
    )

    reply = response.choices[0].message

    if reply.tool_calls:
        tool_call = reply.tool_calls[0]
        func_name = tool_call.function.name
        raw_args = tool_call.function.arguments

        print(f"  LLM returned a tool call:")
        print(f"    function: {func_name}")
        print(f"    arguments: {raw_args}\n")

        try:
            args = json.loads(raw_args)
            print(f"  json.loads(arguments) → SUCCESS")
            print(f"  Parsed cleanly: {args}")
            print(f"  product_name = \"{args['product_name']}\"")
            print(f"\n  Your code can use this directly:")
            print(f"    search_product(product_name=\"{args['product_name']}\")")
        except (json.JSONDecodeError, TypeError):
            print(f"  json.loads() failed — this shouldn't happen with tools.")


while True:
    print("\nWhat would you like to try?")
    print(f"  1) Without tools — plain text response")
    print(f"  2) With tools — structured response")
    print(f"  3) Run both side by side")
    print(f"  q) Quit")

    choice = input("\nChoose [1/2/3/q]: ").strip().lower()

    if choice in ("q", "quit", "exit"):
        break
    elif choice == "1":
        without_tools()
    elif choice == "2":
        with_tools()
    elif choice == "3":
        print(f"\nQuestion: \"{QUESTION}\"")
        without_tools()
        with_tools()
        print("\n--- THE POINT ---")
        print("  Same question. Same LLM. Same model.")
        print("  Without tools → free text, can't parse reliably")
        print("  With tools    → clean JSON, works every time")
    else:
        print("Invalid choice. Pick 1, 2, 3 or q.")
