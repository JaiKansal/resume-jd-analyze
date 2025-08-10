"""Analytics module for Resume + JD Analyzer"""

# Ensure module can be imported safely
try:
    from .google_analytics import ga_tracker, funnel_analyzer
    __all__ = ['ga_tracker', 'funnel_analyzer']
except ImportError:
    # Fallback for import issues
    class FallbackTracker:
        def track_event(self, *args, **kwargs): pass
        def track_page_view(self, *args, **kwargs): pass
        def track_conversion(self, *args, **kwargs): pass
        def track_user_signup(self, *args, **kwargs): pass
        def track_subscription_event(self, *args, **kwargs): pass
        def track_analysis_completion(self, *args, **kwargs): pass
        def track_conversion_funnel(self, *args, **kwargs): pass
        def track_feature_usage(self, *args, **kwargs): pass
        def track_error(self, *args, **kwargs): pass
        def get_funnel_metrics(self, *args, **kwargs): return {}
        def get_cohort_analysis(self, *args, **kwargs): return {}
        def analyze_funnel(self, *args, **kwargs): return {}
    
    ga_tracker = FallbackTracker()
    funnel_analyzer = FallbackTracker()
    __all__ = ['ga_tracker', 'funnel_analyzer']
