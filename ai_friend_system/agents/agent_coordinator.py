import asyncio
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from .emotion_agent import EmotionAgent
from .context_agent import ContextAgent
from .task_agent import TaskAgent
from utils.logger import Logger

# class AgentCoordinator:
#     def __init__(self):
#         self.emotion_agent = EmotionAgent()
#         self.context_agent = ContextAgent()
#         self.task_agent = TaskAgent()
#         self.executor = ThreadPoolExecutor(max_workers=3)
#         self.logger = Logger("AgentCoordinator")
    
#     async def process_parallel(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
#         # Run all agents in parallel for lightning-fast processing
#         tasks = [
#             self.emotion_agent.execute(input_data),
#             self.context_agent.execute(input_data),
#             self.task_agent.execute(input_data)
#         ]
        
#         results = await asyncio.gather(*tasks, return_exceptions=True)
        
#         combined_result = {
#             'emotion': {},
#             'context': {},
#             'task': {},
#             'success': True
#         }
        
#         for result in results:
#             if isinstance(result, Exception):
#                 self.logger.error(f"Agent error: {result}")
#                 combined_result['success'] = False
#                 continue
            
#             if result['success']:
#                 agent_type = result['agent_type']
#                 combined_result[agent_type] = result['result']
#             else:
#                 self.logger.error(f"Agent {result['agent_type']} failed: {result.get('error')}")
#                 combined_result['success'] = False
        
#         return combined_result

class AgentCoordinator:
    def __init__(self):
        self.emotion_agent = EmotionAgent()
        self.context_agent = ContextAgent()
        self.task_agent = TaskAgent()

        # Future-safe agent registry
        self.agents = [
            self.emotion_agent,
            self.context_agent,
            self.task_agent
        ]

        self.logger = Logger("AgentCoordinator")

    async def process_parallel(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        tasks = [
            asyncio.wait_for(agent.execute(input_data), timeout=1.5)
            for agent in self.agents
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        combined_result = {
            "emotion": {},
            "context": {},
            "task": {},
            "memories": [],
            "success": True
        }

        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Agent failed: {result}")
                combined_result["success"] = False
                continue

            if not isinstance(result, dict):
                self.logger.error("Agent returned invalid data")
                combined_result["success"] = False
                continue

            agent_type = result.get("agent_type")
            agent_success = result.get("success", False)
            agent_output = result.get("result", {})

            if agent_type not in ("emotion", "context", "task"):
                self.logger.error(f"Unknown agent type: {agent_type}")
                combined_result["success"] = False
                continue

            if not isinstance(agent_output, dict):
                agent_output = {}

            combined_result[agent_type] = agent_output

            if not agent_success:
                combined_result["success"] = False

            if isinstance(agent_output.get("memories"), list):
                combined_result["memories"].extend(agent_output["memories"])

        return combined_result
