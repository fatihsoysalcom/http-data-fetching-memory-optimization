import requests
import json
import time
import sys

# --- Configuration ---
# Simulate fetching data from multiple "financial endpoints".
# httpbin.org/stream/N yields N lines of JSON, perfect for line-by-line processing.
# This simulates receiving multiple transaction records from different sources.
MOCK_FINANCIAL_ENDPOINTS = [
    "https://httpbin.org/stream/5",  # Simulate 5 transaction records
    "https://httpbin.org/stream/10", # Simulate 10 transaction records
    "https://httpbin.org/stream/3",  # Simulate 3 transaction records
    "https://httpbin.org/status/500", # Simulate an error condition
    "https://httpbin.org/stream/7",  # Simulate 7 transaction records
]

# --- Memory-efficient Data Fetching and Processing ---

def fetch_data_lines_streamed(url):
    """
    Fetches data from a URL line by line, demonstrating memory efficiency
    for potentially large responses. Yields each line as a string.
    This avoids loading the entire response body into memory at once.
    """
    print(f"[{time.time():.2f}] Fetching (streamed lines): {url}...")
    try:
        with requests.get(url, stream=True, timeout=10) as response:
            response.raise_for_status() # Raise an exception for HTTP errors (e.g., 4xx, 5xx)
            for line in response.iter_lines(): # Iterate over response content line by line
                if line: # Filter out keep-alive new lines
                    yield line.decode('utf-8') # Decode bytes to string
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return # Stop yielding on error

def parse_transaction_lines(line_generator):
    """
    Parses lines of data (expected to be JSON) and yields individual
    transaction objects. This uses a generator to process data item by item,
    further reducing memory footprint by not storing all parsed objects.
    """
    for line in line_generator:
        try:
            # Each line from httpbin.org/stream/N is a JSON object
            transaction_data = json.loads(line)
            # In a real scenario, you'd extract specific financial fields here
            yield transaction_data # Yield the parsed transaction object
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON line: {line[:100]}...", file=sys.stderr)
        except Exception as e:
            print(f"Error processing line: {e} for line: {line[:100]}...", file=sys.stderr)

def get_financial_summaries_efficiently(endpoints):
    """
    Iterates through financial endpoints, fetches data efficiently (line by line),
    and yields a summary for each, without holding all raw data or all parsed
    transactions in memory simultaneously. Uses generators for memory optimization.
    """
    for url in endpoints:
        summary = {"url": url, "status": "failed", "transactions_count": 0}
        try:
            # Step 1: Fetch data lines in a streaming fashion (memory efficient)
            line_generator = fetch_data_lines_streamed(url)
            
            # Step 2: Parse each line (transaction) using a generator (memory efficient)
            transaction_generator = parse_transaction_lines(line_generator)
            
            # Step 3: Aggregate summary without storing all individual transactions
            current_endpoint_transactions = 0
            for transaction in transaction_generator:
                current_endpoint_transactions += 1 # Each yielded item is a transaction
            
            if current_endpoint_transactions > 0:
                summary["status"] = "success"
                summary["transactions_count"] = current_endpoint_transactions
            else:
                # If no transactions were yielded, check if it was an error or just empty
                summary["status"] = "no_data" if "status/500" not in url else "http_error"

        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error for {url}: {e}", file=sys.stderr)
            summary["status"] = "http_error"
        except requests.exceptions.RequestException as e:
            print(f"Network Error for {url}: {e}", file=sys.stderr)
            summary["status"] = "network_error"
        except Exception as e:
            print(f"Unexpected Error for {url}: {e}", file=sys.stderr)
            summary["status"] = "unexpected_error"
        
        yield summary # Yield summary for the current endpoint

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting financial data retrieval with RAM optimization focus...")
    print(f"Python version: {sys.version.split(' ')[0]}")
    print(f"Requests version: {requests.__version__}")
    print("-" * 40)

    all_summaries = []
    
    # Iterate through the generator, processing one endpoint at a time.
    # This ensures that raw response bodies and full parsed objects
    # for all endpoints are NOT kept in memory simultaneously.
    for summary in get_financial_summaries_efficiently(MOCK_FINANCIAL_ENDPOINTS):
        print(f"[{time.time():.2f}] Processed: {summary['url']} -> Status: {summary['status']}, Transactions: {summary['transactions_count']}")
        all_summaries.append(summary) # Store only the lightweight summary

    print("-" * 40)
    print("All financial data retrieval attempts completed.")
    print(f"Total endpoints processed: {len(all_summaries)}")
    
    # Calculate total transactions from collected summaries
    total_successful_transactions = sum(s['transactions_count'] for s in all_summaries if s['status'] == 'success')
    print(f"Total transactions counted across all successful endpoints: {total_successful_transactions}")

    print("\nDemonstrating memory usage concept:")
    print("The 'all_summaries' list holds only lightweight summary dictionaries.")
    print("Raw response data and full parsed transaction objects are processed")
    print("and discarded for each endpoint before moving to the next, ")
    print("minimizing peak memory footprint. This is crucial for environments")
    print("with limited RAM (e.g., 38MB as mentioned in the article).")
    print(f"Size of 'all_summaries' list object: {sys.getsizeof(all_summaries)} bytes")
    # A very rough estimate of the data stored in all_summaries
    total_elements_size = sum(sys.getsizeof(str(v)) for s in all_summaries for v in s.values()) + sum(sys.getsizeof(k) for s in all_summaries for k in s.keys())
    print(f"Approximate total size of data within 'all_summaries': {total_elements_size} bytes (excluding Python object overhead)")
    print("Note: Actual memory usage is more complex, involving Python interpreter overhead,")
    print("requests library internal buffers, etc. The demonstration focuses on the pattern.")
