-- Customer Feedback and Support System Migration
-- This migration adds tables for feedback collection, support tickets, and knowledge base

-- Feedback submissions table - In-app feedback and surveys
CREATE TABLE feedback_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) CHECK (feedback_type IN ('bug_report', 'feature_request', 'general_feedback', 'survey_response', 'rating')) NOT NULL,
    category VARCHAR(100), -- UI/UX, Performance, Feature, Billing, etc.
    title VARCHAR(255),
    description TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5), -- For rating feedback
    page_url VARCHAR(500), -- Where feedback was submitted from
    user_agent TEXT,
    browser_info JSONB, -- Browser and device information
    screenshot_url VARCHAR(500), -- Optional screenshot
    metadata JSONB, -- Additional context data
    status VARCHAR(50) CHECK (status IN ('new', 'reviewed', 'in_progress', 'resolved', 'closed')) DEFAULT 'new',
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'critical')) DEFAULT 'medium',
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Support tickets table - Customer support requests
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_number VARCHAR(20) UNIQUE NOT NULL, -- Human-readable ticket number
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100), -- Technical, Billing, Account, Feature, etc.
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
    status VARCHAR(50) CHECK (status IN ('open', 'in_progress', 'waiting_customer', 'resolved', 'closed')) DEFAULT 'open',
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL, -- Support agent
    first_response_at TIMESTAMP,
    resolved_at TIMESTAMP,
    closed_at TIMESTAMP,
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
    satisfaction_feedback TEXT,
    tags TEXT[], -- Array of tags for categorization
    metadata JSONB, -- Additional ticket data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Support ticket messages table - Conversation history
CREATE TABLE support_ticket_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID REFERENCES support_tickets(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id) ON DELETE SET NULL,
    sender_type VARCHAR(20) CHECK (sender_type IN ('customer', 'agent', 'system')) NOT NULL,
    message_type VARCHAR(20) CHECK (message_type IN ('text', 'attachment', 'internal_note')) DEFAULT 'text',
    content TEXT NOT NULL,
    attachments JSONB, -- Array of attachment URLs and metadata
    is_internal BOOLEAN DEFAULT FALSE, -- Internal notes not visible to customer
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge base articles table
CREATE TABLE knowledge_base_articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    category VARCHAR(100),
    tags TEXT[],
    author_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(20) CHECK (status IN ('draft', 'published', 'archived')) DEFAULT 'draft',
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,
    search_keywords TEXT, -- For search optimization
    meta_description VARCHAR(160),
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge base article views table - Track article usage
CREATE TABLE knowledge_base_views (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID REFERENCES knowledge_base_articles(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    ip_address INET,
    user_agent TEXT,
    referrer VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Live chat sessions table
CREATE TABLE live_chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(20) CHECK (status IN ('waiting', 'active', 'ended', 'transferred')) DEFAULT 'waiting',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    wait_time_seconds INTEGER,
    duration_seconds INTEGER,
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
    satisfaction_feedback TEXT,
    metadata JSONB
);

-- Live chat messages table
CREATE TABLE live_chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES live_chat_sessions(id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id) ON DELETE SET NULL,
    sender_type VARCHAR(20) CHECK (sender_type IN ('customer', 'agent', 'system')) NOT NULL,
    message_type VARCHAR(20) CHECK (message_type IN ('text', 'attachment', 'system_message')) DEFAULT 'text',
    content TEXT NOT NULL,
    attachments JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customer satisfaction surveys table
CREATE TABLE satisfaction_surveys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    survey_type VARCHAR(50) CHECK (survey_type IN ('nps', 'csat', 'ces', 'onboarding', 'feature_feedback')) NOT NULL,
    trigger_event VARCHAR(100), -- What triggered the survey
    questions JSONB NOT NULL, -- Survey questions and structure
    responses JSONB, -- User responses
    overall_score DECIMAL(3,2), -- Calculated overall score
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Support metrics table - Track response times and performance
CREATE TABLE support_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- first_response_time, resolution_time, satisfaction, etc.
    metric_value DECIMAL(10,2) NOT NULL,
    category VARCHAR(100), -- Optional category breakdown
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, metric_type, category)
);

-- Indexes for performance
CREATE INDEX idx_feedback_submissions_user_id ON feedback_submissions(user_id);
CREATE INDEX idx_feedback_submissions_status ON feedback_submissions(status);
CREATE INDEX idx_feedback_submissions_created_at ON feedback_submissions(created_at);
CREATE INDEX idx_feedback_submissions_type ON feedback_submissions(feedback_type);

CREATE INDEX idx_support_tickets_user_id ON support_tickets(user_id);
CREATE INDEX idx_support_tickets_status ON support_tickets(status);
CREATE INDEX idx_support_tickets_assigned_to ON support_tickets(assigned_to);
CREATE INDEX idx_support_tickets_created_at ON support_tickets(created_at);
CREATE INDEX idx_support_tickets_ticket_number ON support_tickets(ticket_number);

CREATE INDEX idx_support_ticket_messages_ticket_id ON support_ticket_messages(ticket_id);
CREATE INDEX idx_support_ticket_messages_created_at ON support_ticket_messages(created_at);

CREATE INDEX idx_knowledge_base_articles_status ON knowledge_base_articles(status);
CREATE INDEX idx_knowledge_base_articles_category ON knowledge_base_articles(category);
CREATE INDEX idx_knowledge_base_articles_slug ON knowledge_base_articles(slug);
CREATE INDEX idx_knowledge_base_articles_published_at ON knowledge_base_articles(published_at);

CREATE INDEX idx_knowledge_base_views_article_id ON knowledge_base_views(article_id);
CREATE INDEX idx_knowledge_base_views_user_id ON knowledge_base_views(user_id);
CREATE INDEX idx_knowledge_base_views_created_at ON knowledge_base_views(created_at);

CREATE INDEX idx_live_chat_sessions_user_id ON live_chat_sessions(user_id);
CREATE INDEX idx_live_chat_sessions_agent_id ON live_chat_sessions(agent_id);
CREATE INDEX idx_live_chat_sessions_status ON live_chat_sessions(status);
CREATE INDEX idx_live_chat_sessions_started_at ON live_chat_sessions(started_at);

CREATE INDEX idx_live_chat_messages_session_id ON live_chat_messages(session_id);
CREATE INDEX idx_live_chat_messages_created_at ON live_chat_messages(created_at);

CREATE INDEX idx_satisfaction_surveys_user_id ON satisfaction_surveys(user_id);
CREATE INDEX idx_satisfaction_surveys_survey_type ON satisfaction_surveys(survey_type);
CREATE INDEX idx_satisfaction_surveys_created_at ON satisfaction_surveys(created_at);

CREATE INDEX idx_support_metrics_date ON support_metrics(date);
CREATE INDEX idx_support_metrics_type ON support_metrics(metric_type);

-- Add updated_at triggers
CREATE TRIGGER update_feedback_submissions_updated_at BEFORE UPDATE ON feedback_submissions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_support_tickets_updated_at BEFORE UPDATE ON support_tickets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_knowledge_base_articles_updated_at BEFORE UPDATE ON knowledge_base_articles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to generate ticket numbers
CREATE OR REPLACE FUNCTION generate_ticket_number()
RETURNS TEXT AS $$
DECLARE
    ticket_num TEXT;
    counter INTEGER;
BEGIN
    -- Get current date in YYYYMMDD format
    ticket_num := 'TKT-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-';
    
    -- Get count of tickets created today
    SELECT COUNT(*) + 1 INTO counter
    FROM support_tickets 
    WHERE DATE(created_at) = CURRENT_DATE;
    
    -- Pad with zeros to make 4 digits
    ticket_num := ticket_num || LPAD(counter::TEXT, 4, '0');
    
    RETURN ticket_num;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-generate ticket numbers
CREATE OR REPLACE FUNCTION set_ticket_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ticket_number IS NULL THEN
        NEW.ticket_number := generate_ticket_number();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_support_ticket_number 
    BEFORE INSERT ON support_tickets 
    FOR EACH ROW EXECUTE FUNCTION set_ticket_number();

-- Insert sample knowledge base articles
INSERT INTO knowledge_base_articles (title, slug, content, excerpt, category, status, published_at) VALUES
('Getting Started with Resume Analysis', 'getting-started-resume-analysis', 
'# Getting Started with Resume Analysis

Welcome to Resume + JD Analyzer! This guide will help you get started with analyzing your resume against job descriptions.

## Step 1: Upload Your Resume
- Click on the "Upload Resume" section
- Select a PDF file of your resume
- Make sure the file is under the size limit for your plan

## Step 2: Add Job Description
- Copy and paste the job description you want to analyze against
- Include the full job posting for best results
- You can also upload a text file with the job description

## Step 3: Run Analysis
- Click "Analyze Compatibility" to start the process
- Wait for the AI to process your documents (usually 10-30 seconds)
- Review your results and recommendations

## Understanding Your Results
- **Compatibility Score**: Overall match percentage
- **Matching Skills**: Skills found in both your resume and the job description
- **Skill Gaps**: Important skills mentioned in the job that are missing from your resume
- **Recommendations**: Specific suggestions to improve your resume

For more detailed help, contact our support team!',
'Learn how to analyze your resume against job descriptions with our step-by-step guide.',
'Getting Started', 'published', CURRENT_TIMESTAMP),

('Understanding Your Analysis Results', 'understanding-analysis-results',
'# Understanding Your Analysis Results

After running an analysis, you''ll receive a comprehensive report. Here''s how to interpret each section:

## Compatibility Score
The compatibility score is calculated based on:
- Skill matches between resume and job description
- Experience level alignment
- Education requirements
- Industry-specific terminology

## Score Ranges:
- **70-100%**: Strong match - you''re well-qualified
- **40-69%**: Moderate match - some gaps to address
- **0-39%**: Poor match - significant improvements needed

## Skill Gaps Analysis
We categorize missing skills into three levels:
- **Critical**: Must-have skills for the role
- **Important**: Valuable skills that strengthen your application
- **Nice-to-have**: Bonus skills that could set you apart

## Recommendations
Our AI provides specific, actionable recommendations to:
- Add missing keywords to your resume
- Highlight relevant experience
- Improve formatting and structure
- Tailor your resume for the specific role

Use these insights to optimize your resume before applying!',
'Learn how to interpret your analysis results and improve your job application success.',
'Analysis Results', 'published', CURRENT_TIMESTAMP),

('Subscription Plans and Features', 'subscription-plans-features',
'# Subscription Plans and Features

Choose the plan that best fits your needs:

## Free Tier
- 3 analyses per month
- Basic job seeker reports
- PDF download (watermarked)
- Community support

## Professional ($19/month)
- Unlimited analyses
- Both job seeker and company reports
- All download formats (PDF, CSV, Word)
- Priority processing
- Email support
- Resume template library

## Business ($99/month for 5 seats)
- Team collaboration features
- Bulk upload and processing
- Advanced analytics dashboard
- API access
- Integration support
- Phone support
- Custom branding

## Enterprise (Custom pricing)
- Unlimited seats and usage
- SSO and security features
- Custom integrations
- Dedicated customer success
- SLA guarantees
- On-premise deployment
- White-label licensing

## Upgrading Your Plan
You can upgrade your plan at any time from your account settings. Upgrades take effect immediately, and you''ll be prorated for the remaining billing period.

## Need Help Choosing?
Contact our sales team for a personalized recommendation based on your needs.',
'Compare our subscription plans and find the right fit for your resume analysis needs.',
'Billing', 'published', CURRENT_TIMESTAMP);