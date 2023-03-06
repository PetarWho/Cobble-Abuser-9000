import pyautogui
import asyncio
import datetime
import keyboard
from colorama import Fore, Style

mining_category_location = [743, 319]
cobble_location = [851, 321]
enchanted_cobble_location = [1014, 371]
sell_location = [850, 483]
confirm_location = [850, 405]


async def click(x, y):
    pyautogui.moveTo(x, y)
    await asyncio.sleep(0.5)
    pyautogui.click()


async def send_command(command: str):
    if command.startswith('/'):
        command = command[1:]

    pyautogui.press('/')
    pyautogui.typewrite(command)
    pyautogui.press('enter')


async def stop_mining():
    pyautogui.click()
    pyautogui.press('f2')
    pyautogui.press('f9')


async def start_mining():
    pyautogui.press('f9')
    pyautogui.press('f10')
    await asyncio.sleep(1)
    pyautogui.press('f1')
    pyautogui.click()


async def close_menu():
    pyautogui.press('esc')


def write(text: str, color=''):
    print(color + text + Style.RESET_ALL)


def current_time():
    return f"{Fore.GREEN + '[' + datetime.datetime.now().strftime('%d %b, %I:%M %p')  + ']' + Style.RESET_ALL}"


def print_mine_hours():
    print(f"{current_time()} You've been mining for {Fore.LIGHTMAGENTA_EX + str(hours_spent) + Style.RESET_ALL} hour") if hours_spent == 1 else print(f"{current_time()} You've been mining for {Fore.LIGHTMAGENTA_EX + str(hours_spent) + Style.RESET_ALL} hours")


async def abuse():
    write("Mining Starts in 5 secs...\n", Fore.LIGHTYELLOW_EX)
    await asyncio.sleep(6)
    print(f"{ current_time()} Mining started!")
    global hours_spent
    hours_spent = 1
    while True:
        await start_mining()
        await asyncio.sleep(3600)
        await stop_mining()
        await asyncio.sleep(0.5)
        await send_command("bz")
        await asyncio.sleep(1)
        await click(mining_category_location[0], mining_category_location[1])
        await asyncio.sleep(1)
        await click(cobble_location[0], cobble_location[1])
        await asyncio.sleep(1)
        await click(enchanted_cobble_location[0], enchanted_cobble_location[1])
        await asyncio.sleep(1)
        await click(sell_location[0], sell_location[1])
        await asyncio.sleep(1)
        await click(confirm_location[0], confirm_location[1])
        await asyncio.sleep(1)
        await close_menu()
        await asyncio.sleep(1)
        print_mine_hours()
        hours_spent += 1


async def terminate(task):
    while True:
        if keyboard.is_pressed('q'):
            task.cancel()
            break
        await asyncio.sleep(0.1)


async def run():
    task = asyncio.create_task(abuse())
    try:
        await asyncio.gather(task, terminate(task))
    except asyncio.CancelledError:
        print(f"\n{current_time()} Cobble Abuser 9000 has finished it's task...")
    keyboard.wait()


asyncio.run(run())
