import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import requests

def get_movie_details(movie_url):
    """Universal movie detail extraction with rating and genre"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(movie_url, headers=headers)
        movie_soup = BeautifulSoup(response.text, "html.parser")

        # Extract rating from movie page
        rating_element = movie_soup.find("div", {"data-testid": "hero-rating-bar__aggregate-rating__score"})
        rating = rating_element.text.strip() if rating_element else "N/A"

        # Extract genre
        genre_elements = movie_soup.select("div[data-testid='interests'] a")
        genre = ", ".join([g.text for g in genre_elements]) if genre_elements else "N/A"

        # Other details
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
        print(f"Error getting details: {str(e)}")
        return None

def scraper(movie_name=None):
    """Main scraping function with both modes"""

    driver = webdriver.Chrome()

    movie_data = []
    
    try:
        if movie_name:  # Single movie search mode
            search_query = movie_name.replace(" ", "+")
            search_url = f"https://www.imdb.com/find?q={search_query}"
            driver.get(search_url)
            time.sleep(2)

            # Get first movie result
            first_result = driver.find_element(By.CSS_SELECTOR, "a.ipc-metadata-list-summary-item__t")
            movie_url = first_result.get_attribute("href")
            
            if "/title/tt" not in movie_url:
                print("Movie page not found")
                return

            # Get basic info from search result
            title = first_result.text.strip()
            year_element = driver.find_element(By.CSS_SELECTOR, "div.ipc-metadata-list-summary-item__tc li")
            year = year_element.text.strip() if year_element else "N/A"

            # Get detailed info including rating and genre
            details = get_movie_details(movie_url)
            if not details:
                return

            movie_entry = {
                "Title": title,
                "Year": year,
                **details
            }

            movie_data.append(movie_entry)

        else:  # Top 250 mode
            driver.get("https://www.imdb.com/chart/top")
            
            # Scroll to load all movies
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            soup = BeautifulSoup(driver.page_source, "html.parser")
            movies = soup.select("li.ipc-metadata-list-summary-item")

            for movie in movies:
                try:
                    title = movie.select_one("h3.ipc-title__text").get_text(strip=True).split(". ", 1)[1]
                    metadata = movie.select("span.cli-title-metadata-item")
                    year = metadata[0].text if len(metadata) > 0 else "N/A"
                    rating = movie.select_one("span.ipc-rating-star--imdb").get_text(strip=True).split()[0]
                    movie_url = "https://www.imdb.com" + movie.select_one("a.ipc-title-link-wrapper")["href"]

                    # Get additional details
                    details = get_movie_details(movie_url)
                    if not details:
                        continue

                    # Preserve list rating but use detailed genre
                    movie_data.append({
                        "Title": title,
                        "Year": year,
                        "Rating": rating,
                        **{k: v for k, v in details.items() if k != "Rating"}
                    })

                    print(f"Scraped: {title}")

                except Exception as e:
                    print(f"Error processing movie: {str(e)}")
                    continue

        # Save to CSV
        try:
            existing_df = pd.read_csv("movies.csv")
        except (FileNotFoundError, pd.errors.EmptyDataError):
            existing_df = pd.DataFrame()

        if not movie_data:
            return

        new_df = pd.DataFrame(movie_data)
        combined_df = pd.concat([existing_df, new_df]).drop_duplicates(
            subset=["Title", "Year"], 
            keep="last"
        )
        
        combined_df.to_csv("movies.csv", index=False)
        print(f"Successfully updated database with {len(new_df)} new entries")

    finally:
        driver.quit()

# Usage:
# scraper()  # Scrape Top 250 with all details
scraper("The Avengers")  # Add specific movie with rating and genre