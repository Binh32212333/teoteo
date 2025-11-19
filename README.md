# Automated Image Management and SEO Post Enhancement System

A comprehensive Python-based system that automatically downloads, filters, analyzes, and manages images for SEO content. The system uses OCR to filter out images with phone numbers or websites, employs AI to categorize and tag images, stores them on AWS S3, and intelligently inserts relevant images into text-based SEO posts.

## Features

### Core Functionality
- **Automated Image Download**: Download images from URLs provided in a CSV file
- **Intelligent Filtering**: Use OCR (EasyOCR or Tesseract) to detect and filter out images containing phone numbers or websites
- **AI-Powered Recognition**: Automatically categorize and tag images using CLIP (Contrastive Language-Image Pre-training)
- **AWS S3 Integration**: Securely upload and store filtered images on Amazon S3
- **Metadata Management**: Track all images with comprehensive metadata including tags, categories, and usage
- **SEO Post Enhancement**: Automatically analyze text-based SEO posts and insert relevant images
- **Content Matching**: Use semantic similarity to match images with post content for maximum relevance

### User Interfaces
- **🌐 Web UI**: User-friendly web interface built with Streamlit (recommended for most users)
- **💻 CLI**: Command-line interface for automation and advanced users
- **📊 Analytics Dashboard**: Visual statistics and insights about your image database
- **🔍 Interactive Search**: Browse and search images with multiple filters

## System Architecture

```
┌─────────────────┐
│   CSV File      │
│  (Image URLs)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Image Downloader│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OCR Filter     │◄─── EasyOCR/Tesseract
│ (Phone/Website) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Image Recognizer │◄─── CLIP Model
│ (Tags/Category) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AWS S3 Upload  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│Metadata Manager │◄────►│ SEO Post     │
│    (JSON DB)    │      │  Processor   │
└─────────────────┘      └──────────────┘
```

## Installation

### Prerequisites

- Python 3.8 or higher
- AWS Account with S3 bucket
- Tesseract OCR (if using tesseract engine)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/teoteo.git
cd teoteo
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install System Dependencies

**For EasyOCR (Recommended):**
No additional system dependencies required.

**For Tesseract OCR:**

- Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
- macOS: `brew install tesseract`
- Windows: Download installer from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### Step 5: Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your AWS credentials:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name
```

## Usage

The system can be used in two ways: **Web UI (Recommended)** or **Command Line Interface**

### 🌐 Web UI (Recommended for Beginners)

The easiest way to use the system is through the web-based user interface:

#### Starting the Web UI

**Quick Start (Recommended):**

```bash
# Linux/Mac
./run.sh

# Windows
run.bat
```

These launcher scripts automatically:
- Create virtual environment if needed
- Install dependencies
- Create .env file from template
- Start the web UI

**Manual Start:**

```bash
streamlit run streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

#### Web UI Features

The web interface provides six main pages:

1. **🏠 Home**: Dashboard with quick stats and getting started guide
2. **📤 Upload Images**:
   - Upload CSV files with image URLs
   - Select OCR engine
   - Monitor upload progress in real-time
   - View filtered and uploaded images

3. **🔍 Search Images**:
   - Search by text query, tags, or categories
   - Browse all images in a gallery view
   - View detailed metadata for each image
   - Export search results as JSON or CSV

4. **📝 Process SEO Posts**:
   - Upload single post files (TXT, HTML, MD)
   - Batch process multiple posts via ZIP upload
   - Select number of images to insert
   - Download enhanced posts

5. **📊 Statistics**:
   - View comprehensive analytics
   - Category and tag distribution charts
   - Usage statistics and trends
   - Recent activity monitoring

6. **⚙️ Settings**:
   - Configure AWS credentials via UI
   - Test S3 connection
   - View system information
   - Manage storage and maintenance

#### Web UI Advantages

- ✅ No command line knowledge required
- ✅ Visual feedback and progress indicators
- ✅ Interactive image gallery
- ✅ Easy file uploads and downloads
- ✅ Real-time statistics and charts
- ✅ Configure settings through forms

### 💻 Command Line Interface

The system provides four main CLI commands:

### 1. Upload Images from CSV

Download images from a CSV file, filter out unwanted images, analyze content, and upload to AWS S3:

```bash
python main.py upload path/to/images.csv
```

**CSV Format:**
Your CSV file should have a column named `url`, `image_url`, or `URL`:

```csv
url
https://example.com/image1.jpg
https://example.com/image2.png
https://example.com/image3.jpg
```

**Optional Parameters:**
- `--ocr-engine`: Choose OCR engine (`easyocr` or `tesseract`, default: `easyocr`)

```bash
python main.py upload images.csv --ocr-engine tesseract
```

### 2. Process SEO Posts

Automatically analyze SEO posts and insert relevant images:

```bash
python main.py process /path/to/posts/directory
```

**Optional Parameters:**
- `--output-dir`: Specify output directory (if not set, overwrites original files)
- `--num-images`: Number of images to insert per post (default: 5)

```bash
python main.py process ./posts --output-dir ./posts_with_images --num-images 3
```

**Supported File Formats:**
- Plain text (`.txt`)
- Markdown (`.md`)
- HTML (`.html`, `.htm`)

### 3. View Statistics

Display statistics about your image database:

```bash
python main.py stats
```

### 4. Search Images

Search for images in your database:

```bash
# Search by text query
python main.py search --query "business meeting"

# Search by tag
python main.py search --tag "technology"

# Search by category
python main.py search --category "business"

# List all images
python main.py search
```

## Configuration

All configuration is managed through environment variables in the `.env` file:

### AWS Settings
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_REGION`: AWS region (e.g., `us-east-1`)
- `AWS_S3_BUCKET`: S3 bucket name

### Image Processing
- `MAX_IMAGE_SIZE_MB`: Maximum image size in MB (default: 10)
- `ALLOWED_IMAGE_FORMATS`: Comma-separated list of formats (default: `jpg,jpeg,png,webp`)

### OCR Settings
- `OCR_ENGINE`: OCR engine to use (`easyocr` or `tesseract`)
- `OCR_LANGUAGES`: Comma-separated list of languages (default: `en`)

### Storage Paths
- `LOCAL_STORAGE_PATH`: Local storage for images (default: `./storage/images`)
- `TEMP_DOWNLOAD_PATH`: Temporary download location (default: `./temp`)
- `METADATA_DB_PATH`: Path to metadata JSON file (default: `./storage/metadata.json`)

## How It Works

### Image Upload Workflow

1. **Download**: Images are downloaded from URLs in the CSV file
2. **Validation**: Each image is validated for format, size, and integrity
3. **OCR Analysis**: Text is extracted from images using OCR
4. **Filtering**: Images containing phone numbers or website URLs are filtered out
5. **Recognition**: Remaining images are analyzed using CLIP for content understanding
6. **Tagging**: Images are automatically tagged and categorized
7. **Upload**: Filtered images are uploaded to AWS S3
8. **Metadata Storage**: All metadata is stored in a local JSON database

### SEO Post Processing Workflow

1. **Content Analysis**: Post content is analyzed to understand topics and structure
2. **Image Matching**: AI finds the most relevant images from your database
3. **Smart Insertion**: Images are inserted at strategic positions in the content
4. **Format Handling**: Different insertion strategies for HTML vs. plain text
5. **Usage Tracking**: System tracks which images are used in which posts

### Image Recognition

The system uses OpenAI's CLIP model to understand image content:

- **Categories**: Images are classified into 20+ predefined categories (technology, business, food, etc.)
- **Tags**: Specific descriptive tags are generated (e.g., "laptop", "meeting", "outdoor")
- **Similarity Matching**: Semantic similarity is used to match images with post content

## Project Structure

```
teoteo/
├── streamlit_app.py                  # Streamlit web UI entry point
├── main.py                 # CLI entry point
├── config.py              # Configuration management
├── image_downloader.py    # Download images from URLs
├── image_filter.py        # OCR filtering for phone/website
├── image_recognizer.py    # AI-powered image analysis
├── aws_uploader.py        # AWS S3 integration
├── metadata_manager.py    # Metadata storage and retrieval
├── seo_post_manager.py    # SEO post processing
├── pages/                 # Web UI pages
│   ├── __init__.py
│   ├── home.py           # Home dashboard
│   ├── upload.py         # Image upload interface
│   ├── search.py         # Image search and gallery
│   ├── process_posts.py  # SEO post processing
│   ├── statistics.py     # Analytics dashboard
│   └── settings.py       # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
├── LICENSE              # MIT License
├── README.md            # This file
├── example_urls.csv     # Example CSV file
└── example_post.txt     # Example SEO post
```

## Examples

### Example 1: Upload Images and Process Posts

```bash
# Step 1: Upload images from CSV
python main.py upload example_urls.csv

# Step 2: Check what was uploaded
python main.py stats

# Step 3: Process your SEO posts
python main.py process ./my-blog-posts --output-dir ./enhanced-posts --num-images 3
```

### Example 2: Search and Reuse Images

```bash
# Find images about technology
python main.py search --category technology

# Find images with specific content
python main.py search --query "people working on computers"
```

## Troubleshooting

### Common Issues

**Issue**: EasyOCR fails to load
- **Solution**: Ensure you have enough RAM (minimum 4GB recommended) and a stable internet connection for first-time model download

**Issue**: AWS upload fails
- **Solution**:
  - Verify your AWS credentials in `.env`
  - Check that the S3 bucket exists and you have write permissions
  - Ensure the bucket allows public read access if you want images publicly accessible

**Issue**: No images found for SEO posts
- **Solution**:
  - Run `python main.py stats` to verify images are in the database
  - Upload more images using the `upload` command
  - Ensure images have diverse content matching your posts

**Issue**: Images contain phone numbers but aren't filtered
- **Solution**:
  - Try switching to `tesseract` OCR engine if using `easyocr`
  - Adjust phone number patterns in `config.py`

## Performance Considerations

- **OCR Processing**: Can be slow for large batches. EasyOCR is more accurate but slower than Tesseract
- **Image Recognition**: Requires downloading CLIP model (~350MB) on first run
- **Memory Usage**: CLIP model requires ~2GB RAM when loaded
- **Parallel Processing**: Currently sequential; can be parallelized for better performance

## Security Notes

- Never commit your `.env` file to version control
- Use IAM roles with minimum required S3 permissions
- Consider using AWS SSM Parameter Store for production credentials
- Regularly rotate your AWS access keys

## Future Enhancements

- [ ] Support for video frame extraction
- [ ] Multi-language OCR support
- [ ] Custom image classification models
- [ ] Batch processing parallelization
- [ ] Web interface for management
- [ ] Integration with popular CMS platforms
- [ ] Advanced duplicate detection
- [ ] Image quality assessment

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review this README thoroughly

## Acknowledgments

- OpenAI CLIP for image understanding
- EasyOCR for text detection
- AWS for reliable cloud storage
- The open-source community for various dependencies
