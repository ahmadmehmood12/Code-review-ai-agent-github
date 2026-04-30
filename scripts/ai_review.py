import os
import json
import subprocess
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


MAX_FILE_SIZE = 5000  # characters per file (prevent token overflow)


def get_changed_files():
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        capture_output=True,
        text=True
    )

    files = result.stdout.strip().split("\n")

    # Handle empty case
    if not files or files == ['']:
        print("No files changed.")
        return []

    return files


def read_files(files):
    code_map = {}

    for f in files:
        if os.path.exists(f) and os.path.isfile(f):
            try:
                with open(f, "r", encoding="utf-8", errors="ignore") as file:
                    content = file.read()

                    # Trim large files
                    if len(content) > MAX_FILE_SIZE:
                        content = content[:MAX_FILE_SIZE] + "\n... [TRUNCATED]"

                    code_map[f] = content
            except Exception as e:
                print(f"Error reading {f}: {e}")

    return code_map


def build_prompt(code_map):
    combined = ""

    for file, content in code_map.items():
        combined += f"\nFILE: {file}\n{content}\n"

    return combined


def clean_json_response(content: str):
    """Fix common LLM JSON formatting issues"""
    content = content.strip()

    # Remove markdown wrappers
    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    return content


def review_code(prompt):
    system_prompt = """
You are a strict senior code reviewer.

Return ONLY valid JSON:

{
  "status": "approved" | "rejected",
  "summary": "short explanation",
  "issues": [
    {
      "file": "path/to/file.py",
      "line": 10,
      "severity": "critical|warning",
      "comment": "what is wrong and how to fix"
    }
  ]
}

Rules:
- Reject if ANY critical issue exists
- Always include line numbers (best effort)
- If unsure about line, use line = 1
- Be concise and precise
- No extra text outside JSON
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    cleaned = clean_json_response(content)

    try:
        return json.loads(cleaned)
    except Exception as e:
        print("❌ Raw AI response:\n", content)
        raise Exception("Invalid JSON from AI")


def save_result(result):
    with open("review_result.json", "w") as f:
        json.dump(result, f, indent=2)


def main():
    print("🔍 Detecting changed files...")
    files = get_changed_files()

    if not files:
        # No changes → auto approve
        result = {
            "status": "approved",
            "summary": "No files changed",
            "issues": []
        }
        save_result(result)
        print("✅ No changes, auto-approved")
        return

    print(f"📂 Files changed: {files}")

    code_map = read_files(files)

    if not code_map:
        result = {
            "status": "approved",
            "summary": "No readable files",
            "issues": []
        }
        save_result(result)
        print("✅ No readable files, auto-approved")
        return

    prompt = build_prompt(code_map)

    print("🤖 Sending to AI for review...")
    result = review_code(prompt)

    save_result(result)

    print("📝 Review result:", result["status"])

    if result["status"] == "rejected":
        print("❌ Code rejected")
        exit(1)
    else:
        print("✅ Code approved")


if __name__ == "__main__":
    main()