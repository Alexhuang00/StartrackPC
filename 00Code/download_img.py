import os, requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.lulin.ncu.edu.tw/weather/allSkyHistory/2024-09-26"
DL_DIR = "/home/user/StartrackPC/01Image/"
SITE_ROOT = "https://www.lulin.ncu.edu.tw/"

os.makedirs(DL_DIR, exist_ok=True)

def list_remote_images():
    html = requests.get(BASE_URL).text
    soup = BeautifulSoup(html, "html.parser")
    all_links = [a['href'] for a in soup.find_all("a") if a['href'].lower().endswith(".jpg")]
    filtered_links = []
    for link in all_links:
        try:
            parts = link.replace(".jpg", "").split("__")
            date_part, time_part = parts
            hour = int(time_part.split("_")[0])
            if hour >= 23 or hour <= 0:
                filtered_links.append(link)
        except Exception as e:
            print(f"Skipping {link}, parse error:", e)
    return sorted(set(filtered_links))

def download_image(filename):
    # Build full download URL from site root + relative path
    url = SITE_ROOT + filename.lstrip("/")

    # Only save the file name (no subfolders)
    img_name = os.path.basename(filename)
    path = os.path.join(DL_DIR, img_name)

    if not os.path.exists(path):
        r = requests.get(url)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        print("Downloaded", img_name)
    else:
        print("Already exists:", img_name)

    return path

def cleanup_downloads():
    for img in list_remote_images():
        img_name = os.path.basename(img)
        path = os.path.join(DL_DIR, img_name)
        if os.path.exists(path):
            os.remove(path)
            print("Deleted", img_name)
        else:
            print("Not found:", img_name)

for img in list_remote_images():
    download_image(img)

