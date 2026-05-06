from playwright.sync_api import sync_playwright

def test_scrape():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://nextleap.app/course/product-management-course", wait_until="networkidle")
        page.wait_for_timeout(3000)
        
        # Get all visible text on the page
        text = page.evaluate("document.body.innerText")
        
        with open("scratch_text.txt", "w", encoding="utf-8") as f:
            f.write(text)
            
        print("Text saved to scratch_text.txt")
        browser.close()

if __name__ == "__main__":
    test_scrape()
