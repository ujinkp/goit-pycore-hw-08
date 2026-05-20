import pickle
from collections import UserDict
from datetime import datetime, timedelta

    
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, name):
        super().__init__(name)

class Phone(Field):
    def __init__(self, phone):
        if phone.isdigit() and len(phone) == 10:
            super().__init__(phone)
        else:
             raise ValueError
        
class Birthday(Field):
    def __init__(self, value):
        try:
            date_obj = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(date_obj)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        
    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def find_phone(self,phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
        
    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
        return

    def edit_phone(self, old_phone, new_phone):
        if not self.find_phone(old_phone):
             raise ValueError ("Номер не знайдено")
        new_phone_obj = Phone(new_phone)
        self.remove_phone(old_phone)
        self.phones.append(new_phone_obj)

    def add_birthday(self, birthday_string):
        birthday = Birthday(birthday_string)
        self.birthday = birthday

    def __str__(self):
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self,name):
        self.data.pop(name, None)

    def get_upcoming_birthdays(self):
        current_day = datetime.today().date()
        birthdays = []
    
        for record in self.data.values():
            if record.birthday is None:
                continue
            
            user_birthday = record.birthday.value.replace(year=current_day.year)
            
            if user_birthday < current_day:
                user_birthday = user_birthday.replace(year=current_day.year + 1)      
            
            days_difference = (user_birthday - current_day).days
            if 0 <= days_difference <= 7:
                day_of_week = user_birthday.weekday()
                if day_of_week == 5:
                    user_birthday += timedelta(days=2)
                elif day_of_week == 6:
                    user_birthday += timedelta(days=1)

                birthdays.append({
                    "name": record.name.value,
                    "congratulation_date": user_birthday.strftime("%d.%m.%Y")
                })

        return birthdays      

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e) if str(e) else "Give me name and phone please."
        except IndexError:
            return "Enter user argument."
        except KeyError:
            return "Contact not found."
    return inner

def parse_input(user_input):
    if not user_input.strip():
        return "", []
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    if old_phone:
        record.edit_phone(old_phone, new_phone)

    return "Contact changed."

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    
    if record is None:
        raise KeyError

    return "; ".join(phone.value for phone in record.phones)

@input_error
def show_all_contacts(book: AddressBook):
    if not book.data:
        return "Address book is empty."

    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    if record:
        record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError
    
    if record.birthday is None:
        raise ValueError("Birthday not set.")

    return record.birthday

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays next week."
    return "\n".join(f"{user['name']}: {user['congratulation_date']}" for user in upcoming)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook() 
    
def main():
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all_contacts(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")
    
    save_data(book)

if __name__ == "__main__":
    main()
    