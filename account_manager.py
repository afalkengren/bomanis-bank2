from typing import List, Dict, Optional, overload
from random import randint
from enum import Enum
from datetime import date
from pathlib import Path
from dataclasses import dataclass
import pickle

# TypeAlias for readability
type BankAccountID = int
type UserAccountID = str

@dataclass
class BankAccount():
    class AccType(Enum):
        Savings = 0
        Checkings = 1

        def __format__(self, _) -> str:
            return self.name

    id: BankAccountID
    owner: "UserAccount"
    account_type: AccType
    balance: float
    overdraft_limit: float

    def __str__(self) -> str:
        return f"""{self.account_type.name} Account ({self.id})
    Balance: ${self.balance:.2f}
    Overdraft Limit: {self.overdraft_limit}"""

    def __format__(self, __format_spec: str) -> str:
        return self.__str__()

@dataclass
class UserAccount():
    id: UserAccountID
    first_name: str
    last_name: str
    birthday: date
    pin: str
    accounts: List[BankAccount]

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

class AccountManager():
    user_accounts: Dict[UserAccountID, UserAccount]
    bank_accounts: Dict[BankAccountID, BankAccount]
    _file_db_path = Path("./bomanis_bank.db")

    # Singleton
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AccountManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if not self._load_from_file():
            self.user_accounts = {}
            self.bank_accounts = {}
    
    # Create Accounts
    def create_user_account(self, first: str, last: str, birthday: date) -> UserAccount:
        pin = f"{randint(0, 9999):04d}"
        new_acc = UserAccount(self._create_unique_user_id(first, last), first, last, birthday, pin, [])
        self.user_accounts[new_acc.id] = new_acc
        self._save_to_file()
        return new_acc

    @overload    
    def create_bank_account(self, user: UserAccount, acc_type: BankAccount.AccType, balance = 0.0, overdraft = 0.0) -> BankAccount:
        pass

    @overload
    def create_bank_account(self, user: UserAccountID, acc_type: BankAccount.AccType, balance = 0.0, overdraft = 0.0) -> BankAccount:
        pass

    def create_bank_account(self, user, acc_type: BankAccount.AccType, balance = 0.0, overdraft = 0.0) -> Optional[BankAccount]:
        if type(user) is UserAccountID:
            user = self.get_user_account(user)
        if type(user) is not UserAccount: return None
        new_acc = BankAccount(self._create_unique_bank_id(), user, acc_type, balance, overdraft)
        self.bank_accounts[new_acc.id] = new_acc
        user.accounts.append(new_acc)
        self._save_to_file()
        return new_acc
    
    # Get/Find Accounts
    def get_bank_account(self, id: BankAccountID) -> Optional[BankAccount]:
        return self.bank_accounts.get(id)
    
    def get_user_account(self, id: UserAccountID) -> Optional[UserAccount]:
        return self.user_accounts.get(id)

    def find_user_accounts(self, first: str, last: str) -> List[UserAccount]:
        return [user for user in self.user_accounts.values() if user.first_name == first and user.last_name == last]

    # Operations on User
    def user_modify_name(self, user: UserAccount, first: Optional[str], last: Optional[str]) -> None:
        if (first := first) and len(first) > 0:
            user.first_name = first
        if (last := last) and len(last) > 0:
            user.last_name = last
    
    def user_remove_acc(self, user: UserAccount, bank_id: BankAccountID) -> bool:
        accs = [acc for acc in user.accounts if acc.id == bank_id]
        if len(accs) == 0:
            return False
        if len(accs) > 1:
            print("WARNING! More than one of the same account ID detected!")
        for acc in accs:
            del self.bank_accounts[acc.id]
            user.accounts.remove(acc)
        return True

    # Operations on Account
    @overload
    def acc_deposit(self, acc: BankAccount, value: float) -> bool:
        pass

    @overload
    def acc_deposit(self, acc: BankAccountID, value: float) -> bool:
        pass
    
    def acc_deposit(self, acc: BankAccount | BankAccountID, value: float) -> bool:
        if type(acc) is BankAccountID:
            acc = self.get_bank_account(id)
        if type(acc) is not BankAccount: return False
        acc.balance += value
        self._save_to_file()
        return True
    
    def acc_is_valid_withdrawal(self, acc: BankAccount, value: float) -> bool:
        if (value > acc.balance): # if overdraft, check if valid transaction
            overdraft_amount_required = value - acc.balance
            if (overdraft_amount_required > acc.overdraft_limit): return False
        return True
    
    @overload    
    def acc_withdraw(self, acc: BankAccount, value: float) -> bool:
        pass
    
    def acc_withdraw(self, acc: BankAccountID, value: float) -> bool:
        pass
    
    def acc_withdraw(self, acc: BankAccount | BankAccountID, value: float) -> bool:
        if type(acc) is BankAccountID:
            acc = self.get_bank_account(id)
        if type(acc) is not BankAccount: return False
        if not self.acc_is_valid_withdrawal(self, acc, value): return False
        acc.balance -= value
        self._save_to_file()
        return True
    
    def modify_overdraft(self, acc: BankAccount, value: float) -> None:
        acc.overdraft_limit = value
        self._save_to_file()

    # Helper methods
    def _save_to_file(self) -> bool:
        with self._file_db_path.open('wb') as f:
            concatdb = (self.user_accounts, self.bank_accounts)
            pickle.dump(concatdb, f)
        return True
    
    def _load_from_file(self) -> bool:
        if not self._file_db_path.exists(): return False
        with self._file_db_path.open('rb') as f:
            (self.user_accounts, self.bank_accounts) = pickle.load(f)
        return True

    def _create_unique_user_id(self, first: str, last: str) -> UserAccountID:
        fnCreate4DigitStr = lambda: "".join([str(randint(0,9)) for _ in range(4)])
        initials = (first[0] + last[0]).lower()
        new_id = initials + fnCreate4DigitStr()
        while new_id in self.bank_accounts:
            new_id = initials + fnCreate4DigitStr()
        return new_id

    def _create_unique_bank_id(self) -> BankAccountID:
        new_id = randint(0, 9999999)
        while new_id in self.bank_accounts:
            new_id = randint(0, 9999999)
        return new_id