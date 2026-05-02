import os
import requests
from github import Github
from openai import OpenAI

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)

repo_name = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("GITHUB_REF").split("/")[-2]

g = Github(GITHUB_TOKEN)
repo = g.get_repo(repo_name)
pr = repo.get_pull(int(pr_number))

diff = pr.get_files()

code_diff = ""
for file in diff:
    if file.patch:
        code_diff += f"\nFILE: {file.filename}\n{file.patch}\n"

prompt = f"""
You are a Senior Software Engineer performing a Pull Request review.

Your responsibilities:
- Detect syntax errors
- Detect bad coding practices
- Identify missing or weak exception handling
- Detect unsafe dictionary access or null handling issues
- Detect performance issues if obvious
- Suggest improvements like a senior engineer
- Be strict but constructive

Return format:
- Line-specific comments when possible
- Clear fix suggestion
- Severity: LOW / MEDIUM / HIGH

Code Diff:
{code_diff}
"""

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "system", "content": "You are a strict senior code reviewer."},
        {"role": "user", "content": prompt}
    ]
)

review = response.choices[0].message.content

# Post general PR comment
pr.create_issue_comment(review)

print("AI review completed")