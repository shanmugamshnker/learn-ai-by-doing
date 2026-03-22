"""
Exercise 05: Multiple Tools
==============================
The LLM now has 4 tools. Watch it pick the right one for each question.

Tools available:
  - search_product:     Find a product by name
  - compare_products:   Compare two products side by side
  - check_availability: Check if a product is in stock
  - get_recommendations: Find products by category/budget

Run: uv run python 05_multiple_tools.py
"""

import json
from config import client, MODEL
from tools.catalog import ALL_TOOLS, execute_tool


def ask(question: str) -> str:
    """Send a question with ALL tools available. LLM picks the right one."""

    messages = [
        {"role": "system", "content": "You are a helpful shopping assistant. Be concise."},
        {"role": "user", "content": question},
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=ALL_TOOLS,
    )

    reply = response.choices[0].message

    # No tool call — LLM answered directly
    if not reply.tool_calls:
        print(f"  Tool used: None (answered directly)")
        return reply.content

    # Handle one or more tool calls
    messages.append(reply)

    for tool_call in reply.tool_calls:
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)

        print(f"  Tool used: {func_name}({json.dumps(func_args)})")

        result = execute_tool(func_name, func_args)

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })

    # Get final answer
    final = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=ALL_TOOLS,
    )
    return final.choices[0].message.content


QUESTIONS = {
    "1": "What is the price of MacBook Air M3?",
    "2": "Compare Samsung Galaxy S24 and iPhone 16",
    "3": "Is AirPods Pro 2 in stock?",
    "4": "Suggest me a laptop under 120000 INR",
    "5": "What is the capital of France?",
}

while True:
    print("\n4 tools available: search | compare | availability | recommendations")
    print("\nWhich question?")
    print("  1) Price of MacBook Air M3           → which tool?")
    print("  2) Compare Samsung S24 vs iPhone 16  → which tool?")
    print("  3) Is AirPods Pro 2 in stock?        → which tool?")
    print("  4) Laptop under 120000 INR           → which tool?")
    print("  5) What is the capital of France?    → which tool?")
    print("  6) Ask your own question")
    print("  q) Quit")

    choice = input("\nChoose [1-6/q]: ").strip().lower()

    if choice in ("q", "quit", "exit"):
        break

    if choice in QUESTIONS:
        print(f"\nQ: {QUESTIONS[choice]}")
        answer = ask(QUESTIONS[choice])
        print(f"\nLLM: {answer}")

    elif choice == "6":
        print()
        while True:
            q = input("You: ").strip()
            if q.lower() in ("quit", "exit", "q", "back"):
                break
            if q:
                answer = ask(q)
                print(f"\nLLM: {answer}\n")

    else:
        print("Invalid choice.")
