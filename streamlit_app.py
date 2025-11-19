import json

import streamlit as st

from pipeline import process_short_url, NewsItem

st.set_page_config(
    page_title="AI News Extractor from YouTube Shorts (PoC)",
    layout="centered",
)

st.title("📰 AI Agent for Real-Time News Extraction from YouTube Shorts (PoC)")

st.write(
    """
Paste a **YouTube Short URL**, and this PoC will:

1. Download the audio with yt-dlp  
2. Transcribe it using Whisper  
3. Ask an LLM to decide if it's news  
4. If yes, generate a headline, summary, and tags  
"""
)

url = st.text_input("YouTube Short URL", placeholder="https://youtube.com/shorts/...")
run_btn = st.button("Analyze Short")

if run_btn and url:
    with st.spinner("Processing video (download → transcribe → analyze)..."):
        try:
            item: NewsItem = process_short_url(url)
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    st.divider()

    if not item.is_news:
        st.subheader("Result")
        st.warning("This video does **not** look like news based on the transcript.")
        with st.expander("Show transcript anyway"):
            st.write(item.transcript or "_(empty transcript)_")
    else:
        st.subheader("✅ News Detected")

        if item.thumbnail:
            st.image(item.thumbnail, caption=item.video_title, use_container_width=True)

        st.markdown(f"**Headline**: {item.headline or '—'}")
        st.markdown(f"**Summary**: {item.summary or '—'}")

        meta_cols = st.columns(2)
        with meta_cols[0]:
            st.markdown(f"**Category**: `{item.category or 'N/A'}`")
        with meta_cols[1]:
            st.markdown(f"**Channel**: `{item.channel or 'Unknown'}`")

        if item.tags:
            st.markdown("**Tags**:")
            st.write(" ".join(item.tags))

        with st.expander("Raw transcript"):
            st.write(item.transcript or "_(empty transcript)_")

        with st.expander("Raw LLM output (debug)"):
            st.json(item.raw_llm_output)

    st.divider()
    st.caption("Note: This is a PoC. For production, add DB storage + auto-post to X/Telegram/etc.")
else:
    st.info("Enter a YouTube Short URL above and click **Analyze Short**.")
