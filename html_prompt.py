import os
import re
import requests
import google.genai as genai
from ddgs import DDGS  # ✅ for image search
import time
import subprocess
# ============================
# CONFIGURATION
# ============================
API_KEY = os.getenv("GEMINI_API_KEY")   # Replace with your Gemini API key
PROMPT_FILE = "mani_banifect.txt"
PROMPT_FILE2 = "prmopt2.txt"
OUTPUT_DIR = "output_parts"

# ============================
# CLIENT INIT
# ============================
client = genai.Client(api_key=API_KEY)

# ✅ Create a chat session (this remembers history!)
chat = client.chats.create(
    model="gemini-2.5-flash"
)
def concatenate_html_parts(output_dir=OUTPUT_DIR, final_filename="index.html"):
    """Concatenate all Part*.html files into one single HTML file."""
    files = sorted(
        [f for f in os.listdir(output_dir) if f.startswith("Part") and f.endswith(".html")],
        key=lambda x: int("".join(filter(str.isdigit, x)))
    )

    final_path = os.path.join(output_dir, final_filename)
    with open(final_path, "w", encoding="utf-8") as final_file:
        # Write the HTML header once
        final_file.write("<html>\n<head>\n")
        final_file.write('<link rel="stylesheet" href="style.css">\n')
        final_file.write("</head>\n<body>\n")

        # Append the body content of each Part file
        for fname in files:
            path = os.path.join(output_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

                # Remove duplicate <html>, <head>, <body>, </html>, </body>
                text = re.sub(r"<\/?(html|head|body).*?>", "", text, flags=re.IGNORECASE)
                final_file.write("\n" + text.strip() + "\n")

        # Close body/html tags once
        final_file.write("</body>\n</html>")

    print(f"✅ Final report saved as {final_path}")
    return final_path
# ============================
# HELPER FUNCTIONS
# ============================
# Remove Markdown code fences if present
def strip_code_fence(text: str) -> str:
    """
    Remove leading/trailing Markdown code fences and return inner content.
    Handles ```html, ```html\n, ``` (any language) and also single backtick blocks.
    If no fence found, returns original text.
    """
    if not text:
        return text

    text = text.strip()

    # 1) Remove triple-backtick fence with optional language tag
    m = re.search(r"^```[ \t]*([a-zA-Z0-9_-]+)?\n(.*)\n```$", text, flags=re.DOTALL)
    if m:
        return m.group(2).strip()

    # 2) If fences but not closing fence on same string, remove leading/trailing backticks
    #    (covers cases like "```html\n...html..." with no trailing fence)
    text = re.sub(r"^```[^\n]*\n", "", text, count=1)
    text = re.sub(r"\n```$", "", text, count=1)

    # 3) remove single-line fence: ```<lang>...``` or inline backticks
    text = re.sub(r"^`{3,}\s*", "", text)
    text = re.sub(r"\s*`{3,}$", "", text)

    # 4) Also remove a single pair of backticks around content
    if text.startswith("`") and text.endswith("`"):
        text = text[1:-1]

    return text.strip()
# Remove unwanted mentions of 'Part 1', 'Part 2', 'भाग 1', 'भाग 2' etc.

def clean_output(text: str) -> str:
    """
    Remove unwanted mentions of 'Part 1', 'Part 2', 'भाग 1', 'भाग 2' etc.
    """
    import re
    # Remove English "Part X"
    text = re.sub(r"Part\s*\d+", "" , text, flags=re.IGNORECASE)
    # Remove Hindi "भाग X"
    text = re.sub(r"भाग\s*\d+", "", text)
    return text.strip()

def call_gemini_chat(message_text):
    """Send a message in the chat session and return text output."""
    response = chat.send_message(message_text)
    return response.text

def save_output(text, filename, output_dir=OUTPUT_DIR):
    """Save model output to file with correct extension."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path
# ✅ Image download function using DuckDuckGo Images


def download_image(query, filename, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)

    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=1))
        if not results:
            print(f"❌ No results for {query}")
            return None

        img_url = results[0]["image"]
        print(f"🔗 Found image for {query}: {img_url}")

        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(img_url, headers=headers, timeout=15)

        with open(path, "wb") as f:
            f.write(resp.content)

        print(f"✅ Saved {filename}")
        time.sleep(2)  # small pause
        return path
    except Exception as e:
        print(f"⚠️ Error downloading {query}: {e}")
        return None

# ✅ Process image_prompt.txt to extract URLs and download images
def process_image_prompt(file_path):
    """Read image_prompt.txt and download images for policy, company, product."""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    matches = re.findall(r'"([^"]+)"', text)

    if len(matches) == 3:
        policy, company, product = matches
        download_image(policy, "policy_announcement.png")
        download_image(company, "company_announcement.png")
        download_image(product, "product_announcement.png")
    else:
        print("❌ Could not parse image_prompt.txt")

# ============================
# MAIN LOGIC
# ============================

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    prompt1 = f.read().strip()
with open(PROMPT_FILE2, "r", encoding="utf-8") as f:
    prompt2 = f.read().strip()

html_counter = 1
state = None   # "html" or "image"

# --- Step 1: Run PROMPT_FILE → Part1.html ---
print("🔄 Running PROMPT_FILE...")
res1 = call_gemini_chat(prompt1)
res1 = strip_code_fence(res1)
res1 = clean_output(res1)
file1 = save_output(res1, f"Part{html_counter}.html")
print("💾 Saved:", file1)
state = "html"
html_counter += 1

# --- Simulated user messages ---
user_messages = ["next part strick foll", "next part", "PROMPT_FILE2", "next part"]

for msg in user_messages:
    print(f"\n📝 User sent: {msg}")

    if msg == "next part" and state == "html":
        res = call_gemini_chat("Continue with next part of the report.")
        res = strip_code_fence(res)
        res = clean_output(res)
        filename = f"Part{html_counter}.html"
        file = save_output(res, filename)
        print("💾 Saved:", file)
        html_counter += 1

    elif msg == "PROMPT_FILE2":
        res = call_gemini_chat(prompt2)
        
        file = save_output(res, "image_prompt.txt")
        print("💾 Saved:", file)
        state = "image"

        # ✅ After saving image_prompt.txt, auto-download images
        process_image_prompt(file)

    elif msg == "next part" and state == "image":
        res = call_gemini_chat("Continue with CSS styling output.")
        
        file = save_output(res, "style.css")
        print("💾 Saved:", file)
# ✅ Concatenate only once, after the loop finishes
concatenate_html_parts()


def upload_to_github_and_netlify():
    print("\n🚀 Uploading to GitHub + Netlify...")

    repo_path = r"D:\Astik_Project\Goverment _project\automation_html"  # your repo path
    commit_msg = "Daily auto-update final report"

    try:
        # GitHub push
        subprocess.run(["git", "-C", repo_path, "add", "."], check=True)
        subprocess.run(["git", "-C", repo_path, "commit", "-m", commit_msg], check=True)

        # First try normal push
        result = subprocess.run(["git", "-C", repo_path, "push"], capture_output=True, text=True)

        # If rejected, force push
        if "rejected" in result.stderr:
            print("⚠️ Normal push failed, trying force push...")
            subprocess.run(["git", "-C", repo_path, "push", "--force"], check=True)

        print("✅ Uploaded to GitHub")

        # Netlify deploy
        subprocess.run(["netlify", "deploy", "--dir", repo_path, "--prod"], check=True)
        print("🌐 Site deployed to Netlify")

    except Exception as e:
        print(f"⚠️ Upload failed: {e}")

# ============================
# ASK USER AT END
# ============================
choice = input("\nDo you want to upload to GitHub + Netlify? (y/n): ").strip().lower()
if choice == "y":
    upload_to_github_and_netlify()
else:
    print("❌ Skipped upload.")