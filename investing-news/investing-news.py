# Import necessary libraries
import feedparser
import gradio as gr
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import pytz
from dateutil import parser as date_parser

rss_feeds = {
    "MarketWatch": {
        "MarketWatch Top Stories": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "MarketWatch Real-Time Headlines": "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines",
        "MarketWatch Bulletins": "http://feeds.marketwatch.com/marketwatch/bulletins",
        "MarketWatch Market Pulse": "https://feeds.content.dowjones.io/public/rss/mw_marketpulse",
        "MarketWatch Investing": "https://feeds.marketwatch.com/marketwatch/investing",
        "MarketWatch Mutual Funds": "https://feeds.marketwatch.com/marketwatch/mutualfunds",
        "MarketWatch ETFs": "https://feeds.marketwatch.com/marketwatch/etfs",
        "MarketWatch Retirement": "https://feeds.marketwatch.com/marketwatch/retirement"
    },
    "Nasdaq": {
        "Nasdaq Original": "https://www.nasdaq.com/feed/nasdaq-original/rss.xml",
        "Nasdaq Commodities": "https://www.nasdaq.com/feed/rssoutbound?category=Commodities",
        "Nasdaq Cryptocurrencies": "https://www.nasdaq.com/feed/rssoutbound?category=Cryptocurrencies",
        "Nasdaq Dividends": "https://www.nasdaq.com/feed/rssoutbound?category=Dividends",
        "Nasdaq Earnings": "https://www.nasdaq.com/feed/rssoutbound?category=Earnings",
        "Nasdaq ETFs": "https://www.nasdaq.com/feed/rssoutbound?category=ETFs",
        "Nasdaq IPOs": "https://www.nasdaq.com/feed/rssoutbound?category=IPOs",
        "Nasdaq Markets": "https://www.nasdaq.com/feed/rssoutbound?category=Markets",
        "Nasdaq Options": "https://www.nasdaq.com/feed/rssoutbound?category=Options",
        "Nasdaq Stocks": "https://www.nasdaq.com/feed/rssoutbound?category=Stocks"
    },
    "CNBC": {
        "Top News (CNBC)": "https://www.cnbc.com/id/100003114/device/rss",
        "World News (CNBC)": "https://www.cnbc.com/id/100727362/device/rss",
        "Business News (CNBC)": "https://www.cnbc.com/id/10001147/device/rss",
        "Earnings (CNBC)": "https://www.cnbc.com/id/15839135/device/rss",
        "Investing (CNBC)": "https://www.cnbc.com/id/15839069/device/rss",
        "Economy (CNBC)": "https://www.cnbc.com/id/20910258/device/rss",
        "Finance (CNBC)": "https://www.cnbc.com/id/15839263/device/rss",
        "Health Care (CNBC)": "https://www.cnbc.com/id/10000108/device/rss",
        "Real Estate (CNBC)": "https://www.cnbc.com/id/10000115/device/rss",
        "Technology (CNBC)": "https://www.cnbc.com/id/10001045/device/rss",
        "Small Business (CNBC)": "https://www.cnbc.com/id/10000113/device/rss",
        "Personal Finance (CNBC)": "https://www.cnbc.com/id/10000520/device/rss",
        "Latest Videos (CNBC)": "https://www.cnbc.com/id/10000664/device/rss",
        "Top Video (CNBC)": "https://www.cnbc.com/id/25490312/device/rss",
        "Breaking News (CNBC)": "https://www.cnbc.com/id/15839135/device/rss",
        "Commentary (CNBC)": "https://www.cnbc.com/id/100370673/device/rss",
        "Technology Blog (CNBC)": "https://www.cnbc.com/id/16315768/device/rss",
        "Latest Market News (CNBC)": "https://www.cnbc.com/id/20910256/device/rss",
        "Mutual Funds (CNBC)": "https://www.cnbc.com/id/100375113/device/rss",
        "Forex (CNBC)": "https://www.cnbc.com/id/15840232/device/rss",
        "Bonds (CNBC)": "https://www.cnbc.com/id/15839755/device/rss",
        "US News (CNBC)": "https://www.cnbc.com/id/15837362/device/rss",
        "Asia News (CNBC)": "https://www.cnbc.com/id/19832390/device/rss",
        "Europe News (CNBC)": "https://www.cnbc.com/id/19794221/device/rss",
        "Financial Advisors (CNBC)": "https://www.cnbc.com/id/100646059/device/rss",
        "Travel (CNBC)": "https://www.cnbc.com/id/10000739/device/rss",
        "Politics (CNBC)": "https://www.cnbc.com/id/10000113/device/rss",
        "Wealth (CNBC)": "https://www.cnbc.com/id/10001478/device/rss",
        "Sports Business (CNBC)": "https://www.cnbc.com/id/10000108/device/rss",
        "Financial Wellness (CNBC)": "https://www.cnbc.com/id/100437540/device/rss",
        "Pro (CNBC)": "https://www.cnbc.com/id/100546132/device/rss",
        "Reimagining Business (CNBC)": "https://www.cnbc.com/id/106512258/device/rss",
        "Investing in Space (CNBC)": "https://www.cnbc.com/id/106010965/device/rss",
        "ETF Edge (CNBC)": "https://www.cnbc.com/id/106010964/device/rss",
        "Sustainable Energy (CNBC)": "https://www.cnbc.com/id/106010963/device/rss",
        "Disruptor 50 (CNBC)": "https://www.cnbc.com/id/100024999/device/rss",
        "Stock Market Data (CNBC)": "https://www.cnbc.com/id/15839069/device/rss",
        "Squawk Box (CNBC)": "https://www.cnbc.com/id/15838368/device/rss",
        "Squawk on the Street (CNBC)": "https://www.cnbc.com/id/15839060/device/rss",
        "Squawk Alley (CNBC)": "https://www.cnbc.com/id/10000108/device/rss",
        "Squawk Box Europe (CNBC)": "https://www.cnbc.com/id/19854918/device/rss",
        "Squawk Box Asia (CNBC)": "https://www.cnbc.com/id/19832390/device/rss"
    },
    "Bloomberg": {
        "Bloomberg Markets": "https://feeds.bloomberg.com/markets/news.rss",
        "Bloomberg Politics": "https://feeds.bloomberg.com/politics/news.rss",
        "Bloomberg Technology": "https://feeds.bloomberg.com/technology/news.rss",
        "Bloomberg Wealth": "https://feeds.bloomberg.com/wealth/news.rss",
        "Bloomberg Economics": "https://feeds.bloomberg.com/economics/news.rss",
        "Bloomberg Industries": "https://feeds.bloomberg.com/industries/news.rss",
        "Bloomberg Green": "https://feeds.bloomberg.com/green/news.rss",
        "Bloomberg Personal Finance": "https://www.bloomberg.com/feeds/personal-finance-news.rss",
        "Bloomberg Mutual Funds": "https://www.bloomberg.com/feeds/mutual-funds-news.rss",
        "Bloomberg Hedge Funds": "https://www.bloomberg.com/feeds/hedge-funds-news.rss"
    },
    "Seeking Alpha": {
        "Seeking Alpha Top News": "https://seekingalpha.com/feed.xml",
        "Seeking Alpha Market News": "https://seekingalpha.com/market-news/feed",
        "Seeking Alpha Investing Ideas": "https://seekingalpha.com/author/marketplace/feed",
        "Seeking Alpha Earnings": "https://seekingalpha.com/earnings/feed"
    },
    "The Motley Fool": {
        "Motley Fool Top Stories": "https://www.fool.com/feeds/index.aspx",
        "Motley Fool Stock Market": "https://www.fool.com/investing-news/feed.aspx",
        "Motley Fool Personal Finance": "https://www.fool.com/personal-finance-news/feed.aspx"
    },
    "Yahoo Finance": {
        "Yahoo Finance Top News": "https://finance.yahoo.com/news/rss",
        "Yahoo Finance Market News": "https://finance.yahoo.com/markets/rss",
        "Yahoo Finance Personal Finance": "https://finance.yahoo.com/personal-finance/rss",
        "Yahoo Finance Investments": "https://finance.yahoo.com/investing/rss"
    },
    "Charles Schwab": {
        "Schwab Insights & Ideas": "https://www.schwab.com/rss.xml"
    },
    "Fidelity": {
        "Fidelity Viewpoints": "https://www.fidelity.com/viewpoints.xml"
    },
    "Morgan Stanley": {
        "Morgan Stanley Insights": "https://www.morganstanley.com/feeds/rss/news.xml"
    },
    "BlackRock": {
        "BlackRock Blog": "https://www.blackrockblog.com/feed/"
    },
    "Vanguard": {
        "Vanguard News": "https://personal.vanguard.com/us/insights/rss"
    },
    "J.P. Morgan": {
        "J.P. Morgan Private Bank Insights": "https://privatebank.jpmorgan.com/gl/en/insights/feed.xml"
    },
    "Goldman Sachs": {
        "Goldman Sachs Insights": "https://www.goldmansachs.com/insights/rss/"
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
