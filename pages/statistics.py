import streamlit as st
from metadata_manager import MetadataManager
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

def show():
    st.markdown('<div class="main-header">📊 Statistics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Analytics and insights about your image database</div>', unsafe_allow_html=True)

    metadata_manager = MetadataManager()
    stats = metadata_manager.get_stats()
    all_images = metadata_manager.get_all_images()

    if not all_images:
        st.info("📭 No data available yet. Upload some images to see statistics!")
        return

    # Overview stats
    st.markdown("### 📈 Overview")

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
        usage_percentage = (stats['images_used'] / stats['total_images'] * 100) if stats['total_images'] > 0 else 0
        st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{usage_percentage:.0f}%</div>
                <div class="stat-label">Usage Rate</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Category distribution
    st.markdown("### 📂 Category Distribution")

    category_counts = {}
    for img in all_images:
        for cat in img.get('categories', []):
            category_counts[cat] = category_counts.get(cat, 0) + 1

    if category_counts:
        col1, col2 = st.columns([2, 1])

        with col1:
            # Pie chart
            fig = px.pie(
                values=list(category_counts.values()),
                names=list(category_counts.keys()),
                title="Images by Category"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Table
            st.markdown("**Category Breakdown**")
            for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                st.text(f"{cat}: {count}")
    else:
        st.info("No category data available")

    st.markdown("---")

    # Top tags
    st.markdown("### 🏷️ Top Tags")

    tag_counts = {}
    for img in all_images:
        for tag in img.get('tags', []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    if tag_counts:
        # Get top 20 tags
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]

        col1, col2 = st.columns([2, 1])

        with col1:
            # Bar chart
            fig = go.Figure(data=[
                go.Bar(
                    x=[count for tag, count in top_tags],
                    y=[tag for tag, count in top_tags],
                    orientation='h'
                )
            ])
            fig.update_layout(
                title="Top 20 Tags",
                xaxis_title="Number of Images",
                yaxis_title="Tag",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Tag Usage**")
            for tag, count in top_tags[:10]:
                st.text(f"{tag}: {count}")
            if len(top_tags) > 10:
                st.caption(f"... and {len(top_tags) - 10} more")
    else:
        st.info("No tag data available")

    st.markdown("---")

    # Usage statistics
    st.markdown("### 📊 Usage Statistics")

    col1, col2 = st.columns(2)

    with col1:
        # Images by usage
        unused = stats['total_images'] - stats['images_used']

        fig = go.Figure(data=[
            go.Bar(
                x=['Used in Posts', 'Unused'],
                y=[stats['images_used'], unused],
                marker_color=['#1f77b4', '#d3d3d3']
            )
        ])
        fig.update_layout(
            title="Image Usage",
            yaxis_title="Number of Images"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Most used images
        st.markdown("**Most Used Images**")

        images_by_usage = sorted(
            all_images,
            key=lambda x: len(x.get('used_in_posts', [])),
            reverse=True
        )[:5]

        for idx, img in enumerate(images_by_usage, 1):
            usage_count = len(img.get('used_in_posts', []))
            if usage_count > 0:
                st.text(f"{idx}. {img['id'][:12]}... - {usage_count} posts")

        if not any(len(img.get('used_in_posts', [])) > 0 for img in images_by_usage):
            st.info("No images have been used in posts yet")

    st.markdown("---")

    # Filter reason breakdown
    st.markdown("### 🔍 Filter Analysis")

    filter_reasons = {}
    for img in all_images:
        reason = img.get('filter_reason', 'unknown')
        filter_reasons[reason] = filter_reasons.get(reason, 0) + 1

    if filter_reasons:
        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                values=list(filter_reasons.values()),
                names=list(filter_reasons.keys()),
                title="Filter Results"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Filter Breakdown**")
            for reason, count in sorted(filter_reasons.items(), key=lambda x: x[1], reverse=True):
                st.text(f"{reason}: {count}")

    st.markdown("---")

    # Recent activity
    st.markdown("### 🕒 Recent Activity")

    # Sort by upload date
    sorted_images = sorted(
        all_images,
        key=lambda x: x.get('uploaded_at', ''),
        reverse=True
    )[:10]

    if sorted_images:
        st.markdown("**Last 10 Uploaded Images**")

        for idx, img in enumerate(sorted_images, 1):
            with st.expander(f"{idx}. {img.get('id', 'Unknown')[:12]}... - {img.get('uploaded_at', 'Unknown date')[:10]}"):
                col1, col2 = st.columns([1, 2])

                with col1:
                    try:
                        st.image(img['s3_url'], use_container_width=True)
                    except:
                        st.text("Preview unavailable")

                with col2:
                    st.markdown(f"**Description**: {img.get('description', 'N/A')}")
                    st.markdown(f"**Categories**: {', '.join(img.get('categories', []))}")
                    st.markdown(f"**Tags**: {', '.join(img.get('tags', [])[:5])}")
                    st.markdown(f"**Used in posts**: {len(img.get('used_in_posts', []))}")

    # Export statistics
    st.markdown("---")
    st.markdown("### 💾 Export Statistics")

    import json

    stats_export = {
        'overview': stats,
        'category_distribution': category_counts,
        'tag_distribution': dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:50]),
        'filter_analysis': filter_reasons,
        'total_images': len(all_images)
    }

    json_data = json.dumps(stats_export, indent=2)

    st.download_button(
        label="📥 Download Statistics (JSON)",
        data=json_data,
        file_name="image_statistics.json",
        mime="application/json",
        use_container_width=True
    )
