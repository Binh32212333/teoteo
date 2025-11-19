# Quick Start Guide

Get started with the Image Management & SEO Enhancement System in just a few minutes!

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows

# Install packages
pip install -r requirements.txt
```

### 2. Start the Web UI

```bash
streamlit run streamlit_app.py
```

The application will automatically open in your browser at `http://localhost:8501`

### 3. Configure AWS (First Time Only)

1. Go to **⚙️ Settings** page in the web UI
2. Enter your AWS credentials:
   - AWS Access Key ID
   - AWS Secret Access Key
   - AWS Region (e.g., `us-east-1`)
   - S3 Bucket Name
3. Click **Save AWS Configuration**
4. Click **Test S3 Connection** to verify

## 📸 Upload Your First Images

### Using the Web UI

1. Go to **📤 Upload Images** page
2. Click on the file uploader
3. Select your CSV file with image URLs (see format below)
4. Choose OCR engine (EasyOCR recommended)
5. Click **Start Upload Process**
6. Wait for processing to complete

### CSV Format

Create a CSV file with this format:

```csv
url
https://images.unsplash.com/photo-1517694712202-14dd9538aa97
https://images.unsplash.com/photo-1522071820081-009f0129c71c
https://images.unsplash.com/photo-1556761175-4b46a572b786
```

Save it as `my_images.csv` and upload!

## 📝 Enhance Your First SEO Post

1. Go to **📝 Process SEO Posts** page
2. Upload a text, HTML, or Markdown file
3. Select how many images to insert (default: 5)
4. Click **Process Post**
5. Preview the enhanced content
6. Download the enhanced post

## 🔍 Search Your Images

1. Go to **🔍 Search Images** page
2. Choose search type:
   - **Text Query**: Search by keywords
   - **Tag**: Browse by specific tags
   - **Category**: Filter by category
   - **View All**: See everything
3. Browse results in gallery view
4. Click on images to see details

## 📊 View Statistics

Go to **📊 Statistics** page to see:
- Total images and usage rates
- Category distribution charts
- Top tags analysis
- Recent activity

## 💡 Tips for Success

### Best Practices

1. **Image Quality**: Use high-quality image URLs from reliable sources
2. **CSV Organization**: Keep your CSV files organized with clear naming
3. **Regular Backups**: Export your metadata regularly from Statistics page
4. **OCR Selection**:
   - Use **EasyOCR** for better accuracy (slower)
   - Use **Tesseract** for faster processing (less accurate)

### Common Use Cases

#### For Bloggers
1. Upload images from free stock photo sites
2. System filters out watermarked images
3. Auto-tag images for easy finding
4. Insert relevant images into blog posts

#### For Content Marketers
1. Build a library of brand-approved images
2. Search by category for campaign-specific content
3. Batch process multiple articles
4. Track which images perform best

#### For SEO Specialists
1. Ensure all posts have optimized images
2. Automatically add alt text from descriptions
3. Maintain consistent image usage
4. Export usage reports

## 🐛 Troubleshooting

### Web UI Won't Start

```bash
# Make sure Streamlit is installed
pip install streamlit

# Try running with full path
python -m streamlit run streamlit_app.py
```

### AWS Connection Failed

1. Check credentials in Settings
2. Verify S3 bucket exists
3. Ensure bucket is in the same region
4. Check IAM permissions for S3 access

### No Images Passing Filter

- Images might contain text (phone numbers/websites)
- Try different image sources
- Check OCR detection in filtered images report
- Adjust patterns in `config.py` if needed

### Processing Very Slow

- First run downloads AI models (~2GB) - this is normal
- EasyOCR is slower but more accurate
- Switch to Tesseract for faster processing
- Consider processing in smaller batches

## 📚 Next Steps

### Learn More

- Read full [README.md](README.md) for detailed documentation
- Explore all Web UI features
- Try the CLI for automation (`python main.py --help`)

### Customize

- Edit `config.py` for custom detection patterns
- Modify `pages/*.py` to customize the UI
- Add your own image categories in `image_recognizer.py`

### Automate

Use the CLI for automated workflows:

```bash
# Automated upload
python main.py upload images.csv --ocr-engine easyocr

# Batch process posts
python main.py process ./posts --output-dir ./enhanced --num-images 3

# View stats
python main.py stats

# Search images
python main.py search --query "technology"
```

## 🎯 Example Workflow

Here's a complete workflow from start to finish:

```bash
# 1. Start the web UI
streamlit run streamlit_app.py

# 2. Configure AWS in Settings page

# 3. Upload images (Web UI: Upload Images page)
#    - Upload my_images.csv
#    - Select EasyOCR
#    - Click "Start Upload Process"
#    - Wait for completion

# 4. Check results (Web UI: Statistics page)
#    - View total images uploaded
#    - See category distribution
#    - Review top tags

# 5. Search images (Web UI: Search Images page)
#    - Try searching by category "technology"
#    - Browse gallery view
#    - Export as CSV if needed

# 6. Process blog posts (Web UI: Process SEO Posts page)
#    - Upload blog_post.html
#    - Set 5 images
#    - Click "Process Post"
#    - Download enhanced version

# 7. Done! Your posts are now enhanced with relevant images
```

## 🎉 You're All Set!

You now have a fully functional image management system. Start uploading images and enhancing your SEO content!

For questions or issues, check the [README.md](README.md) or open an issue on GitHub.

Happy image managing! 🖼️
