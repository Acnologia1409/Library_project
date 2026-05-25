# 📚 Library Management System

A feature-rich Python application for managing a personal library — add books, borrow/return them, track your reading, get recommendations, and more.

> **No external dependencies required.** Everything runs on the Python standard library.

---

## ✨ Features

### Core Features
| # | Feature | Description |
|---|---------|-------------|
| 1 | **View Books** | Browse the full library catalog with status indicators |
| 2 | **Add Book** | Add books with title, author, year, and genre |
| 3 | **Delete Book** | Remove books from the library (undo-able!) |
| 4 | **Borrow Book** | Borrow a book — auto-assigns a 14-day due date |
| 5 | **Return Book** | Return a borrowed book and clear the due date |

### 🚀 Advanced Features
| # | Feature | Description |
|---|---------|-------------|
| 6 | **🔍 Smart Search (Fuzzy)** | Search by title, author, year, or genre with fuzzy/partial matching. Typing `"harr"` finds `"Harry Potter"`. Ranked by relevance score. |
| 7 | **📖 Reading Tracker & Notes** | Mark books as read, rate them 1–5 stars, and add personal reviews/notes. Separate from borrowing — this is your personal reading log. |
| 8 | **🤖 Recommendation Engine** | Analyzes your reading history (genres, authors, ratings) and recommends unread books using a weighted scoring algorithm. No ML libraries needed. |
| 9 | **📊 Analytics Dashboard** | ASCII-art dashboard showing total/borrowed/available counts, most popular author, average rating, genre distribution bar chart, and overdue summary. |
| 10 | **⏰ Overdue Tracking** | Auto-assigns 14-day due dates on borrow. Check overdue books to see which are late and by how many days. |
| 11 | **📤 Export (CSV & Text)** | Export the full catalog to CSV (Excel-compatible) or a formatted text report. Includes all metadata — ratings, notes, status, due dates. |
| 12 | **↩️ Undo / Redo** | Stack-based undo/redo system using the **Command Design Pattern**. Accidentally deleted a book? Just undo it. |
| 13 | **💾 JSON Persistence** | Library auto-saves to `library_data.json` on every change and auto-loads on startup. Your data survives between sessions. |

---

## 🛠️ Project Structure

```
Library_project-main/
├── README.md
└── final python project/
    ├── book.py       # Book class — data model with serialization
    ├── library.py    # Library engine — all features & Command Pattern
    └── main.py       # CLI menu — user interface & input handling
```

### File Responsibilities

- **`book.py`** — The `Book` class with fields for title, author, year, genre, borrow status, due date, reading tracker (rating, notes, date read), and JSON serialization (`to_dict()` / `from_dict()`).

- **`library.py`** — The `Library` class and Command Pattern classes (`AddBookCommand`, `DeleteBookCommand`, `BorrowBookCommand`, `ReturnBookCommand`). Contains the search engine, recommendation algorithm, analytics dashboard, overdue checker, export functions, and JSON persistence.

- **`main.py`** — The interactive menu loop with 15 options (including exit), input validation, and safe integer parsing.

---

## 🚀 How to Run

```bash
# Navigate to the project folder
cd "final python project"

# Run the application
python main.py
```

On first launch, if no `library_data.json` exists, you start with an empty library. All changes are auto-saved.

---

## 📋 Menu Options

```
╔══════════════════════════════════════════════════╗
║          📚  LIBRARY MANAGEMENT SYSTEM  📚       ║
╠══════════════════════════════════════════════════╣
║  1.  View All Books                              ║
║  2.  Add Book                                    ║
║  3.  Delete Book                                 ║
║  4.  Borrow Book                                 ║
║  5.  Return Book                                 ║
║  6.  Search Books (Fuzzy)                        ║
║  7.  Mark Book as Read / Rate / Review           ║
║  8.  View Reading Log                            ║
║  9.  Get Recommendations                         ║
║ 10.  Analytics Dashboard                         ║
║ 11.  Check Overdue Books                         ║
║ 12.  Export Library (CSV / Text Report)           ║
║ 13.  Undo Last Action                            ║
║ 14.  Redo Last Action                            ║
║  0.  Exit                                        ║
╚══════════════════════════════════════════════════╝
```

---

## 🔍 How the Smart Search Works

The search engine uses Python's `difflib.SequenceMatcher` for fuzzy matching — no external libraries needed.

1. Your query is compared against every book's title, author, year, and genre.
2. **Exact substring matches** get a high score (0.8–1.0).
3. **Fuzzy matches** are scored by character similarity.
4. Results are filtered (score ≥ 0.4) and sorted by relevance.

**Example:** Searching `"tol"` would match `"Tolkien"` and `"Tolstoy"`.

---

## 🤖 How the Recommendation Engine Works

The recommendation engine uses a **weighted scoring algorithm** (no machine learning):

1. **Author Affinity** — Authors you've rated highly get a 3× weight.
2. **Genre Affinity** — Genres you've read and liked get a 2× weight.
3. **Exploration Bonus** — Unread genres get a small bonus to encourage variety.

The engine scores all unread books and returns the top 5 recommendations.

---

## ↩️ How Undo/Redo Works

Uses the **Command Design Pattern**:

- Every mutating action (add, delete, borrow, return) is wrapped in a `Command` object.
- Executed commands are pushed onto an **undo stack**.
- Undoing pops from the undo stack, reverses the action, and pushes onto a **redo stack**.
- New actions clear the redo stack.

This is a genuine software design pattern rarely seen in student projects.

---

## 💾 Data Persistence

The library saves to `library_data.json` automatically:
- On every add, delete, borrow, return, or read action.
- On exit.

The file is human-readable JSON. Example:

```json
[
  {
    "title": "Harry Potter",
    "author": "J.K. Rowling",
    "year": "1997",
    "genre": "Fantasy",
    "borrowed": false,
    "borrowed_date": null,
    "due_date": null,
    "is_read": true,
    "rating": 5,
    "notes": "A magical journey!",
    "date_read": "2026-05-25"
  }
]
```

---

## 📤 Export Formats

### CSV Export (`library_export.csv`)
Opens in Excel, Google Sheets, or any spreadsheet app. Columns: Title, Author, Year, Genre, Status, Due Date, Read, Rating, Notes, Date Read.

### Text Report (`library_report.txt`)
A formatted text report with a summary section — perfect for printing or sharing.

---

## 🧰 Technologies Used

- **Python 3.6+** (standard library only)
- `json` — data persistence
- `csv` — CSV export
- `datetime` — due dates and overdue tracking
- `difflib` — fuzzy string matching for search
- `collections.Counter` — analytics and recommendation scoring

---

## 📝 License

This project is open source and available for educational purposes.
