import requests
from concurrent.futures import ThreadPoolExecutor
import threading
import argparse
import json
import time
import os
import sys
import colorama
from colorama import init, Fore
from datetime import datetime

directory = os.path.dirname(os.path.abspath(__file__))
usernamesdir = os.path.join(directory, "usernames.txt")
outputdir = os.path.join(directory, "valid.txt")

printlock = threading.Lock()
init(autoreset=True)

starttime = None
checked = 0
valid = 0
sendwebhook = False
webhook = "" #add ur own here if u want and uncomment the line 94.

def title(title):
    if os.name == 'nt':
        safe_title = title.replace(":", "-").replace("|", "-")
        os.system(f"title {safe_title}")
    else:
        sys.stdout.write(f"\x1b]2;{title}\x07")
        sys.stdout.flush()

def result(status, username):
    status_text = f"[{status}]".ljust(7)
    username_text = username.ljust(10)
    with printlock:
        if status == "VALID":
            print(Fore.GREEN + f"{status_text} {username_text}")
        else:
            print(Fore.RED + f"{status_text} {username_text}")

def send_webhook(webhook, username):
    try:
        payload = {
            "content": f"**valid user found: ** `{username}`"
        }
        headers = {"Content-Type": "application/json"}
        requests.post(webhook, data=json.dumps(payload), headers=headers, timeout=5)
    except Exception as e:
        with printlock:
            print(Fore.YELLOW + f"[ERROR] webhook send failed: {e}")

def logresult(status, username):
    status_label = f"[{status}]".ljust(7)
    username_field = username.ljust(10)
    with printlock:
        if status == "VALID":
            print(Fore.GREEN + f"{status_label} {username_field}")
        else:
            print(Fore.RED + f"{status_label} {username_field}")
    
        
def check_user(username):
    url = f"https://auth.roblox.com/v1/usernames/validate?Username={username}&Birthday=2000-01-01"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", "").strip().lower()
            return username, (message == "username is valid")
    except Exception as e:
        with printlock:
            print(Fore.YELLOW + f"[ERROR] {username} - {e}")
    return username, False
    
def process_user(username):
    global checked, valid
    username, is_valid = check_user(username)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with printlock:
        checked += 1
        if is_valid:
            valid += 1
        elapsed = max(time.time() - starttime, 1)
        cpm = int((checked / elapsed) * 60)
        title(f"/tracing: {checked} | Valid: {valid} | CPM: {cpm}")

    if is_valid:
        logresult("VALID", username)
        with open(outputdir, "a") as vf:
            vf.write(f"[{timestamp}] {username}\n")
        #send_webhook(webhook, username)
    else:
        logresult("TAKEN", username)
        with open(outputdir, "a") as inf:
            inf.write(f"[{timestamp}] {username}\n")
            
def main():
    
    
    print(Fore.BLUE + r"""
       ____                  _            
     _/_/ /__________ ______(_)___  ____ _
   _/_// __/ ___/ __ `/ ___/ / __ \/ __ `/
 _/_/ / /_/ /  / /_/ / /__/ / / / / /_/ / 
/_/   \__/_/   \__,_/\___/_/_/ /_/\__, /  
                                 /____/   
    """)

    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, default=20, help="Number of threads (default 20)")
    args = parser.parse_args()
    print(Fore.RED + "PLEASE read README file before using.")
    choice = input(Fore.RED + "start sniping(y/n): ").strip().lower()
    if choice != 'y':
        print("exiting")
        return

    open("valid.txt", "w").close()
    open("invalid.txt", "w").close()

    with open("usernames.txt", "r") as f:
        usernames = [line.strip() for line in f if line.strip()]

    max_threads = min(len(usernames), args.threads)
    starttime = time.time()

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        executor.map(process_user, usernames)

    elapsed = round(time.time() - starttime, 2)
    print(Fore.BLUE + f"checked: {checked}")
    print(Fore.GREEN + f"valid: {valid}")
    print(Fore.RED + f"taken: {checked - valid}")
    print(Fore.BLUE + f"time elapsed: {elapsed} seconds")
    

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"idk what happend dawg error {e}")
        print("please send screenshot of this to my discord @tracinghumanoid :)")
    finally:
        input("Press enter to exit")
    