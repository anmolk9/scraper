import requests
from bs4 import BeautifulSoup
import socket
import argparse

def get_volunteer_counts(event_name, start, end):
    # Generate URLs of the pages to scrape
    urls = [f'https://www.parkrun.org.uk/{event_name}/results/{i}/' for i in range(start, end - 1, -1)]

    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Global dictionary to store the count of volunteers
    volunteer_counts = {}

    for url in urls:
        try:
            # Send a GET request to the page with headers
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, features='html.parser')

            # Find the paddedb paragraph within the nested divs
            paddedb_p = (soup.find('div', id='main')
                         .find('div', id='primary')
                         .find('div', id='content')
                         .find('div', class_='paddedt left')
                         .find('p', class_='paddedb'))

            if paddedb_p:
                # Extract the text from the paddedb paragraph
                paddedb_text = paddedb_p.get_text(strip=True)

                # Remove the introductory text
                intro_text = "We are very grateful to the volunteers who made this event happen:"
                names_text = paddedb_text.replace(intro_text, "").strip()

                # Extract names and update the count in the global dictionary
                for name in names_text.split(','):
                    name = name.strip()
                    if name:
                        if name in volunteer_counts:
                            volunteer_counts[name] += 1
                        else:
                            volunteer_counts[name] = 1
            else:
                print("Paddedb paragraph not found.")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        except socket.gaierror as e:
            print(f"DNS resolution failed: {e}")

    # Sort the dictionary by count in descending order and print the sorted list
    sorted_volunteers = sorted(volunteer_counts.items(), key=lambda item: item[1], reverse=True)
    return sorted_volunteers


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape volunteer counts from parkrun results pages.')
    parser.add_argument('event_name', type=str, help='The name of the parkrun event (e.g., southwark)')
    parser.add_argument('start', type=int, help='The starting event number')
    parser.add_argument('end', type=int, help='The ending event number')

    args = parser.parse_args()

    volunteer_counts = get_volunteer_counts(args.event_name, args.start, args.end)
    print(volunteer_counts)
