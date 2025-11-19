import streamlit as st
import os
import tempfile
from config import Config
from image_downloader import ImageDownloader
from image_filter import ImageFilter
from image_recognizer import ImageRecognizer
from aws_uploader import AWSUploader
from metadata_manager import MetadataManager

def show():
    st.markdown('<div class="main-header">📤 Upload Images</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Download, filter, and upload images from CSV</div>', unsafe_allow_html=True)

    # Check AWS configuration
    if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
        st.error("⚠️ AWS credentials not configured. Please go to Settings to configure your AWS credentials.")
        return

    # Instructions
    with st.expander("📋 Instructions", expanded=False):
        st.markdown("""
        ### How to Upload Images

        1. **Prepare CSV File**: Create a CSV file with a column named `url`, `image_url`, or `URL` containing image URLs
        2. **Upload CSV**: Click the file uploader below and select your CSV file
        3. **Select OCR Engine**: Choose between EasyOCR (more accurate) or Tesseract (faster)
        4. **Start Process**: Click the button to start the upload workflow

        ### What Happens

        The system will:
        - ✅ Download images from URLs
        - ✅ Validate image format and size
        - ✅ Use OCR to detect text in images
        - ✅ Filter out images containing phone numbers or websites
        - ✅ Analyze remaining images with AI to generate tags and categories
        - ✅ Upload approved images to AWS S3
        - ✅ Save metadata for search and reuse

        **Example CSV:**
        ```csv
        url
        https://images.unsplash.com/photo-1517694712202-14dd9538aa97
        https://images.unsplash.com/photo-1522071820081-009f0129c71c
        ```
        """)

    st.markdown("---")

    # File upload
    uploaded_file = st.file_uploader(
        "Upload CSV file with image URLs",
        type=['csv'],
        help="CSV file should have a column named 'url', 'image_url', or 'URL'"
    )

    # OCR engine selection
    col1, col2 = st.columns(2)
    with col1:
        ocr_engine = st.selectbox(
            "OCR Engine",
            options=['easyocr', 'tesseract'],
            help="EasyOCR is more accurate but slower. Tesseract is faster but may miss some text."
        )

    with col2:
        st.info(f"**Selected**: {ocr_engine.upper()}")
        if ocr_engine == 'easyocr':
            st.caption("✅ More accurate text detection")
        else:
            st.caption("⚡ Faster processing")

    st.markdown("---")

    # Process button
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        # Show file info
        st.success(f"✅ Uploaded: {uploaded_file.name}")

        if st.button("🚀 Start Upload Process", type="primary", use_container_width=True):
            try:
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Step 1: Download images
                status_text.text("Step 1/5: Downloading images from CSV...")
                progress_bar.progress(0.2)

                downloader = ImageDownloader()
                downloaded_images = downloader.download_from_csv(tmp_path)

                if not downloaded_images:
                    st.error("❌ No images were downloaded. Please check your CSV file and URLs.")
                    os.unlink(tmp_path)
                    return

                st.info(f"📥 Downloaded {len(downloaded_images)} images")

                # Step 2: Filter images
                status_text.text("Step 2/5: Filtering images with OCR...")
                progress_bar.progress(0.4)

                image_filter = ImageFilter(ocr_engine=ocr_engine)
                passed_images, filtered_images = image_filter.filter_images(downloaded_images)

                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"✅ Passed filter: {len(passed_images)}")
                with col2:
                    st.warning(f"⚠️ Filtered out: {len(filtered_images)}")

                # Show filtered images details
                if filtered_images:
                    with st.expander(f"View {len(filtered_images)} filtered images"):
                        for img in filtered_images:
                            reason = img.get('filter_reason', 'unknown')
                            st.text(f"❌ {img['url']} - Reason: {reason}")

                if not passed_images:
                    st.error("❌ No images passed the filter. All images contained phone numbers or websites.")
                    os.unlink(tmp_path)
                    return

                # Step 3: Analyze images
                status_text.text("Step 3/5: Analyzing images with AI...")
                progress_bar.progress(0.6)

                recognizer = ImageRecognizer()
                analyzed_images = recognizer.analyze_batch(passed_images)

                st.info(f"🤖 Analyzed {len(analyzed_images)} images")

                # Step 4: Upload to AWS
                status_text.text("Step 4/5: Uploading to AWS S3...")
                progress_bar.progress(0.8)

                uploader = AWSUploader()

                if not uploader.check_bucket_exists():
                    st.error(f"❌ S3 bucket '{Config.AWS_S3_BUCKET}' does not exist or is not accessible")
                    os.unlink(tmp_path)
                    return

                uploaded_images = uploader.upload_images(analyzed_images)

                if not uploaded_images:
                    st.error("❌ Failed to upload images to S3")
                    os.unlink(tmp_path)
                    return

                st.success(f"☁️ Uploaded {len(uploaded_images)} images to S3")

                # Step 5: Save metadata
                status_text.text("Step 5/5: Saving metadata...")
                progress_bar.progress(0.9)

                metadata_manager = MetadataManager()
                metadata_manager.add_images_batch(uploaded_images)

                progress_bar.progress(1.0)
                status_text.text("✅ Complete!")

                st.markdown("---")
                st.success(f"🎉 Successfully processed {len(uploaded_images)} images!")

                # Show some sample results
                st.markdown("### 📸 Sample Uploaded Images")

                for idx, img in enumerate(uploaded_images[:3]):  # Show first 3
                    with st.expander(f"Image {idx + 1}: {img['url_hash'][:8]}..."):
                        col1, col2 = st.columns([1, 2])

                        with col1:
                            try:
                                st.image(img['s3_url'], use_container_width=True)
                            except:
                                st.text("Image preview not available")

                        with col2:
                            st.markdown(f"**S3 URL**: {img['s3_url']}")
                            st.markdown(f"**Categories**: {', '.join(img.get('categories', []))}")
                            st.markdown(f"**Tags**: {', '.join(img.get('tags', []))}")
                            st.markdown(f"**Description**: {img.get('description', 'N/A')}")

                if len(uploaded_images) > 3:
                    st.info(f"... and {len(uploaded_images) - 3} more images. Go to Search to view all.")

                # Clean up
                os.unlink(tmp_path)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                with st.expander("View error details"):
                    st.code(traceback.format_exc())
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    else:
        st.info("👆 Upload a CSV file to get started")

        # Show example
        with st.expander("💡 Example CSV File"):
            example_csv = """url
https://images.unsplash.com/photo-1517694712202-14dd9538aa97
https://images.unsplash.com/photo-1522071820081-009f0129c71c
https://images.unsplash.com/photo-1556761175-4b46a572b786"""

            st.code(example_csv, language='csv')
            st.download_button(
                label="📥 Download Example CSV",
                data=example_csv,
                file_name="example_urls.csv",
                mime="text/csv"
            )
