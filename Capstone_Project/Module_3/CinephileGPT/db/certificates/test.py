import base64

with open(r"D:\Github\Purwadhika-AI-Engineering-Bootcamp\Capstone Project\Module 3\CinephileGPT\db\certificates\ca.pem", "rb") as f:
    print(base64.b64encode(f.read()).decode())