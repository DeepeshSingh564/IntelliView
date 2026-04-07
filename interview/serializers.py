
from rest_framework import serializers
from .models import Role, Question, Attempt

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'slug']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'difficulty', 'keywords']

class AnswerSubmissionSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_text = serializers.CharField()
    user_session = serializers.CharField(required=False, allow_blank=True)

class AttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = ['id', 'score', 'feedback_text', 'user_session', 'created_at','ai_feedback']
