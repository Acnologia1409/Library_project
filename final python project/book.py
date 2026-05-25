# book.py

from datetime import datetime, timedelta


class Book:
    """Represents a book in the library with borrowing, reading, and rating support."""

    BORROW_DURATION_DAYS = 14  # default loan period

    def __init__(self, title, author, year, genre="General"):
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre
        self.borrowed = False
        self.borrowed_date = None
        self.due_date = None
        self.is_read = False
        self.rating = None        # 1-5 stars
        self.notes = ""           # personal review/notes
        self.date_read = None

    # ── Borrowing ──────────────────────────────────────────────

    def borrow(self):
        """Borrow the book. Sets due date 14 days from now."""
        if not self.borrowed:
            self.borrowed = True
            self.borrowed_date = datetime.now().isoformat()
            self.due_date = (datetime.now() + timedelta(days=self.BORROW_DURATION_DAYS)).isoformat()
            return True
        return False

    def return_book(self):
        """Return a borrowed book. Clears borrow/due dates."""
        if self.borrowed:
            self.borrowed = False
            self.borrowed_date = None
            self.due_date = None
            return True
        return False

    def is_overdue(self):
        """Check if the book is past its due date."""
        if self.borrowed and self.due_date:
            return datetime.now() > datetime.fromisoformat(self.due_date)
        return False

    def days_overdue(self):
        """Return how many days overdue, or 0 if not overdue."""
        if self.is_overdue():
            delta = datetime.now() - datetime.fromisoformat(self.due_date)
            return delta.days
        return 0

    # ── Reading Tracker ────────────────────────────────────────

    def mark_as_read(self, rating=None, notes=""):
        """Mark the book as read with an optional rating (1-5) and notes."""
        self.is_read = True
        self.date_read = datetime.now().isoformat()
        if rating is not None:
            self.rating = max(1, min(5, int(rating)))
        if notes:
            self.notes = notes

    # ── Serialization ──────────────────────────────────────────

    def to_dict(self):
        """Convert book to a dictionary for JSON storage."""
        return {
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "genre": self.genre,
            "borrowed": self.borrowed,
            "borrowed_date": self.borrowed_date,
            "due_date": self.due_date,
            "is_read": self.is_read,
            "rating": self.rating,
            "notes": self.notes,
            "date_read": self.date_read,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Book instance from a dictionary (loaded from JSON)."""
        book = cls(
            title=data["title"],
            author=data["author"],
            year=data["year"],
            genre=data.get("genre", "General"),
        )
        book.borrowed = data.get("borrowed", False)
        book.borrowed_date = data.get("borrowed_date")
        book.due_date = data.get("due_date")
        book.is_read = data.get("is_read", False)
        book.rating = data.get("rating")
        book.notes = data.get("notes", "")
        book.date_read = data.get("date_read")
        return book

    # ── Display ────────────────────────────────────────────────

    def __str__(self):
        status = "Borrowed" if self.borrowed else "Available"
        stars = f" {'★' * self.rating}{'☆' * (5 - self.rating)}" if self.rating else ""
        overdue_flag = " ⚠ OVERDUE!" if self.is_overdue() else ""
        read_flag = " ✓Read" if self.is_read else ""
        return f"{self.title} by {self.author} ({self.year}) [{self.genre}] - {status}{read_flag}{stars}{overdue_flag}"

    def __repr__(self):
        return f"Book('{self.title}', '{self.author}', {self.year})"