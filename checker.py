import requests
import time


def check_url(url: str, timeout: float, retries: int, slow_threshold: float, follow_redirects, json_output, quiet, user_agent) -> None:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    for attempt in range(1, retries + 1):
        if not json_output and not quiet:
            print(f"Checking {url} ({attempt}/{retries})...")
        start = time.perf_counter()

        try:
            headers = {
    "User-Agent": user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}
            response = requests.get(url, timeout=timeout, allow_redirects=follow_redirects, headers=headers)
            status_code = response.status_code
            
        except requests.exceptions.Timeout:
            label = "TIMEOUT"

        except requests.exceptions.SSLError:
            label = "SSL_ERROR"

        except requests.exceptions.ConnectionError as e:

            if "NameResolutionError" in str(e):
                label = "DNS_ERROR"
            else:
                label = "CONNECTION_ERROR"

        except requests.exceptions.RequestException:
            label = "ERROR"

        else:    
            end = time.perf_counter()
            duration_ms = (end - start) * 1000
            is_slow = slow_threshold is not None and duration_ms > slow_threshold

            if 200 <= status_code < 300:
                label = "OK"
            elif 300 <= status_code < 400:
                label = "REDIRECT"
            elif 400 <= status_code < 500:
                label = "CLIENT_ERROR"
            else:
                label = "SERVER_ERROR"

            if is_slow:
                label = "SLOW"

            return {
                "url": url,
                "label": label,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
            }
        
          
        if attempt == retries:
            end = time.perf_counter()
            duration_ms = (end - start) * 1000

            return {
                "url": url,
                "label": label,
                "status_code": None,
                "duration_ms": round(duration_ms, 2),
            }

        else:
            time.sleep(0.5)