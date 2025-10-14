import requests
from bs4 import BeautifulSoup
import re
import os
import time
from pathlib import Path

# --- కాన్ఫిగరేషన్ (Configuration) ---
# కథల కేటగిరీకి బేస్ URL
BASE_URL = "https://eemaata.com/em/category/features/stories"
# గరిష్ట పేజీల సంఖ్య (1 నుండి 52 వరకు)
MAX_PAGES = 52 
# అవుట్‌పుట్ ఫైళ్లను సేవ్ చేయడానికి డైరెక్టరీ
OUTPUT_DIR_NAME = "eemaata_stories_output"

# ఫైల్ పేరు స్థిరత్వం కోసం నెల సంఖ్య నుండి ఇంగ్లీష్ సంక్షిప్త రూపంలోకి మ్యాపింగ్
MONTH_NUMBER_TO_ABBR = {
    '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May',
    '06': 'Jun', '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct',
    '11': 'Nov', '12': 'Dec'
}

def sanitize_filename(title: str, month: str, year: str) -> str:
    """
    కథ వివరాల నుండి ఫైల్సిస్టమ్-సేఫ్ ఫైల్ పేరును సృష్టిస్తుంది.
    """
    # అవసరమైన ఫార్మాట్: title_publication-month_publication-year.txt
    filename = f"{title}_{month}_{year}"
    
    # సిస్టమ్‌లలో సమస్యలను కలిగించే అక్షరాలను తొలగిస్తుంది.
    safe_filename = re.sub(r'[\\/?%*:|"<>\[\]\r\n\t]', '', filename)
    
    # అదనపు ఖాళీలను ఒకే ఖాళీతో భర్తీ చేసి, ముందు/వెనుక ఖాళీలను తొలగిస్తుంది
    safe_filename = re.sub(r'\s+', ' ', safe_filename).strip()
    
    # ఫైల్ పేరు సులభంగా చదవడానికి ఖాళీలను అండర్‌స్కోర్‌లతో భర్తీ చేస్తుంది
    safe_filename = safe_filename.replace(' ', '_')
    
    # OS పరిమితులను నివారించడానికి పొడవును పరిమితం చేస్తుంది (శీర్షిక చివరి భాగాన్ని మరియు తేదీని అలాగే ఉంచుతుంది)
    if len(safe_filename) > 150:
        date_suffix = f"_{month}_{year}"
        title_part = safe_filename[:-len(date_suffix)]
        safe_filename = title_part[:150 - len(date_suffix)] + date_suffix
        
    return safe_filename + ".txt"

def extract_date_from_href(url: str) -> tuple[str, str]:
    """
    Permalinks (https://eemaata.com/em/issues/YYYYMM/entry_id.html) నుండి 
    నెల మరియు సంవత్సరాన్ని YYYYMM ఫార్మాట్‌లో సంగ్రహిస్తుంది.
    """
    month, year = "UnknownMonth", "UnknownYear"
    if url:
        # /issues/YYYYMM/ ను కనుగొనే ప్యాటర్న్ (ఉదా: /issues/202510/)
        match = re.search(r'/issues/(\d{6})/', url) 
        if match:
            date_code = match.group(1) # e.g., '202510'
            year = date_code[:4]       # e.g., '2025'
            month_num = date_code[4:]  # e.g., '10'
            month = MONTH_NUMBER_TO_ABBR.get(month_num, f"Month{month_num}")
    return month, year

def scrape_story_details(session: requests.Session, story_data: dict, output_dir: Path) -> int:
    """
    ఒక వ్యక్తిగత కథ పేజీని ఫెచ్ చేసి, దాని నుండి పూర్తి వివరాలను సంగ్రహించి, ఫైల్‌గా సేవ్ చేస్తుంది.
    """
    story_url = story_data['url']
    author = story_data['author']
    
    # 1. వ్యక్తిగత కథ పేజీని ఫెచ్ చేయండి
    try:
        response = session.get(story_url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] కథ పేజీని ఫెచ్ చేయడంలో లోపం: {story_url}: {e}")
        return 0 # Indicate failure

    story_soup = BeautifulSoup(response.content, 'html.parser')
    
    # 2. శీర్షిక (Title) - H1 ఎలిమెంట్ (పేజీలో నిర్ధారించబడింది)
    full_title_tag = story_soup.find('h1', class_='entry-title')
    title = full_title_tag.get_text(strip=True) if full_title_tag else story_data['title']

    # 3. తేదీని permalink (story_url) నుండి సంగ్రహించండి
    month, year = extract_date_from_href(story_url)

    # 4. పూర్తి కథా కంటెంట్‌ను సంగ్రహించండి (ఎటువంటి సెపరేటర్ లేకుండా)
    content_tag = story_soup.find('div', class_='entry-content')
    
    content_text = "ERROR: కథ కంటెంట్ కనుగొనబడలేదు."
    if content_tag:
        # యూజర్ అభ్యర్థన మేరకు: ట్యాగ్‌లను తొలగించి, ఖాళీలను శుభ్రం చేస్తూ మొత్తం టెక్స్ట్‌ను సంగ్రహిస్తుంది (separator లేకుండా).
        content_text = content_tag.get_text(strip=True) 

    # 5. ఫైల్ కంటెంట్‌ను నిర్మించి సేవ్ చేయండి
    file_content = (
        f"శీర్షిక (Title): {title}\n"
        f"రచయిత (Author): {author}\n"
        f"ప్రచురణ తేదీ (Publication Date): {month}, {year}\n"
        f"{'='*50}\n\n"
        f"{content_text}"
    )
    
    filename = sanitize_filename(title, month, year)
    filepath = output_dir / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)
        print(f"  [SUCCESS] కథ సేవ్ చేయబడింది: {title} -> {filename}")
        return 1 # Indicate success
    except Exception as e:
        print(f"  [ERROR] ఫైల్ సేవ్ చేయడంలో లోపం {filename}: {e}")
        return 0


def scrape_eemaata_stories(max_pages: int):
    """
    eemaata.com కథల ఇండెక్స్ పేజీల నుండి లింకులను సేకరించి, ప్రతి కథ పేజీని సందర్శించి,
    పూర్తి కథా వివరాలను ఫైళ్లకు సేవ్ చేయడానికి ప్రధాన ఫంక్షన్.
    """
    print(f"eemaata.com యొక్క {max_pages} పేజీల నుండి కథల లింకులను సేకరిస్తోంది...")
    
    output_dir = Path(OUTPUT_DIR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    story_links_to_scrape = []

    # --- Step 1: ఇండెక్స్ పేజీల నుండి అన్ని కథ లింకులను సేకరించండి ---
    for page_num in range(1, max_pages + 1):
        url = BASE_URL if page_num == 1 else f"{BASE_URL}/page/{page_num}"
            
        print(f"\n--- లింకులు సేకరిస్తోంది: పేజీ {page_num}/{max_pages} ---")
        
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status() 
        except requests.exceptions.RequestException as e:
            print(f"[CRITICAL ERROR] ఇండెక్స్ పేజీ {page_num} ({url}) ను ఫెచ్ చేయడంలో లోపం: {e}")
            time.sleep(5) 
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        posts_container = soup.find('div', id='posts')
        
        if not posts_container:
            print(f"[WARNING] పేజీ {page_num} లో '#posts' కంటైనర్ కనుగొనబడలేదు. దాటవేయబడుతోంది.")
            continue
            
        story_articles = posts_container.find_all('article')
        
        if not story_articles:
            print(f"[WARNING] పేజీ {page_num} లో కథల ఆర్టికల్స్ కనుగొనబడలేదు.")
            
        for article in story_articles:
            # ప్రధాన కథ లింక్ (మీరు అడిగిన permalink)
            permalink_tag = article.find('a', class_='entry-permalink')
            story_url = permalink_tag.get('href') if permalink_tag else None
            
            # శీర్షిక (ఫాల్‌బ్యాక్ కోసం)
            title_tag = article.find(class_='entry-title')
            title = title_tag.get_text(strip=True) if title_tag else "No Title"

            # రచయిత (ఇండెక్స్ పేజీ నుండి)
            author_tag = article.find(class_='entry-meta')
            author = author_tag.get_text(strip=True).replace('రచన: ', '').strip() if author_tag else "Unknown Author"

            # లింకులో తేదీ సమాచారం ఉంది కాబట్టి cat-links నుండి href అవసరం లేదు.

            if story_url:
                story_links_to_scrape.append({
                    'url': story_url,
                    'title': title, # ఇండెక్స్ పేజీ నుండి టైటిల్ ఫాల్‌బ్యాక్‌గా ఉంచబడింది
                    'author': author,
                    # 'date_href' ను తొలగించారు, ఎందుకంటే తేదీని story_url నుండి సంగ్రహిస్తారు
                })

        time.sleep(1) # ఇండెక్స్ పేజీల మధ్య విరామం

    print(f"\n--- మొత్తం {len(story_links_to_scrape)} కథల లింకులు సేకరించబడ్డాయి. ఇప్పుడు వ్యక్తిగత కథలను స్క్రేపింగ్ చేస్తోంది ---")
    
    # --- Step 2: ప్రతి కథ లింక్‌ను సందర్శించి, కంటెంట్‌ను సంగ్రహించి సేవ్ చేయండి ---
    total_stories_saved = 0
    for story_data in story_links_to_scrape:
        
        # వ్యక్తిగత కథ పేజీని స్క్రేప్ చేసి సేవ్ చేయండి
        success = scrape_story_details(session, story_data, output_dir)
        total_stories_saved += success
        
        time.sleep(1) # ప్రతి కథ మధ్య విరామం
        
    print(f"\n{'#'*60}")
    print(f"--- స్క్రేపింగ్ పూర్తయింది ---")
    print(f"మొత్తం {total_stories_saved} కథలు '{output_dir}' డైరెక్టరీలో విజయవంతంగా సేవ్ చేయబడ్డాయి.")
    print(f"{'#'*60}")


if __name__ == '__main__':
    # మీరు MAX_PAGES ను 10 లాంటి చిన్న సంఖ్యకు సెట్ చేయడం ద్వారా మొదట టెస్ట్ చేయవచ్చు.
    scrape_eemaata_stories(MAX_PAGES)
