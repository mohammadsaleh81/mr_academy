import requests
import pandas as pd
import time  # To add delays between requests


def fetch_single_page_data(api_url, params=None):
    """Fetches data from a single specified API page."""
    try:
        print(f"Fetching data from: {api_url} with parameters: {params}")
        response = requests.get(api_url, params=params)
        # response.raise_for_status()  # Raises an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API at URL {api_url}: {e}")
        return None
    except requests.exceptions.JSONDecodeError:
        print(f"Error decoding JSON from URL {api_url}. The response was not valid JSON.")
        return None


def export_to_excel(all_items, fields_to_export, excel_filename="output.xlsx"):
    """Exports the specified data to an Excel file."""
    if not all_items:
        print("No data to export.")
        return

    items_to_export = []
    for item in all_items:
        if isinstance(item, dict):  # Ensure each item is a dictionary
            # Select only the desired fields.
            # If a field is not present in the item, it will be skipped for that item.
            selected_item = {field: item.get(field) for field in fields_to_export if field in item}

            # If you want all specified fields in the Excel, even if they are missing in some items (with a None/blank value):
            # selected_item = {field: item.get(field, None) for field in fields_to_export}
            items_to_export.append(selected_item)
        else:
            print(f"Skipped item as it is not a dictionary: {item}")

    if not items_to_export:
        print("No data found with the specified fields to export.")
        return

    df = pd.DataFrame(items_to_export)

    try:
        df.to_excel(excel_filename, index=False, engine='openpyxl')
        print(f"Data successfully exported to '{excel_filename}'. Total rows: {len(df)}")
    except Exception as e:
        print(f"Error exporting data to Excel: {e}")


# --- Configuration ---
BASE_API_URL = "https://mindapi.mobo.news/ex/acs/"  # Base URL without page parameters

# Fields you want to export from each item to the Excel file.
# You should edit this list based on your needs and the actual API response.
FIELDS_TO_EXPORT = [
    'id',
    'title',
    'title_fa',
    'slug',
    'global_barcode',
    'tf_model'
    'tf_model_2'
    'techfinder'

]
EXCEL_FILENAME = "mobo_news_data_all_pages.xlsx"
REQUEST_DELAY_SECONDS = 1  # Delay between consecutive requests to avoid overloading the server

# --- Script Execution ---
# if __name__ == "__main__":
def run():
    all_items_from_api = []
    current_page = 1
    # An upper limit to prevent infinite loops, based on your information (around 140 pages)
    max_pages_to_try = 126

    print("Starting the process to fetch data from all pages...")
    # Attempting to use a 'page' query parameter
    while current_page <= max_pages_to_try:
        params = {'page': current_page}  # Assuming the API uses 'page' as the query parameter
        page_data = fetch_single_page_data(BASE_API_URL, params=params)
        print(current_page)

        if page_data:
            page_data = page_data['results']
            for item in page_data:
                # print(item['title'])
                # print(item['organization'])
                # print('8888888888888888888888888888')
                if item['organization'] != 1:
                    item['techfinder'] =f'https://techfinder.ir/product/{item["slug"]}'
                    all_items_from_api.append(item)


            current_page += 1

        else:
            print(f"Error fetching data from page {current_page} or page does not exist. Halting process.")
            break  # Exit loop on error fetching data

        time.sleep(REQUEST_DELAY_SECONDS)  # Delay before the next request

    if all_items_from_api:
        export_to_excel(all_items_from_api, FIELDS_TO_EXPORT, EXCEL_FILENAME)
    else:
        print("No data was fetched from the API.")


run()