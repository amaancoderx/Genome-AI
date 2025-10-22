# Pixaro - AI-Powered Marketing Intelligence Platform

Pixaro is an intelligent marketing platform that provides AI-powered brand analysis, content generation, and strategic marketing insights.

## 🚀 Features

### 1. **Market Genome Analysis**
- Comprehensive brand DNA analysis
- Competitor intelligence mapping
- Growth roadmap generation
- Content strategy blueprints

### 2. **Brand AI Assistant (Chat Interface)**
- Real-time conversational AI strategist
- Content creation (Instagram posts, captions, campaigns)
- AI image generation using DALL-E 3
- Audience insights and micro-personas
- Competitor analysis with actionable insights
- Engagement predictions
- Weekly content planning

### 3. **Key Capabilities**
- 🎨 **Content Creation**: Generate posts, captions, and visual content
- 👥 **Audience Insights**: Understand micro-personas and behavior
- 🎯 **Competitor Analysis**: Identify gaps and opportunities
- 📊 **Strategic Planning**: Get actionable growth roadmaps
- 🖼️ **AI Image Generation**: Create professional visuals using DALL-E 3
- 📧 **PDF Reports**: Comprehensive marketing genome reports via email

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **AI/ML**: OpenAI GPT-4, DALL-E 3
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Email**: SMTP for report delivery
- **Styling**: Custom CSS with responsive design

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- SMTP credentials for email functionality

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/amaancoderx/pixaro.git
   cd pixaro
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env` file in the root directory:
   ```env
   # API Configuration
   API_HOST=0.0.0.0
   API_PORT=8000

   # Email Configuration
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SENDER_EMAIL=your-email@gmail.com
   SENDER_NAME=Pixaro AI Agent

   # AI Service API Keys
   OPENAI_API_KEY=your-openai-api-key

   # Optional: Additional AI services
   REPLICATE_API_KEY=your-replicate-key
   STABILITY_API_KEY=your-stability-key
   RUNWAY_API_KEY=your-runway-key
   ```

4. **Run the application**
   ```bash
   python start_simple.py
   ```

5. **Access the application**
   - **AI Chat Assistant** (Homepage): http://127.0.0.1:8000/
   - Market Genome Analysis: http://127.0.0.1:8000/genome
   - API Documentation: http://127.0.0.1:8000/docs

## 📱 Responsive Design

Pixaro is fully responsive and works seamlessly on:
- Desktop computers
- Tablets (iPad, Android tablets)
- Mobile phones (iPhone, Android)
- Both portrait and landscape orientations

## 🎯 Usage

### AI Chat Assistant (Default Homepage)
1. Navigate to http://127.0.0.1:8000/ (homepage)
2. Connect your brand by entering Instagram handle or brand name
3. Start chatting with your personal AI marketing strategist
4. Ask for:
   - Content ideas and post generation
   - AI image creation
   - Competitor analysis
   - Audience insights
   - Strategic recommendations

### Example Prompts
- "Generate 5 Instagram posts for this week"
- "Create an image about cybersecurity awareness"
- "Who are my competitors? Give me the list with links"
- "Show me my audience personas"
- "Create a weekly content strategy"
- "Predict engagement for this content idea"

### Market Genome Analysis (Advanced)
1. Navigate to http://127.0.0.1:8000/genome
2. Enter a brand name, website URL, or social media handle
3. Provide your email address
4. Receive a comprehensive Marketing Genome Report via email

## 📂 Project Structure

```
pixaro/
├── brand_ai_assistant.py      # AI chat assistant logic
├── chat_interface.html        # Chat UI (responsive)
├── config.py                  # Configuration settings
├── email_service.py           # Email functionality
├── market_genome_engine.py    # Brand analysis engine
├── market_genome_main.py      # FastAPI main application
├── market_genome_page.html    # Main page UI
├── models.py                  # Pydantic models
├── start_simple.py            # Startup script
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔐 Security Notes

- Never commit your `.env` file to version control
- Use app-specific passwords for Gmail SMTP
- Keep your API keys secure
- The `.env` file is excluded via `.gitignore`

## 🌐 Deployment

### Deploy to Render.com (Recommended - FREE)

1. **Fork/Clone this repository**

2. **Go to [Render.com](https://render.com)** and sign up

3. **Create a New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `Genome-AI` repository

4. **Configure the service**
   - **Name**: genome-ai (or your preferred name)
   - **Region**: Choose closest to you
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn market_genome_main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

5. **Add Environment Variables**
   Click "Advanced" → "Add Environment Variable" and add:
   ```
   OPENAI_API_KEY=your-openai-key
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SENDER_EMAIL=your-email@gmail.com
   SENDER_NAME=Genome AI
   ```

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (3-5 minutes)
   - Your app will be live at: `https://your-app-name.onrender.com`

### Alternative: Deploy to Railway.app

1. Go to [Railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose `Genome-AI` repository
5. Add environment variables (same as above)
6. Railway will auto-detect and deploy!

### Deploy to Vercel (Not Recommended)

⚠️ Vercel has limitations for FastAPI apps (10s timeout, serverless only). Use Render or Railway instead.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👤 Author

**Amaan**
- GitHub: [@amaancoderx](https://github.com/amaancoderx)

## 🙏 Acknowledgments

- OpenAI for GPT-4 and DALL-E 3 APIs
- FastAPI for the excellent web framework
- The open-source community

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ by Amaan**

🤖 Generated with AI-Powered Marketing Intelligence
