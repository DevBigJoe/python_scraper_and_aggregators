import tkinter as tk
from tkinter import ttk
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import webbrowser
import threading
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

class NewsSearcher:
    def __init__(self, root):
        self.root = root
        root.title("Scrapygator")
        root.geometry("1150x750")

        main_frame = tk.Frame(root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title label
        tk.Label(main_frame, text="Scrapygator", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(main_frame, text="Keywords (; separated, + for combination)").pack(anchor="w")

        # Keyword input
        self.keyword_entry = ttk.Entry(main_frame)
        self.keyword_entry.pack(fill="x", pady=5)

        # Time filter
        option_frame = tk.Frame(main_frame)
        option_frame.pack(anchor="w", pady=10)
        tk.Label(option_frame, text="Maximum Age").pack(side="left")

        self.age_var = tk.StringVar()
        self.age_dropdown = ttk.Combobox(option_frame, textvariable=self.age_var, state="readonly",
                                         values=["Now (~10min)","1 Hour","2 Hours","3 Hours","5 Hours",
                                                 "12 Hours","24 Hours","3 Days","7 Days"])
        self.age_dropdown.current(5)
        self.age_dropdown.pack(side="left", padx=10)

        # News sources
        engine_frame = tk.LabelFrame(main_frame, text="News Sources")
        engine_frame.pack(fill="x", pady=10)

        self.engines = {
            "Google": tk.BooleanVar(value=True),
            "Bing": tk.BooleanVar(value=True),
            "BBC": tk.BooleanVar(),
            "Reuters": tk.BooleanVar(),
            "NYTimes": tk.BooleanVar(),
            "The Guardian": tk.BooleanVar(),
            "Al Jazeera": tk.BooleanVar(),
            "CNN": tk.BooleanVar(),
            "AP News": tk.BooleanVar(),
            "Financial Times": tk.BooleanVar(),
            "Le Monde": tk.BooleanVar(),
            "Der Spiegel": tk.BooleanVar(),
            "El País": tk.BooleanVar(),
            "The Washington Post": tk.BooleanVar()
        }

        for name, var in self.engines.items():
            ttk.Checkbutton(engine_frame, text=name, variable=var).pack(side="left", padx=5)

        # Start search button
        ttk.Button(main_frame, text="Start Search", command=self.start_search_thread).pack(anchor="w", pady=10)

        # Global progress bar
        self.progress = ttk.Progressbar(main_frame, length=500)
        self.progress.pack(anchor="w")

        # Results table
        columns = ("Time", "Source", "Title")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Source", text="Source")
        self.tree.heading("Title", text="Title")
        self.tree.column("Time", width=160)
        self.tree.column("Source", width=180)
        self.tree.column("Title", width=740)
        self.tree.pack(fill="both", expand=True, pady=10)
        self.tree.bind("<Double-1>", self.open_link)
        self.links = []

    # Get maximum age filter in timedelta
    def get_age_limit(self):
        mapping = {
            "Now (~10min)": timedelta(minutes=10),
            "1 Hour": timedelta(hours=1),
            "2 Hours": timedelta(hours=2),
            "3 Hours": timedelta(hours=3),
            "5 Hours": timedelta(hours=5),
            "12 Hours": timedelta(hours=12),
            "24 Hours": timedelta(hours=24),
            "3 Days": timedelta(days=3),
            "7 Days": timedelta(days=7)
        }
        return mapping.get(self.age_var.get(), timedelta(days=1))

    # Check if title matches keywords
    def keyword_match(self, title, keywords):
        title = title.lower()
        for kw in keywords:
            if "+" in kw:
                if all(p in title for p in kw.split("+")):
                    return True
            else:
                if kw in title:
                    return True
        return False

    # Return RSS feed URLs for selected sources
    def get_sources(self, keyword):
        q = urllib.parse.quote(keyword)
        sources = []
        if self.engines["Google"].get():
            sources.append(f"https://news.google.com/rss/search?q={q}")
        if self.engines["Bing"].get():
            sources.append(f"https://www.bing.com/news/search?q={q}&format=rss")
        if self.engines["BBC"].get():
            sources.append("http://feeds.bbci.co.uk/news/world/rss.xml")
        if self.engines["Reuters"].get():
            sources.append("http://feeds.reuters.com/reuters/worldNews")
        if self.engines["NYTimes"].get():
            sources.append("https://rss.nytimes.com/services/xml/rss/nyt/World.xml")
        if self.engines["The Guardian"].get():
            sources.append("https://www.theguardian.com/world/rss")
        if self.engines["Al Jazeera"].get():
            sources.append("https://www.aljazeera.com/xml/rss/all.xml")
        if self.engines["CNN"].get():
            sources.append("http://rss.cnn.com/rss/edition_world.rss")
        if self.engines["AP News"].get():
            sources.append("https://apnews.com/rss/apf-intlnews")
        if self.engines["Financial Times"].get():
            sources.append("https://www.ft.com/?format=rss")
        if self.engines["Le Monde"].get():
            sources.append("https://www.lemonde.fr/rss/une.xml")
        if self.engines["Der Spiegel"].get():
            sources.append("https://www.spiegel.de/international/index.rss")
        if self.engines["El País"].get():
            sources.append("https://elpais.com/rss/elpais/internacional.xml")
        if self.engines["The Washington Post"].get():
            sources.append("http://feeds.washingtonpost.com/rss/world")
        return sources

    # Parse RSS feed and return list of (title, link, pubdate)
    def parse_rss(self, url):
        results = []
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as response:
                xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall(".//item"):
                title = item.findtext("title")
                link = item.findtext("link")
                pub = item.find("pubDate")
                pubdate = None
                if pub is not None:
                    try:
                        pubdate = parsedate_to_datetime(pub.text).replace(tzinfo=None)
                    except:
                        pubdate = None
                results.append((title, link, pubdate))
        except:
            pass
        return results

    # Start search in a separate thread
    def start_search_thread(self):
        thread = threading.Thread(target=self.search)
        thread.daemon = True
        thread.start()

    # Main search logic
    def search(self):
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.links.clear()

        keywords = [k.strip().lower() for k in self.keyword_entry.get().split(";") if k.strip()]

        sources = []
        for k in keywords:
            sources.extend(self.get_sources(k))

        self.progress["maximum"] = len(sources)
        self.progress["value"] = 0

        age_limit = self.get_age_limit()
        now = datetime.utcnow()

        all_results = []
        seen = set()
        threads = []

        # Fetch feeds in parallel
        for url in sources:
            t = threading.Thread(
                target=self.fetch_source,
                args=(url, all_results, seen, keywords, age_limit, now)
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Sort by publication date descending
        all_results.sort(key=lambda x: x[2] if x[2] else datetime.min, reverse=True)

        # Insert results into treeview
        for title, link, pubdate in all_results:
            source = urlparse(link).netloc.replace("www.", "")
            time_str = pubdate.strftime("%Y-%m-%d %H:%M") if pubdate else "?"
            self.tree.insert("", "end", values=(time_str, source, title))
            self.links.append(link)

    # Fetch and filter one RSS feed
    def fetch_source(self, url, all_results, seen, keywords, age_limit, now):
        results = self.parse_rss(url)
        for title, link, pubdate in results:
            if link in seen:
                continue
            if not self.keyword_match(title.lower(), keywords):
                continue
            if pubdate and now - pubdate > age_limit:
                continue
            seen.add(link)
            all_results.append((title, link, pubdate))
        self.progress["value"] += 1
        self.root.update_idletasks()

    # Open selected article in default browser
    def open_link(self, event):
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            webbrowser.open(self.links[index])

if __name__ == "__main__":
    root = tk.Tk()
    app = NewsSearcher(root)
    root.mainloop()