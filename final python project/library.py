# library.py

import json
import csv
import os
import copy
from datetime import datetime
from difflib import SequenceMatcher
from collections import Counter

from book import Book


# ══════════════════════════════════════════════════════════════
#  UNDO / REDO  —  Command Pattern
# ══════════════════════════════════════════════════════════════

class Command:
    """Base class for undoable commands (Command Pattern)."""
    def execute(self):
        raise NotImplementedError
    def undo(self):
        raise NotImplementedError
    def description(self):
        return "Unknown action"


class AddBookCommand(Command):
    def __init__(self, library, book):
        self._library = library
        self._book = book

    def execute(self):
        self._library.books.append(self._book)

    def undo(self):
        self._library.books.remove(self._book)

    def description(self):
        return f"Add '{self._book.title}'"


class DeleteBookCommand(Command):
    def __init__(self, library, index):
        self._library = library
        self._index = index
        self._book = None  # saved on execute

    def execute(self):
        self._book = self._library.books.pop(self._index)

    def undo(self):
        self._library.books.insert(self._index, self._book)

    def description(self):
        return f"Delete '{self._book.title}'" if self._book else "Delete book"


class BorrowBookCommand(Command):
    def __init__(self, library, index):
        self._library = library
        self._index = index

    def execute(self):
        self._library.books[self._index].borrow()

    def undo(self):
        self._library.books[self._index].return_book()

    def description(self):
        return f"Borrow '{self._library.books[self._index].title}'"


class ReturnBookCommand(Command):
    def __init__(self, library, index):
        self._library = library
        self._index = index
        self._old_borrowed_date = None
        self._old_due_date = None

    def execute(self):
        book = self._library.books[self._index]
        self._old_borrowed_date = book.borrowed_date
        self._old_due_date = book.due_date
        book.return_book()

    def undo(self):
        book = self._library.books[self._index]
        book.borrowed = True
        book.borrowed_date = self._old_borrowed_date
        book.due_date = self._old_due_date

    def description(self):
        return f"Return '{self._library.books[self._index].title}'"


# ══════════════════════════════════════════════════════════════
#  LIBRARY  —  Main Engine
# ══════════════════════════════════════════════════════════════

class Library:
    DATA_FILE = "library_data.json"

    def __init__(self):
        self.books = []           # list of Book objects
        self._undo_stack = []     # list of executed Commands
        self._redo_stack = []     # list of undone Commands
        self.load_from_file()     # auto-load on startup

    # ── Execute with undo tracking ─────────────────────────────

    def _execute(self, command):
        """Run a command and push it onto the undo stack."""
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()  # new action invalidates redo history
        self.save_to_file()

    def undo(self):
        """Undo the last action."""
        if not self._undo_stack:
            print("\n✗ Nothing to undo.")
            return False
        cmd = self._undo_stack.pop()
        cmd.undo()
        self._redo_stack.append(cmd)
        self.save_to_file()
        print(f"\n↩ Undid: {cmd.description()}")
        return True

    def redo(self):
        """Redo the last undone action."""
        if not self._redo_stack:
            print("\n✗ Nothing to redo.")
            return False
        cmd = self._redo_stack.pop()
        cmd.execute()
        self._undo_stack.append(cmd)
        self.save_to_file()
        print(f"\n↪ Redid: {cmd.description()}")
        return True

    # ── Core CRUD ──────────────────────────────────────────────

    def add_book(self, title, author, year, genre="General"):
        new_book = Book(title, author, year, genre)
        self._execute(AddBookCommand(self, new_book))

    def delete_book(self, index):
        if 0 <= index < len(self.books):
            self._execute(DeleteBookCommand(self, index))
            return True
        return False

    def show_books(self):
        if not self.books:
            print("\n📚 No books in the library yet!")
            return
        print("\n╔══════════════════════════════════════════════════════╗")
        print("║              📚  LIBRARY CATALOG  📚               ║")
        print("╠══════════════════════════════════════════════════════╣")
        for i, book in enumerate(self.books, start=1):
            print(f"  [{i:>2}] {book}")
        print("╚══════════════════════════════════════════════════════╝")

    def borrow_book(self, index):
        if 0 <= index < len(self.books):
            if self.books[index].borrowed:
                return False
            self._execute(BorrowBookCommand(self, index))
            return True
        return False

    def return_book(self, index):
        if 0 <= index < len(self.books):
            if not self.books[index].borrowed:
                return False
            self._execute(ReturnBookCommand(self, index))
            return True
        return False

    # ── Feature 2: Smart Search ────────────────────────────────

    def search_books(self, query):
        """Fuzzy search across title, author, year, and genre.
        Returns a list of (score, index, book) sorted by relevance."""
        query_lower = query.lower()
        results = []

        for i, book in enumerate(self.books):
            best_score = 0.0
            for field in [book.title, book.author, str(book.year), book.genre]:
                field_lower = field.lower()
                # exact substring match gets a bonus
                if query_lower in field_lower:
                    score = 0.8 + 0.2 * (len(query_lower) / len(field_lower))
                else:
                    score = SequenceMatcher(None, query_lower, field_lower).ratio()
                best_score = max(best_score, score)

            if best_score >= 0.4:  # threshold
                results.append((best_score, i, book))

        results.sort(key=lambda x: x[0], reverse=True)
        return results

    # ── Feature 3: Reading Tracker ─────────────────────────────

    def mark_as_read(self, index, rating=None, notes=""):
        if 0 <= index < len(self.books):
            self.books[index].mark_as_read(rating, notes)
            self.save_to_file()
            return True
        return False

    def show_reading_log(self):
        """Display all books the user has read with ratings and notes."""
        read_books = [(i, b) for i, b in enumerate(self.books) if b.is_read]
        if not read_books:
            print("\n📖 You haven't marked any books as read yet.")
            return

        print("\n╔══════════════════════════════════════════════════════╗")
        print("║              📖  READING LOG  📖                   ║")
        print("╠══════════════════════════════════════════════════════╣")
        for i, book in read_books:
            stars = f"{'★' * book.rating}{'☆' * (5 - book.rating)}" if book.rating else "Not rated"
            date_str = book.date_read[:10] if book.date_read else "Unknown"
            print(f"  [{i+1:>2}] {book.title} by {book.author}")
            print(f"        Rating: {stars}  |  Read on: {date_str}")
            if book.notes:
                print(f"        Notes: {book.notes}")
            print()
        print("╚══════════════════════════════════════════════════════╝")

    # ── Feature 4: Recommendation Engine ───────────────────────

    def get_recommendations(self, top_n=5):
        """Recommend unread books based on reading history.
        
        Algorithm:
        - Scores each unread book based on:
          1. Author affinity  — how many books by this author you liked (weighted by rating)
          2. Genre affinity   — how many books in this genre you liked (weighted by rating)
          3. Recency bonus    — recently active genres/authors get a small boost
        """
        read_books = [b for b in self.books if b.is_read]
        unread_books = [(i, b) for i, b in enumerate(self.books) if not b.is_read]

        if not read_books:
            print("\n🤖 Read and rate some books first so I can learn your taste!")
            return []
        if not unread_books:
            print("\n🤖 You've read everything in the library! Add more books.")
            return []

        # Build preference profiles
        author_scores = Counter()
        genre_scores = Counter()
        for book in read_books:
            weight = book.rating if book.rating else 3  # default 3 if unrated
            author_scores[book.author.lower()] += weight
            genre_scores[book.genre.lower()] += weight

        # Score unread books
        recommendations = []
        for idx, book in unread_books:
            score = 0.0
            # Author affinity (heavy weight)
            score += author_scores.get(book.author.lower(), 0) * 3.0
            # Genre affinity
            score += genre_scores.get(book.genre.lower(), 0) * 2.0
            # Small boost for variety — books in less-read genres
            if book.genre.lower() not in genre_scores:
                score += 1.0  # exploration bonus

            recommendations.append((score, idx, book))

        recommendations.sort(key=lambda x: x[0], reverse=True)
        return recommendations[:top_n]

    # ── Feature 5: Analytics Dashboard ─────────────────────────

    def show_analytics(self):
        """Print a rich ASCII analytics dashboard."""
        total = len(self.books)
        if total == 0:
            print("\n📊 No books to analyze yet!")
            return

        borrowed_count = sum(1 for b in self.books if b.borrowed)
        available_count = total - borrowed_count
        read_count = sum(1 for b in self.books if b.is_read)
        rated_books = [b for b in self.books if b.rating is not None]
        avg_rating = sum(b.rating for b in rated_books) / len(rated_books) if rated_books else 0
        overdue_count = sum(1 for b in self.books if b.is_overdue())

        # Author frequency
        author_counts = Counter(b.author for b in self.books)
        top_author = author_counts.most_common(1)[0] if author_counts else ("N/A", 0)

        # Genre distribution
        genre_counts = Counter(b.genre for b in self.books)

        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                 📊  LIBRARY ANALYTICS  📊                  ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print(f"║  Total Books      : {total:<6}                                  ║")
        print(f"║  Available        : {available_count:<6}  Borrowed : {borrowed_count:<6}              ║")
        print(f"║  Read             : {read_count:<6}  Unread   : {total - read_count:<6}              ║")
        print(f"║  Overdue          : {overdue_count:<6}                                  ║")
        print(f"║  Average Rating   : {'★' * round(avg_rating)}{'☆' * (5 - round(avg_rating))} ({avg_rating:.1f}/5)                    ║")
        print(f"║  Top Author       : {top_author[0][:25]:<25} ({top_author[1]} books)     ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print("║  GENRE DISTRIBUTION                                        ║")
        print("╠══════════════════════════════════════════════════════════════╣")

        max_bar = 30
        max_count = max(genre_counts.values()) if genre_counts else 1
        for genre, count in genre_counts.most_common():
            bar_len = int((count / max_count) * max_bar)
            bar = "█" * bar_len
            label = genre[:15].ljust(15)
            print(f"║  {label} {bar} {count:>3}                   ║")

        print("╚══════════════════════════════════════════════════════════════╝")

    # ── Feature 6: Overdue Tracking ────────────────────────────

    def get_overdue_books(self):
        """Return list of (index, book) for all overdue books."""
        return [(i, b) for i, b in enumerate(self.books) if b.is_overdue()]

    def show_overdue(self):
        """Display all overdue books with days late."""
        overdue = self.get_overdue_books()
        if not overdue:
            print("\n✓ No overdue books. Everything is on time!")
            return

        print("\n╔══════════════════════════════════════════════════════╗")
        print("║            ⚠  OVERDUE BOOKS  ⚠                    ║")
        print("╠══════════════════════════════════════════════════════╣")
        for idx, book in overdue:
            days = book.days_overdue()
            due = book.due_date[:10] if book.due_date else "?"
            print(f"  [{idx+1:>2}] {book.title}")
            print(f"        Due: {due}  |  {days} day(s) late!")
            print()
        print("╚══════════════════════════════════════════════════════╝")

    # ── Feature 7: Export ──────────────────────────────────────

    def export_csv(self, filename="library_export.csv"):
        """Export the library catalog to a CSV file."""
        if not self.books:
            print("\n✗ No books to export.")
            return

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Title", "Author", "Year", "Genre", "Status",
                "Due Date", "Read", "Rating", "Notes", "Date Read"
            ])
            for book in self.books:
                writer.writerow([
                    book.title,
                    book.author,
                    book.year,
                    book.genre,
                    "Borrowed" if book.borrowed else "Available",
                    book.due_date[:10] if book.due_date else "",
                    "Yes" if book.is_read else "No",
                    book.rating if book.rating else "",
                    book.notes,
                    book.date_read[:10] if book.date_read else "",
                ])

        print(f"\n✓ Exported {len(self.books)} books to '{filename}'")

    def export_report(self, filename="library_report.txt"):
        """Export a formatted text report of the library."""
        if not self.books:
            print("\n✗ No books to export.")
            return

        lines = []
        lines.append("=" * 60)
        lines.append("           LIBRARY REPORT")
        lines.append(f"           Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 60)
        lines.append("")

        for i, book in enumerate(self.books, start=1):
            stars = f"{'★' * book.rating}{'☆' * (5 - book.rating)}" if book.rating else "Not rated"
            status = "Borrowed" if book.borrowed else "Available"
            lines.append(f"[{i}] {book.title}")
            lines.append(f"    Author : {book.author}")
            lines.append(f"    Year   : {book.year}")
            lines.append(f"    Genre  : {book.genre}")
            lines.append(f"    Status : {status}")
            if book.borrowed and book.due_date:
                lines.append(f"    Due    : {book.due_date[:10]}")
                if book.is_overdue():
                    lines.append(f"    ⚠ OVERDUE by {book.days_overdue()} day(s)!")
            lines.append(f"    Read   : {'Yes' if book.is_read else 'No'}")
            if book.is_read:
                lines.append(f"    Rating : {stars}")
                if book.notes:
                    lines.append(f"    Notes  : {book.notes}")
            lines.append("")

        # Summary section
        lines.append("-" * 60)
        lines.append("SUMMARY")
        lines.append(f"  Total Books     : {len(self.books)}")
        lines.append(f"  Available       : {sum(1 for b in self.books if not b.borrowed)}")
        lines.append(f"  Borrowed        : {sum(1 for b in self.books if b.borrowed)}")
        lines.append(f"  Read            : {sum(1 for b in self.books if b.is_read)}")
        lines.append(f"  Overdue         : {sum(1 for b in self.books if b.is_overdue())}")
        lines.append("=" * 60)

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"\n✓ Report saved to '{filename}'")

    # ── Persistence ────────────────────────────────────────────

    def save_to_file(self):
        """Save the entire library to a JSON file."""
        data = [book.to_dict() for book in self.books]
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_from_file(self):
        """Load the library from a JSON file if it exists."""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.books = [Book.from_dict(d) for d in data]
                print(f"📂 Loaded {len(self.books)} book(s) from saved data.")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"⚠ Could not load saved data: {e}")
                self.books = []