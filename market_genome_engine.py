"""
Market Genome Engine - Core AI Analysis System
Scrapes, analyzes, and generates marketing strategy from brand data
"""

import os
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
from openai import OpenAI
from config import settings
import json
import importlib
import sys


class MarketGenomeEngine:
    """
    Core engine for Market Genome analysis

    Capabilities:
    - Multi-source data scraping (web, social, reviews)
    - AI-powered brand DNA extraction
    - Competitor intelligence
    - Strategic roadmap generation
    """

    def __init__(self):
        self.openai_client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=45.0,  # 45 second timeout for analysis tasks
            max_retries=2   # Retry only 2 times
        ) if settings.openai_api_key else None

        if not self.openai_client:
            raise ValueError("OpenAI API key required for Market Genome analysis")

    def collect_brand_data(self, brand_input: str, input_type: str = "auto") -> Dict:
        """
        Collect brand data from multiple sources

        Args:
            brand_input: Brand name, URL, or social handle
            input_type: Type of input (auto-detected)

        Returns:
            Comprehensive brand data dictionary
        """

        print(f"   Collecting data for: {brand_input}")

        brand_data = {
            'brand_input': brand_input,
            'brand_name': '',
            'website_data': {},
            'social_data': {},
            'review_data': {},
            'industry': '',
            'target_audience': ''
        }

        # Detect input type
        if input_type == "auto":
            input_type = self._detect_input_type(brand_input)

        print(f"   Detected type: {input_type}")

        # Scrape based on type
        if input_type == "website":
            brand_data['website_data'] = self._scrape_website(brand_input)
            brand_data['brand_name'] = brand_data['website_data'].get('title', brand_input)

        elif input_type in ["instagram", "twitter", "linkedin"]:
            brand_data['social_data'] = self._scrape_social(brand_input, input_type)
            brand_data['brand_name'] = brand_input.replace('@', '')

        else:  # brand_name
            brand_data['brand_name'] = brand_input
            # Search for brand website
            website_url = self._find_brand_website(brand_input)
            if website_url:
                brand_data['website_data'] = self._scrape_website(website_url)

        print(f"   SUCCESS - Data collected for: {brand_data['brand_name']}")

        return brand_data

    def analyze_brand_dna(self, brand_data: Dict) -> Dict:
        """
        Extract brand DNA using AI analysis

        Analyzes:
        - Brand personality (tone, voice, values)
        - Positioning (how they position themselves)
        - Target audience
        - Unique value proposition
        - Visual identity

        Returns:
            Brand DNA dictionary
        """

        print(f"   Analyzing brand DNA...")

        # Prepare context for AI
        context = self._prepare_brand_context(brand_data)

        # AI Analysis
        system_prompt = """You are an expert brand strategist and marketing analyst.
Analyze the provided brand data and extract the brand's DNA - its core identity, positioning, and strategy.

Be specific, insightful, and data-driven. Focus on what makes this brand unique."""

        user_prompt = f"""Analyze this brand and extract its DNA:

Brand: {brand_data['brand_name']}

Data Collected:
{context}

Provide a comprehensive brand DNA analysis covering:

1. BRAND PERSONALITY
   - Tone & Voice
   - Core Values
   - Brand Archetype

2. POSITIONING
   - Market Position
   - Unique Value Proposition
   - Differentiation Strategy

3. TARGET AUDIENCE
   - Primary Demographics
   - Psychographics
   - Pain Points Addressed

4. VISUAL IDENTITY
   - Color Psychology
   - Design Language
   - Brand Aesthetics

5. MESSAGING STRATEGY
   - Key Messages
   - Communication Style
   - Emotional Appeal

Return as JSON with these exact keys:
{{
  "personality": {{"tone": "", "values": [], "archetype": ""}},
  "positioning": {{"market_position": "", "uvp": "", "differentiation": ""}},
  "audience": {{"demographics": "", "psychographics": "", "pain_points": []}},
  "visual": {{"colors": [], "design_language": "", "aesthetics": ""}},
  "messaging": {{"key_messages": [], "style": "", "emotional_appeal": ""}}
}}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",  # Much faster than turbo-preview
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        brand_dna = json.loads(response.choices[0].message.content)

        print(f"   SUCCESS - Brand DNA extracted")

        return brand_dna

    def analyze_competitors(self, brand_data: Dict, brand_dna: Dict) -> Dict:
        """
        Analyze competitor landscape and find weaknesses

        Returns:
            Competitor intelligence with opportunities
        """

        print(f"   Analyzing competitors...")

        system_prompt = """You are a competitive intelligence analyst.
Identify competitors and their weaknesses to find market opportunities."""

        user_prompt = f"""Based on this brand analysis, identify competitors and their weaknesses:

Brand: {brand_data['brand_name']}
Industry: {brand_data.get('industry', 'Unknown')}
Positioning: {brand_dna['positioning']['market_position']}

Provide:
1. Top 3-5 direct competitors
2. Their key weaknesses
3. Market gaps/opportunities
4. Competitive advantages to leverage

Return as JSON:
{{
  "competitors": [
    {{"name": "", "weakness": "", "market_share": ""}}
  ],
  "market_gaps": [],
  "opportunities": [],
  "competitive_advantages": []
}}"""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",  # Much faster than turbo-preview
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.8
        )

        competitor_intel = json.loads(response.choices[0].message.content)

        print(f"   SUCCESS - Competitor analysis complete")

        return competitor_intel

    def create_growth_roadmap(self, brand_dna: Dict, competitor_intel: Dict) -> Dict:
        """
        Generate strategic growth roadmap

        Returns:
            Actionable growth strategy
        """

        print(f"   Creating growth roadmap...")

        system_prompt = """You are a growth marketing strategist.
Create actionable growth roadmaps based on brand DNA and market opportunities."""

        user_prompt = f"""Create a 90-day growth roadmap:

Brand DNA:
{json.dumps(brand_dna, indent=2)}

Market Opportunities:
{json.dumps(competitor_intel['opportunities'], indent=2)}

Provide:
1. Month 1 priorities (quick wins)
2. Month 2 priorities (momentum building)
3. Month 3 priorities (scaling)
4. Key metrics to track
5. Resource requirements

Return as JSON with timeline and specific actions."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",  # Much faster than turbo-preview
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        raw_content = response.choices[0].message.content
        print(f"[DEBUG] Growth Roadmap Raw Response: {raw_content[:500]}")

        growth_roadmap = json.loads(raw_content)
        print(f"[DEBUG] Growth Roadmap Parsed Keys: {list(growth_roadmap.keys())}")

        print(f"   SUCCESS - Growth roadmap created")

        return growth_roadmap

    def create_content_strategy(self, brand_dna: Dict) -> Dict:
        """
        Generate content pillar strategy

        Returns:
            Content strategy with pillars and topics
        """

        print(f"   Building content strategy...")

        system_prompt = """You are a content strategist.
Create content pillar frameworks that align with brand DNA."""

        user_prompt = f"""Create a content strategy framework:

Brand DNA:
Tone: {brand_dna['personality']['tone']}
Values: {', '.join(brand_dna['personality']['values'])}
Target Audience: {brand_dna['audience']['demographics']}

Provide:
1. 3-5 Content Pillars (core themes)
2. Topic clusters for each pillar
3. Content formats (blog, video, social, etc.)
4. Posting frequency recommendations
5. Platform-specific strategies

Return as JSON with detailed content pillars."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",  # Much faster than turbo-preview
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.8
        )

        raw_content = response.choices[0].message.content
        print(f"[DEBUG] Content Strategy Raw Response: {raw_content[:500]}")

        content_strategy = json.loads(raw_content)
        print(f"[DEBUG] Content Strategy Parsed Keys: {list(content_strategy.keys())}")

        print(f"   SUCCESS - Content strategy created")

        return content_strategy

    def generate_genome_report(
        self,
        job_id: str,
        brand_name: str,
        brand_dna: Dict,
        competitor_intel: Dict,
        growth_roadmap: Dict,
        content_strategy: Dict
    ) -> str:
        """
        Generate comprehensive PDF report

        Returns:
            Path to generated PDF
        """

        print(f"   Generating PREMIUM PDF report with visuals...")

        # Force reload the report generator module to pick up any code changes
        import report_generator_v2
        if 'report_generator_v2' in sys.modules:
            importlib.reload(report_generator_v2)
        from report_generator_v2 import PixaroReportGenerator

        report_gen = PixaroReportGenerator()

        # Compile genome data
        genome_data = {
            'brand_dna': brand_dna,
            'competitors': competitor_intel,
            'growth_roadmap': growth_roadmap,
            'content_strategy': content_strategy
        }

        pdf_path = report_gen.generate_report(
            genome_data=genome_data,
            brand_input=brand_name
        )

        print(f"   SUCCESS - PREMIUM PDF generated with charts and visuals: {pdf_path}")

        return pdf_path

    # Helper Methods

    def _detect_input_type(self, brand_input: str) -> str:
        """Auto-detect input type"""
        if brand_input.startswith(('http://', 'https://', 'www.')):
            return "website"
        elif brand_input.startswith('@'):
            if 'instagram' in brand_input or 'insta' in brand_input:
                return "instagram"
            elif 'twitter' in brand_input or 'x.com' in brand_input:
                return "twitter"
            else:
                return "social"
        else:
            return "brand_name"

    def _scrape_website(self, url: str) -> Dict:
        """Scrape website for brand data"""
        try:
            if not url.startswith('http'):
                url = 'https://' + url

            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract key data
            data = {
                'url': url,
                'title': soup.find('title').text if soup.find('title') else '',
                'description': '',
                'headlines': [],
                'text_content': ''
            }

            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                data['description'] = meta_desc.get('content', '')

            # Headlines
            for tag in ['h1', 'h2']:
                headlines = [h.text.strip() for h in soup.find_all(tag)[:5]]
                data['headlines'].extend(headlines)

            # Main text content (first 1000 chars)
            paragraphs = soup.find_all('p')
            text = ' '.join([p.text.strip() for p in paragraphs[:10]])
            data['text_content'] = text[:1000]

            return data

        except Exception as e:
            print(f"   Warning: Could not scrape website: {e}")
            return {'url': url, 'error': str(e)}

    def _scrape_social(self, handle: str, platform: str) -> Dict:
        """Scrape social media (simplified - would use APIs in production)"""
        return {
            'platform': platform,
            'handle': handle,
            'note': 'Social scraping requires API access - using brand name analysis'
        }

    def _find_brand_website(self, brand_name: str) -> str:
        """Find brand website (simplified - would use search API)"""
        # In production, use Google Search API or similar
        # For now, construct likely URL
        clean_name = brand_name.lower().replace(' ', '')
        return f"https://www.{clean_name}.com"

    def _prepare_brand_context(self, brand_data: Dict) -> str:
        """Prepare context string for AI analysis"""
        context_parts = []

        if brand_data.get('website_data'):
            wd = brand_data['website_data']
            context_parts.append(f"Website: {wd.get('url', '')}")
            context_parts.append(f"Title: {wd.get('title', '')}")
            context_parts.append(f"Description: {wd.get('description', '')}")
            context_parts.append(f"Headlines: {', '.join(wd.get('headlines', []))}")
            context_parts.append(f"Content: {wd.get('text_content', '')[:500]}")

        return '\n'.join(context_parts)
