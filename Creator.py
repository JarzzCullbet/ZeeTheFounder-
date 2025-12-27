#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elite Facebook Account Creator - Complete Ultimate Edition
Developer: ZeeTheFounder
Mobile (reg.py) + Desktop (main.py) Full Integration
Triple-Worker Architecture with Complete Menu System
"""

import sys
import time
import re
import random
import string
import sqlite3
import os
import json
import hashlib
import uuid
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from contextlib import contextmanager
from faker import Faker
from fake_useragent import UserAgent
import threading
from queue import Queue, Empty

# Configuration
W = 60
OUTPUT_FILE = "/sdcard/akunw.txt"
LOG_FILE = "/sdcard/fb_creator_logs.txt"
DB_FILE = "domains.db"
CONFIG_FILE = "config.json"
SHORTCUTS_FILE = "shortcuts.json"
API_BASE = "https://tinyhost.shop/api"
DOMAINS_PER_PAGE = 150

# Enhanced Color Palette
R = "\033[0m"
B = "\033[1m"
D = "\033[2m"
U = "\033[4m"
P1 = "\033[38;5;93m"
P2 = "\033[38;5;99m"
P3 = "\033[38;5;135m"
P4 = "\033[38;5;141m"
P5 = "\033[38;5;177m"
PK = "\033[38;5;213m"
MG = "\033[38;5;201m"
CY = "\033[38;5;51m"
WH = "\033[38;5;231m"
GR = "\033[38;5;240m"
GN = "\033[38;5;46m"
RD = "\033[38;5;196m"
YL = "\033[38;5;226m"
BL = "\033[38;5;39m"
OR = "\033[38;5;214m"
BG1 = "\033[48;5;93m"
BG2 = "\033[48;5;213m"

# Default Config
DEFAULT_CONFIG = {
    "endpoint": "desktop",
    "gender": "random",
    "password_type": "auto",
    "custom_password": "",
    "min_age": 18,
    "max_age": 35,
    "use_gmail": False,
    "use_phone": False,
    "use_tinyhost": True,
    "use_manual_email": False,
    "account_limit": 10,
    "otp_timeout": 15,
    "otp_check_interval": 1,
    "name_type": "filipino"
}

config = DEFAULT_CONFIG.copy()
fake_id = Faker('id_ID')
lock = threading.Lock()
log_lock = threading.Lock()

# Worker Queues
creation_queue = Queue()
monitor_queue = Queue()
verify_queue = Queue()

# Statistics
stats = {
    "total_created": 0,
    "total_verified": 0,
    "total_with_cookies": 0,
    "total_failed": 0,
    "worker1_status": "Idle",
    "worker2_status": "Idle",
    "worker3_status": "Idle",
    "ok_count": 0,
    "cp_count": 0
}

# FILE LOGGING SYSTEM
def write_log(message, level="INFO"):
    """Write logs to file only, keep terminal clean"""
    try:
        with log_lock:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] {message}\n"
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry)
    except:
        pass

def clear_logs():
    """Clear log file at start"""
    try:
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        write_log("=" * 80, "SYSTEM")
        write_log("Facebook Creator - New Session Started", "SYSTEM")
        write_log("=" * 80, "SYSTEM")
    except:
        pass

# NAME DATABASES
FILIPINO_FIRST_NAMES_MALE = [
    'Juan', 'Jose', 'Miguel', 'Gabriel', 'Rafael', 'Antonio', 'Carlos', 'Luis',
    'Marco', 'Paolo', 'Angelo', 'Joshua', 'Christian', 'Mark', 'John', 'James',
    'Daniel', 'David', 'Michael', 'Jayson', 'Kenneth', 'Ryan', 'Kevin', 'Neil',
    'Jerome', 'Renzo', 'Carlo', 'Andres', 'Felipe', 'Diego', 'Mateo', 'Lucas',
    'Adrian', 'Albert', 'Aldrin', 'Alfred', 'Allen', 'Alonzo', 'Amiel',
    'Andre', 'Andrew', 'Angelo', 'Anton', 'Arden', 'Aries', 'Arman', 'Arnel',
    'Arnold', 'Arthur', 'August', 'Avery', 'Benito', 'Benjamin', 'Bernard'
]

FILIPINO_FIRST_NAMES_FEMALE = [
    'Maria', 'Ana', 'Sofia', 'Isabella', 'Gabriela', 'Valentina', 'Camila',
    'Angelica', 'Nicole', 'Michelle', 'Christine', 'Sarah', 'Jessica',
    'Andrea', 'Patricia', 'Jennifer', 'Karen', 'Ashley', 'Jasmine', 'Princess',
    'Angel', 'Joyce', 'Kristine', 'Diane', 'Joanna', 'Carmela', 'Isabel',
    'Lucia', 'Elena', 'Abigail', 'Adeline', 'Adrienne', 'Agnes', 'Aileen'
]

FILIPINO_LAST_NAMES = [
    'Reyes', 'Santos', 'Cruz', 'Bautista', 'Garcia', 'Flores', 'Gonzales',
    'Martinez', 'Ramos', 'Mendoza', 'Rivera', 'Torres', 'Fernandez', 'Lopez',
    'Castillo', 'Aquino', 'Villanueva', 'Santiago', 'Dela Cruz', 'Perez',
    'Castro', 'Mercado', 'Domingo', 'Gutierrez', 'Ramirez', 'Valdez'
]

RPW_NAMES_MALE = [
    'Zephyr', 'Shadow', 'Phantom', 'Blaze', 'Storm', 'Frost', 'Raven', 'Ace',
    'Knight', 'Wolf', 'Dragon', 'Phoenix', 'Thunder', 'Void', 'Eclipse',
    'Nexus', 'Atlas', 'Orion', 'Dante', 'Xavier', 'Axel', 'Kai', 'Ryker',
    'Jax', 'Cole', 'Zane', 'Blake', 'Rex', 'Ash', 'Chase', 'Zero', 'Jet'
]

RPW_NAMES_FEMALE = [
    'Luna', 'Aurora', 'Mystic', 'Crystal', 'Sapphire', 'Scarlet', 'Violet',
    'Rose', 'Athena', 'Venus', 'Nova', 'Stella', 'Serena', 'Raven', 'Jade',
    'Ruby', 'Pearl', 'Ivy', 'Willow', 'Hazel', 'Skye', 'Aria', 'Melody',
    'Harmony', 'Grace', 'Faith', 'Hope', 'Trinity', 'Destiny', 'Serenity'
]

RPW_LAST_NAMES = [
    'Shadow', 'Dark', 'Light', 'Star', 'Moon', 'Sun', 'Sky', 'Night', 'Dawn',
    'Storm', 'Frost', 'Fire', 'Stanley', 'Nero', 'Clifford', 'Volsckev',
    'Draven', 'Smith', 'Greisler', 'Wraith', 'Hale', 'Voss', 'Lockhart',
    'Ashford', 'Wynters', 'Grayson', 'Ravenwood', 'Langford', 'Averill'
]

proxies_dict = {}

def load_proxies():
    """Load proxies from multiple sources"""
    proxy_sources = {
        "http": [
            "https://raw.githubusercontent.com/ERRORDEATH-403/PROXY/main/http_proxies.txt",
            "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt",
            "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        ]
    }
    proxies = {}
    for ptype, urls in proxy_sources.items():
        proxies[ptype] = []
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    proxies[ptype].extend([proxy.strip() for proxy in response.text.splitlines()])
            except:
                continue
    return proxies

def get_random_proxy():
    """Get random proxy if enabled"""
    if not config.get('use_proxy', False):
        return None
    
    global proxies_dict
    if not proxies_dict:
        proxies_dict = load_proxies()
    
    available_types = [ptype for ptype, lst in proxies_dict.items() if lst]
    if not available_types:
        return None
    ptype = random.choice(available_types)
    return {ptype: random.choice(proxies_dict[ptype])}

# ADVANCED UI EFFECTS
def clear():
    os.system('clear' if os.name != 'nt' else 'cls')

def loading_animation(text, duration=2):
    frames = ['o', 'O', 'o', 'O']
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        frame = frames[i % len(frames)]
        print(f"\r{P4}{frame}{R} {text}...", end='', flush=True)
        time.sleep(0.1)
        i += 1
    print(f"\r{GN}*{R} {text}... {B}{GN}Done{R}")

def W_ueragent():
    chrome_versions = [(80, 3987, 163), (90, 4430, 212), (100, 4896, 127)]
    webkit_versions = [(537, 36), (537, 36), (537, 36)]
    safari_versions = [500, 600]
    windows_versions = [(10, 0), (10, 1), (11, 0)]
    chrome_version = random.choice(chrome_versions)
    webkit_version = random.choice(webkit_versions)
    safari_version = random.choice(safari_versions)
    windows_version = random.choice(windows_versions)
    is_win64 = random.choice([True, False])
    win64_str = 'Win64; x64' if is_win64 else 'WOW64'
    user_agent = (
        f'Mozilla/5.0 (Windows NT {windows_version[0]}.{windows_version[1]}; {win64_str}) '
        f'AppleWebKit/{webkit_version[0]}.{webkit_version[1]} (KHTML, like Gecko) '
        f'Chrome/{chrome_version[0]}.{chrome_version[1]}.{chrome_version[2]} Safari/{safari_version}'
    )
    return user_agent

def progress_bar_download(current, total, prefix=''):
    percent = int((current / total) * 100)
    filled = int((50) * current // total)
    bar = f"{P3}{'#' * filled}{P1}{'.' * (50 - filled)}{R}"
    print(f"\r{prefix} {bar} {B}{percent}%{R} ({current}/{total})", end='', flush=True)

def typewriter_effect(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def enhanced_banner():
    clear()
    print(f"""
{P1}+============================================================+
{P1}|{P2}############################################################{P1}|
{P1}|{P3}##{P4}+====================================================+{P3}##{P1}|
{P1}|{P3}##{P4}|{PK}   FACEBOOK CREATOR - UNIFIED EDITION          {P4}|{P3}##{P1}|
{P1}|{P3}##{P4}|{PK}   Triple-Worker Architecture                   {P4}|{P3}##{P1}|
{P1}|{P3}##{P4}|{P5}   Create -> Monitor -> Verify -> Extract       {P4}|{P3}##{P1}|
{P1}|{P3}##{P4}|{CY}   Mobile + Desktop Endpoints                    {P4}|{P3}##{P1}|
{P1}|{P3}##{P4}|{BL}   File Logging System Enabled                  {P4}|{P3}##{P1}|
{P1}|{P3}##{P4}+====================================================+{P3}##{P1}|
{P1}|{P2}############################################################{P1}|
{P1}+============================================================+{R}

{P3}+============================================================+
{P3}|{R}            {B}{PK}Developer: ZeeTheFounder{R}                     {P3}|
{P3}+============================================================+{R}
""")

def banner():
    enhanced_banner()

def box(title, lines=None, color=P3):
    print(f"\n{color}+{'-' * (W-2)}+{R}")
    if title:
        t_pad = (W - 4 - len(title)) // 2
        print(f"{color}|{R} {' ' * t_pad}{B}{WH}{title}{R}{' ' * (W - 4 - t_pad - len(title))} {color}|{R}")
    if lines:
        print(f"{color}+{'-' * (W-2)}+{R}")
        for line in lines:
            clean = re.sub(r'\033\[[0-9;]+m', '', line)
            pad = W - 4 - len(clean)
            print(f"{color}|{R} {line}{' ' * pad} {color}|{R}")
    print(f"{color}+{'-' * (W-2)}+{R}")

def box_fade_in(title, lines=None, color=P3):
    print(f"\n{color}+{'-' * (W-2)}+{R}")
    time.sleep(0.05)
    if title:
        t_pad = (W - 4 - len(title)) // 2
        print(f"{color}|{R} {' ' * t_pad}{B}{WH}{title}{R}{' ' * (W - 4 - t_pad - len(title))} {color}|{R}")
        time.sleep(0.05)
    if lines:
        print(f"{color}+{'-' * (W-2)}+{R}")
        time.sleep(0.05)
        for line in lines:
            clean = re.sub(r'\033\[[0-9;]+m', '', line)
            pad = W - 4 - len(clean)
            print(f"{color}|{R} {line}{' ' * pad} {color}|{R}")
            time.sleep(0.05)
    print(f"{color}+{'-' * (W-2)}+{R}")

def divider(char="-", color=P3):
    print(f"{color}{char * W}{R}")

def get_input(prompt):
    sys.stdout.write(f"{P4}>>> {B}{WH}{prompt}: {R}")
    sys.stdout.flush()
    return input().strip()

def display_account_ok(uid, password, email, cookies, creation_time):
    print(f"\n{GN}{'-' * W}{R}")
    print(f"{BG1}{B}{WH}  * ACCOUNT OK - SUCCESSFULLY CREATED  {R}".center(W + 35))
    print(f"{GN}{'-' * W}{R}\n")
    
    time.sleep(0.1)
    
    box_lines = [
        f"{CY}UID        :{R} {B}{WH}{uid}{R}",
        f"{CY}Password   :{R} {B}{WH}{password}{R}",
        f"{CY}Email      :{R} {B}{WH}{email}{R}",
        f"{CY}Created At :{R} {B}{WH}{creation_time}{R}",
        "",
        f"{GN}Cookies:{R}",
        f"{D}{cookies[:55]}...{R}" if len(cookies) > 58 else f"{D}{cookies}{R}"
    ]
    
    box("ACCOUNT DETAILS", box_lines, GN)
    print(f"{GN}{'-' * W}{R}\n")

# DATABASE
@contextmanager
def db_conn():
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        write_log(f"DB error: {e}", "ERROR")
        raise
    finally:
        conn.close()

def init_db():
    with db_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT UNIQUE NOT NULL,
                tld TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def get_tld_stats():
    try:
        with db_conn() as conn:
            cursor = conn.execute("SELECT tld, COUNT(*) as count FROM domains GROUP BY tld ORDER BY count DESC")
            return {row['tld']: row['count'] for row in cursor.fetchall()}
    except:
        return {}

def get_domains_by_tld(tld, page=1):
    try:
        with db_conn() as conn:
            cursor = conn.execute("SELECT COUNT(*) as total FROM domains WHERE tld = ?", (tld,))
            total = cursor.fetchone()['total']
            offset = (page - 1) * DOMAINS_PER_PAGE
            cursor = conn.execute("SELECT domain FROM domains WHERE tld = ? ORDER BY domain LIMIT ? OFFSET ?", (tld, DOMAINS_PER_PAGE, offset))
            domains = [row['domain'] for row in cursor.fetchall()]
            total_pages = (total + DOMAINS_PER_PAGE - 1) // DOMAINS_PER_PAGE
            return domains, total_pages, total
    except:
        return [], 0, 0

def search_domain(domain_query):
    try:
        with db_conn() as conn:
            cursor = conn.execute("SELECT domain FROM domains WHERE domain LIKE ?", (f"%{domain_query}%",))
            return [row['domain'] for row in cursor.fetchall()]
    except:
        return []

# CONFIG & SHORTCUTS
def load_config():
    global config
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config.update(json.load(f))
    except:
        pass

def save_config():
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        pass

def load_shortcuts():
    try:
        if os.path.exists(SHORTCUTS_FILE):
            with open(SHORTCUTS_FILE, 'r') as f:
                return json.load(f)
    except:
        return {}
    return {}

def save_shortcuts(shortcuts):
    try:
        with open(SHORTCUTS_FILE, 'w') as f:
            json.dump(shortcuts, f, indent=2)
    except:
        pass

# NAME GENERATORS
def get_filipino_name(gender):
    if gender == '1':
        first_name = random.choice(FILIPINO_FIRST_NAMES_MALE)
    else:
        first_name = random.choice(FILIPINO_FIRST_NAMES_FEMALE)
    last_name = random.choice(FILIPINO_LAST_NAMES)
    return first_name, last_name

def get_rpw_name(gender):
    if gender == '1':
        first_name = random.choice(RPW_NAMES_MALE)
    else:
        first_name = random.choice(RPW_NAMES_FEMALE)
    last_name = random.choice(RPW_LAST_NAMES)
    return first_name, last_name

def gen_password(first, last):
    name = f"{first}{last}".replace(' ', '')
    return f"{name}{random.randint(1000,9999)}"

def generate_random_phone_number():
    random_number = str(random.randint(1000000, 9999999))
    third = random.randint(0, 4)
    forth = random.randint(1, 7)
    return f"9{third}{forth}{random_number}"

def generate_temp_email():
    domains = ['hotmail.com', 'gmail.com', 'mail.com', 'outlook.co.id', 'gamemail.com']
    username_length = random.randint(10, 15)
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_length))
    domain = random.choice(domains)
    return f"{username}@{domain}"

def ugenX():
    ua = UserAgent()
    return ua.random

def random_device_model():
    models = ["Samsung-SM-S918B","Xiaomi-2210132G","OnePlus-CPH2451","OPPO-CPH2207","vivo-V2203","realme-RMX3085"]
    return random.choice(models)

def random_device_id():
    return str(uuid.uuid4())

def random_fingerprint():
    fps = ["samsung/a54/a54:13/TP1A.220624.014/A546EXXU1AWF2:user/release-keys","xiaomi/umi/umi:12/RKQ1.211001.001/V12.5.6.0.RJBCNXM:user/release-keys"]
    return random.choice(fps)

def get_via_user_agent():
    ua_list = [
        "Mozilla/5.0 (Linux; Android 13; SM-A546E Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36 [FBAN/EMA;FBLC/id_ID;FBAV/484.0.0.14.106;]",
        "Mozilla/5.0 (Linux; Android 12; SM-G991B Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.86 Mobile Safari/537.36 [FBAN/EMA;FBLC/id_ID;FBAV/483.0.0.15.109;]"
    ]
    return random.choice(ua_list)

# API CLIENT
class EmailAPI:
    def __init__(self):
        self.session = requests.Session()
    
    def get_all_domains(self, show_progress=True):
        all_domains = []
        page = 1
        
        if show_progress:
            print(f"\n{P4}*{R} {B}Fetching domains from server...{R}\n")
        
        while True:
            try:
                url = f"{API_BASE}/all-domains/"
                params = {"page": page, "limit": 100}
                
                r = self.session.get(url, params=params, timeout=15)
                r.raise_for_status()
                data = r.json()
                
                if isinstance(data, dict):
                    domains = data.get('domains', [])
                    total = data.get('total', 0)
                    has_next = data.get('has_next', False)
                else:
                    domains = data if isinstance(data, list) else []
                    total = len(domains)
                    has_next = False
                
                if not domains:
                    break
                
                all_domains.extend(domains)
                
                if show_progress:
                    progress_bar_download(len(all_domains), total if total > 0 else len(all_domains), f"{CY}Page {page}{R}")
                
                if not has_next and total > 0 and len(all_domains) >= total:
                    break
                
                if len(domains) < 100:
                    break
                
                page += 1
                time.sleep(0.3)
                
            except Exception as e:
                write_log(f"Domain fetch error on page {page}: {str(e)}", "ERROR")
                if page == 1:
                    try:
                        r = self.session.get(f"{API_BASE}/all-domains/", timeout=15)
                        r.raise_for_status()
                        data = r.json()
                        domains = data.get('domains', []) if isinstance(data, dict) else data
                        all_domains = domains if isinstance(domains, list) else []
                    except:
                        pass
                break
        
        if show_progress:
            print(f"\n\n{GN}*{R} {B}Downloaded {len(all_domains)} domains{R}")
        
        write_log(f"Downloaded {len(all_domains)} domains from server", "SUCCESS")
        return all_domains
    
    def get_emails(self, domain, username, limit=20):
        try:
            r = self.session.get(f"{API_BASE}/email/{domain}/{username}/", params={"limit": limit}, timeout=10)
            r.raise_for_status()
            data = r.json()
            return data.get('emails', []) if isinstance(data, dict) else data
        except:
            return None
    
    def get_email_detail(self, domain, username, email_id):
        try:
            r = self.session.get(f"{API_BASE}/email/{domain}/{username}/{email_id}", timeout=10)
            r.raise_for_status()
            return r.json()
        except:
            return None

email_api = EmailAPI()

# OTP DETECTION
class OTPEngine:
    PATTERNS = [
        r'^(\d{4,8})$',
        r'(?:kode|otp|code)\s*(?:verifikasi)?\s*(?:adalah|is|:)?\s*(\d{4,8})',
        r'gunakan\s*(?:kode)?\s*(\d{4,8})',
        r'\b(\d{4,8})\b'
    ]
    
    @classmethod
    def extract(cls, subject, content):
        combined = f"{subject} {content}".strip()
        for pattern in cls.PATTERNS:
            match = re.search(pattern, combined, re.IGNORECASE)
            if match:
                code = match.group(1)
                if 4 <= len(code) <= 8 and code.isdigit():
                    return code
        return None

otp_engine = OTPEngine()

# FACEBOOK REGISTRATION ENGINES
def extractor(data):
    try:
        soup = BeautifulSoup(data, "html.parser")
        result = {}
        for inputs in soup.find_all("input"):
            name = inputs.get("name")
            value = inputs.get("value")
            if name:
                result[name] = value
        return result
    except Exception as e:
        return {"error": str(e)}

class DesktopEngine:
    """Desktop endpoint using main.py logic - EXACT COPY"""
    
    def register(self, first, last, contact, password, gender):
        try:
            write_log(f"Desktop registration started for {first} {last}", "INFO")
            proxies = get_random_proxy()
            ses = requests.Session()
            
            response = ses.get(
                url='https://x.facebook.com/reg',
                params={
                    "_rdc": "1",
                    "_rdr": "",
                    "wtsid": "rdr_0t3qOXoIHbMS6isLw",
                    "refsrc": "deprecated"
                },
               proxies=proxies
            )
            
            mts = ses.get("https://x.facebook.com", proxies=proxies).text
            m_ts_match = re.search(r'name="m_ts" value="(.*?)"', str(mts))
            m_ts = m_ts_match.group(1) if m_ts_match else ""
            
            formula = extractor(response.text)
            
            min_age = config.get('min_age', 18)
            max_age = config.get('max_age', 35)
            current_year = datetime.now().year
            birth_year = random.randint(current_year - max_age, current_year - min_age)
            
            fb_gender = "2" if gender == "male" else "1"
            
            birthday_day = str(random.randint(1, 28))
            birthday_month = str(random.randint(1, 12))
            
            payload = {
                'ccp': "2",
                'reg_instance': str(formula.get("reg_instance", "")),
                'submission_request': "true",
                'helper': "",
                'reg_impression_id': str(formula.get("reg_impression_id", "")),
                'ns': "1",
                'zero_header_af_client': "",
                'app_id': "103",
                'logger_id': str(formula.get("logger_id", "")),
                'field_names[0]': "firstname",
                'firstname': first,
                'lastname': last,
                'field_names[1]': "birthday_wrapper",
                'birthday_day': birthday_day,
                'birthday_month': birthday_month,
                'birthday_year': str(birth_year),
                'age_step_input': "",
                'did_use_age': "false",
                'field_names[2]': "reg_email__",
                'reg_email__': contact,
                'field_names[3]': "sex",
                'sex': fb_gender,
                'preferred_pronoun': "",
                'custom_gender': "",
                'field_names[4]': "reg_passwd__",
                'name_suggest_elig': "false",
                'was_shown_name_suggestions': "false",
                'did_use_suggested_name': "false",
                'use_custom_gender': "false",
                'guid': "",
                'pre_form_step': "",
                'encpass': f'#PWD_BROWSER:0:{int(time.time())}:{password}',
                'submit': "Sign Up",
                'm_ts': m_ts,
                'fb_dtsg': str(formula.get("fb_dtsg", "")),
                'jazoest': str(formula.get("jazoest", "")),
                'lsd': str(formula.get("lsd", "")),
                '__dyn': str(formula.get("__dyn", "")),
                '__csr': str(formula.get("__csr", "")),
                '__req': str(formula.get("__req", "p")),
                '__fmt': str(formula.get("__fmt", "1")),
                '__a': str(formula.get("__a", "")),
                '__user': "0"
            }
            
            header1 = {
                "Authority": "https://m.facebook.com/reg",
                "Host": "m.facebook.com",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": W_ueragent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "dnt": "1",
                "X-Requested-With": "mark.via.gp",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "dpr": "1.75",
                "viewport-width": "980",
                "sec-ch-ua": '"Android WebView";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"',
                "sec-ch-prefers-color-scheme": "dark",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
            }
            
            reg_url = "https://www.facebook.com/reg/submit/?privacy_mutation_token=eyJ0eXBlIjowLCJjcmVhdGlvbl90aW1lIjoxNzM0NDE0OTk2LCJjYWxsc2l0ZV9pZCI6OTA3OTI0NDAyOTQ4MDU4fQ%3D%3D&multi_step_form=1&skip_suma=0&shouldForceMTouch=1"
            
            submit = ses.post(reg_url, data=payload, headers=header1, proxies=proxies, timeout=30)
            
            if "c_user" in submit.cookies:
                cookies = ses.cookies.get_dict()
                uid = str(cookies["c_user"])
                write_log(f"Desktop registration successful - UID: {uid}", "SUCCESS")
                return {'success': True, 'uid': uid, 'session': ses}
            
            write_log("Desktop registration failed - No c_user cookie", "ERROR")
            return {'success': False, 'error': 'No c_user'}
        except Exception as e:
            write_log(f"Desktop registration exception: {str(e)}", "ERROR")
            return {'success': False, 'error': str(e)}

class MobileEngine:
    """Mobile endpoint menggunakan logika MobileRegistration dengan perbaikan lengkap"""
    
    def __init__(self):
        self.ua = UserAgent()
    
    def random_device_model(self):
        models = [
            "Samsung-SM-S918B", "Xiaomi-2210132G", "OnePlus-CPH2451", 
            "OPPO-CPH2207", "vivo-V2203", "realme-RMX3085",
            "Google-Pixel-6", "Apple-iPhone14,1", "Huawei-NOH-AN01"
        ]
        return random.choice(models)
    
    def random_device_id(self):
        return str(uuid.uuid4())
    
    def random_fingerprint(self):
        fps = [
            "samsung/a54/a54:13/TP1A.220624.014/A546EXXU1AWF2:user/release-keys",
            "xiaomi/umi/umi:12/RKQ1.211001.001/V12.5.6.0.RJBCNXM:user/release-keys",
            "google/redfin/redfin:12/SP1A.210812.016/7679547:user/release-keys",
            "oneplus/OnePlus9/OnePlus9:11/RKQ1.201105.002/2105071800:user/release-keys"
        ]
        return random.choice(fps)
    
    def generate_random_phone_number(self):
        random_number = str(random.randint(1000000, 9999999))
        third = random.randint(0, 4)
        forth = random.randint(1, 7)
        return f"9{third}{forth}{random_number}"
    
    def get_mobile_headers(self):
        """Get mobile headers for registration"""
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://m.facebook.com/reg",
            "Connection": "keep-alive",
            "Accept-Language": "en-US,en;q=0.9",
            "X-FB-Connection-Type": "mobile.LTE",
            "X-FB-Device": self.random_device_model(),
            "X-FB-Device-ID": self.random_device_id(),
            "X-FB-Fingerprint": self.random_fingerprint(),
            "X-FB-Connection-Quality": "EXCELLENT",
            "X-FB-Net-HNI": "51502",
            "X-FB-SIM-HNI": "51502",
            "X-FB-HTTP-Engine": "Liger",
            'accept-encoding': 'gzip, deflate',
            'content-type': 'application/x-www-form-urlencoded',
            'x-fb-http-engine': 'Liger',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 15; V2508 Build/AP3A.240905.015.A2_D1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/141.0.7390.122 Mobile Safari/537.36[FBAN/EMA;FBLC/en_GB;FBAV/484.0.0.14.106;FBCX/modulariab;]',
        }
    
    def get_registration_form(self, session, url):
        """Fetch registration form with retry logic - enhanced version"""
        urls_to_try = [
            "https://mbasic.facebook.com/reg",
            "https://m.facebook.com/reg",
            "https://www.facebook.com/reg",
            "https://x.facebook.com/reg",
            "https://facebook.com/reg"
        ]
        
        for attempt in range(3):
            for form_url in urls_to_try:
                try:
                    write_log(f"Mobile form fetch attempt {attempt + 1}: {form_url}", "INFO")
                    response = session.get(form_url, headers=self.get_mobile_headers(), timeout=30)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        form = soup.find("form")
                        if form:
                            write_log("Mobile form fetched successfully", "SUCCESS")
                            return True, form, response.cookies.get_dict(), response.text
                    
                except Exception as e:
                    write_log(f"Mobile form fetch failed: {str(e)[:50]}", "WARNING")
                    continue
            
            if attempt < 2:
                wait_time = random.uniform(0, 1)
                write_log(f"Mobile form fetch waiting {wait_time:.1f}s before retry...", "INFO")
                time.sleep(wait_time)
        
        return False, None, {}, ""
    
    def generate_user_details(self, first, last, contact, password, gender):
        """Generate user details for registration"""
        min_age = config.get('min_age', 18)
        max_age = config.get('max_age', 35)
        current_year = datetime.now().year
        birth_year = random.randint(current_year - max_age, current_year - min_age)
        
        return {
            'firstname': first,
            'lastname': last,
            'date': random.randint(1, 28),
            'month': random.randint(1, 12),
            'year': birth_year,
            'contact': contact,
            'password': password,
            'gender': '2' if gender == 'male' else '1'  # Facebook: 1=female, 2=male
        }
    
    def register(self, first, last, contact, password, fb_gender):
        """Main registration function - enhanced with retry logic"""
        try:
            write_log(f"Mobile registration started for {first} {last}", "INFO")
            
            # Convert gender format
            gender = 'male' if fb_gender == 2 else 'female'
            
            session = requests.Session()
            
            # Try multiple endpoints with retry
            endpoints = [
                "https://m.facebook.com/reg",
                "https://mbasic.facebook.com/reg", 
                "https://www.facebook.com/reg"
            ]
            
            for endpoint_attempt in range(2):  # Try 2 times
                for endpoint in endpoints:
                    try:
                        write_log(f"Mobile registration attempt {endpoint_attempt + 1} at {endpoint}", "INFO")
                        
                        # Get registration form
                        success, form, initial_cookies, page_html = self.get_registration_form(session, endpoint)
                        
                        if not success:
                            write_log(f"Failed to get form from {endpoint}", "WARNING")
                            continue
                        
                        # Generate user details
                        user_details = self.generate_user_details(first, last, contact, password, gender)
                        
                        # Prepare registration data
                        data = {
                            "firstname": user_details['firstname'],
                            "lastname": user_details['lastname'],
                            "birthday_day": str(user_details['date']),
                            "birthday_month": str(user_details['month']),
                            "birthday_year": str(user_details['year']),
                            "reg_email__": user_details['contact'],
                            "sex": user_details['gender'],
                            "encpass": f'#PWD_BROWSER:0:{int(time.time())}:{user_details["password"]}',
                            "submit": "Sign Up"
                        }
                        
                        # Add hidden form fields
                        if form:
                            for inp in form.find_all("input"):
                                if inp.has_attr("name") and inp["name"] not in data:
                                    data[inp["name"]] = inp.get("value", "")
                        
                        # Extract action URL
                        action_url = ""
                        if form and form.get("action"):
                            action = form.get("action")
                            if action.startswith('/'):
                                action_url = f"https://m.facebook.com{action}"
                            elif action.startswith('http'):
                                action_url = action
                            else:
                                action_url = endpoint.rstrip('/') + '/' + action.lstrip('/')
                        else:
                            action_url = endpoint
                        
                        # Submit registration
                        write_log(f"Submitting mobile registration to {action_url}", "INFO")
                        
                        response = session.post(
                            action_url,
                            data=data,
                            headers=self.get_mobile_headers(),
                            timeout=60,
                            allow_redirects=True
                        )
                        
                        # Check for success
                        cookies = session.cookies.get_dict()
                        
                        if "c_user" in cookies:
                            uid = str(cookies["c_user"])
                            write_log(f"Mobile registration successful - UID: {uid}", "SUCCESS")
                            
                            return {
                                'success': True, 
                                'uid': uid, 
                                'session': session,
                                'cookies': cookies,
                                'details': user_details
                            }
                        
                        # Check for checkpoint/verification
                        if "checkpoint" in response.url.lower() or "confirm" in response.url.lower():
                            write_log("Mobile registration requires verification", "INFO")
                            # Still consider success if we got cookies
                            temp_cookies = session.cookies.get_dict()
                            if 'c_user' in temp_cookies:
                                uid = str(temp_cookies['c_user'])
                                write_log(f"Mobile registration pending verification - UID: {uid}", "SUCCESS")
                                return {
                                    'success': True, 
                                    'uid': uid, 
                                    'session': session,
                                    'cookies': temp_cookies,
                                    'details': user_details,
                                    'requires_verification': True
                                }
                        
                        # Try to extract error
                        soup = BeautifulSoup(response.text, "html.parser")
                        error_div = soup.find("div", class_=lambda x: x and 'error' in x.lower() if x else False)
                        if error_div:
                            error_msg = error_div.get_text(strip=True)[:100]
                            write_log(f"Mobile registration error: {error_msg}", "ERROR")
                        
                    except requests.exceptions.Timeout:
                        write_log(f"Mobile registration timeout at {endpoint}", "WARNING")
                        continue
                    except requests.exceptions.ConnectionError:
                        write_log(f"Mobile connection error at {endpoint}", "WARNING")
                        continue
                    except Exception as e:
                        write_log(f"Mobile registration exception at {endpoint}: {str(e)[:50]}", "WARNING")
                        continue
                
                # Wait before next attempt
                if endpoint_attempt < 1:
                    wait_time = random.uniform(3, 7)
                    write_log(f"Mobile registration waiting {wait_time:.1f}s before retry...", "INFO")
                    time.sleep(wait_time)
            
            write_log("Mobile registration failed after all attempts", "ERROR")
            return {'success': False, 'error': 'Registration failed after all attempts'}
            
        except Exception as e:
            write_log(f"Mobile registration fatal error: {str(e)}", "ERROR")
            return {'success': False, 'error': str(e)}

desktop_engine = DesktopEngine()
mobile_engine = MobileEngine()

# OTP VERIFICATION ENGINE
class OTPVerifier:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.prefix = email[:20] if email else "Unknown"
        self.via_browser = ViaBrowserSimulator()
        self.session = None
    
    def login_and_extract(self):
        """Login via browser simulation (like verif.py)"""
        try:
            write_log(f"Browser login started for {self.email}", "INFO")
            
            # Use ViaBrowserSimulator for login
            result = self.via_browser.login_and_extract(self.email, self.password, self.prefix)
            
            if result['status'] == 'success':
                self.session = result['session']
                write_log(f"Browser login successful - UID: {result['uid']}", "SUCCESS")
                return {'success': True, 'uid': result['uid'], 'session': self.session}
            else:
                write_log(f"Browser login failed: {result.get('message', 'Unknown')}", "ERROR")
                return {'success': False, 'error': result.get('message', 'Login failed')}
                
        except Exception as e:
            write_log(f"Browser login exception: {str(e)}", "ERROR")
            return {'success': False, 'error': str(e)}
    
    def verify_with_otp(self, otp_code, max_retries=3):
        """Complete OTP verification flow using same session"""
        write_log(f"Starting OTP verification for {self.email} with code {otp_code}", "INFO")
        
        for attempt in range(max_retries):
            try:
                write_log(f"Verification attempt {attempt + 1}/{max_retries}", "INFO")
                
                # Step 1: Login via browser simulation
                login_result = self.login_and_extract()
                
                if not login_result['success']:
                    if attempt < max_retries - 1:
                        write_log("Browser login failed, retrying...", "WARNING")
                        time.sleep(3)
                        continue
                    else:
                        write_log("Browser login failed after all retries", "ERROR")
                        return False, "LOGIN_FAILED"
                
                # Step 2: Create OTP submitter with the same session
                otp_submitter = HardcoreEndpointOTPSubmitter(self.session, self.prefix)
                
                # Step 3: Submit OTP using the same session
                success, msg = otp_submitter.submit_otp_via_endpoint(otp_code)
                
                if success:
                    write_log("OTP verification completed successfully", "SUCCESS")
                    return True, "SUCCESS"
                else:
                    if attempt < max_retries - 1:
                        write_log(f"Verification failed: {msg}, retrying...", "WARNING")
                        time.sleep(3)
                        continue
                    else:
                        write_log(f"OTP verification failed after all retries: {msg}", "ERROR")
                        return False, msg
                        
            except Exception as e:
                write_log(f"Verification attempt {attempt + 1} error: {str(e)}", "ERROR")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                else:
                    return False, str(e)
        
        return False, "MAX_RETRIES_EXCEEDED"
    
    def get_session(self):
        """Return the authenticated session for cookie extraction"""
        return self.session

class ViaBrowserSimulator:
    def get_via_user_agent(self):
        ua_list = [
            "Mozilla/5.0 (Linux; Android 13; SM-A546E Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36 [FBAN/EMA;FBLC/id_ID;FBAV/484.0.0.14.106;]",
            "Mozilla/5.0 (Linux; Android 12; SM-G991B Build/SP1A.210812.016; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.86 Mobile Safari/537.36 [FBAN/EMA;FBLC/id_ID;FBAV/483.0.0.15.109;]",
            "Mozilla/5.0 (Linux; Android 13; SM-A525F Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.104 Mobile Safari/537.36 [FBAN/EMA;FBLC/id_ID;FBAV/484.0.0.14.106;]"
        ]
        return random.choice(ua_list)

    def create_via_session(self):
        session = requests.Session()
        session.headers.update({
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://m.facebook.com',
            'referer': 'https://m.facebook.com/',
            'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': self.get_via_user_agent(),
            'x-requested-with': 'mark.via.gp',
        })
        return session

    def build_thick_cookies(self, session, uid):
        cookies_dict = {}
        for cookie in session.cookies:
            cookies_dict[cookie.name] = cookie.value
        
        if 'c_user' not in cookies_dict:
            return None
            
        cookies_dict.update({
            'm_pixel_ratio': cookies_dict.get('m_pixel_ratio', '2'),
            'wd': cookies_dict.get('wd', '360x806'),
            'ps_l': cookies_dict.get('ps_l', '1'),
            'ps_n': cookies_dict.get('ps_n', '1'),
            'locale': cookies_dict.get('locale', 'id_ID'),
            'pas': cookies_dict.get('pas', f'{uid}%3AdrxQXO9bo9'),
            'wl_cbv': cookies_dict.get('wl_cbv', f'v2%3Bclient_version%3A3000%3Btimestamp%3A{int(time.time())}'),
            'vpd': cookies_dict.get('vpd', 'v1%3B662x360x2')
        })
        return cookies_dict

    def format_cookie_string(self, cookies_dict):
        priority = ['datr', 'sb', 'm_pixel_ratio', 'wd', 'ps_l', 'ps_n', 'c_user', 'xs', 'fr', 'locale', 'pas', 'presence', 'spin']
        ending = ['wl_cbv', 'vpd']
        parts = []
        
        for key in priority:
            if key in cookies_dict:
                parts.append(f"{key}={cookies_dict[key]}")
        for key, value in cookies_dict.items():
            if key not in priority and key not in ending:
                parts.append(f"{key}={value}")
        for key in ending:
            if key in cookies_dict:
                parts.append(f"{key}={cookies_dict[key]}")
        return "; ".join(parts)

    def login_and_extract(self, identifier, password, prefix=""):
        """Login method that returns session for OTP verification"""
        try:
            write_log(f"{prefix} - Initializing session", "INFO")
            session = self.create_via_session()
            
            write_log(f"{prefix} - Requesting login page", "INFO")
            resp = session.get('https://m.facebook.com/login/', timeout=30)
            
            lsd = re.search(r'name="lsd" value="(.*?)"', resp.text)
            jazoest = re.search(r'name="jazoest" value="(.*?)"', resp.text)
            privacy = re.search(r'privacy_mutation_token=([^&"]+)', resp.text)
            
            data = {
                'lsd': lsd.group(1) if lsd else "",
                'jazoest': jazoest.group(1) if jazoest else "",
                'email': identifier,
                'pass': password,
                'login_source': 'comet_headerless_login',
                'encpass': f'#PWD_BROWSER:0:{int(time.time())}:{password}'
            }
            
            url = f'https://m.facebook.com/login/device-based/regular/login/?privacy_mutation_token={privacy.group(1)}&refsrc=deprecated' if privacy else 'https://m.facebook.com/login/device-based/regular/login/?refsrc=deprecated'
            
            write_log(f"{prefix} - Authenticating credentials", "INFO")
            session.post(url, data=data, timeout=30, allow_redirects=True)
            
            cookies = {c.name: c.value for c in session.cookies}
            if 'c_user' not in cookies:
                write_log(f"{prefix} - Authentication failed", "ERROR")
                return {'status': 'failed', 'message': 'No c_user', 'session': session, 'cookies': None}
            
            uid = cookies['c_user']
            write_log(f"{prefix} - Authenticated → UID: {uid}", "SUCCESS")
            
            return {
                'status': 'success',
                'uid': uid,
                'session': session,
                'cookies': cookies
            }
        except Exception as e:
            write_log(f"{prefix} - Login exception: {str(e)[:30]}", "ERROR")
            return {'status': 'failed', 'message': str(e), 'session': None, 'cookies': None}

class HardcoreEndpointOTPSubmitter:
    def __init__(self, session, prefix=""):
        self.session = session
        self.prefix = prefix
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
        })

    def detect_otp_page(self):
        write_log(f"{self.prefix} - Scanning for OTP page", "INFO")
        urls = [
            "https://www.facebook.com/checkpoint/",
            "https://www.facebook.com/confirmemail.php",
            "https://www.facebook.com/"
        ]
        
        for url in urls:
            try:
                r = self.session.get(url, timeout=10, allow_redirects=True)
                if r.status_code == 200:
                    if any(k in r.url.lower() or k in r.text.lower() for k in ['confirmemail', 'checkpoint', 'verification']):
                        write_log(f"{self.prefix} - OTP page detected", "SUCCESS")
                        form = self.extract_form(r.text)
                        if form and 'error' not in form:
                            form['__action_url'] = self.get_action(r.text, r.url)
                            form['__code_input_name'] = self.get_code_field(r.text)
                            return True, form, r.url
            except Exception as e:
                write_log(f"{self.prefix} - Error checking URL {url}: {str(e)}", "WARNING")
                continue
        
        write_log(f"{self.prefix} - No OTP page found", "WARNING")
        return False, {}, ""

    def extract_form(self, html):
        try:
            soup = BeautifulSoup(html, "html.parser")
            return {inp.get("name"): inp.get("value", '') for inp in soup.find_all("input") if inp.get("name")}
        except:
            return {"error": "parse_failed"}

    def get_action(self, html, url):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            form = soup.find('form')
            if form:
                action = form.get('action', '')
                if action and not action.startswith('http'):
                    return f"https://www.facebook.com{action}" if action.startswith('/') else f"{url.rsplit('/', 1)[0]}/{action}"
                return action or url
        except:
            pass
        return url

    def get_code_field(self, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            code_inp = soup.find('input', {'name': lambda x: x and 'code' in x.lower()})
            return code_inp.get('name', 'code') if code_inp else 'code'
        except:
            return 'code'

    def submit_otp_via_endpoint(self, otp_code):
        write_log(f"{self.prefix} - Submitting OTP: {otp_code}", "INFO")
        
        has_page, form, otp_url = self.detect_otp_page()
        if not has_page or not form:
            write_log(f"{self.prefix} - OTP page unavailable", "ERROR")
            return False, "NO_OTP_PAGE"
        
        payload = {k: v for k, v in form.items() if not k.startswith('__') and v is not None}
        code_field = form.get('__code_input_name', 'code')
        payload[code_field] = otp_code
        submit_url = form.get('__action_url', otp_url)
        
        self.session.headers.update({
            'Referer': otp_url,
            'Origin': 'https://www.facebook.com',
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        
        try:
            r = self.session.post(submit_url, data=payload, timeout=15, allow_redirects=True)
            
            if r.status_code != 200:
                write_log(f"{self.prefix} - HTTP {r.status_code} response", "ERROR")
                return False, f"HTTP_{r.status_code}"
            
            success_ind = ['home.php', 'welcome', 'feed', 'confirmed', 'success', 'verified']
            error_ind = ['error', 'invalid', 'wrong', 'incorrect']
            
            if any(i in r.url.lower() or i in r.text.lower() for i in success_ind):
                write_log(f"{self.prefix} - OTP verified successfully", "SUCCESS")
                return True, "SUCCESS"
            
            if any(i in r.text.lower() for i in error_ind):
                write_log(f"{self.prefix} - OTP verification rejected", "ERROR")
                return False, "OTP_INVALID"
            
            write_log(f"{self.prefix} - OTP submitted (status unclear)", "INFO")
            return True, "SUCCESS"
        except Exception as e:
            write_log(f"{self.prefix} - Submit error: {str(e)[:20]}", "ERROR")
            return False, str(e)

# COOKIE EXTRACTOR
class CookieExtractor:
    def __init__(self, session):
        self.session = session
        self.via_browser = ViaBrowserSimulator()
    
    def extract(self, uid):
        try:
            write_log(f"Cookie extraction started for UID: {uid}", "INFO")
            
            # Navigate to profile to refresh cookies
            self.session.get(f'https://m.facebook.com/{uid}', timeout=30)
            
            # Build thick cookies using ViaBrowserSimulator method
            thick = self.via_browser.build_thick_cookies(self.session, uid)
            if not thick:
                write_log("Cookie extraction failed - Unable to build thick cookies", "ERROR")
                return None
            
            cookie_str = self.via_browser.format_cookie_string(thick)
            write_log(f"Cookie extraction successful - Length: {len(cookie_str)}", "SUCCESS")
            return cookie_str
        except Exception as e:
            write_log(f"Cookie extraction exception: {str(e)}", "ERROR")
            return None

# TRIPLE WORKER SYSTEM
class CreationWorker(threading.Thread):
    def __init__(self, worker_id):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.running = True
    
    def run(self):
        write_log(f"Creation Worker {self.worker_id} started", "SYSTEM")
        
        while self.running:
            try:
                task = creation_queue.get(timeout=1)
                
                if task == "STOP":
                    break
                
                domain = task
                stats['worker1_status'] = f"Creating..."
                
                if stats['total_created'] >= config.get('account_limit', 10):
                    creation_queue.task_done()
                    break
                
                gender_cfg = config.get('gender', 'random')
                gender = random.choice(['male', 'female']) if gender_cfg == 'random' else gender_cfg
                
                name_type = config.get('name_type', 'filipino')
                if name_type == 'filipino':
                    first, last = get_filipino_name('1' if gender == 'male' else '2')
                else:
                    first, last = get_rpw_name('1' if gender == 'male' else '2')
                
                if config.get('password_type') == 'auto' or not config.get('custom_password'):
                    password = gen_password(first, last)
                else:
                    password = config.get('custom_password')
                
                username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
                email = f"{username}@{domain}"
                
                if config.get('use_manual_email'):
                    with lock:
                        contact = get_input(f"Email for {first} {last}")
                elif config.get('use_phone'):
                    contact = generate_random_phone_number()
                elif config.get('use_gmail'):
                    contact = generate_temp_email()
                else:
                    contact = email
                
                write_log(f"Creating account: {first} {last} | {contact}", "INFO")
                
                if config.get('endpoint') == 'desktop':
                    result = desktop_engine.register(first, last, contact, password, gender)
                else:
                    fb_gender = 2 if gender == 'male' else 1
                    result = mobile_engine.register(first, last, contact, password, fb_gender)
                
                if result['success']:
                    uid = result['uid']
                    
                    account_data = {
                        'uid': uid,
                        'first': first,
                        'last': last,
                        'email': email,
                        'contact': contact,
                        'password': password,
                        'domain': domain,
                        'username': username,
                        'session': result.get('session')
                    }
                    
                    if config.get('use_manual_email'):
                        with lock:
                            otp_input = get_input(f"Enter OTP for {uid}")
                        
                        if otp_input.strip():
                            account_data['otp'] = otp_input.strip()
                            verify_queue.put(account_data)
                        else:
                            stats['total_failed'] += 1
                            stats['cp_count'] += 1
                    elif config.get('use_tinyhost'):
                        monitor_queue.put(account_data)
                    else:
                        save_account(uid, password, email, 'N/A')
                        stats['total_created'] += 1
                else:
                    stats['total_failed'] += 1
                    stats['cp_count'] += 1
                
                stats['worker1_status'] = "Idle"
                creation_queue.task_done()
                
            except Empty:
                stats['worker1_status'] = "Waiting"
                continue
            except Exception as e:
                write_log(f"Creation Worker error: {str(e)}", "ERROR")
                stats['cp_count'] += 1
        
        write_log(f"Creation Worker {self.worker_id} stopped", "SYSTEM")

class MonitorWorker(threading.Thread):
    def __init__(self, worker_id):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.running = True
    
    def run(self):
        write_log(f"Monitor Worker {self.worker_id} started", "SYSTEM")
        
        while self.running:
            try:
                account = monitor_queue.get(timeout=1)
                
                if account == "STOP":
                    break
                
                domain = account['domain']
                username = account['username']
                uid = account['uid']
                
                stats['worker2_status'] = f"Monitoring..."
                
                write_log(f"Monitoring OTP for {username}@{domain}", "INFO")
                
                timeout = config.get('otp_timeout', 15)
                interval = config.get('otp_check_interval', 1)
                checks = int(timeout / interval)
                otp = None
                
                for i in range(checks):
                    time.sleep(interval)
                    try:
                        emails = email_api.get_emails(domain, username, limit=5)
                        if not emails:
                            continue
                        
                        for email_msg in emails[:3]:
                            email_id = email_msg.get('id')
                            if not email_id:
                                continue
                            
                            detail = email_api.get_email_detail(domain, username, email_id)
                            if not detail:
                                continue
                            
                            subject = detail.get('subject', '')
                            content = detail.get('body', '') or detail.get('text', '')
                            
                            otp = otp_engine.extract(subject, content)
                            if otp:
                                break
                        
                        if otp:
                            break
                    except:
                        continue
                
                if otp:
                    write_log(f"OTP found: {otp} for {uid}", "SUCCESS")
                    account['otp'] = otp
                    verify_queue.put(account)
                else:
                    write_log(f"OTP timeout for {uid}", "WARNING")
                    stats['total_failed'] += 1
                    stats['cp_count'] += 1
                    stats['total_created'] += 1
                
                stats['worker2_status'] = "Idle"
                monitor_queue.task_done()
                
            except Empty:
                stats['worker2_status'] = "Waiting"
                continue
            except Exception as e:
                write_log(f"Monitor Worker error: {str(e)}", "ERROR")
                stats['cp_count'] += 1
        
        write_log(f"Monitor Worker {self.worker_id} stopped", "SYSTEM")

class VerifyWorker(threading.Thread):
    def __init__(self, worker_id):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.running = True
    
    def run(self):
        write_log(f"Verify Worker {self.worker_id} started", "SYSTEM")
        
        while self.running:
            try:
                account = verify_queue.get(timeout=1)
                
                if account == "STOP":
                    break
                
                # Use registration email/contact (not the temporary email)
                email = account['contact']  # This is the email/phone used for registration
                password = account['password']
                otp = account['otp']
                uid = account.get('uid', 'Unknown')
                
                stats['worker3_status'] = f"Verifying..."
                
                write_log(f"Starting verification for {email} with OTP: {otp}", "INFO")
                
                # Create new verifier with proper credentials
                verifier = OTPVerifier(email, password)
                success, msg = verifier.verify_with_otp(otp, max_retries=2)
                
                if success:
                    stats['total_verified'] += 1
                    write_log(f"Verification successful for {email}", "SUCCESS")
                    
                    # Wait a bit before cookie extraction
                    time.sleep(random.uniform(1, 2))
                    
                    # Extract cookies using the verified session
                    verified_session = verifier.get_session()
                    if verified_session:
                        extractor = CookieExtractor(verified_session)
                        cookies = extractor.extract(uid)
                        
                        if cookies:
                            creation_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                            save_account(uid, password, account['email'], cookies)
                            stats['total_with_cookies'] += 1
                            stats['ok_count'] += 1
                            
                            with lock:
                                display_account_ok(uid, password, account['email'], cookies, creation_time)
                        else:
                            write_log(f"Cookie extraction failed for UID {uid}", "ERROR")
                            stats['cp_count'] += 1
                    else:
                        write_log(f"No session available for cookie extraction", "ERROR")
                        stats['cp_count'] += 1
                else:
                    write_log(f"Verification failed for {email}: {msg}", "ERROR")
                    stats['total_failed'] += 1
                    stats['cp_count'] += 1
                
                stats['total_created'] += 1
                stats['worker3_status'] = "Idle"
                verify_queue.task_done()
                
            except Empty:
                stats['worker3_status'] = "Waiting"
                continue
            except Exception as e:
                write_log(f"Verify Worker error: {str(e)}", "ERROR")
                stats['cp_count'] += 1

def save_account(uid, password, email, cookies):
    try:
        with open(OUTPUT_FILE, 'a') as f:
            f.write(f"{uid}|{password}|{email}|{cookies}\n")
        write_log(f"Account saved: {uid} | {email}", "SUCCESS")
    except Exception as e:
        write_log(f"Save error: {str(e)}", "ERROR")

# MENU SYSTEM - COMPLETE
def menu_main():
    while True:
        banner()
        
        menu_items = [
            (f"{PK}1.{R}", f"Create Accounts", f"{GR}(Triple-Worker){R}"),
            (f"{PK}2.{R}", f"Configuration", f"{GR}(Settings){R}"),
            (f"{PK}3.{R}", f"Domain Manager", f"{GR}(Database){R}"),
            (f"{PK}4.{R}", f"Shortcuts Manager", f"{GR}(Quick Access){R}"),
            (f"{PK}5.{R}", f"Statistics", f"{GR}(Reports){R}"),
            (f"{PK}6.{R}", f"Exit", f"{GR}(Quit){R}")
        ]
        
        box("MAIN MENU", None, P3)
        print()
        
        for num, item, desc in menu_items:
            print(f"  {num} {B}{item:<25}{R} {desc}")
        
        print(f"\n{P3}{'-' * W}{R}")
        
        choice = get_input("Select option")
        
        if choice == "1":
            menu_create()
        elif choice == "2":
            menu_config()
        elif choice == "3":
            menu_domains()
        elif choice == "4":
            menu_shortcuts()
        elif choice == "5":
            menu_stats()
        elif choice == "6":
            clear()
            print(f"\n{P3}{'=' * W}{R}")
            print(f"{B}{CY}Thank you for using Elite Creator!{R}".center(W + 18))
            print(f"{P3}{'=' * W}{R}\n")
            write_log("Program exited by user", "SYSTEM")
            time.sleep(1)
            break

def menu_create():
    banner()
    box("SELECT DOMAIN SOURCE")
    
    print(f"\n{P4}1.{R} Select by TLD Category")
    print(f"{P4}2.{R} Use Shortcut")
    print(f"{P4}0.{R} Back")
    
    choice = get_input("Select option")
    
    if choice == "1":
        menu_tld_selection()
    elif choice == "2":
        menu_use_shortcut()
    elif choice == "0":
        return

def menu_tld_selection():
    banner()
    box("SELECT TLD CATEGORY")
    
    stats_tld = get_tld_stats()
    if not stats_tld:
        print(f"\n{RD}No domains available. Sync domains first!{R}")
        time.sleep(2)
        return
    
    tlds = list(stats_tld.keys())[:100]
    for i, tld in enumerate(tlds, 1):
        print(f"{P4}{i:2d}.{R} .{tld.upper():<10} {GR}({stats_tld[tld]} domains){R}")
    
    print(f"\n{P4} 0.{R} Back to main menu")
    
    choice = get_input("Select TLD")
    if choice == "0":
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(tlds):
            tld = tlds[idx]
            menu_select_domains(tld)
    except:
        pass

def menu_select_domains(tld):
    page = 1
    selected = []
    
    while True:
        banner()
        domains, total_pages, total = get_domains_by_tld(tld, page)
        
        box(f"SELECT DOMAINS - .{tld.upper()}", [
            f"{CY}Page:{R} {page}/{total_pages}",
            f"{CY}Selected:{R} {len(selected)} domains",
            f"{CY}Total:{R} {total} available"
        ])
        
        for i, domain in enumerate(domains, 1):
            marker = f"{GN}*{R}" if domain in selected else f"{GR}o{R}"
            print(f"{marker} {P4}{i:2d}.{R} {domain}")
        
        print(f"\n{P3}{'-' * W}{R}")
        print(f"{P4}N.{R} Next  {P4}P.{R} Previous  {P4}A.{R} All")
        print(f"{P4}C.{R} Clear  {P4}V.{R} Save shortcut")
        print(f"{P4}S.{R} Start  {P4}0.{R} Back")
        
        choice = get_input("Action").lower()
        
        if choice == "0":
            return
        elif choice == "n" and page < total_pages:
            page += 1
        elif choice == "p" and page > 1:
            page -= 1
        elif choice == "a":
            selected.extend([d for d in domains if d not in selected])
        elif choice == "c":
            selected = []
        elif choice == "v":
            if selected:
                save_shortcut_prompt(selected)
        elif choice == "s":
            if selected:
                start_creation(selected)
                return
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(domains):
                    domain = domains[idx]
                    if domain in selected:
                        selected.remove(domain)
                    else:
                        selected.append(domain)
            except:
                pass

def save_shortcut_prompt(domains):
    banner()
    box("SAVE SHORTCUT")
    
    name = get_input("Shortcut name")
    if name:
        shortcuts = load_shortcuts()
        shortcuts[name] = domains
        save_shortcuts(shortcuts)
        print(f"\n{GN}*{R} Shortcut '{name}' saved with {len(domains)} domains")
        write_log(f"Shortcut created: {name} with {len(domains)} domains", "INFO")
        time.sleep(2)

def menu_use_shortcut():
    banner()
    box("USE SHORTCUT")
    
    shortcuts = load_shortcuts()
    
    if not shortcuts:
        print(f"\n{YL}No shortcuts available{R}")
        time.sleep(2)
        return
    
    for i, (name, domains) in enumerate(shortcuts.items(), 1):
        print(f"{P4}{i:2d}.{R} {name:<30} {GR}({len(domains)} domains){R}")
    
    print(f"\n{P4} 0.{R} Back")
    
    choice = get_input("Select shortcut")
    
    if choice == "0":
        return
    
    try:
        idx = int(choice) - 1
        shortcut_list = list(shortcuts.items())
        if 0 <= idx < len(shortcut_list):
            name, domains = shortcut_list[idx]
            start_creation(domains)
    except:
        pass

def menu_config():
    while True:
        banner()
        endpoint_display = f"{B}{GN if config.get('endpoint') == 'desktop' else CY}{config.get('endpoint', 'desktop').title()}{R}"
        
        box("CONFIGURATION", [
            f"{PK}1.{R} Endpoint: {endpoint_display}",
            f"{PK}2.{R} Name Type: {B}{config.get('name_type', 'filipino').title()}{R}",
            f"{PK}3.{R} Gender: {B}{config.get('gender', 'random').title()}{R}",
            f"{PK}4.{R} Password: {B}{config.get('password_type', 'auto').title()}{R}",
            f"{PK}5.{R} Min Age: {B}{config.get('min_age', 18)}{R}",
            f"{PK}6.{R} Max Age: {B}{config.get('max_age', 35)}{R}",
            f"{PK}7.{R} Account Limit: {B}{config.get('account_limit', 10)}{R}",
            f"{PK}8.{R} Manual Email: {B}{GN if config.get('use_manual_email') else RD}{'ON' if config.get('use_manual_email') else 'OFF'}{R}",
            f"{PK}9.{R} Use Gmail: {B}{GN if config.get('use_gmail') else RD}{'ON' if config.get('use_gmail') else 'OFF'}{R}",
            f"{PK}10.{R} Use Phone: {B}{GN if config.get('use_phone') else RD}{'ON' if config.get('use_phone') else 'OFF'}{R}",
            f"{PK}11.{R} Tinyhost OTP: {B}{GN if config.get('use_tinyhost') else RD}{'ON' if config.get('use_tinyhost') else 'OFF'}{R}",
            f"{PK}12.{R} OTP Timeout: {B}{config.get('otp_timeout', 15)}s{R}",
            f"{PK}13.{R} Save & Back"
        ])
        
        choice = get_input("Select option")
        
        if choice == "1":
            print(f"\n{P4}1.{R} Desktop  {P4}2.{R} Mobile")
            ep = get_input("Endpoint")
            if ep == "1":
                config['endpoint'] = "desktop"
            elif ep == "2":
                config['endpoint'] = "mobile"
        elif choice == "2":
            print(f"\n{P4}1.{R} Filipino  {P4}2.{R} RPW")
            nt = get_input("Name Type")
            if nt == "1":
                config['name_type'] = "filipino"
            elif nt == "2":
                config['name_type'] = "rpw"
        elif choice == "3":
            print(f"\n{P4}1.{R} Male  {P4}2.{R} Female  {P4}3.{R} Random")
            gen = get_input("Gender")
            if gen == "1":
                config['gender'] = "male"
            elif gen == "2":
                config['gender'] = "female"
            elif gen == "3":
                config['gender'] = "random"
        elif choice == "4":
            print(f"\n{P4}1.{R} Auto  {P4}2.{R} Custom")
            pt = get_input("Password type")
            if pt == "1":
                config['password_type'] = "auto"
            elif pt == "2":
                config['password_type'] = "custom"
                pwd = get_input("Enter custom password")
                if len(pwd) >= 6:
                    config['custom_password'] = pwd
        elif choice == "5":
            age = get_input("Min age")
            try:
                config['min_age'] = max(13, int(age))
            except:
                pass
        elif choice == "6":
            age = get_input("Max age")
            try:
                config['max_age'] = min(100, int(age))
            except:
                pass
        elif choice == "7":
            limit = get_input("Account limit")
            try:
                config['account_limit'] = max(1, int(limit))
            except:
                pass
        elif choice == "8":
            config['use_manual_email'] = not config.get('use_manual_email', False)
            if config['use_manual_email']:
                config['use_gmail'] = False
                config['use_phone'] = False
        elif choice == "9":
            config['use_gmail'] = not config.get('use_gmail', False)
            if config['use_gmail']:
                config['use_phone'] = False
                config['use_manual_email'] = False
        elif choice == "10":
            config['use_phone'] = not config.get('use_phone', False)
            if config['use_phone']:
                config['use_gmail'] = False
                config['use_manual_email'] = False
        elif choice == "11":
            config['use_tinyhost'] = not config.get('use_tinyhost', True)
        elif choice == "12":
            timeout = get_input("OTP timeout (seconds)")
            try:
                config['otp_timeout'] = max(5, min(60, int(timeout)))
            except:
                pass
        elif choice == "13":
            save_config()
            print(f"\n{GN}*{R} Configuration saved")
            write_log("Configuration saved", "INFO")
            time.sleep(1)
            break

def menu_domains():
    while True:
        banner()
        box("DOMAIN MANAGER")
        
        with db_conn() as conn:
            cursor = conn.execute("SELECT COUNT(*) as total FROM domains")
            total = cursor.fetchone()['total']
        
        stats_tld = get_tld_stats()
        
        print(f"\n{CY}Total Domains:{R} {B}{total}{R}")
        print(f"{CY}TLD Categories:{R} {B}{len(stats_tld)}{R}\n")
        
        print(f"{P4}1.{R} Sync Domains from Server")
        print(f"{P4}2.{R} View TLD Statistics")
        print(f"{P4}3.{R} Clear Database")
        print(f"{P4}0.{R} Back")
        
        choice = get_input("Select option")
        
        if choice == "1":
            sync_domains()
        elif choice == "2":
            view_tld_stats()
        elif choice == "3":
            confirm = get_input("Clear all domains? (yes/no)")
            if confirm.lower() == "yes":
                with db_conn() as conn:
                    conn.execute("DELETE FROM domains")
                print(f"\n{GN}*{R} Database cleared")
                write_log("Database cleared", "INFO")
                time.sleep(1)
        elif choice == "0":
            break

def menu_shortcuts():
    while True:
        banner()
        box("SHORTCUTS MANAGER")
        
        shortcuts = load_shortcuts()
        
        if shortcuts:
            for i, (name, domains) in enumerate(shortcuts.items(), 1):
                print(f"{P4}{i:2d}.{R} {name:<30} {GR}({len(domains)} domains){R}")
        else:
            print(f"\n{GR}No shortcuts saved yet{R}")
        
        print(f"\n{P4}1.{R} Add Shortcut by Domain Name")
        print(f"{P4}2.{R} Delete Shortcut")
        print(f"{P4}0.{R} Back")
        
        choice = get_input("Select option")
        
        if choice == "1":
            add_shortcut_by_domain()
        elif choice == "2":
            if shortcuts:
                delete_shortcut(shortcuts)
        elif choice == "0":
            break

def add_shortcut_by_domain():
    banner()
    box("ADD SHORTCUT BY DOMAIN")
    
    name = get_input("Shortcut name")
    if not name:
        return
    
    print(f"\n{CY}Enter domain names (one per line, empty to finish):{R}")
    print(f"{GR}Example: example.com{R}\n")
    
    selected_domains = []
    
    while True:
        domain_input = input(f"{P4}> {R}").strip()
        
        if not domain_input:
            break
        
        found = search_domain(domain_input)
        
        if found:
            if len(found) == 1:
                selected_domains.append(found[0])
                print(f"{GN}*{R} Added: {found[0]}")
            else:
                print(f"\n{YL}Multiple matches found:{R}")
                for i, d in enumerate(found[:10], 1):
                    print(f"{P4}{i}.{R} {d}")
                
                sel = get_input("Select number (or 0 to add all)")
                
                if sel == "0":
                    selected_domains.extend(found)
                    print(f"{GN}*{R} Added {len(found)} domains")
                else:
                    try:
                        idx = int(sel) - 1
                        if 0 <= idx < len(found):
                            selected_domains.append(found[idx])
                            print(f"{GN}*{R} Added: {found[idx]}")
                    except:
                        pass
        else:
            print(f"{RD}x{R} Domain not found: {domain_input}")
    
    if selected_domains:
        shortcuts = load_shortcuts()
        shortcuts[name] = selected_domains
        save_shortcuts(shortcuts)
        print(f"\n{GN}*{R} Shortcut '{name}' saved with {len(selected_domains)} domains")
        write_log(f"Shortcut created: {name} with {len(selected_domains)} domains", "INFO")
        time.sleep(2)

def delete_shortcut(shortcuts):
    banner()
    box("DELETE SHORTCUT")
    
    for i, name in enumerate(shortcuts.keys(), 1):
        print(f"{P4}{i:2d}.{R} {name}")
    
    choice = get_input("Select shortcut to delete")
    
    try:
        idx = int(choice) - 1
        shortcut_list = list(shortcuts.keys())
        if 0 <= idx < len(shortcut_list):
            name = shortcut_list[idx]
            del shortcuts[name]
            save_shortcuts(shortcuts)
            print(f"\n{GN}*{R} Shortcut '{name}' deleted")
            write_log(f"Shortcut deleted: {name}", "INFO")
            time.sleep(1)
    except:
        pass

def sync_domains():
    banner()
    box("DOMAIN SYNCHRONIZATION", None, P2)
    
    print()
    loading_animation("Connecting to Tinyhost API", 1.0)
    
    domains = email_api.get_all_domains(show_progress=True)
    
    if not domains:
        print(f"\n{RD}x{R} No domains received from server")
        time.sleep(2)
        return
    
    print(f"\n{P4}*{R} {B}Processing domains...{R}\n")
    
    added = 0
    updated = 0
    
    with db_conn() as conn:
        for i, domain in enumerate(domains):
            tld = domain.split('.')[-1]
            try:
                cursor = conn.execute("SELECT id FROM domains WHERE domain = ?", (domain,))
                if not cursor.fetchone():
                    conn.execute("INSERT INTO domains (domain, tld) VALUES (?, ?)", (domain, tld))
                    added += 1
                else:
                    updated += 1
                
                if (i + 1) % 50 == 0:
                    progress_bar_download(i + 1, len(domains), f"{CY}Processing{R}")
            except:
                pass
        
        progress_bar_download(len(domains), len(domains), f"{CY}Processing{R}")
    
    print(f"\n\n{GN}{'=' * W}{R}")
    print(f"  {GN}*{R} {B}New domains added:{R} {added}")
    print(f"  {BL}*{R} {B}Existing domains:{R} {updated}")
    print(f"  {CY}*{R} {B}Total in database:{R} {added + updated}")
    print(f"{GN}{'=' * W}{R}\n")
    
    time.sleep(2)

def view_tld_stats():
    banner()
    box("TLD STATISTICS")
    
    stats_tld = get_tld_stats()
    
    if not stats_tld:
        print(f"\n{YL}No domains in database{R}")
        time.sleep(2)
        return
    
    total = sum(stats_tld.values())
    
    print(f"\n{B}{CY}Total Domains: {total}{R}\n")
    
    for i, (tld, count) in enumerate(sorted(stats_tld.items(), key=lambda x: x[1], reverse=True)[:40], 1):
        bar_len = int((count / total) * 30)
        bar = f"{P3}{'#' * bar_len}{GR}{'.' * (30 - bar_len)}{R}"
        print(f"{P4}{i:2d}.{R} .{tld.upper():<8} {bar} {B}{count}{R}")
    
    input(f"\n{P4}Press Enter to continue...{R}")

def menu_stats():
    banner()
    box("STATISTICS")
    
    try:
        if not os.path.exists(OUTPUT_FILE):
            print(f"\n{YL}No accounts created yet{R}")
            time.sleep(2)
            return
        
        with open(OUTPUT_FILE, 'r') as f:
            lines = f.readlines()
        
        total = len(lines)
        with_cookies = sum(1 for line in lines if line.count('|') >= 3 and len(line.split('|')[3].strip()) > 20)
        without_cookies = total - with_cookies
        
        print(f"\n{CY}Total Accounts:{R} {B}{total}{R}")
        print(f"{GN}With Cookies:{R} {B}{with_cookies}{R}")
        print(f"{YL}Without Cookies:{R} {B}{without_cookies}{R}")
        print(f"\n{CY}Output File:{R} {OUTPUT_FILE}")
        print(f"{CY}Log File:{R} {LOG_FILE}")
        
        if lines:
            print(f"\n{P3}{'-' * W}{R}")
            print(f"{B}Last 5 Accounts:{R}\n")
            for line in lines[-5:]:
                parts = line.strip().split('|')
                if len(parts) >= 4:
                    uid, pwd, email, cookies = parts[0], parts[1], parts[2], parts[3]
                    cookie_status = f"{GN}YES{R}" if len(cookies) > 20 else f"{RD}NO{R}"
                    print(f"{P4}*{R} {uid[:15]:<15} {GR}|{R} {email[:22]:<22}")
                    print(f"  {CY}Cookies:{R} {cookie_status}\n")
        
    except Exception as e:
        write_log(f"Stats error: {str(e)}", "ERROR")
    
    input(f"\n{P4}Press Enter to continue...{R}")

# CREATION PROCESS
def start_creation(domains):
    banner()
    
    box_fade_in("CREATION PROCESS", [
        f"{CY}Domains:{R} {B}{len(domains)}{R}",
        f"{CY}Target:{R} {B}{config.get('account_limit', 10)} accounts{R}",
        f"{CY}Endpoint:{R} {B}{config.get('endpoint', 'desktop').title()}{R}",
        f"{CY}OTP Mode:{R} {B}{'Enabled' if config.get('use_tinyhost') else 'Disabled'}{R}"
    ])
    
    print()
    loading_animation("Starting Worker 1 (Creation)", 0.5)
    worker1 = CreationWorker(1)
    worker1.start()
    
    if config.get('use_tinyhost') and not config.get('use_manual_email'):
        loading_animation("Starting Worker 2 (Monitor)", 0.5)
        worker2 = MonitorWorker(2)
        worker2.start()
    else:
        worker2 = None
    
    loading_animation("Starting Worker 3 (Verifier)", 0.5)
    worker3 = VerifyWorker(3)
    worker3.start()
    
    account_limit = config.get('account_limit', 10)
    domain_index = 0
    
    for i in range(account_limit):
        domain = domains[domain_index % len(domains)]
        creation_queue.put(domain)
        domain_index += 1
    
    print(f"\n{GN}{'=' * W}{R}")
    print(f"{B}{WH}Creating {account_limit} accounts using {len(domains)} domain(s){R}".center(W + 18))
    print(f"{GN}{'=' * W}{R}\n")
    
    write_log(f"Creation process started - Target: {account_limit} accounts", "SYSTEM")
    
    time.sleep(1)
    
    print(f"{P3}+{'-' * (W-2)}+{R}")
    print(f"{P3}|{R} {B}{WH}{'LIVE STATUS':^56}{R} {P3}|{R}")
    print(f"{P3}+{'-' * (W-2)}+{R}")
    
    start_time = time.time()
    last_update = time.time()
    
    while not creation_queue.empty() or not monitor_queue.empty() or not verify_queue.empty():
        current_time = time.time()
        
        if stats['total_created'] >= account_limit:
            break
        
        if current_time - last_update >= 0.5:
            elapsed = int(current_time - start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            
            progress = int((stats['total_created'] / account_limit) * 40)
            bar = f"{P3}{'#' * progress}{P1}{'.' * (40 - progress)}{R}"
            percent = int((stats['total_created'] / account_limit) * 100)
            
            print(f"{P3}|{R} {bar} {B}{percent:3d}%{R} {P3}|{R}")
            print(f"{P3}|{R} {' ' * 56} {P3}|{R}")
            print(f"{P3}|{R} {BG1}{B}{WH} OK = {stats['ok_count']:3d} {R}  {BG2}{B}{WH} CP = {stats['cp_count']:3d} {R}  {CY}Time: {mins:02d}:{secs:02d}{R} {P3}|{R}")
            print(f"{P3}+{'-' * (W-2)}+{R}")
            
            print(f"\033[4A", end='')
            
            last_update = current_time
        
        time.sleep(0.3)
    
    creation_queue.join()
    monitor_queue.join()
    verify_queue.join()
    
    creation_queue.put("STOP")
    if worker2:
        monitor_queue.put("STOP")
    verify_queue.put("STOP")
    
    worker1.join(timeout=5)
    if worker2:
        worker2.join(timeout=5)
    worker3.join(timeout=5)
    
    print(f"\033[4B")
    
    duration = time.time() - start_time
    mins = int(duration // 60)
    secs = int(duration % 60)
    
    print(f"\n{GN}{'=' * W}{R}")
    print(f"{B}{GN}CREATION COMPLETED!{R}".center(W + 20))
    print(f"{GN}{'=' * W}{R}\n")
    
    write_log(f"Creation process completed - Duration: {mins}m {secs}s", "SYSTEM")
    
    time.sleep(0.5)
    
    box("FINAL REPORT", [
        f"{GN}* OK (With Cookies):{R} {B}{stats['ok_count']}{R}",
        f"{RD}x CP (Failed/No Cookies):{R} {B}{stats['cp_count']}{R}",
        f"{CY}- Total Processed:{R} {B}{stats['total_created']}{R}",
        f"{BL}T Duration:{R} {B}{mins:02d}m {secs:02d}s{R}",
        f"{PK}F Output:{R} {OUTPUT_FILE}",
        f"{YL}L Logs:{R} {LOG_FILE}"
    ], GN)
    
    stats['total_created'] = 0
    stats['total_verified'] = 0
    stats['total_with_cookies'] = 0
    stats['total_failed'] = 0
    stats['ok_count'] = 0
    stats['cp_count'] = 0
    
    input(f"\n{P4}> Press Enter to continue...{R}")

# INITIALIZATION
def welcome_screen():
    clear()
    
    banner_lines = [
        f"{P1}+============================================================+",
        f"{P1}|{P2}############################################################{P1}|",
        f"{P1}|{P3}##{P4}+====================================================+{P3}##{P1}|",
        f"{P1}|{P3}##{P4}|{PK}   FACEBOOK CREATOR - UNIFIED EDITION          {P4}|{P3}##{P1}|",
        f"{P1}|{P3}##{P4}|{PK}   Triple-Worker Architecture                   {P4}|{P3}##{P1}|",
        f"{P1}|{P3}##{P4}|{P5}   Create -> Monitor -> Verify -> Extract       {P4}|{P3}##{P1}|",
        f"{P1}|{P3}##{P4}|{CY}   Mobile + Desktop Endpoints                    {P4}|{P3}##{P1}|",
        f"{P1}|{P3}##{P4}|{BL}   File Logging System Enabled                  {P4}|{P3}##{P1}|",
        f"{P1}|{P3}##{P4}+====================================================+{P3}##{P1}|",
        f"{P1}|{P2}############################################################{P1}|",
        f"{P1}+============================================================+{R}"
    ]
    
    for line in banner_lines:
        print(line)
        time.sleep(0.08)
    
    print(f"\n{P3}+============================================================+")
    time.sleep(0.05)
    print(f"{P3}|{R}            {B}{PK}Developer: ZeeTheFounder{R}                     {P3}|")
    time.sleep(0.05)
    print(f"{P3}+============================================================+{R}\n")
    time.sleep(0.3)
    
    typewriter_effect(f"{B}{CY}Welcome to Elite Facebook Creator!{R}", 0.04)
    time.sleep(0.5)
    
    loading_animation("Initializing Core Systems", 1.5)
    loading_animation("Loading Security Modules", 1.2)
    loading_animation("Preparing Worker Threads", 1.0)
    
    print(f"\n{GN}{'=' * W}{R}")
    print(f"{B}{WH}System Ready!{R}".center(W + 18))
    print(f"{GN}{'=' * W}{R}\n")
    time.sleep(1)

def init_system():
    try:
        banner()
        box_fade_in("INITIALIZING SYSTEM", [
            f"{BL}Triple-Worker Architecture{R}",
            f"{P4}Worker 1: Account Creation (Mobile/Desktop){R}",
            f"{P4}Worker 2: OTP Monitoring (Tinyhost){R}",
            f"{P4}Worker 3: OTP Verification & Cookie Extract{R}"
        ])
        
        print()
        loading_animation("Initializing database", 1.0)
        init_db()
        
        loading_animation("Loading configuration", 0.8)
        load_config()
        
        loading_animation("Clearing old logs", 0.5)
        clear_logs()
        
        with db_conn() as conn:
            cursor = conn.execute("SELECT COUNT(*) as total FROM domains")
            total = cursor.fetchone()['total']
        
        if total == 0:
            print(f"\n{YL}!{R} {B}No domains in local database{R}")
            loading_animation("Connecting to server", 1.0)
            
            domains = email_api.get_all_domains(show_progress=True)
            
            if domains:
                print(f"\n{P4}*{R} {B}Storing domains in database...{R}")
                with db_conn() as conn:
                    stored = 0
                    for i, domain in enumerate(domains):
                        tld = domain.split('.')[-1]
                        try:
                            conn.execute("INSERT OR IGNORE INTO domains (domain, tld) VALUES (?, ?)", (domain, tld))
                            stored += 1
                            if (i + 1) % 50 == 0:
                                progress_bar_download(i + 1, len(domains), f"{CY}Storing{R}")
                        except:
                            pass
                    progress_bar_download(len(domains), len(domains), f"{CY}Storing{R}")
                print(f"\n\n{GN}*{R} {B}Stored {stored} domains in database{R}")
            else:
                print(f"\n{RD}x{R} {B}Failed to fetch domains from server{R}")
                time.sleep(2)
        else:
            print(f"\n{GN}*{R} {B}Found {total} domains in local database{R}")
        
        print()
        loading_animation("Preparing system components", 1.0)
        
        print(f"\n{GN}{'=' * W}{R}")
        print(f"{B}{GN}* System Ready!{R}".center(W + 20))
        print(f"{GN}{'=' * W}{R}\n")
        time.sleep(1.5)
        return True
    except Exception as e:
        print(f"\n{RD}x{R} {B}Initialization failed: {str(e)}{R}")
        write_log(f"Initialization failed: {str(e)}", "ERROR")
        time.sleep(3)
        return False

# MAIN
def main():
    try:
        welcome_screen()
        
        if not init_system():
            print(f"\n{RD}x{R} {B}Startup failed{R}")
            return
        
        menu_main()
        
    except KeyboardInterrupt:
        clear()
        print(f"\n{P3}{'=' * W}{R}")
        print(f"{B}{YL}! Interrupted by user{R}".center(W + 20))
        print(f"{P3}{'=' * W}{R}\n")
        write_log("Program interrupted by user", "SYSTEM")
        time.sleep(1)
    except Exception as e:
        print(f"\n{RD}x{R} {B}Fatal error: {str(e)}{R}")
        write_log(f"Fatal error: {str(e)}", "ERROR")
        time.sleep(2)

if __name__ == "__main__":
    main()
