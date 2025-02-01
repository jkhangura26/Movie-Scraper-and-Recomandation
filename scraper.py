import csv
from bs4 import BeautifulSoup
import requests
import sys

def get_movie_details(movie_url, session):
    """Universal movie detail extraction with rating and genre using requests session"""
    try:
        response = session.get(movie_url)
        response.raise_for_status()
        movie_soup = BeautifulSoup(response.text, "html.parser")

        rating_element = movie_soup.find("div", {"data-testid": "hero-rating-bar__aggregate-rating__score"})
        rating = rating_element.text.strip() if rating_element else "N/A"
        rating = rating.replace('/10', '').strip() if rating != "N/A" else "N/A"

        genre_elements = movie_soup.select("div[data-testid='interests'] a")
        genre = ", ".join([g.text for g in genre_elements]) if genre_elements else "N/A"

        director_section = movie_soup.find("li", {"data-testid": "title-pc-principal-credit"})
        director = ", ".join([a.text for a in director_section.select("a")]) if director_section else "N/A"
        
        cast = ", ".join([a.text.strip() for a in movie_soup.select("a[data-testid='title-cast-item__actor']")[:3]]) or "N/A"
        
        plot = movie_soup.select_one("span[data-testid='plot-xl']").text if movie_soup.select_one("span[data-testid='plot-xl']") else "N/A"
        
        runtime = movie_soup.select_one("li[data-testid='title-techspec_runtime']").get_text(" ", strip=True).replace("Runtime", "").strip() if movie_soup.select_one("li[data-testid='title-techspec_runtime']") else "N/A"
        
        poster = movie_soup.select_one("img.ipc-image")["src"] if movie_soup.select_one("img.ipc-image") else "N/A"

        return {
            "Rating": rating,
            "Genre": genre,
            "Director": director,
            "Cast": cast,
            "Plot": plot,
            "Runtime": runtime,
            "Poster": poster
        }
    except Exception as e:
        print(f"Error getting details: {str(e)}", file=sys.stderr)
        return None

def scraper(movie_names):
    """Main scraping function with optimized memory usage"""
    movie_data = []
    titles_added_or_existing = []
    existing_entries = set()
    file_exists = False

    # Read existing entries
    try:
        with open("movies.csv", 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            file_exists = True
            for row in reader:
                existing_entries.add((row['Title'], row['Year']))
    except FileNotFoundError:
        pass

    # Create reusable session
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })

    current_run_entries = set()

    for movie_name in movie_names:
        try:
            search_query = movie_name.replace(" ", "+")
            search_url = f"https://www.imdb.com/find?q={search_query}&s=tt&ttype=ft&ref_=fn_mv"
            response = session.get(search_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Search error for '{movie_name}': {e}", file=sys.stderr)
            continue

        search_soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract first result
        first_result = search_soup.select_one("a.ipc-metadata-list-summary-item__t")
        if not first_result:
            print(f"Movie '{movie_name}' not found.", file=sys.stderr)
            continue

        # Get title and URL
        title = first_result.text.strip()
        movie_url = first_result.get('href', '')
        if not movie_url.startswith('http'):
            movie_url = f'https://www.imdb.com{movie_url}'

        # Extract year
        year_element = search_soup.select_one("div.ipc-metadata-list-summary-item__tc li")
        year = year_element.text.strip() if year_element else "N/A"

        # Check duplicates
        if (title, year) in existing_entries or (title, year) in current_run_entries:
            print(f"{title} ({year}) already exists, skipping.", file=sys.stderr)
            titles_added_or_existing.append(title)
            continue

        # Get detailed information
        details = get_movie_details(movie_url, session)
        if not details:
            continue

        current_run_entries.add((title, year))
        movie_entry = {
            "Title": title,
            "Year": year,
            **details
        }
        movie_data.append(movie_entry)
        titles_added_or_existing.append(title)

    # Write results
    if movie_data:
        fieldnames = ["Title", "Year", "Rating", "Genre", "Director", 
                     "Cast", "Plot", "Runtime", "Poster"]
        
        with open("movies.csv", 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(movie_data)
            
        print(f"Added {len(movie_data)} new entries to movies.csv", file=sys.stderr)

    return titles_added_or_existing

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python optimized_scraper.py \"Movie Name\" or movie_list.txt", file=sys.stderr)
        sys.exit(1)
    
    input_arg = sys.argv[1]
    
    if input_arg.endswith(".txt"):
        try:
            with open(input_arg, "r") as f:
                movie_list = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"File '{input_arg}' not found.", file=sys.stderr)
            sys.exit(1)
    else:
        movie_list = [input_arg]

    result = scraper(movie_list)
    print("\n".join(result))