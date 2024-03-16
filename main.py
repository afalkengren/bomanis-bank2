from typing import Optional, List
from datetime import date, datetime
from account_manager import AccountManager, UserAccount, BankAccount
import opt_helper

def menu_login():
    while True:
        print(f"""
Hello, welcome to Bomani's Bank!
Please select an option:
1. Login
2. Register a new account
3. Exit
    """)
        match input("Your choice: "):
            case "1":
                if user := menu_login_login():
                    menu_main(user)
            case "2":
                if user := menu_login_register():
                    menu_main(user)
            case "3":
                print("Goodbye...! uwu </3")

def menu_login_login() -> UserAccount:
    user_id = input("User ID: ")
    pin = input("PIN: ")
    if (user := AccountManager().get_user_account(user_id)) and user.pin == pin:
        print("Login successful! Redirecting you to the main menu.")
        _ = input("Press any key to continue...")
        return user
    print("Login was unsuccessful. Please try again.")
    _ = input("Press any key to continue...")
    return None

def menu_login_register() -> UserAccount:
    print(f"""
You have indicated that you would like to make a new account.
Please enter some details.""")
    first = input("Your first name: ")
    last = input("Your last name: ")
    dob = opt_helper.str_to_date(input("Your date of birth (MM/DD/YYYY): "))
    while dob == None:
        print("Invalid date format, please try again...")
        dob = opt_helper.str_to_date(input("Your date of birth (MM/DD/YYYY): "))
    new_acc = AccountManager().create_user_account(first, last, dob)
    print(f"""Thank you {first}! Your account has been created with the details: 
User ID is {new_acc.id}
PIN code is {new_acc.pin}.""")
    _ = input("Press any key to continue...")
    return new_acc

def submenu_select_account(user: UserAccount) -> Optional[BankAccount]:
    if len(user.accounts) == 0:
        print("You currently have no accounts with us.")
        return None

    print("Your accounts:")
    len_acc = len(user.accounts)
    for i in range(len_acc):
        print(f"{i}. {user.accounts[i]}")
    choice = input("Which account would you like to use? ")
    return opt_helper.get_item(user.accounts, choice)
    
def menu_deposit(user: UserAccount):
    acc = submenu_select_account(user)
    if not acc:
        print("Invalid choice. Please try again.") 
        _ = input("Press any key to continue...")
        return 
    
    print(f"You have chosen to deposit into account {acc.id}.")
    if value := opt_helper.to_float(input("Please enter amount to deposit. Press any non-digit key to cancel.")):
        _ = AccountManager().acc_deposit(acc, value) # ignore return at the moment
    print("Transaction cancelled.")
    _ = input("Press any key to continue...")
    return

def menu_withdraw(user: UserAccount):
    acc = submenu_select_account(user)
    if not acc:
        print("Invalid choice. Please try again.") 
        _ = input("Press any key to continue...")
        return 
    
    print(f"You have chosen to withdraw from account {acc.id}.")
    value = opt_helper.to_float(input("Please enter amount to withdraw. Press any non-digit key to cancel."))
    if not value:
        print("Transaction cancelled.")
        _ = input("Press any key to continue...")
        return
    if AccountManager().acc_withdraw(acc, value):
        print(f"Withdraw successful. Current balance is now ${acc.balance}")
    print("Invalid transaction.")
    _ = input("Press any key to continue...")
    return


def menu_transfer(user: UserAccount):
    def submenu_query_beneficiary() -> Optional[BankAccount]:
        target_id = input("Please enter account ID to transfer to: ")
        if target_id.isdigit() and (target_id := int(target_id)):
            return AccountManager().get_bank_account(target_id)
        return None

    while not (acc := submenu_select_account(user)):
        print("Invalid choice. Please try again.") 
    
    print(f"You have selected {acc.account_type} account {acc.id}.")
    choice = input("OK? Type Y to confirm, any other key to cancel transaction.")
    if choice.upper() != "Y":
        print("Transaction cancelled.")
        _ = input("Press any key to continue...")
        return
    
    while not (tgt := submenu_query_beneficiary()):
        print("Could not find bank account. Please try again.")
    
    print(f"{tgt.owner.full_name} - {tgt.account_type} account {tgt.id}.")
    choice = input("OK? Type Y to confirm, any other key to cancel transaction.")
    if choice.upper() != "Y":
        print("Transaction cancelled.")
        _ = input("Press any key to continue...")
        return
    
    while amount := opt_helper.to_float(input("Please input amount to transfer.")):
        print("Invalid amount. Please enter a valid number.")
    
    if not AccountManager().acc_is_valid_withdrawal(acc, amount):
        print("Not enough funds.")
        _ = input("Press any key to continue...")
        return
    
    print(f"""
Transfering {amount} from {acc.account_type} account {acc.id} to
{tgt.owner.full_name}'s {tgt.account_type} account {tgt.id}.""")
    choice = input("OK? Type Y to confirm, any other key to cancel transaction.")
    if choice.upper() != "Y":
        print("Transaction cancelled.")
        _ = input("Press any key to continue...")
        return
    
    _ = AccountManager().acc_withdraw(acc, amount)
    _ = AccountManager().acc_deposit(tgt, amount)
    print("Transaction completed.")
    _ = input("Press any key to continue...")
    return

def menu_create_account(user: UserAccount):  
    def submenu_acc_type_select() -> Optional[BankAccount.AccType]:
        print("What type of account would you like to make?")
        for i, v in enumerate(BankAccount.AccType):
            print(f"{i+1}. {v}")
        choice = input("Enter value: ")
        if (choice := opt_helper.to_int(choice)) and (choice-1) < len(BankAccount.AccType):
            return BankAccount.AccType(choice-1)
        return None
    
    while not (acc_type := submenu_acc_type_select()):
        print("Invalid selection. Please try again.")
    
    print(f"Making new {acc_type} account.")
    choice = input("OK? Type Y to confirm, any other key to cancel transaction.")
    if choice.upper() != "Y":
        print("Operation cancelled.")
        _ = input("Press any key to continue...")
        return
    
    new_acc = AccountManager().create_bank_account(user, acc_type)
    print(f"New {new_acc.account_type} account created successfully with ID {new_acc.id}!")
    _ = input("Press any key to continue...")

def menu_change_name(user: UserAccount):
    print(f"Your name is currently set to {user.full_name}")
    choice = input("Change name? Type Y to confirm, any other key to cancel.")
    if choice.upper() != "Y":
        print("Operation cancelled.")
        _ = input("Press any key to continue...")
        return
    
    first = input("Please enter new first name (empty for no change):").strip()
    last = input("Please enter new last name (empty for no change):").strip()
    AccountManager().user_modify_name(user, first, last)
    print(f"Account name successfully changed to {user.full_name}!")
    _ = input("Press any key to continue...")

def menu_main(user: UserAccount):
    while True:
        print(f"""
Hello {user.first_name}, welcome to Bomani's Bank!
How can we help you today?

Your accounts:""")
        for i, acc in enumerate(user.accounts):
            print(f"{i}. {acc}")
        print(f"""
Please enter a choice:
0. Withdraw
1. Deposit
2. Transfer

Account Options:
3. Create new bank account
4. Change name
5. Log out
              """)
        choice = input("Enter choice:")
        match choice:
            case "0": # withdraw
                menu_withdraw(user)
            case "1": # deposit
                menu_deposit(user)
            case "2": # transfer
                menu_transfer(user)
            case "3": # create bank account
                menu_create_account(user)
            case "4": # change name
                menu_change_name(user)
            case "5": # logout
                print("Logging out...")
                return

menu_login()