# 🎬 YouTube Finder Bot

A Python tool that helps students (and anyone learning) find YouTube videos on a specific topic.  
It ranks results by **views** and **likes**, filters out very short videos (like Shorts), and prints a clean table with clickable links.

---

## 🚀 Features
- Search YouTube videos using **YouTube Data API v3**
- Collect statistics: views, likes, duration, channel
- Rank videos by popularity (views + likes)
- Filter out very short videos (avoid Shorts noise)
- Display results in a **pretty table** in your terminal
- Configurable options: region, language, max results, min duration

---

## 📦 Installation

1. Clone this repo:
   ```bash
   git clone https://github.com/AlonB22/youtube-finder-bot.git
   cd youtube-finder-bot

## ▶️ Usage

Run a search for "dynamic programming knapsack":

```bash
python app.py "dynamic programming knapsack" --region US --lang en --top 5

| Title                         | Channel       |   Views |   Likes | Duration | Link                                   |
|-------------------------------|---------------|---------|---------|----------|----------------------------------------|
| Knapsack Problem Explained    | CS Simplified | 1234567 |   54321 | 12m3s    | https://www.youtube.com/watch?v=XXXXX  |


---

## 📦 Requirements

```bash
- Python 3.10+
- google-api-python-client
- python-dotenv
- tabulate
- isodate

## 👨‍💻 Author

```bash
Created by **Alon Berla** — Computer Science student passionate about software & AI.  
Connect with me on [LinkedIn](https://www.linkedin.com/in/alon-berla/) ✨
