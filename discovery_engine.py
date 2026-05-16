import os
import json
import time
import logging
import yt_dlp
import pandas as pd

from dotenv import load_dotenv
from googleapiclient.discovery import build

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

# =========================================================
# CREATE REQUIRED FOLDERS
# =========================================================

os.makedirs("logs", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# =========================================================
# LOGGING CONFIGURATION
# =========================================================

logging.basicConfig(
    filename="logs/engine.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =========================================================
# REGION CODE MAPPING
# =========================================================

REGION_CODES = {

    "india": "IN",
    "usa": "US",
    "united states": "US",
    "canada": "CA",
    "russia": "RU",
    "uk": "GB",
    "united kingdom": "GB",
    "australia": "AU",
    "germany": "DE",
    "france": "FR",
    "japan": "JP",
    "china": "CN",
    "south korea": "KR",
    "brazil": "BR",
    "italy": "IT",
    "spain": "ES",
    "mexico": "MX",
    "uae": "AE",
    "singapore": "SG"

}

VALID_REGION_CODES = set(REGION_CODES.values())

# =========================================================
# API KEY VALIDATION
# =========================================================

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:

    raise ValueError(
        "YOUTUBE_API_KEY not found in .env file"
    )

# =========================================================
# BUILD YOUTUBE CLIENT
# =========================================================

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

# =========================================================
# USER INPUTS
# =========================================================

print("\n========== Influencer Discovery Engine ==========\n")

# =========================================================
# KEYWORD INPUT VALIDATION
# =========================================================

search_keyword = input(
    "Enter niche keyword (Example: Tech, Finance): "
).strip()

if not search_keyword:

    raise ValueError(
        "Keyword cannot be empty."
    )

# =========================================================
# REGION INPUT VALIDATION
# =========================================================

region_input = input(
    "Enter country or region code: "
).strip().lower()

region = REGION_CODES.get(
    region_input,
    region_input.upper()
)

if region not in VALID_REGION_CODES:

    raise ValueError(
        f"Invalid region: {region_input}. "
        f"Use supported countries like "
        f"India, USA, Canada, France, Russia, etc."
    )

# =========================================================
# CREATOR COUNT VALIDATION
# =========================================================

creator_input = input(
    "Enter number of creators to audit: "
).strip()

if not creator_input.isdigit():

    raise ValueError(
        "Creator count must be a positive number."
    )

creator_limit = int(creator_input)

if creator_limit <= 0:

    raise ValueError(
        "Creator count must be greater than 0."
    )

if creator_limit > 50:

    raise ValueError(
        "Maximum allowed creators is 50."
    )

print("\nStarting influencer audit pipeline...\n")

logging.info(
    f"Pipeline started | "
    f"Keyword: {search_keyword} | "
    f"Region: {region} | "
    f"Limit: {creator_limit}"
)

# =========================================================
# FINAL RESULTS STORAGE
# =========================================================

final_results = []

# =========================================================
# SEARCH CHANNELS
# =========================================================

try:

    search_request = youtube.search().list(
        q=search_keyword,
        type="channel",
        regionCode=region,
        maxResults=creator_limit,
        part="snippet"
    )

    search_response = search_request.execute()

except Exception as search_error:

    logging.error(
        f"Search API failed: {search_error}"
    )

    raise RuntimeError(
        f"Failed to search creators: {search_error}"
    )

# =========================================================
# LOOP THROUGH CHANNELS
# =========================================================

for item in search_response["items"]:

    channel_name = item["snippet"]["title"]
    channel_id = item["snippet"]["channelId"]

    print(f"\nProcessing: {channel_name}")

    logging.info(
        f"Processing creator: {channel_name}"
    )

    try:

        # =====================================================
        # CHANNEL STATISTICS
        # =====================================================

        stats_request = youtube.channels().list(
            part="statistics",
            id=channel_id
        )

        stats_response = stats_request.execute()

        stats = stats_response["items"][0]["statistics"]

        subscribers = stats.get(
            "subscriberCount",
            "Metric restricted"
        )

        total_views = stats.get(
            "viewCount",
            "Metric restricted"
        )

        total_videos = stats.get(
            "videoCount",
            "Metric restricted"
        )

        print("Subscribers:", subscribers)
        print("Total Views:", total_views)
        print("Total Videos:", total_videos)

        # =====================================================
        # RECENT UPLOAD STORAGE
        # =====================================================

        recent_uploads = []

        print("\nRecent Uploads:")

        # =====================================================
        # FETCH RECENT VIDEOS
        # =====================================================

        video_request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=5,
            order="date",
            type="video"
        )

        video_response = video_request.execute()

        # =====================================================
        # PROCESS VIDEOS
        # =====================================================

        for video in video_response["items"]:

            title = video["snippet"].get(
                "title",
                "Title not found"
            )

            video_id = video["id"]["videoId"]

            video_url = (
                f"https://www.youtube.com/watch?v={video_id}"
            )

            # =================================================
            # PRIMARY DATE EXTRACTION
            # =================================================

            raw_date = video["snippet"].get(
                "publishedAt"
            )

            if raw_date:

                upload_date = raw_date[:10]

            # =================================================
            # yt-dlp FALLBACK EXTRACTION
            # =================================================

            else:

                try:

                    logging.warning(
                        f"API date missing. "
                        f"Using yt-dlp fallback for "
                        f"{video_url}"
                    )

                    ydl_opts = {

                        "quiet": True,
                        "skip_download": True

                    }

                    with yt_dlp.YoutubeDL(
                        ydl_opts
                    ) as ydl:

                        info = ydl.extract_info(
                            video_url,
                            download=False
                        )

                        fallback_date = info.get(
                            "upload_date",
                            None
                        )

                        if fallback_date:

                            upload_date = (
                                f"{fallback_date[:4]}-"
                                f"{fallback_date[4:6]}-"
                                f"{fallback_date[6:]}"
                            )

                        else:

                            upload_date = (
                                "Date not found"
                            )

                except Exception as fallback_error:

                    logging.error(
                        f"yt-dlp fallback failed: "
                        f"{fallback_error}"
                    )

                    upload_date = "Date not found"

            # =================================================
            # DISPLAY VIDEO DETAILS
            # =================================================

            print(f"- {title}")
            print(f"  Upload Date: {upload_date}")

            # =================================================
            # STORE VIDEO DATA
            # =================================================

            recent_uploads.append({

                "title": title,
                "upload_date": upload_date

            })

        # =====================================================
        # STORE CREATOR DATA
        # =====================================================

        creator_data = {

            "channel_name": channel_name,
            "channel_id": channel_id,
            "subscribers": subscribers,
            "total_views": total_views,
            "total_videos": total_videos,
            "recent_uploads": recent_uploads

        }

        final_results.append(
            creator_data
        )

        logging.info(
            f"Successfully processed: "
            f"{channel_name}"
        )

        print("-" * 60)

    # =========================================================
    # CHANNEL PROCESSING ERROR HANDLING
    # =========================================================

    except Exception as e:

        print(
            f"Error processing "
            f"{channel_name}: {e}"
        )

        logging.error(
            f"Error processing "
            f"{channel_name}: {e}"
        )

        final_results.append({

            "channel_name": channel_name,
            "channel_id": channel_id,
            "error": str(e)

        })

        print("-" * 60)

    # =========================================================
    # RATE LIMITING
    # =========================================================

    time.sleep(2)

# =========================================================
# EXPORT JSON
# =========================================================

json_output_path = (
    "outputs/sample_output.json"
)

with open(
    json_output_path,
    "w",
    encoding="utf-8"
) as json_file:

    json.dump(
        final_results,
        json_file,
        indent=4,
        ensure_ascii=False
    )

print("\nJSON export completed!")

logging.info(
    "JSON export completed"
)

# =========================================================
# CREATE FLAT CSV ROWS
# =========================================================

flat_rows = []

for creator in final_results:

    if "recent_uploads" not in creator:
        continue

    uploads = creator["recent_uploads"]

    for upload in uploads:

        flat_rows.append({

            "channel_name": creator["channel_name"],
            "channel_id": creator["channel_id"],
            "subscribers": creator["subscribers"],
            "total_views": creator["total_views"],
            "total_videos": creator["total_videos"],

            "video_title": upload["title"],
            "upload_date": upload["upload_date"]

        })

# =========================================================
# CREATE DATAFRAME
# =========================================================

df = pd.DataFrame(flat_rows)

# =========================================================
# EXPORT CSV
# =========================================================

csv_output_path = (
    "outputs/sample_output.csv"
)

df.to_csv(
    csv_output_path,
    index=False
)

print("CSV export completed!")

logging.info(
    "CSV export completed"
)

# =========================================================
# SUMMARY STATISTICS
# =========================================================

successful_creators = len(
    [x for x in final_results if "error" not in x]
)

failed_creators = len(
    [x for x in final_results if "error" in x]
)

print("\n========== Pipeline Summary ==========")

print(
    f"Successful creators: "
    f"{successful_creators}"
)

print(
    f"Failed creators: "
    f"{failed_creators}"
)

print(
    f"JSON Output: "
    f"{json_output_path}"
)

print(
    f"CSV Output: "
    f"{csv_output_path}"
)

print(
    "\nInfluencer audit pipeline "
    "completed successfully!"
)

logging.info(
    f"Pipeline completed | "
    f"Successful: {successful_creators} | "
    f"Failed: {failed_creators}"
)