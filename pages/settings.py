import streamlit as st
import os
from config import Config

def show():
    st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Configure your application settings</div>', unsafe_allow_html=True)

    # Tabs for different settings
    tab1, tab2, tab3 = st.tabs(["☁️ AWS Configuration", "🔧 Processing Settings", "ℹ️ System Info"])

    with tab1:
        show_aws_settings()

    with tab2:
        show_processing_settings()

    with tab3:
        show_system_info()


def show_aws_settings():
    """AWS configuration settings"""

    st.markdown("### AWS S3 Configuration")
    st.info("Configure your AWS credentials to enable image upload to S3")

    # Load current settings
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env_exists = os.path.exists(env_path)

    if env_exists:
        current_key = Config.AWS_ACCESS_KEY_ID or ""
        current_secret = Config.AWS_SECRET_ACCESS_KEY or ""
        current_region = Config.AWS_REGION or "us-east-1"
        current_bucket = Config.AWS_S3_BUCKET or ""
    else:
        current_key = ""
        current_secret = ""
        current_region = "us-east-1"
        current_bucket = ""

    # Form for AWS settings
    with st.form("aws_settings_form"):
        st.markdown("#### AWS Credentials")

        aws_key = st.text_input(
            "AWS Access Key ID",
            value=current_key,
            type="password",
            help="Your AWS access key ID"
        )

        aws_secret = st.text_input(
            "AWS Secret Access Key",
            value=current_secret,
            type="password",
            help="Your AWS secret access key"
        )

        col1, col2 = st.columns(2)

        with col1:
            aws_region = st.text_input(
                "AWS Region",
                value=current_region,
                help="e.g., us-east-1, eu-west-1"
            )

        with col2:
            aws_bucket = st.text_input(
                "S3 Bucket Name",
                value=current_bucket,
                help="Name of your S3 bucket"
            )

        submitted = st.form_submit_button("💾 Save AWS Configuration", use_container_width=True)

        if submitted:
            try:
                # Read existing .env or create new
                env_lines = []

                if env_exists:
                    with open(env_path, 'r') as f:
                        env_lines = f.readlines()

                # Update or add AWS settings
                settings = {
                    'AWS_ACCESS_KEY_ID': aws_key,
                    'AWS_SECRET_ACCESS_KEY': aws_secret,
                    'AWS_REGION': aws_region,
                    'AWS_S3_BUCKET': aws_bucket
                }

                new_env_lines = []
                updated_keys = set()

                # Update existing lines
                for line in env_lines:
                    if '=' in line and not line.strip().startswith('#'):
                        key = line.split('=')[0].strip()
                        if key in settings:
                            new_env_lines.append(f"{key}={settings[key]}\n")
                            updated_keys.add(key)
                        else:
                            new_env_lines.append(line)
                    else:
                        new_env_lines.append(line)

                # Add new keys
                for key, value in settings.items():
                    if key not in updated_keys:
                        new_env_lines.append(f"{key}={value}\n")

                # Write back
                with open(env_path, 'w') as f:
                    f.writelines(new_env_lines)

                st.success("✅ AWS configuration saved successfully!")
                st.info("🔄 Please restart the application for changes to take effect")

            except Exception as e:
                st.error(f"❌ Error saving configuration: {str(e)}")

    # Test connection
    st.markdown("---")
    st.markdown("#### Test AWS Connection")

    if st.button("🔍 Test S3 Connection"):
        if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
            st.warning("⚠️ Please configure AWS credentials first")
        else:
            try:
                from aws_uploader import AWSUploader

                with st.spinner("Testing connection..."):
                    uploader = AWSUploader()
                    bucket_exists = uploader.check_bucket_exists()

                    if bucket_exists:
                        st.success(f"✅ Successfully connected to S3 bucket: {Config.AWS_S3_BUCKET}")
                    else:
                        st.error(f"❌ S3 bucket '{Config.AWS_S3_BUCKET}' does not exist or is not accessible")

            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")


def show_processing_settings():
    """Image processing settings"""

    st.markdown("### Image Processing Configuration")

    # Current settings
    st.markdown("#### Current Settings")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"**Max Image Size**: {Config.MAX_IMAGE_SIZE_MB} MB")
        st.info(f"**OCR Engine**: {Config.OCR_ENGINE}")

    with col2:
        st.info(f"**Allowed Formats**: {', '.join(Config.ALLOWED_IMAGE_FORMATS)}")
        st.info(f"**OCR Languages**: {', '.join(Config.OCR_LANGUAGES)}")

    st.markdown("---")

    # Storage paths
    st.markdown("#### Storage Paths")

    st.code(f"""
Local Storage: {Config.LOCAL_STORAGE_PATH}
Temp Downloads: {Config.TEMP_DOWNLOAD_PATH}
Metadata DB: {Config.METADATA_DB_PATH}
    """)

    # Create directories
    if st.button("📁 Create/Verify Storage Directories"):
        try:
            Config.ensure_directories()
            st.success("✅ Storage directories created/verified successfully!")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    st.markdown("---")

    # Pattern configuration
    st.markdown("#### Detection Patterns")

    with st.expander("📞 Phone Number Patterns"):
        st.code("\n".join(Config.PHONE_PATTERNS))

    with st.expander("🌐 Website Patterns"):
        st.code("\n".join(Config.WEBSITE_PATTERNS))

    st.info("💡 To modify these patterns, edit the `config.py` file")


def show_system_info():
    """System information"""

    st.markdown("### System Information")

    # Python version
    import sys
    st.markdown(f"**Python Version**: {sys.version}")

    st.markdown("---")

    # Installed packages
    st.markdown("#### Key Dependencies")

    dependencies = {
        'streamlit': 'Web UI framework',
        'boto3': 'AWS SDK',
        'Pillow': 'Image processing',
        'easyocr': 'OCR engine',
        'transformers': 'AI models',
        'torch': 'Deep learning',
        'pandas': 'Data manipulation',
        'beautifulsoup4': 'HTML parsing'
    }

    for package, description in dependencies.items():
        try:
            import importlib
            mod = importlib.import_module(package.replace('-', '_'))
            version = getattr(mod, '__version__', 'installed')
            st.text(f"✅ {package}: {version} - {description}")
        except ImportError:
            st.text(f"❌ {package}: not installed - {description}")

    st.markdown("---")

    # Database info
    st.markdown("#### Database Information")

    from metadata_manager import MetadataManager

    metadata_manager = MetadataManager()

    if os.path.exists(metadata_manager.db_path):
        file_size = os.path.getsize(metadata_manager.db_path)
        file_size_kb = file_size / 1024

        st.info(f"**Database Path**: {metadata_manager.db_path}")
        st.info(f"**Database Size**: {file_size_kb:.2f} KB")
    else:
        st.warning("No database file exists yet")

    st.markdown("---")

    # Clear cache/data
    st.markdown("#### Maintenance")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Clear Temp Files", use_container_width=True):
            try:
                import shutil
                if os.path.exists(Config.TEMP_DOWNLOAD_PATH):
                    shutil.rmtree(Config.TEMP_DOWNLOAD_PATH)
                    Config.ensure_directories()
                    st.success("✅ Temp files cleared")
                else:
                    st.info("No temp files to clear")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    with col2:
        if st.button("🔄 Reload Configuration", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Cache cleared. Please restart for full reload.")

    st.markdown("---")

    # About
    st.markdown("#### About")

    st.markdown("""
    **Image Management & SEO Enhancement System**

    Version: 1.0

    A comprehensive solution for automated image management and SEO content enhancement.

    Features:
    - Automated image download and filtering
    - AI-powered image recognition and tagging
    - AWS S3 cloud storage
    - Intelligent SEO post enhancement
    - Advanced search and analytics

    For more information, see the README.md file.
    """)
