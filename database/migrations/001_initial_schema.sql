-- Resume + JD Analyzer - User Authentication Database Schema (SQLite)
-- This schema supports the monetization strategy with user management,
-- subscriptions, teams, and usage tracking

-- Users table - Core user authentication and profile information
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(255),
    role VARCHAR(50) CHECK (role IN ('individual', 'hr_manager', 'admin', 'enterprise_admin')) DEFAULT 'individual',
    phone VARCHAR(20),
    country VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC',
    email_verified BOOLEAN DEFAULT 0,
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,
    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subscription plans lookup table
CREATE TABLE subscription_plans (
    id TEXT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    plan_type VARCHAR(50) CHECK (plan_type IN ('free', 'professional', 'business', 'enterprise')) NOT NULL,
    price_monthly REAL,
    price_annual REAL,
    monthly_analysis_limit INTEGER,
    features TEXT, -- Store plan features as JSON string
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subscriptions table - User subscription management
CREATE TABLE subscriptions (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    plan_id TEXT REFERENCES subscription_plans(id),
    status VARCHAR(20) CHECK (status IN ('active', 'cancelled', 'past_due', 'trialing', 'incomplete')) DEFAULT 'active',
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    trial_start TIMESTAMP,
    trial_end TIMESTAMP,
    monthly_analysis_used INTEGER DEFAULT 0,
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    cancel_at_period_end BOOLEAN DEFAULT 0,
    cancelled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Teams table - For business and enterprise accounts
CREATE TABLE teams (
    id TEXT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    subscription_id TEXT REFERENCES subscriptions(id),
    seat_limit INTEGER DEFAULT 5,
    seats_used INTEGER DEFAULT 1,
    settings TEXT, -- Team-specific settings as JSON string
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Team members table - Many-to-many relationship between users and teams
CREATE TABLE team_members (
    id TEXT PRIMARY KEY,
    team_id TEXT REFERENCES teams(id) ON DELETE CASCADE,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) CHECK (role IN ('member', 'admin', 'owner')) DEFAULT 'member',
    permissions TEXT, -- Member-specific permissions as JSON string
    invited_by TEXT REFERENCES users(id),
    invited_at TIMESTAMP,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    UNIQUE(team_id, user_id)
);

-- Analysis sessions table - Track usage for billing and analytics
CREATE TABLE analysis_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    team_id TEXT REFERENCES teams(id) ON DELETE SET NULL,
    session_type VARCHAR(50) CHECK (session_type IN ('single', 'bulk', 'job_matching', 'api')) DEFAULT 'single',
    resume_count INTEGER DEFAULT 1,
    job_description_count INTEGER DEFAULT 1,
    processing_time_seconds REAL,
    api_cost_usd REAL,
    tokens_used INTEGER,
    status VARCHAR(20) CHECK (status IN ('completed', 'failed', 'processing')) DEFAULT 'completed',
    error_message TEXT,
    metadata TEXT, -- Store additional session data as JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User sessions table - Track login sessions for security
CREATE TABLE user_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Revenue events table - Track all revenue-generating events
CREATE TABLE revenue_events (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    subscription_id TEXT REFERENCES subscriptions(id) ON DELETE SET NULL,
    event_type VARCHAR(50) CHECK (event_type IN ('subscription', 'upgrade', 'downgrade', 'service', 'marketplace', 'refund')) NOT NULL,
    amount_usd REAL NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    stripe_payment_id VARCHAR(255),
    stripe_invoice_id VARCHAR(255),
    description TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User engagement tracking table
CREATE TABLE user_engagement (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    sessions_count INTEGER DEFAULT 0,
    analyses_performed INTEGER DEFAULT 0,
    features_used TEXT, -- Array of feature names as JSON string
    time_spent_minutes INTEGER DEFAULT 0,
    pages_visited INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

-- Conversion events table - Track user journey and conversion funnel
CREATE TABLE conversion_events (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    event_name VARCHAR(100) NOT NULL, -- signup, first_analysis, upgrade, churn, etc.
    event_properties TEXT,
    source VARCHAR(100), -- marketing channel, referral, etc.
    medium VARCHAR(100), -- organic, paid, email, etc.
    campaign VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API keys table - For API access management
CREATE TABLE api_keys (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    key_name VARCHAR(100) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    key_prefix VARCHAR(20) NOT NULL, -- First few chars for identification
    permissions TEXT, -- API permissions and rate limits as JSON string
    rate_limit_per_minute INTEGER DEFAULT 60,
    rate_limit_per_day INTEGER DEFAULT 1000,
    last_used_at TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log table - Track important system events
CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id TEXT,
    old_values TEXT,
    new_values TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schema migrations tracking table
CREATE TABLE schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_email_verified ON users(email_verified);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_last_login ON users(last_login);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_current_period_end ON subscriptions(current_period_end);

CREATE INDEX idx_teams_owner_id ON teams(owner_id);
CREATE INDEX idx_team_members_team_id ON team_members(team_id);
CREATE INDEX idx_team_members_user_id ON team_members(user_id);

CREATE INDEX idx_analysis_sessions_user_id ON analysis_sessions(user_id);
CREATE INDEX idx_analysis_sessions_created_at ON analysis_sessions(created_at);
CREATE INDEX idx_analysis_sessions_status ON analysis_sessions(status);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

CREATE INDEX idx_revenue_events_user_id ON revenue_events(user_id);
CREATE INDEX idx_revenue_events_created_at ON revenue_events(created_at);
CREATE INDEX idx_revenue_events_event_type ON revenue_events(event_type);

CREATE INDEX idx_user_engagement_user_id ON user_engagement(user_id);
CREATE INDEX idx_user_engagement_date ON user_engagement(date);

CREATE INDEX idx_conversion_events_user_id ON conversion_events(user_id);
CREATE INDEX idx_conversion_events_event_name ON conversion_events(event_name);
CREATE INDEX idx_conversion_events_created_at ON conversion_events(created_at);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key_prefix ON api_keys(key_prefix);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Insert default subscription plans
INSERT INTO subscription_plans (id, name, plan_type, price_monthly, price_annual, monthly_analysis_limit, features) VALUES
('plan_free', 'Free Tier', 'free', 0.00, 0.00, 3, '{"pdf_download": true, "basic_reports": true, "community_support": true, "watermarked_pdfs": true}'),
('plan_professional', 'Professional', 'professional', 19.00, 190.00, -1, '{"unlimited_analyses": true, "premium_ai": true, "all_formats": true, "priority_processing": true, "email_support": true, "resume_templates": true}'),
('plan_business', 'Business', 'business', 99.00, 990.00, -1, '{"team_collaboration": true, "bulk_upload": true, "analytics_dashboard": true, "api_access": true, "integration_support": true, "phone_support": true, "custom_branding": true, "seats": 5}'),
('plan_enterprise', 'Enterprise', 'enterprise', 500.00, 5000.00, -1, '{"unlimited_seats": true, "sso": true, "custom_integrations": true, "dedicated_support": true, "sla_guarantee": true, "on_premise": true, "white_label": true, "custom_features": true}');