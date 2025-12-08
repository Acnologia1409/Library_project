# book.py

class Book:
    def _init_(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year
        self.borrowed = False

    def borrow(self):
        if not self.borrowed:
            self.borrowed = True
            return True
        return False

    def return_book(self):
        if self.borrowed:
            self.borrowed = False
            return True
        return False

    def _str_(self):
        status = "Borrowed" if self.borrowed else "Available"
        return f"{self.title} by {self.author} ({self.year}) - {status}"