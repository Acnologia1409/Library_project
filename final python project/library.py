# library.py

from book import Book

class Library:
    def _init_(self):
        self.books = []  # list of Book objects

    def add_book(self, title, author, year):
        new_book = Book(title, author, year)
        self.books.append(new_book)

    def show_books(self):
        if not self.books:
            print("\nNo books in the library yet!")
            return

        print("\n--- Library Books ---")
        for i, book in enumerate(self.books, start=1):
            print(f"[{i}] {book}")

    def borrow_book(self, index):
        if 0 <= index < len(self.books):
            return self.books[index].borrow()
        return False

    def return_book(self, index):
        if 0 <= index < len(self.books):
            return self.books[index].return_book()
        return False