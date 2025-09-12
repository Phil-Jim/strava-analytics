# Social Authentication Setup Guide

This guide explains how to configure Google, Facebook, and Apple social authentication for the Strava Analytics application.

## Facebook App Setup

### 1. Create Facebook App
1. Go to [Facebook Developers](https://developers.facebook.com/apps/)
2. Click "Create App"
3. Select "Consumer" as app type
4. Fill in:
   - **App Name**: "Strava Analytics" (or your preferred name)
   - **App Contact Email**: Your email address
   - **Purpose**: Choose "Yourself or your own business"

### 2. Configure Facebook Login
1. In your Facebook app dashboard, go to "Add a Product"
2. Find "Facebook Login" and click "Set Up"
3. Choose "Web" platform
4. Enter Site URL: `http://localhost:8000` (for development)
5. Go to Facebook Login → Settings
6. Add Valid OAuth Redirect URIs:
   ```
   http://localhost:8000/accounts/facebook/login/callback/
   ```

### 3. Get App Credentials
1. Go to Settings → Basic
2. Copy your **App ID** and **App Secret**
3. Update your `.env` file:
   ```
   FACEBOOK_CLIENT_ID=your-app-id-here
   FACEBOOK_CLIENT_SECRET=your-app-secret-here
   ```

### 4. App Review (Production)
For production use, you'll need to submit your app for review to access user emails.

---

## Google OAuth Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Name: "Strava Analytics" (or your preferred name)

### 2. Enable Google+ API
1. Go to "APIs & Services" → "Library"
2. Search for "Google+ API" and enable it
3. Also enable "People API" for better profile access

### 3. Create OAuth Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Web application"
4. Fill in:
   - **Name**: "Strava Analytics Web Client"
   - **Authorized JavaScript origins**: `http://localhost:8000`
   - **Authorized redirect URIs**: `http://localhost:8000/accounts/google/login/callback/`

### 4. Get Credentials
1. Copy your **Client ID** and **Client Secret**
2. Update your `.env` file:
   ```
   GOOGLE_CLIENT_ID=your-client-id-here.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   ```

---

## Apple Sign In Setup

### 1. Apple Developer Account
You need a paid Apple Developer account ($99/year) to use Sign in with Apple.

### 2. Create App ID
1. Go to [Apple Developer](https://developer.apple.com/account/)
2. Go to "Certificates, Identifiers & Profiles" → "Identifiers"
3. Create new App ID:
   - **Description**: "Strava Analytics"
   - **Bundle ID**: `com.yourcompany.stravaanalytics` (reverse domain)
   - Enable "Sign In with Apple"

### 3. Create Service ID
1. Create new identifier → "Services IDs"
2. Fill in:
   - **Description**: "Strava Analytics Web"
   - **Identifier**: `com.yourcompany.stravaanalytics.web`
   - Enable "Sign In with Apple"
   - Configure domains: `localhost` (for development)
   - Return URLs: `http://localhost:8000/accounts/apple/login/callback/`

### 4. Create Private Key
1. Go to "Keys" section
2. Create new key for "Sign in with Apple"
3. Download the `.p8` file (keep it secure!)
4. Note the Key ID

### 5. Get Credentials
Update your `.env` file:
```
APPLE_CLIENT_ID=com.yourcompany.stravaanalytics.web
APPLE_CLIENT_SECRET=your-generated-jwt-secret
APPLE_KEY_ID=your-key-id-here
APPLE_TEAM_ID=your-team-id-here
```

**Note**: Apple Client Secret is a JWT token you need to generate using your private key.

---

## Testing the Setup

### 1. Restart Django Server
After updating your `.env` file:
```bash
python3 manage.py runserver 8000
```

### 2. Test Login Page
1. Go to `http://localhost:8000/accounts/login/`
2. You should see social login buttons for configured providers
3. If credentials are missing, you'll see setup instructions instead

### 3. Test Social Login Flow
1. Click a social login button
2. Complete OAuth flow on provider's site
3. Should redirect back to Strava Analytics
4. Should automatically redirect to Strava connection

---

## Production Deployment

### Domain Configuration
For production, update all redirect URIs to use your actual domain:
- `https://yourdomain.com/accounts/google/login/callback/`
- `https://yourdomain.com/accounts/facebook/login/callback/`
- `https://yourdomain.com/accounts/apple/login/callback/`

### Security
- Keep all secrets secure and never commit to version control
- Use environment variables or secure secret management
- Enable HTTPS for all production OAuth flows
- Consider implementing additional security measures like CSRF protection

---

## Troubleshooting

### Facebook "Invalid App ID"
- Double-check App ID in .env file
- Ensure app is not in development mode restrictions
- Verify redirect URI matches exactly

### Google "OAuth Error"
- Check if APIs are enabled in Google Cloud Console
- Verify redirect URI format and spelling
- Ensure JavaScript origins are configured

### Apple Sign In Issues
- Verify Service ID configuration
- Check domain and return URL settings
- Ensure JWT secret generation is correct

### General Issues
- Restart Django server after .env changes
- Check Django logs for detailed error messages
- Verify internet connectivity for OAuth callbacks