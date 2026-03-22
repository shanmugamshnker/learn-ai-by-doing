"""
Exercise 02: First Tool Call
==============================
Same kind of question from Exercise 01, but now the LLM has a tool.
Watch what changes.

Run: uv run python 02_first_tool_call.py
"""

import json
from config import client, MODEL
from tools.catalog import search_product, PRODUCT_TOOLS


def ask_with_tool(question: str) -> str:
    """Send a question to the LLM WITH the product search tool available."""

    messages = [
        {"role": "system", "content": "You are a helpful shopping assistant. Be concise."},
        {"role": "user", "content": question},
    ]

    # Step 1: Send question + tool definition to the LLM
    print("  [Step 1] Sending question to LLM (with search_product tool available)...")
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=PRODUCT_TOOLS,
    )

    reply = response.choices[0].message

    # Step 2: Check if the LLM wants to call a tool
    if reply.tool_calls:
        tool_call = reply.tool_calls[0]
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)

        print(f"  [Step 2] LLM wants to call: {func_name}({func_args})")

        # Step 3: WE run the function (not the LLM!)
        result = search_product(**func_args)
        print(f"  [Step 3] Tool returned: {result}")

        # Step 4: Send the tool result back to the LLM
        messages.append(reply)  # add the assistant's tool_call message
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })

        print("  [Step 4] Sending result back to LLM for final answer...")
        final_response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=PRODUCT_TOOLS,
        )
        return final_response.choices[0].message.content

    # If the LLM didn't use a tool, just return its text response
    return reply.content


QUESTIONS = {
    "1": "Find the current price and availability of Samsung Galaxy S24",
    "2": "Which phone under 70000 INR is available right now?",
    "3": "Compare iPhone 16 and Pixel 9 prices",
}

while True:
    print("\nWhat would you like to try?")
    print("  1) Search for Samsung Galaxy S24")
    print("  2) Find a phone under 70000 INR")
    print("  3) Compare iPhone 16 vs Pixel 9")
    print("  4) Ask your own question (tool available)")
    print("  q) Quit")

    choice = input("\nChoose [1/2/3/4/q]: ").strip().lower()

    if choice in ("q", "quit", "exit"):
        break

    if choice in QUESTIONS:
        print(f"\nQ: {QUESTIONS[choice]}")
        answer = ask_with_tool(QUESTIONS[choice])
        print(f"\nLLM: {answer}")

    elif choice == "4":
        print()
        while True:
            q = input("You: ").strip()
            if q.lower() in ("quit", "exit", "q", "back"):
                break
            if q:
                answer = ask_with_tool(q)
                print(f"\nLLM: {answer}\n")

    else:
        print("Invalid choice. Pick 1, 2, 3, 4 or q.")
