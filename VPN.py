# edge_loc_test.py
import time
import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def start_edge_with_geolocation(lat, lon, accuracy=100, inprivate=True):
    options = Options()
    # اگر می‌خواهی با پنجره خصوصی باز شود:
    if inprivate:
        options.add_argument("--inprivate")

    # اگر لازم شد مسیر باینری edge را صراحتاً مشخص کن:
    # options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    # webdriver-manager برای msedgedriver مناسب را دانلود می‌کند
    service = Service(EdgeChromiumDriverManager().install())

    driver = webdriver.Edge(service=service, options=options)

    # پاک کردن کوکی‌ها برای شروع پاک (اختیاری)
    try:
        driver.delete_all_cookies()
    except Exception:
        pass

    # دادن دسترسی geolocation به origin عمومی google (این دستور ممکن است گاهی خطا دهد اما معمولاً کار می‌کند)
    try:
        driver.execute_cdp_cmd("Browser.grantPermissions", {
            "origin": "https://www.google.com",
            "permissions": ["geolocation"]
        })
    except Exception as e:
        print("Warn: grantPermissions failed:", e)

    # override موقعیت
    try:
        driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
            "latitude": float(lat),
            "longitude": float(lon),
            "accuracy": int(accuracy)
        })
    except Exception as e:
        print("Error setting geolocation override:", e)
        driver.quit()
        raise

    return driver

def test_google_search_for_location(lat, lon, query="my+location"):
    driver = start_edge_with_geolocation(lat, lon, inprivate=True)
    try:
        driver.get("https://www.google.com")
        time.sleep(1)

        # اگر می‌خوای از جستجوی فارسی استفاده کنی، query را تغییر بده
        search_url = f"https://www.google.com/search?q={query}"
        driver.get(search_url)
        time.sleep(3)

        out_dir = "edge_loc_results"
        os.makedirs(out_dir, exist_ok=True)
        base = f"{out_dir}/result_lat{lat}_lon{lon}"
        driver.save_screenshot(base + ".png")
        with open(base + ".html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        print("Saved:", base + ".png", "and", base + ".html")
    finally:
        driver.quit()

if __name__ == "__main__":
    # نمونه مختصات: تهران
    lat, lon = 35.6892, 51.3890
    # query را می‌توانی به فارسی یا انگلیسی بذاری؛ مثلاً "نزدیک‌ترین رستوران" یا "weather"
    query = "نزدیک‌ترین+رستوران"
    test_google_search_for_location(lat, lon, query)
