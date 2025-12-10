from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
import asyncio

class BaseAgent(ABC):
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.last_execution = None
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = datetime.now()
        try:
            result = await self.process(input_data)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'agent_type': self.agent_type,
                'result': result,
                'execution_time': execution_time
            }
        except Exception as e:
            return {
                'success': False,
                'agent_type': self.agent_type,
                'error': str(e),
                'execution_time': (datetime.now() - start_time).total_seconds()
            }
