# main.py

from library import Library

def menu():
    print("""
========= LIBRARY MENU =========
1. View Books
2. Add Book
3. Borrow Book
4. Return Book
5. Exit
================================
""")

def main():
    my_library = Library()  # create Library object
    
    while True:
        menu()
        choice = input("Choose an option: ")

        if choice == "1":
            my_library.show_books()

        elif choice == "2":
            title = input("Book Title: ")
            author = input("Author: ")
            year = input("Year: ")

            my_library.add_book(title, author, year)
            print("Book added!")

        elif choice == "3":
            my_library.show_books()
            index = int(input("Book number to borrow: ")) - 1

            if my_library.borrow_book(index):
                print("Book borrowed!")
            else:
                print("Could not borrow the book.")

        elif choice == "4":
            my_library.show_books()
            index = int(input("Book number to return: ")) - 1

            if my_library.return_book(index):
                print("Book returned!")
            else:
                print("Could not return the book.")

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice, try again!")

if _name_ == "_main_":
    main()