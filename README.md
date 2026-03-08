# Scrapygator

This Python program creates a GUI application to **search worldwide news articles** using RSS feeds from multiple international news sources. Users can enter keywords or word combinations, select sources, apply a time filter, and view results sorted by publication date.  

---

## Features

- **Keyword Input:**  
  Enter multiple keywords separated by `;`. Use `+` to indicate that all words must appear in the title.
- **Time Filter:**  
  Select maximum article age (e.g., 1 hour, 24 hours, 7 days). Only articles published within the selected time are shown.
- **Selectable News Sources:**  
  Choose from Google, Bing, BBC, Reuters, NYTimes, The Guardian, Al Jazeera, CNN, AP News, Financial Times, Le Monde, Der Spiegel, El País, and The Washington Post.
- **Global Progress Bar:**  
  Displays overall progress of fetching feeds.
- **Result Table:**  
  Shows article publication time, source domain, and title. Double-click opens the article in the default web browser.
- **Multithreading:**  
  Fetches multiple RSS feeds in parallel for faster results.
- **Duplicate Removal:**  
  Same links appear only once, even if multiple feeds contain the same article.

---

## Key Functions

### `get_age_limit()`
Returns a `timedelta` object corresponding to the selected maximum article age.

### `keyword_match(title, keywords)`
Checks if a news title matches the entered keywords. Supports:
- `;` for separate keywords (OR logic)
- `+` for word combination (all words must exist in title)

### `get_sources(keyword)`
Returns a list of RSS feed URLs for selected news sources, URL-encoded with the keyword.

### `parse_rss(url)`
Fetches and parses a single RSS feed. Returns a list of tuples: `(title, link, pubdate)`.

### `start_search_thread()`
Starts the main search process in a separate thread to keep the GUI responsive.

### `search()`
- Clears previous results.
- Gathers all RSS feeds for entered keywords.
- Starts parallel threads to fetch articles.
- Filters by keyword and maximum age.
- Sorts results by publication date descending.
- Populates the results table.

### `fetch_source(url, all_results, seen, keywords, age_limit, now)`
Fetches one RSS feed, filters results, and appends them to the shared results list.

### `open_link(event)`
Opens the selected article in the default web browser when a row in the table is double-clicked.

---

## Usage

1. Enter keywords separated by `;`.  
   - Use `+` for mandatory word combinations.
2. Select the desired maximum article age from the dropdown.
3. Check the news sources you want to search.
4. Click **"Start Search"**.
5. Wait for the progress bar to complete.
6. Browse the results table and double-click to open articles in the browser.

---

This structure allows you to **quickly monitor global news** for specific keywords, with optional combination searches and time filtering, all within a **modern, simple Tkinter GUI**.
