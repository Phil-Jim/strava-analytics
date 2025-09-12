# DigitalOcean Deployment Guide - Low Volume Test Site

**Perfect for: Less than 100 hits/week, testing, personal use**
**Total Monthly Cost: $5-7**

This guide is specifically tailored for deploying your Strava Analytics app on DigitalOcean's most cost-effective options.

## Cost Breakdown (Monthly)
- **DigitalOcean App Platform (Basic)**: $5/month
- **Managed PostgreSQL (Basic)**: $15/month ❌ (too expensive)
- **Alternative: App Platform with SQLite**: $5/month ✅ (recommended for low volume)

## Quick Start (15 minutes to live site)

First, let's create the necessary files:

```bash
# 1. Create requirements.txt
pip freeze > requirements.txt

# 2. Create runtime.txt (specify Python version)
echo "python-3.12.0" > runtime.txt

# 3. Add gunicorn to requirements
echo "gunicorn==21.2.0" >> requirements.txt
```

### Step 2: Create DigitalOcean App Spec (2 minutes)

Create `.do/app.yaml` in your project root:

```yaml
name: strava-analytics-test
services:
- name: web
  source_dir: /
  github:
    repo: your-username/your-repo-name
    branch: main
  run_command: |
    python manage.py migrate
    python manage.py collectstatic --noinput
    gunicorn strava_analytics.wsgi:application --bind 0.0.0.0:$PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8080
  envs:
  - key: DEBUG
    value: "False"
  - key: DJANGO_SECRET_KEY
    value: "your-very-long-random-secret-key-here-change-this"
  - key: ALLOWED_HOSTS
    value: ".ondigitalocean.app"
  - key: STRAVA_CLIENT_ID
    value: "176560"
  - key: STRAVA_CLIENT_SECRET
    value: "5dedff302150ac96088259de5e2f28fb37c9e16d"
  - key: STRAVA_ACCESS_TOKEN
    value: "cc5a6c0eca66a8392c4f69d85a040c59c44e162e"
  - key: STRAVA_REFRESH_TOKEN
    value: "b6d677327d7f25eca8f142c0967e3d6abbc74fe7"
  - key: FACEBOOK_CLIENT_ID
    value: "1529630181550200"
  - key: FACEBOOK_CLIENT_SECRET
    value: "93a7949d5cf01c1cd97da274499881bb"
  - key: GOOGLE_CLIENT_ID
    value: "your-google-client-id-here"
  - key: GOOGLE_CLIENT_SECRET
    value: "your-google-client-secret-here"
```

**Cost: $5/month (Basic XXS instance)**

### Step 3: Update Django Settings for Production (3 minutes)

Add this to your `settings.py`:

```python
import os
from pathlib import Path

# Production settings
if not os.getenv('DEBUG', 'False').lower() == 'true':
    DEBUG = False
    
    # Use environment variable for secret key
    SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-ux^p(+vxwi8a+=+xe9b-=wvxudg+0yaz6^$5jkjoh94o*mud^s')
    
    # Allow DigitalOcean App Platform domains
    ALLOWED_HOSTS = [
        '.ondigitalocean.app',
        'localhost',
        '127.0.0.1'
    ]
    
    # Keep SQLite for low volume (saves $15/month vs PostgreSQL)
    # For 100 hits/week, SQLite is perfectly fine
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    
    # HTTPS and Security (DigitalOcean provides SSL automatically)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Static files
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATIC_URL = '/static/'
    
    # Logging (helpful for debugging)
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
            },
        },
    }
```

### Step 4: Deploy to DigitalOcean (5 minutes)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for DigitalOcean deployment"
   git push origin main
   ```

2. **Create DigitalOcean Account:**
   - Go to [digitalocean.com](https://digitalocean.com)
   - Sign up (get $200 credit with GitHub Student Pack)
   - Verify email

3. **Deploy App:**
   - Click "Create" → "Apps"
   - Connect GitHub account
   - Select your repository
   - DigitalOcean will auto-detect the `app.yaml` file
   - Review settings (should show $5/month Basic XXS)
   - Click "Create Resources"
   - Wait 5-10 minutes for deployment

4. **Get Your App URL:**
   - Your app will be live at: `https://your-app-name-xxxxx.ondigitalocean.app`

### Step 5: Update Social Authentication (5 minutes)

**Update Facebook App:**
1. Go to [Facebook Developers Console](https://developers.facebook.com/apps/1529630181550200/)
2. Facebook Login → Settings
3. **Update Valid OAuth Redirect URIs:**
   ```
   https://your-app-name-xxxxx.ondigitalocean.app/accounts/facebook/login/callback/
   ```
4. Settings → Basic → **App Domains:**
   ```
   your-app-name-xxxxx.ondigitalocean.app
   ```

**Update Google (if configured):**
1. [Google Console](https://console.cloud.google.com/apis/credentials)
2. Edit OAuth client → **Authorized redirect URIs:**
   ```
   https://your-app-name-xxxxx.ondigitalocean.app/accounts/google/login/callback/
   ```

## Testing Your Live Site

Visit: `https://your-app-name-xxxxx.ondigitalocean.app`

Test the flow:
1. Click "Continue with Facebook" ✅
2. Should redirect to Strava after Facebook login ✅  
3. Authorize Strava ✅
4. See your activity data ✅

## Monthly Cost Breakdown

| Service | Cost | Why This Choice |
|---------|------|----------------|
| **DigitalOcean App Platform (Basic XXS)** | $5.00 | Perfect for <100 hits/week |
| **SSL Certificate** | Free | Included automatically |
| **Database** | Free | SQLite (stored with app) |
| **Domain** | $0-12/year | `.ondigitalocean.app` subdomain free |
| **Total** | **$5.00/month** | **Most cost-effective for testing** |

## Why This Setup is Perfect for Low Volume:

✅ **SQLite is fine for <100 hits/week** - Saves $15/month vs managed PostgreSQL  
✅ **Basic XXS instance** - 0.5GB RAM, sufficient for personal use  
✅ **Free SSL** - DigitalOcean provides automatic HTTPS  
✅ **Auto-scaling** - Sleeps when not in use (saves resources)  
✅ **Easy updates** - Just push to GitHub, auto-deploys  

## Scaling Up Later (When You Need It)

If you get more traffic later, easy upgrades:
- **Basic XS** ($12/month) - 1GB RAM, better performance
- **Add PostgreSQL** (+$15/month) - When you need concurrent users
- **Custom domain** (+$10-15/year) - yourdomain.com instead of .ondigitalocean.app

## Troubleshooting

**Check logs:**
```bash
# Install DigitalOcean CLI
curl -OL https://github.com/digitalocean/doctl/releases/download/v1.94.0/doctl-1.94.0-linux-amd64.tar.gz
tar xf doctl-*-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin

# View logs
doctl apps logs <your-app-id> --follow
```

**Common issues:**
- **Build fails**: Check `requirements.txt` has all dependencies
- **Facebook login fails**: Verify redirect URI matches exactly
- **Static files missing**: Ensure `STATIC_ROOT` is set correctly

## Next Steps After Deployment

1. **Create superuser account:**
   - Add a run command in app.yaml: `python manage.py createsuperuser`
   - Or access via Django shell in DigitalOcean console

2. **Monitor usage:**
   - DigitalOcean provides usage metrics
   - Set up billing alerts

3. **Test thoroughly:**
   - Test all authentication flows
   - Verify Strava data sync works
   - Check mobile responsiveness

**Your site is now live for just $5/month!** 🎉