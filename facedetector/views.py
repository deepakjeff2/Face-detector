import os
from .models import Video, Frame
import cv2
import numpy as np
from django.shortcuts import render, redirect

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def process_video(request):
    if request.method == 'POST' and request.FILES['video']:
        video = request.FILES['video']
        video_instance = Video(video_file=video, title=video.name)
        video_instance.save()

        # Path to the uploaded video file
        video_path = video_instance.video_file.path

        # Create a directory to store processed frames
        frame_dir = os.path.join('media', 'frames', str(video_instance.id))
        os.makedirs(frame_dir, exist_ok=True)

        # Open the video file
        cap = cv2.VideoCapture(video_path)

        # Process each frame of the video
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Detect faces in the current frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                # Draw bounding boxes around detected faces
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                frame_count += 1

                # Save the frame with bounding boxes
                frame_filename = os.path.join(frame_dir, f'frame_{frame_count}.jpg')
                cv2.imwrite(frame_filename, frame)

                # Create a Frame instance to link to the video
                frame_instance = Frame(video=video_instance, frame_image=frame_filename, face_detected=True)
                frame_instance.save()

        # Release the video capture object
        cap.release()

        return redirect('show_results', video_id=video_instance.id)

    return render(request, 'upload_video.html')



def upload_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        video_title = video_file.name

        # Create a Video instance and save the uploaded video
        video_instance = Video(title=video_title, video_file=video_file)
        video_instance.save()
        
        return redirect('show_results', video_id=video_instance.id)

    return render(request, 'upload_video.html')



def show_results(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
        frames_with_faces = Frame.objects.filter(video=video, face_detected=True)

        return render(request, 'results.html', {'video': video, 'frames_with_faces': frames_with_faces})
    except Video.DoesNotExist:
        return redirect('upload_video')
