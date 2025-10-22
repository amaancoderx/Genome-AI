"""
Market Genome - AI Marketing Strategy Builder
Analyzes brands from real data and creates complete marketing DNA
"""

from fastapi import FastAPI, Form, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
from typing import Dict, Optional
from pydantic import EmailStr, BaseModel
from datetime import datetime

from config import settings, ensure_directories
from models import JobStatus

# Create FastAPI app
app = FastAPI(
    title="Market Genome - AI Marketing Strategy Builder",
    description="Analyze any brand and get a complete Marketing Genome Report",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage
genome_jobs: Dict[str, dict] = {}

# In-memory chat session storage
chat_sessions: Dict[str, dict] = {}

ensure_directories()


# Pydantic models for chat
class ChatInitRequest(BaseModel):
    brand_handle: str


class ChatMessageRequest(BaseModel):
    session_id: str
    message: str


class ChatReportRequest(BaseModel):
    session_id: str
    email: str


@app.on_event("startup")
async def startup_event():
    """Initialize app"""
    print("=" * 60)
    print("MARKET GENOME - AI Marketing Strategy Builder")
    print("=" * 60)
    print("")
    print("Capabilities:")
    print("   - Brand DNA Analysis")
    print("   - Competitor Intelligence")
    print("   - Growth Roadmap Generation")
    print("   - Content Strategy Blueprint")
    print("")
    print(f"API: http://localhost:{settings.api_port}")
    print(f"Docs: http://localhost:{settings.api_port}/docs")
    print(f"UI: http://localhost:{settings.api_port}/")
    print("")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the Market Genome UI"""
    html_file = os.path.join(os.path.dirname(__file__), "market_genome_page.html")
    with open(html_file, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/chat", response_class=HTMLResponse)
async def chat_interface():
    """Serve the Chat Interface"""
    html_file = os.path.join(os.path.dirname(__file__), "chat_interface.html")
    with open(html_file, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Market Genome",
        "status": "running",
        "version": "1.0.0",
        "tagline": "Build marketing strategy from real brand DNA",
        "features": [
            "Brand personality analysis",
            "Competitor weakness mapping",
            "Growth roadmap creation",
            "Content pillar strategy"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy"}


async def analyze_brand_genome(
    job_id: str,
    brand_input: str,
    input_type: str,
    email: str
):
    """
    Background task: Analyze brand and generate Marketing Genome Report

    Steps:
    1. Scrape brand data (website, social, reviews)
    2. AI analysis - extract brand DNA
    3. Competitor analysis
    4. Generate growth strategy
    5. Create PDF report
    6. Email to user
    """
    try:
        genome_jobs[job_id]['status'] = JobStatus.PROCESSING
        genome_jobs[job_id]['message'] = 'Analyzing brand data...'

        from market_genome_engine import MarketGenomeEngine
        from email_service import EmailService

        print(f"\n[{job_id}] Starting Market Genome Analysis")
        print(f"[{job_id}] Brand: {brand_input}")
        print(f"[{job_id}] Type: {input_type}")

        # Initialize engine
        engine = MarketGenomeEngine()
        email_service = EmailService()

        # Step 1: Data Collection
        print(f"[{job_id}] Step 1: Collecting brand data...")
        genome_jobs[job_id]['message'] = 'Collecting brand data from multiple sources...'

        brand_data = engine.collect_brand_data(
            brand_input=brand_input,
            input_type=input_type
        )

        # Step 2: AI Analysis
        print(f"[{job_id}] Step 2: Analyzing brand DNA...")
        genome_jobs[job_id]['message'] = 'Analyzing brand personality and positioning...'

        brand_dna = engine.analyze_brand_dna(brand_data)

        # Step 3: Competitor Analysis
        print(f"[{job_id}] Step 3: Mapping competitors...")
        genome_jobs[job_id]['message'] = 'Analyzing competitor landscape...'

        competitor_intel = engine.analyze_competitors(brand_data, brand_dna)

        # Step 4: Growth Strategy
        print(f"[{job_id}] Step 4: Creating growth roadmap...")
        genome_jobs[job_id]['message'] = 'Generating growth strategy...'

        growth_roadmap = engine.create_growth_roadmap(brand_dna, competitor_intel)

        # Step 5: Content Strategy
        print(f"[{job_id}] Step 5: Building content pillars...")
        genome_jobs[job_id]['message'] = 'Creating content strategy...'

        content_strategy = engine.create_content_strategy(brand_dna)

        # Step 6: Generate PDF Report
        print(f"[{job_id}] Step 6: Generating PDF report...")
        genome_jobs[job_id]['message'] = 'Creating Marketing Genome Report...'

        pdf_path = engine.generate_genome_report(
            job_id=job_id,
            brand_name=brand_data['brand_name'],
            brand_dna=brand_dna,
            competitor_intel=competitor_intel,
            growth_roadmap=growth_roadmap,
            content_strategy=content_strategy
        )

        genome_jobs[job_id]['pdf_path'] = pdf_path
        genome_jobs[job_id]['pdf_url'] = f"/api/download/report/{job_id}"

        # Step 7: Send Email
        print(f"[{job_id}] Step 7: Sending report via email...")
        genome_jobs[job_id]['message'] = 'Sending Marketing Genome Report...'

        email_sent = email_service.send_genome_report_email(
            to_email=email,
            brand_input=brand_input,
            report_path=pdf_path
        )

        genome_jobs[job_id]['email_sent'] = email_sent

        # Complete
        genome_jobs[job_id]['status'] = JobStatus.COMPLETED
        genome_jobs[job_id]['message'] = 'Marketing Genome Report generated successfully!'
        genome_jobs[job_id]['completed_at'] = datetime.now().isoformat()

        print(f"[{job_id}] SUCCESS - Complete! Report sent to {email}")

    except Exception as e:
        error_msg = f"Error generating genome: {str(e)}"
        print(f"[{job_id}] ERROR - {error_msg}")

        genome_jobs[job_id]['status'] = JobStatus.FAILED
        genome_jobs[job_id]['message'] = error_msg

        # Send error email
        try:
            email_service = EmailService()
            email_service.send_error_email(email, brand_input, str(e))
        except:
            pass


@app.post("/api/analyze")
async def analyze_brand(
    background_tasks: BackgroundTasks,
    brand_input: str = Form(..., description="Brand name, website URL, or social handle"),
    input_type: str = Form("auto", description="Type: website, instagram, twitter, brand_name, auto"),
    email: EmailStr = Form(..., description="Email to receive the Marketing Genome Report")
):
    """
    Analyze a brand and generate Marketing Genome Report

    Args:
        brand_input: Brand name, website URL, or social media handle
        input_type: Type of input (auto-detected if not specified)
        email: Email address to receive the PDF report

    Returns:
        Job ID to track progress
    """

    # Validate input
    if len(brand_input) < 3:
        raise HTTPException(
            status_code=400,
            detail="Brand input too short. Please provide a brand name, website, or social handle."
        )

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Initialize job
    genome_jobs[job_id] = {
        'job_id': job_id,
        'status': JobStatus.PENDING,
        'message': 'Analysis starting...',
        'brand_input': brand_input,
        'input_type': input_type,
        'email': email,
        'created_at': datetime.now().isoformat(),
        'pdf_url': None,
        'email_sent': False
    }

    # Start background analysis
    background_tasks.add_task(
        analyze_brand_genome,
        job_id,
        brand_input,
        input_type,
        email
    )

    print(f"\nSUCCESS - Genome analysis started: {job_id}")
    print(f"   Brand: {brand_input}")

    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Marketing Genome analysis started. Report will be emailed when complete.",
        "estimated_time": "3-5 minutes"
    }


@app.get("/api/status/{job_id}")
async def get_genome_status(job_id: str):
    """Get analysis status"""

    if job_id not in genome_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = genome_jobs[job_id]

    return {
        "job_id": job_id,
        "status": job['status'],
        "message": job['message'],
        "brand_input": job.get('brand_input'),
        "pdf_url": job.get('pdf_url'),
        "email_sent": job.get('email_sent', False),
        "created_at": job.get('created_at'),
        "completed_at": job.get('completed_at')
    }


@app.get("/api/jobs")
async def list_genome_jobs():
    """List all genome analysis jobs"""
    return {
        "total_jobs": len(genome_jobs),
        "jobs": [
            {
                "job_id": job_id,
                "status": job['status'],
                "brand": job.get('brand_input', ''),
                "created_at": job.get('created_at')
            }
            for job_id, job in genome_jobs.items()
        ]
    }


@app.get("/api/download/report/{job_id}")
async def download_report(job_id: str):
    """Download Marketing Genome Report PDF"""
    from fastapi.responses import FileResponse

    if job_id not in genome_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    pdf_path = genome_jobs[job_id].get('pdf_path')

    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"marketing_genome_{job_id}.pdf"
    )


# ===================================================================
# CHAT API ENDPOINTS - Personal Brand AI Assistant
# ===================================================================

@app.post("/api/chat/init")
async def initialize_chat(request: ChatInitRequest):
    """
    Initialize a chat session with brand AI assistant.
    No authentication required - connects based on brand handle.

    Args:
        brand_handle: Instagram handle, website, or brand name

    Returns:
        Session ID and welcome message
    """
    from brand_ai_assistant import PixaroBrandAssistant

    try:
        # Generate session ID
        session_id = str(uuid.uuid4())

        # Try to load existing brand context if available
        brand_context = None

        # Check if there's a recent genome analysis for this brand
        for job_id, job in genome_jobs.items():
            if (job.get('brand_input', '').lower() == request.brand_handle.lower() and
                job.get('status') == JobStatus.COMPLETED):
                # Load the brand context from previous analysis
                # This gives the AI more context about the brand
                brand_context = {
                    'brand_dna': job.get('brand_dna', {}),
                    'audience': job.get('audience', {}),
                    'competitors': job.get('competitors', {})
                }
                break

        # Initialize AI assistant
        assistant = PixaroBrandAssistant(
            brand_handle=request.brand_handle,
            brand_context=brand_context
        )

        # Store session
        chat_sessions[session_id] = {
            'session_id': session_id,
            'brand_handle': request.brand_handle,
            'assistant': assistant,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }

        welcome_message = f"""Hi! I'm your personal AI strategist for **{request.brand_handle}**.

I can help you with:
- Content creation (Instagram posts, captions, campaigns)
- Audience insights and personas
- Competitor analysis
- Growth strategies
- Engagement predictions
- Weekly content planning

What would you like to work on today?"""

        print(f"\nSUCCESS - Chat session started: {session_id}")
        print(f"   Brand: {request.brand_handle}")

        return {
            "session_id": session_id,
            "brand_handle": request.brand_handle,
            "welcome_message": welcome_message,
            "has_context": brand_context is not None
        }

    except Exception as e:
        print(f"ERROR - Chat init failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize chat: {str(e)}")


@app.post("/api/chat/message")
async def send_chat_message(request: ChatMessageRequest):
    """
    Send a message to the brand AI assistant.

    Args:
        session_id: Active chat session ID
        message: User's message/question

    Returns:
        AI response with action type and metadata
    """
    try:
        # Validate session
        if request.session_id not in chat_sessions:
            raise HTTPException(status_code=404, detail="Session not found. Please initialize chat first.")

        session = chat_sessions[request.session_id]
        assistant = session['assistant']

        # Update last activity
        session['last_activity'] = datetime.now().isoformat()

        # Get AI response
        response_data = assistant.chat(request.message)

        print(f"\n[{request.session_id[:8]}] User: {request.message[:50]}...")
        print(f"[{request.session_id[:8]}] AI: {response_data['response'][:50]}...")

        return {
            "session_id": request.session_id,
            "response": response_data['response'],
            "action_type": response_data.get('action_type', 'general_chat'),
            "needs_report": response_data.get('needs_report', False),
            "image_url": response_data.get('image_url'),
            "timestamp": response_data.get('timestamp')
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR - Chat message failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/api/chat/generate-report")
async def generate_chat_report(request: ChatReportRequest, background_tasks: BackgroundTasks):
    """
    Generate and email a comprehensive report based on chat conversation.

    Args:
        session_id: Active chat session ID
        email: Email to send report to

    Returns:
        Job ID for report generation
    """
    try:
        # Validate session
        if request.session_id not in chat_sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = chat_sessions[request.session_id]
        brand_handle = session['brand_handle']

        # Create a genome analysis job for this brand
        job_id = str(uuid.uuid4())

        genome_jobs[job_id] = {
            'job_id': job_id,
            'status': JobStatus.PENDING,
            'message': 'Generating report from chat session...',
            'brand_input': brand_handle,
            'input_type': 'auto',
            'email': request.email,
            'created_at': datetime.now().isoformat(),
            'pdf_url': None,
            'email_sent': False,
            'from_chat': True,
            'chat_session_id': request.session_id
        }

        # Start background report generation
        background_tasks.add_task(
            analyze_brand_genome,
            job_id,
            brand_handle,
            'auto',
            request.email
        )

        print(f"\nSUCCESS - Chat report started: {job_id}")
        print(f"   Brand: {brand_handle}")
        print(f"   Email: {request.email}")

        return {
            "success": True,
            "job_id": job_id,
            "message": f"Report is being generated for {brand_handle} and will be sent to {request.email}",
            "estimated_time": "3-5 minutes"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR - Report generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")


@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get conversation history for a session."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = chat_sessions[session_id]
    assistant = session['assistant']

    return {
        "session_id": session_id,
        "brand_handle": session['brand_handle'],
        "conversation": assistant.get_conversation_history(),
        "created_at": session['created_at'],
        "last_activity": session['last_activity']
    }


@app.delete("/api/chat/session/{session_id}")
async def end_chat_session(session_id: str):
    """End a chat session and optionally export conversation."""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = chat_sessions[session_id]
    assistant = session['assistant']

    # Export conversation before deleting
    try:
        export_path = assistant.export_conversation()
        print(f"\nINFO - Chat session exported: {export_path}")
    except Exception as e:
        print(f"WARN - Failed to export conversation: {str(e)}")
        export_path = None

    # Remove session
    del chat_sessions[session_id]

    return {
        "success": True,
        "message": "Chat session ended",
        "export_path": export_path
    }


@app.get("/api/chat/sessions")
async def list_chat_sessions():
    """List all active chat sessions."""
    return {
        "total_sessions": len(chat_sessions),
        "sessions": [
            {
                "session_id": sid,
                "brand_handle": session['brand_handle'],
                "created_at": session['created_at'],
                "last_activity": session['last_activity']
            }
            for sid, session in chat_sessions.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "market_genome_main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
