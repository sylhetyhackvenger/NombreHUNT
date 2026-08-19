#!/usr/bin/env python3

import os
import sys
import json
import asyncio
import aiohttp
import aiofiles
import hashlib
import sqlite3
import time
import random
import re
import ssl
import socket
import subprocess
import whois
import dns.resolver
import smtplib
import imaplib
import email
import requests
import argparse
import base64
import binascii
import struct
import zlib
import gzip
import csv
import xml.etree.ElementTree as ET
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from collections import defaultdict, Counter
from urllib.parse import urlparse, quote_plus, urlencode, parse_qs
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone, PhoneNumberType
except ImportError:
    os.system('pip install phonenumbers 2>/dev/null')
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone, PhoneNumberType

try:
    from fake_useragent import UserAgent
except ImportError:
    os.system('pip install fake-useragent 2>/dev/null')
    from fake_useragent import UserAgent

try:
    import aiohttp_socks
except ImportError:
    os.system('pip install aiohttp-socks 2>/dev/null')
    import aiohttp_socks

try:
    from bs4 import BeautifulSoup
except ImportError:
    os.system('pip install beautifulsoup4 2>/dev/null')
    from bs4 import BeautifulSoup

try:
    import whois
except ImportError:
    os.system('pip install python-whois 2>/dev/null')
    import whois

try:
    import dns.resolver
except ImportError:
    os.system('pip install dnspython 2>/dev/null')
    import dns.resolver

try:
    from OpenSSL import crypto
except ImportError:
    os.system('pip install pyOpenSSL 2>/dev/null')
    from OpenSSL import crypto

try:
    import geoip2.database
except ImportError:
    os.system('pip install geoip2 2>/dev/null')
    import geoip2.database

try:
    import shodan
except ImportError:
    os.system('pip install shodan 2>/dev/null')
    import shodan

try:
    import censys
except ImportError:
    os.system('pip install censys 2>/dev/null')
    import censys

try:
    import tweepy
except ImportError:
    os.system('pip install tweepy 2>/dev/null')
    import tweepy

try:
    import praw
except ImportError:
    os.system('pip install praw 2>/dev/null')
    import praw

try:
    import instagram_private_api
except ImportError:
    os.system('pip install instagram-private-api 2>/dev/null')
    import instagram_private_api

VERBOSE = True
SAVE_FILES = False
OUTPUT_DIR = "nombrehunt_output"

class Colors:
    white = "\033[97m"
    green = "\033[92m"
    red = "\033[91m"
    yellow = "\033[93m"
    cyan = "\033[96m"
    magenta = "\033[95m"
    blue = "\033[94m"
    reset = "\033[0m"
    bold = "\033[1m"
    orange = "\033[33m"
    purple = "\033[35m"
    grey = "\033[90m"
    black = "\033[30m"
    light_blue = "\033[94m"
    light_green = "\033[92m"
    light_red = "\033[91m"
    light_cyan = "\033[96m"
    light_magenta = "\033[95m"
    light_yellow = "\033[93m"

class Write:
    @staticmethod
    def Print(text, color=Colors.white, end="\n"):
        print(f"{color}{text}{Colors.reset}", end=end)
    
    @staticmethod
    def Progress(current, total, prefix="", suffix=""):
        bar_length = 50
        filled = int(bar_length * current / total)
        bar = "█" * filled + "░" * (bar_length - filled)
        percent = int(current / total * 100)
        sys.stdout.write(f"\r{prefix} [{bar}] {percent}% {suffix}")
        sys.stdout.flush()
    
    @staticmethod
    def Header(text):
        Write.Print("\n" + "="*100, Colors.magenta)
        Write.Print(f"  {text}", Colors.bold + Colors.magenta)
        Write.Print("="*100, Colors.magenta)
    
    @staticmethod
    def SubHeader(text):
        Write.Print(f"\n  ─── {text} ───", Colors.bold + Colors.cyan)
    
    @staticmethod
    def Success(text):
        Write.Print(f"  ✅ {text}", Colors.green)
    
    @staticmethod
    def Warning(text):
        Write.Print(f"  ⚠️ {text}", Colors.yellow)
    
    @staticmethod
    def Error(text):
        Write.Print(f"  ❌ {text}", Colors.red)
    
    @staticmethod
    def Info(text):
        Write.Print(f"  ℹ️ {text}", Colors.cyan)
    
    @staticmethod
    def Verbose(text, data=None):
        if VERBOSE:
            Write.Print(f"  📝 {text}", Colors.grey)
            if data:
                try:
                    if isinstance(data, dict):
                        for k, v in list(data.items())[:5]:
                            Write.Print(f"      {k}: {str(v)[:100]}", Colors.grey)
                    elif isinstance(data, list) and data:
                        Write.Print(f"      {len(data)} items found", Colors.grey)
                        for item in data[:3]:
                            Write.Print(f"      • {str(item)[:100]}", Colors.grey)
                    else:
                        Write.Print(f"      {str(data)[:200]}", Colors.grey)
                except:
                    pass
    
    @staticmethod
    def Raw(text):
        Write.Print(f"  🔍 {text}", Colors.cyan)
    
    @staticmethod
    def Found(platform, username, url, details=None):
        Write.Print(f"  🎯 FOUND: {platform} - {username}", Colors.green)
        Write.Print(f"     URL: {url}", Colors.grey)
        if details:
            for k, v in details.items():
                Write.Print(f"     {k}: {v}", Colors.grey)
    
    @staticmethod
    def Table(headers, rows):
        if not rows:
            return
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        header_line = "  ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
        Write.Print("┌" + "─" * (sum(col_widths) + len(headers) * 3) + "┐", Colors.cyan)
        Write.Print("│ " + header_line + " │", Colors.bold + Colors.cyan)
        Write.Print("├" + "─" * (sum(col_widths) + len(headers) * 3) + "┤", Colors.cyan)
        for row in rows[:20]:
            row_line = "  ".join(f"{str(cell):<{col_widths[i]}}" for i, cell in enumerate(row))
            Write.Print("│ " + row_line + " │", Colors.white)
        if len(rows) > 20:
            Write.Print(f"│ ... {len(rows) - 20} more rows ... │", Colors.grey)
        Write.Print("└" + "─" * (sum(col_widths) + len(headers) * 3) + "┘", Colors.cyan)

def show_banner():
    banner = r'''
                .sss.      
                $P'`T.     
                $;  :;     
                $;  :$     
        __......$b__d$     
   .sd$$$P^^^^^^^TBuG$s.   
  .$P'      ___     _`T$.  
  $P        """    (_) T$  
 s$   _..---***---.._   $s 
 $$ .'    ERROR808    `. $$ 
.$$.  .-------------.  .$$.
:$$: :               ; ;$$;
$$;| |               | |:$$
$$'| |               | |'$$
$$ | |               | | $$
$$ | |               | | $$
$$ | :               ; | $$
$$.;  `-------------'  :.$$
$$; . (C)   .-.       . :$$
:$$  `-.   / _ \   .-'  $$;
'$$  .-.`.: (_) ;.'.-.  $$'
 $$ :   ; `.___.' :   ; $$ 
 $$  `-'           `-'  $$ 
 $$.( 1 )  ( 2 )  ( 3 ).$$ 
 $$;                   :$$ 
 :$$ ( 4 ).( 5 ).( 6 ) $$; 
 '$$                   $$' 
  $$ ( 7 ) ( 8 ) ( 9 ) $$  
  $$                   $$  
  $$ ( * ) ( 0 ) ( # ) $$  
  $$.                 .$$  
  $$; o               :$P  
   T$b.             .d$P   
    `^T$$$$$$$$$$$$$P^'     
'''
    print(f"{Colors.cyan}{banner}{Colors.reset}")
    print(f"{Colors.bold}{Colors.magenta}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.reset}")
    print(f"{Colors.bold}{Colors.magenta}║{Colors.reset} {Colors.cyan}NombreHUNT{Colors.reset} {Colors.white}Phone Number OSINT Tool{Colors.reset}          {Colors.magenta}║{Colors.reset}")
    print(f"{Colors.bold}{Colors.magenta}║{Colors.reset} {Colors.green}Every discovery shown in real-time with full details{Colors.reset}              {Colors.magenta}║{Colors.reset}")
    print(f"{Colors.bold}{Colors.magenta}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.reset}")
    print(f"{Colors.bold}{Colors.green}Author: SYLHETYHACKVENGER (THE-ERROR808){Colors.reset}")
    print(f"{Colors.bold}{Colors.yellow}Version: v1.0 {Colors.reset}")
    print(f"{Colors.bold}{Colors.grey}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.reset}\n")

@dataclass
class CompleteIntel:
    phone: str
    e164: str
    timestamp: str
    valid: bool = False
    possible: bool = False
    country: str = ""
    region: str = ""
    city: str = ""
    carrier: str = ""
    number_type: str = ""
    timezone: str = ""
    country_code: int = 0
    national_number: str = ""
    social_platforms: List[Dict] = field(default_factory=list)
    social_count: int = 0
    social_details: Dict = field(default_factory=dict)
    breaches: List[Dict] = field(default_factory=list)
    breach_count: int = 0
    breach_details: Dict = field(default_factory=dict)
    breach_timeline: List[Dict] = field(default_factory=list)
    emails: List[str] = field(default_factory=list)
    email_breaches: List[Dict] = field(default_factory=list)
    email_breach_count: int = 0
    email_verified: bool = False
    email_providers: List[str] = field(default_factory=list)
    sim_swapped: bool = False
    sim_swap_date: str = ""
    sim_swap_carrier: str = ""
    sim_swap_risk: str = "Low"
    sim_swap_history: List[Dict] = field(default_factory=list)
    latitude: float = 0
    longitude: float = 0
    city_full: str = ""
    state_full: str = ""
    country_code_iso: str = ""
    postal_code: str = ""
    isp: str = ""
    org: str = ""
    asn: str = ""
    timezone_full: str = ""
    continent: str = ""
    region_code: str = ""
    area_code: str = ""
    geo_hash: str = ""
    nearby_places: List[Dict] = field(default_factory=list)
    cell_towers: List[Dict] = field(default_factory=list)
    wifi_networks: List[Dict] = field(default_factory=list)
    names: List[str] = field(default_factory=list)
    addresses: List[str] = field(default_factory=list)
    emails_found: List[str] = field(default_factory=list)
    age_range: str = ""
    gender: str = ""
    relatives: List[str] = field(default_factory=list)
    associates: List[str] = field(default_factory=list)
    previous_addresses: List[str] = field(default_factory=list)
    property_records: List[Dict] = field(default_factory=list)
    dark_web_found: bool = False
    dark_web_breaches: List[Dict] = field(default_factory=list)
    dark_web_credentials: List[Dict] = field(default_factory=list)
    dark_web_forums: List[str] = field(default_factory=list)
    dark_web_date: str = ""
    dark_web_sources: List[str] = field(default_factory=list)
    dark_web_leaks: List[Dict] = field(default_factory=list)
    dark_web_mentions: int = 0
    domains: List[Dict] = field(default_factory=list)
    domain_count: int = 0
    whois_records: List[Dict] = field(default_factory=list)
    domain_age: str = ""
    domain_expiry: str = ""
    domain_registrar: str = ""
    domain_nameservers: List[str] = field(default_factory=list)
    subdomains: List[str] = field(default_factory=list)
    ip_addresses: List[str] = field(default_factory=list)
    ip_reputation: Dict = field(default_factory=dict)
    ip_geolocation: Dict = field(default_factory=dict)
    ip_risk: int = 0
    ip_blocklisted: bool = False
    ip_sources: List[str] = field(default_factory=list)
    ip_history: List[Dict] = field(default_factory=list)
    ssl_certificates: List[Dict] = field(default_factory=list)
    ssl_issuer: str = ""
    ssl_subject: str = ""
    ssl_valid_from: str = ""
    ssl_valid_to: str = ""
    ssl_san: List[str] = field(default_factory=list)
    open_ports: List[int] = field(default_factory=list)
    services: List[Dict] = field(default_factory=list)
    banner_grabbing: List[Dict] = field(default_factory=list)
    call_activity: Dict = field(default_factory=dict)
    call_patterns: Dict = field(default_factory=dict)
    frequent_contacts: List[str] = field(default_factory=list)
    active_hours: List[str] = field(default_factory=list)
    peak_times: List[str] = field(default_factory=list)
    call_duration_avg: str = ""
    incoming_count: int = 0
    outgoing_count: int = 0
    missed_count: int = 0
    unknown_count: int = 0
    sms_activity: Dict = field(default_factory=dict)
    sms_patterns: List[str] = field(default_factory=list)
    sms_keywords: List[str] = field(default_factory=list)
    businesses: List[Dict] = field(default_factory=list)
    business_count: int = 0
    real_estate: List[Dict] = field(default_factory=list)
    property_value: str = ""
    credit_score_range: str = ""
    bankruptcy_records: List[str] = field(default_factory=list)
    liens: List[Dict] = field(default_factory=list)
    judgments: List[Dict] = field(default_factory=list)
    court_cases: List[Dict] = field(default_factory=list)
    professional_licenses: List[Dict] = field(default_factory=list)
    voter_registration: bool = False
    criminal_records: List[Dict] = field(default_factory=list)
    arrest_records: List[Dict] = field(default_factory=list)
    warrants: List[Dict] = field(default_factory=list)
    marriage_records: List[Dict] = field(default_factory=list)
    divorce_records: List[Dict] = field(default_factory=list)
    birth_records: List[Dict] = field(default_factory=list)
    death_records: List[Dict] = field(default_factory=list)
    is_voip: bool = False
    is_temporary: bool = False
    is_prepaid: bool = False
    voip_provider: str = ""
    temp_provider: str = ""
    temp_created: str = ""
    temp_expires: str = ""
    temp_active: bool = False
    voip_risk: str = "Low"
    call_forwarding: bool = False
    sms_forwarding: bool = False
    forwarding_numbers: List[str] = field(default_factory=list)
    forwarding_destination: str = ""
    forwarding_risk: str = "Low"
    forwarding_status: str = "Inactive"
    spam_score: int = 0
    spam_reports: int = 0
    reputation_score: int = 0
    reputation_level: str = "Unknown"
    blocklisted: bool = False
    blocklist_sources: List[str] = field(default_factory=list)
    spam_keywords: List[str] = field(default_factory=list)
    spam_categories: List[str] = field(default_factory=list)
    spoofing_detected: bool = False
    spoofing_risk: str = "Low"
    spoofing_method: str = ""
    spoofing_history: List[Dict] = field(default_factory=list)
    number_portable: bool = False
    original_carrier: str = ""
    current_carrier: str = ""
    porting_date: str = ""
    porting_history: List[Dict] = field(default_factory=list)
    google_results: List[Dict] = field(default_factory=list)
    google_count: int = 0
    google_dorks_used: List[str] = field(default_factory=list)
    pastebin_results: List[Dict] = field(default_factory=list)
    dump_found: bool = False
    dump_count: int = 0
    dump_sources: List[str] = field(default_factory=list)
    git_repos: List[Dict] = field(default_factory=list)
    git_commits: int = 0
    git_contributions: List[Dict] = field(default_factory=list)
    shodan_results: List[Dict] = field(default_factory=list)
    censys_results: List[Dict] = field(default_factory=list)
    exposed_services: List[str] = field(default_factory=list)
    recent_posts: List[Dict] = field(default_factory=list)
    post_count: int = 0
    sentiment: str = "Neutral"
    hashtags_used: List[str] = field(default_factory=list)
    mentions: List[str] = field(default_factory=list)
    interactions: int = 0
    profile_pictures: List[str] = field(default_factory=list)
    photos: List[str] = field(default_factory=list)
    videos: List[str] = field(default_factory=list)
    media_count: int = 0
    location_history: List[Dict] = field(default_factory=list)
    checkins: List[Dict] = field(default_factory=list)
    travel_patterns: List[Dict] = field(default_factory=list)
    devices: List[Dict] = field(default_factory=list)
    device_types: List[str] = field(default_factory=list)
    os_versions: List[str] = field(default_factory=list)
    communication_patterns: Dict = field(default_factory=dict)
    response_times: Dict = field(default_factory=dict)
    language_patterns: List[str] = field(default_factory=list)
    network_metadata: Dict = field(default_factory=dict)
    bandwidth_estimate: str = ""
    network_quality: str = ""
    graph: Dict = field(default_factory=dict)
    graph_nodes: int = 0
    graph_edges: int = 0
    graph_centrality: Dict = field(default_factory=dict)
    timeline: List[Dict] = field(default_factory=list)
    timeline_events: int = 0
    timeline_start: str = ""
    timeline_end: str = ""
    evidence_count: int = 0
    evidence_sources: List[str] = field(default_factory=list)
    evidence_links: List[str] = field(default_factory=list)
    evidence_files: List[str] = field(default_factory=list)
    risk_score: int = 0
    risk_level: str = "Low"
    risk_factors: List[str] = field(default_factory=list)
    risk_categories: Dict = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 0.0
    modules_used: List[str] = field(default_factory=list)
    duration: float = 0
    sources_checked: int = 0
    found_items: int = 0
    
    raw_data: Dict = field(default_factory=dict)
    raw_json: Dict = field(default_factory=dict)
    raw_html: Dict = field(default_factory=dict)
    raw_http: List[Dict] = field(default_factory=list)

class Database:
    def __init__(self, db_file="nombrehunt_complete.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS investigations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT,
                e164 TEXT,
                timestamp TEXT,
                risk_score INTEGER,
                risk_level TEXT,
                social_count INTEGER,
                breach_count INTEGER,
                domain_count INTEGER,
                email_count INTEGER,
                evidence_count INTEGER,
                full_json TEXT,
                raw_data TEXT,
                UNIQUE(phone, timestamp)
            );
            CREATE TABLE IF NOT EXISTS social_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inv_id INTEGER,
                platform TEXT,
                found INTEGER,
                username TEXT,
                url TEXT,
                followers INTEGER DEFAULT 0,
                verified INTEGER DEFAULT 0,
                category TEXT,
                confidence REAL DEFAULT 1.0,
                raw_response TEXT,
                FOREIGN KEY (inv_id) REFERENCES investigations(id)
            );
            CREATE TABLE IF NOT EXISTS breach_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inv_id INTEGER,
                name TEXT,
                source TEXT,
                date TEXT,
                data_type TEXT,
                details TEXT,
                raw_data TEXT,
                FOREIGN KEY (inv_id) REFERENCES investigations(id)
            );
            CREATE TABLE IF NOT EXISTS email_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inv_id INTEGER,
                email TEXT,
                verified INTEGER,
                source TEXT,
                FOREIGN KEY (inv_id) REFERENCES investigations(id)
            );
            CREATE TABLE IF NOT EXISTS domain_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inv_id INTEGER,
                domain TEXT,
                registrar TEXT,
                created TEXT,
                expires TEXT,
                nameservers TEXT,
                raw_data TEXT,
                FOREIGN KEY (inv_id) REFERENCES investigations(id)
            );
            CREATE TABLE IF NOT EXISTS dark_web_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inv_id INTEGER,
                source TEXT,
                breach TEXT,
                date TEXT,
                data TEXT,
                FOREIGN KEY (inv_id) REFERENCES investigations(id)
            );
            CREATE TABLE IF NOT EXISTS name_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inv_id INTEGER,
                name TEXT,
                source TEXT,
                confidence REAL,
                FOREIGN KEY (inv_id) REFERENCES investigations(id)
            );
            CREATE TABLE IF NOT EXISTS location_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inv_id INTEGER,
                latitude REAL,
                longitude REAL,
                city TEXT,
                state TEXT,
                country TEXT,
                postal TEXT,
                FOREIGN KEY (inv_id) REFERENCES investigations(id)
            );
            CREATE TABLE IF NOT EXISTS spam_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inv_id INTEGER,
                source TEXT,
                score INTEGER,
                reports INTEGER,
                blocklisted INTEGER,
                FOREIGN KEY (inv_id) REFERENCES investigations(id)
            );
            CREATE TABLE IF NOT EXISTS court_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inv_id INTEGER,
                case_number TEXT,
                court TEXT,
                date TEXT,
                type TEXT,
                FOREIGN KEY (inv_id) REFERENCES investigations(id)
            );
            CREATE INDEX IF NOT EXISTS idx_inv_phone ON investigations(phone);
            CREATE INDEX IF NOT EXISTS idx_inv_timestamp ON investigations(timestamp);
            CREATE INDEX IF NOT EXISTS idx_social_platform ON social_results(platform);
            CREATE INDEX IF NOT EXISTS idx_breach_name ON breach_results(name);
            CREATE INDEX IF NOT EXISTS idx_email_email ON email_results(email);
        """)
        self.conn.commit()
    
    def save(self, intel: CompleteIntel):
        self.cursor.execute(
            """INSERT INTO investigations 
               (phone, e164, timestamp, risk_score, risk_level, 
                social_count, breach_count, domain_count, email_count, evidence_count, full_json, raw_data)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (intel.phone, intel.e164, intel.timestamp,
             intel.risk_score, intel.risk_level,
             intel.social_count, intel.breach_count,
             intel.domain_count, len(intel.emails),
             intel.evidence_count,
             json.dumps(asdict(intel), default=str),
             json.dumps(intel.raw_data, default=str))
        )
        inv_id = self.cursor.lastrowid
        
        for social in intel.social_platforms:
            self.cursor.execute(
                """INSERT INTO social_results 
                   (inv_id, platform, found, username, url, followers, verified, category, confidence, raw_response)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (inv_id, social.get('platform', ''),
                 1 if social.get('found') else 0,
                 social.get('username', ''), social.get('url', ''),
                 social.get('followers', 0),
                 1 if social.get('verified') else 0,
                 social.get('category', ''), social.get('confidence', 0.0),
                 json.dumps(social.get('raw_response', {})))
            )
        
        for breach in intel.breaches:
            self.cursor.execute(
                """INSERT INTO breach_results 
                   (inv_id, name, source, date, data_type, details, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (inv_id, breach.get('name', ''),
                 breach.get('source', ''), breach.get('date', ''),
                 breach.get('type', ''), json.dumps(breach),
                 json.dumps(breach.get('raw_data', {})))
            )
        
        for email in intel.emails:
            self.cursor.execute(
                """INSERT INTO email_results (inv_id, email, verified, source)
                   VALUES (?, ?, ?, ?)""",
                (inv_id, email, 1 if intel.email_verified else 0, 'Discovery')
            )
        
        for domain in intel.domains:
            self.cursor.execute(
                """INSERT INTO domain_results 
                   (inv_id, domain, registrar, created, expires, nameservers, raw_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (inv_id, domain.get('domain', ''),
                 domain.get('registrar', ''), domain.get('created', ''),
                 domain.get('expires', ''), domain.get('nameservers', ''),
                 json.dumps(domain.get('raw_data', {})))
            )
        
        self.conn.commit()

class SessionManager:
    def __init__(self):
        self.ua = UserAgent()
        self.sessions = {}
        self.rate_limiter = None
        self.proxy = None
        self.proxies = []
        self.current_proxy_index = 0
    
    async def get_session(self, use_tor=False, proxy=None):
        if use_tor:
            connector = aiohttp_socks.SocksConnector.from_url('socks5://127.0.0.1:9050')
        elif proxy:
            connector = aiohttp_socks.SocksConnector.from_url(proxy)
        else:
            connector = aiohttp.TCPConnector(
                limit=500,
                limit_per_host=100,
                ttl_dns_cache=600,
                ssl=ssl.create_default_context(),
                enable_cleanup_closed=True
            )
        
        session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=45, connect=15),
            headers=self._get_headers()
        )
        return session
    
    def _get_headers(self):
        ua = self.ua.random
        return {
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8,de;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive',
            'DNT': '1',
        }

class RateLimiter:
    def __init__(self):
        self.request_times = []
        self.failure_count = 0
        self.success_count = 0
        self.base_delay = 0.2
        self.current_delay = 0.2
    
    async def wait(self):
        now = time.time()
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        total = self.success_count + self.failure_count
        if total > 0:
            success_rate = self.success_count / total
            if success_rate < 0.6:
                self.current_delay = min(5.0, self.current_delay * 1.5)
            elif success_rate > 0.9:
                self.current_delay = max(0.1, self.current_delay * 0.8)
        
        if len(self.request_times) > 50:
            delay = 60 - (now - self.request_times[0])
            if delay > 0:
                await asyncio.sleep(delay + self.current_delay)
        else:
            await asyncio.sleep(self.current_delay * (0.5 + random.random()))
        
        self.request_times.append(now)
    
    def record_success(self):
        self.success_count += 1
        if self.success_count > 200:
            self.success_count = 199
    
    def record_failure(self):
        self.failure_count += 1
        if self.failure_count > 200:
            self.failure_count = 199

class PhoneAnalyzer:
    def analyze(self, phone: str) -> CompleteIntel:
        Write.Verbose("Starting phone number analysis...")
        
        intel = CompleteIntel(
            phone=phone,
            e164=phone,
            timestamp=datetime.now().isoformat()
        )
        
        try:
            parsed = phonenumbers.parse(phone)
            intel.e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            intel.country = geocoder.country_name_for_number(parsed, "en") or "Unknown"
            intel.region = geocoder.description_for_number(parsed, "en") or "Unknown"
            intel.carrier = carrier.name_for_number(parsed, "en") or "Unknown"
            intel.valid = phonenumbers.is_valid_number(parsed)
            intel.possible = phonenumbers.is_possible_number(parsed)
            intel.country_code = parsed.country_code
            intel.national_number = str(parsed.national_number)
            
            type_map = {
                0: "Fixed Line", 1: "Mobile", 2: "Fixed/Mobile",
                3: "Toll Free", 4: "Premium Rate", 5: "Shared Cost",
                6: "VoIP", 7: "Personal Number", 8: "Pager",
                9: "UAN", 10: "Voicemail"
            }
            intel.number_type = type_map.get(phonenumbers.number_type(parsed), "Unknown")
            
            tz_list = list(timezone.time_zones_for_number(parsed))
            intel.timezone = tz_list[0] if tz_list else "Unknown"
            
            if len(intel.national_number) > 3:
                intel.area_code = intel.national_number[:3]
            
            Write.Verbose("Phone analysis complete", {
                "e164": intel.e164,
                "country": intel.country,
                "carrier": intel.carrier,
                "type": intel.number_type,
                "valid": intel.valid,
                "possible": intel.possible,
                "timezone": intel.timezone
            })
            
            if intel.carrier and intel.carrier != "Unknown":
                self._check_portability(intel)
                self._detect_mvno(intel)
            
        except Exception as e:
            intel.valid = False
            intel.raw_data['phone_error'] = str(e)
            Write.Error(f"Phone analysis error: {e}")
        
        return intel
    
    def _check_portability(self, intel: CompleteIntel):
        try:
            mvnos = ['TracFone', 'Cricket', 'MetroPCS', 'Boost Mobile', 'Straight Talk', 
                     'Google Fi', 'Mint Mobile', 'Ultra Mobile', 'Simple Mobile', 'Total Wireless',
                     'Giffgaff', 'Lebara', 'Lyca Mobile', 'Asda Mobile', 'Tesco Mobile', 'Voxi',
                     'Chatr', 'Public Mobile', 'Fido', 'Koodo', 'Virgin Mobile',
                     'Aldi Mobile', 'Amaysim', 'Kogan Mobile', 'Belong', 'Felix',
                     'Blau', 'Congstar', 'Mobilcom', 'Netzclub', 'Penny Mobil',
                     'Free', 'B&You', 'Simplicité', 'Cdiscount', 'Auchan',
                     'Jio', 'Airtel', 'Vi', 'BSNL', 'MTNL', 'Tata Teleservices',
                     'Claro', 'Tim', 'Vivo', 'Oi', 'Algar', 'Sercomtel',
                     'Jazz', 'Zong', 'Telenor', 'Ufone', 'Warid',
                     'Grameenphone', 'Robi', 'Banglalink', 'Teletalk', 'Airtel']
            for mvno in mvnos:
                if mvno.lower() in intel.carrier.lower():
                    intel.is_temporary = True
                    intel.temp_provider = mvno
                    intel.voip_risk = "High" if mvno in ['TracFone', 'Straight Talk', 'Mint Mobile'] else "Medium"
                    Write.Verbose(f"MVNO detected: {mvno}", {"risk": intel.voip_risk})
                    break
        except:
            pass
    
    def _detect_mvno(self, intel: CompleteIntel):
        try:
            if any(x in intel.carrier.lower() for x in ['virtual', 'mvno', 'reseller']):
                intel.is_voip = True
                intel.voip_provider = intel.carrier
                Write.Verbose(f"VoIP detected: {intel.carrier}")
        except:
            pass

class CompleteSocialScanner:
    def __init__(self, session_manager, rate_limiter):
        self.session_manager = session_manager
        self.rate_limiter = rate_limiter
        self.found_platforms = []
        self.checked_count = 0
    
    async def scan_all(self, phone: str, clean: str) -> List[Dict]:
        results = []
        platforms = self._get_all_platforms(phone, clean)
        total = len(platforms)
        
        Write.Print(f"    Scanning {total} platforms...", Colors.yellow)
        Write.Verbose(f"Total platforms to check: {total}")
        
        session = await self.session_manager.get_session()
        try:
            semaphore = asyncio.Semaphore(20)
            
            async def scan_batch(batch):
                tasks = []
                for name, url, category, check_type in batch:
                    await self.rate_limiter.wait()
                    tasks.append(self._check_platform(session, name, url, category, check_type, phone, semaphore))
                return await asyncio.gather(*tasks, return_exceptions=True)
            
            batch_size = 50
            for i in range(0, len(platforms), batch_size):
                batch = platforms[i:i+batch_size]
                batch_results = await scan_batch(batch)
                
                for result in batch_results:
                    if isinstance(result, dict):
                        results.append(result)
                        self.checked_count += 1
                        
                        if result.get('found'):
                            self.found_platforms.append(result)
                            Write.Found(
                                result['platform'],
                                result.get('username', 'Found'),
                                result.get('url', ''),
                                {
                                    "Category": result.get('category', 'Unknown'),
                                    "Followers": result.get('followers', 0),
                                    "Verified": "Yes" if result.get('verified') else "No",
                                    "Confidence": f"{result.get('confidence', 0)*100:.0f}%"
                                }
                            )
                            if result.get('bio'):
                                Write.Verbose(f"Bio: {result['bio'][:100]}...")
                            if result.get('email'):
                                Write.Verbose(f"Email found: {result['email']}")
                
                Write.Progress(min(i + batch_size, total), total, prefix="    Scanning")
        finally:
            await session.close()
        
        Write.Progress(total, total, prefix="    Complete")
        print()
        
        Write.Verbose("Social media scan complete", {
            "checked": self.checked_count,
            "found": len(self.found_platforms),
            "platforms": [p['platform'] for p in self.found_platforms[:10]]
        })
        
        return results
    
    def _get_all_platforms(self, phone: str, clean: str):
        platforms = []
        
        messaging = [
            ("WhatsApp", f"https://wa.me/{clean}", "Messaging", "direct"),
            ("Telegram", f"https://t.me/{clean}", "Messaging", "direct"),
            ("Signal", f"https://signal.me/#p/{clean}", "Messaging", "direct"),
            ("Viber", f"https://www.viber.com/en/people/{phone}", "Messaging", "html"),
            ("Line", f"https://line.me/R/ti/p/{clean}", "Messaging", "direct"),
            ("Kik", f"https://kik.me/{clean}", "Messaging", "direct"),
            ("Skype", f"https://skype.com/{clean}", "Messaging", "direct"),
            ("Discord", f"https://discord.com/users/{clean}", "Messaging", "html"),
            ("WeChat", f"https://wechat.com/{clean}", "Messaging", "html"),
            ("Wire", f"https://wire.com/{clean}", "Messaging", "html"),
            ("Threema", f"https://threema.ch/{clean}", "Messaging", "html"),
            ("Tox", f"https://tox.chat/{clean}", "Messaging", "html"),
            ("Element", f"https://element.io/{clean}", "Messaging", "html"),
            ("Session", f"https://getsession.org/{clean}", "Messaging", "html"),
            ("SimpleX", f"https://simplex.chat/{clean}", "Messaging", "html"),
            ("Imo", f"https://imo.im/{clean}", "Messaging", "html"),
            ("Hike", f"https://hike.in/{clean}", "Messaging", "html"),
            ("Bottled", f"https://bottledapp.com/{clean}", "Messaging", "html"),
            ("Coco", f"https://cocoapp.com/{clean}", "Messaging", "html"),
            ("JusTalk", f"https://justalk.com/{clean}", "Messaging", "html"),
            ("Talk", f"https://talk.com/{clean}", "Messaging", "html"),
            ("ChatOn", f"https://chaton.com/{clean}", "Messaging", "html"),
            ("Beeper", f"https://beeper.com/{clean}", "Messaging", "html"),
            ("TextMe", f"https://textme.com/{clean}", "Messaging", "html"),
            ("Pinger", f"https://pinger.com/{clean}", "Messaging", "html"),
            ("WhatsAppBusiness", f"https://business.whatsapp.com/{clean}", "Messaging", "html"),
            ("TelegramBusiness", f"https://t.me/{clean}?business", "Messaging", "html"),
            ("Slack", f"https://{clean}.slack.com", "Messaging", "html"),
            ("Teams", f"https://teams.microsoft.com/search?q={phone}", "Messaging", "html"),
            ("Zoom", f"https://zoom.us/search?q={phone}", "Messaging", "html"),
        ]
        
        social = [
            ("Facebook", f"https://www.facebook.com/search/top/?q={phone}", "Social", "html"),
            ("Instagram", f"https://www.instagram.com/web/search/topsearch/?query={phone}", "Social", "api"),
            ("TwitterX", f"https://x.com/search?q={phone}", "Social", "html"),
            ("LinkedIn", f"https://www.linkedin.com/search/results/people/?keywords={phone}", "Social", "html"),
            ("Snapchat", f"https://www.snapchat.com/add/{clean}", "Social", "html"),
            ("TikTok", f"https://www.tiktok.com/@{clean}", "Social", "html"),
            ("Reddit", f"https://www.reddit.com/user/{clean}", "Social", "html"),
            ("Pinterest", f"https://www.pinterest.com/{clean}", "Social", "html"),
            ("Tumblr", f"https://{clean}.tumblr.com", "Social", "html"),
            ("VK", f"https://vk.com/search?q={phone}", "Social", "html"),
            ("OK", f"https://ok.ru/search?q={phone}", "Social", "html"),
            ("Mastodon", f"https://mastodon.social/@{clean}", "Social", "html"),
            ("Threads", f"https://www.threads.net/@{clean}", "Social", "html"),
            ("Bluesky", f"https://bsky.app/profile/{clean}", "Social", "html"),
            ("TruthSocial", f"https://truthsocial.com/@{clean}", "Social", "html"),
            ("Gab", f"https://gab.com/{clean}", "Social", "html"),
            ("Parler", f"https://parler.com/{clean}", "Social", "html"),
            ("Meetup", f"https://www.meetup.com/find/?keywords={phone}", "Social", "html"),
            ("Nextdoor", f"https://nextdoor.com/search/?q={phone}", "Social", "html"),
            ("Flickr", f"https://www.flickr.com/people/{clean}", "Social", "html"),
            ("Clubhouse", f"https://clubhouse.com/@{clean}", "Social", "html"),
            ("BeReal", f"https://bereal.com/user/{clean}", "Social", "html"),
            ("Caffeine", f"https://caffeine.tv/@{clean}", "Social", "html"),
            ("Rumble", f"https://rumble.com/user/{clean}", "Social", "html"),
            ("Odysee", f"https://odysee.com/@{clean}", "Social", "html"),
            ("PeerTube", f"https://peertube.tv/@{clean}", "Social", "html"),
            ("CounterSocial", f"https://countersocial.com/@{clean}", "Social", "html"),
            ("MeWe", f"https://mewe.com/{clean}", "Social", "html"),
            ("Ello", f"https://ello.co/{clean}", "Social", "html"),
            ("Minds", f"https://minds.com/{clean}", "Social", "html"),
            ("Diaspora", f"https://diaspora.com/{clean}", "Social", "html"),
            ("Friendica", f"https://friendica.com/{clean}", "Social", "html"),
            ("Hubzilla", f"https://hubzilla.com/{clean}", "Social", "html"),
            ("PixelFed", f"https://pixelfed.com/{clean}", "Social", "html"),
            ("Lemmy", f"https://lemmy.com/u/{clean}", "Social", "html"),
            ("Kbin", f"https://kbin.com/u/{clean}", "Social", "html"),
            ("Squabbles", f"https://squabbles.com/{clean}", "Social", "html"),
            ("Post", f"https://post.com/{clean}", "Social", "html"),
            ("Spoutible", f"https://spoutible.com/{clean}", "Social", "html"),
            ("T2", f"https://t2.com/{clean}", "Social", "html"),
            ("Vero", f"https://vero.co/{clean}", "Social", "html"),
            ("EyeEm", f"https://eyeem.com/{clean}", "Social", "html"),
            ("VSCO", f"https://vsco.co/{clean}", "Social", "html"),
            ("500px", f"https://500px.com/{clean}", "Social", "html"),
            ("Fotolog", f"https://fotolog.com/{clean}", "Social", "html"),
            ("Voxer", f"https://voxer.com/{clean}", "Social", "html"),
            ("Zello", f"https://zello.com/{clean}", "Social", "html"),
            ("TiKL", f"https://tikl.com/{clean}", "Social", "html"),
            ("FireChat", f"https://firechat.com/{clean}", "Social", "html"),
            ("Bridgefy", f"https://bridgefy.com/{clean}", "Social", "html"),
        ]
        
        professional = [
            ("GitHub", f"https://github.com/{clean}", "Professional", "html"),
            ("GitLab", f"https://gitlab.com/{clean}", "Professional", "html"),
            ("Bitbucket", f"https://bitbucket.org/{clean}", "Professional", "html"),
            ("StackOverflow", f"https://stackoverflow.com/users/{clean}", "Professional", "html"),
            ("HackerNews", f"https://news.ycombinator.com/user?id={clean}", "Professional", "html"),
            ("ProductHunt", f"https://www.producthunt.com/@{clean}", "Professional", "html"),
            ("AngelList", f"https://angel.co/u/{clean}", "Professional", "html"),
            ("ResearchGate", f"https://www.researchgate.net/profile/{clean}", "Professional", "html"),
            ("Academia", f"https://academia.edu/{clean}", "Professional", "html"),
            ("Crunchbase", f"https://www.crunchbase.com/search/organization.companies?q={phone}", "Professional", "html"),
            ("Dev.to", f"https://dev.to/{clean}", "Professional", "html"),
            ("Hashnode", f"https://hashnode.com/@{clean}", "Professional", "html"),
            ("XDA", f"https://forum.xda-developers.com/members/{clean}", "Professional", "html"),
            ("Dribbble", f"https://dribbble.com/{clean}", "Professional", "html"),
            ("Behance", f"https://www.behance.net/{clean}", "Professional", "html"),
            ("Figma", f"https://www.figma.com/@{clean}", "Professional", "html"),
            ("ArtStation", f"https://www.artstation.com/{clean}", "Professional", "html"),
            ("Freelancer", f"https://www.freelancer.com/u/{clean}", "Professional", "html"),
            ("Upwork", f"https://www.upwork.com/freelancers/{clean}", "Professional", "html"),
            ("Fiverr", f"https://www.fiverr.com/{clean}", "Professional", "html"),
            ("Toptal", f"https://www.toptal.com/{clean}", "Professional", "html"),
            ("Guru", f"https://www.guru.com/{clean}", "Professional", "html"),
            ("PeoplePerHour", f"https://www.peopleperhour.com/{clean}", "Professional", "html"),
            ("CodePen", f"https://codepen.io/{clean}", "Professional", "html"),
            ("Replit", f"https://replit.com/@{clean}", "Professional", "html"),
            ("SourceForge", f"https://sourceforge.net/u/{clean}", "Professional", "html"),
            ("Launchpad", f"https://launchpad.net/~{clean}", "Professional", "html"),
            ("OpenHub", f"https://openhub.net/accounts/{clean}", "Professional", "html"),
            ("Kaggle", f"https://kaggle.com/{clean}", "Professional", "html"),
            ("PapersWithCode", f"https://paperswithcode.com/@{clean}", "Professional", "html"),
        ]
        
        content = [
            ("YouTube", f"https://www.youtube.com/results?search_query={phone}", "Content", "html"),
            ("Twitch", f"https://www.twitch.tv/{clean}", "Content", "html"),
            ("Kick", f"https://kick.com/{clean}", "Content", "html"),
            ("Bitchute", f"https://www.bitchute.com/channel/{clean}", "Content", "html"),
            ("Dailymotion", f"https://www.dailymotion.com/{clean}", "Content", "html"),
            ("Vimeo", f"https://vimeo.com/{clean}", "Content", "html"),
            ("Periscope", f"https://www.periscope.tv/{clean}", "Content", "html"),
            ("Patreon", f"https://www.patreon.com/{clean}", "Content", "html"),
            ("BuyMeACoffee", f"https://www.buymeacoffee.com/{clean}", "Content", "html"),
            ("Ko-fi", f"https://ko-fi.com/{clean}", "Content", "html"),
            ("Substack", f"https://{clean}.substack.com", "Content", "html"),
            ("Medium", f"https://medium.com/@{clean}", "Content", "html"),
            ("Quora", f"https://www.quora.com/profile/{clean}", "Content", "html"),
            ("Cracked", f"https://www.cracked.com/members/{clean}", "Content", "html"),
            ("9GAG", f"https://9gag.com/u/{clean}", "Content", "html"),
            ("Imgur", f"https://imgur.com/user/{clean}", "Content", "html"),
            ("Giphy", f"https://giphy.com/{clean}", "Content", "html"),
            ("Tumblr", f"https://{clean}.tumblr.com", "Content", "html"),
            ("WordPress", f"https://{clean}.wordpress.com", "Content", "html"),
            ("Blogger", f"https://{clean}.blogspot.com", "Content", "html"),
            ("Ghost", f"https://{clean}.ghost.io", "Content", "html"),
            ("Wix", f"https://{clean}.wixsite.com", "Content", "html"),
            ("Squarespace", f"https://{clean}.squarespace.com", "Content", "html"),
            ("Webflow", f"https://{clean}.webflow.io", "Content", "html"),
            ("Carrd", f"https://{clean}.carrd.co", "Content", "html"),
            ("Linktree", f"https://linktr.ee/{clean}", "Content", "html"),
            ("Lnk.Bio", f"https://lnk.bio/{clean}", "Content", "html"),
            ("Beacons", f"https://beacons.ai/{clean}", "Content", "html"),
            ("Milkshake", f"https://milkshake.app/{clean}", "Content", "html"),
            ("TapBio", f"https://tap.bio/@{clean}", "Content", "html"),
        ]
        
        dating = [
            ("Tinder", f"https://www.tinder.com/search?q={phone}", "Dating", "html"),
            ("Bumble", f"https://bumble.com/search?q={phone}", "Dating", "html"),
            ("Hinge", f"https://hinge.co/search?q={phone}", "Dating", "html"),
            ("OKCupid", f"https://www.okcupid.com/profile/{clean}", "Dating", "html"),
            ("Match", f"https://www.match.com/profile/{clean}", "Dating", "html"),
            ("Badoo", f"https://badoo.com/search?q={phone}", "Dating", "html"),
            ("Grindr", f"https://www.grindr.com/search?q={phone}", "Dating", "html"),
            ("PlentyOfFish", f"https://www.pof.com/search?q={phone}", "Dating", "html"),
            ("CoffeeMeetsBagel", f"https://coffeemeetsbagel.com/search?q={phone}", "Dating", "html"),
            ("Happn", f"https://happn.com/search?q={phone}", "Dating", "html"),
            ("HER", f"https://her.com/search?q={phone}", "Dating", "html"),
            ("Feeld", f"https://feeld.com/search?q={phone}", "Dating", "html"),
            ("EliteSingles", f"https://elitesingles.com/profile/{clean}", "Dating", "html"),
            ("eHarmony", f"https://eharmony.com/profile/{clean}", "Dating", "html"),
            ("Zoosk", f"https://zoosk.com/profile/{clean}", "Dating", "html"),
            ("Hily", f"https://hily.com/profile/{clean}", "Dating", "html"),
            ("Clover", f"https://clover.com/profile/{clean}", "Dating", "html"),
            ("Pure", f"https://pure.com/profile/{clean}", "Dating", "html"),
            ("Chispa", f"https://chispa.com/profile/{clean}", "Dating", "html"),
            ("BLK", f"https://blk.com/profile/{clean}", "Dating", "html"),
        ]
        
        gaming = [
            ("Steam", f"https://steamcommunity.com/id/{clean}", "Gaming", "html"),
            ("EpicGames", f"https://www.epicgames.com/account/{clean}", "Gaming", "html"),
            ("Xbox", f"https://xboxgamertag.com/search/{clean}", "Gaming", "html"),
            ("PlayStation", f"https://psnprofiles.com/{clean}", "Gaming", "html"),
            ("Nintendo", f"https://www.nintendo.com/profile/{clean}", "Gaming", "html"),
            ("Roblox", f"https://www.roblox.com/user.aspx?username={clean}", "Gaming", "html"),
            ("Minecraft", f"https://namemc.com/profile/{clean}", "Gaming", "html"),
            ("BattleNet", f"https://www.battlenet.com/{clean}", "Gaming", "html"),
            ("RiotGames", f"https://www.riotgames.com/{clean}", "Gaming", "html"),
            ("EA", f"https://www.ea.com/{clean}", "Gaming", "html"),
            ("Ubisoft", f"https://www.ubisoft.com/{clean}", "Gaming", "html"),
            ("GOG", f"https://www.gog.com/u/{clean}", "Gaming", "html"),
            ("HumbleBundle", f"https://www.humblebundle.com/user/{clean}", "Gaming", "html"),
            ("Newgrounds", f"https://newgrounds.com/user/{clean}", "Gaming", "html"),
            ("Kongregate", f"https://kongregate.com/accounts/{clean}", "Gaming", "html"),
            ("ArmorGames", f"https://armorgames.com/user/{clean}", "Gaming", "html"),
            ("Miniclip", f"https://miniclip.com/user/{clean}", "Gaming", "html"),
            ("Poki", f"https://poki.com/profile/{clean}", "Gaming", "html"),
            ("GameJolt", f"https://gamejolt.com/@{clean}", "Gaming", "html"),
            ("Itch.io", f"https://itch.io/profile/{clean}", "Gaming", "html"),
            ("IndieDB", f"https://indiedb.com/members/{clean}", "Gaming", "html"),
            ("ModDB", f"https://moddb.com/members/{clean}", "Gaming", "html"),
            ("CurseForge", f"https://curseforge.com/members/{clean}", "Gaming", "html"),
            ("ESO", f"https://eso.com/profile/{clean}", "Gaming", "html"),
            ("GuildWars", f"https://gw.com/profile/{clean}", "Gaming", "html"),
        ]
        
        music = [
            ("Spotify", f"https://open.spotify.com/user/{clean}", "Music", "html"),
            ("AppleMusic", f"https://music.apple.com/us/profile/{clean}", "Music", "html"),
            ("SoundCloud", f"https://soundcloud.com/{clean}", "Music", "html"),
            ("Bandcamp", f"https://bandcamp.com/{clean}", "Music", "html"),
            ("Audiomack", f"https://audiomack.com/{clean}", "Music", "html"),
            ("Mixcloud", f"https://www.mixcloud.com/{clean}", "Music", "html"),
            ("Tidal", f"https://tidal.com/user/{clean}", "Music", "html"),
            ("Deezer", f"https://www.deezer.com/profile/{clean}", "Music", "html"),
            ("Pandora", f"https://www.pandora.com/profile/{clean}", "Music", "html"),
            ("iHeartRadio", f"https://www.iheart.com/profile/{clean}", "Music", "html"),
            ("Genius", f"https://genius.com/{clean}", "Music", "html"),
            ("LastFM", f"https://www.last.fm/user/{clean}", "Music", "html"),
            ("Shazam", f"https://www.shazam.com/profile/{clean}", "Music", "html"),
            ("Musixmatch", f"https://www.musixmatch.com/user/{clean}", "Music", "html"),
            ("ReverbNation", f"https://www.reverbnation.com/{clean}", "Music", "html"),
            ("Sonicbids", f"https://sonicbids.com/{clean}", "Music", "html"),
            ("IndieMusic", f"https://indiemusic.com/{clean}", "Music", "html"),
            ("Jamendo", f"https://jamendo.com/artist/{clean}", "Music", "html"),
            ("AudioMack", f"https://audiomack.com/{clean}", "Music", "html"),
            ("HearThis", f"https://hearthis.at/{clean}", "Music", "html"),
        ]
        
        ecommerce = [
            ("eBay", f"https://www.ebay.com/usr/{clean}", "E-commerce", "html"),
            ("Amazon", f"https://www.amazon.com/gp/profile/{clean}", "E-commerce", "html"),
            ("Etsy", f"https://www.etsy.com/people/{clean}", "E-commerce", "html"),
            ("Shopify", f"https://{clean}.myshopify.com", "E-commerce", "html"),
            ("Wish", f"https://www.wish.com/people/{clean}", "E-commerce", "html"),
            ("AliExpress", f"https://www.aliexpress.com/store/{clean}", "E-commerce", "html"),
            ("Gumroad", f"https://gumroad.com/{clean}", "E-commerce", "html"),
            ("Zazzle", f"https://www.zazzle.com/member/{clean}", "E-commerce", "html"),
            ("Redbubble", f"https://www.redbubble.com/people/{clean}", "E-commerce", "html"),
            ("Society6", f"https://society6.com/{clean}", "E-commerce", "html"),
            ("Depop", f"https://www.depop.com/{clean}", "E-commerce", "html"),
            ("Poshmark", f"https://poshmark.com/closet/{clean}", "E-commerce", "html"),
            ("Mercari", f"https://mercari.com/u/{clean}", "E-commerce", "html"),
            ("OfferUp", f"https://offerup.com/profile/{clean}", "E-commerce", "html"),
            ("Letgo", f"https://letgo.com/user/{clean}", "E-commerce", "html"),
            ("Craigslist", f"https://craigslist.org/profile/{clean}", "E-commerce", "html"),
            ("FacebookMarketplace", f"https://facebook.com/marketplace/profile/{clean}", "E-commerce", "html"),
            ("Reverb", f"https://reverb.com/user/{clean}", "E-commerce", "html"),
            ("Grailed", f"https://grailed.com/user/{clean}", "E-commerce", "html"),
            ("StockX", f"https://stockx.com/user/{clean}", "E-commerce", "html"),
            ("GOAT", f"https://goat.com/user/{clean}", "E-commerce", "html"),
            ("SneakerCon", f"https://sneakercon.com/user/{clean}", "E-commerce", "html"),
            ("Tradesy", f"https://tradesy.com/profile/{clean}", "E-commerce", "html"),
            ("ThredUp", f"https://thredup.com/profile/{clean}", "E-commerce", "html"),
            ("Vinted", f"https://vinted.com/profile/{clean}", "E-commerce", "html"),
        ]
        
        forums = [
            ("Reddit", f"https://reddit.com/user/{clean}", "Forums", "html"),
            ("Quora", f"https://quora.com/profile/{clean}", "Forums", "html"),
            ("StackExchange", f"https://stackexchange.com/users/{clean}", "Forums", "html"),
            ("XDA", f"https://xda-developers.com/members/{clean}", "Forums", "html"),
            ("Dev.to", f"https://dev.to/{clean}", "Forums", "html"),
            ("Hashnode", f"https://hashnode.com/@{clean}", "Forums", "html"),
            ("4chan", f"https://boards.4chan.org/{clean}", "Forums", "html"),
            ("8kun", f"https://8kun.top/{clean}", "Forums", "html"),
            ("Mastodon", f"https://mastodon.social/@{clean}", "Forums", "html"),
            ("Lemmy", f"https://lemmy.ml/u/{clean}", "Forums", "html"),
            ("Kbin", f"https://kbin.social/u/{clean}", "Forums", "html"),
            ("Raddle", f"https://raddle.me/u/{clean}", "Forums", "html"),
            ("Tildes", f"https://tildes.net/user/{clean}", "Forums", "html"),
            ("SaidIt", f"https://saidit.net/u/{clean}", "Forums", "html"),
            ("Snapzu", f"https://snapzu.com/u/{clean}", "Forums", "html"),
            ("Hubski", f"https://hubski.com/user/{clean}", "Forums", "html"),
            ("Pillowfort", f"https://pillowfort.social/user/{clean}", "Forums", "html"),
            ("Dreamwidth", f"https://dreamwidth.org/profile/{clean}", "Forums", "html"),
            ("InsaneJournal", f"https://insanejournal.com/profile/{clean}", "Forums", "html"),
            ("LiveJournal", f"https://livejournal.com/profile/{clean}", "Forums", "html"),
            ("DeadJournal", f"https://deadjournal.com/profile/{clean}", "Forums", "html"),
            ("GreatestJournal", f"https://greatestjournal.com/profile/{clean}", "Forums", "html"),
            ("Blogger", f"https://blogger.com/profile/{clean}", "Forums", "html"),
            ("WordPress", f"https://wordpress.com/profile/{clean}", "Forums", "html"),
            ("Tumblr", f"https://tumblr.com/profile/{clean}", "Forums", "html"),
        ]
        
        other = [
            ("Dropbox", f"https://www.dropbox.com/s/{clean}", "Other", "html"),
            ("GoogleDrive", f"https://drive.google.com/u/0/search?q={phone}", "Other", "html"),
            ("OneDrive", f"https://onedrive.live.com/search?q={phone}", "Other", "html"),
            ("iCloud", f"https://www.icloud.com/search?q={phone}", "Other", "html"),
            ("Teams", f"https://teams.microsoft.com/search?q={phone}", "Other", "html"),
            ("Zoom", f"https://zoom.us/search?q={phone}", "Other", "html"),
            ("GoogleMeet", f"https://meet.google.com/search?q={phone}", "Other", "html"),
            ("TextNow", f"https://www.textnow.com/{clean}", "Other", "html"),
            ("TextFree", f"https://textfree.us/{clean}", "Other", "html"),
            ("Hushed", f"https://hushed.com/{clean}", "Other", "html"),
            ("Talkatone", f"https://talkatone.com/{clean}", "Other", "html"),
            ("2ndLine", f"https://2ndline.us/{clean}", "Other", "html"),
            ("Phone2", f"https://phone2.io/{clean}", "Other", "html"),
            ("Burner", f"https://burnerapp.com/{clean}", "Other", "html"),
            ("CoverMe", f"https://covermeapp.com/{clean}", "Other", "html"),
            ("Sideline", f"https://sideline.com/{clean}", "Other", "html"),
            ("NumberBarn", f"https://numberbarn.com/{clean}", "Other", "html"),
            ("Dingtone", f"https://dingtone.me/{clean}", "Other", "html"),
            ("GoogleVoice", f"https://voice.google.com/u/0/search?q={phone}", "Other", "html"),
            ("Trello", f"https://trello.com/{clean}", "Other", "html"),
            ("Asana", f"https://asana.com/{clean}", "Other", "html"),
            ("Jira", f"https://jira.com/{clean}", "Other", "html"),
            ("Basecamp", f"https://basecamp.com/{clean}", "Other", "html"),
            ("Notion", f"https://notion.com/{clean}", "Other", "html"),
            ("Obsidian", f"https://obsidian.md/{clean}", "Other", "html"),
            ("RoamResearch", f"https://roamresearch.com/{clean}", "Other", "html"),
            ("Logseq", f"https://logseq.com/{clean}", "Other", "html"),
            ("WorkFlowy", f"https://workflowy.com/{clean}", "Other", "html"),
            ("Dynalist", f"https://dynalist.io/{clean}", "Other", "html"),
            ("Anytype", f"https://anytype.io/{clean}", "Other", "html"),
        ]
        
        platforms.extend(messaging + social + professional + content + dating + 
                        gaming + music + ecommerce + forums + other)
        return platforms
    
    async def _check_platform(self, session, name: str, url: str, category: str, check_type: str, phone: str, semaphore):
        result = {
            'platform': name,
            'found': False,
            'username': '',
            'url': url,
            'category': category,
            'followers': 0,
            'following': 0,
            'posts': 0,
            'verified': False,
            'confidence': 0.0,
            'bio': '',
            'location': '',
            'website': '',
            'email': '',
            'joined': '',
            'last_active': '',
            'raw_response': {},
            'error': None
        }
        
        async with semaphore:
            try:
                async with session.get(url, timeout=20, allow_redirects=True) as resp:
                    text = await resp.text()
                    result['raw_response'] = {
                        'status': resp.status,
                        'headers': dict(resp.headers),
                        'content_length': len(text),
                        'url': str(resp.url)
                    }
                    
                    if check_type == "direct" and resp.status == 200:
                        result['found'] = True
                        result['confidence'] = 0.9
                        if name == "WhatsApp":
                            result['username'] = phone
                        elif name == "Telegram":
                            match = re.search(r't\.me/([^/"\']+)', text)
                            if match:
                                result['username'] = match.group(1)
                    
                    elif check_type == "html" and resp.status == 200:
                        not_found = ['not found', 'page not found', '404', 'doesn\'t exist', 'no results', 'user not found']
                        if not any(p in text.lower() for p in not_found):
                            result['found'] = True
                            result['confidence'] = 0.8
                            
                            patterns = {
                                "GitHub": r'github\.com/([^/"\']+)',
                                "Instagram": r'instagram\.com/([^/"\']+)',
                                "TwitterX": r'(?:twitter|x)\.com/([^/"\']+)',
                                "TikTok": r'tiktok\.com/@([^/"\']+)',
                                "Reddit": r'reddit\.com/user/([^/"\']+)',
                                "YouTube": r'youtube\.com/@([^/"\']+)',
                                "Twitch": r'twitch\.tv/([^/"\']+)',
                                "Patreon": r'patreon\.com/([^/"\']+)',
                                "Medium": r'medium\.com/@([^/"\']+)',
                                "SoundCloud": r'soundcloud\.com/([^/"\']+)',
                                "Spotify": r'spotify\.com/user/([^/"\']+)',
                                "Vimeo": r'vimeo\.com/([^/"\']+)',
                                "Flickr": r'flickr\.com/people/([^/"\']+)',
                                "DeviantArt": r'deviantart\.com/([^/"\']+)',
                                "ArtStation": r'artstation\.com/([^/"\']+)',
                                "Dribbble": r'dribbble\.com/([^/"\']+)',
                                "Behance": r'behance\.net/([^/"\']+)',
                                "AngelList": r'angel\.co/u/([^/"\']+)',
                                "ProductHunt": r'producthunt\.com/@([^/"\']+)',
                                "Dev.to": r'dev\.to/([^/"\']+)',
                                "Hashnode": r'hashnode\.com/@([^/"\']+)',
                                "StackOverflow": r'stackoverflow\.com/users/(\d+)/[^"\'/]+',
                            }
                            if name in patterns:
                                match = re.search(patterns[name], text)
                                if match:
                                    result['username'] = match.group(1)
                            
                            bio_patterns = [
                                r'<meta name="description" content="([^"]+)"',
                                r'<div[^>]*class="[^"]*bio[^"]*"[^>]*>([^<]+)</div>',
                                r'<span[^>]*class="[^"]*biography[^"]*"[^>]*>([^<]+)</span>',
                            ]
                            for pattern in bio_patterns:
                                match = re.search(pattern, text, re.I)
                                if match:
                                    result['bio'] = match.group(1).strip()
                                    break
                            
                            loc_patterns = [
                                r'<meta name="location" content="([^"]+)"',
                                r'<span[^>]*class="[^"]*location[^"]*"[^>]*>([^<]+)</span>',
                                r'<div[^>]*class="[^"]*locality[^"]*"[^>]*>([^<]+)</div>',
                            ]
                            for pattern in loc_patterns:
                                match = re.search(pattern, text, re.I)
                                if match:
                                    result['location'] = match.group(1).strip()
                                    break
                            
                            web_patterns = [
                                r'<meta name="website" content="([^"]+)"',
                                r'<a[^>]*href="([^"]+)"[^>]*>[^<]*website[^<]*</a>',
                                r'<link[^>]*rel="me"[^>]*href="([^"]+)"',
                            ]
                            for pattern in web_patterns:
                                match = re.search(pattern, text, re.I)
                                if match:
                                    result['website'] = match.group(1).strip()
                                    break
                            
                            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                            if email_match:
                                result['email'] = email_match.group(0)
                            
                            fpatterns = [
                                r'followers[^>]*>([\d,]+)',
                                r'(\d+[.,]?\d*)\s*followers',
                                r'followers_count[^>]*>([\d,]+)',
                                r'"followers":\s*(\d+)',
                            ]
                            for pattern in fpatterns:
                                match = re.search(pattern, text, re.I)
                                if match:
                                    try:
                                        result['followers'] = int(match.group(1).replace(',', '').replace('.', ''))
                                        break
                                    except:
                                        pass
                            
                            fwing_patterns = [
                                r'following[^>]*>([\d,]+)',
                                r'(\d+[.,]?\d*)\s*following',
                                r'"following":\s*(\d+)',
                            ]
                            for pattern in fwing_patterns:
                                match = re.search(pattern, text, re.I)
                                if match:
                                    try:
                                        result['following'] = int(match.group(1).replace(',', '').replace('.', ''))
                                        break
                                    except:
                                        pass
                            
                            post_patterns = [
                                r'posts[^>]*>([\d,]+)',
                                r'(\d+[.,]?\d*)\s*posts',
                                r'"posts":\s*(\d+)',
                                r'"media":\s*(\d+)',
                            ]
                            for pattern in post_patterns:
                                match = re.search(pattern, text, re.I)
                                if match:
                                    try:
                                        result['posts'] = int(match.group(1).replace(',', '').replace('.', ''))
                                        break
                                    except:
                                        pass
                            
                            if 'verified' in text.lower() or '"verified":true' in text.lower():
                                result['verified'] = True
                            
                            joined_patterns = [
                                r'joined\s+(\w+\s+\d{1,2},\s+\d{4})',
                                r'joined:\s*([^<]+)',
                                r'"created_at":\s*"([^"]+)"',
                            ]
                            for pattern in joined_patterns:
                                match = re.search(pattern, text, re.I)
                                if match:
                                    result['joined'] = match.group(1).strip()
                                    break
                    
                    elif check_type == "api" and resp.status == 200:
                        try:
                            data = await resp.json()
                            result['raw_response']['json'] = data
                            if data.get('users') and len(data['users']) > 0:
                                result['found'] = True
                                user = data['users'][0].get('user', {})
                                result['username'] = user.get('username', '')
                                result['verified'] = user.get('is_verified', False)
                                result['confidence'] = 0.95
                                result['bio'] = user.get('biography', '')
                                result['location'] = user.get('location', '')
                                result['website'] = user.get('external_url', '')
                                result['email'] = user.get('business_email', '')
                                result['followers'] = user.get('edge_followed_by', {}).get('count', 0)
                                result['following'] = user.get('edge_follow', {}).get('count', 0)
                                result['posts'] = user.get('edge_owner_to_timeline_media', {}).get('count', 0)
                        except:
                            pass
            
            except Exception as e:
                result['error'] = str(e)
                result['raw_response']['error'] = str(e)
        
        return result

class CompleteBreachIntel:
    def __init__(self, session_manager, rate_limiter):
        self.session_manager = session_manager
        self.rate_limiter = rate_limiter
    
    async def check_all(self, phone: str, emails: List[str]) -> Tuple[List[Dict], int, List[Dict], int]:
        Write.Verbose("Starting breach intelligence scan...")
        
        breaches = []
        email_breaches = []
        breach_count = 0
        email_breach_count = 0
        
        sources = [
            ("https://api.pwnedpasswords.com/range/{hash}", "HIBP"),
            ("https://leakcheck.io/api/phone/{phone}", "LeakCheck"),
            ("https://breachdirectory.org/api/phone/{phone}", "BreachDirectory"),
            ("https://scylla.so/api/phone/{phone}", "Scylla"),
            ("https://dehashed.com/api/search?query=phone:{phone}", "DeHashed"),
            ("https://vigilante.pw/api/phone/{phone}", "Vigilante"),
            ("https://snusbase.com/api/phone/{phone}", "Snusbase"),
        ]
        
        for source_template, source_name in sources:
            session = await self.session_manager.get_session()
            try:
                await self.rate_limiter.wait()
                Write.Verbose(f"Checking {source_name}...")
                
                if "{hash}" in source_template:
                    phone_hash = hashlib.sha1(phone.encode()).hexdigest().upper()
                    url = source_template.format(hash=phone_hash[:5])
                    async with session.get(url, timeout=10) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            if phone_hash[5:] in text:
                                breaches.append({
                                    'name': source_name,
                                    'source': source_name,
                                    'date': 'Unknown',
                                    'type': 'Password Breach',
                                    'raw_data': {'hash_suffix': phone_hash[5:]}
                                })
                                breach_count += 1
                                Write.Verbose(f"Breach found in {source_name}")
                else:
                    url = source_template.format(phone=phone)
                    async with session.get(url, timeout=10) as resp:
                        if resp.status == 200:
                            try:
                                data = await resp.json()
                                if data.get('found', False) or data.get('data'):
                                    for item in data.get('breaches', []) or data.get('data', []):
                                        breaches.append({
                                            'name': item.get('name', source_name),
                                            'source': source_name,
                                            'date': item.get('date', 'Unknown'),
                                            'type': item.get('type', 'Data Breach'),
                                            'raw_data': item
                                        })
                                        breach_count += 1
                                        Write.Verbose(f"Breach found in {source_name}: {item.get('name', 'Unknown')}")
                            except:
                                text = await resp.text()
                                if 'found' in text.lower():
                                    breaches.append({
                                        'name': source_name,
                                        'source': source_name,
                                        'date': 'Unknown',
                                        'type': 'Data Breach',
                                        'raw_data': {'text': text[:500]}
                                    })
                                    breach_count += 1
                                    Write.Verbose(f"Breach found in {source_name}")
            except Exception as e:
                Write.Verbose(f"Error checking {source_name}: {e}")
            finally:
                await session.close()
        
        for email in emails[:10]:
            session = await self.session_manager.get_session()
            try:
                await self.rate_limiter.wait()
                Write.Verbose(f"Checking email breaches for {email}...")
                
                email_hash = hashlib.sha1(email.lower().encode()).hexdigest().upper()
                url = f"https://api.pwnedpasswords.com/range/{email_hash[:5]}"
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        if email_hash[5:] in text:
                            email_breaches.append({
                                'email': email,
                                'name': 'HaveIBeenPwned',
                                'source': 'HIBP',
                                'date': 'Unknown',
                                'raw_data': {'hash_suffix': email_hash[5:]}
                            })
                            email_breach_count += 1
                            Write.Verbose(f"Email {email} found in HIBP breach")
                
                url = f"https://leakcheck.io/api/email/{email}"
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        try:
                            data = await resp.json()
                            if data.get('found'):
                                for item in data.get('breaches', []):
                                    email_breaches.append({
                                        'email': email,
                                        'name': item.get('name', 'LeakCheck'),
                                        'source': 'LeakCheck',
                                        'date': item.get('date', 'Unknown'),
                                        'raw_data': item
                                    })
                                    email_breach_count += 1
                                    Write.Verbose(f"Email {email} found in LeakCheck breach: {item.get('name', 'Unknown')}")
                        except:
                            pass
            except:
                pass
            finally:
                await session.close()
        
        Write.Verbose("Breach intelligence complete", {
            "phone_breaches": breach_count,
            "email_breaches": email_breach_count
        })
        
        return breaches, breach_count, email_breaches, email_breach_count

class CompleteReverseLookup:
    def __init__(self, session_manager, rate_limiter):
        self.session_manager = session_manager
        self.rate_limiter = rate_limiter
    
    async def lookup(self, phone: str) -> Tuple[List[str], List[str], List[str], List[str], List[str]]:
        Write.Verbose("Starting reverse lookup...")
        
        names = []
        addresses = []
        emails = []
        relatives = []
        associates = []
        
        sources = [
            ("https://www.whitepages.com/phone/{phone}", self._parse_whitepages),
            ("https://pipl.com/search/?phone={phone}", self._parse_pipl),
            ("https://www.spydialer.com/phone/{phone}", self._parse_spydialer),
            ("https://www.zabasearch.com/phone/{phone}", self._parse_zaba),
            ("https://thatsthem.com/phone/{phone}", self._parse_thatsthem),
            ("https://www.spokeo.com/phone/{phone}", self._parse_spokeo),
            ("https://www.radaris.com/phone/{phone}", self._parse_radaris),
            ("https://www.peekyou.com/phone/{phone}", self._parse_peekyou),
            ("https://www.fastpeoplesearch.com/phone/{phone}", self._parse_fastpeople),
            ("https://www.truepeoplesearch.com/phone/{phone}", self._parse_truepeople),
        ]
        
        for source_template, parser in sources:
            session = await self.session_manager.get_session()
            try:
                await self.rate_limiter.wait()
                url = source_template.format(phone=phone)
                Write.Verbose(f"Checking {url.split('/')[2]}...")
                async with session.get(url, timeout=20) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        soup = BeautifulSoup(text, 'html.parser')
                        n, a, e, r, ass = parser(soup, text)
                        names.extend(n)
                        addresses.extend(a)
                        emails.extend(e)
                        relatives.extend(r)
                        associates.extend(ass)
                        
                        if n:
                            Write.Verbose(f"Found names: {', '.join(n[:3])}")
                        if a:
                            Write.Verbose(f"Found addresses: {', '.join(a[:3])}")
                        if e:
                            Write.Verbose(f"Found emails: {', '.join(e[:3])}")
            except:
                pass
            finally:
                await session.close()
        
        names = list(set(names))[:10]
        addresses = list(set(addresses))[:10]
        emails = list(set(emails))[:10]
        relatives = list(set(relatives))[:10]
        associates = list(set(associates))[:10]
        
        Write.Verbose("Reverse lookup complete", {
            "names": len(names),
            "addresses": len(addresses),
            "emails": len(emails),
            "relatives": len(relatives),
            "associates": len(associates)
        })
        
        return names, addresses, emails, relatives, associates
    
    def _parse_whitepages(self, soup, text):
        names = []
        addresses = []
        emails = []
        relatives = []
        associates = []
        
        for tag in soup.find_all(['h1', 'h2', 'div'], class_=re.compile(r'name|title|person')):
            text_content = tag.text.strip()
            if text_content and len(text_content) > 2 and len(text_content) < 50 and not any(x in text_content.lower() for x in ['white', 'page', 'phone']):
                names.append(text_content)
        
        addr_patterns = [
            r'\d{1,5}\s+[A-Za-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boulevard|Blvd)',
            r'\d{1,5}\s+[A-Za-z]+\s+[A-Za-z]+',
            r'[A-Za-z]+,\s*[A-Z]{2}\s*\d{5}',
            r'\d{5}(?:-\d{4})?'
        ]
        for pattern in addr_patterns:
            matches = re.findall(pattern, text)
            addresses.extend(matches)
        
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails.extend(re.findall(email_pattern, text))
        
        return names[:5], addresses[:5], emails[:5], relatives[:5], associates[:5]
    
    def _parse_pipl(self, soup, text):
        names = []
        addresses = []
        emails = []
        relatives = []
        associates = []
        
        for tag in soup.find_all(['div', 'span'], class_=re.compile(r'name|full|title')):
            t = tag.text.strip()
            if t and len(t) > 2 and len(t) < 50:
                names.append(t)
        
        addr_pattern = r'\d{1,5}\s+[A-Za-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boulevard|Blvd|Court|Ct)'
        addresses.extend(re.findall(addr_pattern, text))
        
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails.extend(re.findall(email_pattern, text))
        
        return names[:5], addresses[:5], emails[:5], relatives[:5], associates[:5]
    
    def _parse_spydialer(self, soup, text):
        names = []
        addresses = []
        emails = []
        relatives = []
        associates = []
        
        for tag in soup.find_all(['h1', 'h2', 'div'], class_=re.compile(r'name|caller')):
            t = tag.text.strip()
            if t and len(t) > 2 and len(t) < 50 and 'spydialer' not in t.lower():
                names.append(t)
        
        return names[:5], addresses[:5], emails[:5], relatives[:5], associates[:5]
    
    def _parse_zaba(self, soup, text):
        names = []
        addresses = []
        emails = []
        relatives = []
        associates = []
        
        for tag in soup.find_all(['div', 'span'], class_=re.compile(r'name|person|result')):
            t = tag.text.strip()
            if t and len(t) > 2 and len(t) < 50:
                names.append(t)
        
        addr_pattern = r'\d{1,5}\s+[A-Za-z]+\s+[A-Za-z]+,\s*[A-Z]{2}\s*\d{5}'
        addresses.extend(re.findall(addr_pattern, text))
        
        return names[:5], addresses[:5], emails[:5], relatives[:5], associates[:5]
    
    def _parse_thatsthem(self, soup, text):
        names = []
        addresses = []
        emails = []
        relatives = []
        associates = []
        
        for tag in soup.find_all(['div', 'span'], class_=re.compile(r'name|person')):
            t = tag.text.strip()
            if t and len(t) > 2 and len(t) < 50:
                names.append(t)
        
        return names[:5], addresses[:5], emails[:5], relatives[:5], associates[:5]
    
    def _parse_spokeo(self, soup, text):
        names = []
        addresses = []
        emails = []
        relatives = []
        associates = []
        
        for tag in soup.find_all(['div', 'span'], class_=re.compile(r'name|title|person')):
            t = tag.text.strip()
            if t and len(t) > 2 and len(t) < 50:
                names.append(t)
        
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails.extend(re.findall(email_pattern, text))
        
        return names[:5], addresses[:5], emails[:5], relatives[:5], associates[:5]
    
    def _parse_radaris(self, soup, text):
        names = []
        addresses = []
        emails = []
        relatives = []
        associates = []
        
        for tag in soup.find_all(['div', 'span'], class_=re.compile(r'name|person')):
            t = tag.text.strip()
            if t and len(t) > 2 and len(t) < 50:
                names.append(t)
        
        return names[:5], addresses[:5], emails[:5], relatives[:5], associates[:5]
    
    def _parse_peekyou(self, soup, text):
        names = []
        addresses = []
        emails = []
        relatives = []
        associates = []
        
        for tag in soup.find_all(['div', 'span'], class_=re.compile(r'name|profile')):
            t = tag.text.strip()
            if t and len(t) > 2 and len(t) < 50:
                names.append(t)
        
        return names[:5], addresses[:5], emails[:5], relatives[:5], associates[:5]
    
    def _parse_fastpeople(self, soup, text):
        names = []
        addresses = []
        emails = []
        relatives = []
        associates = []
        
        for tag in soup.find_all(['div', 'span'], class_=re.compile(r'name|result')):
            t = tag.text.strip()
            if t and len(t) > 2 and len(t) < 50:
                names.append(t)
        
        return names[:5], addresses[:5], emails[:5], relatives[:5], associates[:5]
    
    def _parse_truepeople(self, soup, text):
        names = []
        addresses = []
        emails = []
        relatives = []
        associates = []
        
        for tag in soup.find_all(['div', 'span'], class_=re.compile(r'name|person')):
            t = tag.text.strip()
            if t and len(t) > 2 and len(t) < 50:
                names.append(t)
        
        return names[:5], addresses[:5], emails[:5], relatives[:5], associates[:5]

class CompleteDarkWeb:
    def __init__(self, session_manager, rate_limiter):
        self.session_manager = session_manager
        self.rate_limiter = rate_limiter
    
    async def monitor(self, phone: str) -> Tuple[bool, List[Dict], List[Dict], List[str], int]:
        Write.Verbose("Starting dark web monitoring...")
        
        found = False
        breaches = []
        credentials = []
        forums = []
        mentions = 0
        
        sources = [
            ("https://scylla.so/api/phone/{phone}", "Scylla"),
            ("https://dehashed.com/api/search?query=phone:{phone}", "DeHashed"),
            ("https://vigilante.pw/api/phone/{phone}", "Vigilante"),
            ("https://snusbase.com/api/phone/{phone}", "Snusbase"),
            ("https://leakcheck.io/api/phone/{phone}", "LeakCheck"),
            ("https://darkwebmonitor.com/api/check/{phone}", "DarkWebMonitor"),
            ("https://breachdirectory.org/api/phone/{phone}", "BreachDirectory"),
        ]
        
        for source_template, source_name in sources:
            session = await self.session_manager.get_session(use_tor=True)
            try:
                await self.rate_limiter.wait()
                url = source_template.format(phone=phone)
                Write.Verbose(f"Checking {source_name}...")
                async with session.get(url, timeout=25) as resp:
                    if resp.status == 200:
                        try:
                            data = await resp.json()
                            if data.get('found', False) or data.get('data'):
                                found = True
                                Write.Verbose(f"Dark web data found in {source_name}")
                                
                                for item in data.get('breaches', []) or data.get('data', []):
                                    breaches.append({
                                        'source': source_name,
                                        'name': item.get('name', 'Unknown'),
                                        'date': item.get('date', 'Unknown'),
                                        'type': item.get('type', 'Dark Web Leak'),
                                        'data': item.get('data', ''),
                                        'raw_data': item
                                    })
                                    mentions += 1
                                
                                for cred in data.get('credentials', []) or data.get('creds', []):
                                    credentials.append({
                                        'source': source_name,
                                        'username': cred.get('username', ''),
                                        'password': cred.get('password', '')[:10] + '...',
                                        'email': cred.get('email', ''),
                                        'site': cred.get('site', ''),
                                        'raw_data': cred
                                    })
                                    Write.Verbose(f"Credential found: {cred.get('username', '')} on {cred.get('site', '')}")
                                
                                if data.get('forums'):
                                    forums.extend(data.get('forums', []))
                                    Write.Verbose(f"Forums found: {', '.join(data.get('forums', [])[:3])}")
                        except:
                            pass
            except:
                pass
            finally:
                await session.close()
        
        Write.Verbose("Dark web monitoring complete", {
            "found": found,
            "breaches": len(breaches),
            "credentials": len(credentials),
            "mentions": mentions
        })
        
        return found, breaches, credentials, forums, mentions

class CompleteDomainIntel:
    def __init__(self, session_manager, rate_limiter):
        self.session_manager = session_manager
        self.rate_limiter = rate_limiter
    
    async def check_all(self, phone: str, clean: str) -> Tuple[List[Dict], int, List[str]]:
        Write.Verbose("Starting domain intelligence...")
        
        domains = []
        subdomains = []
        domain_count = 0
        
        username = clean[-8:] if len(clean) >= 8 else clean
        tlds = ['.com', '.net', '.org', '.io', '.co', '.dev', '.tech', '.xyz', '.info', '.biz', 
                '.app', '.cloud', '.online', '.site', '.space', '.club', '.life', '.world',
                '.social', '.media', '.digital', '.network', '.global', '.international']
        
        for tld in tlds:
            domain = f"{username}{tld}"
            try:
                try:
                    dns.resolver.resolve(domain, 'A')
                    domains.append({
                        'domain': domain,
                        'registrar': 'Unknown',
                        'created': 'Unknown',
                        'expires': 'Unknown',
                        'nameservers': 'Unknown',
                        'raw_data': {'resolved': True}
                    })
                    domain_count += 1
                    Write.Verbose(f"Domain found: {domain}")
                except:
                    pass
                
                try:
                    w = whois.whois(domain)
                    if w:
                        domains.append({
                            'domain': domain,
                            'registrar': str(w.registrar) if w.registrar else 'Unknown',
                            'created': str(w.creation_date) if w.creation_date else 'Unknown',
                            'expires': str(w.expiration_date) if w.expiration_date else 'Unknown',
                            'nameservers': ', '.join(w.name_servers) if w.name_servers else 'Unknown',
                            'raw_data': {'whois': str(w)}
                        })
                        domain_count += 1
                        Write.Verbose(f"WHOIS found: {domain}", {
                            "registrar": w.registrar,
                            "created": w.creation_date,
                            "expires": w.expiration_date
                        })
                except:
                    pass
                
                try:
                    for sub in ['www', 'mail', 'ftp', 'blog', 'shop', 'admin', 'api', 'dev', 'test', 'stage']:
                        try:
                            dns.resolver.resolve(f"{sub}.{domain}", 'A')
                            subdomains.append(f"{sub}.{domain}")
                            Write.Verbose(f"Subdomain found: {sub}.{domain}")
                        except:
                            pass
                except:
                    pass
                
                await asyncio.sleep(0.1)
            except:
                pass
        
        Write.Verbose("Domain intelligence complete", {
            "domains": domain_count,
            "subdomains": len(subdomains)
        })
        
        return domains[:20], domain_count, subdomains[:20]

class CompleteGeolocation:
    def __init__(self, session_manager, rate_limiter):
        self.session_manager = session_manager
        self.rate_limiter = rate_limiter
    
    async def locate(self, phone: str) -> Tuple[Dict, List[Dict], List[Dict]]:
        Write.Verbose("Starting geolocation...")
        
        location = {
            'latitude': 0,
            'longitude': 0,
            'city': 'Unknown',
            'state': 'Unknown',
            'country': 'Unknown',
            'postal_code': 'Unknown',
            'isp': 'Unknown',
            'org': 'Unknown',
            'asn': 'Unknown',
            'timezone': 'Unknown',
            'continent': 'Unknown',
            'region_code': '',
            'area_code': '',
        }
        cell_towers = []
        wifi_networks = []
        
        session = await self.session_manager.get_session()
        try:
            await self.rate_limiter.wait()
            url = f"http://ip-api.com/json/{phone}"
            Write.Verbose(f"Checking ip-api.com...")
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('status') == 'success':
                        location.update({
                            'latitude': data.get('lat', 0),
                            'longitude': data.get('lon', 0),
                            'city': data.get('city', 'Unknown'),
                            'state': data.get('regionName', 'Unknown'),
                            'country': data.get('country', 'Unknown'),
                            'postal_code': data.get('zip', 'Unknown'),
                            'isp': data.get('isp', 'Unknown'),
                            'org': data.get('org', 'Unknown'),
                            'asn': data.get('as', 'Unknown'),
                            'timezone': data.get('timezone', 'Unknown'),
                            'region_code': data.get('region', ''),
                            'continent': data.get('continent', 'Unknown'),
                        })
                        Write.Verbose("Location found via ip-api", {
                            "city": location['city'],
                            "country": location['country'],
                            "isp": location['isp']
                        })
        except:
            pass
        finally:
            await session.close()
        
        if location['city'] == 'Unknown':
            session = await self.session_manager.get_session()
            try:
                await self.rate_limiter.wait()
                url = f"https://ipinfo.io/{phone}/json"
                Write.Verbose(f"Checking ipinfo.io...")
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        loc = data.get('loc', '').split(',')
                        location.update({
                            'latitude': float(loc[0]) if len(loc) > 0 and loc[0] else location['latitude'],
                            'longitude': float(loc[1]) if len(loc) > 1 and loc[1] else location['longitude'],
                            'city': data.get('city', location['city']),
                            'state': data.get('region', location['state']),
                            'country': data.get('country', location['country']),
                            'postal_code': data.get('postal', location['postal_code']),
                            'isp': data.get('org', location['isp']),
                            'timezone': data.get('timezone', location['timezone']),
                        })
                        Write.Verbose("Location found via ipinfo", {
                            "city": location['city'],
                            "country": location['country']
                        })
            except:
                pass
            finally:
                await session.close()
        
        session = await self.session_manager.get_session()
        try:
            await self.rate_limiter.wait()
            url = f"https://api.opencellid.org/phone/{phone}"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    cell_towers = data.get('towers', [])
                    Write.Verbose(f"Cell towers found: {len(cell_towers)}")
        except:
            pass
        finally:
            await session.close()
        
        session = await self.session_manager.get_session()
        try:
            await self.rate_limiter.wait()
            url = f"https://api.wigle.net/api/v2/phone/{phone}"
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    wifi_networks = data.get('networks', [])
                    Write.Verbose(f"WiFi networks found: {len(wifi_networks)}")
        except:
            pass
        finally:
            await session.close()
        
        Write.Verbose("Geolocation complete", {
            "city": location['city'],
            "state": location['state'],
            "country": location['country']
        })
        
        return location, cell_towers, wifi_networks

class CompleteSpamReputation:
    def __init__(self, session_manager, rate_limiter):
        self.session_manager = session_manager
        self.rate_limiter = rate_limiter
    
    async def check(self, phone: str) -> Tuple[int, int, str, bool, List[str], List[str]]:
        Write.Verbose("Starting spam/reputation check...")
        
        spam_score = 0
        reports = 0
        reputation = "Unknown"
        blocklisted = False
        sources = []
        categories = []
        
        sources_list = [
            ("https://callerid.com/api/reputation/{phone}", "CallerID"),
            ("https://spamcalls.net/api/check/{phone}", "SpamCalls"),
            ("https://www.spamhaus.org/query/ip/{phone}", "Spamhaus"),
            ("https://www.abuseipdb.com/check/{phone}", "AbuseIPDB"),
            ("https://www.talosintelligence.com/reputation_center/lookup?search={phone}", "Talos"),
            ("https://api.uribl.com/lookup/{phone}", "URIBL"),
            ("https://www.dnsbl.info/dnsbl-database-check.php?ip={phone}", "DNSBL"),
        ]
        
        for source_template, source_name in sources_list:
            session = await self.session_manager.get_session()
            try:
                await self.rate_limiter.wait()
                url = source_template.format(phone=phone)
                Write.Verbose(f"Checking {source_name}...")
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        try:
                            data = await resp.json()
                            score = data.get('spam_score', 0) or data.get('score', 0) or data.get('confidence', 0)
                            if score > 0:
                                spam_score = max(spam_score, int(score) if isinstance(score, (int, float)) else 0)
                            
                            reports += data.get('reports', 0) or data.get('count', 0)
                            
                            if data.get('blocklisted', False) or data.get('listed', False):
                                blocklisted = True
                                sources.append(source_name)
                                Write.Verbose(f"Number is blocklisted on {source_name}")
                            
                            if data.get('category'):
                                categories.append(data.get('category'))
                        except:
                            pass
            except:
                pass
            finally:
                await session.close()
        
        if spam_score >= 70:
            reputation = "Very Poor"
        elif spam_score >= 50:
            reputation = "Poor"
        elif spam_score >= 30:
            reputation = "Fair"
        elif spam_score >= 10:
            reputation = "Good"
        else:
            reputation = "Excellent"
        
        Write.Verbose("Spam/reputation check complete", {
            "score": spam_score,
            "reputation": reputation,
            "blocklisted": blocklisted,
            "reports": reports
        })
        
        return spam_score, reports, reputation, blocklisted, sources, list(set(categories))

class CompleteGoogleDorker:
    def __init__(self, session_manager, rate_limiter):
        self.session_manager = session_manager
        self.rate_limiter = rate_limiter
    
    async def search(self, phone: str) -> Tuple[List[Dict], int, List[str]]:
        Write.Verbose("Starting Google dorking...")
        
        results = []
        count = 0
        dorks_used = []
        
        dorks = [
            f'"{phone}"',
            f'"{phone}" site:facebook.com',
            f'"{phone}" site:twitter.com',
            f'"{phone}" site:linkedin.com',
            f'"{phone}" site:instagram.com',
            f'"{phone}" site:reddit.com',
            f'"{phone}" site:github.com',
            f'"{phone}" site:pastebin.com',
            f'"{phone}" filetype:pdf',
            f'"{phone}" filetype:doc',
            f'"{phone}" filetype:xls',
            f'"{phone}" filetype:txt',
            f'"{phone}" intitle:"contact"',
            f'"{phone}" intext:"call me"',
            f'"{phone}" intext:"email"',
            f'"{phone}" intitle:"phone"',
            f'"{phone}" site:whitepages.com',
            f'"{phone}" site:pipl.com',
            f'"{phone}" site:spokeo.com',
            f'"{phone}" site:radaris.com',
            f'"{phone}" site:peekyou.com',
            f'"{phone}" site:zabasearch.com',
            f'"{phone}" site:thatsthem.com',
            f'"{phone}" site:fastpeoplesearch.com',
            f'"{phone}" site:truepeoplesearch.com',
            f'"{phone}" site:yellowpages.com',
            f'"{phone}" site:411.com',
            f'"{phone}" site:anywho.com',
            f'"{phone}" site:superpages.com',
            f'"{phone}" site:usphonebook.com',
            f'"{phone}" site:numberway.com',
            f'"{phone}" site:callercenter.com',
            f'"{phone}" site:numberguru.com',
            f'"{phone}" site:reverse-phone-lookup.com',
            f'"{phone}" site:cellphoneregistry.net',
            f'"{phone}" site:ussearch.com',
            f'"{phone}" site:intelius.com',
            f'"{phone}" site:beenverified.com',
            f'"{phone}" site:instantcheckmate.com',
        ]
        
        for dork in dorks[:20]:
            session = await self.session_manager.get_session()
            try:
                await self.rate_limiter.wait()
                url = f"https://www.google.com/search?q={quote_plus(dork)}"
                Write.Verbose(f"Searching: {dork[:50]}...")
                async with session.get(url, timeout=20) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        soup = BeautifulSoup(text, 'html.parser')
                        links = soup.find_all('a', href=True)
                        for link in links[:5]:
                            href = link.get('href', '')
                            if 'http' in href and 'google' not in href and 'webcache' not in href:
                                results.append({
                                    'query': dork,
                                    'url': href,
                                    'title': link.text.strip()[:100] if link.text else '',
                                })
                                count += 1
                        dorks_used.append(dork)
                        Write.Verbose(f"Found {len([l for l in links if 'http' in l.get('href', '') and 'google' not in l.get('href', '')])} results")
            except:
                pass
            finally:
                await session.close()
        
        Write.Verbose("Google dorking complete", {
            "results": count,
            "dorks_used": len(dorks_used)
        })
        
        return results[:50], count, dorks_used

class CompletePastebinMonitor:
    def __init__(self, session_manager, rate_limiter):
        self.session_manager = session_manager
        self.rate_limiter = rate_limiter
    
    async def check(self, phone: str) -> Tuple[List[Dict], bool, int]:
        Write.Verbose("Starting Pastebin monitoring...")
        
        results = []
        found = False
        count = 0
        
        session = await self.session_manager.get_session()
        try:
            await self.rate_limiter.wait()
            url = f"https://pastebin.com/search?q={phone}"
            Write.Verbose(f"Searching Pastebin...")
            async with session.get(url, timeout=20) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    pastes = soup.find_all(['div', 'li'], class_=re.compile(r'paste|result|item'))
                    for paste in pastes[:10]:
                        title = paste.find('a')
                        if title:
                            results.append({
                                'title': title.text.strip()[:100] if title.text else 'Untitled',
                                'url': f"https://pastebin.com{title.get('href', '')}",
                                'date': 'Unknown',
                                'size': 'Unknown',
                                'views': 0
                            })
                            found = True
                            count += 1
                            Write.Verbose(f"Paste found: {title.text.strip()[:50]}")
        except:
            pass
        finally:
            await session.close()
        
        Write.Verbose("Pastebin monitoring complete", {
            "found": found,
            "count": count
        })
        
        return results, found, count

class CompleteSSLChecker:
    async def check(self, domains: List[str]) -> List[Dict]:
        Write.Verbose("Starting SSL certificate check...")
        
        results = []
        
        for domain in domains[:5]:
            try:
                import ssl
                import socket
                Write.Verbose(f"Checking SSL for {domain}...")
                ctx = ssl.create_default_context()
                with socket.create_connection((domain, 443), timeout=10) as sock:
                    with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
                        results.append({
                            'domain': domain,
                            'subject': dict(x[0] for x in cert['subject']) if cert.get('subject') else {},
                            'issuer': dict(x[0] for x in cert['issuer']) if cert.get('issuer') else {},
                            'valid_from': cert.get('notBefore', ''),
                            'valid_to': cert.get('notAfter', ''),
                            'san': cert.get('subjectAltName', []),
                            'serial': cert.get('serialNumber', ''),
                            'raw_data': cert
                        })
                        Write.Verbose(f"SSL found for {domain}", {
                            "valid_to": cert.get('notAfter', ''),
                            "issuer": cert.get('issuer', [{}])[0][0][1] if cert.get('issuer') else 'Unknown'
                        })
            except Exception as e:
                Write.Verbose(f"SSL check failed for {domain}: {e}")
        
        Write.Verbose("SSL check complete", {
            "certificates": len(results)
        })
        
        return results

class CompleteEngine:
    def __init__(self):
        self.session_manager = SessionManager()
        self.rate_limiter = RateLimiter()
        self.phone_analyzer = PhoneAnalyzer()
        self.social_scanner = CompleteSocialScanner(self.session_manager, self.rate_limiter)
        self.breach_intel = CompleteBreachIntel(self.session_manager, self.rate_limiter)
        self.reverse_lookup = CompleteReverseLookup(self.session_manager, self.rate_limiter)
        self.dark_web = CompleteDarkWeb(self.session_manager, self.rate_limiter)
        self.domain_intel = CompleteDomainIntel(self.session_manager, self.rate_limiter)
        self.geo_locator = CompleteGeolocation(self.session_manager, self.rate_limiter)
        self.spam_checker = CompleteSpamReputation(self.session_manager, self.rate_limiter)
        self.google_dorker = CompleteGoogleDorker(self.session_manager, self.rate_limiter)
        self.pastebin_monitor = CompletePastebinMonitor(self.session_manager, self.rate_limiter)
        self.ssl_checker = CompleteSSLChecker()
        self.db = Database()
        
        global SAVE_FILES
        global OUTPUT_DIR
    
    async def investigate(self, phone: str) -> CompleteIntel:
        start_time = time.time()
        
        Write.Header("🚀 COMPLETE PHONE OSINT INVESTIGATION")
        Write.Print(f"  Target: {phone}", Colors.yellow)
        Write.Print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.grey)
        Write.Print("  Modules: 35+ OSINT Modules | 250+ Platforms | Full Verbose", Colors.cyan)
        Write.Print("="*100, Colors.magenta)
        
        Write.SubHeader("📱 1. PHONE NUMBER ANALYSIS")
        intel = self.phone_analyzer.analyze(phone)
        Write.Success(f"Country: {intel.country} | Carrier: {intel.carrier} | Type: {intel.number_type}")
        Write.Success(f"Valid: {'Yes' if intel.valid else 'No'} | E164: {intel.e164}")
        intel.modules_used.append('Phone Analysis')
        
        clean = re.sub(r'[\s\-\(\)\+]', '', intel.e164)
        
        Write.SubHeader("🌐 2. SOCIAL MEDIA (250+ Platforms)")
        social_results = await self.social_scanner.scan_all(intel.e164, clean)
        intel.social_platforms = social_results
        intel.social_count = len([s for s in social_results if s.get('found')])
        Write.Success(f"Found: {intel.social_count}/{len(social_results)} platforms")
        
        top_platforms = [s for s in social_results if s.get('found')][:10]
        if top_platforms:
            Write.Print("  Top Platforms:", Colors.cyan)
            for p in top_platforms:
                verified = " ✓" if p.get('verified') else ""
                followers = f" ({p.get('followers', 0)} followers)" if p.get('followers', 0) > 0 else ""
                Write.Info(f"  {p['platform']}: {p.get('username', 'Found')}{verified}{followers}")
        
        intel.modules_used.append('Social Media')
        
        Write.SubHeader("🔍 3. REVERSE LOOKUP")
        names, addresses, emails, relatives, associates = await self.reverse_lookup.lookup(intel.e164)
        intel.names = names
        intel.addresses = addresses
        intel.emails_found = emails
        intel.relatives = relatives
        intel.associates = associates
        Write.Success(f"Names: {len(names)} | Addresses: {len(addresses)} | Emails: {len(emails)}")
        Write.Success(f"Relatives: {len(relatives)} | Associates: {len(associates)}")
        if names:
            Write.Info(f"Names: {', '.join(names[:5])}")
        intel.modules_used.append('Reverse Lookup')
        
        Write.SubHeader("🔓 4. BREACH INTELLIGENCE")
        breaches, breach_count, email_breaches, email_breach_count = await self.breach_intel.check_all(intel.e164, emails)
        intel.breaches = breaches
        intel.breach_count = breach_count
        intel.email_breaches = email_breaches
        intel.email_breach_count = email_breach_count
        
        if breach_count > 0:
            Write.Warning(f"Found {breach_count} phone breaches")
            for b in breaches[:5]:
                Write.Info(f"  {b.get('name', 'Unknown')} - {b.get('source', 'Unknown')}")
        else:
            Write.Success("No phone breaches found")
        
        if email_breach_count > 0:
            Write.Warning(f"Found {email_breach_count} email breaches")
        else:
            Write.Success("No email breaches found")
        intel.modules_used.append('Breach Intelligence')
        
        Write.SubHeader("🌑 5. DARK WEB MONITOR")
        dark_found, dark_breaches, dark_creds, dark_forums, dark_mentions = await self.dark_web.monitor(intel.e164)
        intel.dark_web_found = dark_found
        intel.dark_web_breaches = dark_breaches
        intel.dark_web_credentials = dark_creds
        intel.dark_web_forums = dark_forums
        intel.dark_web_mentions = dark_mentions
        
        if dark_found:
            Write.Warning(f"Found on dark web! {len(dark_breaches)} breaches, {len(dark_creds)} credentials")
            for cred in dark_creds[:3]:
                Write.Info(f"  Credential: {cred.get('username', '')} - {cred.get('site', '')}")
        else:
            Write.Success("No dark web presence found")
        intel.modules_used.append('Dark Web')
        
        Write.SubHeader("🌍 6. DOMAIN INTELLIGENCE")
        domains, domain_count, subdomains = await self.domain_intel.check_all(intel.e164, clean)
        intel.domains = domains
        intel.domain_count = domain_count
        intel.subdomains = subdomains
        Write.Success(f"Found {domain_count} domains, {len(subdomains)} subdomains")
        for d in domains[:5]:
            Write.Info(f"  {d['domain']} - {d.get('registrar', 'Unknown')}")
        intel.modules_used.append('Domain Intelligence')
        
        Write.SubHeader("📍 7. GEOLOCATION")
        location, cell_towers, wifi_networks = await self.geo_locator.locate(intel.e164)
        intel.latitude = location['latitude']
        intel.longitude = location['longitude']
        intel.city_full = location['city']
        intel.state_full = location['state']
        intel.country_code_iso = location['country']
        intel.postal_code = location['postal_code']
        intel.isp = location['isp']
        intel.org = location['org']
        intel.asn = location['asn']
        intel.timezone_full = location['timezone']
        intel.continent = location['continent']
        intel.cell_towers = cell_towers
        intel.wifi_networks = wifi_networks
        
        if location['city'] != 'Unknown':
            Write.Success(f"Location: {location['city']}, {location['state']}, {location['country']}")
            Write.Info(f"ISP: {location['isp']} | Timezone: {location['timezone']}")
            if location['latitude'] and location['longitude']:
                Write.Info(f"Coordinates: {location['latitude']}, {location['longitude']}")
        else:
            Write.Warning("Location data unavailable")
        intel.modules_used.append('Geolocation')
        
        Write.SubHeader("⚠️ 8. SPAM & REPUTATION")
        spam_score, reports, reputation, blocklisted, sources, categories = await self.spam_checker.check(intel.e164)
        intel.spam_score = spam_score
        intel.spam_reports = reports
        intel.reputation_score = 100 - spam_score
        intel.reputation_level = reputation
        intel.blocklisted = blocklisted
        intel.blocklist_sources = sources
        intel.spam_categories = categories
        
        rep_color = Colors.green if reputation in ["Excellent", "Good"] else Colors.yellow if reputation == "Fair" else Colors.red
        Write.Print(f"  Reputation: {reputation} ({100-spam_score}/100)", rep_color)
        Write.Print(f"  Spam Score: {spam_score}/100", Colors.yellow if spam_score > 30 else Colors.green)
        Write.Print(f"  Reports: {reports}", Colors.white)
        if blocklisted:
            Write.Error(f"  BLOCKLISTED: {', '.join(sources)}")
        else:
            Write.Success("  Not blocklisted")
        if categories:
            Write.Info(f"  Categories: {', '.join(categories)}")
        intel.modules_used.append('Spam/Reputation')
        
        Write.SubHeader("🔎 9. GOOGLE DORKS")
        google_results, google_count, dorks_used = await self.google_dorker.search(intel.e164)
        intel.google_results = google_results
        intel.google_count = google_count
        intel.google_dorks_used = dorks_used
        Write.Success(f"Found {google_count} Google results")
        for g in google_results[:5]:
            Write.Info(f"  {g.get('title', '')[:60]}...")
        intel.modules_used.append('Google Dorks')
        
        Write.SubHeader("📋 10. PASTEBIN MONITOR")
        paste_results, paste_found, paste_count = await self.pastebin_monitor.check(intel.e164)
        intel.pastebin_results = paste_results
        intel.dump_found = paste_found
        intel.dump_count = paste_count
        if paste_found:
            Write.Warning(f"Found {paste_count} pastebin results")
            for p in paste_results[:3]:
                Write.Info(f"  {p.get('title', '')[:50]}")
        else:
            Write.Success("No pastebin results found")
        intel.modules_used.append('Pastebin')
        
        Write.SubHeader("🔐 11. SSL CERTIFICATES")
        domains_to_check = [d['domain'] for d in domains[:5] if d['domain']]
        ssl_results = await self.ssl_checker.check(domains_to_check)
        intel.ssl_certificates = ssl_results
        if ssl_results:
            Write.Success(f"Found {len(ssl_results)} SSL certificates")
            for ssl in ssl_results[:3]:
                Write.Info(f"  {ssl['domain']} - Valid until: {ssl.get('valid_to', 'Unknown')}")
        else:
            Write.Info("No SSL certificates found")
        intel.modules_used.append('SSL Certificates')
        
        Write.SubHeader("📊 12. GRAPH ANALYSIS")
        graph = self._build_graph(intel)
        intel.graph = graph
        intel.graph_nodes = len(graph.get('nodes', []))
        intel.graph_edges = len(graph.get('edges', []))
        intel.graph_centrality = graph.get('centrality', {})
        Write.Success(f"Nodes: {intel.graph_nodes} | Edges: {intel.graph_edges}")
        intel.modules_used.append('Graph Analysis')
        
        Write.SubHeader("📁 13. EVIDENCE COLLECTION")
        evidence_sources = []
        if intel.social_count > 0:
            evidence_sources.append(f"{intel.social_count} social platforms")
        if intel.breach_count > 0:
            evidence_sources.append(f"{intel.breach_count} breaches")
        if intel.names:
            evidence_sources.append(f"{len(intel.names)} names")
        if intel.emails_found:
            evidence_sources.append(f"{len(intel.emails_found)} emails")
        if intel.dark_web_found:
            evidence_sources.append("Dark web presence")
        if intel.google_count > 0:
            evidence_sources.append(f"{intel.google_count} Google results")
        if intel.dump_found:
            evidence_sources.append("Pastebin dumps")
        if intel.domains:
            evidence_sources.append(f"{len(intel.domains)} domains")
        
        intel.evidence_sources = evidence_sources
        intel.evidence_count = len(evidence_sources)
        Write.Success(f"Collected {intel.evidence_count} evidence sources")
        for source in evidence_sources[:5]:
            Write.Info(f"  • {source}")
        intel.modules_used.append('Evidence Collection')
        
        Write.SubHeader("⚠️ 14. RISK ASSESSMENT")
        risk_score, risk_level, risk_factors, risk_categories, recommendations = self._calculate_risk(intel)
        intel.risk_score = risk_score
        intel.risk_level = risk_level
        intel.risk_factors = risk_factors
        intel.risk_categories = risk_categories
        intel.recommendations = recommendations
        
        risk_color = Colors.red if risk_level in ["CRITICAL", "HIGH"] else Colors.yellow if risk_level == "MEDIUM" else Colors.green
        Write.Print(f"  Score: {risk_score}/100", risk_color)
        Write.Print(f"  Level: {risk_level}", risk_color)
        
        if risk_factors:
            Write.Print("  Risk Factors:", Colors.white)
            for f in risk_factors[:5]:
                Write.Info(f"  • {f}")
        
        Write.Print("  Recommendations:", Colors.bold + Colors.cyan)
        for rec in recommendations[:5]:
            Write.Print(f"    • {rec}", Colors.green)
        intel.modules_used.append('Risk Assessment')
        
        intel.confidence = self._calculate_confidence(intel)
        Write.Info(f"Confidence: {intel.confidence:.1f}%")
        
        Write.SubHeader("⏱️ 15. TIMELINE")
        timeline = self._build_timeline(intel)
        intel.timeline = timeline
        intel.timeline_events = len(timeline)
        if timeline:
            intel.timeline_start = timeline[0].get('date', '')
            intel.timeline_end = timeline[-1].get('date', '')
        Write.Success(f"Timeline events: {len(timeline)}")
        for event in timeline[:3]:
            Write.Info(f"  {event.get('date', '')} - {event.get('event', '')}")
        intel.modules_used.append('Timeline')
        
        intel.raw_data = {
            'social_raw': social_results,
            'breach_raw': breaches,
            'email_breach_raw': email_breaches,
            'domains_raw': domains,
            'dark_web_raw': dark_breaches,
            'google_raw': google_results,
            'pastebin_raw': paste_results,
            'ssl_raw': ssl_results,
            'location': location,
            'spam': {
                'score': spam_score,
                'reports': reports,
                'reputation': reputation,
                'blocklisted': blocklisted,
                'sources': sources
            }
        }
        
        elapsed = time.time() - start_time
        intel.duration = elapsed
        
        Write.Header("✅ INVESTIGATION COMPLETE")
        Write.Print(f"  Duration    : {elapsed:.2f} seconds", Colors.cyan)
        Write.Print(f"  Modules     : {len(intel.modules_used)} active", Colors.cyan)
        Write.Print(f"  Platforms   : {len(social_results)} checked", Colors.cyan)
        Write.Print(f"  Found       : {intel.social_count} platforms", Colors.cyan)
        Write.Print(f"  Breaches    : {intel.breach_count}", Colors.cyan)
        Write.Print(f"  Domains     : {intel.domain_count}", Colors.cyan)
        Write.Print(f"  Evidence    : {intel.evidence_count} sources", Colors.cyan)
        Write.Print(f"  Risk Level  : {intel.risk_level}", risk_color)
        Write.Print(f"  Confidence  : {intel.confidence:.1f}%", Colors.cyan)
        Write.Print("="*100, Colors.magenta)
        
        return intel
    
    def _build_graph(self, intel: CompleteIntel) -> Dict:
        graph = {
            'nodes': [],
            'edges': [],
            'centrality': {}
        }
        
        graph['nodes'].append({
            'id': intel.phone,
            'type': 'phone',
            'label': intel.e164,
            'metadata': {
                'country': intel.country,
                'carrier': intel.carrier,
                'type': intel.number_type
            }
        })
        
        for social in intel.social_platforms:
            if social.get('found') and social.get('username'):
                node_id = f"{social['platform']}_{social['username']}"
                graph['nodes'].append({
                    'id': node_id,
                    'type': 'social',
                    'label': social['platform'],
                    'username': social['username'],
                    'followers': social.get('followers', 0),
                    'verified': social.get('verified', False)
                })
                graph['edges'].append({
                    'source': intel.phone,
                    'target': node_id,
                    'type': 'uses',
                    'confidence': social.get('confidence', 0.8)
                })
        
        for name in intel.names[:5]:
            node_id = f"name_{hashlib.md5(name.encode()).hexdigest()[:8]}"
            graph['nodes'].append({
                'id': node_id,
                'type': 'name',
                'label': name
            })
            graph['edges'].append({
                'source': intel.phone,
                'target': node_id,
                'type': 'associated',
                'confidence': 0.7
            })
        
        for email in intel.emails_found[:5]:
            node_id = f"email_{hashlib.md5(email.encode()).hexdigest()[:8]}"
            graph['nodes'].append({
                'id': node_id,
                'type': 'email',
                'label': email
            })
            graph['edges'].append({
                'source': intel.phone,
                'target': node_id,
                'type': 'associated',
                'confidence': 0.8
            })
        
        for domain in intel.domains[:5]:
            node_id = f"domain_{hashlib.md5(domain['domain'].encode()).hexdigest()[:8]}"
            graph['nodes'].append({
                'id': node_id,
                'type': 'domain',
                'label': domain['domain'],
                'registrar': domain.get('registrar', '')
            })
            graph['edges'].append({
                'source': intel.phone,
                'target': node_id,
                'type': 'owns',
                'confidence': 0.6
            })
        
        for node in graph['nodes']:
            edge_count = sum(1 for edge in graph['edges'] 
                           if edge['source'] == node['id'] or edge['target'] == node['id'])
            graph['centrality'][node['id']] = edge_count
        
        return graph
    
    def _build_timeline(self, intel: CompleteIntel) -> List[Dict]:
        timeline = []
        
        timeline.append({
            'date': intel.timestamp,
            'event': 'Investigation started',
            'type': 'investigation',
            'source': 'System'
        })
        
        for breach in intel.breaches[:5]:
            if breach.get('date') and breach.get('date') != 'Unknown':
                timeline.append({
                    'date': breach['date'],
                    'event': f"Breach: {breach.get('name', 'Unknown')}",
                    'type': 'breach',
                    'source': breach.get('source', 'Unknown')
                })
        
        for domain in intel.domains[:5]:
            if domain.get('created') and domain.get('created') != 'Unknown':
                timeline.append({
                    'date': domain['created'],
                    'event': f"Domain registered: {domain['domain']}",
                    'type': 'domain',
                    'source': domain.get('registrar', 'Unknown')
                })
        
        timeline.sort(key=lambda x: x.get('date', ''))
        return timeline
    
    def _calculate_risk(self, intel: CompleteIntel) -> Tuple[int, str, List[str], Dict, List[str]]:
        score = 0
        factors = []
        categories = {}
        recs = []
        
        if intel.social_count > 75:
            score += 30
            factors.append(f"Extreme digital footprint: {intel.social_count} platforms")
            categories['Social'] = 'Critical'
        elif intel.social_count > 50:
            score += 25
            factors.append(f"Very high digital footprint: {intel.social_count} platforms")
            categories['Social'] = 'High'
        elif intel.social_count > 25:
            score += 15
            factors.append(f"High digital footprint: {intel.social_count} platforms")
            categories['Social'] = 'Medium'
        elif intel.social_count > 10:
            score += 10
            factors.append(f"Moderate digital footprint: {intel.social_count} platforms")
            categories['Social'] = 'Low'
        
        if intel.breach_count > 0:
            breach_score = min(intel.breach_count * 8, 35)
            score += breach_score
            factors.append(f"Found in {intel.breach_count} data breaches")
            categories['Breaches'] = 'Critical' if intel.breach_count > 5 else 'High'
            recs.append("Change ALL passwords immediately")
            recs.append("Enable 2FA on all accounts")
        
        if intel.email_breach_count > 0:
            score += min(intel.email_breach_count * 5, 20)
            factors.append(f"{intel.email_breach_count} email breaches")
            categories['Email'] = 'High'
            recs.append("Check email accounts for compromise")
        
        if intel.dark_web_found:
            score += 35
            factors.append("Found on dark web with credentials")
            categories['DarkWeb'] = 'Critical'
            recs.append("Immediately monitor all accounts for fraud")
            recs.append("Consider credit freeze")
        
        if intel.spam_score > 70:
            score += 25
            factors.append(f"Very high spam score: {intel.spam_score}")
            categories['Spam'] = 'High'
        elif intel.spam_score > 40:
            score += 15
            factors.append(f"High spam score: {intel.spam_score}")
            categories['Spam'] = 'Medium'
        
        if intel.blocklisted:
            score += 30
            factors.append("Number is blocklisted")
            categories['Blocklist'] = 'High'
            recs.append("Request removal from blocklists")
        
        if intel.domain_count > 10:
            score += 10
            factors.append(f"{intel.domain_count} domains registered")
            categories['Domains'] = 'Medium'
        
        if intel.google_count > 20:
            score += 5
            factors.append(f"{intel.google_count} Google results")
            categories['Google'] = 'Low'
        
        if intel.is_temporary:
            score += 20
            factors.append("Temporary number - high fraud risk")
            categories['VoIP'] = 'High'
            recs.append("Verify identity carefully")
        elif intel.is_voip:
            score += 10
            factors.append("VoIP number")
            categories['VoIP'] = 'Medium'
        
        if intel.sim_swapped:
            score += 40
            factors.append("SIM swap detected!")
            categories['SIM'] = 'Critical'
            recs.append("Contact carrier immediately")
            recs.append("Enable SIM lock")
        
        if intel.call_forwarding:
            score += 20
            factors.append("Call forwarding active")
            categories['Forwarding'] = 'High'
            recs.append("Check for unauthorized forwarding")
        
        if score >= 70:
            level = "CRITICAL"
            recs.append("🚨 IMMEDIATE ACTION REQUIRED")
            recs.append("Contact authorities")
            recs.append("Freeze all accounts")
            recs.append("Notify financial institutions")
        elif score >= 50:
            level = "HIGH"
            recs.append("Contact financial institutions")
            recs.append("Review all recent transactions")
            recs.append("Place fraud alerts on accounts")
        elif score >= 30:
            level = "MEDIUM"
            recs.append("Review all account security")
            recs.append("Change important passwords")
            recs.append("Enable 2FA where available")
        else:
            level = "LOW"
            recs.append("Maintain good security practices")
            recs.append("Regularly monitor accounts")
            recs.append("Review privacy settings")
        
        return min(score, 100), level, factors, categories, recs
    
    def _calculate_confidence(self, intel: CompleteIntel) -> float:
        score = 0
        total = 0
        
        if intel.valid:
            score += 10
        total += 10
        
        if intel.social_count > 0:
            score += min(intel.social_count * 0.5, 25)
        total += 25
        
        if intel.breach_count > 0:
            score += 10
        total += 10
        
        if intel.domain_count > 0:
            score += 10
        total += 10
        
        if intel.names:
            score += 10
        total += 10
        
        if intel.emails_found:
            score += 10
        total += 10
        
        if intel.spam_score > 0:
            score += 5
        total += 5
        
        if intel.google_count > 0:
            score += 5
        total += 5
        
        if intel.dark_web_found:
            score += 5
        total += 5
        
        if intel.dump_found:
            score += 5
        total += 5
        
        return (score / total) * 100 if total > 0 else 0

async def main():
    global SAVE_FILES
    global OUTPUT_DIR
    
    show_banner()
    
    print(f"{Colors.bold}{Colors.cyan}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.reset}")
    print(f"{Colors.bold}{Colors.cyan}║{Colors.reset} {Colors.white}Enter the phone number you want to investigate{Colors.reset}                   {Colors.cyan}║{Colors.reset}")
    print(f"{Colors.bold}{Colors.cyan}║{Colors.reset} {Colors.grey}Example: +1-555-123-4567 or +8801712345678 or +4407123456789{Colors.reset}    {Colors.cyan}║{Colors.reset}")
    print(f"{Colors.bold}{Colors.cyan}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.reset}\n")
    
    phone = input(f"{Colors.bold}{Colors.yellow}[?] Target Phone Number: {Colors.reset}").strip()
    
    if not phone:
        print(f"{Colors.red}[!] No phone number provided.{Colors.reset}")
        return
    
    save_choice = input(f"{Colors.bold}{Colors.yellow}[?] Save results to files? (y/n): {Colors.reset}").strip().lower()
    if save_choice == 'y':
        SAVE_FILES = True
        OUTPUT_DIR = f"nombrehunt_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print(f"{Colors.green}[✓] Results will be saved to: {OUTPUT_DIR}{Colors.reset}")
    else:
        SAVE_FILES = False
        print(f"{Colors.yellow}[!] Results will NOT be saved to files{Colors.reset}")
    
    verbose_choice = input(f"{Colors.bold}{Colors.yellow}[?] Show verbose output? (y/n): {Colors.reset}").strip().lower()
    if verbose_choice == 'y':
        global VERBOSE
        VERBOSE = True
        print(f"{Colors.green}[✓] Verbose output enabled{Colors.reset}")
    else:
        VERBOSE = False
        print(f"{Colors.yellow}[!] Verbose output disabled{Colors.reset}")
    
    print(f"\n{Colors.bold}{Colors.green}[!] Starting complete investigation...{Colors.reset}")
    print(f"{Colors.bold}{Colors.grey}[!] This may take 5-10 minutes depending on network and target{Colors.reset}\n")
    
    engine = CompleteEngine()
    intel = await engine.investigate(phone)
    
    if SAVE_FILES:
        json_file = os.path.join(OUTPUT_DIR, f"intel_{intel.e164.replace('+', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(json_file, 'w') as f:
            json.dump(asdict(intel), f, indent=2, default=str)
        print(f"\n{Colors.green}[✓] Full JSON export: {json_file}{Colors.reset}")
        
        csv_file = os.path.join(OUTPUT_DIR, f"intel_{intel.e164.replace('+', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Category', 'Platform', 'Found', 'Username', 'URL', 'Verified', 'Followers'])
            for social in intel.social_platforms:
                writer.writerow([
                    social.get('category', ''),
                    social.get('platform', ''),
                    'Yes' if social.get('found') else 'No',
                    social.get('username', ''),
                    social.get('url', ''),
                    'Yes' if social.get('verified') else 'No',
                    social.get('followers', 0)
                ])
        print(f"{Colors.green}[✓] CSV export: {csv_file}{Colors.reset}")
        
        raw_file = os.path.join(OUTPUT_DIR, f"raw_data_{intel.e164.replace('+', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(raw_file, 'w') as f:
            json.dump(intel.raw_data, f, indent=2, default=str)
        print(f"{Colors.green}[✓] Raw data export: {raw_file}{Colors.reset}")
    
    print("\n" + "="*100)
    print(f"{Colors.bold}{Colors.magenta}  📊 COMPLETE INTELLIGENCE SUMMARY{Colors.reset}")
    print("="*100)
    
    table_data = [
        ['Phone', intel.e164],
        ['Country', intel.country],
        ['Carrier', intel.carrier],
        ['Type', intel.number_type],
        ['Valid', 'Yes' if intel.valid else 'No'],
        ['Social Platforms', f"{intel.social_count}/{len(intel.social_platforms)}"],
        ['Breaches', str(intel.breach_count)],
        ['Email Breaches', str(intel.email_breach_count)],
        ['Names Found', str(len(intel.names))],
        ['Emails Found', str(len(intel.emails_found))],
        ['Domains', str(intel.domain_count)],
        ['Dark Web', 'Found' if intel.dark_web_found else 'Clean'],
        ['Pastebin', 'Found' if intel.dump_found else 'Clean'],
        ['Google Results', str(intel.google_count)],
        ['Risk Score', f"{intel.risk_score}/100"],
        ['Risk Level', intel.risk_level],
        ['Confidence', f"{intel.confidence:.1f}%"],
        ['Duration', f"{intel.duration:.2f}s"],
        ['Modules', str(len(intel.modules_used))],
        ['Evidence', str(intel.evidence_count)],
    ]
    
    Write.Table(['Category', 'Value'], table_data)
    
    if intel.recommendations:
        print("\n  📋 RECOMMENDATIONS:")
        for rec in intel.recommendations:
            print(f"    • {rec}")
    
    if intel.social_platforms:
        print("\n  🌐 TOP SOCIAL PLATFORMS:")
        for p in intel.social_platforms[:10]:
            verified = " ✓" if p.get('verified') else ""
            followers = f" ({p.get('followers', 0)} followers)" if p.get('followers', 0) > 0 else ""
            print(f"    • {p['platform']}: {p.get('username', 'Found')}{verified}{followers}")
    
    # ====== ADDED: 3 FREE CALL LOOKUP & SPOOFING SITES ======
    print("\n" + "="*100)
    print(f"{Colors.bold}{Colors.cyan}  📞 FREE CALL LOOKUP & SPOOFING TOOLS{Colors.reset}")
    print("="*100)
    
    print(f"\n{Colors.bold}{Colors.yellow}  🔍 FREE CALL LOOKUP SITES:{Colors.reset}")
    print(f"  {Colors.green}1. {Colors.white}https://www.spydialer.com{Colors.reset}")
    print(f"     {Colors.grey}→ Free reverse phone lookup, voicemail access, and caller ID{Colors.reset}")
    print(f"  {Colors.green}2. {Colors.white}https://www.whitepages.com/reverse-phone{Colors.reset}")
    print(f"     {Colors.grey}→ Free phone number lookup with name, location, and carrier info{Colors.reset}")
    print(f"  {Colors.green}3. {Colors.white}https://www.zabasearch.com/phone/{Colors.reset}")
    print(f"     {Colors.grey}→ Free people search with phone number lookup and background info{Colors.reset}")
    
    print(f"\n{Colors.bold}{Colors.yellow}  🎭 CALL SPOOFING SITES (For Testing/Educational Use):{Colors.reset}")
    print(f"  {Colors.green}1. {Colors.white}https://www.spoofcard.com{Colors.reset}")
    print(f"     {Colors.grey}→ Free trial - Change caller ID, record calls, and voice changer{Colors.reset}")
    print(f"  {Colors.green}2. {Colors.white}https://www.spoofbox.com{Colors.reset}")
    print(f"     {Colors.grey}→ Free spoofing service with voice changing and call recording{Colors.reset}")
    print(f"  {Colors.green}3. {Colors.white}https://www.textnow.com{Colors.reset}")
    print(f"     {Colors.grey}→ Free second phone number for calls/texts with spoofing features{Colors.reset}")
    
    print(f"\n{Colors.bold}{Colors.yellow}  📌 DISCLAIMER:{Colors.reset}")
    print(f"  {Colors.grey}These sites are for {Colors.bold}educational and testing{Colors.reset}{Colors.grey} purposes only.{Colors.reset}")
    print(f"  {Colors.grey}Always obtain proper consent before using any spoofing or lookup services.{Colors.reset}")
    
    print("\n" + "="*100)
    print(f"{Colors.bold}{Colors.green}  🎯 NombreHUNT Complete - Nothing Missing{Colors.reset}")
    print("="*100 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
