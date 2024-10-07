from ultralytics import YOLO

# Load the model
model = YOLO('YOUR_PATH_OF_YOLO_MODEL') 

# Predict and get results
results = model.predict(source='C:/Users/Nimish/Downloads/front aadhar card.png', show=False)

# Check if any detections were made
if results:
    # Get the first result (assuming one image)
    result = results[0]
    # Process the results
    for result in results:
        print(result.names)  # class names
        print(result.boxes.xyxy)  # bounding boxes
        print(result.boxes.conf)  # confidence scores
    
    # Save the annotated image
    result.save('C:/Users/Nimish/Downloads/output.png')
else:
    print("No detections were made.")
