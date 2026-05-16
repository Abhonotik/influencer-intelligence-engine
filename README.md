# Influencer Intelligence & Discovery Engine

A Python-based Influencer Discovery and Audit Tool built using the YouTube Data API v3 and yt-dlp.

This system identifies creators based on niche keywords, extracts influencer metadata, audits recent uploads, and exports structured JSON/CSV reports.

---

# Features

## Creator Discovery
- Keyword-based creator search
- Regional filtering support
- Channel ID extraction

## Channel Audit
- Subscriber count extraction
- Total view count extraction
- Total video count extraction
- Recent upload verification

## Metadata Extraction
- Upload date extraction
- Date normalization (YYYY-MM-DD)
- yt-dlp fallback metadata extraction
- No media download required

## Operational Resilience
- Exception handling
- Fault-tolerant processing
- 2-second rate limiting
- Logging system

## Export System
- JSON export
- CSV export
- Structured audit records

---

# Tech Stack

- Python 3.7+
- YouTube Data API v3
- yt-dlp
- pandas
- python-dotenv

---

# Project Structure

```bash
influencer-engine/
│
├── discovery_engine.py
├── requirements.txt
├── sample_output.json
├── sample_output.csv
├── .env
│
├── logs/
│   └── engine.log
```

---

# Installation

## Clone or Download Project

```bash
git clone <repository-url>
```

OR download the ZIP file.

---

# Create Virtual Environment

## Windows

```bash
python -m venv venv
```

Activate environment:

```bash
venv\Scripts\activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

OR manually:

```bash
pip install google-api-python-client
pip install yt-dlp
pip install pandas
pip install python-dotenv
```

---

# YouTube API Setup

1. Open Google Cloud Console
2. Create a new project
3. Enable:
   - YouTube Data API v3
4. Create API Key

---

# Environment Variables

Create a `.env` file:

```env
YOUTUBE_API_KEY=YOUR_API_KEY
```

Example:

```env
YOUTUBE_API_KEY=AIzaSyXXXXXXXX
```

---

# Running The Project

```bash
python discovery_engine.py
```

---

# Output Files

## JSON Output

```text
sample_output.json
```

Contains structured influencer audit records.

---

## CSV Output

```text
sample_output.csv
```

Contains flattened influencer audit data.

---

# Logging

Logs are stored inside:

```text
logs/engine.log
```

Tracks:
- creator processing
- successful audits
- errors
- export events

---

# yt-dlp Fallback System

The system primarily uses the YouTube Data API.

If upload metadata becomes unavailable or restricted, the pipeline automatically uses yt-dlp fallback extraction without downloading media files.

---

# Rate Limiting

A mandatory 2-second delay is applied between creator processing requests to reduce API throttling and bot detection risks.

---

# Exception Handling

The system is fault tolerant:
- broken creators
- missing metadata
- API issues
- restricted metrics

will not crash the pipeline.

---

# Sample Data Collected

- Channel Name
- Channel ID
- Subscriber Count
- Total Views
- Total Videos
- Recent Upload Titles
- Upload Dates

---

# Future Improvements

- Pagination support
- Async processing
- Streamlit dashboard
- FastAPI integration
- Database integration
- Advanced analytics

---

# Author

Built as part of the Technical Assessment:
Influencer Intelligence & Discovery Engine