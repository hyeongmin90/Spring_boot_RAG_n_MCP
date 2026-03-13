import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from markdownify import markdownify as md
import re
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def get_content(url):
    """페이지 본문 추출 (Markdown 변환)"""
    try:
        resp = requests.get(url, headers=headers, timeout=300)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, "html.parser")
        
        for tag in soup(["nav", "footer", "header", "script", "style", "aside"]):
            tag.decompose()
        
        content = soup.find("article", class_="doc") or soup.find("main") or soup.find("div", {"id": "content"})
        
        if not content:
            return ""

        html_content = str(content)
        text = md(html_content, heading_style="ATX", strip=['a'])
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
        
    except Exception as e:
        print(f"    Error: {e}")
        return ""
    return ""

def extract_path_from_url(url):
    """URL에서 경로 추출"""
    if '/docs.spring.io/' in url:
        path = url.split('/docs.spring.io/')[-1]
        path = path.replace('.html', '')
        path = path.replace('/', '_')
        return path
    else:
        return url.split('/')[-1].replace('.html', '')

def fetch_docs(start_url="https://docs.spring.io/spring-boot/reference/", max_pages=None):
    """Spring 문서 크롤링 (Markdown 변환 후 yield)"""
    
    print(f"Fetching index from {start_url}...")
    
    try:
        response = requests.get(start_url, headers=headers, timeout=30)
        response.raise_for_status()
        index_html = response.text
    except requests.RequestException as e:
        print(f"Error: {e}")
        return
    
    soup = BeautifulSoup(index_html, 'html.parser')
    
    base_domain = urlparse(start_url).netloc
    url_path = urlparse(start_url).path
    if url_path.endswith('/'):
        url_path = url_path[:-1]
    base_path = url_path
    
    links_to_visit = set()
    sidebar = soup.find("div", class_="nav-panel-menu") or soup.find("nav", class_="nav-menu")
    
    if not sidebar:
        links_source = soup
    else:
        links_source = sidebar
        
    for a in links_source.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(start_url, href)
        clean_url = full_url.split('#')[0]
        parsed_url = urlparse(clean_url)

        if (parsed_url.netloc == base_domain and 
            base_path in parsed_url.path and 
            clean_url.endswith('.html') and
            clean_url != start_url):
            
            relative_path = parsed_url.path.replace(base_path, '')
            if relative_path.startswith('/'):
                relative_path = relative_path[1:]
                
            if relative_path and (relative_path[0].isdigit() or 'SNAPSHOT' in relative_path):
                continue
                
            links_to_visit.add(clean_url)
    
    print(f"Found {len(links_to_visit)} unique URLs")
    links_list = list(links_to_visit)
    
    if max_pages:
        links_list = links_list[:max_pages]
    
    print(f"\nCrawling {len(links_list)} pages...")
    print("="*80)
    
    success_count = 0
    saved_files = {}

    for i, url in enumerate(links_list, 1):
        filepath_name = extract_path_from_url(url)
        print(f"[{i}/{len(links_list)}] {filepath_name}", flush=True)
        
        markdown_text = get_content(url)
        
        if markdown_text:
            filename = filepath_name or f"page_{i}"
            
            if filename in saved_files:
                counter = 1
                base = filename
                while f"{base}_{counter}" in saved_files:
                    counter += 1
                filename = f"{base}_{counter}"
            
            saved_files[filename] = url
            success_count += 1
            yield {'url': url, 'content': markdown_text}
        else:
            print(f"  ✗ Content too short or empty")
    
    print("\n" + "="*80)
    print(f"Completed: {success_count}/{len(links_list)} pages saved")


if __name__ == "__main__":
    for _ in fetch_docs(max_pages=100):
        pass
