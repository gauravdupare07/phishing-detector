import math
import re
import ipaddress
from urllib.parse import urlsplit, parse_qs
from collections import Counter
import pandas as pd
import tldextract

SUSPICIOUS_KEYWORDS = [
    "login","verify","update","secure","account","signin","confirm","support",
    "service","payment","billing","wallet","redirect","bank","alert","suspend",
    "reset","verification"
]

URL_SHORTENERS = {
    "bit.ly","t.co","tinyurl.com","ow.ly","is.gd","buff.ly","adf.ly","bitly.com",
    "cutt.ly","rebrand.ly","lnkd.in","shorturl.at","v.gd","youtu.be"
}

_tldx = tldextract.TLDExtract(cache_dir=".tldcache")

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c/n) * math.log2(c/n) for c in counts.values())

def is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except Exception:
        return False

def safe_len(x) -> int:
    return len(x) if x else 0

def extract_features(url: str) -> dict:
    feat = {}
    try:
        parts = urlsplit(url)
        scheme = parts.scheme.lower()
        host = parts.hostname or ""
        netloc = parts.netloc or ""
        path = parts.path or ""
        query = parts.query or ""

        feat['url_len'] = len(url)
        feat['host_len'] = safe_len(host)
        feat['path_len'] = safe_len(path)
        feat['query_len'] = safe_len(query)
        feat['num_dots'] = host.count('.')

        only_host = host.encode('idna').decode('ascii', errors='ignore') if host else ''
        feat['host_entropy'] = shannon_entropy(only_host)
        feat['count_digits'] = sum(ch.isdigit() for ch in url)
        feat['count_alpha'] = sum(ch.isalpha() for ch in url)
        feat['count_special'] = len(re.findall(r'[^A-Za-z0-9]', url))
        feat['pct_encoded'] = url.count('%') / max(1, feat['url_len'])

        feat['has_at'] = int('@' in url)
        feat['has_underscore'] = int('_' in host)
        feat['has_dash_in_host'] = int('-' in host)
        feat['has_double_slash_in_path'] = int('//' in path.strip('/'))
        feat['has_port'] = int(':' in netloc and not netloc.endswith(':80') and not netloc.endswith(':443'))
        feat['port_value'] = int(re.findall(r':(\d+)$', netloc)[0]) if re.search(r':(\d+)$', netloc) else 0
        feat['has_hex_in_path_or_query'] = int(bool(re.search(r'%[0-9A-Fa-f]{2}', path + '?' + query)))

        feat['scheme'] = scheme
        feat['uses_https'] = int(scheme == 'https')

        ext = _tldx(host)
        sld = ext.domain or ""
        suffix = ext.suffix or ""
        subdomain = ext.subdomain or ""
        feat['tld'] = suffix if suffix else 'NA'
        feat['sld'] = sld
        feat['num_subdomains'] = 0 if not subdomain else subdomain.count('.') + 1
        feat['is_ip_host'] = int(is_ip(host))
        feat['is_punycode'] = int(host.startswith('xn--') if host else 0)
        feat['is_shortener'] = int(host in URL_SHORTENERS)
        lower_all = (host + path + '?' + query).lower()
        feat['keyword_hits'] = sum(kw in lower_all for kw in SUSPICIOUS_KEYWORDS)

        qs = parse_qs(query, keep_blank_values=True)
        feat['query_kv_count'] = len(qs)
        feat['query_key_entropy'] = shannon_entropy(''.join(qs.keys()))

        feat['ratio_digits_host'] = sum(ch.isdigit() for ch in host) / max(1, len(host))
        feat['ratio_special_url'] = feat['count_special'] / max(1, feat['url_len'])
    except Exception:
        # fallback defaults
        keys = [
            'url_len','host_len','path_len','query_len','num_dots','host_entropy',
            'count_digits','count_alpha','count_special','pct_encoded',
            'has_at','has_underscore','has_dash_in_host','has_double_slash_in_path',
            'has_port','port_value','has_hex_in_path_or_query','scheme','uses_https',
            'tld','sld','num_subdomains','is_ip_host','is_punycode','is_shortener',
            'keyword_hits','query_kv_count','query_key_entropy','ratio_digits_host','ratio_special_url'
        ]
        for k in keys:
            feat[k] = 0
        feat['scheme'] = 'http'
        feat['tld'] = 'NA'
        feat['sld'] = ''
    return feat

def featurize_dataframe(df):
    feats = [extract_features(u) for u in df['url'].astype(str)]
    X = pd.DataFrame(feats)
    # group for split (e2LD)
    e2lds = []
    for u in df['url'].astype(str):
        try:
            host = urlsplit(u).hostname or ""
            ext = _tldx(host)
            e2ld = f"{ext.domain}.{ext.suffix}".strip('.')
            e2lds.append(e2ld if e2ld else host)
        except Exception:
            e2lds.append('')
    X['group_e2ld'] = e2lds
    return X
