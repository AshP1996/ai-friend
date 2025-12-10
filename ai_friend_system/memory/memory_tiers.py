from datetime import datetime, timedelta
from typing import Dict, Optional
from config.constants import MemoryTier
from config import settings

class MemoryTierManager:
    def __init__(self):
        self.tier_config = settings.memory_config
    
    def calculate_expiry(self, tier: MemoryTier) -> Optional[datetime]:
        config = self.tier_config.get(tier.value, {})
        retention_days = config.get('retention_days', -1)
        
        if retention_days == -1:
            return None
        
        return datetime.now() + timedelta(days=retention_days)
    
    def get_tier_priority(self, tier: MemoryTier) -> int:
        config = self.tier_config.get(tier.value, {})
        return config.get('priority', 0)
    
    def determine_tier(self, content: str, importance: float, context: Dict) -> MemoryTier:
        if context.get('is_personal_info'):
            return MemoryTier.PERSONAL
        
        if importance >= 0.9:
            return MemoryTier.PERMANENT
        elif importance >= 0.7:
            return MemoryTier.TEMPORARY
        elif importance >= 0.5:
            return MemoryTier.SUB_TEMPORARY
        else:
            return MemoryTier.SESSION