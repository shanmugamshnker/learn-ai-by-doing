"""
Exercise 04: Under the Hood
==============================
See the exact messages flowing between your code and the LLM at every step.
This is the protocol that makes tool calling work.

Run: uv run python 04_under_the_hood.py
"""

import json
from config import client, MODEL
from tools.catalog import search_product, PRODUCT_TOOLS


def print_messages(messages, stage):
    """Print the messages array in a readable format."""
    print(f"\n{'='*60}")
    print(f"  STAGE {stage} — messages array ({len(messages)} messages)")
    print(f"{'='*60}")
    for i, msg in enumerate(messages):
        role = msg["role"] if isinstance(msg, dict) else msg.role

        if role == "system":
            content = msg["content"] if isinstance(msg, dict) else msg.content
            print(f"\n  [{i}] role: system")
            print(f"      content: \"{content}\"")

        elif role == "user":
            content = msg["content"] if isinstance(msg, dict) else msg.content
            print(f"\n  [{i}] role: user")
            print(f"      content: \"{content}\"")

        elif role == "assistant":
            if isinstance(msg, dict):
                content = msg.get("content")
                tool_calls = msg.get("tool_calls")
            else:
                content = msg.content
                tool_calls = msg.tool_calls

            print(f"\n  [{i}] role: assistant")
            if tool_calls:
                print(f"      content: None  ← no text! it wants a tool instead")
                for tc in tool_calls:
                    if isinstance(tc, dict):
                        tc_id = tc["id"]
                        tc_name = tc["function"]["name"]
                        tc_args = tc["function"]["arguments"]
                    else:
                        tc_id = tc.id
                        tc_name = tc.function.name
                        tc_args = tc.function.arguments
                    print(f"      tool_calls:")
                    print(f"        id: \"{tc_id}\"")
                    print(f"        function.name: \"{tc_name}\"")
                    print(f"        function.arguments: '{tc_args}'")
            else:
                print(f"      content: \"{content}\"")

        elif role == "tool":
            content = msg["content"] if isinstance(msg, dict) else msg.content
            tc_id = msg["tool_call_id"] if isinstance(msg, dict) else msg.tool_call_id
            print(f"\n  [{i}] role: tool")
            print(f"      tool_call_id: \"{tc_id}\"  ← links to the assistant's request")
            print(f"      content: '{content}'")


def trace_tool_call(question: str):
    """Run a tool call and print every stage of the message flow."""

    messages = [
        {"role": "system", "content": "You are a helpful shopping assistant. Be concise."},
        {"role": "user", "content": question},
    ]

    # Stage 1: What we send to the LLM
    print_messages(messages, stage="1 — WHAT WE SEND")
    input("\n  Press Enter to send to LLM...")

    # Call the LLM
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=PRODUCT_TOOLS,
    )
    reply = response.choices[0]

    # Stage 2: What the LLM sends back
    print(f"\n  finish_reason: \"{reply.finish_reason}\"", end="")
    if reply.finish_reason == "tool_calls":
        print("  ← means 'I want to call a tool, not reply with text'")
    else:
        print()

    messages.append(reply.message)
    print_messages(messages, stage="2 — LLM RESPONSE")

    if not reply.message.tool_calls:
        print("\n  LLM answered directly without using a tool.")
        return

    input("\n  Press Enter to execute the tool...")

    # Stage 3: Execute tool and add result
    tool_call = reply.message.tool_calls[0]
    func_args = json.loads(tool_call.function.arguments)
    result = search_product(**func_args)

    print(f"\n  Executed: search_product({func_args})")
    print(f"  Result: {result}")

    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result,
    })

    print_messages(messages, stage="3 — AFTER ADDING TOOL RESULT")
    input("\n  Press Enter to send back to LLM for final answer...")

    # Stage 4: Final response
    final = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=PRODUCT_TOOLS,
    )
    messages.append(final.choices[0].message)
    print_messages(messages, stage="4 — FINAL (complete conversation)")

    print(f"\n  Final answer: {final.choices[0].message.content}")


QUESTIONS = {
    "1": "Find the price of Samsung Galaxy S24",
    "2": "Is OnePlus 12 available?",
    "3": "Compare iPhone 16 and Samsung Galaxy S24",
}

while True:
    print("\n\nWhat would you like to trace?")
    print("  1) Search Samsung Galaxy S24")
    print("  2) Check OnePlus 12 availability")
    print("  3) Compare iPhone 16 vs Samsung Galaxy S24")
    print("  4) Ask your own question")
    print("  q) Quit")

    choice = input("\nChoose [1/2/3/4/q]: ").strip().lower()

    if choice in ("q", "quit", "exit"):
        break

    if choice in QUESTIONS:
        print(f"\nQ: {QUESTIONS[choice]}")
        trace_tool_call(QUESTIONS[choice])

    elif choice == "4":
        q = input("\nYour question: ").strip()
        if q:
            trace_tool_call(q)

    else:
        print("Invalid choice.")
