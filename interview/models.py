
from django.db import models
from django.utils import timezone

class Role(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    keywords = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.role.name} - {self.text[:50]}..."
    
    class Meta:
        ordering = ['-created_at']


class Session(models.Model):
    user_session = models.CharField(max_length=100, unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="sessions")
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.id} for {self.role.name} ({self.user_session})"



class Attempt(models.Model):
    session = models.ForeignKey(Session , on_delete=models.CASCADE, related_name="attempts")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="attempts")
    user_session = models.CharField(max_length=100)
    answer_text = models.TextField()
    feedback_text = models.TextField(blank=True)
    score = models.IntegerField(default=0)
    ai_feedback= models.JSONField(null=True, blank=True)
    raw_ai_response = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Attempt {self.id} - Score: {self.score}"
    
    class Meta:
        ordering = ['-created_at']


