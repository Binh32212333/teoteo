# Deployment Guide

## Streamlit Cloud (Recommended for Quick Start)

### Step 1: Prepare Repository
Your code is already on GitHub - ready to deploy! ✅

### Step 2: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "Sign in with GitHub"
3. Click "New app"
4. Fill in the form:
   - **Repository**: `Binh32212333/teoteo`
   - **Branch**: `claude/continue-work-017CHbS5U6dANLYAFoyN6Bkh`
   - **Main file path**: `app.py`

5. Click "Advanced settings"
6. Add your secrets (copy from `.streamlit/secrets.toml.example`):
   ```toml
   AWS_ACCESS_KEY_ID = "your_actual_key"
   AWS_SECRET_ACCESS_KEY = "your_actual_secret"
   AWS_REGION = "us-east-1"
   AWS_S3_BUCKET = "your-actual-bucket"
   ```

7. Click "Deploy!"

### Step 3: Wait for Deployment
- First deployment takes ~2-5 minutes
- You'll get a URL like: `https://your-app.streamlit.app`

### Step 4: Test Your App
- Open the URL
- Go to Settings and verify AWS connection
- Upload test images

### Updates
Every time you push to GitHub, Streamlit Cloud automatically redeploys!

---

## AWS EC2 (For Production)

### Prerequisites
- AWS account
- EC2 instance (t2.medium recommended)
- Security group allowing ports 80, 443, 22

### Quick Setup Script

SSH into your EC2 instance and run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx git -y

# Clone repository
cd ~
git clone https://github.com/Binh32212333/teoteo.git
cd teoteo

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket
MAX_IMAGE_SIZE_MB=10
ALLOWED_IMAGE_FORMATS=jpg,jpeg,png,webp
OCR_ENGINE=easyocr
OCR_LANGUAGES=en
LOCAL_STORAGE_PATH=./storage/images
TEMP_DOWNLOAD_PATH=./temp
METADATA_DB_PATH=./storage/metadata.json
EOF

# Create systemd service
sudo tee /etc/systemd/system/streamlit.service > /dev/null << EOF
[Unit]
Description=Streamlit Image Management App
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/teoteo
Environment="PATH=$HOME/teoteo/venv/bin"
ExecStart=$HOME/teoteo/venv/bin/streamlit run app.py --server.port=8501 --server.address=localhost
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl start streamlit
sudo systemctl enable streamlit

# Configure Nginx
sudo tee /etc/nginx/sites-available/streamlit > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

echo "✅ Deployment complete!"
echo "🌐 Access your app at: http://$(curl -s ifconfig.me)"
```

### Optional: Add SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Heroku

### Setup Files

Create `Procfile`:
```
web: sh setup.sh && streamlit run app.py
```

Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/

echo "[server]
headless = true
port = $PORT
enableCORS = false
enableXsrfProtection = false
" > ~/.streamlit/config.toml
```

### Deploy

```bash
heroku login
heroku create your-app-name
heroku config:set AWS_ACCESS_KEY_ID=your_key
heroku config:set AWS_SECRET_ACCESS_KEY=your_secret
heroku config:set AWS_REGION=us-east-1
heroku config:set AWS_S3_BUCKET=your-bucket
git push heroku claude/continue-work-017CHbS5U6dANLYAFoyN6Bkh:main
```

---

## Troubleshooting

### App Won't Start
- Check logs: `streamlit logs` (Cloud) or `sudo journalctl -u streamlit -f` (EC2)
- Verify all dependencies installed
- Check Python version (3.8+)

### AWS Connection Failed
- Verify credentials in secrets/env
- Check S3 bucket exists and region matches
- Verify IAM permissions

### Memory Issues
- EasyOCR + CLIP models need ~2GB RAM
- Use at least t2.medium on EC2
- Consider switching to Tesseract for lighter memory usage

### Slow Performance
- First run downloads models (~2GB) - normal
- Subsequent runs much faster
- Consider caching strategies for production

---

## Cost Comparison

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| Streamlit Cloud | ✅ Free (1GB RAM) | N/A | Testing, personal use |
| Heroku | ✅ Free (512MB) | $7-25/mo | Small apps |
| AWS EC2 | ❌ ~$10/mo (t2.medium) | $10-100+/mo | Production |
| Google Cloud Run | ✅ Pay per use | ~$5-20/mo | Serverless |
| DigitalOcean | ✅ $200 credit | $5-12/mo | Managed hosting |

---

## Recommended Path

1. **Start**: Deploy to Streamlit Cloud (free, 5 minutes)
2. **Test**: Validate everything works
3. **Scale**: Move to AWS EC2 if needed
4. **Optimize**: Add CDN, caching, etc.
