import asyncio
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from .emotion_agent import EmotionAgent
from .context_agent import ContextAgent
from .task_agent import TaskAgent
from utils.logger import Logger

class AgentCoordinator:
    def __init__(self):
        self.emotion_agent = EmotionAgent()
        self.context_agent = ContextAgent()
        self.task_agent = TaskAgent()
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.logger = Logger("AgentCoordinator")
    
    async def process_parallel(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Run all agents in parallel for lightning-fast processing
        tasks = [
            self.emotion_agent.execute(input_data),
            self.context_agent.execute(input_data),
            self.task_agent.execute(input_data)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        combined_result = {
            'emotion': {},
            'context': {},
            'task': {},
            'success': True
        }
        
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Agent error: {result}")
                combined_result['success'] = False
                continue
            
            if result['success']:
                agent_type = result['agent_type']
                combined_result[agent_type] = result['result']
            else:
                self.logger.error(f"Agent {result['agent_type']} failed: {result.get('error')}")
                combined_result['success'] = False
        
        return combined_result