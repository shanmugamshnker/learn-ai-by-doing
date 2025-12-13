"""
IIT Bombay Library - Book Catalog
==================================
In-memory book catalog for IIT Bombay Central Library.
Focus: Computer Science, AI/ML, and Advanced Engineering.
"""

from typing import Optional

# IIT Bombay Library Book Catalog
BOOKS = [
    {
        "id": "IITB-001",
        "title": "Introduction to Algorithms",
        "author": "Thomas H. Cormen (CLRS)",
        "genre": "Computer Science",
        "year": 2022,
        "isbn": "978-0262046305",
        "available_copies": 10,
        "total_copies": 20,
        "description": "The definitive guide to algorithms, known as CLRS.",
        "location": "IIT Bombay Central Library"
    },
    {
        "id": "IITB-002",
        "title": "Deep Learning",
        "author": "Ian Goodfellow, Yoshua Bengio",
        "genre": "Artificial Intelligence",
        "year": 2016,
        "isbn": "978-0262035613",
        "available_copies": 5,
        "total_copies": 12,
        "description": "Comprehensive textbook on deep learning fundamentals.",
        "location": "IIT Bombay Central Library"
    },
    {
        "id": "IITB-003",
        "title": "Pattern Recognition and Machine Learning",
        "author": "Christopher Bishop",
        "genre": "Artificial Intelligence",
        "year": 2006,
        "isbn": "978-0387310732",
        "available_copies": 3,
        "total_copies": 8,
        "description": "Classic ML textbook covering Bayesian methods.",
        "location": "IIT Bombay Central Library"
    },
    {
        "id": "IITB-004",
        "title": "Computer Organization and Design",
        "author": "David Patterson & John Hennessy",
        "genre": "Computer Architecture",
        "year": 2020,
        "isbn": "978-0128201091",
        "available_copies": 8,
        "total_copies": 15,
        "description": "RISC-V edition of the classic hardware/software interface book.",
        "location": "IIT Bombay Central Library"
    },
    {
        "id": "IITB-005",
        "title": "Artificial Intelligence: A Modern Approach",
        "author": "Stuart Russell & Peter Norvig",
        "genre": "Artificial Intelligence",
        "year": 2020,
        "isbn": "978-0134610993",
        "available_copies": 6,
        "total_copies": 10,
        "description": "The leading textbook on artificial intelligence.",
        "location": "IIT Bombay Central Library"
    },
    {
        "id": "IITB-006",
        "title": "Database System Concepts",
        "author": "Silberschatz, Korth, Sudarshan",
        "genre": "Computer Science",
        "year": 2019,
        "isbn": "978-0078022159",
        "available_copies": 7,
        "total_copies": 12,
        "description": "Comprehensive database management systems textbook.",
        "location": "IIT Bombay Central Library"
    },
    {
        "id": "IITB-007",
        "title": "Computer Networks",
        "author": "Andrew S. Tanenbaum",
        "genre": "Computer Science",
        "year": 2021,
        "isbn": "978-0132126953",
        "available_copies": 4,
        "total_copies": 10,
        "description": "Classic networking textbook with modern updates.",
        "location": "IIT Bombay Central Library"
    },
    {
        "id": "IITB-008",
        "title": "Reinforcement Learning: An Introduction",
        "author": "Richard Sutton & Andrew Barto",
        "genre": "Artificial Intelligence",
        "year": 2018,
        "isbn": "978-0262039246",
        "available_copies": 2,
        "total_copies": 6,
        "description": "The definitive guide to reinforcement learning.",
        "location": "IIT Bombay Central Library"
    },
    {
        "id": "IITB-009",
        "title": "Operating System Concepts",
        "author": "Abraham Silberschatz",
        "genre": "Computer Science",
        "year": 2018,
        "isbn": "978-1119320913",
        "available_copies": 9,
        "total_copies": 15,
        "description": "The dinosaur book - comprehensive OS textbook.",
        "location": "IIT Bombay Central Library"
    },
    {
        "id": "IITB-010",
        "title": "Natural Language Processing with Python",
        "author": "Steven Bird, Ewan Klein",
        "genre": "Artificial Intelligence",
        "year": 2019,
        "isbn": "978-0596516499",
        "available_copies": 0,
        "total_copies": 5,
        "description": "Practical NLP with NLTK library.",
        "location": "IIT Bombay Central Library"
    },
    {
        "id": "IITB-011",
        "title": "Quantum Computing: An Applied Approach",
        "author": "Jack Hidary",
        "genre": "Quantum Computing",
        "year": 2021,
        "isbn": "978-3030832735",
        "available_copies": 3,
        "total_copies": 4,
        "description": "Practical introduction to quantum computing.",
        "location": "IIT Bombay Central Library"
    },
    {
        "id": "IITB-012",
        "title": "Speech and Language Processing",
        "author": "Dan Jurafsky & James Martin",
        "genre": "Artificial Intelligence",
        "year": 2023,
        "isbn": "978-0131873216",
        "available_copies": 4,
        "total_copies": 7,
        "description": "Comprehensive NLP and speech recognition textbook.",
        "location": "IIT Bombay Central Library"
    },
]


def search_books(query: str) -> list[dict]:
    """Search books by title, author, or genre."""
    query_lower = query.lower()
    results = []
    for book in BOOKS:
        if (query_lower in book["title"].lower() or
            query_lower in book["author"].lower() or
            query_lower in book["genre"].lower()):
            results.append(book)
    return results


def get_book_by_id(book_id: str) -> Optional[dict]:
    """Get a specific book by ID."""
    for book in BOOKS:
        if book["id"] == book_id:
            return book
    return None


def get_book_by_title(title: str) -> Optional[dict]:
    """Get a book by exact or partial title match."""
    title_lower = title.lower()
    for book in BOOKS:
        if title_lower in book["title"].lower():
            return book
    return None


def check_availability(book_id: Optional[str] = None, title: Optional[str] = None) -> dict:
    """Check availability of a book."""
    book = None
    if book_id:
        book = get_book_by_id(book_id)
    elif title:
        book = get_book_by_title(title)

    if not book:
        return {"found": False, "message": "Book not found in IIT Bombay Library catalog."}

    return {
        "found": True,
        "book_id": book["id"],
        "title": book["title"],
        "available": book["available_copies"] > 0,
        "available_copies": book["available_copies"],
        "total_copies": book["total_copies"],
        "location": book["location"]
    }


def get_all_genres() -> list[str]:
    """Get unique list of genres."""
    return list(set(book["genre"] for book in BOOKS))


def get_books_by_genre(genre: str) -> list[dict]:
    """Get all books in a specific genre."""
    return [book for book in BOOKS if book["genre"].lower() == genre.lower()]


def get_available_books() -> list[dict]:
    """Get all books that are currently available."""
    return [book for book in BOOKS if book["available_copies"] > 0]


def get_catalog_stats() -> dict:
    """Get catalog statistics."""
    total_books = len(BOOKS)
    total_copies = sum(book["total_copies"] for book in BOOKS)
    available_copies = sum(book["available_copies"] for book in BOOKS)
    genres = get_all_genres()

    return {
        "library": "IIT Bombay Central Library",
        "total_titles": total_books,
        "total_copies": total_copies,
        "available_copies": available_copies,
        "genres": genres,
        "genre_count": len(genres)
    }
