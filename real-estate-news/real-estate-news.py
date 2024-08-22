# Import necessary libraries
import feedparser
import gradio as gr
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import pytz
from dateutil import parser as date_parser

# Define the Real Estate RSS feed URLs and their categories
rss_feeds = {
    "Zillow": {
        "Zillow Real Estate Market Report": "https://www.zillow.com/blog/feed/",
        "Zillow Research": "https://www.zillow.com/research/feed/"
    },
    "Realtor.com": {
        "Realtor.com News": "https://www.realtor.com/news/feed/"
    },
    "Curbed": {
        "Curbed National": "https://www.curbed.com/rss/index.xml"
    },
    "Redfin": {
        "Redfin Real Estate News": "https://www.redfin.com/blog/feed/"
    },
    "HousingWire": {
        "HousingWire News": "https://www.housingwire.com/rss"
    },
    "NAR": {
        "NAR News": "https://www.nar.realtor/newsroom/rss.xml",
        "NAR Research and Statistics": "https://www.nar.realtor/research-and-statistics/rss.xml"
    },
    "Inman": {
        "Inman News": "https://www.inman.com/feed/",
        "Inman Marketing": "https://www.inman.com/category/marketing/feed/",
        "Inman Technology": "https://www.inman.com/category/technology/feed/"
    },
    "The Real Deal": {
        "The Real Deal National": "https://therealdeal.com/national/feed/",
        "The Real Deal New York": "https://therealdeal.com/new-york/feed/",
        "The Real Deal Los Angeles": "https://therealdeal.com/la/feed/",
        "The Real Deal Chicago": "https://therealdeal.com/chicago/feed/",
        "The Real Deal South Florida": "https://therealdeal.com/miami/feed/"
    },
    "Mashvisor": {
        "Mashvisor Real Estate News": "https://www.mashvisor.com/blog/feed/"
    },
    "PropertyWire": {
        "PropertyWire News": "https://www.propertywire.com/feed/"
    },
    "Investopedia": {
        "Investopedia Real Estate": "https://www.investopedia.com/real-estate-4427761/feed/"
    },
    "RISMedia": {
        "RISMedia News": "https://rismedia.com/feed/"
    },
    "Commercial Observer": {
        "Commercial Observer Real Estate News": "https://commercialobserver.com/category/real-estate/feed/"
    },
    "GlobeSt": {
        "GlobeSt.com News": "https://www.globest.com/rss/"
    },
    "Mortgage News Daily": {
        "Mortgage News Daily": "https://www.mortgagenewsdaily.com/rss/"
    },
    "Apartment Therapy": {
        "Apartment Therapy Real Estate": "https://www.apartmenttherapy.com/feeds/real-estate.xml"
    },
    "CNBC": {
        "CNBC Real Estate": "https://www.cnbc.com/id/10000115/device/rss/rss.html"
    },
    "Forbes": {
        "Forbes Real Estate": "https://www.forbes.com/real-estate/feed/"
    },
    "Business Insider": {
        "Business Insider Real Estate": "https://www.businessinsider.com/sai/rss"
    }
}

# Set User-Agent to mimic an iPhone
user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"

# Function to parse a single RSS feed and return the latest headlines
def parse_feed(url, title):
    headers = {'User-Agent': user_agent}
    feed = feedparser.parse(url, request_headers=headers)
    print(f"Parsing feed: {title} ({url})")
    return feed.entries

# Function to convert published date to EST and format it
def format_date_to_est(entry):
    if 'published' in entry:
        dt = date_parser.parse(entry.published)
        est = pytz.timezone('America/New_York')
        dt_est = dt.astimezone(est)
        return dt_est.strftime('%Y-%m-%d %H:%M:%S %Z')
    else:
        return 'Date not available'

# Function to get the latest headlines for a publisher
def get_headlines_for_publisher(publisher_feeds, publisher_name):
    all_entries = []
    seen_entries = set()
    for category, url in publisher_feeds.items():
        try:
            entries = parse_feed(url, category)
            time.sleep(2)  # Add a 2-second delay between requests
            if entries:
                for entry in entries:
                    if 'title' in entry and 'link' in entry and (entry.title, entry.link) not in seen_entries:
                        seen_entries.add((entry.title, entry.link))
                        all_entries.append((category, entry, publisher_name))
                print(f"Successfully parsed {len(entries)} entries from feed: {category} ({url})")
            else:
                print(f"No entries found in feed: {category} ({url})")
        except Exception as e:
            print(f"Error parsing feed {category} ({url}): {e}")
    return all_entries

# Function to get the latest headlines for all categories
def get_latest_headlines():
    all_entries = []
    headlines = defaultdict(list)
    with ThreadPoolExecutor(max_workers=len(rss_feeds)) as executor:
        future_to_publisher = {
            executor.submit(get_headlines_for_publisher, rss_feeds[publisher], publisher): publisher 
            for publisher in rss_feeds
        }
        for future in as_completed(future_to_publisher):
            publisher = future_to_publisher[future]
            try:
                publisher_entries = future.result()
                for category, entry, publisher_name in publisher_entries:
                    headlines[category].append((entry, publisher_name))
                    headlines[publisher].append((entry, publisher_name))
                    all_entries.append((category, entry, publisher_name))
            except Exception as e:
                print(f"Error processing feeds for {publisher}: {e}")

    # Sort all entries by published date
    sorted_all_entries_date = sorted(all_entries, key=lambda x: date_parser.parse(x[1].published) if 'published' in x[1] else datetime.min, reverse=True)
    headlines["All by Date"] = [(entry[1], entry[2]) for entry in sorted_all_entries_date if 'published' in entry[1]]

    return headlines

# Function to format the headlines for display
def format_headlines(headlines):
    formatted_headlines = defaultdict(str)
    for category, entries in headlines.items():
        if entries:
            sorted_entries = sorted(entries, key=lambda x: date_parser.parse(x[0].published) if 'published' in x[0] else datetime.min, reverse=True)
            for entry, publisher_name in sorted_entries:
                published_date = format_date_to_est(entry)
                entry_info = f"<p><strong>{entry.title}</strong><br><a href='{entry.link}'>Check it out on {publisher_name}</a><br>Published: {published_date}</p>"
                formatted_headlines[category] += entry_info
    return formatted_headlines

# Function to create Gradio interface with tabs for each category and each feed
def create_interface():
    headlines = get_latest_headlines()
    formatted_headlines = format_headlines(headlines)
    
    with gr.Blocks() as iface:
        tabs = gr.Tabs()
        with tabs:
            # Add individual tabs for each feed
            for publisher, feeds in rss_feeds.items():
                if len(feeds) > 1 and headlines[publisher]:  # Only add publisher tab if more than one feed
                    with gr.TabItem(publisher):
                        gr.HTML(value=formatted_headlines[publisher])
                for feed_name in feeds.keys():
                    if headlines[feed_name]:  # Only add tabs with content
                        with gr.TabItem(feed_name):
                            gr.HTML(value=formatted_headlines[feed_name])
            
            # Add the "All by Date" tab
            if headlines["All by Date"]:
                with gr.TabItem("All by Date"):
                    gr.HTML(value=formatted_headlines["All by Date"])

    return iface

# Create the Gradio interface
iface = create_interface()

# Launch the Gradio interface
iface.launch(share=True, debug=True)
