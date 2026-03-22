"""
Exercise 01: LLM Without Tools
================================
See what happens when you ask an LLM questions it can't handle well.

Run: uv run python 01_without_tools.py
"""

from config import client, MODEL


def ask(question: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Be concise."},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


QUESTIONS = {
    "1": {
        "label": "Product Lookup",
        "question": "Find the current price and availability of Samsung Galaxy S24 on amazon.in",
    },
    "2": {
        "label": "Private Data",
        "question": "Which track should I take from Shan's AI training program if I know basic Python?",
    },
    "3": {
        "label": "Take an Action",
        "question": "Book a cab from Chennai airport to T Nagar for tomorrow 6 AM.",
    },
}

while True:
    print("\nWhat would you like to try?")
    print("  1) Product Lookup — can it check amazon.in?")
    print("  2) Private Data — can it access Shan's training program?")
    print("  3) Take an Action — can it book a cab?")
    print("  4) Ask your own question")
    print("  q) Quit")

    choice = input("\nChoose [1/2/3/4/q]: ").strip().lower()

    if choice in ("q", "quit", "exit"):
        break

    if choice in QUESTIONS:
        item = QUESTIONS[choice]
        print(f"\n[{item['label']}]")
        print(f"Q: {item['question']}")
        print(f"LLM: {ask(item['question'])}")
        if "actual" in item:
            print(f"Actual: {item['actual']}")

    elif choice == "4":
        print()
        while True:
            q = input("You: ").strip()
            if q.lower() in ("quit", "exit", "q", "back"):
                break
            if q:
                print(f"LLM: {ask(q)}\n")

    else:
        print("Invalid choice. Pick 1, 2, 3, 4 or q.")
