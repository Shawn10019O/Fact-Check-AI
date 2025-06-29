from typing import Tuple

#ドメインごとに信頼度ラベルとスコアを返す
def get_source_reliability(url: str) -> Tuple[str, int]:
    url = url.lower()
    high = [
        ".sciencemag.org",
        "nature.com",
        "cell.com",
        "arxiv.org",
        "ieee.org",
        "acm.org",
        "pubmed.ncbi.nlm.nih.gov",
        ".go.jp",
        ".gov",
        ".ac.jp",
        ".edu",
    ]
    med = [
        "wikipedia.org",
        "bbc.com",
        "reuters.com",
        "apnews.com",
        "nytimes.com",
        "nikkei.com",
        "asahi.com",
        "yomiuri.co.jp",
        "stat.go.jp",
    ]
    if any(d in url for d in high):
        return "高", 3
    if any(d in url for d in med):
        return "中", 2
    return "低", 1