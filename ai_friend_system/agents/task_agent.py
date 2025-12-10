from typing import Dict, Any
from .base_agent import BaseAgent

class TaskAgent(BaseAgent):
    def __init__(self):
        super().__init__("task")
        self.task_keywords = {
            'reminder': ['remind', 'remember to', 'dont forget'],
            'search': ['search', 'find', 'look up', 'google'],
            'calculation': ['calculate', 'compute', 'sum', 'total'],
            'information': ['what is', 'tell me about', 'explain']
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        text = input_data.get('text', '').lower()
        
        detected_tasks = []
        for task_type, keywords in self.task_keywords.items():
            if any(kw in text for kw in keywords):
                detected_tasks.append(task_type)
        
        has_task = len(detected_tasks) > 0
        
        return {
            'has_task': has_task,
            'task_types': detected_tasks,
            'priority': 'high' if 'urgent' in text or 'important' in text else 'normal'
        }
