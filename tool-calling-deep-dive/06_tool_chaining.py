"""
Exercise 06: Tool Chaining
==============================
The LLM calls one tool, reads the result, then decides to call another.
One tool's output feeds into the next decision.

Run: uv run python 06_tool_chaining.py
"""

import json
from config import client, MODEL
from tools.catalog import ALL_TOOLS, execute_tool


def ask(question: str) -> str:
    """Send a question and let the LLM chain as many tool calls as it needs."""

    messages = [
        {"role": "system", "content": "You are a helpful shopping assistant. Be concise. Use tools when needed."},
        {"role": "user", "content": question},
    ]

    round_num = 0

    while True:
        round_num += 1
        print(f"\n  --- API Round {round_num} ---")

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=ALL_TOOLS,
        )

        reply = response.choices[0].message

        # No tool calls — LLM is done, return the final answer
        if not reply.tool_calls:
            print(f"  LLM responded with text (done)")
            return reply.content

        # Process each tool call
        messages.append(reply)

        for tool_call in reply.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)

            print(f"  Tool call: {func_name}({json.dumps(func_args)})")

            result = execute_tool(func_name, func_args)
            print(f"  Result: {result[:100]}{'...' if len(result) > 100 else ''}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        # Loop back — send results to LLM, it may call more tools or give final answer


QUESTIONS = {
    "1": "Find the cheapest smartphone and tell me if it's in stock",
    "2": "Compare the best rated laptop with the best rated smartphone",
    "3": "I have 80000 INR budget. Show me available smartphones and compare the top two",
    "4": "What headphones are available? Compare them and tell me which one to buy",
}

while True:
    print("\nTool chaining — watch the LLM call multiple tools in sequence")
    print("\nWhich question?")
    print("  1) Find cheapest smartphone + check stock")
    print("  2) Compare best laptop vs best smartphone")
    print("  3) Smartphones under 80k + compare top two")
    print("  4) Available headphones + compare + recommend")
    print("  5) Ask your own question")
    print("  q) Quit")

    choice = input("\nChoose [1-5/q]: ").strip().lower()

    if choice in ("q", "quit", "exit"):
        break

    if choice in QUESTIONS:
        print(f"\nQ: {QUESTIONS[choice]}")
        answer = ask(QUESTIONS[choice])
        print(f"\nLLM: {answer}")

    elif choice == "5":
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
