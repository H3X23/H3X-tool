#!/usr/bin/env python3
import subprocess
import time
import sys
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# --- RENKLER ---
DARK_RED = "\033[38;5;124m"
RED      = "\033[31m"
BLUE     = "\033[34m"
YELLOW   = "\033[33m"
GREEN    = "\033[32m"
BOLD     = "\033[1m"
CYAN     = "\033[36m"
RESET    = "\033[0m"

found_count = 0

def loading_anim(mesaj, renk, duration=10):
    spinner = ["|", "/", "-", "\\"]
    for i in range(duration):
        sys.stdout.write(f"\r{renk}{mesaj} {spinner[i % 4]}{RESET}")
        sys.stdout.flush()
        time.sleep(0.05)
    sys.stdout.write("\r" + " " * 80 + "\r")

def check_dir(site, d):
    global found_count
    # Bazı WAF'ları atlatmak için User-Agent ekledik
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) H3X-Scanner/1.0'}
    try:
        url = f"{site}/{d}"
        r = requests.get(url, timeout=3, allow_redirects=False, headers=headers)
        if r.status_code == 200:
            # tqdm barı varken print kullanımı barı kaydırabilir, 
            # tqdm.write kullanarak bunu engelliyoruz
            tqdm.write(f"{GREEN}[+] BULUNDU: /{d:<20} {BOLD}(200 OK){RESET}")
            found_count += 1
        elif r.status_code == 403:
            tqdm.write(f"{YELLOW}[!] YASAKLI: /{d:<20} (403 Forbidden){RESET}")
            found_count += 1
    except requests.exceptions.RequestException:
        pass

# --- ANA PROGRAM DÖNGÜSÜ ---
while True:
    os.system("clear || cls") 
    print(f"{DARK_RED}{BOLD}")
    print("    ██╗  ██╗ ██████╗ ██╗  ██╗")
    print("    ██║  ██║ ╚════██╗╚██╗██╔╝")
    print("    ███████║  █████╔╝ ╚███╔╝ ")
    print("    ██╔══██║  ╚═══██╗ ██╔██╗ ")
    print("    ██║  ██║ ██████╔╝██╔╝ ██╗")
    print("    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝")
    print(f"\n{YELLOW}{BOLD}PROF.DR H3X DER Kİ:{RESET}")
    print(f"{CYAN}\"Başarı yolunda pc de yaksan elektrikte çarpsa eve fbi gelse bile mübahtır\"{RESET}")
    
    print(f"\n{BLUE}_____________________________________{RESET}\n")
    print(f"  {RED}[0]{RESET} Çıkış\n  {YELLOW}[1]{RESET} Port Tarama (Nmap)\n  {GREEN}[2]{RESET} Basit load test (AB)\n  {CYAN}[3]{RESET} Dizin Tarama")
    print(f"{BLUE}_____________________________________{RESET}\n")

    secim = input(DARK_RED + "H3X > " + RESET)

    if secim == "0":
        loading_anim("Çıkılıyor", RED, 15)
        print(f"{BLUE}Bye Bye{RESET}"); break

    elif secim == "1":
        target = input(f"{YELLOW}Hedef IP: {RESET}")
        p = subprocess.Popen(["nmap", "-F", target], stdout=subprocess.PIPE, text=True)
        while p.poll() is None:
            loading_anim("Portlar taranıyor", YELLOW, 5)
        out, _ = p.communicate()
        print(f"{GREEN}\n[+] AKTİF PORTLAR:{RESET}")
        for line in out.splitlines():
            if "/tcp" in line and "open" in line:
                parts = line.split()
                print(f"    {GREEN}● {YELLOW}{parts[0]:<10} {GREEN}{parts[2]}{RESET}")
        input(f"\n{YELLOW}Geri dönmek için Enter...{RESET}")

    elif secim == "2":
        url = input(f"{GREEN}Hedef URL: {RESET}")
        if not url.startswith("http"): url = "http://" + url
        p = subprocess.Popen(["ab", "-n", "1000", "-c", "50", url], stdout=subprocess.DEVNULL)
        while p.poll() is None:
            loading_anim("Paketler basılıyor", GREEN, 5)
        print(f"{GREEN}[+] Tamamlandı.{RESET}")
        input(f"\n{YELLOW}Geri dönmek için Enter...{RESET}")

    elif secim == "3":
        site = input(f"{CYAN}Hedef Site: {RESET}")
        if not site.startswith("http"): site = "http://" + site
        
        if os.path.exists("wordlist"):
            files = [f for f in os.listdir("wordlist") if f.endswith('.txt')]
            if not files:
                print(f"{RED}[!] 'wordlist' klasörü boş!{RESET}")
                input(f"\n{YELLOW}Geri dönmek için Enter...{RESET}"); continue
                
            print(f"\n{YELLOW}Mevcut Listeler:{RESET}")
            for f in files: print(f"  {CYAN}» {f}{RESET}")
        else: 
            print(f"{RED}[!] 'wordlist' klasörü yok!{RESET}")
            input(f"\n{YELLOW}Geri dönmek için Enter...{RESET}"); continue

        wordlist_name = input(f"\n{DARK_RED}Seçilen dosya: {RESET}").strip()
        filepath = os.path.join("wordlist", wordlist_name)
        
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                dirs = [line.strip() for line in f if line.strip()]
            
            found_count = 0
            print(f"\n{BLUE}[>] Hızlıca {len(dirs)} dizin taranıyor...{RESET}\n")
            
            # TQDM ENTEGRASYONU
            with tqdm(total=len(dirs), desc="H3X Scan", unit="dir", colour="cyan") as pbar:
                with ThreadPoolExecutor(max_workers=100) as executor:
                    futures = [executor.submit(check_dir, site, d) for d in dirs]
                    for future in as_completed(futures):
                        pbar.update(1)
            
            print(f"\n{GREEN}[✔] Tarama bitti. Toplam {found_count} bulgu.{RESET}")
            print(f"{BOLD}{CYAN}tarama bitti{RESET}")
        else:
            print(f"{RED}\n[!] Dosya bulunamadı!{RESET}")
            
        input(f"\n{YELLOW}Geri dönmek için Enter...{RESET}")
