import streamlit as st
import os
import tempfile
import zipfile
from metadata_manager import MetadataManager
from image_recognizer import ImageRecognizer
from seo_post_manager import SEOPostManager

def show():
    st.markdown('<div class="main-header">📝 Process SEO Posts</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automatically enhance your posts with relevant images</div>', unsafe_allow_html=True)

    # Check if images are available
    metadata_manager = MetadataManager()
    all_images = metadata_manager.get_all_images()

    if not all_images:
        st.warning("⚠️ No images in database. Please upload images first before processing posts.")
        return

    st.success(f"✅ {len(all_images)} images available for insertion")

    # Instructions
    with st.expander("📋 Instructions", expanded=False):
        st.markdown("""
        ### How to Process SEO Posts

        1. **Single Post**: Upload one post file (TXT, HTML, or MD)
        2. **Batch Processing**: Upload a ZIP file containing multiple posts
        3. **Select Settings**: Choose number of images to insert
        4. **Process**: Click the button to analyze and enhance your post(s)

        ### What Happens

        The system will:
        - 📖 Analyze your post content
        - 🤖 Find the most relevant images using AI
        - 📍 Insert images at strategic positions
        - 💾 Provide enhanced post for download

        **Supported Formats**: `.txt`, `.html`, `.htm`, `.md`
        """)

    st.markdown("---")

    # Upload type selection
    upload_type = st.radio(
        "Upload type:",
        ["📄 Single Post", "📦 Batch (ZIP file)"],
        horizontal=True
    )

    # Settings
    col1, col2 = st.columns(2)

    with col1:
        num_images = st.slider(
            "Number of images to insert",
            min_value=1,
            max_value=10,
            value=5,
            help="How many images to insert into each post"
        )

    with col2:
        st.info(f"**Will insert**: {num_images} image(s)")

    st.markdown("---")

    if upload_type == "📄 Single Post":
        process_single_post(num_images, metadata_manager)
    else:
        process_batch_posts(num_images, metadata_manager)


def process_single_post(num_images, metadata_manager):
    """Process a single post file"""

    uploaded_file = st.file_uploader(
        "Upload post file",
        type=['txt', 'html', 'htm', 'md'],
        help="Upload your SEO post file"
    )

    if uploaded_file is not None:
        st.success(f"✅ Uploaded: {uploaded_file.name}")

        # Preview content
        with st.expander("👀 Preview Original Content"):
            content = uploaded_file.getvalue().decode('utf-8')
            st.text_area("Content", content, height=200, disabled=True)

        if st.button("🚀 Process Post", type="primary", use_container_width=True):
            try:
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1], mode='w', encoding='utf-8') as tmp_file:
                    tmp_file.write(content)
                    tmp_path = tmp_file.name

                # Create progress indicator
                with st.spinner("Processing post..."):
                    # Initialize components
                    recognizer = ImageRecognizer()
                    post_manager = SEOPostManager(metadata_manager, recognizer)

                    # Create output file
                    output_path = tmp_path.replace(os.path.splitext(tmp_path)[1], '_enhanced' + os.path.splitext(tmp_path)[1])

                    # Process post
                    success = post_manager.process_post(
                        tmp_path,
                        output_path,
                        num_images=num_images,
                        post_id=uploaded_file.name
                    )

                    if success:
                        # Read enhanced content
                        with open(output_path, 'r', encoding='utf-8') as f:
                            enhanced_content = f.read()

                        st.success("✅ Post processed successfully!")

                        # Show preview
                        with st.expander("👀 Preview Enhanced Content"):
                            st.text_area("Enhanced Content", enhanced_content, height=300, disabled=True)

                        # Download button
                        st.download_button(
                            label="📥 Download Enhanced Post",
                            data=enhanced_content,
                            file_name=f"enhanced_{uploaded_file.name}",
                            mime="text/plain",
                            use_container_width=True
                        )

                        # Clean up
                        os.unlink(tmp_path)
                        os.unlink(output_path)
                    else:
                        st.error("❌ Failed to process post. Please check logs.")
                        os.unlink(tmp_path)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                with st.expander("View error details"):
                    st.code(traceback.format_exc())

    else:
        st.info("👆 Upload a post file to get started")


def process_batch_posts(num_images, metadata_manager):
    """Process multiple posts from a ZIP file"""

    uploaded_file = st.file_uploader(
        "Upload ZIP file containing posts",
        type=['zip'],
        help="ZIP file should contain TXT, HTML, or MD files"
    )

    if uploaded_file is not None:
        st.success(f"✅ Uploaded: {uploaded_file.name}")

        # Extract and show files
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, 'posts.zip')

            with open(zip_path, 'wb') as f:
                f.write(uploaded_file.getvalue())

            # Extract zip
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Find post files
            supported_extensions = ['.txt', '.html', '.htm', '.md']
            post_files = []

            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if any(file.endswith(ext) for ext in supported_extensions):
                        post_files.append(os.path.join(root, file))

            st.info(f"Found {len(post_files)} post files in ZIP")

            if post_files:
                with st.expander("📄 Files to process"):
                    for pf in post_files:
                        st.text(f"• {os.path.basename(pf)}")

                if st.button("🚀 Process All Posts", type="primary", use_container_width=True):
                    try:
                        # Create progress bar
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        # Initialize components
                        recognizer = ImageRecognizer()
                        post_manager = SEOPostManager(metadata_manager, recognizer)

                        # Create output directory
                        output_dir = os.path.join(temp_dir, 'enhanced')
                        os.makedirs(output_dir, exist_ok=True)

                        # Process each file
                        processed = 0
                        failed = []

                        for idx, post_file in enumerate(post_files):
                            status_text.text(f"Processing {idx + 1}/{len(post_files)}: {os.path.basename(post_file)}")

                            output_path = os.path.join(output_dir, f"enhanced_{os.path.basename(post_file)}")

                            success = post_manager.process_post(
                                post_file,
                                output_path,
                                num_images=num_images,
                                post_id=os.path.basename(post_file)
                            )

                            if success:
                                processed += 1
                            else:
                                failed.append(os.path.basename(post_file))

                            progress_bar.progress((idx + 1) / len(post_files))

                        status_text.text("✅ Complete!")

                        # Show results
                        col1, col2 = st.columns(2)
                        with col1:
                            st.success(f"✅ Processed: {processed}")
                        with col2:
                            if failed:
                                st.error(f"❌ Failed: {len(failed)}")

                        if failed:
                            with st.expander("Failed files"):
                                for f in failed:
                                    st.text(f"• {f}")

                        # Create ZIP of enhanced posts
                        output_zip_path = os.path.join(temp_dir, 'enhanced_posts.zip')

                        with zipfile.ZipFile(output_zip_path, 'w') as zip_out:
                            for root, dirs, files in os.walk(output_dir):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.relpath(file_path, output_dir)
                                    zip_out.write(file_path, arcname)

                        # Provide download
                        with open(output_zip_path, 'rb') as f:
                            st.download_button(
                                label="📥 Download Enhanced Posts (ZIP)",
                                data=f.read(),
                                file_name="enhanced_posts.zip",
                                mime="application/zip",
                                use_container_width=True
                            )

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        import traceback
                        with st.expander("View error details"):
                            st.code(traceback.format_exc())

            else:
                st.warning("No valid post files found in ZIP")

    else:
        st.info("👆 Upload a ZIP file to get started")
