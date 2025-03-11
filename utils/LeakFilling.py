import requests
import time

proxies = {
    "YOUR_PROXY",
}

def retry_request(url, retries=3, timeout=2):
    last_status_code = None
    for _ in range(retries):
        try:
            response = requests.get(url, timeout=timeout, proxies=proxies)
            if response.status_code == 200:
                print(f"Success: {url}")
                return response.status_code
            elif response.status_code == 404:
                print(f"404: {url}")
                return response.status_code
            else:
                last_status_code = response.status_code
        except requests.RequestException:
            time.sleep(1)
    return last_status_code

def process_failed_urls(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            url = line.strip()
            status_code = retry_request(url)
            outfile.write(f"{status_code}\n")

if __name__ == "__main__":
    input_file = 'Logs/failed_day_urls.txt'
    output_file = 'Logs/retry_results.txt'
    process_failed_urls(input_file, output_file)