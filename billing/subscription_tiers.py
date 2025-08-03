"""
Subscription tiers and pricing logic for Resume + JD Analyzer
Implements freemium, professional, business, and enterprise tiers
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from auth.models import PlanType, SubscriptionPlan, Subscription, User
from auth.services import subscription_service, user_service

logger = logging.getLogger(__name__)

class SubscriptionTierManager:
    """Manages subscription tiers, features, and pricing logic"""
    
    def __init__(self):
        self.tier_definitions = self._initialize_tier_definitions()
    
    def _initialize_tier_definitions(self) -> Dict[PlanType, Dict[str, Any]]:
        """Initialize subscription tier definitions with features and limits"""
        return {
            PlanType.FREE: {
                'name': 'Free Tier',
                'price_monthly': 0.00,
                'price_annual': 0.00,
                'monthly_analysis_limit': 3,
                'features': {
                    # Core features
                    'basic_analysis': True,
                    'pdf_download': True,
                    'basic_reports': True,
                    'community_support': True,
                    
                    # Limitations
                    'watermarked_pdfs': True,
                    'limited_file_size': True,  # 5MB limit
                    'basic_ai_model': True,
                    
                    # Disabled features
                    'unlimited_analyses': False,
                    'premium_ai': False,
                    'all_formats': False,
                    'priority_processing': False,
                    'email_support': False,
                    'phone_support': False,
                    'team_collaboration': False,
                    'bulk_upload': False,
                    'analytics_dashboard': False,
                    'api_access': False,
                    'custom_branding': False,
                    'sso': False,
                    'dedicated_support': False
                },
                'description': 'Perfect for trying out our AI-powered resume analysis',
                'target_audience': 'Individual job seekers exploring the platform',
                'upgrade_prompts': [
                    'Unlock unlimited analyses with Professional plan',
                    'Get premium AI insights and priority processing',
                    'Remove watermarks and access all export formats'
                ]
            },
            
            PlanType.PROFESSIONAL: {
                'name': 'Professional',
                'price_monthly': 19.00,
                'price_annual': 190.00,  # 2 months free
                'monthly_analysis_limit': -1,  # Unlimited
                'features': {
                    # All free features
                    'basic_analysis': True,
                    'pdf_download': True,
                    'basic_reports': True,
                    
                    # Professional features
                    'unlimited_analyses': True,
                    'premium_ai': True,
                    'all_formats': True,  # CSV, PDF, Word, JSON
                    'priority_processing': True,
                    'email_support': True,
                    'resume_templates': True,
                    'advanced_insights': True,
                    'skill_recommendations': True,
                    'industry_benchmarking': True,
                    
                    # No watermarks
                    'watermarked_pdfs': False,
                    'limited_file_size': False,  # 50MB limit
                    'basic_ai_model': False,
                    
                    # Still disabled
                    'team_collaboration': False,
                    'bulk_upload': False,
                    'analytics_dashboard': False,
                    'api_access': False,
                    'custom_branding': False,
                    'sso': False,
                    'dedicated_support': False
                },
                'description': 'Ideal for serious job seekers and career professionals',
                'target_audience': 'Individual professionals, career changers, consultants',
                'upgrade_prompts': [
                    'Add team collaboration with Business plan',
                    'Get bulk processing and analytics dashboard',
                    'Access API for custom integrations'
                ]
            },
            
            PlanType.BUSINESS: {
                'name': 'Business',
                'price_monthly': 99.00,
                'price_annual': 990.00,  # 2 months free
                'monthly_analysis_limit': -1,  # Unlimited
                'seat_limit': 5,
                'features': {
                    # All professional features
                    'basic_analysis': True,
                    'pdf_download': True,
                    'basic_reports': True,
                    'unlimited_analyses': True,
                    'premium_ai': True,
                    'all_formats': True,
                    'priority_processing': True,
                    'email_support': True,
                    'resume_templates': True,
                    'advanced_insights': True,
                    'skill_recommendations': True,
                    'industry_benchmarking': True,
                    
                    # Business features
                    'team_collaboration': True,
                    'bulk_upload': True,
                    'analytics_dashboard': True,
                    'api_access': True,  # 1000 calls/month
                    'integration_support': True,
                    'phone_support': True,
                    'custom_branding': True,
                    'team_management': True,
                    'usage_analytics': True,
                    'export_analytics': True,
                    
                    # Still disabled
                    'sso': False,
                    'dedicated_support': False,
                    'unlimited_seats': False,
                    'white_label': False,
                    'on_premise': False
                },
                'description': 'Perfect for growing companies and HR teams',
                'target_audience': 'SMEs, startups, HR departments, recruiting agencies',
                'upgrade_prompts': [
                    'Get enterprise security with SSO integration',
                    'Add unlimited seats and dedicated support',
                    'Enable white-label and on-premise options'
                ]
            },
            
            PlanType.ENTERPRISE: {
                'name': 'Enterprise',
                'price_monthly': 500.00,
                'price_annual': 5000.00,  # 2 months free
                'monthly_analysis_limit': -1,  # Unlimited
                'seat_limit': -1,  # Unlimited
                'features': {
                    # All business features
                    'basic_analysis': True,
                    'pdf_download': True,
                    'basic_reports': True,
                    'unlimited_analyses': True,
                    'premium_ai': True,
                    'all_formats': True,
                    'priority_processing': True,
                    'email_support': True,
                    'resume_templates': True,
                    'advanced_insights': True,
                    'skill_recommendations': True,
                    'industry_benchmarking': True,
                    'team_collaboration': True,
                    'bulk_upload': True,
                    'analytics_dashboard': True,
                    'api_access': True,  # Unlimited
                    'integration_support': True,
                    'phone_support': True,
                    'custom_branding': True,
                    'team_management': True,
                    'usage_analytics': True,
                    'export_analytics': True,
                    
                    # Enterprise features
                    'unlimited_seats': True,
                    'sso': True,
                    'custom_integrations': True,
                    'dedicated_support': True,
                    'sla_guarantee': True,
                    'on_premise': True,
                    'white_label': True,
                    'custom_features': True,
                    'priority_support': True,
                    'custom_ai_models': True,
                    'advanced_security': True,
                    'audit_logs': True,
                    'compliance_reports': True
                },
                'description': 'Complete solution for large organizations',
                'target_audience': 'Large enterprises, Fortune 500, government agencies',
                'upgrade_prompts': []  # No upgrades from enterprise
            }
        }
    
    def get_tier_definition(self, plan_type: PlanType) -> Dict[str, Any]:
        """Get tier definition for a plan type"""
        return self.tier_definitions.get(plan_type, {})
    
    def get_all_tiers(self) -> List[Dict[str, Any]]:
        """Get all tier definitions for display"""
        tiers = []
        for plan_type in [PlanType.FREE, PlanType.PROFESSIONAL, PlanType.BUSINESS, PlanType.ENTERPRISE]:
            tier_def = self.tier_definitions[plan_type]
            tiers.append({
                'plan_type': plan_type,
                'name': tier_def['name'],
                'price_monthly': tier_def['price_monthly'],
                'price_annual': tier_def['price_annual'],
                'monthly_analysis_limit': tier_def['monthly_analysis_limit'],
                'features': tier_def['features'],
                'description': tier_def['description'],
                'target_audience': tier_def['target_audience'],
                'upgrade_prompts': tier_def['upgrade_prompts']
            })
        return tiers
    
    def check_feature_access(self, user_id: str, feature_name: str) -> bool:
        """Check if user has access to a specific feature"""
        subscription = subscription_service.get_user_subscription(user_id)
        if not subscription or not subscription.plan:
            return False
        
        tier_def = self.get_tier_definition(subscription.plan.plan_type)
        return tier_def.get('features', {}).get(feature_name, False)
    
    def get_usage_limits(self, user_id: str) -> Dict[str, Any]:
        """Get usage limits for a user"""
        subscription = subscription_service.get_user_subscription(user_id)
        if not subscription or not subscription.plan:
            return self._get_default_limits()
        
        tier_def = self.get_tier_definition(subscription.plan.plan_type)
        
        return {
            'monthly_analysis_limit': tier_def.get('monthly_analysis_limit', 3),
            'monthly_analysis_used': subscription.monthly_analysis_used,
            'file_size_limit_mb': 50 if tier_def['features'].get('limited_file_size') else 100,
            'api_calls_limit': self._get_api_limit(subscription.plan.plan_type),
            'team_seats_limit': tier_def.get('seat_limit', 1),
            'bulk_upload_limit': 100 if tier_def['features'].get('bulk_upload') else 1
        }
    
    def can_upgrade_to(self, current_plan_type: PlanType, target_plan_type: PlanType) -> bool:
        """Check if user can upgrade from current plan to target plan"""
        plan_hierarchy = [PlanType.FREE, PlanType.PROFESSIONAL, PlanType.BUSINESS, PlanType.ENTERPRISE]
        
        try:
            current_index = plan_hierarchy.index(current_plan_type)
            target_index = plan_hierarchy.index(target_plan_type)
            return target_index > current_index
        except ValueError:
            return False
    
    def get_upgrade_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get upgrade recommendations for a user based on usage patterns"""
        subscription = subscription_service.get_user_subscription(user_id)
        if not subscription or not subscription.plan:
            return []
        
        current_tier = self.get_tier_definition(subscription.plan.plan_type)
        recommendations = []
        
        # Check if user is hitting limits
        if subscription.plan.monthly_analysis_limit != -1:
            usage_percentage = (subscription.monthly_analysis_used / subscription.plan.monthly_analysis_limit) * 100
            
            if usage_percentage >= 80:
                recommendations.append({
                    'reason': 'usage_limit',
                    'message': f"You've used {usage_percentage:.0f}% of your monthly analyses",
                    'suggested_plan': PlanType.PROFESSIONAL if subscription.plan.plan_type == PlanType.FREE else PlanType.BUSINESS,
                    'benefit': 'Get unlimited analyses and never worry about limits again'
                })
        
        # Add tier-specific upgrade prompts
        for prompt in current_tier.get('upgrade_prompts', []):
            recommendations.append({
                'reason': 'feature_upgrade',
                'message': prompt,
                'suggested_plan': self._get_next_tier(subscription.plan.plan_type),
                'benefit': 'Unlock advanced features and capabilities'
            })
        
        return recommendations
    
    def calculate_pricing(self, plan_type: PlanType, billing_cycle: str = 'monthly', 
                         seats: int = 1, region: str = 'US') -> Dict[str, Any]:
        """Calculate pricing for a plan with regional adjustments"""
        tier_def = self.get_tier_definition(plan_type)
        
        base_price = tier_def['price_annual'] if billing_cycle == 'annual' else tier_def['price_monthly']
        
        # Apply regional pricing adjustments
        regional_multiplier = self._get_regional_multiplier(region)
        adjusted_price = base_price * regional_multiplier
        
        # Calculate seat-based pricing for business/enterprise
        if plan_type in [PlanType.BUSINESS, PlanType.ENTERPRISE] and seats > 1:
            if plan_type == PlanType.BUSINESS:
                # Business plan: $99 for 5 seats, $15 per additional seat
                if seats > 5:
                    additional_seats = seats - 5
                    seat_cost = additional_seats * (15 * regional_multiplier)
                    adjusted_price += seat_cost
            # Enterprise pricing is custom, so no automatic seat calculation
        
        # Calculate savings for annual billing
        annual_savings = 0
        if billing_cycle == 'annual':
            monthly_equivalent = tier_def['price_monthly'] * 12 * regional_multiplier
            annual_savings = monthly_equivalent - adjusted_price
        
        return {
            'base_price': base_price,
            'adjusted_price': adjusted_price,
            'regional_multiplier': regional_multiplier,
            'billing_cycle': billing_cycle,
            'seats': seats,
            'annual_savings': annual_savings,
            'currency': self._get_regional_currency(region),
            'tax_rate': self._get_regional_tax_rate(region)
        }
    
    def _get_default_limits(self) -> Dict[str, Any]:
        """Get default limits for users without subscription"""
        return {
            'monthly_analysis_limit': 3,
            'monthly_analysis_used': 0,
            'file_size_limit_mb': 5,
            'api_calls_limit': 0,
            'team_seats_limit': 1,
            'bulk_upload_limit': 1
        }
    
    def _get_api_limit(self, plan_type: PlanType) -> int:
        """Get API call limit for plan type"""
        limits = {
            PlanType.FREE: 0,
            PlanType.PROFESSIONAL: 0,
            PlanType.BUSINESS: 1000,
            PlanType.ENTERPRISE: -1  # Unlimited
        }
        return limits.get(plan_type, 0)
    
    def _get_next_tier(self, current_plan_type: PlanType) -> PlanType:
        """Get the next tier for upgrade recommendations"""
        next_tier_map = {
            PlanType.FREE: PlanType.PROFESSIONAL,
            PlanType.PROFESSIONAL: PlanType.BUSINESS,
            PlanType.BUSINESS: PlanType.ENTERPRISE,
            PlanType.ENTERPRISE: PlanType.ENTERPRISE  # No upgrade from enterprise
        }
        return next_tier_map.get(current_plan_type, PlanType.PROFESSIONAL)
    
    def _get_regional_multiplier(self, region: str) -> float:
        """Get pricing multiplier for different regions (PPP adjustment)"""
        multipliers = {
            'US': 1.0,
            'CA': 1.0,
            'UK': 0.85,
            'AU': 0.85,
            'DE': 0.85,
            'FR': 0.85,
            'NL': 0.85,
            'SE': 0.85,
            'JP': 0.85,
            'KR': 0.85,
            'IN': 0.6,
            'BR': 0.6,
            'MX': 0.6,
            'PL': 0.6,
            'SG': 0.4,
            'ZA': 0.4,
            'OTHER': 0.4
        }
        return multipliers.get(region, 1.0)
    
    def _get_regional_currency(self, region: str) -> str:
        """Get currency for different regions"""
        currencies = {
            'US': 'USD',
            'CA': 'CAD',
            'UK': 'GBP',
            'AU': 'AUD',
            'DE': 'EUR',
            'FR': 'EUR',
            'NL': 'EUR',
            'SE': 'SEK',
            'JP': 'JPY',
            'KR': 'KRW',
            'IN': 'INR',
            'BR': 'BRL',
            'MX': 'MXN',
            'PL': 'PLN',
            'SG': 'SGD',
            'ZA': 'ZAR'
        }
        return currencies.get(region, 'USD')
    
    def _get_regional_tax_rate(self, region: str) -> float:
        """Get tax rate for different regions"""
        tax_rates = {
            'US': 0.0,  # Varies by state
            'CA': 0.13,  # HST
            'UK': 0.20,  # VAT
            'AU': 0.10,  # GST
            'DE': 0.19,  # VAT
            'FR': 0.20,  # VAT
            'NL': 0.21,  # VAT
            'SE': 0.25,  # VAT
            'JP': 0.10,  # Consumption tax
            'KR': 0.10,  # VAT
            'IN': 0.18,  # GST
            'BR': 0.17,  # ICMS
            'MX': 0.16,  # IVA
            'PL': 0.23,  # VAT
            'SG': 0.07,  # GST
            'ZA': 0.15   # VAT
        }
        return tax_rates.get(region, 0.0)

class UsageTracker:
    """Tracks and enforces usage limits for different subscription tiers"""
    
    def __init__(self):
        self.tier_manager = SubscriptionTierManager()
    
    def can_perform_analysis(self, user_id: str) -> tuple[bool, Optional[str]]:
        """Check if user can perform an analysis"""
        subscription = subscription_service.get_user_subscription(user_id)
        
        if not subscription:
            return False, "No active subscription found"
        
        if not subscription.is_active():
            return False, "Subscription is not active"
        
        # Check monthly limit
        if subscription.plan.monthly_analysis_limit != -1:
            if subscription.monthly_analysis_used >= subscription.plan.monthly_analysis_limit:
                return False, f"Monthly limit of {subscription.plan.monthly_analysis_limit} analyses reached"
        
        return True, None
    
    def can_upload_file(self, user_id: str, file_size_mb: float) -> tuple[bool, Optional[str]]:
        """Check if user can upload a file of given size"""
        limits = self.tier_manager.get_usage_limits(user_id)
        max_size = limits['file_size_limit_mb']
        
        if file_size_mb > max_size:
            return False, f"File size ({file_size_mb:.1f}MB) exceeds limit ({max_size}MB)"
        
        return True, None
    
    def can_bulk_upload(self, user_id: str, file_count: int) -> tuple[bool, Optional[str]]:
        """Check if user can perform bulk upload"""
        if not self.tier_manager.check_feature_access(user_id, 'bulk_upload'):
            return False, "Bulk upload not available in your plan"
        
        limits = self.tier_manager.get_usage_limits(user_id)
        max_files = limits['bulk_upload_limit']
        
        if file_count > max_files:
            return False, f"Bulk upload limit is {max_files} files"
        
        return True, None
    
    def can_access_api(self, user_id: str) -> tuple[bool, Optional[str]]:
        """Check if user can access API"""
        if not self.tier_manager.check_feature_access(user_id, 'api_access'):
            return False, "API access not available in your plan"
        
        return True, None
    
    def track_analysis_usage(self, user_id: str, count: int = 1) -> bool:
        """Track analysis usage and update counters"""
        return subscription_service.increment_user_usage(user_id, count)
    
    def get_usage_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive usage summary for user"""
        subscription = subscription_service.get_user_subscription(user_id)
        limits = self.tier_manager.get_usage_limits(user_id)
        
        if not subscription:
            return {'error': 'No subscription found'}
        
        # Calculate usage percentages
        analysis_percentage = 0
        if limits['monthly_analysis_limit'] > 0:
            analysis_percentage = (limits['monthly_analysis_used'] / limits['monthly_analysis_limit']) * 100
        
        return {
            'plan_name': subscription.plan.name,
            'plan_type': subscription.plan.plan_type.value,
            'status': subscription.status.value,
            'analyses': {
                'used': limits['monthly_analysis_used'],
                'limit': limits['monthly_analysis_limit'],
                'percentage': analysis_percentage,
                'unlimited': limits['monthly_analysis_limit'] == -1
            },
            'features': {
                'bulk_upload': self.tier_manager.check_feature_access(user_id, 'bulk_upload'),
                'api_access': self.tier_manager.check_feature_access(user_id, 'api_access'),
                'team_collaboration': self.tier_manager.check_feature_access(user_id, 'team_collaboration'),
                'premium_ai': self.tier_manager.check_feature_access(user_id, 'premium_ai'),
                'priority_processing': self.tier_manager.check_feature_access(user_id, 'priority_processing')
            },
            'limits': limits,
            'upgrade_recommendations': self.tier_manager.get_upgrade_recommendations(user_id)
        }

# Service instances
tier_manager = SubscriptionTierManager()
usage_tracker = UsageTracker()