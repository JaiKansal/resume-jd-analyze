"""
Knowledge Base Service
Handles knowledge base articles, search, and user interactions
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
from database.connection import get_db

class KnowledgeBaseService:
    """Service for managing knowledge base articles"""
    
    def get_published_articles(self, category: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get published knowledge base articles"""
        try:
            db = get_db()
            
            query = """
                SELECT id, title, slug, excerpt, category, view_count,
                       helpful_count, not_helpful_count, published_at
                FROM knowledge_base_articles
                WHERE status = 'published'
            """
            params = []
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY published_at DESC LIMIT ?"
            params.append(limit)
            
            results = db.execute_query(query, tuple(params))
            
            articles = []
            for row in results:
                articles.append({
                    'id': str(row['id']),
                    'title': row['title'],
                    'slug': row['slug'],
                    'excerpt': row['excerpt'],
                    'category': row['category'],
                    'view_count': row['view_count'],
                    'helpful_count': row['helpful_count'],
                    'not_helpful_count': row['not_helpful_count'],
                    'published_at': row['published_at']
                })
            
            return articles
            
        except Exception as e:
            print(f"Error getting published articles: {e}")
            return []
    
    def get_article_by_slug(self, slug: str, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Get a knowledge base article by slug"""
        try:
            db = get_db()
            
            result = db.get_single_result("""
                SELECT id, title, content, category, view_count,
                       helpful_count, not_helpful_count, published_at
                FROM knowledge_base_articles
                WHERE slug = ? AND status = 'published'
            """, (slug,))
            
            if not result:
                return None
            
            article = {
                'id': str(result['id']),
                'title': result['title'],
                'content': result['content'],
                'category': result['category'],
                'view_count': result['view_count'],
                'helpful_count': result['helpful_count'],
                'not_helpful_count': result['not_helpful_count'],
                'published_at': result['published_at']
            }
            
            # Track article view
            if user_id:
                self._track_article_view(str(result['id']), user_id)
            
            # Increment view count
            db.execute_command("""
                UPDATE knowledge_base_articles 
                SET view_count = view_count + 1
                WHERE id = ?
            """, (str(result['id']),))
            
            return article
            
        except Exception as e:
            print(f"Error getting article by slug: {e}")
            return None
    
    def search_articles(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge base articles"""
        try:
            db = get_db()
            
            # Simple text search - in production, you might want to use full-text search
            search_query = f"%{query.lower()}%"
            
            results = db.execute_query("""
                SELECT id, title, slug, excerpt, category, view_count
                FROM knowledge_base_articles
                WHERE status = 'published' 
                AND (LOWER(title) LIKE ? 
                     OR LOWER(content) LIKE ? 
                     OR LOWER(search_keywords) LIKE ?)
                ORDER BY view_count DESC, helpful_count DESC
                LIMIT ?
            """, (search_query, search_query, search_query, limit))
            
            articles = []
            for row in results:
                articles.append({
                    'id': str(row['id']),
                    'title': row['title'],
                    'slug': row['slug'],
                    'excerpt': row['excerpt'],
                    'category': row['category'],
                    'view_count': row['view_count']
                })
            
            return articles
            
        except Exception as e:
            print(f"Error searching articles: {e}")
            return []
    
    def get_categories(self) -> List[str]:
        """Get all article categories"""
        try:
            db = get_db()
            
            results = db.execute_query("""
                SELECT DISTINCT category 
                FROM knowledge_base_articles
                WHERE status = 'published' AND category IS NOT NULL
                ORDER BY category
            """)
            
            categories = [row['category'] for row in results]
            
            return categories
            
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def rate_article_helpful(self, article_id: str, is_helpful: bool) -> Dict[str, Any]:
        """Rate an article as helpful or not helpful"""
        try:
            db = get_db()
            
            if is_helpful:
                db.execute_command("""
                    UPDATE knowledge_base_articles 
                    SET helpful_count = helpful_count + 1
                    WHERE id = ?
                """, (article_id,))
            else:
                db.execute_command("""
                    UPDATE knowledge_base_articles 
                    SET not_helpful_count = not_helpful_count + 1
                    WHERE id = ?
                """, (article_id,))
            
            return {'success': True}
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_popular_articles(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most popular articles by view count"""
        try:
            db = get_db()
            
            results = db.execute_query("""
                SELECT id, title, slug, excerpt, view_count
                FROM knowledge_base_articles
                WHERE status = 'published'
                ORDER BY view_count DESC
                LIMIT ?
            """, (limit,))
            
            articles = []
            for row in results:
                articles.append({
                    'id': str(row['id']),
                    'title': row['title'],
                    'slug': row['slug'],
                    'excerpt': row['excerpt'],
                    'view_count': row['view_count']
                })
            
            return articles
            
        except Exception as e:
            print(f"Error getting popular articles: {e}")
            return []
    
    def _track_article_view(self, article_id: str, user_id: str):
        """Track an article view"""
        try:
            db = get_db()
            view_id = str(uuid.uuid4())
            
            db.execute_command("""
                INSERT INTO knowledge_base_views 
                (id, article_id, user_id)
                VALUES (?, ?, ?)
            """, (view_id, article_id, user_id))
        except Exception as e:
            # Don't fail the main operation if view tracking fails
            print(f"Error tracking article view: {e}")

# Global instance
knowledge_base = KnowledgeBaseService()