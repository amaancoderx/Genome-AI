# OAuth Setup Guide for Social Media Posting

This guide will help you set up OAuth authentication for Instagram, Twitter (X), and LinkedIn to enable real social media posting from Pixaro.

## Overview

Currently, the content automation feature is in **DEMO MODE**. To enable real posting to social media platforms, you need to:

1. Register your application with each social media platform
2. Obtain API credentials (Client ID, Client Secret)
3. Implement OAuth 2.0 authentication flow
4. Store user access tokens securely
5. Use platform APIs to post content

---

## 1. Instagram (via Meta/Facebook)

### Step 1: Create a Meta App

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click **"My Apps"** → **"Create App"**
3. Select **"Business"** as the app type
4. Fill in app details:
   - App Name: "Pixaro Content Automation"
   - Contact Email: your email
   - Business Account: (select or create)

### Step 2: Add Instagram Graph API

1. In your app dashboard, go to **"Add Products"**
2. Find **"Instagram Graph API"** and click **"Set Up"**
3. Configure settings:
   - Add Instagram Business Account
   - Set up Instagram permissions

### Step 3: Get API Credentials

1. Go to **Settings** → **Basic**
2. Copy your:
   - **App ID** (Client ID)
   - **App Secret** (Client Secret)
3. Add to your `.env` file:

```env
META_APP_ID=your_app_id_here
META_APP_SECRET=your_app_secret_here
META_REDIRECT_URI=http://localhost:8000/api/auth/instagram/callback
```

### Step 4: Required Permissions

Request these permissions during OAuth:
- `instagram_basic`
- `instagram_content_publish`
- `pages_read_engagement`
- `pages_manage_posts`

### Step 5: Implementation Code

```python
# Add to market_genome_main.py

from fastapi import HTTPException
import requests

INSTAGRAM_AUTH_URL = "https://api.instagram.com/oauth/authorize"
INSTAGRAM_TOKEN_URL = "https://api.instagram.com/oauth/access_token"
INSTAGRAM_API_URL = "https://graph.instagram.com"

@app.get("/api/auth/instagram")
async def instagram_oauth():
    """Redirect user to Instagram OAuth page"""
    params = {
        "client_id": os.getenv("META_APP_ID"),
        "redirect_uri": os.getenv("META_REDIRECT_URI"),
        "scope": "instagram_basic,instagram_content_publish",
        "response_type": "code"
    }
    auth_url = f"{INSTAGRAM_AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    return {"auth_url": auth_url}

@app.get("/api/auth/instagram/callback")
async def instagram_callback(code: str, session_id: str):
    """Handle Instagram OAuth callback"""
    # Exchange code for access token
    response = requests.post(INSTAGRAM_TOKEN_URL, data={
        "client_id": os.getenv("META_APP_ID"),
        "client_secret": os.getenv("META_APP_SECRET"),
        "grant_type": "authorization_code",
        "redirect_uri": os.getenv("META_REDIRECT_URI"),
        "code": code
    })

    token_data = response.json()
    access_token = token_data.get("access_token")

    # Store token in session
    if session_id in chat_sessions:
        chat_sessions[session_id]['instagram_token'] = access_token

    return {"success": True, "message": "Instagram connected"}

async def post_to_instagram(access_token: str, image_url: str, caption: str):
    """Post content to Instagram"""
    # Step 1: Create media container
    container_response = requests.post(
        f"{INSTAGRAM_API_URL}/me/media",
        params={
            "image_url": image_url,
            "caption": caption,
            "access_token": access_token
        }
    )

    container_id = container_response.json().get("id")

    # Step 2: Publish media
    publish_response = requests.post(
        f"{INSTAGRAM_API_URL}/me/media_publish",
        params={
            "creation_id": container_id,
            "access_token": access_token
        }
    )

    return publish_response.json()
```

### Documentation
- [Instagram Graph API Docs](https://developers.facebook.com/docs/instagram-api)
- [Content Publishing Guide](https://developers.facebook.com/docs/instagram-api/guides/content-publishing)

---

## 2. Twitter (X)

### Step 1: Create Twitter App

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Sign up for a developer account (if needed)
3. Click **"Create Project"**
4. Fill in project details:
   - Project Name: "Pixaro"
   - Use Case: "Making a bot"
   - Description: "AI-powered content automation"

### Step 2: Get API Keys

1. Go to your app settings
2. Navigate to **"Keys and tokens"**
3. Generate and copy:
   - **API Key** (Client ID)
   - **API Key Secret** (Client Secret)
   - **Bearer Token**
4. Add to `.env`:

```env
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_REDIRECT_URI=http://localhost:8000/api/auth/twitter/callback
```

### Step 3: Enable OAuth 2.0

1. In app settings, go to **"User authentication settings"**
2. Enable **OAuth 2.0**
3. Set permissions: **Read and Write**
4. Add callback URL: `http://localhost:8000/api/auth/twitter/callback`

### Step 4: Implementation Code

```python
# Add to market_genome_main.py

import tweepy

TWITTER_AUTH_URL = "https://twitter.com/i/oauth2/authorize"
TWITTER_TOKEN_URL = "https://api.twitter.com/2/oauth2/token"

@app.get("/api/auth/twitter")
async def twitter_oauth():
    """Redirect user to Twitter OAuth page"""
    oauth2_user_handler = tweepy.OAuth2UserHandler(
        client_id=os.getenv("TWITTER_API_KEY"),
        redirect_uri=os.getenv("TWITTER_REDIRECT_URI"),
        scope=["tweet.read", "tweet.write", "users.read"],
        client_secret=os.getenv("TWITTER_API_SECRET")
    )
    auth_url = oauth2_user_handler.get_authorization_url()
    return {"auth_url": auth_url}

@app.get("/api/auth/twitter/callback")
async def twitter_callback(code: str, session_id: str):
    """Handle Twitter OAuth callback"""
    oauth2_user_handler = tweepy.OAuth2UserHandler(
        client_id=os.getenv("TWITTER_API_KEY"),
        redirect_uri=os.getenv("TWITTER_REDIRECT_URI"),
        scope=["tweet.read", "tweet.write", "users.read"],
        client_secret=os.getenv("TWITTER_API_SECRET")
    )

    access_token = oauth2_user_handler.fetch_token(code)

    # Store token in session
    if session_id in chat_sessions:
        chat_sessions[session_id]['twitter_token'] = access_token

    return {"success": True, "message": "Twitter connected"}

async def post_to_twitter(access_token: str, text: str, image_path: str = None):
    """Post content to Twitter"""
    client = tweepy.Client(bearer_token=access_token)

    if image_path:
        # Upload media first
        auth = tweepy.OAuth1UserHandler(
            os.getenv("TWITTER_API_KEY"),
            os.getenv("TWITTER_API_SECRET")
        )
        api = tweepy.API(auth)
        media = api.media_upload(filename=image_path)

        # Create tweet with media
        response = client.create_tweet(text=text, media_ids=[media.media_id])
    else:
        response = client.create_tweet(text=text)

    return response.data
```

### Install Required Package

```bash
pip install tweepy
```

### Documentation
- [Twitter API v2 Docs](https://developer.twitter.com/en/docs/twitter-api)
- [Tweepy Documentation](https://docs.tweepy.org/)

---

## 3. LinkedIn

### Step 1: Create LinkedIn App

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Click **"Create App"**
3. Fill in app details:
   - App Name: "Pixaro Content Automation"
   - LinkedIn Page: (create or select a page)
   - Privacy Policy URL: your website
   - App Logo: upload logo

### Step 2: Get API Credentials

1. In app settings, go to **"Auth"** tab
2. Copy:
   - **Client ID**
   - **Client Secret**
3. Add authorized redirect URL: `http://localhost:8000/api/auth/linkedin/callback`
4. Add to `.env`:

```env
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/auth/linkedin/callback
```

### Step 3: Request API Access

1. Go to **"Products"** tab
2. Request access to:
   - **Sign In with LinkedIn**
   - **Share on LinkedIn**
   - **Marketing Developer Platform** (for posting)

### Step 4: Implementation Code

```python
# Add to market_genome_main.py

from linkedin_api import Linkedin
import requests

LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_API_URL = "https://api.linkedin.com/v2"

@app.get("/api/auth/linkedin")
async def linkedin_oauth():
    """Redirect user to LinkedIn OAuth page"""
    params = {
        "response_type": "code",
        "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
        "redirect_uri": os.getenv("LINKEDIN_REDIRECT_URI"),
        "scope": "r_liteprofile w_member_social"
    }
    auth_url = f"{LINKEDIN_AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    return {"auth_url": auth_url}

@app.get("/api/auth/linkedin/callback")
async def linkedin_callback(code: str, session_id: str):
    """Handle LinkedIn OAuth callback"""
    # Exchange code for access token
    response = requests.post(LINKEDIN_TOKEN_URL, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.getenv("LINKEDIN_REDIRECT_URI"),
        "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET")
    })

    token_data = response.json()
    access_token = token_data.get("access_token")

    # Store token in session
    if session_id in chat_sessions:
        chat_sessions[session_id]['linkedin_token'] = access_token

    return {"success": True, "message": "LinkedIn connected"}

async def post_to_linkedin(access_token: str, text: str, image_url: str = None):
    """Post content to LinkedIn"""
    # Get user profile
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_response = requests.get(f"{LINKEDIN_API_URL}/me", headers=headers)
    person_urn = profile_response.json().get("id")

    # Create post
    post_data = {
        "author": f"urn:li:person:{person_urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    if image_url:
        # Upload image first (additional steps required)
        post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
        # Add image upload logic here

    response = requests.post(
        f"{LINKEDIN_API_URL}/ugcPosts",
        headers={**headers, "Content-Type": "application/json"},
        json=post_data
    )

    return response.json()
```

### Install Required Package

```bash
pip install linkedin-api
```

### Documentation
- [LinkedIn API Docs](https://docs.microsoft.com/en-us/linkedin/)
- [Share on LinkedIn Guide](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/share-api)

---

## 4. Security Best Practices

### Store Tokens Securely

Never commit tokens to git. Use environment variables:

```python
# Add to .env (NEVER commit this file)
META_APP_ID=your_app_id
META_APP_SECRET=your_secret
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
LINKEDIN_CLIENT_ID=your_id
LINKEDIN_CLIENT_SECRET=your_secret
```

### Use Database for Production

Replace in-memory storage with a database:

```python
# Example with SQLite
import sqlite3

# Store tokens in database
def store_user_token(session_id, platform, access_token, refresh_token=None):
    conn = sqlite3.connect('pixaro.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO user_tokens
        (session_id, platform, access_token, refresh_token, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (session_id, platform, access_token, refresh_token, datetime.now()))
    conn.commit()
    conn.close()
```

### Refresh Tokens

Implement token refresh logic:

```python
async def refresh_access_token(platform, refresh_token):
    """Refresh expired access token"""
    if platform == "instagram":
        response = requests.post(INSTAGRAM_TOKEN_URL, data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": os.getenv("META_APP_ID"),
            "client_secret": os.getenv("META_APP_SECRET")
        })
        return response.json().get("access_token")
    # Add similar logic for other platforms
```

---

## 5. Update Content Scheduling Endpoint

Modify the `/api/content/schedule` endpoint to use real APIs:

```python
@app.post("/api/content/schedule")
async def schedule_content(
    background_tasks: BackgroundTasks,
    session_id: str = Form(...),
    platform: str = Form(...),
    content_text: str = Form(""),
    schedule_time: str = Form(""),
    image: Optional[UploadFile] = File(None)
):
    """Schedule content with real social media APIs"""

    try:
        session = chat_sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get access token for platform
        token_key = f"{platform}_token"
        access_token = session.get(token_key)

        if not access_token:
            raise HTTPException(
                status_code=401,
                detail=f"Please connect your {platform} account first"
            )

        # Save image if provided
        image_path = None
        if image:
            image_path = f"uploads/{uuid.uuid4()}_{image.filename}"
            with open(image_path, "wb") as f:
                f.write(await image.read())

        # Post immediately or schedule
        if not schedule_time:
            # Post now
            if platform == "instagram":
                result = await post_to_instagram(access_token, image_path, content_text)
            elif platform == "twitter":
                result = await post_to_twitter(access_token, content_text, image_path)
            elif platform == "linkedin":
                result = await post_to_linkedin(access_token, content_text, image_path)

            return {
                "success": True,
                "message": f"Posted to {platform} successfully!",
                "post_id": result.get("id")
            }
        else:
            # Schedule for later (use Celery or similar)
            background_tasks.add_task(schedule_post, platform, access_token, content_text, image_path, schedule_time)
            return {
                "success": True,
                "message": f"Content scheduled for {schedule_time}"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 6. Frontend Integration

Update chat_interface.html to handle OAuth flow:

```javascript
async function connectPlatform(platform) {
    try {
        // Get OAuth URL
        const response = await fetch(`/api/auth/${platform}?session_id=${sessionId}`);
        const data = await response.json();

        // Open OAuth popup
        const popup = window.open(
            data.auth_url,
            'oauth',
            'width=600,height=800'
        );

        // Listen for callback
        window.addEventListener('message', (event) => {
            if (event.data.platform === platform && event.data.success) {
                alert(`${platform} connected successfully!`);
                popup.close();
            }
        });
    } catch (error) {
        console.error('OAuth error:', error);
        alert('Failed to connect platform');
    }
}
```

---

## 7. Testing

### Test OAuth Flow

1. Start your server: `python start_simple.py`
2. Click connect button for a platform
3. Authorize the app
4. Verify token is stored
5. Try posting content

### Test API Posting

```python
# Test script
import requests

# Test Instagram post
response = requests.post('http://localhost:8000/api/content/schedule', data={
    'session_id': 'your_session_id',
    'platform': 'instagram',
    'content_text': 'Test post from Pixaro! 🚀',
    'schedule_time': ''  # Empty for immediate posting
})

print(response.json())
```

---

## 8. Required Dependencies

Update requirements.txt:

```txt
fastapi==0.115.0
uvicorn[standard]==0.32.1
python-multipart==0.0.20
pydantic==2.10.3
openai==1.57.2
requests==2.31.0
tweepy==4.14.0
linkedin-api==2.2.0
python-dotenv==1.0.0
sqlalchemy==2.0.23  # For database storage
celery==5.3.4  # For scheduling
redis==5.0.1  # For task queue
```

Install:
```bash
pip install -r requirements.txt
```

---

## Summary

You've now learned how to:
1. ✅ Register apps with Instagram, Twitter, and LinkedIn
2. ✅ Implement OAuth 2.0 authentication
3. ✅ Store and refresh access tokens securely
4. ✅ Post content to social media via APIs
5. ✅ Schedule posts for later
6. ✅ Handle errors and edge cases

For production deployment, consider:
- Use a proper database (PostgreSQL, MySQL)
- Implement rate limiting
- Add error handling and retries
- Use task queue (Celery) for scheduling
- Encrypt tokens in database
- Monitor API usage and quotas

**Next Steps:**
1. Register your apps on each platform
2. Add credentials to `.env` file
3. Test OAuth flow locally
4. Deploy to production with HTTPS (required for OAuth)

Need help? Check the official documentation for each platform linked above.
