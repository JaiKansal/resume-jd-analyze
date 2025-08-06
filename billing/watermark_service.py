"""
Watermark service for free tier PDF reports
Adds watermarks to PDF reports for free users and provides upgrade prompts
"""

import logging
from typing import Optional, Tuple
from io import BytesIO
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from auth.models import User, PlanType
from auth.services import subscription_service

logger = logging.getLogger(__name__)

class WatermarkService:
    """Service for adding watermarks to PDF reports for free tier users"""
    
    def __init__(self):
        self.watermark_text = "Resume + JD Analyzer - Free Plan"
        self.upgrade_message = "Upgrade to Professional to remove this watermark"
    
    def should_add_watermark(self, user: User) -> bool:
        """Check if watermark should be added based on user's plan"""
        subscription = subscription_service.get_user_subscription(user.id)
        
        if not subscription:
            return True
        
        # Add watermark for free plan users
        return subscription.plan.plan_type == PlanType.FREE
    
    def create_watermarked_pdf(self, content: str, title: str, user: User) -> Optional[bytes]:
        """Create PDF with watermark for free tier users"""
        if not PDF_AVAILABLE:
            logger.error("ReportLab not available for PDF generation")
            return None
        
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Create styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2E86AB')
            )
            
            # Build story (content)
            story = []
            
            # Add watermark notice at the top
            watermark_style = ParagraphStyle(
                'Watermark',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.red,
                alignment=TA_CENTER,
                spaceAfter=20,
                borderWidth=1,
                borderColor=colors.red,
                borderPadding=10
            )
            
            watermark_notice = f"""
            <b>🔒 FREE PLAN REPORT</b><br/>
            This report was generated using the free plan of Resume + JD Analyzer.<br/>
            <b>Upgrade to Professional to remove this watermark and unlock premium features.</b><br/>
            Visit our website to upgrade: https://resume-analyzer.com/upgrade
            """
            
            story.append(Paragraph(watermark_notice, watermark_style))
            story.append(Spacer(1, 20))
            
            # Add title
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 20))
            
            # Add content
            content_style = styles['Normal']
            content_paragraphs = content.split('\n\n')
            
            for paragraph in content_paragraphs:
                if paragraph.strip():
                    story.append(Paragraph(paragraph.strip(), content_style))
                    story.append(Spacer(1, 12))
            
            # Add footer with upgrade prompt
            story.append(Spacer(1, 30))
            
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER,
                borderWidth=1,
                borderColor=colors.grey,
                borderPadding=10
            )
            
            footer_text = f"""
            <b>Want more features?</b><br/>
            • Unlimited analyses • Premium AI models • All export formats<br/>
            • Priority processing • Email support • No watermarks<br/>
            <b>Upgrade to Professional for just $19/month</b><br/>
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Resume + JD Analyzer Free Plan
            """
            
            story.append(Paragraph(footer_text, footer_style))
            
            # Build PDF with custom page template for watermarks
            doc.build(story, onFirstPage=self._add_page_watermark, 
                     onLaterPages=self._add_page_watermark)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create watermarked PDF: {e}")
            return None
    
    def _add_page_watermark(self, canvas_obj, doc):
        """Add watermark to each page"""
        try:
            # Save the current state
            canvas_obj.saveState()
            
            # Add diagonal watermark text
            canvas_obj.setFont("Helvetica-Bold", 40)
            canvas_obj.setFillColor(colors.lightgrey)
            canvas_obj.setFillAlpha(0.3)
            
            # Rotate and position watermark
            canvas_obj.rotate(45)
            
            # Use drawString instead of drawCentredString for better compatibility
            canvas_obj.drawString(300, -100, "FREE PLAN")
            canvas_obj.drawString(250, -150, "UPGRADE TO REMOVE")
            
            # Add small watermark in corner
            canvas_obj.rotate(-45)  # Reset rotation
            canvas_obj.setFont("Helvetica", 8)
            canvas_obj.setFillColor(colors.red)
            canvas_obj.setFillAlpha(1.0)
            canvas_obj.drawString(72, 750, "Resume + JD Analyzer - Free Plan")
            
            # Restore the state
            canvas_obj.restoreState()
            
        except Exception as e:
            logger.error(f"Failed to add page watermark: {e}")
            # Continue without watermark rather than failing
    
    def create_upgrade_prompt_pdf(self, user: User) -> Optional[bytes]:
        """Create a PDF that's just an upgrade prompt for exceeded users"""
        if not PDF_AVAILABLE:
            return None
        
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            styles = getSampleStyleSheet()
            
            # Title style
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#FF6B35')
            )
            
            # Content style
            content_style = ParagraphStyle(
                'Content',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=20,
                alignment=TA_CENTER
            )
            
            # Build content
            story = []
            
            # Title
            story.append(Paragraph("🔒 Monthly Limit Reached", title_style))
            story.append(Spacer(1, 30))
            
            # Main message
            main_message = """
            <b>You've reached your monthly limit of 3 free analyses.</b><br/><br/>
            
            Don't let this stop your progress! Upgrade to Professional and get:<br/><br/>
            
            ✅ <b>Unlimited analyses</b> - Never hit a limit again<br/>
            ✅ <b>Premium AI models</b> - 40% more accurate results<br/>
            ✅ <b>All export formats</b> - CSV, PDF, Word, JSON<br/>
            ✅ <b>Priority processing</b> - Faster results<br/>
            ✅ <b>Email support</b> - Get help when you need it<br/>
            ✅ <b>No watermarks</b> - Professional reports<br/><br/>
            
            <b>Special Offer: Start your 14-day free trial today!</b><br/>
            No credit card required for trial.
            """
            
            story.append(Paragraph(main_message, content_style))
            story.append(Spacer(1, 40))
            
            # Pricing table
            pricing_data = [
                ['Plan', 'Price', 'Analyses', 'Features'],
                ['Free', '$0/month', '3 per month', 'Basic features'],
                ['Professional', '$19/month', 'Unlimited', 'All premium features'],
                ['Business', '$99/month', 'Unlimited', 'Team features + API']
            ]
            
            pricing_table = Table(pricing_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 2*inch])
            pricing_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            
            story.append(pricing_table)
            story.append(Spacer(1, 30))
            
            # Call to action
            cta_style = ParagraphStyle(
                'CTA',
                parent=styles['Normal'],
                fontSize=16,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#FF6B35'),
                borderWidth=2,
                borderColor=colors.HexColor('#FF6B35'),
                borderPadding=15
            )
            
            cta_text = """
            <b>Ready to upgrade?</b><br/>
            Visit: https://resume-analyzer.com/upgrade<br/>
            Or contact us at: support@resume-analyzer.com<br/>
            Phone: 1-800-RESUME-1
            """
            
            story.append(Paragraph(cta_text, cta_style))
            
            # Build PDF
            doc.build(story)
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create upgrade prompt PDF: {e}")
            return None
    
    def get_watermark_notice_text(self) -> str:
        """Get text notice about watermarks for UI display"""
        return """
        📄 **Free Plan Notice**: PDF reports include watermarks and upgrade prompts. 
        Upgrade to Professional to get clean, professional reports without watermarks.
        """
    
    def get_file_size_limit_mb(self, user: User) -> int:
        """Get file size limit based on user's plan"""
        subscription = subscription_service.get_user_subscription(user.id)
        
        if not subscription:
            return 5  # 5MB for unsubscribed users
        
        # File size limits by plan
        limits = {
            PlanType.FREE: 5,           # 5MB
            PlanType.PROFESSIONAL: 50,  # 50MB
            PlanType.BUSINESS: 100,     # 100MB
            PlanType.ENTERPRISE: 500    # 500MB
        }
        
        return limits.get(subscription.plan.plan_type, 5)
    
    def check_file_size_limit(self, user: User, file_size_mb: float) -> Tuple[bool, Optional[str]]:
        """Check if file size is within user's plan limits"""
        limit = self.get_file_size_limit_mb(user)
        
        if file_size_mb > limit:
            subscription = subscription_service.get_user_subscription(user.id)
            current_plan = subscription.plan.plan_type if subscription else PlanType.FREE
            
            if current_plan == PlanType.FREE:
                message = f"File size ({file_size_mb:.1f}MB) exceeds free plan limit ({limit}MB). Upgrade to Professional for 50MB limit."
            else:
                message = f"File size ({file_size_mb:.1f}MB) exceeds your plan limit ({limit}MB). Contact support for higher limits."
            
            return False, message
        
        return True, None

# Service instance
watermark_service = WatermarkService()