"""
Support Ticket Service
Handles customer support tickets, messages, and ticket management
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from database.connection import get_db

class TicketService:
    """Service for managing support tickets"""
    
    def create_ticket(self, user_id: str, subject: str, description: str, 
                     category: str = None, priority: str = 'medium') -> Dict[str, Any]:
        """Create a new support ticket"""
        try:
            db = get_db()
            ticket_id = str(uuid.uuid4())
            
            # Generate ticket number manually for SQLite
            ticket_number = self._generate_ticket_number()
            
            db.execute_command("""
                INSERT INTO support_tickets 
                (id, ticket_number, user_id, subject, description, category, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket_id,
                ticket_number,
                user_id,
                subject,
                description,
                category,
                priority
            ))
            
            # Add initial system message
            self._add_system_message(ticket_id, 
                                   f"Support ticket {ticket_number} has been created. "
                                   f"We'll respond within 24 hours.")
            
            return {
                'success': True,
                'ticket_id': ticket_id,
                'ticket_number': ticket_number,
                'message': f'Support ticket {ticket_number} created successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_message(self, ticket_id: str, sender_id: str, content: str, 
                   sender_type: str = 'customer', message_type: str = 'text') -> Dict[str, Any]:
        """Add a message to a support ticket"""
        try:
            db = get_db()
            message_id = str(uuid.uuid4())
            
            db.execute_command("""
                INSERT INTO support_ticket_messages 
                (id, ticket_id, sender_id, sender_type, message_type, content)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                message_id,
                ticket_id,
                sender_id,
                sender_type,
                message_type,
                content
            ))
            
            # Update ticket status if customer is responding
            if sender_type == 'customer':
                db.execute_command("""
                    UPDATE support_tickets 
                    SET status = 'open', updated_at = ?
                    WHERE id = ? AND status = 'waiting_customer'
                """, (datetime.utcnow().isoformat(), ticket_id))
            
            return {
                'success': True,
                'message_id': message_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_tickets(self, user_id: str, status: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get support tickets for a user"""
        try:
            db = get_db()
            
            query = """
                SELECT id, ticket_number, subject, category, priority, status,
                       created_at, updated_at, resolved_at
                FROM support_tickets
                WHERE user_id = ?
            """
            params = [user_id]
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            results = db.execute_query(query, tuple(params))
            
            tickets = []
            for row in results:
                tickets.append({
                    'id': str(row['id']),
                    'ticket_number': row['ticket_number'],
                    'subject': row['subject'],
                    'category': row['category'],
                    'priority': row['priority'],
                    'status': row['status'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'resolved_at': row['resolved_at']
                })
            
            return tickets
            
        except Exception as e:
            print(f"Error getting user tickets: {e}")
            return []
    
    def get_ticket_messages(self, ticket_id: str, user_id: str = None) -> List[Dict[str, Any]]:
        """Get messages for a support ticket"""
        try:
            db = get_db()
            
            # Verify user has access to this ticket if user_id provided
            if user_id:
                access_check = db.get_single_result("""
                    SELECT COUNT(*) as count FROM support_tickets 
                    WHERE id = ? AND user_id = ?
                """, (ticket_id, user_id))
                
                if not access_check or access_check['count'] == 0:
                    return []
            
            results = db.execute_query("""
                SELECT stm.id, stm.sender_type, stm.content, stm.message_type,
                       stm.created_at, u.first_name, u.last_name
                FROM support_ticket_messages stm
                LEFT JOIN users u ON stm.sender_id = u.id
                WHERE stm.ticket_id = ? AND stm.is_internal = 0
                ORDER BY stm.created_at ASC
            """, (ticket_id,))
            
            messages = []
            for row in results:
                sender_name = "System"
                if row['first_name'] and row['last_name']:
                    sender_name = f"{row['first_name']} {row['last_name']}"
                elif row['sender_type'] == 'agent':
                    sender_name = "Support Agent"
                
                messages.append({
                    'id': str(row['id']),
                    'sender_type': row['sender_type'],
                    'content': row['content'],
                    'message_type': row['message_type'],
                    'created_at': row['created_at'],
                    'sender_name': sender_name
                })
            
            return messages
            
        except Exception as e:
            print(f"Error getting ticket messages: {e}")
            return []
    
    def update_ticket_status(self, ticket_id: str, status: str, user_id: str = None) -> Dict[str, Any]:
        """Update ticket status"""
        try:
            db = get_db()
            
            # Verify user has access if user_id provided
            if user_id:
                access_check = db.get_single_result("""
                    SELECT COUNT(*) as count FROM support_tickets 
                    WHERE id = ? AND user_id = ?
                """, (ticket_id, user_id))
                
                if not access_check or access_check['count'] == 0:
                    return {'success': False, 'error': 'Ticket not found'}
            
            current_time = datetime.utcnow().isoformat()
            
            if status == 'resolved':
                db.execute_command("""
                    UPDATE support_tickets 
                    SET status = ?, updated_at = ?, resolved_at = ?
                    WHERE id = ?
                """, (status, current_time, current_time, ticket_id))
            elif status == 'closed':
                db.execute_command("""
                    UPDATE support_tickets 
                    SET status = ?, updated_at = ?, closed_at = ?
                    WHERE id = ?
                """, (status, current_time, current_time, ticket_id))
            else:
                db.execute_command("""
                    UPDATE support_tickets 
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                """, (status, current_time, ticket_id))
            
            return {'success': True}
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_support_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get support metrics for the specified period"""
        try:
            db = get_db()
            start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Total tickets
            total_result = db.get_single_result("""
                SELECT COUNT(*) as count FROM support_tickets 
                WHERE created_at >= ?
            """, (start_date,))
            total_tickets = total_result['count'] if total_result else 0
            
            # Tickets by status
            status_results = db.execute_query("""
                SELECT status, COUNT(*) as count
                FROM support_tickets 
                WHERE created_at >= ?
                GROUP BY status
            """, (start_date,))
            tickets_by_status = {row['status']: row['count'] for row in status_results}
            
            # For SQLite, we'll calculate time differences in a simpler way
            # Average response time (first response) - simplified for SQLite
            response_results = db.execute_query("""
                SELECT first_response_at, created_at
                FROM support_tickets 
                WHERE created_at >= ? AND first_response_at IS NOT NULL
            """, (start_date,))
            
            response_times = []
            for row in response_results:
                try:
                    created = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
                    responded = datetime.fromisoformat(row['first_response_at'].replace('Z', '+00:00'))
                    diff_hours = (responded - created).total_seconds() / 3600
                    response_times.append(diff_hours)
                except:
                    continue
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Average resolution time - simplified for SQLite
            resolution_results = db.execute_query("""
                SELECT resolved_at, created_at
                FROM support_tickets 
                WHERE created_at >= ? AND resolved_at IS NOT NULL
            """, (start_date,))
            
            resolution_times = []
            for row in resolution_results:
                try:
                    created = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
                    resolved = datetime.fromisoformat(row['resolved_at'].replace('Z', '+00:00'))
                    diff_hours = (resolved - created).total_seconds() / 3600
                    resolution_times.append(diff_hours)
                except:
                    continue
            
            avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
            
            return {
                'total_tickets': total_tickets,
                'tickets_by_status': tickets_by_status,
                'avg_response_time_hours': float(avg_response_time),
                'avg_resolution_time_hours': float(avg_resolution_time),
                'period_days': days
            }
            
        except Exception as e:
            print(f"Error getting support metrics: {e}")
            return {}
    
    def _generate_ticket_number(self) -> str:
        """Generate a ticket number for SQLite"""
        from datetime import date
        today = date.today()
        date_str = today.strftime('%Y%m%d')
        
        # Get count of tickets created today
        db = get_db()
        count_result = db.get_single_result("""
            SELECT COUNT(*) as count FROM support_tickets 
            WHERE DATE(created_at) = DATE('now')
        """)
        
        counter = (count_result['count'] if count_result else 0) + 1
        return f"TKT-{date_str}-{counter:04d}"
    
    def _add_system_message(self, ticket_id: str, content: str):
        """Add a system message to a ticket"""
        db = get_db()
        message_id = str(uuid.uuid4())
        
        db.execute_command("""
            INSERT INTO support_ticket_messages 
            (id, ticket_id, sender_type, content)
            VALUES (?, ?, 'system', ?)
        """, (message_id, ticket_id, content))

# Global instance
ticket_service = TicketService()