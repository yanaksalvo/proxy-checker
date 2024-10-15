import requests
import threading
from tkinter import Tk
from tkinter.filedialog import askopenfilename

WORKING_PROXIES_FILE = 'work.txt'
BAD_PROXIES_FILE = 'bad.txt'
TEST_URL = 'https://www.google.com'

valid_proxies = 0
bad_proxies = 0
total_proxies = 0
lock = threading.Lock()

def check_proxy(proxy, sem):
    global valid_proxies, bad_proxies
    try:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        response = requests.get(TEST_URL, proxies=proxies, timeout=3)
        
        if response.status_code == 200:
            with lock:
                valid_proxies += 1
            save_proxy_to_file(proxy, WORKING_PROXIES_FILE)
        else:
            raise Exception("Invalid response")
    except Exception:
        with lock:
            bad_proxies += 1
        save_proxy_to_file(proxy, BAD_PROXIES_FILE)
    finally:
        sem.release()

def save_proxy_to_file(proxy, file_name):
    with open(file_name, 'a') as f:
        f.write(f"{proxy}\n")

def main():
    global total_proxies

    thread_count = int(input("Thread sayısını girin: "))

    Tk().withdraw()
    proxy_file = askopenfilename(title="Proxy Dosyasını Seçin", filetypes=[("Text files", "*.txt")])
    
    if not proxy_file:
        print("Dosya seçilmedi, çıkılıyor.")
        return

    with open(proxy_file, 'r') as f:
        proxies = [line.strip() for line in f]

    total_proxies = len(proxies)

    sem = threading.Semaphore(thread_count)
    threads = []

    for proxy in proxies:
        sem.acquire()
        thread = threading.Thread(target=check_proxy, args=(proxy, sem))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(f"Çalışan proxy sayısı: {valid_proxies}/{total_proxies}")
    print(f"Çalışmayan proxy sayısı: {bad_proxies}/{total_proxies}")

if __name__ == '__main__':
    main()
