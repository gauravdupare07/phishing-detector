import os
import csv
import pandas as pd
import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

def normalize_url(u: str) -> str:
    try:
        parts = urlsplit(u.strip())
        scheme = parts.scheme.lower() or 'http'
        netloc = parts.netloc.lower()
        netloc = re.sub(r':(80|443)$', '', netloc)
        path = parts.path or '/'
        path = re.sub(r'/+$', '/', path)
        q = urlencode(sorted(parse_qsl(parts.query, keep_blank_values=True)))
        return urlunsplit((scheme, netloc, path, q, ''))
    except Exception:
        return u.strip()

def create_sample_files():
    os.makedirs('data', exist_ok=True)
    phishing = [
        "http://secure-paypal.com.login.verify-account.xyz/Confirm?user=test@example.com",
        "http://accounts.google.com.secure-login-example.xyz/signin",
        "http://login.paypal-security.verify-info.example/confirm",
        "http://bit.ly/2fakeid?redirect=http://malicious.example.com"
    ]
    legit = [
        "https://www.google.com/",
        "https://www.github.com/",
        "https://www.paypal.com/us/home",
        "https://www.microsoft.com/en-us"
    ]
    with open('data/raw_phishing.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['url','label'])
        for u in phishing:
            writer.writerow([u, 1])
    with open('data/raw_legit.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['url','label'])
        for u in legit:
            writer.writerow([u, 0])
    print("Sample files written to data/raw_phishing.csv and data/raw_legit.csv")

def build_dataset(input_files=None):
    if input_files is None:
        input_files = [('data/raw_phishing.csv', 1), ('data/raw_legit.csv', 0)]
    frames = []
    for path, lbl in input_files:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        df = pd.read_csv(path)
        if 'url' not in df.columns:
            raise ValueError(f"{path} missing 'url' column")
        if 'label' not in df.columns:
            df['label'] = lbl
        frames.append(df[['url','label']])
    df = pd.concat(frames, ignore_index=True)
    df['url'] = df['url'].astype(str).map(normalize_url)
    df.drop_duplicates(subset=['url'], inplace=True)
    df = df[df['url'].str.startswith(('http://','https://'))].copy()
    df.reset_index(drop=True, inplace=True)
    return df

if __name__ == "__main__":
    # If the user doesn't provide any data, create small samples
    if not (os.path.exists('data/raw_phishing.csv') and os.path.exists('data/raw_legit.csv')):
        create_sample_files()
    df = build_dataset()
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/urls_clean.csv', index=False)
    print("Wrote data/urls_clean.csv with counts:")
    print(df['label'].value_counts())
