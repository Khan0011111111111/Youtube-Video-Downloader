import streamlit as st
#import yt-dlp
import pandas as pd

st.set_page_config(
    page_title="YouTube Video Downloader",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS styling
st.markdown("""
    <style>
        .header {
            font-size: 40px;
            font-weight: bold;
            color: #FF0000;
            text-align: center;
            margin-bottom: 30px;
        }
        .stButton>button {
            background-color: #FF0000;
            color: white;
            border-radius: 5px;
            padding: 10px 24px;
        }
        .stButton>button:hover {
            background-color: #CC0000;
            color: white;
        }
        .success { color: #4CAF50; }
        .error { color: #FF0000; }
    </style>
""", unsafe_allow_html=True)

def list_formats(url):
    """List all available formats for the video"""
    ydl_opts = {'quiet': True, 'no_warnings': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info['formats']
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def download_video(url, format_id=None, output_path='.'):
    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'quiet': False,
        'progress_hooks': [lambda d: st.progress(d['downloaded_bytes']/d['total_bytes'])],
    }

    if format_id:
        ydl_opts['format'] = format_id
    else:
        ydl_opts['format'] = 'best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False

# App Interface
st.markdown('<div class="header">🎬 YouTube Video Downloader</div>', unsafe_allow_html=True)

url = st.text_input("", placeholder="Enter YouTube URL here")

if 'formats' not in st.session_state:
    st.session_state.formats = None

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("📋 List Formats"):
        if url:
            with st.spinner("Fetching available formats..."):
                st.session_state.formats = list_formats(url)
        else:
            st.error("Please enter a valid YouTube URL")

if st.session_state.formats:
    # Create formatted DataFrame
    format_data = []
    for f in st.session_state.formats:
        format_id = f.get('format_id', 'N/A')
        ext = f.get('ext', 'N/A').upper()
        resolution = f.get('resolution', 'N/A')
        filesize = f.get('filesize')
        filesize = f"{filesize/1024/1024:.1f} MB" if filesize else 'N/A'
        
        format_data.append({
            'Quality': resolution,
            'Format': ext,
            'Size': filesize,
            'ID': format_id
        })

    df = pd.DataFrame(format_data)
    st.dataframe(
        df[['ID', 'Quality', 'Format', 'Size']],
        height=300,
        use_container_width=True,
        hide_index=True
    )

    # Format selection
    format_options = {f['ID']: f"ID: {f['ID']} | {f['Quality']} | {f['Format']} | {f['Size']}" 
                     for f in format_data}
    format_options['best'] = "Best Quality (Auto Select)"
    
    selected = st.selectbox(
        "Select Download Format:",
        options=['best'] + list(format_options.keys())[:-1],
        format_func=lambda x: format_options.get(x, x)
    )

    with col2:
        if st.button("⬇️ Download Video"):
            if url:
                with st.spinner("Downloading... This may take a while"):
                    if download_video(url, None if selected == 'best' else selected):
                        st.balloons()
                        st.success("🎉 Download completed! Check your local directory")
            else:
                st.error("Please enter a valid YouTube URL")

st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666;">
        Made with ❤️ using Streamlit & yt-dlp
    </div>
""", unsafe_allow_html=True)
