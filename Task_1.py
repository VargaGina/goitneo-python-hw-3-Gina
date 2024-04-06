from collections import UserDict, defaultdict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value): # Check if the phone number is a 10-digit string
        if not isinstance(value, str) or len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must be a 10 digit string.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format.")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday=None

    def add_phone_number(self, phone):  # Add a phone number to the record
        self.phones.append(Phone(phone))

    def remove_phone_number(self, phone):  # Delete a phone number from the record
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone_number(self, old_phone, new_phone):  # Edit a phone number 
        for idx, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[idx] = Phone(new_phone)
                break

    def find_phone_number(self, phone):  # Search for a phone number
        for p in self.phones:
            if p.value == phone:
                return p.value
        return None
    
    def add_birthday(self, birthday):
        if self.birthday:
            raise ValueError("Birthday alredy exist.")
        self.birthday=Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
   
    def add_record(self, record):   # Add a record to the address book
        self.data[record.name.value] = record

    def search_record_by_name(self, name): # Search for a record by name in the address book
        return self.data.get(name)

    def delete_record_by_name(self, name): # Delete a record by name from the address book
        if name in self.data:
            del self.data[name]
        else:
            print(f"Record with name {name}, not found.")

    def get_birthdays_per_week(self, users):
        birthdays = defaultdict(list)

        # Fetch today's date
        today = datetime.today().date()

        # Iterate through each user
        for user in users:
            name = user.name.value
            birthday = user.birthday.value
            
            # Convert birthday to a datetime object
            birthday_date = datetime.strptime(birthday, '%d.%m.%Y').date()

            # Calculate the birthday for this year
            birthday_this_year = birthday_date.replace(year=today.year)

            # Check if the birthday has occurred this year
            if birthday_this_year < today:
                # If yes, consider the date for the following year
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            # Calculate the difference between the birthday and the current day
            delta_days = (birthday_this_year - today).days

            # Calculate the week day
            birthday_day = (today + timedelta(days=delta_days)).strftime('%A')

            if 0 <= delta_days < 7:
                # if birthday on weekend, move to Monday
                if birthday_day in ['Saturday', 'Sunday']:
                    birthday_day = 'Monday'

                birthdays[birthday_day].append(name)

        return birthdays
        
        



def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):  # Decorator to handle input errors and exceptions
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            return str(ve)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Please provide all required arguments."
        except Exception as e:
            return f"An error ocurred: {str(e)}"
        

    return inner


@input_error
def add_contact(args, address_book):  # Handler function to add a new contact
    if len(args)!=2:
        raise IndexError("Please provide all required arguments.")
    name, phone = args
    record=Record(name)
    record.add_phone_number(phone)
    address_book.add_record(record)
    return "Contact added."

@input_error
def change_contact(args, address_book):  # Handler function to change an existing contact's phone number
    if len(args)!=2:
        raise IndexError("Pleas provide name and new phone number")
    name, new_phone=args
    record=address_book.search_record_by_name(name)
    if not record:
        raise KeyError("Contact not found.")
    record.remove_phone_number(record.phones[0].value)
    record.add_phone_number(new_phone)
    
    return f"Phone number for {name} is updated to {new_phone}"
   

@input_error
def display_contact(args, address_book):  # Handler function to display phone number of a contact
    if len(args)!=1:
        raise IndexError("Please provide the name of the contact")
    name=args[0]
    record=address_book.search_record_by_name(name)
    if not record:
        raise KeyError("contact not found")
    return f"Phone number for {name} is {record.phones[0]}"

@input_error
def add_birthday(args,address_book):
    if len(args)!=2:
        raise IndexError("Please provide name an birthday")
    name, birthday=args
    record=address_book.search_record_by_name(name)
    if not record:
        raise KeyError("Contact not found.")
    record.add_birthday(birthday)
    return f"Birthday added for {name}"

@input_error
def show_birthday(args, address_book):
    if len(args) != 1:
        raise IndexError("Please provide the name of the contact.")
    name = args[0]
    record = address_book.search_record_by_name(name)
    if not record:
        raise KeyError("Contact not found.")
    if not record.birthday:
        return f"No birthday found for {name}."
    return f"Birthday for {name} is {record.birthday.value}."

def birthdays(address_book):
    users = address_book.data.values()
    upcoming_birthdays = address_book.get_birthdays_per_week(users)
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    output = "Upcoming birthdays:\n"
    for day, names in upcoming_birthdays.items():
        output += f"{day}: {', '.join(names)}\n"
    return output
    
    
def display_all(address_book):  # Function to display all contacts and their phone numbers
    if not address_book:
        return "No contacts found."
    output=""
    for record in address_book.values():
        output+= f"{record}\n"
    return output
    
def main():   # Main function to execute the contact
    address_book =AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, address_book))
        elif command=="change":
            print (change_contact(args, address_book))
        elif command=="phone":
            print(display_contact(args, address_book))
        elif command=="all":
            print(display_all(address_book))
        elif command=="add_birthday":
            print(add_birthday(args, address_book))
        elif command=="show_birthday":
            print(show_birthday(args, address_book))
        elif command=="birthdays":
            print(birthdays(address_book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()

