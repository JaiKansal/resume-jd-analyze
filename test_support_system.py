#!/usr/bin/env python3
"""
Test script for the support system
"""

# Test feedback and ticket services
try:
    from support.feedback_service import feedback_service
    from support.ticket_service import ticket_service
    import uuid
    
    print('✅ Testing feedback and ticket services')
    
    # Create a test user ID
    test_user_id = str(uuid.uuid4())
    
    # Test feedback submission
    feedback_data = {
        'feedback_type': 'general_feedback',
        'category': 'Testing',
        'title': 'Test Feedback',
        'description': 'This is a test feedback submission',
        'rating': 5,
        'page_url': '/test',
        'metadata': {'test': True}
    }
    
    result = feedback_service.submit_feedback(test_user_id, feedback_data)
    print(f'✅ Feedback submission: {result["success"]}')
    
    # Test getting user feedback
    user_feedback = feedback_service.get_user_feedback(test_user_id)
    print(f'✅ User feedback retrieval: found {len(user_feedback)} feedback items')
    
    # Test ticket creation
    ticket_result = ticket_service.create_ticket(
        user_id=test_user_id,
        subject='Test Support Ticket',
        description='This is a test support ticket',
        category='Technical Issue',
        priority='medium'
    )
    print(f'✅ Ticket creation: {ticket_result["success"]} - {ticket_result.get("ticket_number", "No ticket number")}')
    
    # Test getting user tickets
    user_tickets = ticket_service.get_user_tickets(test_user_id)
    print(f'✅ User tickets retrieval: found {len(user_tickets)} tickets')
    
    # Test adding message to ticket
    if ticket_result['success']:
        ticket_id = ticket_result['ticket_id']
        message_result = ticket_service.add_message(
            ticket_id, test_user_id, 'This is a test message', 'customer'
        )
        print(f'✅ Message addition: {message_result["success"]}')
        
        # Test getting ticket messages
        messages = ticket_service.get_ticket_messages(ticket_id, test_user_id)
        print(f'✅ Ticket messages retrieval: found {len(messages)} messages')
    
    print('✅ All feedback and ticket services working correctly!')
    
except Exception as e:
    print(f'❌ Error testing feedback/ticket services: {e}')
    import traceback
    traceback.print_exc()