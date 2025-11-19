import streamlit as st
from metadata_manager import MetadataManager

def show():
    st.markdown('<div class="main-header">🔍 Search Images</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Find and explore your image database</div>', unsafe_allow_html=True)

    metadata_manager = MetadataManager()
    all_images = metadata_manager.get_all_images()

    if not all_images:
        st.info("📭 No images in database yet. Upload some images first!")
        return

    st.markdown(f"**Total images in database**: {len(all_images)}")
    st.markdown("---")

    # Search options
    search_type = st.radio(
        "Search by:",
        ["🔤 Text Query", "🏷️ Tag", "📂 Category", "📋 View All"],
        horizontal=True
    )

    results = []

    if search_type == "🔤 Text Query":
        query = st.text_input(
            "Enter search query",
            placeholder="e.g., business meeting, technology, outdoor...",
            help="Search in image descriptions and OCR text"
        )

        if query:
            results = metadata_manager.search_by_text(query)
            st.info(f"Found {len(results)} images matching '{query}'")

    elif search_type == "🏷️ Tag":
        # Get all available tags
        all_tags = list(metadata_manager.metadata.get('tags', {}).keys())

        if all_tags:
            tag = st.selectbox("Select tag", options=sorted(all_tags))
            results = metadata_manager.search_by_tags(tag)
            st.info(f"Found {len(results)} images with tag '{tag}'")
        else:
            st.warning("No tags available in database")

    elif search_type == "📂 Category":
        # Get all available categories
        all_categories = list(metadata_manager.metadata.get('categories', {}).keys())

        if all_categories:
            category = st.selectbox("Select category", options=sorted(all_categories))
            results = metadata_manager.search_by_category(category)
            st.info(f"Found {len(results)} images in category '{category}'")
        else:
            st.warning("No categories available in database")

    else:  # View All
        results = all_images
        st.info(f"Showing all {len(results)} images")

    # Display results
    if results:
        st.markdown("---")
        st.markdown("### 📸 Search Results")

        # Pagination
        items_per_page = 12
        total_pages = (len(results) - 1) // items_per_page + 1

        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1

        # Page selector
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.select_slider(
                "Page",
                options=list(range(1, total_pages + 1)),
                value=st.session_state.current_page
            )
            st.session_state.current_page = page

        # Calculate slice
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(results))
        page_results = results[start_idx:end_idx]

        # Display in grid
        cols_per_row = 3
        for i in range(0, len(page_results), cols_per_row):
            cols = st.columns(cols_per_row)

            for j in range(cols_per_row):
                idx = i + j
                if idx < len(page_results):
                    img = page_results[idx]

                    with cols[j]:
                        # Show image
                        try:
                            st.image(img['s3_url'], use_container_width=True)
                        except:
                            st.error("Image preview unavailable")

                        # Show metadata in expander
                        with st.expander("ℹ️ Details"):
                            st.markdown(f"**ID**: `{img['id'][:12]}...`")

                            if img.get('description'):
                                st.markdown(f"**Description**: {img['description']}")

                            if img.get('categories'):
                                st.markdown(f"**Categories**: {', '.join(img['categories'])}")

                            if img.get('tags'):
                                tags_str = ', '.join(img['tags'][:5])
                                if len(img['tags']) > 5:
                                    tags_str += f" +{len(img['tags']) - 5} more"
                                st.markdown(f"**Tags**: {tags_str}")

                            if img.get('original_url'):
                                st.markdown(f"**Original URL**: [{img['original_url'][:30]}...]({img['original_url']})")

                            st.markdown(f"**S3 URL**: [{img['s3_url'][:30]}...]({img['s3_url']})")

                            used_in = img.get('used_in_posts', [])
                            if used_in:
                                st.markdown(f"**Used in {len(used_in)} posts**")

                            # Copy URL button
                            if st.button(f"📋 Copy URL", key=f"copy_{img['id']}"):
                                st.code(img['s3_url'], language=None)

        # Page info
        st.caption(f"Showing {start_idx + 1}-{end_idx} of {len(results)} images")

    elif search_type != "📋 View All":
        st.warning("No results found. Try a different search query.")

    # Export functionality
    if results:
        st.markdown("---")
        st.markdown("### 💾 Export Results")

        col1, col2 = st.columns(2)

        with col1:
            # Export as JSON
            import json
            json_data = json.dumps(results, indent=2, ensure_ascii=False)

            st.download_button(
                label="📥 Download as JSON",
                data=json_data,
                file_name="search_results.json",
                mime="application/json",
                use_container_width=True
            )

        with col2:
            # Export as CSV
            import csv
            import io

            csv_buffer = io.StringIO()
            if results:
                fieldnames = ['id', 's3_url', 'original_url', 'categories', 'tags', 'description']
                writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
                writer.writeheader()

                for img in results:
                    writer.writerow({
                        'id': img.get('id', ''),
                        's3_url': img.get('s3_url', ''),
                        'original_url': img.get('original_url', ''),
                        'categories': ', '.join(img.get('categories', [])),
                        'tags': ', '.join(img.get('tags', [])),
                        'description': img.get('description', '')
                    })

            st.download_button(
                label="📥 Download as CSV",
                data=csv_buffer.getvalue(),
                file_name="search_results.csv",
                mime="text/csv",
                use_container_width=True
            )
