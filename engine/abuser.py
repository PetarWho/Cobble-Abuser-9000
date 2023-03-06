import pyautogui
import asyncio
import keyboard
import time
from colorama import Fore, Style
import console_utils
from engine_utils import current_time

mining_category_location = [743, 319]
cobble_location = [851, 321]
enchanted_cobble_location = [1014, 371]
sell_location = [850, 483]
confirm_location = [850, 405]
interval = console_utils.get_interval_input()
global start_time


async def click(x, y):
    pyautogui.moveTo(x, y)
    await asyncio.sleep(0.2)
    pyautogui.click()


async def send_command(command: str):
    if command.startswith('/'):
        command = command[1:]

    pyautogui.press('/')
    pyautogui.typewrite(command)
    pyautogui.press('enter')


async def start_mining():
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('w')
    pyautogui.mouseDown(button='left')


async def stop_mining():
    pyautogui.mouseUp(button='left')
    pyautogui.keyUp('w')
    pyautogui.keyUp('ctrl')


async def close_menu():
    pyautogui.press('esc')


def print_mine_time():
    try:
        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time < 60:
            print(f"{current_time()} You've been mining for {Fore.LIGHTMAGENTA_EX + str(round(elapsed_time, 1)) + Style.RESET_ALL} seconds")
        elif elapsed_time < 3600:
            print(f"{current_time()} You've been mining for {Fore.LIGHTMAGENTA_EX + str(round(elapsed_time/60, 1)) + Style.RESET_ALL} minute") if elapsed_time == 1 else print(f"{current_time()} You've been mining for {Fore.LIGHTMAGENTA_EX + str(round(elapsed_time/60, 1)) + Style.RESET_ALL} minutes")
        else:
            print(f"{current_time()} You've been mining for {Fore.LIGHTMAGENTA_EX + str(round(elapsed_time/3600, 1)) + Style.RESET_ALL} hour") if elapsed_time == 1 else print(f"{current_time()} You've been mining for {Fore.LIGHTMAGENTA_EX + str(round(elapsed_time/3600, 1)) + Style.RESET_ALL} hours")
    except Exception:
        pass

async def abuse():
    console_utils.write("Mining Starts in 5 secs...\n", Fore.LIGHTYELLOW_EX)
    await asyncio.sleep(6)
    global start_time
    start_time = time.time()
    print(f"{ current_time()} Mining started!")
    while True:
        await start_mining()
        await asyncio.sleep(interval)
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


async def terminate(task):
    while True:
        if keyboard.is_pressed('z'):
            task.cancel()
            await stop_mining()
            break
        await asyncio.sleep(0.1)


async def run():
    task = asyncio.create_task(abuse())
    try:
        await asyncio.gather(task, terminate(task))
    except asyncio.CancelledError:
        print(f"\n{current_time()} Cobble Abuser 9000 has finished it's task...")
        print_mine_time()
    keyboard.wait()


asyncio.run(run())