import cv2
import numpy as np
from ultralytics import YOLO
import base64
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import queue
import time

class ThreatDetector:
    def __init__(self, model_path='yolo11s.pt'):
        """Initialize the YOLO model for threat detection with optimizations"""
        self.model = YOLO(model_path)
        
        # Optimize model for inference speed
        self.model.overrides['verbose'] = False
        self.model.overrides['device'] = 'cuda' if self._check_cuda() else 'cpu'
        
        # Use the actual class names from the model instead of hardcoding
        self.class_names = self.model.names  # This will get {0: 'civilian', 1: 'soldier'}
        
        # Performance settings
        self.confidence_threshold = 0.5
        self.iou_threshold = 0.4
        
    def _check_cuda(self):
        """Check if CUDA is available for GPU acceleration"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
        
    def detect_image(self, image_path):
        """
        Detect objects in a single image
        Returns: dict with detections and annotated image
        """
        # Read image
        img = cv2.imread(image_path)
        
        # Perform detection
        results = self.model(img)
        
        # Process results
        detections = []
        annotated_img = img.copy()
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.class_names.get(class_id, f"Class {class_id}")
                
                # Store detection data
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': confidence,
                    'class': class_name,
                    'class_id': class_id
                })
                
                # Draw bounding box
                color = (0, 255, 0) if class_name == 'civilian' else (0, 0, 255)
                cv2.rectangle(annotated_img, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label = f"{class_name}: {confidence:.2f}"
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(annotated_img, (x1, y1 - label_size[1] - 10), 
                            (x1 + label_size[0], y1), color, -1)
                cv2.putText(annotated_img, label, (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Convert annotated image to base64
        _, buffer = cv2.imencode('.jpg', annotated_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            'detections': detections,
            'annotated_image': img_base64,
            'total_detections': len(detections)
        }
    
    def detect_video(self, video_path, output_path=None):
        """
        Process video and detect objects frame by frame
        Returns: generator yielding frame results
        """
        cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Video writer (optional)
        out = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Perform detection
            results = self.model(frame)
            
            # Process results
            detections = []
            annotated_frame = frame.copy()
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = self.class_names.get(class_id, f"Class {class_id}")
                    
                    detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'confidence': confidence,
                        'class': class_name,
                        'class_id': class_id
                    })
                    
                    # Draw bounding box
                    color = (0, 255, 0) if class_name == 'civilian' else (0, 0, 255)
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                    
                    label = f"{class_name}: {confidence:.2f}"
                    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    cv2.rectangle(annotated_frame, (x1, y1 - label_size[1] - 10), 
                                (x1 + label_size[0], y1), color, -1)
                    cv2.putText(annotated_frame, label, (x1, y1 - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Write frame
            if out:
                out.write(annotated_frame)
            
            # Convert frame to base64
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            yield {
                'frame_number': frame_count,
                'total_frames': total_frames,
                'progress': (frame_count / total_frames) * 100,
                'detections': detections,
                'frame': frame_base64
            }
        
        cap.release()
        if out:
            out.release()
    
    def create_processed_video_fast(self, input_path, output_path, skip_frames=2, max_size=640):
        """
        Create a processed video file with optimizations for speed:
        - Frame skipping to reduce processing time
        - Frame resizing for faster inference
        - Optimized codec settings
        - Batch processing when possible
        """
        cap = cv2.VideoCapture(input_path)
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate resize factor for faster processing
        scale_factor = min(max_size / max(width, height), 1.0)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Use faster codec settings
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Faster than H264 for processing
        out = cv2.VideoWriter(output_path, fourcc, fps // (skip_frames + 1), (width, height))
        
        total_detections = 0
        frame_count = 0
        processed_frames = 0
        
        print(f"Processing video with {skip_frames} frame skip, resize factor: {scale_factor:.2f}")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Skip frames for faster processing
            if frame_count % (skip_frames + 1) != 0:
                continue
            
            processed_frames += 1
            
            # Resize frame for faster inference if needed
            if scale_factor < 1.0:
                resized_frame = cv2.resize(frame, (new_width, new_height))
            else:
                resized_frame = frame
            
            # Perform detection with optimized settings
            results = self.model(
                resized_frame,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False,
                stream=False
            )
            
            # Process results and draw on original frame
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Scale coordinates back to original size if resized
                        if scale_factor < 1.0:
                            x1, y1, x2, y2 = box.xyxy[0] / scale_factor
                            x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                        else:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        class_name = self.class_names.get(class_id, f"Class {class_id}")
                        
                        total_detections += 1
                        
                        # Draw bounding box with optimized drawing
                        color = (0, 255, 0) if class_name == 'civilian' else (0, 0, 255)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                        
                        # Draw label with background
                        label = f"{class_name}: {confidence:.2f}"
                        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                        cv2.rectangle(frame, (x1, y1 - label_size[1] - 15), 
                                    (x1 + label_size[0] + 10, y1), color, -1)
                        cv2.putText(frame, label, (x1 + 5, y1 - 8),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Write frame to output video
            out.write(frame)
            
            # Progress feedback
            if processed_frames % 30 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"Progress: {progress:.1f}% ({processed_frames} frames processed)")
        
        cap.release()
        out.release()
        
        print(f"Video processing complete! Processed {processed_frames} frames, found {total_detections} detections")
        return total_detections
    
    def create_processed_video_fast(self, video_path, output_path, skip_frames=2, max_size=640):
        """
        Fast video processing with optimizations for speed
        Args:
            video_path: Input video file path
            output_path: Output video file path  
            skip_frames: Number of frames to skip between detections (0 = process all)
            max_size: Maximum resolution for processing (smaller = faster)
        Returns:
            total_detections: Total number of detections found
        """
        cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate optimal processing size
        if original_width > max_size:
            scale = max_size / original_width
            process_width = max_size
            process_height = int(original_height * scale)
        else:
            process_width = original_width
            process_height = original_height
            scale = 1.0
        
        # Use H.264 codec for better web compatibility
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
        out = cv2.VideoWriter(output_path, fourcc, fps, (original_width, original_height))
        
        if not out.isOpened():
            # Fallback to mp4v if H.264 not available
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (original_width, original_height))
        
        frame_count = 0
        processed_frames = 0
        total_detections = 0
        last_detections = []  # Store last detection results for skipped frames
        
        print(f"Processing video: {original_width}x{original_height} -> {process_width}x{process_height}")
        print(f"Skip frames: {skip_frames}, Expected speedup: {skip_frames + 1}x")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            current_detections = []
            
            # Only run detection on selected frames
            if frame_count % (skip_frames + 1) == 1:
                # Resize frame for faster processing
                if scale != 1.0:
                    small_frame = cv2.resize(frame, (process_width, process_height))
                else:
                    small_frame = frame
                
                # Run detection on smaller frame
                results = self.model(small_frame, 
                                   conf=self.confidence_threshold,
                                   iou=self.iou_threshold,
                                   verbose=False)
                
                # Process detection results
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            # Scale coordinates back to original size
                            x1, y1, x2, y2 = box.xyxy[0]
                            if scale != 1.0:
                                x1, y1, x2, y2 = x1/scale, y1/scale, x2/scale, y2/scale
                            
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                            confidence = float(box.conf[0])
                            class_id = int(box.cls[0])
                            class_name = self.class_names.get(class_id, f"Class {class_id}")
                            
                            current_detections.append({
                                'bbox': [x1, y1, x2, y2],
                                'confidence': confidence,
                                'class': class_name,
                                'class_id': class_id
                            })
                
                # Update last detections for reuse
                last_detections = current_detections.copy()
                processed_frames += 1
            else:
                # Reuse last detection results for skipped frames
                current_detections = last_detections.copy()
            
            # Draw detections on original size frame
            annotated_frame = frame.copy()
            for detection in current_detections:
                x1, y1, x2, y2 = detection['bbox']
                class_name = detection['class']
                confidence = detection['confidence']
                
                # Draw bounding box
                color = (0, 255, 0) if class_name == 'civilian' else (0, 0, 255)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label = f"{class_name}: {confidence:.2f}"
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(annotated_frame, (x1, y1 - label_size[1] - 10), 
                            (x1 + label_size[0], y1), color, -1)
                cv2.putText(annotated_frame, label, (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            total_detections += len(current_detections)
            out.write(annotated_frame)
            
            # Progress feedback
            if frame_count % 60 == 0:  # Every 2 seconds at 30fps
                progress = (frame_count / total_frames) * 100
                print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames} frames)")
        
        cap.release()
        out.release()
        
        actual_speedup = total_frames / processed_frames if processed_frames > 0 else 1
        print(f"Fast processing complete! Processed {processed_frames}/{total_frames} frames")
        print(f"Found {total_detections} detections, Speedup: {actual_speedup:.1f}x")
        
        return total_detections

if __name__ == "__main__":
    # Test the detector
    detector = ThreatDetector('yolo11s.pt')
    
    # Test with an image
    # result = detector.detect_image('test_image.jpg')
    # print(f"Found {result['total_detections']} objects")