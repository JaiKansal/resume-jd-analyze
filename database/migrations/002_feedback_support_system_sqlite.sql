-- Customer Feedback and Support System Migration (SQLite Compatible)
-- This migration adds tables for feedback collection, support tickets, and knowledge base

-- Feedback submissions table - In-app feedback and surveys
CREATE TABLE IF NOT EXISTS feedback_submissions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    feedback_type TEXT CHECK (feedback_type IN ('bug_report', 'feature_request', 'general_feedback', 'survey_response', 'rating')) NOT NULL,
    category TEXT, -- UI/UX, Performance, Feature, Billing, etc.
    title TEXT,
    description TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5), -- For rating feedback
    page_url TEXT, -- Where feedback was submitted from
    user_agent TEXT,
    browser_info TEXT, -- JSON string
    screenshot_url TEXT, -- Optional screenshot
    metadata TEXT, -- JSON string - Additional context data
    status TEXT CHECK (status IN ('new', 'reviewed', 'in_progress', 'resolved', 'closed')) DEFAULT 'new',
    priority TEXT CHECK (priority IN ('low', 'medium', 'high', 'critical')) DEFAULT 'medium',
    assigned_to TEXT,
    resolved_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

-- Support tickets table - Customer support requests
CREATE TABLE IF NOT EXISTS support_tickets (
    id TEXT PRIMARY KEY,
    ticket_number TEXT UNIQUE NOT NULL, -- Human-readable ticket number
    user_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT, -- Technical, Billing, Account, Feature, etc.
    priority TEXT CHECK (priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
    status TEXT CHECK (status IN ('open', 'in_progress', 'waiting_customer', 'resolved', 'closed')) DEFAULT 'open',
    assigned_to TEXT, -- Support agent
    first_response_at TEXT,
    resolved_at TEXT,
    closed_at TEXT,
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
    satisfaction_feedback TEXT,
    tags TEXT, -- JSON array of tags for categorization
    metadata TEXT, -- JSON - Additional ticket data
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

-- Support ticket messages table - Conversation history
CREATE TABLE IF NOT EXISTS support_ticket_messages (
    id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL,
    sender_id TEXT,
    sender_type TEXT CHECK (sender_type IN ('customer', 'agent', 'system')) NOT NULL,
    message_type TEXT CHECK (message_type IN ('text', 'attachment', 'internal_note')) DEFAULT 'text',
    content TEXT NOT NULL,
    attachments TEXT, -- JSON array of attachment URLs and metadata
    is_internal INTEGER DEFAULT 0, -- Internal notes not visible to customer
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (ticket_id) REFERENCES support_tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Knowledge base articles table
CREATE TABLE IF NOT EXISTS knowledge_base_articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    category TEXT,
    tags TEXT, -- JSON array
    author_id TEXT,
    status TEXT CHECK (status IN ('draft', 'published', 'archived')) DEFAULT 'draft',
    view_count INTEGER DEFAULT 0,
    helpful_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,
    search_keywords TEXT, -- For search optimization
    meta_description TEXT,
    published_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Knowledge base article views table - Track article usage
CREATE TABLE IF NOT EXISTS knowledge_base_views (
    id TEXT PRIMARY KEY,
    article_id TEXT NOT NULL,
    user_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    referrer TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (article_id) REFERENCES knowledge_base_articles(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Live chat sessions table
CREATE TABLE IF NOT EXISTS live_chat_sessions (
    id TEXT PRIMARY KEY,
    session_token TEXT UNIQUE NOT NULL,
    user_id TEXT NOT NULL,
    agent_id TEXT,
    status TEXT CHECK (status IN ('waiting', 'active', 'ended', 'transferred')) DEFAULT 'waiting',
    started_at TEXT DEFAULT (datetime('now')),
    ended_at TEXT,
    wait_time_seconds INTEGER,
    duration_seconds INTEGER,
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
    satisfaction_feedback TEXT,
    metadata TEXT, -- JSON
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Live chat messages table
CREATE TABLE IF NOT EXISTS live_chat_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    sender_id TEXT,
    sender_type TEXT CHECK (sender_type IN ('customer', 'agent', 'system')) NOT NULL,
    message_type TEXT CHECK (message_type IN ('text', 'attachment', 'system_message')) DEFAULT 'text',
    content TEXT NOT NULL,
    attachments TEXT, -- JSON
    is_read INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (session_id) REFERENCES live_chat_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Customer satisfaction surveys table
CREATE TABLE IF NOT EXISTS satisfaction_surveys (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    survey_type TEXT CHECK (survey_type IN ('nps', 'csat', 'ces', 'onboarding', 'feature_feedback')) NOT NULL,
    trigger_event TEXT, -- What triggered the survey
    questions TEXT NOT NULL, -- JSON - Survey questions and structure
    responses TEXT, -- JSON - User responses
    overall_score REAL, -- Calculated overall score
    completed_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Support metrics table - Track response times and performance
CREATE TABLE IF NOT EXISTS support_metrics (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    metric_type TEXT NOT NULL, -- first_response_time, resolution_time, satisfaction, etc.
    metric_value REAL NOT NULL,
    category TEXT, -- Optional category breakdown
    metadata TEXT, -- JSON
    created_at TEXT DEFAULT (datetime('now'))
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_feedback_submissions_user_id ON feedback_submissions(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_submissions_status ON feedback_submissions(status);
CREATE INDEX IF NOT EXISTS idx_feedback_submissions_created_at ON feedback_submissions(created_at);
CREATE INDEX IF NOT EXISTS idx_feedback_submissions_type ON feedback_submissions(feedback_type);

CREATE INDEX IF NOT EXISTS idx_support_tickets_user_id ON support_tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status);
CREATE INDEX IF NOT EXISTS idx_support_tickets_assigned_to ON support_tickets(assigned_to);
CREATE INDEX IF NOT EXISTS idx_support_tickets_created_at ON support_tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_support_tickets_ticket_number ON support_tickets(ticket_number);

CREATE INDEX IF NOT EXISTS idx_support_ticket_messages_ticket_id ON support_ticket_messages(ticket_id);
CREATE INDEX IF NOT EXISTS idx_support_ticket_messages_created_at ON support_ticket_messages(created_at);

CREATE INDEX IF NOT EXISTS idx_knowledge_base_articles_status ON knowledge_base_articles(status);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_articles_category ON knowledge_base_articles(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_articles_slug ON knowledge_base_articles(slug);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_articles_published_at ON knowledge_base_articles(published_at);

CREATE INDEX IF NOT EXISTS idx_knowledge_base_views_article_id ON knowledge_base_views(article_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_views_user_id ON knowledge_base_views(user_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_views_created_at ON knowledge_base_views(created_at);

CREATE INDEX IF NOT EXISTS idx_live_chat_sessions_user_id ON live_chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_live_chat_sessions_agent_id ON live_chat_sessions(agent_id);
CREATE INDEX IF NOT EXISTS idx_live_chat_sessions_status ON live_chat_sessions(status);
CREATE INDEX IF NOT EXISTS idx_live_chat_sessions_started_at ON live_chat_sessions(started_at);

CREATE INDEX IF NOT EXISTS idx_live_chat_messages_session_id ON live_chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_live_chat_messages_created_at ON live_chat_messages(created_at);

CREATE INDEX IF NOT EXISTS idx_satisfaction_surveys_user_id ON satisfaction_surveys(user_id);
CREATE INDEX IF NOT EXISTS idx_satisfaction_surveys_survey_type ON satisfaction_surveys(survey_type);
CREATE INDEX IF NOT EXISTS idx_satisfaction_surveys_created_at ON satisfaction_surveys(created_at);

CREATE INDEX IF NOT EXISTS idx_support_metrics_date ON support_metrics(date);
CREATE INDEX IF NOT EXISTS idx_support_metrics_type ON support_metrics(metric_type);

-- Insert sample knowledge base articles
INSERT OR IGNORE INTO knowledge_base_articles (id, title, slug, content, excerpt, category, status, published_at) VALUES
('kb_001', 'Getting Started with Resume Analysis', 'getting-started-resume-analysis', 
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
'Getting Started', 'published', datetime('now'));

INSERT OR IGNORE INTO knowledge_base_articles (id, title, slug, content, excerpt, category, status, published_at) VALUES
('kb_002', 'Understanding Your Analysis Results', 'understanding-analysis-results',
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
'Analysis Results', 'published', datetime('now'));

INSERT OR IGNORE INTO knowledge_base_articles (id, title, slug, content, excerpt, category, status, published_at) VALUES
('kb_003', 'Subscription Plans and Features', 'subscription-plans-features',
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
'Billing', 'published', datetime('now'));