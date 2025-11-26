import os

class Config:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), 'models/pose_landmarker_full.task')
        # Padding ya no se usa mucho en el esquiador, pero mal no hace.
        self.padding = 100 

config = Config()