"""
Pixaro Brand AI Assistant - Personal Marketing Strategist
Provides real-time brand analysis, content generation, and strategic insights
"""

import os
import json
import base64
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI
from google import genai
from google.genai import types
from config import settings

class PixaroBrandAssistant:
    """
    Personal AI Brand Assistant that acts as a virtual marketing strategist.

    Features:
    - Continuous social handle analysis
    - On-demand strategy reports
    - Content & campaign generation
    - Predictive insights & what-if scenarios
    - Audience micro-personas
    - Competitor trend alerts
    """

    def __init__(self, brand_handle: str, brand_context: Optional[Dict] = None):
        """
        Initialize the AI assistant for a specific brand.

        Args:
            brand_handle: Social media handle or brand name
            brand_context: Pre-loaded brand DNA data (optional)
        """
        self.brand_handle = brand_handle
        self.brand_context = brand_context or {}
        self.openai_client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=30.0,  # Add 30 second timeout
            max_retries=2   # Retry only 2 times to fail faster
        )
        self.conversation_history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt with brand context."""

        # Detect if this is a Twitter/X account
        is_twitter = any(domain in self.brand_handle.lower() for domain in ['twitter.com/', 'x.com/'])
        platform = "Twitter/X" if is_twitter else "Instagram"
        platform_example = "twitter.com" if is_twitter else "instagram.com"

        base_prompt = f"""You are Pixaro Brand AI - a personal marketing strategist and brand assistant for {self.brand_handle}.

CRITICAL: This is a **{platform}** account. When providing:
- Competitor information: Use {platform} handles ONLY (e.g., @competitor on {platform_example})
- Links: Provide {platform_example} URLs ONLY
- Examples: All examples must be {platform}-specific
- Strategy: Tailor all advice for {platform} best practices

YOUR ROLE:
You are an expert marketing strategist with deep knowledge of this brand's DNA, audience, competitors, and content performance. You provide actionable, data-driven insights and create ready-to-use marketing content.

YOUR CAPABILITIES:
1. Brand Strategy - Analyze brand positioning, voice, and growth opportunities
2. Content Creation - Generate {platform} posts, captions, campaigns
3. Image Generation - Create professional visual content, post designs, and infographics using AI
4. Social Media Posting - Post content directly to Twitter/X (when connected)
5. Audience Insights - Explain audience segments, preferences, and behaviors
6. Competitor Analysis - Identify competitor weaknesses and market gaps on {platform}
7. Predictive Analytics - Forecast engagement, ROI, and campaign performance
8. Trend Alerts - Spot emerging trends and opportunities on {platform}
9. Report Generation - Create custom strategy reports on demand

CONTENT POSTING WORKFLOW:
When users upload content (image/video) and want to post it:
1. If {platform} is Twitter: Post directly (if connected)
2. Ask what caption/text they want (max 280 chars for Twitter)
3. Ask about hashtags (or suggest relevant ones)
4. Ask if they want to post now or schedule for later
5. If posting to Twitter and they're connected, post immediately
6. If not connected, guide them to connect their account first

YOUR PERSONALITY:
- Professional yet conversational
- Data-driven and strategic
- Creative and innovative
- Proactive with suggestions
- Direct and actionable

RESPONSE STYLE:
- Keep answers concise but comprehensive
- Always provide specific, actionable recommendations
- Use bullet points for clarity
- Include metrics and data when relevant
- Suggest next steps proactively
- ALWAYS use {platform} handles and URLs when giving competitor examples

"""

        # Add brand context if available
        if self.brand_context:
            brand_dna = self.brand_context.get('brand_dna', {})
            audience = self.brand_context.get('audience', {})
            competitors = self.brand_context.get('competitors', {})

            context_prompt = f"""
BRAND CONTEXT YOU KNOW:

Brand DNA:
- Tone: {brand_dna.get('tone', 'Professional, engaging')}
- Core Values: {', '.join(brand_dna.get('values', ['Innovation', 'Quality', 'Trust']))}
- Personality Traits: {', '.join(brand_dna.get('personality', ['Authentic', 'Bold', 'Creative']))}
- Brand Voice: {brand_dna.get('voice', 'Confident and approachable')}

Target Audience:
- Primary Demographics: {audience.get('demographics', 'Young professionals, 25-40')}
- Psychographics: {audience.get('psychographics', 'Tech-savvy, growth-minded')}
- Pain Points: {', '.join(audience.get('pain_points', ['Time management', 'Scaling challenges']))}
- Content Preferences: {', '.join(audience.get('content_prefs', ['Educational', 'Visual', 'Data-driven']))}

Competitors:
- Main Competitors: {', '.join(competitors.get('names', ['Competitor A', 'Competitor B']))}
- Market Position: {competitors.get('position', 'Growing challenger brand')}
- Unique Advantages: {', '.join(competitors.get('advantages', ['Innovation', 'Customer service']))}

"""
            base_prompt += context_prompt

        base_prompt += """
SPECIAL COMMANDS YOU RECOGNIZE:
- "generate report" or "send report" - Trigger PDF report generation
- "create content" or "generate post" - Create social media content
- "generate image" or "create photo" or "make a post photo" - Generate visual content using AI
- "analyze competitor" - Deep dive on competitor strategy
- "predict engagement" or "what if" - Run predictive scenarios
- "show personas" - Display audience micro-personas
- "weekly strategy" - Create week-long content plan

When users ask for images or visual content, you will automatically generate professional images using DALL-E 3.
When users ask these commands, provide the requested content immediately and ask if they want it emailed as a PDF report.

IMPORTANT INSTRUCTIONS FOR COMPETITOR ANALYSIS:
When users ask about competitors or request competitor lists with links, you MUST:
1. Provide 3-5 specific competitor names based on the brand's industry/niche
2. For each competitor, include their {platform} handle/username
3. Include their {platform_example} URL in full format
4. Format like this:

   **Competitor 1: CompanyName**
   - {platform}: @companyname on {platform_example}
   - Website: https://companyname.com
   - Key Strength: [what they do well]
   - Opportunity for you: [gap you can fill]

Example for cybersecurity brand on Twitter/X:
- **HackerOne**: @Hacker0x01 | https://twitter.com/Hacker0x01
- **Bugcrowd**: @Bugcrowd | https://twitter.com/Bugcrowd
- **Cobalt**: @CobaltIO | https://twitter.com/CobaltIO

Always provide actionable competitor intelligence with real {platform} handles and URLs.
Always be proactive - suggest what they should do next based on their questions.
"""

        return base_prompt

    def _detect_posting_intent(self, message: str) -> bool:
        """Detect if user wants to post content to Twitter"""
        posting_keywords = [
            'post this', 'upload this', 'tweet this', 'publish this',
            'post it', 'upload it', 'tweet it', 'share this',
            'post on', 'upload on', 'tweet on', 'post to',
            'post the', 'upload the', 'automate', 'schedule'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in posting_keywords)

    def _generate_caption(self, user_message: str, brand_context: str = "") -> str:
        """Generate caption for Twitter post using AI"""
        try:
            prompt = f"""Generate a compelling Twitter caption (max 200 characters) for this content.

Brand: {self.brand_handle}
{brand_context}

User request: {user_message}

Requirements:
- Professional and engaging
- Maximum 200 characters (leave room for hashtags)
- Relevant to the content
- Call-to-action if appropriate

Respond with ONLY the caption text, nothing else."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Much faster than turbo-preview
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=50  # Reduced for faster response
            )

            caption = response.choices[0].message.content.strip().strip('"').strip("'")
            return caption[:200]  # Enforce limit

        except Exception as e:
            # Fallback caption
            return "Check out this content!"

    def _generate_hashtags(self, user_message: str = "", brand_niche: str = "cybersecurity") -> str:
        """Generate relevant hashtags"""
        try:
            prompt = f"""Generate 3-5 relevant Twitter hashtags for a {brand_niche} brand.

Context: {user_message if user_message else 'General post'}

Requirements:
- Popular and relevant hashtags
- Mix of broad and specific
- No more than 5 hashtags
- Format: #hashtag1 #hashtag2 #hashtag3

Respond with ONLY the hashtags, space-separated."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Much faster
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=50
            )

            hashtags = response.choices[0].message.content.strip()
            return hashtags

        except Exception as e:
            # Fallback hashtags
            return "#CyberSecurity #InfoSec #Tech"

    def chat(self, user_message: str, uploaded_image_url: str = None) -> Dict:
        """
        Main chat interface - handles all user queries.

        Args:
            user_message: User's question or command
            uploaded_image_url: URL of uploaded image (if any)

        Returns:
            Dict with response, action_type, and metadata
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })

        # CHECK FOR POSTING INTENT FIRST!
        if uploaded_image_url and self._detect_posting_intent(user_message):
            # User wants to post! Generate caption and hashtags
            print(f"\nPosting intent detected!")
            print(f"   Message: {user_message[:50]}...")
            print(f"   Image: {uploaded_image_url}")

            # Generate caption and hashtags
            caption = self._generate_caption(user_message)
            hashtags = self._generate_hashtags(user_message)

            # Combine
            full_text = f"{caption}\n\n{hashtags}"

            # Ensure it's under 280 characters
            if len(full_text) > 280:
                full_text = caption[:250] + "\n\n" + hashtags

            response_message = f"I'll post this to your Twitter right now!\n\nCaption: {caption}\n\nHashtags: {hashtags}\n\nPosting..."

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_message,
                "timestamp": datetime.now().isoformat()
            })

            return {
                "response": response_message,
                "action_type": "post_to_twitter",
                "needs_posting": True,
                "post_data": {
                    "text": full_text,
                    "image_url": uploaded_image_url
                },
                "timestamp": datetime.now().isoformat()
            }

        # Check for special commands
        action_type = self._detect_action_type(user_message)

        # Handle image generation requests
        if action_type == "generate_image":
            # Extract the image description from the user message
            image_result = self.generate_image(user_message)

            if image_result.get("success"):
                assistant_response = f"I've generated an image for you! Here's what I created:\n\n{image_result.get('prompt')}\n\nWould you like me to create another variation or adjust anything?"

                # Add to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_response,
                    "timestamp": datetime.now().isoformat(),
                    "image_url": image_result.get("image_url")
                })

                return {
                    "response": assistant_response,
                    "action_type": action_type,
                    "needs_report": False,
                    "image_url": image_result.get("image_url"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Return error response immediately without continuing to normal chat
                error_msg = image_result.get('error', 'Unknown error occurred')
                assistant_response = f"Sorry, I encountered an error generating the image: {error_msg}\n\nPlease try again with a different description or let me know how else I can help you!"

                # Add error to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_response,
                    "timestamp": datetime.now().isoformat()
                })

                return {
                    "response": assistant_response,
                    "action_type": "error",
                    "needs_report": False,
                    "timestamp": datetime.now().isoformat()
                }

        # Build messages for OpenAI
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            *[{"role": msg["role"], "content": msg["content"]}
              for msg in self.conversation_history]
        ]

        # Get AI response - Using GPT-4o (much faster than turbo-preview!)
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Changed from gpt-4-turbo-preview for 2-3x speed boost
                messages=messages,
                temperature=0.7,
                max_tokens=1000  # Reduced from 1500 for faster responses
            )

            assistant_response = response.choices[0].message.content

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_response,
                "timestamp": datetime.now().isoformat()
            })

            return {
                "response": assistant_response,
                "action_type": action_type,
                "needs_report": "report" in user_message.lower() and ("generate" in user_message.lower() or "send" in user_message.lower()),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            error_response = f"I encountered an error: {str(e)}. Let me try to help you anyway. What would you like to know about {self.brand_handle}?"
            return {
                "response": error_response,
                "action_type": "error",
                "needs_report": False,
                "timestamp": datetime.now().isoformat()
            }

    def _detect_action_type(self, message: str) -> str:
        """Detect what type of action the user is requesting."""
        message_lower = message.lower()

        # Image generation - check this FIRST and be more flexible with detection
        if any(phrase in message_lower for phrase in [
            "create a image", "create an image", "generate a image", "generate an image",
            "generate image", "make image", "make a image", "make an image",
            "create a photo", "create photo", "generate a photo", "generate photo", "make photo",
            "design a post", "design post", "create visual", "generate visual",
            "make a post photo", "create post image", "image of", "photo of",
            "image about", "photo about", "picture of", "picture about",
            "graphic about", "graphic of", "design about"
        ]):
            return "generate_image"
        elif any(word in message_lower for word in ["generate report", "send report", "create report", "email report"]):
            return "generate_report"
        elif any(word in message_lower for word in ["generate post", "create caption", "write post", "generate content"]):
            return "generate_content"
        elif any(word in message_lower for word in ["competitor", "competition", "rival"]):
            return "competitor_analysis"
        elif any(word in message_lower for word in ["predict", "forecast", "what if", "scenario"]):
            return "predictive_analysis"
        elif any(word in message_lower for word in ["persona", "audience segment", "who is"]):
            return "audience_insights"
        elif any(word in message_lower for word in ["campaign", "strategy", "plan"]):
            return "campaign_creation"
        else:
            return "general_chat"

    def generate_image(self, prompt: str, size: str = "1024x1024") -> Dict:
        """
        Generate an image using DALL-E 3 based on the user's description.

        Args:
            prompt: Description of the image to generate
            size: Image size (1024x1024, 1024x1792, or 1792x1024)

        Returns:
            Dict with image_url and prompt
        """
        try:
            # Enhance the prompt with brand context if available
            brand_context_str = ""
            if self.brand_context:
                brand_dna = self.brand_context.get('brand_dna', {})
                tone = brand_dna.get('tone', 'professional')
                values = brand_dna.get('values', [])
                brand_context_str = f" The style should be {tone}"
                if values:
                    brand_context_str += f" and reflect values of {', '.join(values[:2])}"

            enhanced_prompt = f"{prompt}.{brand_context_str}. High quality, professional social media post design."

            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size=size,
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url

            return {
                "image_url": image_url,
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }

        except Exception as e:
            # Log the actual error for debugging
            print(f"[IMAGE ERROR] {str(e)}")

            # Provide more specific error messages
            error_str = str(e).lower()
            if "billing" in error_str or "quota" in error_str or "insufficient_quota" in error_str:
                error_message = "Image generation quota exceeded. Please check your OpenAI billing settings."
            elif "api_key" in error_str or "authentication" in error_str or "invalid_api_key" in error_str:
                error_message = "API authentication failed. Please verify your OpenAI API key."
            elif "content_policy" in error_str or "safety" in error_str or "rejected" in error_str:
                error_message = "I can't generate images of real people (like politicians or celebrities) due to content policy. Please try describing a fictional character, a scene, or an abstract concept instead!"
            elif "timeout" in error_str:
                error_message = "Image generation timed out. Please try again."
            elif "rate_limit" in error_str:
                error_message = "Too many requests. Please wait a moment and try again."
            else:
                error_message = f"Image generation failed: {str(e)}"

            return {
                "error": error_message,
                "prompt": prompt,
                "success": False,
                "timestamp": datetime.now().isoformat()
            }

    def generate_instagram_posts(self, topic: str, count: int = 5) -> List[Dict]:
        """
        Generate ready-to-use Instagram posts with captions.

        Args:
            topic: Topic or theme for posts
            count: Number of posts to generate

        Returns:
            List of post dicts with caption, hashtags, best_time
        """
        prompt = f"""Create {count} Instagram post captions for {self.brand_handle} about: {topic}

For each post, provide:
1. Engaging caption (150-200 characters)
2. Relevant hashtags (5-8 hashtags)
3. Best posting time
4. Content type suggestion (carousel, reel, static image)

Make sure captions match the brand voice and tone. Include call-to-actions."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )

            content = response.choices[0].message.content

            # Parse the response into structured posts
            posts = self._parse_instagram_posts(content)
            return posts

        except Exception as e:
            return [{"error": str(e), "caption": "Error generating posts"}]

    def _parse_instagram_posts(self, ai_response: str) -> List[Dict]:
        """Parse AI response into structured post objects."""
        posts = []
        lines = ai_response.split('\n')

        current_post = {}
        for line in lines:
            line = line.strip()
            if line.startswith('Post ') or line.startswith('**Post'):
                if current_post:
                    posts.append(current_post)
                current_post = {}
            elif 'caption:' in line.lower():
                current_post['caption'] = line.split(':', 1)[1].strip()
            elif 'hashtag' in line.lower():
                current_post['hashtags'] = line.split(':', 1)[1].strip()
            elif 'time' in line.lower() or 'posting' in line.lower():
                current_post['best_time'] = line.split(':', 1)[1].strip()
            elif 'type' in line.lower():
                current_post['content_type'] = line.split(':', 1)[1].strip()

        if current_post:
            posts.append(current_post)

        return posts if posts else [{"caption": ai_response, "hashtags": "", "best_time": "Peak hours", "content_type": "Static"}]

    def predict_engagement(self, content_idea: str, platform: str = "Instagram") -> Dict:
        """
        Predict engagement for a content idea.

        Args:
            content_idea: Description of the content
            platform: Social media platform

        Returns:
            Dict with predicted metrics and recommendations
        """
        prompt = f"""Analyze this content idea for {platform}: "{content_idea}"

Provide predictions for:
1. Engagement Rate (estimate %)
2. Expected Reach (Low/Medium/High)
3. Audience Sentiment (Positive/Neutral/Negative)
4. Viral Potential Score (1-10)
5. Best Day/Time to Post
6. Recommendations to improve engagement

Base predictions on brand DNA and typical audience behavior for {self.brand_handle}."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )

            content = response.choices[0].message.content

            return {
                "prediction": content,
                "content_idea": content_idea,
                "platform": platform,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e), "prediction": "Unable to generate prediction"}

    def create_campaign(self, goal: str, duration: str = "1 month", budget: str = "Medium") -> Dict:
        """
        Create a complete marketing campaign.

        Args:
            goal: Campaign objective
            duration: Campaign length
            budget: Budget level (Low/Medium/High)

        Returns:
            Dict with complete campaign strategy
        """
        prompt = f"""Create a complete marketing campaign for {self.brand_handle}:

Goal: {goal}
Duration: {duration}
Budget: {budget}

Provide:
1. Campaign Overview (objectives, KPIs)
2. Target Audience Segments
3. Content Calendar (week-by-week breakdown)
4. Channel Strategy (which platforms, why)
5. Creative Concepts (3-5 content ideas)
6. Budget Allocation
7. Success Metrics
8. Risk Mitigation

Make it actionable and specific to the brand's DNA and audience."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )

            campaign = response.choices[0].message.content

            return {
                "campaign": campaign,
                "goal": goal,
                "duration": duration,
                "budget": budget,
                "created": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e), "campaign": "Unable to generate campaign"}

    def analyze_competitor(self, competitor_name: str) -> Dict:
        """
        Deep dive competitor analysis.

        Args:
            competitor_name: Name or handle of competitor

        Returns:
            Dict with competitor insights and opportunities
        """
        prompt = f"""Analyze competitor: {competitor_name} for {self.brand_handle}

Provide:
1. Content Strategy Analysis
   - What are they posting?
   - Posting frequency and timing
   - Engagement patterns

2. Strengths & Weaknesses
   - What are they doing well?
   - What are their gaps?

3. Opportunities for {self.brand_handle}
   - Content gaps we can fill
   - Underserved audience segments
   - Better positioning angles

4. Actionable Recommendations
   - 3 things we should do differently
   - 2 things we should learn from them
   - 1 bold move to differentiate

Be specific and actionable."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            analysis = response.choices[0].message.content

            return {
                "analysis": analysis,
                "competitor": competitor_name,
                "brand": self.brand_handle,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e), "analysis": "Unable to analyze competitor"}

    def get_audience_personas(self) -> Dict:
        """
        Get detailed audience micro-personas.

        Returns:
            Dict with 4 detailed personas
        """
        prompt = f"""Create 4 detailed audience micro-personas for {self.brand_handle}:

For each persona, provide:
1. Name & Age (e.g., "Sarah, 28")
2. Job Title & Industry
3. Key Characteristics (3-4 traits)
4. Pain Points (2-3 specific problems)
5. Content Preferences (what they engage with)
6. Best Way to Reach Them (channel + message type)
7. Engagement Behavior (when/how they interact)

Make them realistic and actionable for targeted marketing."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            personas = response.choices[0].message.content

            return {
                "personas": personas,
                "brand": self.brand_handle,
                "created": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e), "personas": "Unable to generate personas"}

    def weekly_content_strategy(self) -> Dict:
        """
        Generate a week-long content strategy.

        Returns:
            Dict with day-by-day content plan
        """
        prompt = f"""Create a 7-day content strategy for {self.brand_handle}:

For each day (Monday-Sunday), provide:
1. Content Theme/Topic
2. Platform (Instagram/LinkedIn/Twitter/etc.)
3. Content Format (Reel/Carousel/Story/Post)
4. Caption Template (with hashtags)
5. Best Posting Time
6. CTA (call-to-action)

Make sure there's variety in content types and themes. Align with brand DNA and audience preferences."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )

            strategy = response.choices[0].message.content

            return {
                "weekly_plan": strategy,
                "brand": self.brand_handle,
                "created": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e), "weekly_plan": "Unable to generate strategy"}

    def get_conversation_history(self) -> List[Dict]:
        """Get full conversation history."""
        return self.conversation_history

    def clear_conversation(self):
        """Clear conversation history for new session."""
        self.conversation_history = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def export_conversation(self, filepath: str = None) -> str:
        """
        Export conversation to JSON file.

        Args:
            filepath: Optional custom filepath

        Returns:
            Path to exported file
        """
        if not filepath:
            filepath = f"conversations/conversation_{self.brand_handle}_{self.session_id}.json"

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        export_data = {
            "brand_handle": self.brand_handle,
            "session_id": self.session_id,
            "conversation": self.conversation_history,
            "brand_context": self.brand_context,
            "exported_at": datetime.now().isoformat()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return filepath
