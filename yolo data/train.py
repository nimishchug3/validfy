from ultralytics import YOLO

# Load the model
model = YOLO("yolov8n.yaml")  # build a new model from scratch

if __name__ == '__main__':
    # Load the model
    model = YOLO('yolov8n.pt')

    # Define training parameters
    params = {
        'data': 'H:/TE_project/yolo data/data.yaml',  # Path to your dataset configuration file
        'epochs': 100,                       # Total number of epochs
        'batch': 4,                          # Batch size
        'imgsz': 640,                        # Image size
        'optimizer': 'AdamW',                # Optimizer
        'warmup_epochs': 15,                 # Number of warmup epochs
        'seed': 42,                          # Random seed for reproducibility
        'device': '0'                     # Use both GPU 0 and GPU 1
    }

    # Train the model
    model.train(**params)
