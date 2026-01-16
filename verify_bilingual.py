import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

# Check the bilingual EPUB
book = epub.read_epub(r'D:\我的坚果云\在线书库\双语翻译测试\智能简史A Brief History of Intelligence Evolution, AI, and the Five -- Max Solomon Bennett -- S_l, 2023_bilingual.epub')
items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))

print(f"Total documents: {len(items)}")
print("\nChecking first document with content:")

# Find first document with paragraphs
for i, item in enumerate(items):
    content = item.get_content().decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    paras = soup.find_all('p')

    if len(paras) > 5:
        print(f"\nDocument {i}: {len(paras)} paragraphs")
        print("\nFirst 10 paragraphs (checking bilingual pairs):")

        for j in range(min(10, len(paras))):
            p = paras[j]
            text = p.get_text().strip()
            if text:
                has_chinese = any('\u4e00' <= c <= '\u9fff' for c in text)
                print(f"{j}. Chinese={has_chinese}: {text[:80]}...")
        break

print("\n✓ Verification complete")
