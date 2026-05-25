# main.py

from library import Library


def menu():
    print("""
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
""")


def safe_int(prompt, min_val=None, max_val=None):
    """Safely read an integer with optional range validation."""
    while True:
        try:
            value = int(input(prompt))
            if min_val is not None and value < min_val:
                print(f"  ✗ Must be at least {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"  ✗ Must be at most {max_val}.")
                continue
            return value
        except ValueError:
            print("  ✗ Please enter a valid number.")


def main():
    my_library = Library()  # auto-loads from JSON if available

    while True:
        menu()
        choice = input("Choose an option: ").strip()

        # ── 1. View Books ──────────────────────────────────────
        if choice == "1":
            my_library.show_books()

        # ── 2. Add Book ────────────────────────────────────────
        elif choice == "2":
            print("\n── Add a New Book ──")
            title = input("  Book Title : ").strip()
            if not title:
                print("  ✗ Title cannot be empty.")
                continue
            author = input("  Author     : ").strip()
            if not author:
                print("  ✗ Author cannot be empty.")
                continue
            year = input("  Year       : ").strip()
            genre = input("  Genre (press Enter for 'General'): ").strip() or "General"

            my_library.add_book(title, author, year, genre)
            print(f"\n  ✓ '{title}' added to the library!")

        # ── 3. Delete Book ─────────────────────────────────────
        elif choice == "3":
            my_library.show_books()
            if not my_library.books:
                continue
            index = safe_int("  Book number to delete: ", 1, len(my_library.books)) - 1
            title = my_library.books[index].title
            confirm = input(f"  Delete '{title}'? (y/n): ").strip().lower()
            if confirm == "y":
                my_library.delete_book(index)
                print(f"\n  ✓ '{title}' deleted. (You can undo this!)")
            else:
                print("  Cancelled.")

        # ── 4. Borrow Book ─────────────────────────────────────
        elif choice == "4":
            my_library.show_books()
            if not my_library.books:
                continue
            index = safe_int("  Book number to borrow: ", 1, len(my_library.books)) - 1

            if my_library.borrow_book(index):
                book = my_library.books[index]
                print(f"\n  ✓ '{book.title}' borrowed! Due: {book.due_date[:10]}")
            else:
                print("  ✗ Could not borrow — book may already be borrowed.")

        # ── 5. Return Book ─────────────────────────────────────
        elif choice == "5":
            my_library.show_books()
            if not my_library.books:
                continue
            index = safe_int("  Book number to return: ", 1, len(my_library.books)) - 1

            if my_library.return_book(index):
                print(f"\n  ✓ '{my_library.books[index].title}' returned!")
            else:
                print("  ✗ Could not return — book may not be borrowed.")

        # ── 6. Search Books ────────────────────────────────────
        elif choice == "6":
            query = input("\n🔍 Search for: ").strip()
            if not query:
                print("  ✗ Enter a search query.")
                continue
            results = my_library.search_books(query)
            if results:
                print(f"\n── Found {len(results)} result(s) ──")
                for score, idx, book in results:
                    relevance = int(score * 100)
                    print(f"  [{idx+1:>2}] {book}  (relevance: {relevance}%)")
            else:
                print("  No matches found. Try a different query.")

        # ── 7. Mark as Read / Rate / Review ────────────────────
        elif choice == "7":
            my_library.show_books()
            if not my_library.books:
                continue
            index = safe_int("  Book number to mark as read: ", 1, len(my_library.books)) - 1

            rating_input = input("  Rating (1-5 stars, press Enter to skip): ").strip()
            rating = int(rating_input) if rating_input else None
            if rating is not None and not (1 <= rating <= 5):
                print("  ✗ Rating must be 1-5. Setting to None.")
                rating = None

            notes = input("  Notes/Review (press Enter to skip): ").strip()

            my_library.mark_as_read(index, rating, notes)
            print(f"\n  ✓ '{my_library.books[index].title}' marked as read!")

        # ── 8. View Reading Log ────────────────────────────────
        elif choice == "8":
            my_library.show_reading_log()

        # ── 9. Recommendations ─────────────────────────────────
        elif choice == "9":
            recs = my_library.get_recommendations()
            if recs:
                print("\n╔══════════════════════════════════════════════════════╗")
                print("║           🤖  RECOMMENDED FOR YOU  🤖               ║")
                print("╠══════════════════════════════════════════════════════╣")
                for score, idx, book in recs:
                    print(f"  [{idx+1:>2}] {book.title} by {book.author} [{book.genre}]")
                    print(f"        Match score: {score:.1f}")
                print("╚══════════════════════════════════════════════════════╝")

        # ── 10. Analytics Dashboard ────────────────────────────
        elif choice == "10":
            my_library.show_analytics()

        # ── 11. Check Overdue ──────────────────────────────────
        elif choice == "11":
            my_library.show_overdue()

        # ── 12. Export ─────────────────────────────────────────
        elif choice == "12":
            print("\n── Export Options ──")
            print("  1. Export to CSV")
            print("  2. Export to Text Report")
            print("  3. Both")
            export_choice = input("  Choose: ").strip()
            if export_choice == "1":
                my_library.export_csv()
            elif export_choice == "2":
                my_library.export_report()
            elif export_choice == "3":
                my_library.export_csv()
                my_library.export_report()
            else:
                print("  ✗ Invalid export option.")

        # ── 13. Undo ───────────────────────────────────────────
        elif choice == "13":
            my_library.undo()

        # ── 14. Redo ───────────────────────────────────────────
        elif choice == "14":
            my_library.redo()

        # ── 0. Exit ────────────────────────────────────────────
        elif choice == "0":
            my_library.save_to_file()
            print("\n👋 Goodbye! Your library has been saved.")
            break

        else:
            print("  ✗ Invalid choice, try again!")


if __name__ == "__main__":
    main()