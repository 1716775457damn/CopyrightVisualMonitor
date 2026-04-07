"""Debug clipboard parsing - paste clipboard content and parse to see what's extracted"""
import pyperclip
import re

# Read clipboard
raw = pyperclip.paste()

# Save raw clipboard to file first for inspection
with open("debug_clipboard.txt", "w", encoding="utf-8") as f:
    f.write(raw)

print("=== Clipboard saved to debug_clipboard.txt ===")
print("First 2000 chars:")
print(raw[:2000])
