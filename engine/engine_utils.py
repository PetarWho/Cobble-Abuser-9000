from colorama import Fore, Style
import datetime


def current_time():
    return f"{Fore.GREEN + '[' + datetime.datetime.now().strftime('%d %b, %I:%M %p')  + ']' + Style.RESET_ALL}"


