import os
import math
import argparse
from typing import List, Dict
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tabulate import tabulate
import isodate

# ---------- Config & bootstrap ----------
load_dotenv()
API_KEY = os.getenv("YT_API_KEY")

def get_youtube():
    if not API_KEY:
        raise RuntimeError("Missing YT_API_KEY in your .env file")
    return build("youtube", "v3", developerKey=API_KEY)

# ---------- Core logic ----------
def search_video_ids(youtube, query: str, max_results: int = 25, region_code: str = None, lang: str = None) -> List[str]:
    """
    Uses search.list to find video IDs for a query. We fetch IDs first (cheap),
    then call videos.list to get rich stats.
    """
    req = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=min(max_results, 50),  # API limit per page is 50
        order="relevance",                 # we'll re-rank by stats locally
        regionCode=region_code,
        relevanceLanguage=lang
    )
    resp = req.execute()
    return [item["id"]["videoId"] for item in resp.get("items", [])]

def get_video_details(youtube, ids: List[str]) -> List[Dict]:
    """
    Hydrates IDs with statistics + content details using videos.list
    """
    if not ids:
        return []
    req = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(ids)
    )
    resp = req.execute()
    videos = []
    for it in resp.get("items", []):
        stats = it.get("statistics", {})
        snip = it.get("snippet", {})
        content = it.get("contentDetails", {})
        duration_iso = content.get("duration")  # e.g., PT12M3S
        try:
            duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds()) if duration_iso else None
        except Exception:
            duration_seconds = None

        videos.append({
            "id": it.get("id"),
            "title": snip.get("title"),
            "channel": snip.get("channelTitle"),
            "publishedAt": snip.get("publishedAt"),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),  # may be 0 if disabled
            "duration_s": duration_seconds,
            "url": f"https://www.youtube.com/watch?v={it.get('id')}"
        })
    return videos

def rank_videos(videos: List[Dict], min_duration_s: int = 60) -> List[Dict]:
    """
    Simple ranking: filter very short videos (avoid Shorts noise), then sort by:
    1) views desc, 2) likes desc.
    You can swap this for a weighted score later.
    """
    filtered = [v for v in videos if (v["duration_s"] or 0) >= min_duration_s]
    # stable sort: likes desc then views desc
    filtered.sort(key=lambda v: v["likes"], reverse=True)
    filtered.sort(key=lambda v: v["views"], reverse=True)
    return filtered

def pretty_print(videos: List[Dict], top_n: int = 10):
    rows = []
    for v in videos[:top_n]:
        dur = f'{v["duration_s"]//60}m{v["duration_s"]%60}s' if v["duration_s"] else "?"
        rows.append([
            v["title"],
            v["channel"],
            v["views"],
            v["likes"],
            dur,
            v["url"]
        ])
    print(tabulate(rows, headers=["Title", "Channel", "Views", "Likes", "Duration", "Link"], tablefmt="github"))

# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(description="Find top YouTube videos for a topic.")
    parser.add_argument("topic", type=str, help="Search topic, e.g. 'dynamic programming knapsack'")
    parser.add_argument("--max", type=int, default=25, help="Max results to fetch (<=50)")
    parser.add_argument("--region", type=str, default=None, help="regionCode, e.g. US/IL/GB")
    parser.add_argument("--lang", type=str, default=None, help="relevanceLanguage, e.g. en/he")
    parser.add_argument("--min-duration", type=int, default=60, help="Min duration in seconds (filters out very short videos)")
    parser.add_argument("--top", type=int, default=10, help="How many to display")
    args = parser.parse_args()

    try:
        yt = get_youtube()
        ids = search_video_ids(yt, args.topic, max_results=args.max, region_code=args.region, lang=args.lang)
        details = get_video_details(yt, ids)
        ranked = rank_videos(details, min_duration_s=args.min_duration)
        pretty_print(ranked, top_n=args.top)
    except HttpError as e:
        print("YouTube API error:", e)
    except Exception as e:
        print("Unexpected error:", e)

if __name__ == "__main__":
    main()
