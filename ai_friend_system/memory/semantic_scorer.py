"""
Advanced semantic relevance scoring for memory retrieval
Uses keyword matching, context similarity, and temporal relevance
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
from utils.logger import Logger

logger = Logger("SemanticScorer")

class SemanticScorer:
    """Calculate semantic relevance scores for memory retrieval"""
    
    def __init__(self):
        self.logger = logger
    
    def score_memory(self, memory: Dict[str, Any], query: str, 
                    conversation_context: Dict[str, Any] = None) -> float:
        """
        Calculate relevance score for a memory
        
        Args:
            memory: Memory dict with content, tags, tier, etc.
            query: Current query/message
            conversation_context: Current conversation context
        
        Returns:
            Relevance score (0.0 to 1.0)
        """
        scores = []
        
        # 1. Keyword overlap score (0.0 - 0.4)
        keyword_score = self._keyword_overlap_score(memory.get('content', ''), query)
        scores.append(('keyword', keyword_score * 0.4))
        
        # 2. Tag relevance score (0.0 - 0.2)
        tag_score = self._tag_relevance_score(memory.get('tags', ''), query)
        scores.append(('tag', tag_score * 0.2))
        
        # 3. Tier importance score (0.0 - 0.2)
        tier_score = self._tier_importance_score(memory.get('tier', 'temporary'))
        scores.append(('tier', tier_score * 0.2))
        
        # 4. Temporal relevance score (0.0 - 0.1)
        temporal_score = self._temporal_relevance_score(memory.get('created_at'), memory.get('last_accessed'))
        scores.append(('temporal', temporal_score * 0.1))
        
        # 5. Context similarity score (0.0 - 0.1)
        if conversation_context:
            context_score = self._context_similarity_score(memory, conversation_context)
            scores.append(('context', context_score * 0.1))
        
        # Total score
        total = sum(score for _, score in scores)
        
        self.logger.debug(f"Memory score breakdown: {dict(scores)} = {total:.3f}")
        
        return min(1.0, total)
    
    def _keyword_overlap_score(self, memory_content: str, query: str) -> float:
        """Calculate keyword overlap between memory and query"""
        if not memory_content or not query:
            return 0.0
        
        # Simple word-based overlap
        memory_words = set(memory_content.lower().split())
        query_words = set(query.lower().split())
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        memory_words = memory_words - stop_words
        query_words = query_words - stop_words
        
        if not query_words:
            return 0.0
        
        # Calculate overlap ratio
        overlap = len(memory_words & query_words)
        overlap_ratio = overlap / len(query_words)
        
        return min(1.0, overlap_ratio * 2.0)  # Boost for better matching
    
    def _tag_relevance_score(self, tags: str, query: str) -> float:
        """Calculate relevance based on tags"""
        if not tags:
            return 0.0
        
        tag_list = [tag.strip().lower() for tag in tags.split(',')]
        query_words = set(query.lower().split())
        
        # Check if any tag matches query words
        matches = sum(1 for tag in tag_list if tag in query_words or any(tag in word for word in query_words))
        
        if not tag_list:
            return 0.0
        
        return min(1.0, matches / len(tag_list))
    
    def _tier_importance_score(self, tier: str) -> float:
        """Calculate score based on memory tier"""
        tier_scores = {
            'permanent': 1.0,
            'personal': 0.9,
            'temporary': 0.6,
            'sub_temporary': 0.4,
            'session': 0.2
        }
        return tier_scores.get(tier.lower(), 0.5)
    
    def _temporal_relevance_score(self, created_at: datetime = None, 
                                  last_accessed: datetime = None) -> float:
        """Calculate temporal relevance (recent = more relevant)"""
        if not created_at:
            return 0.5
        
        now = datetime.now()
        
        # Check if created_at is datetime or string
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                return 0.5
        
        # Recent memories are more relevant
        age_days = (now - created_at).days
        
        if age_days < 1:
            return 1.0
        elif age_days < 7:
            return 0.8
        elif age_days < 30:
            return 0.6
        elif age_days < 90:
            return 0.4
        else:
            return 0.2
    
    def _context_similarity_score(self, memory: Dict[str, Any], 
                                 conversation_context: Dict[str, Any]) -> float:
        """Calculate similarity based on conversation context"""
        # Check emotion match
        memory_emotion = memory.get('emotion_at_creation')
        current_emotion = conversation_context.get('emotion', {}).get('emotion') if isinstance(conversation_context.get('emotion'), dict) else conversation_context.get('emotion')
        
        if memory_emotion and current_emotion:
            if memory_emotion == current_emotion:
                return 0.5  # Emotion match
        
        # Check topic continuity
        current_topic = conversation_context.get('current_topic')
        if current_topic:
            memory_content = memory.get('content', '').lower()
            topic_words = set(current_topic.lower().split())
            content_words = set(memory_content.split())
            
            overlap = len(topic_words & content_words)
            if overlap > 0:
                return min(0.5, overlap / len(topic_words))
        
        return 0.0
    
    def rank_memories(self, memories: List[Dict[str, Any]], query: str,
                     conversation_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Rank memories by relevance score"""
        scored_memories = []
        
        for memory in memories:
            score = self.score_memory(memory, query, conversation_context)
            scored_memories.append({
                **memory,
                'relevance_score': score
            })
        
        # Sort by relevance score (descending)
        scored_memories.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return scored_memories
