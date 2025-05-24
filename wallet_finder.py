import os
import sys
import json
import requests
import hashlib
from time import sleep
from bip32utils import BIP32Key
from mnemonic import Mnemonic
from telegram import Bot
from telegram.error import TelegramError

#Comradehacker Says don't recode, skid make your own... 
# 🌟 Emoji Constants
EMOJIS = {
    "btc": "💰", "eth": "🔷", "bnb": "🟡", "doge": "🐕",
    "success": "✅", "error": "❌", "warning": "⚠️",
    "search": "🔍", "key": "🔑", "loading": "⏳",
    "found": "🎉", "retry": "🔄", "input": "🔹"
}

# 🏷️ ASCII Banner
BANNER = f"""
██████╗ ██████╗ ██╗   ██╗██████╗ ████████╗ ██████╗ 
██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗
██████╔╝██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║   ██║
██╔══██╗██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║   ██║
██████╔╝██║  ██║   ██║   ██║        ██║   ╚██████╔╝
╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝ 
                                                     
💰🔷🟡🐕 Multi-Crypto Wallet Finder/Hack BY ComradeHacker 🐕🟡🔷💰
"""

# ⚙️ Configuration
CONFIG_FILE = "crypto_config.json"
DEFAULT_CONFIG = {
    "selected_crypto": "",
    "api_keys": {
        "btc": "", "eth": "", "bnb": "", "doge": ""
    },
    "telegram": {
        "enabled": False,
        "bot_token": "",
        "chat_id": ""
    },
    "settings": {
        "scan_delay": 0.5,
        "max_retries": 3
    }
}

# API Guides
API_GUIDES = {
    "btc": "Get free API key from blockchain.com (no key needed for basic use)",
    "eth": "Get free API key from etherscan.io/apis (register for free account)",
    "bnb": "Get free API key from bscscan.com/apis (register for free account)",
    "doge": "No API key needed (public API used)"
}

# Initialize Configuration
def init_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# 🛠️ Setup Wizard
def setup_wizard():
    config = init_config()
    
    print(BANNER)
    print(f"{EMOJIS['input']} Configuration Wizard {EMOJIS['input']}")
    
    # Crypto Selection
    while True:
        print("\nSelect cryptocurrency to scan:")
        print(f"1. Bitcoin {EMOJIS['btc']}")
        print(f"2. Ethereum {EMOJIS['eth']}")
        print(f"3. Binance Coin {EMOJIS['bnb']}")
        print(f"4. Dogecoin {EMOJIS['doge']}")
        choice = input(f"{EMOJIS['input']} Enter choice (1-4): ")
        
        cryptos = ["btc", "eth", "bnb", "doge"]
        if choice in ["1","2","3","4"]:
            crypto = cryptos[int(choice)-1]
            config["selected_crypto"] = crypto
            print(f"{EMOJIS['success']} Selected: {crypto.upper()}")
            break
        else:
            print(f"{EMOJIS['error']} Invalid choice!")
    
    # API Key Setup
    print(f"\n{EMOJIS['input']} API Key Setup for {crypto.upper()}")
    print(f"{EMOJIS['warning']} {API_GUIDES[crypto]}")
    
    if crypto != "doge":  # Doge doesn't need API key
        while True:
            api_key = input(f"{EMOJIS['input']} Enter API key (or press Enter to skip): ")
            
            if api_key:
                # Test API key
                print(f"{EMOJIS['loading']} Testing API key...")
                if test_api_key(crypto, api_key):
                    config["api_keys"][crypto] = api_key
                    print(f"{EMOJIS['success']} API key valid and saved!")
                    break
                else:
                    print(f"{EMOJIS['error']} Invalid API key! Please try again")
            else:
                print(f"{EMOJIS['warning']} No API key entered. Some features may not work")
                break
    
    # Telegram Setup
    print(f"\n{EMOJIS['input']} Telegram Notification Setup")
    enable_tg = input(f"{EMOJIS['input']} Enable Telegram alerts? (y/n): ").lower()
    
    if enable_tg == "y":
        config["telegram"]["enabled"] = True
        print(f"\n{EMOJIS['warning']} Create a Telegram bot with @BotFather and get:")
        print("1. Bot token (looks like '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11')")
        print("2. Your chat ID (use @userinfobot to find it)")
        
        while True:
            bot_token = input(f"{EMOJIS['input']} Enter bot token: ")
            chat_id = input(f"{EMOJIS['input']} Enter chat ID: ")
            
            try:
                test_bot = Bot(token=bot_token)
                test_bot.send_message(chat_id=chat_id, text="🔔 Test notification from Crypto Scanner!")
                config["telegram"]["bot_token"] = bot_token
                config["telegram"]["chat_id"] = chat_id
                print(f"{EMOJIS['success']} Telegram connection successful!")
                break
            except Exception as e:
                print(f"{EMOJIS['error']} Telegram setup failed: {e}")
                retry = input(f"{EMOJIS['input']} Try again? (y/n): ").lower()
                if retry != "y":
                    config["telegram"]["enabled"] = False
                    break
    else:
        config["telegram"]["enabled"] = False
    
    save_config(config)
    print(f"\n{EMOJIS['success']} Configuration saved to {CONFIG_FILE}")
    return config

def test_api_key(crypto, api_key):
    test_urls = {
        "btc": f"https://blockchain.info/balance?active=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa&api_code={api_key}",
        "eth": f"https://api.etherscan.io/api?module=account&action=balance&address=0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae&tag=latest&apikey={api_key}",
        "bnb": f"https://api.bscscan.com/api?module=account&action=balance&address=0x8894E0a0c962CB723c1976a4421c95949bE2D4E3&tag=latest&apikey={api_key}"
    }
    
    try:
        response = requests.get(test_urls[crypto], timeout=10)
        return response.status_code == 200
    except:
        return False

# 🔍 Crypto Scanner Functions
def generate_private_key():
    return hashlib.sha256(os.urandom(256)).hexdigest()

def get_address(crypto, private_key):
    if crypto == "btc":
        key = BIP32Key.fromEntropy(bytes.fromhex(private_key))
        return key.Address()
    elif crypto in ["eth", "bnb"]:
        keccak = hashlib.sha3_256()
        keccak.update(bytes.fromhex(private_key))
        return "0x" + keccak.hexdigest()[-40:]
    elif crypto == "doge":
        return "D" + hashlib.sha256(private_key.encode()).hexdigest()[:33]

def check_balance(config, crypto, address):
    if crypto == "btc":
        url = f"https://blockchain.info/balance?active={address}"
        if config["api_keys"]["btc"]:
            url += f"&api_code={config['api_keys']['btc']}"
    elif crypto == "eth":
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={config['api_keys']['eth']}"
    elif crypto == "bnb":
        url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&tag=latest&apikey={config['api_keys']['bnb']}"
    elif crypto == "doge":
        url = f"https://dogechain.info/api/v1/address/balance/{address}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if crypto == "btc":
                return data.get(address, {}).get("final_balance", 0) / 10**8
            elif crypto in ["eth", "bnb"]:
                return int(data.get("result", 0)) / 10**18
            elif crypto == "doge":
                return float(data.get("balance", 0))
    except:
        return 0
    return 0

def send_telegram_alert(config, crypto, address, private_key, balance):
    if not config["telegram"]["enabled"]:
        return
    
    message = f"""
{EMOJIS['found']} <b>CRYPTO WALLET FOUND!</b> {EMOJIS['found']}
{EMOJIS[crypto]} <b>Type:</b> {crypto.upper()}
{EMOJIS['key']} <b>Address:</b> <code>{address}</code>
{EMOJIS['key']} <b>Private Key:</b> <code>{private_key}</code>
{EMOJIS[crypto]} <b>Balance:</b> {balance} {crypto.upper()}
"""
    try:
        bot = Bot(token=config["telegram"]["bot_token"])
        bot.send_message(
            chat_id=config["telegram"]["chat_id"],
            text=message,
            parse_mode='HTML'
        )
    except Exception as e:
        print(f"{EMOJIS['error']} Telegram alert failed: {e}")

def save_wallet(crypto, address, private_key, balance):
    with open("found_wallets.txt", "a") as f:
        f.write(f"""
[{crypto.upper()} WALLET]
Address: {address}
Private Key: {private_key}
Balance: {balance} {crypto.upper()}
-------------------------------
""")

# 🏁 Main Scanner
def run_scanner(config):
    crypto = config["selected_crypto"]
    counter = 0
    
    print(f"\n{EMOJIS['loading']} Starting {crypto.upper()} scanner...")
    print(f"{EMOJIS['warning']} Press Ctrl+C to stop\n")
    
    try:
        while True:
            counter += 1
            private_key = generate_private_key()
            address = get_address(crypto, private_key)
            balance = check_balance(config, crypto, address)
            
            # Display status
            sys.stdout.write(f"\r{EMOJIS['loading']} Scan #{counter} | {address} | Balance: {balance} {crypto.upper()}")
            sys.stdout.flush()
            
            # Save if balance found
            if balance > 0:
                print(f"\n{EMOJIS['found']} Found balance: {balance} {crypto.upper()}!")
                save_wallet(crypto, address, private_key, balance)
                send_telegram_alert(config, crypto, address, private_key, balance)
            
            sleep(config["settings"]["scan_delay"])
            
    except KeyboardInterrupt:
        print(f"\n\n{EMOJIS['warning']} Scanner stopped. Total scanned: {counter}")

# 🚀 Main Program
if __name__ == "__main__":
    config = init_config()
    
    if not config.get("selected_crypto"):
        config = setup_wizard()
    
    while True:
        print("\nMain Menu:")
        print(f"1. Run {config['selected_crypto'].upper()} Scanner")
        print("2. Change Configuration")
        print("3. Exit")
        
        choice = input(f"{EMOJIS['input']} Select option (1-3): ")
        
        if choice == "1":
            run_scanner(config)
        elif choice == "2":
            config = setup_wizard()
        elif choice == "3":
            print(f"{EMOJIS['success']} Goodbye!")
            sys.exit(0)
        else:
            print(f"{EMOJIS['error']} Invalid choice!")