import os
from colorama import Fore, Style


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_interval_input():
    clear_console()
    while True:
        user_input = input("Enter minutes between each sell: ")
        try:
            interval = float(user_input) * 60
            clear_console()
            return interval
        except ValueError:
            clear_console()
            print(Fore.LIGHTRED_EX + "Please enter a valid number!" + Style.RESET_ALL)


def write(text: str, color=''):
    print(color + text + Style.RESET_ALL)
