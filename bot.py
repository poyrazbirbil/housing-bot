import os
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from grand_relocation import grandreloc
load_dotenv()

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

URLS = {
    "Student Experience Zuidas": "https://studentexperience.com/studios?los=longstay&locationId=3",
    "Student Experience Amstel": "https://studentexperience.com/studios?los=longstay&locationId=5",
    "OurCampus Diemen": "https://new-ourcampus-amsterdam-diemen-rentcafewebsiteuk.securerc.co.uk/onlineleasing/new-ourcampus-amsterdam-diemen/floorplans.aspx",
     "The Social Hub Amsterdam City": "https://www.thesocialhub.co/book-student-room/?hotelId=AMS02",
}

def socialhub_status(page):
    bubble = page.locator(
        ".BubbleMessage__InfoBubbleContainer.BubbleMessage__InfoBubbleContainer--Failure"
    )

    if bubble.count() > 0:
        text = bubble.inner_text().lower()

        if "no availability" in text:
            return False

    return True

def student_experience_status(page):
    text = page.locator("body").inner_text().lower()

    # Explicit "no availability" message
    if "it seems we don't have available studios at this location right now" in text:
        return False, 0

    # Count visible studio cards
    studio_count = page.locator(".studio:visible").count()

    return studio_count > 0, studio_count


def ourcampus_status(page):
    # Find all buttons in the Availability column
    buttons = page.locator("td:last-child")

    count = buttons.count()

    available = 0

    for i in range(count):
        text = buttons.nth(i).inner_text().strip().lower()

        if "get notified" not in text:
            available += 1

    return available > 0, available

def telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": message,
        },
        timeout=30,
    )


def page_available(page_text):
    text = page_text.lower()

    positive = [
        "available",
        "book now",
        "reserve",
        "apply now",
        "lease now",
    ]

    negative = [
        "no availability",
        "fully booked",
        "sold out",
        "unavailable",
        "waitlist",
    ]

    if any(word in text for word in negative):
        return False

    if any(word in text for word in positive):
        return True

    return False


def check_site(browser, name, url):
    page = browser.new_page()

    try:
        page.goto(url, wait_until="load", timeout=90000)
        page.wait_for_timeout(8000)

        text = page.locator("body").inner_text()

        if "studentexperience.com" in url:
            available, studio_count = student_experience_status(page)

            if available:
                status = f"✅ {studio_count} studio(s) available"
            else:
                status = "❌ No studios available"
        elif "securerc.co.uk" in url:
            available, studio_count = ourcampus_status(page)

            if available:
                status = f"✅ {studio_count} available floor plan(s)"
            else:
                status = "❌ No floor plans available"
        elif "thesocialhub.co" in url:
            available = socialhub_status(page)

            if available:
                status = "✅ Rooms available"
            else:
                status = "❌ No rooms available"
        else:
            available = page_available(text)
            studio_count = None

            status = "✅ AVAILABLE" if available else "❌ No availability"

        print(name, status)

        return {
            "name": name,
            "status": status,
            "url": url,
        }

    except Exception as e:
        print(name, e)

        return {
            "name": name,
            "status": f"⚠️ Error: {e}",
            "url": url,
        }

    finally:
        page.close()


def main():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for name, url in URLS.items():
            results.append(check_site(browser, name, url))

        browser.close()

    message = "🏠 Studio Availability Report\n\n"
    data = grandreloc()
    print(data)
    for r in results:
        message += (
            f"{r['name']}\n"
            f"{r['status']}\n"
            f"{r['url']}\n\n"
        )
    
    message += f"{data}"
    print(message)
    telegram(message)


if __name__ == "__main__":
    main()