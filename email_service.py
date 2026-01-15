import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional
from config import settings
import os
import time


class EmailService:
    """Handles sending emails with attachments"""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.sender_email = settings.sender_email
        self.sender_name = settings.sender_name

    def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        attachments: Optional[List[str]] = None,
        max_retries: int = 3
    ) -> bool:
        """
        Send email with optional attachments (with retry logic)

        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML body content
            attachments: List of file paths to attach
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            bool: True if email sent successfully
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                print(f"Sending email to {to_email} (attempt {attempt + 1}/{max_retries})...")

                # Create message
                msg = MIMEMultipart('alternative')
                msg['From'] = f"{self.sender_name} <{self.sender_email}>"
                msg['To'] = to_email
                msg['Subject'] = subject

                # Attach HTML body
                html_part = MIMEText(body_html, 'html')
                msg.attach(html_part)

                # Attach files if provided
                if attachments:
                    for file_path in attachments:
                        if os.path.exists(file_path):
                            self._attach_file(msg, file_path)

                # Connect to SMTP server and send (with timeout for faster failures)
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=20) as server:
                    server.set_debuglevel(0)  # Disable debug output
                    server.starttls()
                    print(f"  TLS connection established")
                    server.login(self.smtp_user, self.smtp_password)
                    print(f"  SMTP login successful")
                    result = server.send_message(msg)
                    print(f"  Message sent, server response: {result if result else 'OK'}")

                print(f"✓ Email sent successfully to {to_email} on attempt {attempt + 1}")
                print(f"  From: {self.sender_email}")
                print(f"  Subject: {subject}")
                if attachments:
                    print(f"  Attachments: {len(attachments)} file(s)")
                return True

            except smtplib.SMTPAuthenticationError as e:
                # Don't retry on auth errors
                print(f"✗ SMTP Authentication failed: {e}")
                return False

            except Exception as e:
                last_error = e
                error_type = type(e).__name__
                print(f"✗ Email send failed (attempt {attempt + 1}/{max_retries})")
                print(f"  Error type: {error_type}")
                print(f"  Error details: {str(e)}")

                # Wait before retrying (exponential backoff)
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    print(f"  Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)

        # All retries failed
        print(f"✗ Failed to send email after {max_retries} attempts. Last error: {last_error}")
        return False

    def _attach_file(self, msg: MIMEMultipart, file_path: str):
        """Attach a file to the email message"""
        filename = Path(file_path).name

        with open(file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )

        msg.attach(part)

    def send_product_video_email(
        self,
        to_email: str,
        product_name: str,
        video_path: str,
        image_path: Optional[str] = None
    ) -> bool:
        """
        Send email with product video and enhanced image

        Args:
            to_email: Recipient email
            product_name: Name of the product
            video_path: Path to generated video
            image_path: Path to enhanced image (optional)

        Returns:
            bool: True if sent successfully
        """
        subject = f"Your {product_name} Marketing Materials Are Ready!"

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
                .feature {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 4px solid #667eea;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎉 Your Marketing Materials Are Ready!</h1>
            </div>
            <div class="content">
                <h2>Hello!</h2>
                <p>Great news! We've successfully processed your product: <strong>{product_name}</strong></p>

                <div class="feature">
                    <h3>📸 What's Included:</h3>
                    <ul>
                        <li><strong>Studio-Quality Product Photo</strong> - Enhanced and professionally edited</li>
                        <li><strong>Marketing Video</strong> - A high-quality promotional video ready to share</li>
                    </ul>
                </div>

                <p>Both files are attached to this email. You can use them immediately for:</p>
                <ul>
                    <li>Social media marketing</li>
                    <li>Your e-commerce website</li>
                    <li>Email campaigns</li>
                    <li>Digital advertising</li>
                </ul>

                <div style="text-align: center; margin: 30px 0;">
                    <p><strong>Start promoting your product today!</strong></p>
                </div>

                <div class="feature">
                    <h3>💡 Tips for Best Results:</h3>
                    <ul>
                        <li>Share the video on Instagram Reels and TikTok for maximum reach</li>
                        <li>Use the enhanced photo as your main product image</li>
                        <li>Post consistently across multiple platforms</li>
                    </ul>
                </div>

                <p>If you have any questions or need additional edits, feel free to upload again or contact our support team.</p>

                <div style="text-align: center;">
                    <p style="font-size: 18px; color: #667eea;"><strong>Thank you for using Genome AI!</strong></p>
                </div>
            </div>
            <div class="footer">
                <p>This is an automated message from Genome AI</p>
                <p>&copy; 2025 Genome AI. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        # Prepare attachments
        attachments = [video_path]
        if image_path and os.path.exists(image_path):
            attachments.append(image_path)

        return self.send_email(to_email, subject, body_html, attachments)

    def send_error_email(self, to_email: str, product_name: str, error_message: str) -> bool:
        """Send email when processing fails"""
        # Truncate product_name if too long for subject
        display_name = product_name[:50] + "..." if len(product_name) > 50 else product_name
        subject = f"Issue Processing Your Content"

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: #dc3545;
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⚠️ Processing Issue</h1>
            </div>
            <div class="content">
                <h2>Hello!</h2>
                <p>We encountered an issue while generating your content.</p>

                <p><strong>Your Prompt:</strong></p>
                <p style="background: #f8f9ff; padding: 15px; border-radius: 5px; font-style: italic; border-left: 4px solid #667eea;">
                    {display_name}
                </p>

                <p><strong>Error Details:</strong></p>
                <p style="background: #fff3cd; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 13px; color: #856404;">
                    {error_message}
                </p>

                <p>Please try again with a different prompt. If the issue persists, contact our support team.</p>

                <p>We apologize for the inconvenience.</p>

                <p><strong>Best regards,</strong><br>Genome AI Team</p>
            </div>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, body_html)

    def send_content_email(
        self,
        to_email: str,
        prompt: str,
        image_path: str,
        video_path: str,
        caption: str,
        hashtags: List[str]
    ) -> bool:
        """
        Send email with AI-generated content (image, video, caption, hashtags)

        Args:
            to_email: Recipient email
            prompt: Original prompt
            image_path: Path to generated image
            video_path: Path to generated video
            caption: Generated caption
            hashtags: List of hashtags

        Returns:
            bool: True if sent successfully
        """
        subject = "Your AI-Generated Content is Ready!"

        hashtags_str = " ".join(hashtags)

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .prompt-box {{
                    background: white;
                    padding: 15px;
                    border-left: 4px solid #667eea;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-style: italic;
                }}
                .caption-box {{
                    background: #f0f8ff;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border: 2px solid #667eea;
                }}
                .hashtags {{
                    background: #fff;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;
                    color: #667eea;
                    font-weight: bold;
                }}
                .feature {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 4px solid #28a745;
                    border-radius: 5px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>✨ Your Content is Ready!</h1>
                <p style="margin: 0; font-size: 18px;">AI-Generated Social Media Package</p>
            </div>
            <div class="content">
                <h2>Hello!</h2>
                <p>Amazing news! Your AI-generated content is ready to go viral! 🚀</p>

                <div class="prompt-box">
                    <strong>Your Prompt:</strong><br>
                    "{prompt}"
                </div>

                <div class="feature">
                    <h3>📦 What's Included:</h3>
                    <ul>
                        <li>✅ <strong>AI-Generated Image</strong> (DALL-E 3) - Professional quality</li>
                        <li>✅ <strong>Cinema-Quality Video</strong> (Veo 3) - 10 seconds of pure awesomeness</li>
                        <li>✅ <strong>Engaging Caption</strong> - Written by GPT-4</li>
                        <li>✅ <strong>Trending Hashtags</strong> - Optimized for reach</li>
                    </ul>
                </div>

                <div class="caption-box">
                    <h3 style="margin-top: 0; color: #667eea;">📝 Your Caption:</h3>
                    <p style="font-size: 16px; line-height: 1.8;">{caption}</p>
                </div>

                <div class="hashtags">
                    <h3 style="margin-top: 0;">📱 Trending Hashtags:</h3>
                    <p style="font-size: 14px; margin: 10px 0;">{hashtags_str}</p>
                </div>

                <div class="feature">
                    <h3>🚀 How to Use:</h3>
                    <ol>
                        <li>Download the attached image and video</li>
                        <li>Post on Instagram, TikTok, or YouTube Shorts</li>
                        <li>Copy-paste the caption</li>
                        <li>Add the hashtags</li>
                        <li>Watch your engagement soar! 📈</li>
                    </ol>
                </div>

                <div class="feature">
                    <h3>💡 Pro Tips:</h3>
                    <ul>
                        <li><strong>Best times to post:</strong> 9 AM, 12 PM, or 7 PM (local time)</li>
                        <li><strong>Instagram:</strong> Use Reels for maximum reach</li>
                        <li><strong>TikTok:</strong> Add trending sounds for viral potential</li>
                        <li><strong>Cross-post:</strong> Share on multiple platforms simultaneously</li>
                    </ul>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <p style="font-size: 20px; color: #667eea;"><strong>Ready to Go Viral! 🔥</strong></p>
                </div>

                <p>Need more content? Just send another prompt!</p>

                <div style="text-align: center; margin-top: 20px;">
                    <p style="font-size: 18px; color: #667eea;"><strong>Thank you for using Genome AI!</strong></p>
                </div>
            </div>
            <div class="footer">
                <p>This is an automated message from Genome AI</p>
                <p>&copy; 2025 Genome AI. All rights reserved.</p>
                <p style="margin-top: 10px; color: #999;">
                    Image: DALL-E 3 | Video: Veo 3 | Caption: GPT-4
                </p>
            </div>
        </body>
        </html>
        """

        # Attach both files
        attachments = [image_path, video_path]

        return self.send_email(to_email, subject, body_html, attachments)

    def send_genome_report_email(
        self,
        to_email: str,
        brand_input: str,
        report_path: str
    ) -> bool:
        """
        Send email with Marketing Genome Report PDF

        Args:
            to_email: Recipient email
            brand_input: Brand name/URL/handle analyzed
            report_path: Path to generated PDF report

        Returns:
            bool: True if sent successfully
        """
        subject = f"🧬 Your Marketing Genome Report is Ready - {brand_input}"

        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .brand-box {{
                    background: white;
                    padding: 20px;
                    border-left: 5px solid #667eea;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-size: 18px;
                }}
                .feature {{
                    background: white;
                    padding: 20px;
                    margin: 15px 0;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .feature h3 {{
                    color: #667eea;
                    margin-top: 0;
                }}
                .highlight-box {{
                    background: linear-gradient(135deg, #f5f7fa 0%, #e8eaf6 100%);
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                    border: 2px solid #667eea;
                }}
                .cta-button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
                .emoji {{
                    font-size: 24px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 style="margin: 0; font-size: 32px;">🧬 Marketing Genome Report</h1>
                <p style="margin: 10px 0 0 0; font-size: 18px;">Your Complete Marketing DNA Analysis</p>
            </div>
            <div class="content">
                <h2>Hello!</h2>
                <p style="font-size: 16px;">Your comprehensive Marketing Genome Report is ready! We've analyzed your brand from every angle using real-time data and AI intelligence.</p>

                <div class="brand-box">
                    <strong>Brand Analyzed:</strong><br>
                    <span style="color: #667eea; font-size: 20px;">{brand_input}</span>
                </div>

                <div class="highlight-box">
                    <h3 style="text-align: center; color: #667eea; margin-top: 0;">📊 What's Inside Your Report</h3>
                    <p style="text-align: center; margin: 0;">Your complete marketing strategy blueprint</p>
                </div>

                <div class="feature">
                    <h3><span class="emoji">🔬</span> Brand DNA Analysis</h3>
                    <ul>
                        <li><strong>Brand Personality:</strong> Tone, voice, and style breakdown</li>
                        <li><strong>Target Audience:</strong> Detailed demographic profile</li>
                        <li><strong>Core Values:</strong> What your brand truly stands for</li>
                        <li><strong>Market Positioning:</strong> Where you fit in the landscape</li>
                    </ul>
                </div>

                <div class="feature">
                    <h3><span class="emoji">🎯</span> Competitive Intelligence</h3>
                    <ul>
                        <li><strong>Market Landscape:</strong> Who you're up against</li>
                        <li><strong>Key Competitors:</strong> Detailed competitor profiles</li>
                        <li><strong>Your Advantages:</strong> What sets you apart</li>
                        <li><strong>Weaknesses to Exploit:</strong> Gaps in competitor strategies</li>
                    </ul>
                </div>

                <div class="feature">
                    <h3><span class="emoji">📈</span> 90-Day Growth Roadmap</h3>
                    <ul>
                        <li><strong>Month 1:</strong> Foundation building strategies</li>
                        <li><strong>Month 2:</strong> Acceleration tactics</li>
                        <li><strong>Month 3:</strong> Optimization and scaling</li>
                        <li><strong>Key Metrics:</strong> KPIs to track your success</li>
                    </ul>
                </div>

                <div class="feature">
                    <h3><span class="emoji">📱</span> Content Strategy Blueprint</h3>
                    <ul>
                        <li><strong>Content Pillars:</strong> Core themes for your brand</li>
                        <li><strong>Content Mix:</strong> Optimal distribution across formats</li>
                        <li><strong>Publishing Frequency:</strong> Platform-specific schedules</li>
                        <li><strong>Monthly Themes:</strong> Strategic content calendar</li>
                    </ul>
                </div>

                <div class="highlight-box">
                    <h3 style="color: #667eea; margin-top: 0; text-align: center;">🚀 Ready to Transform Your Marketing?</h3>
                    <p style="text-align: center;">Your complete Marketing Genome Report is attached as a PDF. Download it now and start implementing your personalized strategy!</p>
                    <div style="text-align: center;">
                        <p style="font-size: 14px; color: #666; margin-top: 15px;">📎 <strong>Attachment:</strong> MarketingGenome_Report.pdf</p>
                    </div>
                </div>

                <div class="feature">
                    <h3>💡 How to Use This Report</h3>
                    <ol>
                        <li><strong>Read the Executive Summary</strong> - Get the big picture first</li>
                        <li><strong>Review Your Brand DNA</strong> - Understand your unique identity</li>
                        <li><strong>Study Competitor Analysis</strong> - Find opportunities to win</li>
                        <li><strong>Follow the 90-Day Roadmap</strong> - Take action month by month</li>
                        <li><strong>Implement Content Strategy</strong> - Start creating with purpose</li>
                    </ol>
                </div>

                <div class="feature" style="background: #fff3e0; border-left: 5px solid #ff9800;">
                    <h3 style="color: #f57c00;">🎁 What Makes This Different?</h3>
                    <p>Unlike generic marketing advice, your Marketing Genome Report is built from <strong>real data</strong> about your brand:</p>
                    <ul>
                        <li>✅ Live social media analysis</li>
                        <li>✅ Website content scraping</li>
                        <li>✅ Competitor intelligence</li>
                        <li>✅ Market positioning research</li>
                        <li>✅ AI-powered strategic insights</li>
                    </ul>
                    <p style="margin-bottom: 0;"><strong>This is YOUR unique marketing DNA</strong> - not a template.</p>
                </div>

                <div style="text-align: center; margin: 40px 0;">
                    <p style="font-size: 22px; color: #667eea; margin: 0;"><strong>Your Marketing Evolution Starts Now</strong>
                    <p style="color: #666; margin: 10px 0;">Open the PDF and discover your brand's true potential</p>
                </div>

                <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; border-left: 5px solid #4caf50;">
                    <p style="margin: 0; color: #2e7d32;"><strong>💬 Questions or Need Clarification?</strong></p>
                    <p style="margin: 10px 0 0 0; color: #333;">Review the report and reach out if you need help implementing any strategies. We're here to help you succeed!</p>
                </div>

                <div style="text-align: center; margin-top: 30px;">
                    <p style="font-size: 20px; color: #667eea;"><strong>Thank you for using Genome AI!</strong></p>
                    <p style="color: #666;">Powered by AI • Built from Real Data • Designed for Growth</p>
                </div>
            </div>
            <div class="footer">
                <p>This is an automated message from Genome AI</p>
                <p>&copy; 2025 Genome AI. All rights reserved.</p>
                <p style="margin-top: 10px; color: #999;">
                    🧬 Marketing Genome Technology | AI-Powered Brand Intelligence
                </p>
            </div>
        </body>
        </html>
        """

        # Attach PDF report
        attachments = [report_path]

        return self.send_email(to_email, subject, body_html, attachments)
