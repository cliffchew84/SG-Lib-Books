from src.modals.book_avail import BookAvailCreate, BookAvail


def get_newly_available_books(
    old_book_avails: list[BookAvail], new_book_avails: list[BookAvailCreate]
) -> list[BookAvailCreate]:
    """
    Compare new and old book availabilities and return books that have just become available.

    :param new_book_avails: List of new book availabilities.
    :param old_book_avails: List of old book availabilities.
    :return: List of books that have just become available.
    """
    # Create a dictionary for quick lookup of old book availabilities by ItemNo
    old_avail_dict = {book.ItemNo: book for book in old_book_avails}

    newly_available_books: list[BookAvailCreate] = []

    for new_book in new_book_avails:
        old_book = old_avail_dict.get(new_book.ItemNo)
        # Check if the book is newly available or doesn't exist in the old list
        if old_book is None or (
            old_book.StatusDesc != "Available" and new_book.StatusDesc == "Available"
        ):
            newly_available_books.append(new_book)

    return newly_available_books
