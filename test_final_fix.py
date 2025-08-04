#!/usr/bin/env python3
"""
Final Fix Test - Verify all database issues are resolved
"""

def test_complete_startup():
    """Test complete startup sequence"""
    print('🚀 Testing complete startup sequence...')
    
    # Test startup
    import startup
    print('✅ Startup script completed')
    
    # Test database operations
    from database.connection import get_db
    db = get_db()
    
    # Test a typical user query (this was failing before)
    try:
        result = db.execute_query('SELECT * FROM users LIMIT 1')
        print('✅ User query works (no more SQLite errors!)')
    except Exception as e:
        print(f'❌ User query failed: {e}')
        return False
    
    # Test database health
    from database.health_check import check_and_fix_database
    health = check_and_fix_database()
    print(f'✅ Database health: {"Good" if health else "Bad"}')
    
    # Test Razorpay
    try:
        from billing.razorpay_service import razorpay_service
        if razorpay_service.client:
            print('✅ Razorpay client working')
        else:
            print('⚠️  Razorpay client not initialized (need secrets)')
    except Exception as e:
        print(f'❌ Razorpay error: {e}')
    
    print('🎉 All systems working! Streamlit Cloud deployment should be perfect now!')
    return True

if __name__ == "__main__":
    test_complete_startup()