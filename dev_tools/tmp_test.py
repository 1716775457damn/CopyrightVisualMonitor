import os
from page_judger import PageJudger

pj = PageJudger(logger_callback=lambda x: None)

with open('debug_clip_全部.txt', 'r', encoding='utf-8') as f:
    raw_text = f.read()

records = pj._parse_clipboard_text(raw_text, '全部')

for r in records:
    print(r)
print(f"Total parsed: {len(records)}")
