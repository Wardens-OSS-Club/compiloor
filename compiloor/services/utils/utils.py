from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    result = urlparse(url)
    return all([result.scheme, result.netloc])