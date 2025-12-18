class AIManager:
    def __init__(self):
        self.models = {}

    async def load_models(self):
        self.models["chat"] = "loaded"
        print("AI models loaded")

    async def unload_models(self):
        self.models.clear()
        print("AI models unloaded")

ai_manager = AIManager()
