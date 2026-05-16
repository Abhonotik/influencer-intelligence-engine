# =========================================================
# IMPORT LIBRARIES
# =========================================================

import os
import json
import time
import pandas as pd
import streamlit as st
import yt_dlp

from dotenv import load_dotenv
from googleapiclient.discovery import build

# =========================================================
# LOAD ENV VARIABLES
# =========================================================

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(

    page_title="Influencer Intelligence Engine",

    page_icon="📊",

    layout="wide"

)

# =========================================================
# SESSION STATE
# =========================================================

if "show_home" not in st.session_state:

    st.session_state.show_home = True

# =========================================================
# TITLE
# =========================================================

st.title(
    "📊 Influencer Intelligence Engine"
)

st.write(
    "Discover and audit YouTube creators using keyword and region filters."
)

# =========================================================
# REGION MAPPING
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

VALID_REGION_CODES = set(
    REGION_CODES.values()
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
# SIDEBAR
# =========================================================

st.sidebar.header(
    "⚙ Search Configuration"
)

# =========================================================
# NICHE DROPDOWN
# =========================================================

selected_niche = st.sidebar.selectbox(

    "Select Niche",

    [
        "Tech",
        "Finance",
        "AI",
        "Gaming",
        "Beauty",
        "Fitness",
        "Education",
        "Lifestyle",
        "Crypto",
        "Custom"
    ]

)

# =========================================================
# CUSTOM NICHE
# =========================================================

if selected_niche == "Custom":

    search_keyword = st.sidebar.text_input(
        "Enter Custom Keyword"
    )

else:

    search_keyword = selected_niche

# =========================================================
# REGION INPUT
# =========================================================

country_input = st.sidebar.text_input(

    "Country or Region",

    placeholder="India, USA, France"

)

# =========================================================
# CREATOR LIMIT
# =========================================================

creator_limit = st.sidebar.slider(

    "Creators To Audit",

    min_value=1,

    max_value=20,

    value=5

)

# =========================================================
# RUN BUTTON
# =========================================================

if st.sidebar.button(
    "🚀 Run Audit Pipeline"
):

    st.session_state.show_home = False

# =========================================================
# MAIN PIPELINE
# =========================================================

if not st.session_state.show_home:

    # =====================================================
    # VALIDATE KEYWORD
    # =====================================================

    if not search_keyword:

        st.error(
            "Keyword cannot be empty."
        )

        if st.button(
            "🏠 Go To Home Page",
            width="stretch"
        ):

            st.session_state.show_home = True
            st.rerun()

        st.stop()

    # =====================================================
    # VALIDATE REGION
    # =====================================================

    region = REGION_CODES.get(

        country_input.lower(),

        country_input.upper()

    )

    if region not in VALID_REGION_CODES:

        st.error(
            "Invalid country or region."
        )

        if st.button(
            "🏠 Go To Home Page",
            width="stretch"
        ):

            st.session_state.show_home = True
            st.rerun()

        st.stop()

    # =====================================================
    # RESULTS STORAGE
    # =====================================================

    final_results = []

    # =====================================================
    # START MESSAGE
    # =====================================================

    st.info(
        "🚀 Starting influencer audit pipeline..."
    )

    # =====================================================
    # SEARCH CHANNELS
    # =====================================================

    try:

        search_request = youtube.search().list(

            q=search_keyword,

            type="channel",

            regionCode=region,

            maxResults=creator_limit,

            part="snippet"

        )

        search_response = search_request.execute()

    # =====================================================
    # API ERROR HANDLING
    # =====================================================

    except Exception:

        st.error(

            "❌ YouTube API quota exceeded or request failed.\n\n"

            "Please try again later or use another API key."

        )

        if st.button(
            "🏠 Go To Home Page",
            width="stretch"
        ):

            st.session_state.show_home = True
            st.rerun()

        st.stop()

    # =====================================================
    # PROGRESS BAR
    # =====================================================

    progress_bar = st.progress(0)

    # =====================================================
    # LOOP THROUGH CHANNELS
    # =====================================================

    for index, item in enumerate(

        search_response["items"]

    ):

        channel_name = item["snippet"]["title"]

        channel_id = item["snippet"]["channelId"]

        st.subheader(
            f"📺 {channel_name}"
        )

        try:

            # =============================================
            # CHANNEL STATS
            # =============================================

            stats_request = youtube.channels().list(

                part="statistics",

                id=channel_id

            )

            stats_response = stats_request.execute()

            stats = stats_response["items"][0][
                "statistics"
            ]

            subscribers = stats.get(
                "subscriberCount",
                "Metric Restricted"
            )

            total_views = stats.get(
                "viewCount",
                "Metric Restricted"
            )

            total_videos = stats.get(
                "videoCount",
                "Metric Restricted"
            )

            # =============================================
            # METRIC DISPLAY
            # =============================================

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Subscribers",
                subscribers
            )

            col2.metric(
                "Total Views",
                total_views
            )

            col3.metric(
                "Videos",
                total_videos
            )

            # =============================================
            # RECENT UPLOAD STORAGE
            # =============================================

            recent_uploads = []

            # =============================================
            # FETCH RECENT VIDEOS
            # =============================================

            video_request = youtube.search().list(

                part="snippet",

                channelId=channel_id,

                maxResults=5,

                order="date",

                type="video"

            )

            video_response = video_request.execute()

            upload_data = []

            # =============================================
            # PROCESS VIDEOS
            # =============================================

            for video in video_response["items"]:

                title = video["snippet"].get(

                    "title",

                    "Title not found"

                )

                video_id = video["id"]["videoId"]

                video_url = (
                    f"https://www.youtube.com/watch?v={video_id}"
                )

                raw_date = video["snippet"].get(
                    "publishedAt"
                )

                # =========================================
                # PRIMARY DATE EXTRACTION
                # =========================================

                if raw_date:

                    upload_date = raw_date[:10]

                # =========================================
                # yt-dlp FALLBACK
                # =========================================

                else:

                    try:

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

                    except Exception:

                        upload_date = (
                            "Date not found"
                        )

                # =========================================
                # STORE VIDEO DATA
                # =========================================

                upload_data.append({

                    "Video Title": title,

                    "Upload Date": upload_date

                })

                recent_uploads.append({

                    "title": title,

                    "upload_date": upload_date

                })

            # =============================================
            # DISPLAY TABLE
            # =============================================

            upload_df = pd.DataFrame(
                upload_data
            )

            st.dataframe(

                upload_df,

                width="stretch"

            )

            # =============================================
            # STORE CREATOR DATA
            # =============================================

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

        # =================================================
        # CHANNEL ERROR HANDLING
        # =================================================

        except Exception as e:

            st.error(
                f"❌ Error processing {channel_name}: {e}"
            )

        # =================================================
        # UPDATE PROGRESS BAR
        # =================================================

        progress_bar.progress(
            (index + 1) / creator_limit
        )

        # =================================================
        # RATE LIMITING
        # =================================================

        time.sleep(2)

    # =====================================================
    # PIPELINE COMPLETED
    # =====================================================

    st.success(
        "✅ Audit Pipeline Completed Successfully!"
    )

    st.balloons()

    st.info(
        "You can download reports below or return to the home page."
    )

    # =====================================================
    # JSON DOWNLOAD
    # =====================================================

    json_data = json.dumps(

        final_results,

        indent=4,

        ensure_ascii=False

    )

    st.download_button(

        label="⬇ Download JSON",

        data=json_data,

        file_name="sample_output.json",

        mime="application/json",

        width="stretch"

    )

    # =====================================================
    # CREATE CSV DATA
    # =====================================================

    flat_rows = []

    for creator in final_results:

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

    # =====================================================
    # CSV DOWNLOAD
    # =====================================================

    csv_df = pd.DataFrame(
        flat_rows
    )

    csv_data = csv_df.to_csv(
        index=False
    )

    st.download_button(

        label="⬇ Download CSV",

        data=csv_data,

        file_name="sample_output.csv",

        mime="text/csv",

        width="stretch"

    )

