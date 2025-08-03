"""
Market Validation Tools
Tools for collecting pricing feedback, feature validation, and market insights
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
from database.connection import get_db

class MarketValidationManager:
    """Service for managing market validation activities"""
    
    def __init__(self):
        self.db = get_db()
        self._ensure_validation_tables()
    
    def _ensure_validation_tables(self):
        """Ensure market validation tables exist"""
        try:
            # Pricing validation table
            self.db.execute_command("""
                CREATE TABLE IF NOT EXISTS pricing_validation (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    user_segment TEXT, -- individual, startup, sme, enterprise
                    current_plan TEXT,
                    expected_price_monthly REAL,
                    max_price_monthly REAL,
                    pricing_model_preference TEXT, -- flat_rate, usage_based, seat_based
                    price_sensitivity TEXT, -- low, medium, high
                    value_perception TEXT, -- underpriced, fair, overpriced
                    willingness_to_pay_more TEXT, -- JSON - features that justify higher price
                    competitor_pricing TEXT, -- JSON - competitor price comparisons
                    feedback TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                )
            """)
            
            # Feature validation table
            self.db.execute_command("""
                CREATE TABLE IF NOT EXISTS feature_validation (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    feature_name TEXT NOT NULL,
                    importance_score INTEGER CHECK (importance_score >= 1 AND importance_score <= 5),
                    current_satisfaction INTEGER CHECK (current_satisfaction >= 1 AND current_satisfaction <= 5),
                    usage_frequency TEXT CHECK (usage_frequency IN ('never', 'rarely', 'sometimes', 'often', 'always')),
                    improvement_suggestions TEXT,
                    willingness_to_pay_extra BOOLEAN DEFAULT FALSE,
                    extra_payment_amount REAL,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                )
            """)
            
            # Market insights table
            self.db.execute_command("""
                CREATE TABLE IF NOT EXISTS market_insights (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    insight_type TEXT CHECK (insight_type IN ('pain_point', 'use_case', 'competitor', 'feature_request', 'workflow')) NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    impact_level TEXT CHECK (impact_level IN ('low', 'medium', 'high', 'critical')) DEFAULT 'medium',
                    frequency TEXT CHECK (frequency IN ('rare', 'occasional', 'frequent', 'constant')) DEFAULT 'occasional',
                    current_solution TEXT, -- How they currently solve this problem
                    ideal_solution TEXT, -- What would be the ideal solution
                    metadata TEXT, -- JSON - additional context
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                )
            """)
            
            # Customer interviews table
            self.db.execute_command("""
                CREATE TABLE IF NOT EXISTS customer_interviews (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    interviewer TEXT,
                    interview_type TEXT CHECK (interview_type IN ('discovery', 'validation', 'pricing', 'feature', 'churn')) NOT NULL,
                    scheduled_at TEXT,
                    completed_at TEXT,
                    duration_minutes INTEGER,
                    interview_notes TEXT,
                    key_insights TEXT, -- JSON - structured insights
                    pain_points TEXT, -- JSON - identified pain points
                    feature_feedback TEXT, -- JSON - feature-specific feedback
                    pricing_feedback TEXT, -- JSON - pricing-related feedback
                    satisfaction_score INTEGER CHECK (satisfaction_score >= 1 AND satisfaction_score <= 10),
                    recommendation_likelihood INTEGER CHECK (recommendation_likelihood >= 0 AND recommendation_likelihood <= 10),
                    follow_up_required BOOLEAN DEFAULT FALSE,
                    follow_up_notes TEXT,
                    status TEXT CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show')) DEFAULT 'scheduled',
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                )
            """)
            
            # Create indexes
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_pricing_validation_user_id ON pricing_validation(user_id)")
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_pricing_validation_user_segment ON pricing_validation(user_segment)")
            
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_feature_validation_user_id ON feature_validation(user_id)")
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_feature_validation_feature_name ON feature_validation(feature_name)")
            
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_market_insights_user_id ON market_insights(user_id)")
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_market_insights_insight_type ON market_insights(insight_type)")
            
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_customer_interviews_user_id ON customer_interviews(user_id)")
            self.db.execute_command("CREATE INDEX IF NOT EXISTS idx_customer_interviews_interview_type ON customer_interviews(interview_type)")
            
        except Exception as e:
            print(f"Error creating market validation tables: {e}")
    
    def submit_pricing_feedback(self, user_id: str, pricing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit pricing validation feedback"""
        try:
            validation_id = str(uuid.uuid4())
            
            self.db.execute_command("""
                INSERT INTO pricing_validation 
                (id, user_id, user_segment, current_plan, expected_price_monthly, 
                 max_price_monthly, pricing_model_preference, price_sensitivity, 
                 value_perception, willingness_to_pay_more, competitor_pricing, feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                validation_id,
                user_id,
                pricing_data.get('user_segment'),
                pricing_data.get('current_plan'),
                pricing_data.get('expected_price_monthly'),
                pricing_data.get('max_price_monthly'),
                pricing_data.get('pricing_model_preference'),
                pricing_data.get('price_sensitivity'),
                pricing_data.get('value_perception'),
                json.dumps(pricing_data.get('willingness_to_pay_more', [])),
                json.dumps(pricing_data.get('competitor_pricing', {})),
                pricing_data.get('feedback')
            ))
            
            return {
                'success': True,
                'validation_id': validation_id,
                'message': 'Pricing feedback submitted successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def submit_feature_feedback(self, user_id: str, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit feature validation feedback"""
        try:
            validation_id = str(uuid.uuid4())
            
            self.db.execute_command("""
                INSERT INTO feature_validation 
                (id, user_id, feature_name, importance_score, current_satisfaction,
                 usage_frequency, improvement_suggestions, willingness_to_pay_extra, extra_payment_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                validation_id,
                user_id,
                feature_data.get('feature_name'),
                feature_data.get('importance_score'),
                feature_data.get('current_satisfaction'),
                feature_data.get('usage_frequency'),
                feature_data.get('improvement_suggestions'),
                feature_data.get('willingness_to_pay_extra', False),
                feature_data.get('extra_payment_amount')
            ))
            
            return {
                'success': True,
                'validation_id': validation_id,
                'message': 'Feature feedback submitted successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_pricing_insights(self, user_segment: str = None) -> Dict[str, Any]:
        """Get pricing validation insights"""
        try:
            query = "SELECT * FROM pricing_validation"
            params = []
            
            if user_segment:
                query += " WHERE user_segment = ?"
                params.append(user_segment)
            
            results = self.db.execute_query(query, tuple(params))
            
            if not results:
                return {'total_responses': 0}
            
            # Calculate insights
            total_responses = len(results)
            
            # Average expected price
            expected_prices = [r['expected_price_monthly'] for r in results if r['expected_price_monthly']]
            avg_expected_price = sum(expected_prices) / len(expected_prices) if expected_prices else 0
            
            # Average max price
            max_prices = [r['max_price_monthly'] for r in results if r['max_price_monthly']]
            avg_max_price = sum(max_prices) / len(max_prices) if max_prices else 0
            
            # Pricing model preferences
            model_preferences = {}
            for result in results:
                if result['pricing_model_preference']:
                    model = result['pricing_model_preference']
                    model_preferences[model] = model_preferences.get(model, 0) + 1
            
            # Value perception
            value_perception = {}
            for result in results:
                if result['value_perception']:
                    perception = result['value_perception']
                    value_perception[perception] = value_perception.get(perception, 0) + 1
            
            return {
                'total_responses': total_responses,
                'avg_expected_price': round(avg_expected_price, 2),
                'avg_max_price': round(avg_max_price, 2),
                'pricing_model_preferences': model_preferences,
                'value_perception': value_perception,
                'user_segment': user_segment
            }
            
        except Exception as e:
            print(f"Error getting pricing insights: {e}")
            return {}
    
    def get_feature_insights(self, feature_name: str = None) -> Dict[str, Any]:
        """Get feature validation insights"""
        try:
            query = "SELECT * FROM feature_validation"
            params = []
            
            if feature_name:
                query += " WHERE feature_name = ?"
                params.append(feature_name)
            
            results = self.db.execute_query(query, tuple(params))
            
            if not results:
                return {'total_responses': 0}
            
            # Calculate insights
            total_responses = len(results)
            
            # Average importance score
            importance_scores = [r['importance_score'] for r in results if r['importance_score']]
            avg_importance = sum(importance_scores) / len(importance_scores) if importance_scores else 0
            
            # Average satisfaction score
            satisfaction_scores = [r['current_satisfaction'] for r in results if r['current_satisfaction']]
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0
            
            # Usage frequency distribution
            usage_frequency = {}
            for result in results:
                if result['usage_frequency']:
                    freq = result['usage_frequency']
                    usage_frequency[freq] = usage_frequency.get(freq, 0) + 1
            
            # Willingness to pay extra
            willing_to_pay = sum(1 for r in results if r['willingness_to_pay_extra'])
            willing_to_pay_percentage = (willing_to_pay / total_responses * 100) if total_responses > 0 else 0
            
            return {
                'total_responses': total_responses,
                'avg_importance_score': round(avg_importance, 2),
                'avg_satisfaction_score': round(avg_satisfaction, 2),
                'usage_frequency_distribution': usage_frequency,
                'willing_to_pay_extra_percentage': round(willing_to_pay_percentage, 1),
                'feature_name': feature_name
            }
            
        except Exception as e:
            print(f"Error getting feature insights: {e}")
            return {}
    
    def get_market_validation_summary(self) -> Dict[str, Any]:
        """Get overall market validation summary"""
        try:
            # Pricing validation summary
            pricing_count = self.db.get_single_result("SELECT COUNT(*) as count FROM pricing_validation")
            pricing_responses = pricing_count['count'] if pricing_count else 0
            
            # Feature validation summary
            feature_count = self.db.get_single_result("SELECT COUNT(*) as count FROM feature_validation")
            feature_responses = feature_count['count'] if feature_count else 0
            
            # Customer interviews summary
            interview_count = self.db.get_single_result("SELECT COUNT(*) as count FROM customer_interviews WHERE status = 'completed'")
            completed_interviews = interview_count['count'] if interview_count else 0
            
            # Market insights summary
            insights_count = self.db.get_single_result("SELECT COUNT(*) as count FROM market_insights")
            total_insights = insights_count['count'] if insights_count else 0
            
            return {
                'pricing_validation_responses': pricing_responses,
                'feature_validation_responses': feature_responses,
                'completed_interviews': completed_interviews,
                'market_insights_collected': total_insights,
                'total_validation_activities': pricing_responses + feature_responses + completed_interviews
            }
            
        except Exception as e:
            print(f"Error getting market validation summary: {e}")
            return {}

# Global instance
market_validation = MarketValidationManager()