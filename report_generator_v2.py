"""
Report Generator V2 - Professional PDF Report Generator for Genome AI
Generates comprehensive Marketing Genome Reports with charts and visuals
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime
import os
from config import settings

# Version 2.2 - Fixed contentStrategyFramework extraction and month handling
print("=" * 80)
print("[REPORT GENERATOR V2.2] Module loaded - ENHANCED DEBUG VERSION")
print("=" * 80)
import json


class PixaroReportGenerator:
    """
    Generates professional PDF Marketing Genome Reports
    """

    def __init__(self):
        self.primary_color = HexColor('#667eea')
        self.secondary_color = HexColor('#764ba2')
        self.text_color = HexColor('#333333')
        self.light_bg = HexColor('#f8f9fa')

        # Setup styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='GenomeTitle',
            parent=self.styles['Title'],
            fontSize=28,
            textColor=self.primary_color,
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='GenomeSectionHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=self.primary_color,
            spaceBefore=20,
            spaceAfter=12
        ))

        self.styles.add(ParagraphStyle(
            name='GenomeSubHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.secondary_color,
            spaceBefore=15,
            spaceAfter=8
        ))

        self.styles.add(ParagraphStyle(
            name='GenomeBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.text_color,
            spaceAfter=8,
            alignment=TA_JUSTIFY
        ))

        self.styles.add(ParagraphStyle(
            name='GenomeBulletText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.text_color,
            leftIndent=20,
            spaceAfter=6
        ))

    def generate_report(self, genome_data: dict, brand_input: str) -> str:
        """
        Generate the Marketing Genome Report PDF

        Args:
            genome_data: Dictionary containing brand_dna, competitors, growth_roadmap, content_strategy
            brand_input: The brand name/URL/handle analyzed

        Returns:
            Path to generated PDF file
        """
        # Create output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_brand = "".join(c for c in brand_input if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
        filename = f"MarketingGenome_{safe_brand}_{timestamp}.pdf"
        filepath = os.path.join(settings.output_dir, filename)

        # Ensure output directory exists
        os.makedirs(settings.output_dir, exist_ok=True)

        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        # Build content
        story = []

        # Title Page
        story.extend(self._create_title_page(brand_input))
        story.append(PageBreak())

        # Executive Summary
        story.extend(self._create_executive_summary(genome_data, brand_input))
        story.append(PageBreak())

        # Brand DNA Section
        story.extend(self._create_brand_dna_section(genome_data.get('brand_dna', {})))
        story.append(PageBreak())

        # Competitor Analysis
        story.extend(self._create_competitor_section(genome_data.get('competitors', {})))
        story.append(PageBreak())

        # Growth Roadmap
        story.extend(self._create_growth_roadmap_section(genome_data.get('growth_roadmap', {})))
        story.append(PageBreak())

        # Content Strategy
        story.extend(self._create_content_strategy_section(genome_data.get('content_strategy', {})))

        # Build PDF
        doc.build(story)

        return filepath

    def _create_title_page(self, brand_input: str) -> list:
        """Create the title page"""
        elements = []

        elements.append(Spacer(1, 2*inch))

        # Main title
        elements.append(Paragraph(
            "Marketing Genome Report",
            self.styles['GenomeTitle']
        ))

        elements.append(Spacer(1, 0.5*inch))

        # Brand name
        elements.append(Paragraph(
            f"<b>{brand_input}</b>",
            ParagraphStyle(
                'BrandName',
                parent=self.styles['Normal'],
                fontSize=20,
                textColor=self.secondary_color,
                alignment=TA_CENTER
            )
        ))

        elements.append(Spacer(1, inch))

        # Date
        elements.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y')}",
            ParagraphStyle(
                'Date',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=self.text_color,
                alignment=TA_CENTER
            )
        ))

        elements.append(Spacer(1, 0.5*inch))

        # Powered by
        elements.append(Paragraph(
            "Powered by Genome AI",
            ParagraphStyle(
                'PoweredBy',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        ))

        return elements

    def _create_executive_summary(self, genome_data: dict, brand_input: str) -> list:
        """Create executive summary section"""
        elements = []

        elements.append(Paragraph("Executive Summary", self.styles['GenomeSectionHeader']))
        elements.append(Spacer(1, 0.2*inch))

        brand_dna = genome_data.get('brand_dna', {})
        positioning = brand_dna.get('positioning', {})

        summary_text = f"""
        This Marketing Genome Report provides a comprehensive analysis of <b>{brand_input}</b>,
        including brand DNA extraction, competitive intelligence, growth strategies, and content recommendations.
        """
        elements.append(Paragraph(summary_text, self.styles['GenomeBodyText']))

        # Key highlights
        elements.append(Paragraph("Key Highlights:", self.styles['GenomeSubHeader']))

        highlights = [
            f"Market Position: {positioning.get('market_position', 'N/A')}",
            f"Unique Value Proposition: {positioning.get('uvp', 'N/A')}",
            f"Primary Differentiation: {positioning.get('differentiation', 'N/A')}"
        ]

        for highlight in highlights:
            elements.append(Paragraph(f"• {highlight}", self.styles['GenomeBulletText']))

        return elements

    def _create_brand_dna_section(self, brand_dna: dict) -> list:
        """Create brand DNA section"""
        elements = []

        elements.append(Paragraph("Brand DNA Analysis", self.styles['GenomeSectionHeader']))

        # Personality
        personality = brand_dna.get('personality', {})
        elements.append(Paragraph("Brand Personality", self.styles['GenomeSubHeader']))

        elements.append(Paragraph(f"<b>Tone:</b> {personality.get('tone', 'N/A')}", self.styles['GenomeBodyText']))

        values = personality.get('values', [])
        if values:
            values_str = ', '.join(values) if isinstance(values, list) else str(values)
            elements.append(Paragraph(f"<b>Core Values:</b> {values_str}", self.styles['GenomeBodyText']))

        elements.append(Paragraph(f"<b>Brand Archetype:</b> {personality.get('archetype', 'N/A')}", self.styles['GenomeBodyText']))

        # Positioning
        positioning = brand_dna.get('positioning', {})
        elements.append(Paragraph("Market Positioning", self.styles['GenomeSubHeader']))

        elements.append(Paragraph(f"<b>Position:</b> {positioning.get('market_position', 'N/A')}", self.styles['GenomeBodyText']))
        elements.append(Paragraph(f"<b>UVP:</b> {positioning.get('uvp', 'N/A')}", self.styles['GenomeBodyText']))
        elements.append(Paragraph(f"<b>Differentiation:</b> {positioning.get('differentiation', 'N/A')}", self.styles['GenomeBodyText']))

        # Audience
        audience = brand_dna.get('audience', {})
        elements.append(Paragraph("Target Audience", self.styles['GenomeSubHeader']))

        elements.append(Paragraph(f"<b>Demographics:</b> {audience.get('demographics', 'N/A')}", self.styles['GenomeBodyText']))
        elements.append(Paragraph(f"<b>Psychographics:</b> {audience.get('psychographics', 'N/A')}", self.styles['GenomeBodyText']))

        pain_points = audience.get('pain_points', [])
        if pain_points:
            elements.append(Paragraph("<b>Pain Points Addressed:</b>", self.styles['GenomeBodyText']))
            for point in pain_points[:5]:
                elements.append(Paragraph(f"• {point}", self.styles['GenomeBulletText']))

        # Messaging
        messaging = brand_dna.get('messaging', {})
        elements.append(Paragraph("Messaging Strategy", self.styles['GenomeSubHeader']))

        elements.append(Paragraph(f"<b>Communication Style:</b> {messaging.get('style', 'N/A')}", self.styles['GenomeBodyText']))
        elements.append(Paragraph(f"<b>Emotional Appeal:</b> {messaging.get('emotional_appeal', 'N/A')}", self.styles['GenomeBodyText']))

        key_messages = messaging.get('key_messages', [])
        if key_messages:
            elements.append(Paragraph("<b>Key Messages:</b>", self.styles['GenomeBodyText']))
            for msg in key_messages[:5]:
                elements.append(Paragraph(f"• {msg}", self.styles['GenomeBulletText']))

        return elements

    def _create_competitor_section(self, competitors: dict) -> list:
        """Create competitor analysis section"""
        elements = []

        elements.append(Paragraph("Competitive Intelligence", self.styles['GenomeSectionHeader']))

        # Competitors list
        competitor_list = competitors.get('competitors', [])
        if competitor_list:
            elements.append(Paragraph("Key Competitors", self.styles['GenomeSubHeader']))

            for comp in competitor_list[:5]:
                if isinstance(comp, dict):
                    name = comp.get('name', 'Unknown')
                    weakness = comp.get('weakness', 'N/A')
                    elements.append(Paragraph(f"<b>{name}</b>", self.styles['GenomeBodyText']))
                    elements.append(Paragraph(f"Weakness: {weakness}", self.styles['GenomeBulletText']))
                    elements.append(Spacer(1, 0.1*inch))

        # Market gaps
        gaps = competitors.get('market_gaps', [])
        if gaps:
            elements.append(Paragraph("Market Gaps & Opportunities", self.styles['GenomeSubHeader']))
            for gap in gaps[:5]:
                elements.append(Paragraph(f"• {gap}", self.styles['GenomeBulletText']))

        # Competitive advantages
        advantages = competitors.get('competitive_advantages', [])
        if advantages:
            elements.append(Paragraph("Your Competitive Advantages", self.styles['GenomeSubHeader']))
            for adv in advantages[:5]:
                elements.append(Paragraph(f"• {adv}", self.styles['GenomeBulletText']))

        return elements

    def _create_growth_roadmap_section(self, roadmap: dict) -> list:
        """Create growth roadmap section"""
        elements = []

        elements.append(Paragraph("90-Day Growth Roadmap", self.styles['GenomeSectionHeader']))

        # Debug: Print roadmap structure
        print(f"[DEBUG] Roadmap keys: {list(roadmap.keys())}")

        # Print sample of Month 1 data to see its structure
        month1_data = roadmap.get('Month 1 Priorities')
        if month1_data:
            print(f"[DEBUG] Month 1 Priorities type: {type(month1_data)}")
            print(f"[DEBUG] Month 1 Priorities sample: {str(month1_data)[:200]}")

        # If roadmap is empty, show placeholder
        if not roadmap:
            elements.append(Paragraph("Growth roadmap data is being generated...", self.styles['GenomeBodyText']))
            return elements

        # Try multiple key variations for months
        # Month 1
        month1 = (roadmap.get('Month 1 Priorities') or roadmap.get('month_1') or roadmap.get('month1') or
                  roadmap.get('Month 1') or roadmap.get('1') or
                  roadmap.get('month_one') or {})
        if month1:
            elements.append(Paragraph("Month 1: Foundation", self.styles['GenomeSubHeader']))
            self._add_month_content(elements, month1)

        # Month 2
        month2 = (roadmap.get('Month 2 Priorities') or roadmap.get('month_2') or roadmap.get('month2') or
                  roadmap.get('Month 2') or roadmap.get('2') or
                  roadmap.get('month_two') or {})
        if month2:
            elements.append(Paragraph("Month 2: Momentum", self.styles['GenomeSubHeader']))
            self._add_month_content(elements, month2)

        # Month 3
        month3 = (roadmap.get('Month 3 Priorities') or roadmap.get('month_3') or roadmap.get('month3') or
                  roadmap.get('Month 3') or roadmap.get('3') or
                  roadmap.get('month_three') or {})
        if month3:
            elements.append(Paragraph("Month 3: Scale", self.styles['GenomeSubHeader']))
            self._add_month_content(elements, month3)

        # Key metrics - try multiple variations
        metrics = (roadmap.get('Key Metrics to Track') or roadmap.get('key_metrics') or roadmap.get('metrics') or
                   roadmap.get('kpis') or roadmap.get('tracking') or [])
        if metrics:
            elements.append(Paragraph("Key Metrics to Track", self.styles['GenomeSubHeader']))
            if isinstance(metrics, list):
                for metric in metrics[:8]:
                    elements.append(Paragraph(f"• {metric}", self.styles['GenomeBulletText']))
            elif isinstance(metrics, dict):
                for key, value in list(metrics.items())[:8]:
                    elements.append(Paragraph(f"• {key}: {value}", self.styles['GenomeBulletText']))
            elif isinstance(metrics, str):
                elements.append(Paragraph(metrics, self.styles['GenomeBodyText']))

        # If no months were found, try to extract any content from the dict
        if not month1 and not month2 and not month3:
            # Check if there's a nested roadmap structure
            nested_roadmap = (roadmap.get('90-Day Growth Roadmap') or roadmap.get('roadmap') or
                            roadmap.get('timeline') or None)

            if nested_roadmap and isinstance(nested_roadmap, dict):
                # Extract from nested structure
                for key, value in list(nested_roadmap.items())[:10]:
                    if key not in ['key_metrics', 'metrics', 'kpis', 'tracking']:
                        if isinstance(value, str):
                            elements.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b>", self.styles['GenomeSubHeader']))
                            elements.append(Paragraph(value, self.styles['GenomeBodyText']))
                        elif isinstance(value, list):
                            elements.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b>", self.styles['GenomeSubHeader']))
                            for item in value[:8]:
                                if isinstance(item, str):
                                    elements.append(Paragraph(f"  • {item}", self.styles['GenomeBulletText']))
                        elif isinstance(value, dict):
                            elements.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b>", self.styles['GenomeSubHeader']))
                            for sub_key, sub_val in list(value.items())[:5]:
                                if isinstance(sub_val, str):
                                    elements.append(Paragraph(f"  <b>{sub_key}:</b> {sub_val}", self.styles['GenomeBodyText']))
                                elif isinstance(sub_val, list):
                                    elements.append(Paragraph(f"  <b>{sub_key}:</b>", self.styles['GenomeBodyText']))
                                    for item in sub_val[:3]:
                                        elements.append(Paragraph(f"    • {item}", self.styles['GenomeBulletText']))
            else:
                # Flat structure
                elements.append(Paragraph("Growth Strategy Overview", self.styles['GenomeSubHeader']))
                for key, value in list(roadmap.items())[:10]:
                    if key not in ['key_metrics', 'metrics', 'kpis', 'tracking', 'Key Metrics to Track']:
                        if isinstance(value, str):
                            elements.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", self.styles['GenomeBodyText']))
                        elif isinstance(value, list):
                            elements.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b>", self.styles['GenomeBodyText']))
                            for item in value[:5]:
                                if isinstance(item, str):
                                    elements.append(Paragraph(f"  • {item}", self.styles['GenomeBulletText']))

        return elements

    def _add_month_content(self, elements: list, month_data):
        """Add month content to elements"""
        print(f"[DEBUG] Month data type: {type(month_data)}")
        print(f"[DEBUG] Month data value: {str(month_data)[:300]}")

        if isinstance(month_data, list):
            # Direct list of priorities
            for item in month_data[:8]:
                if isinstance(item, str):
                    elements.append(Paragraph(f"  • {item}", self.styles['GenomeBulletText']))
        elif isinstance(month_data, dict):
            # Try to get priorities/actions list
            priorities = month_data.get('priorities', month_data.get('actions', []))
            if priorities and isinstance(priorities, list):
                for priority in priorities[:8]:
                    if isinstance(priority, str):
                        elements.append(Paragraph(f"  • {priority}", self.styles['GenomeBulletText']))
            else:
                # If no priorities key, iterate through all dict values
                for key, value in list(month_data.items())[:8]:
                    if isinstance(value, str):
                        elements.append(Paragraph(f"  • {value}", self.styles['GenomeBulletText']))
                    elif isinstance(value, list):
                        elements.append(Paragraph(f"  <b>{key.replace('_', ' ').title()}:</b>", self.styles['GenomeBodyText']))
                        for item in value[:5]:
                            if isinstance(item, str):
                                elements.append(Paragraph(f"    • {item}", self.styles['GenomeBulletText']))
        elif isinstance(month_data, str):
            elements.append(Paragraph(month_data, self.styles['GenomeBodyText']))

        elements.append(Spacer(1, 0.1*inch))

    def _create_content_strategy_section(self, content_strategy: dict) -> list:
        """Create content strategy section"""
        elements = []

        elements.append(Paragraph("Content Strategy Blueprint", self.styles['GenomeSectionHeader']))

        # Debug: Print content strategy structure
        print(f"[DEBUG] Content Strategy keys: {list(content_strategy.keys())}")

        # Print sample of contentPillars to see structure
        pillars_data = content_strategy.get('contentPillars')
        if pillars_data:
            print(f"[DEBUG] contentPillars type: {type(pillars_data)}")
            if isinstance(pillars_data, list) and len(pillars_data) > 0:
                print(f"[DEBUG] First pillar type: {type(pillars_data[0])}")
                print(f"[DEBUG] First pillar sample: {str(pillars_data[0])[:300]}")

        # If content_strategy is empty, show placeholder
        if not content_strategy:
            elements.append(Paragraph("Content strategy data is being generated...", self.styles['GenomeBodyText']))
            return elements

        # Content pillars - try multiple variations
        # First check if there's a nested framework structure
        framework = content_strategy.get('contentStrategyFramework')
        if framework and isinstance(framework, dict):
            print(f"[DEBUG] Found contentStrategyFramework, extracting pillars from it")
            content_strategy = framework  # Use the framework as the main dict

        pillars = None
        for key in ['contentPillars', 'content_pillars', 'pillars', 'themes', 'topics']:
            if key in content_strategy:
                pillars = content_strategy[key]
                print(f"[DEBUG] Found pillars under key: {key}")
                break

        # Debug pillars
        print(f"[DEBUG] Pillars found: {pillars is not None}")
        if pillars is not None:
            print(f"[DEBUG] Pillars type: {type(pillars)}")
            print(f"[DEBUG] Pillars value (first 500 chars): {str(pillars)[:500]}")
            if isinstance(pillars, list):
                print(f"[DEBUG] Number of pillars: {len(pillars)}")
                if len(pillars) > 0:
                    print(f"[DEBUG] First pillar type: {type(pillars[0])}")
                    print(f"[DEBUG] First pillar: {pillars[0]}")

        if pillars is not None and pillars:
            elements.append(Paragraph("Content Pillars", self.styles['GenomeSubHeader']))

            if isinstance(pillars, list):
                for pillar in pillars[:5]:
                    if isinstance(pillar, dict):
                        name = (pillar.get('pillarName') or pillar.get('name') or pillar.get('pillar') or
                                pillar.get('theme') or pillar.get('title') or 'Content Pillar')
                        elements.append(Paragraph(f"<b>{name}</b>", self.styles['GenomeBodyText']))

                        # Get topic clusters
                        topics = (pillar.get('topicClusters') or pillar.get('topics') or
                                  pillar.get('subtopics') or pillar.get('topic_clusters') or [])
                        if topics:
                            elements.append(Paragraph("Topics:", self.styles['GenomeBodyText']))
                            for topic in topics[:5]:
                                elements.append(Paragraph(f"  • {topic}", self.styles['GenomeBulletText']))

                        # Get content formats
                        formats = pillar.get('contentFormats') or pillar.get('formats') or []
                        if formats:
                            formats_str = ', '.join(formats) if isinstance(formats, list) else str(formats)
                            elements.append(Paragraph(f"Formats: {formats_str}", self.styles['GenomeBodyText']))

                        # Get posting frequency
                        freq = pillar.get('postingFrequency') or pillar.get('frequency')
                        if freq:
                            elements.append(Paragraph(f"Frequency: {freq}", self.styles['GenomeBodyText']))

                        elements.append(Spacer(1, 0.15*inch))
                    else:
                        elements.append(Paragraph(f"• {pillar}", self.styles['GenomeBulletText']))
            elif isinstance(pillars, dict):
                for pillar_name, pillar_topics in list(pillars.items())[:5]:
                    elements.append(Paragraph(f"<b>{pillar_name}</b>", self.styles['GenomeBodyText']))
                    if isinstance(pillar_topics, list):
                        for topic in pillar_topics[:3]:
                            elements.append(Paragraph(f"  - {topic}", self.styles['GenomeBulletText']))

        # Content formats - try multiple variations
        formats = (content_strategy.get('content_formats') or content_strategy.get('formats') or
                   content_strategy.get('content_types') or [])
        if formats:
            elements.append(Paragraph("Recommended Content Formats", self.styles['GenomeSubHeader']))
            if isinstance(formats, list):
                for fmt in formats[:6]:
                    elements.append(Paragraph(f"• {fmt}", self.styles['GenomeBulletText']))
            elif isinstance(formats, dict):
                for key, value in list(formats.items())[:6]:
                    elements.append(Paragraph(f"• {key}: {value}", self.styles['GenomeBulletText']))
            elif isinstance(formats, str):
                elements.append(Paragraph(formats, self.styles['GenomeBodyText']))

        # Posting frequency - try multiple variations
        frequency = (content_strategy.get('posting_frequency') or content_strategy.get('frequency') or
                     content_strategy.get('schedule') or content_strategy.get('posting_schedule') or {})
        if frequency:
            elements.append(Paragraph("Posting Schedule", self.styles['GenomeSubHeader']))
            if isinstance(frequency, dict):
                for platform, freq in list(frequency.items())[:5]:
                    elements.append(Paragraph(f"• {platform}: {freq}", self.styles['GenomeBulletText']))
            elif isinstance(frequency, str):
                elements.append(Paragraph(frequency, self.styles['GenomeBodyText']))
            elif isinstance(frequency, list):
                for item in frequency[:5]:
                    elements.append(Paragraph(f"• {item}", self.styles['GenomeBulletText']))

        # If nothing was found, extract any available content
        # But skip brandDNA since it's not part of content strategy
        if not pillars and not formats and not frequency:
            elements.append(Paragraph("Content Strategy Overview", self.styles['GenomeSubHeader']))
            for key, value in list(content_strategy.items())[:10]:
                # Skip brandDNA - it's metadata, not content strategy
                if key in ['brandDNA', 'brand_dna', 'branddna']:
                    continue

                if isinstance(value, str):
                    elements.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value}", self.styles['GenomeBodyText']))
                elif isinstance(value, list):
                    # Don't show raw dict strings
                    elements.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b>", self.styles['GenomeBodyText']))
                    for item in value[:5]:
                        # Only show if it's a string, not a dict
                        if isinstance(item, str):
                            elements.append(Paragraph(f"  • {item}", self.styles['GenomeBulletText']))
                elif isinstance(value, dict):
                    elements.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b>", self.styles['GenomeBodyText']))
                    for sub_key, sub_value in list(value.items())[:3]:
                        # Format the sub_value properly
                        if isinstance(sub_value, (str, int, float)):
                            elements.append(Paragraph(f"  • {sub_key}: {sub_value}", self.styles['GenomeBulletText']))
                        elif isinstance(sub_value, list):
                            val_str = ', '.join(str(v) for v in sub_value[:3])
                            elements.append(Paragraph(f"  • {sub_key}: {val_str}", self.styles['GenomeBulletText']))

        # Footer
        elements.append(Spacer(1, inch))
        elements.append(Paragraph(
            "Report generated by Genome AI - Your AI-Powered Marketing Strategist",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        ))

        return elements
