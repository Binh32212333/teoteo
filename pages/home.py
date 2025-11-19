import streamlit as st
from metadata_manager import MetadataManager
from config import Config
import os

def show():
    st.markdown('<div class="main-header">🖼️ Image Management & SEO Enhancement System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automate your image workflow and enhance SEO content with AI</div>', unsafe_allow_html=True)

    # Quick stats
    try:
        metadata_manager = MetadataManager()
        stats = metadata_manager.get_stats()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number">{stats['total_images']}</div>
                    <div class="stat-label">Total Images</div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number">{stats['total_tags']}</div>
                    <div class="stat-label">Unique Tags</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number">{stats['total_categories']}</div>
                    <div class="stat-label">Categories</div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-number">{stats['images_used']}</div>
                    <div class="stat-label">Images Used</div>
                </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.info("No images in database yet. Upload some images to get started!")

    st.markdown("---")

    # Features overview
    st.markdown("## ✨ Key Features")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 📤 Image Upload & Filtering
        - Download images from CSV files containing URLs
        - Automatic OCR-based filtering for phone numbers and websites
        - AI-powered categorization and tagging
        - Upload to AWS S3 with metadata

        ### 🔍 Smart Search
        - Search by keywords, tags, or categories
        - Semantic similarity search
        - Track image usage across posts
        """)

    with col2:
        st.markdown("""
        ### 📝 SEO Post Enhancement
        - Automatic content analysis
        - Smart image matching based on context
        - Automatic image insertion
        - Support for HTML, Markdown, and plain text

        ### 📊 Analytics & Management
        - Comprehensive statistics dashboard
        - Image metadata management
        - Usage tracking and reporting
        """)

    st.markdown("---")

    # Getting started
    st.markdown("## 🚀 Getting Started")

    tab1, tab2, tab3 = st.tabs(["1️⃣ Configure", "2️⃣ Upload Images", "3️⃣ Process Posts"])

    with tab1:
        st.markdown("""
        ### Configure AWS Credentials

        Before you can upload images, you need to configure your AWS S3 credentials:

        1. Go to **⚙️ Settings** page
        2. Enter your AWS credentials:
           - AWS Access Key ID
           - AWS Secret Access Key
           - AWS Region
           - S3 Bucket Name
        3. Click **Save Configuration**

        Your credentials will be saved securely in the `.env` file.
        """)

        # Check if configured
        if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            st.success("✅ AWS credentials are configured!")
        else:
            st.warning("⚠️ AWS credentials not configured. Go to Settings to configure.")

    with tab2:
        st.markdown("""
        ### Upload Images from CSV

        1. Prepare a CSV file with image URLs (see example below)
        2. Go to **📤 Upload Images** page
        3. Upload your CSV file
        4. Select OCR engine (EasyOCR or Tesseract)
        5. Click **Start Upload Process**

        **Example CSV format:**
        ```csv
        url
        https://example.com/image1.jpg
        https://example.com/image2.png
        https://example.com/image3.jpg
        ```

        The system will:
        - Download images from URLs
        - Filter out images with phone numbers or websites using OCR
        - Analyze and tag images with AI
        - Upload to AWS S3
        - Save metadata for search and reuse
        """)

    with tab3:
        st.markdown("""
        ### Process SEO Posts

        1. Go to **📝 Process SEO Posts** page
        2. Upload your post file (TXT, HTML, or Markdown)
        3. Select number of images to insert
        4. Click **Process Post**

        The system will:
        - Analyze your post content
        - Find the most relevant images from your database
        - Automatically insert images at strategic positions
        - Download the enhanced post

        You can also batch process multiple posts by uploading a ZIP file!
        """)

    st.markdown("---")

    # Quick actions
    st.markdown("## ⚡ Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📤 Upload Images", use_container_width=True):
            st.session_state.page = "📤 Upload Images"
            st.rerun()

    with col2:
        if st.button("🔍 Search Images", use_container_width=True):
            st.session_state.page = "🔍 Search Images"
            st.rerun()

    with col3:
        if st.button("📝 Process Posts", use_container_width=True):
            st.session_state.page = "📝 Process SEO Posts"
            st.rerun()
