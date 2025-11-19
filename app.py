#!/usr/bin/env python3
"""
Streamlit Web UI for Automated Image Management System
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Image Management & SEO System",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 5px;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("# 🖼️ Image Management")
st.sidebar.markdown("### Navigation")

page = st.sidebar.radio(
    "Go to:",
    ["🏠 Home", "📤 Upload Images", "🔍 Search Images", "📝 Process SEO Posts", "📊 Statistics", "⚙️ Settings"]
)

# Import pages
if page == "🏠 Home":
    from pages import home
    home.show()
elif page == "📤 Upload Images":
    from pages import upload
    upload.show()
elif page == "🔍 Search Images":
    from pages import search
    search.show()
elif page == "📝 Process SEO Posts":
    from pages import process_posts
    process_posts.show()
elif page == "📊 Statistics":
    from pages import statistics
    statistics.show()
elif page == "⚙️ Settings":
    from pages import settings
    settings.show()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8rem;'>
    <p>Automated Image Management<br>& SEO Enhancement System</p>
    <p>Version 1.0</p>
</div>
""", unsafe_allow_html=True)
