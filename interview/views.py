from django.shortcuts import get_object_or_404, render
import json
import secrets
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Role, Question, Attempt, Session
from .feedback_engine import score_answer
from .serializers import RoleSerializer, QuestionSerializer, AnswerSubmissionSerializer, AttemptSerializer
from .ai_engine import ai_evaluate_answer
from .feedback_engine import score_answer



# Create your views here.

def home_view(request):
    roles = Role.objects.all()
    return render(request, "interview/home.html", {"roles": roles})

def interview_view(request,role_id):
    role = get_object_or_404(Role, id=role_id)  # default to 1 if missing
    return render(request, "interview/interview.html", {"role": role})

@require_GET
def api_roles(request):
  roles = list(Role.objects.order_by('name').values('id', 'name', 'slug'))
  return JsonResponse({'roles': roles})

@require_GET
def api_questions(request, role_id):
    role = get_object_or_404(Role, id=role_id)
    from .ai_engine import ai_generate_questions
    questions = ai_generate_questions(role.name, count=15)
    if not questions:
        # fallback to database
        questions = list(Question.objects.filter(role_id=role_id).values('id', 'text', 'difficulty', 'keywords'))
    else:
        # Delete old AI questions for this role and save fresh ones
        Question.objects.filter(role=role).delete()
        saved = []
        for q in questions:
            obj = Question.objects.create(
                role=role,
                text=q['text'],
                difficulty=q['difficulty'],
                keywords=q.get('keywords', []) + ['ai_generated']
            )
            saved.append({
                'id': obj.id,
                'text': obj.text,
                'difficulty': obj.difficulty,
                'keywords': obj.keywords
            })
        questions = saved
    return JsonResponse({'questions': questions})

@csrf_exempt
@require_POST
def api_answer(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
        print("Payload received:", payload) 
        session_id = payload.get("session_id")
        question_id = payload.get("question_id")
        answer_text = payload.get("answer_text")

        if session_id is None or question_id is None or answer_text is None:
            return HttpResponseBadRequest("Missing required fields.")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON format.")

        # Get session & question
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return HttpResponseBadRequest("Invalid session_id")
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return HttpResponseBadRequest("Invalid question_id")
    
    result = {}

    # ✅ Decide evaluation method
    if getattr(settings, "USE_AI", False):
        try:

            result = ai_evaluate_answer(question.text, answer_text)
            score = result.get("score", 0)
            feedback_parts = []
            feedback_parts.extend(result.get("strengths", []))
            feedback_parts.extend(result.get("weaknesses", []))
            feedback_parts.extend(result.get("improvements", []))
            feedback = "\n".join(feedback_parts)
            if not feedback.strip():
                feedback = "No feedback provided."
        except Exception:
            score, feedback = score_answer(answer_text, question.keywords or [])
    else:
        score, feedback = score_answer(answer_text, question.keywords or [])

    # Save attempt
    attempt = Attempt.objects.create(
        session=session,
        question=question,
        user_session=session.user_session,
        answer_text=answer_text,
        feedback_text=feedback,
        score=score,
    )

    return JsonResponse({
        "attempt_id": attempt.id,
        "session_id": session.id,
        "score": attempt.score,
        "feedback": attempt.feedback_text,
        "feedback_structured": {
            "strengths": result.get("strengths", []) if getattr(settings, "USE_AI", False) else [],
            "weaknesses": result.get("weaknesses", []) if getattr(settings, "USE_AI", False) else [],
            "improvements": result.get("improvements", []) if getattr(settings, "USE_AI", False) else [],
        }
    })

@api_view(['GET', 'POST'])
def api_answer_browsable(request):
    """
    Browsable API endpoint for submitting answers.
    GET: Shows the form interface
    POST: Submits the answer
    """
    if request.method == 'GET':
           # Get some sample questions for easy testing
            sample_questions = list(Question.objects.select_related('role').values(
                'id', 'text', 'role__name', 'difficulty', 'keywords'
            )[:3])

            # Return information about how to use this endpoint with examples
            return Response({
                'message': 'Submit an answer using the form below. Try copying one of the sample question IDs.',
                'instructions': {
                    'step1': 'Choose a question_id from the samples below',
                    'step2': 'Write your answer in the answer_text field',
                    'step3': 'Optionally add a user_session identifier',
                    'step4': 'Click POST to submit'
                },
                'sample_data_to_try': {
                    'question_id': sample_questions[0]['id'] if sample_questions else 1,
                    'answer_text': 'I have experience with Python, Django, and REST APIs. I can work with databases and implement user authentication systems.',
                    'user_session': 'demo-session-123'
                },
                'available_questions': sample_questions
        })
    
    elif request.method == 'POST':
        serializer = AnswerSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        question_id = serializer.validated_data['question_id']
        answer_text = serializer.validated_data['answer_text']
        user_session = serializer.validated_data.get('user_session') or secrets.token_hex(8)
        
        try:
            q = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({'error': 'Invalid question_id'}, status=status.HTTP_400_BAD_REQUEST)
        
        score, fb = score_answer(answer_text, q.keywords or [])
        attempt = Attempt.objects.create(
            question=q,
            user_session=user_session,
            answer_text=answer_text,
            feedback_text=fb,
            score=score,
        )
        
        result_serializer = AttemptSerializer(attempt)
        return Response({
            'attempt_id': attempt.id,
            'score': score,
            'feedback': fb,
            'user_session': user_session,
            'attempt_details': result_serializer.data
        }, status=status.HTTP_201_CREATED)

@require_POST
def api_start_session(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
        role_id = payload["role_id"]

    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    role = Role.objects.get(id=role_id)
    session = Session.objects.create(
        user_session=secrets.token_hex(8),
        role=role
    )
    return JsonResponse({
        "session_id": session.id,
        "user_session": session.user_session,
        "role": role.name
    })

@require_GET
def api_session_summary(request, session_id):
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return HttpResponseBadRequest("Invalid session_id")

    attempts = session.attempts.all()
    avg_score = attempts.aggregate(models.Avg("score"))["score__avg"] or 0

    return JsonResponse({
        "session_id": session.id,
        "role": session.role.name,
        "started_at": session.started_at,
        "ended_at": session.ended_at,
        "attempts": [
            {
                "question": a.question.text,
                "score": a.score,
                "feedback": a.feedback_text,
            } for a in attempts
        ],
        "average_score": avg_score
    })


