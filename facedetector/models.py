from django.db import models

# Create your models here.
from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    created_at = models.DateTimeField(auto_now_add=True)

class Frame(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    frame_image = models.ImageField(upload_to='frames/')
    face_detected = models.BooleanField(default=False)
