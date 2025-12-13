"""
IIT Delhi Library - Book Catalog
=================================
In-memory book catalog for IIT Delhi Central Library.
Focus: Engineering, Technology, and Research books.
"""

from typing import Optional

# IIT Delhi Library Book Catalog
BOOKS = [
    {
        "id": "IITD-001",
        "title": "Engineering Mathematics",
        "author": "B.S. Grewal",
        "genre": "Mathematics",
        "year": 2020,
        "isbn": "978-8174091154",
        "available_copies": 15,
        "total_copies": 25,
        "description": "Higher engineering mathematics covering calculus, differential equations, and linear algebra.",
        "location": "IIT Delhi Central Library"
    },
    {
        "id": "IITD-002",
        "title": "Digital Electronics",
        "author": "Morris Mano",
        "genre": "Electronics",
        "year": 2018,
        "isbn": "978-0134529561",
        "available_copies": 8,
        "total_copies": 12,
        "description": "Comprehensive guide to digital logic and computer design.",
        "location": "IIT Delhi Central Library"
    },
    {
        "id": "IITD-003",
        "title": "Signals and Systems",
        "author": "Alan V. Oppenheim",
        "genre": "Electronics",
        "year": 2015,
        "isbn": "978-0138147570",
        "available_copies": 5,
        "total_copies": 10,
        "description": "Classic textbook on signals and systems analysis.",
        "location": "IIT Delhi Central Library"
    },
    {
        "id": "IITD-004",
        "title": "Data Structures Using C",
        "author": "Reema Thareja",
        "genre": "Computer Science",
        "year": 2019,
        "isbn": "978-0198099307",
        "available_copies": 12,
        "total_copies": 20,
        "description": "Indian author's comprehensive guide to data structures.",
        "location": "IIT Delhi Central Library"
    },
    {
        "id": "IITD-005",
        "title": "Thermodynamics: An Engineering Approach",
        "author": "Yunus Cengel",
        "genre": "Mechanical Engineering",
        "year": 2019,
        "isbn": "978-1259822674",
        "available_copies": 6,
        "total_copies": 15,
        "description": "Standard textbook for thermodynamics in engineering.",
        "location": "IIT Delhi Central Library"
    },
    {
        "id": "IITD-006",
        "title": "Strength of Materials",
        "author": "R.K. Bansal",
        "genre": "Civil Engineering",
        "year": 2018,
        "isbn": "978-8131808146",
        "available_copies": 10,
        "total_copies": 18,
        "description": "Mechanics of solids for engineering students.",
        "location": "IIT Delhi Central Library"
    },
    {
        "id": "IITD-007",
        "title": "Control Systems Engineering",
        "author": "I.J. Nagrath & M. Gopal",
        "genre": "Electronics",
        "year": 2017,
        "isbn": "978-8122434262",
        "available_copies": 4,
        "total_copies": 10,
        "description": "Indian standard textbook on control systems.",
        "location": "IIT Delhi Central Library"
    },
    {
        "id": "IITD-008",
        "title": "Introduction to Electrodynamics",
        "author": "David J. Griffiths",
        "genre": "Physics",
        "year": 2017,
        "isbn": "978-1108420419",
        "available_copies": 7,
        "total_copies": 12,
        "description": "Undergraduate textbook on classical electromagnetism.",
        "location": "IIT Delhi Central Library"
    },
    {
        "id": "IITD-009",
        "title": "Microprocessors and Microcontrollers",
        "author": "Krishna Kant",
        "genre": "Electronics",
        "year": 2016,
        "isbn": "978-8120351424",
        "available_copies": 0,
        "total_copies": 8,
        "description": "Architecture, programming, and interfacing of microprocessors.",
        "location": "IIT Delhi Central Library"
    },
    {
        "id": "IITD-010",
        "title": "Compiler Design",
        "author": "Aho, Lam, Sethi, Ullman",
        "genre": "Computer Science",
        "year": 2006,
        "isbn": "978-0321486813",
        "available_copies": 3,
        "total_copies": 6,
        "description": "The Dragon Book - definitive guide to compiler construction.",
        "location": "IIT Delhi Central Library"
    },
    {
        "id": "IITD-011",
        "title": "Machine Learning",
        "author": "Tom Mitchell",
        "genre": "Artificial Intelligence",
        "year": 1997,
        "isbn": "978-0070428072",
        "available_copies": 2,
        "total_copies": 5,
        "description": "Foundational textbook on machine learning algorithms.",
        "location": "IIT Delhi Central Library"
    },
    {
        "id": "IITD-012",
        "title": "VLSI Design",
        "author": "Kang & Leblebici",
        "genre": "Electronics",
        "year": 2019,
        "isbn": "978-0073380629",
        "available_copies": 5,
        "total_copies": 8,
        "description": "CMOS digital integrated circuits analysis and design.",
        "location": "IIT Delhi Central Library"
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
        return {"found": False, "message": "Book not found in IIT Delhi Library catalog."}

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
        "library": "IIT Delhi Central Library",
        "total_titles": total_books,
        "total_copies": total_copies,
        "available_copies": available_copies,
        "genres": genres,
        "genre_count": len(genres)
    }
