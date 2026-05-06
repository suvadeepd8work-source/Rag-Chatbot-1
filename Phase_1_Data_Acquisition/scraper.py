from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import markdownify
import os

COHORTS = {
    "Product Management": "https://nextleap.app/course/product-management-course",
    "UX Design": "https://nextleap.app/course/ui-ux-design-course",
    "Data Analytics": "https://nextleap.app/course/data-analyst-course",
    "Business Analytics": "https://nextleap.app/course/business-analyst-course",
    "Generative AI": "https://nextleap.app/course/generative-ai-course",
}

import json
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraped_data")

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove common noisy elements like nav, footer, script, style
    for element in soup(["nav", "footer", "script", "style", "header", "noscript", "svg"]):
        element.extract()
        
    return str(soup)

def extract_key_data(html_content):
    """Extract required fields from the cleaned HTML.
    Returns a dict with keys: live_hours, duration, mentorship, placement_support,
    cohort_start, cost, original_cost, emi, price_increase_date, live_schedule, 
    instructors, average_salary, highest_salary, source_url.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    # Get text with better separator for parsing
    text = soup.get_text(separator=' | ', strip=True)
    data = {}
    import re
    
    # 1. Hours and duration
    hours_match = re.search(r"(\d{1,3}\+?\s*Hours?)\s*[|]*\s*(?:Live\s*Classes|of\s*Live\s*Content|Live\s*Sessions)", text, re.I)
    if not hours_match:
        hours_match = re.search(r"Live\s*Sessions?\s*[|]*\s*on\s*Zoom", text, re.I)
    data["live_hours"] = hours_match.group(1) if hours_match and hours_match.groups() and hours_match.group(1) else (hours_match.group(0) if hours_match else None)
    
    # Duration: prefer "X months Fellowship timeline" or similar patterns
    duration_match = re.search(r"(\d{1,2}\s*months?)\s*Fellowship\s*timeline", text, re.I)
    if not duration_match:
        duration_match = re.search(r"(\d{1,2}\s*(?:months?|weeks?))", text, re.I)
    data["duration"] = duration_match.group(1) if duration_match else None
    
    # 2. Mentorship
    mentor_match = re.search(r"Mentorship\s*[|]*\s*([A-Za-z\s&]+)", text, re.I)
    if not mentor_match:
        mentor_match = re.search(r"Mentorship\s*\|\s*([A-Za-z\s&]+)", text, re.I)
    data["mentorship"] = mentor_match.group(1).strip() if mentor_match else None
    
    # 3. Placement support
    placement_match = re.search(r"((?:1\s*Year\s*)?Placement\s*Support(?:\s*for\s*1\s*year)?)", text, re.I)
    data["placement_support"] = placement_match.group(1).strip() if placement_match else None
    
    # 4. Cohort start date
    start_match = re.search(r"(?:Cohort\s*\d+\s*starts?\s*on|Starts\s*on|Cohort\s*\d+\s*starts?|Starts)\s*[|]*\s*([A-Za-z]+\s*\d{1,2})", text, re.I)
    data["cohort_start"] = start_match.group(1) if start_match else None
    
    # 5. Cost and EMI
    prices = re.findall(r"₹\s*([\d,]+)", text)
    if prices:
        # Unique prices sorted descending to differentiate original vs discounted
        unique_prices = sorted(list(set(p.replace(",", "") for p in prices)), key=lambda x: int(x), reverse=True)
        if len(unique_prices) >= 2:
            data["cost"] = unique_prices[1] # Lower one usually discounted
            data["original_cost"] = unique_prices[0] # Higher one usually original
        else:
            data["cost"] = unique_prices[0]
            data["original_cost"] = None
            
        emi_match = re.search(r"EMI\s*from\s*₹\s*([\d,]+)", text, re.I)
        if emi_match:
            data["emi"] = emi_match.group(1).replace(",", "")
        else:
            data["emi"] = None
    else:
        data["cost"] = None
        data["original_cost"] = None
        data["emi"] = None
        
    # 6. Price increase date
    price_inc_match = re.search(r"Price\s*increase\s*[|]*\s*(?:from|on)\s*[|]*\s*(\d{1,2}\s*[A-Za-z]+|\d{1,2}\s*[A-Za-z]+\s*[\d:]+\s*[APM]+)", text, re.I)
    if not price_inc_match:
        price_inc_match = re.search(r"Price\s*increase\s*from\s*([A-Za-z]+\s*\d{1,2})", text, re.I)
    if not price_inc_match:
        price_inc_match = re.search(r"Enrolment\s*ends\s*on\s*(\d{1,2}\s*[A-Za-z]+)", text, re.I)
    data["price_increase_date"] = price_inc_match.group(1) if price_inc_match else None
    
    # 7. Live schedule
    schedule_section = soup.find(string=re.compile(r"Live\s*Class\s*Schedule", re.I))
    if schedule_section:
        parent = schedule_section.find_parent(['div', 'section'])
        if parent:
            data["live_schedule"] = " ".join(parent.stripped_strings)
        else:
            data["live_schedule"] = schedule_section.strip()
    else:
        data["live_schedule"] = None
        
    # 8. Instructors - More robust extraction
    instructors = []
    # Find instructor cards based on common structure (h3 for names)
    for card in soup.find_all(['div', 'section']):
        # Look for name + role pattern
        h3 = card.find('h3')
        if h3 and h3.get_text(strip=True):
            name = h3.get_text(strip=True)
            # Find the role/company info (often follows in the same card)
            card_text = card.get_text(separator=' | ', strip=True)
            if '@' in card_text or 'Previously' in card_text:
                # Extract the part with @ or Previously
                info_match = re.search(r"([^|]+(?:@|Previously @|Previously\s+@)[^|]+)", card_text)
                if info_match:
                    info = info_match.group(1).strip()
                    if name not in info and len(name) < 40:
                        instructors.append(f"{name} - {info}")

    # Fallback to text-based if DOM search failed
    if not instructors:
        for line in text.split(' | '):
            if '@' in line and '-' in line:
                instructors.append(line.replace('\n', ' ').strip())
                
    # Deduplicate while preserving order
    data["instructors"] = list(dict.fromkeys(instructors))[:20] if instructors else None
    
    # 9. Salary info
    avg_sal_match = re.search(r"Average.*?Salary.*?([\d-]+ Lakhs)", text, re.I)
    data["average_salary"] = avg_sal_match.group(1) if avg_sal_match else None
    high_sal_match = re.search(r"Highest Salary.*?([\d]+ Lakhs)", text, re.I)
    data["highest_salary"] = high_sal_match.group(1) if high_sal_match else None
    
    return data

def scrape_course(page, name, url):
    print(f"Scraping {name} from {url}...")
    try:
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(3000) # wait 3s for React to render
        html_content = page.content()
        cleaned_html = clean_html(html_content)
        md_content = markdownify.markdownify(cleaned_html, heading_style="ATX")
        # Extract structured data
        key_data = extract_key_data(cleaned_html)
        key_data["source_url"] = url
        # Combine markdown and JSON data
        # Return both as a tuple
        return md_content, key_data
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None, None

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for name, url in COHORTS.items():
            md_content, key_data = scrape_course(page, name, url)
            if md_content:
                filename_md = os.path.join(OUTPUT_DIR, f"{name.lower().replace(' ', '_')}.md")
                filename_json = os.path.join(OUTPUT_DIR, f"{name.lower().replace(' ', '_')}.json")
                with open(filename_md, 'w', encoding='utf-8') as f_md:
                    f_md.write(f"# {name}\n\n")
                    f_md.write(f"Source URL: {url}\n\n")
                    f_md.write(md_content)
                with open(filename_json, 'w', encoding='utf-8') as f_json:
                    json.dump(key_data, f_json, indent=2)
                print(f"Successfully saved {name} to {filename_md} and {filename_json}")
                
        browser.close()

if __name__ == "__main__":
    main()
