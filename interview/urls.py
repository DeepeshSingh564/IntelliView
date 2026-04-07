
from django.urls import path
from . import views


urlpatterns =[
  path('', views.home_view, name='home'),
  path("interview/<int:role_id>/", views.interview_view, name="interview"),
  path('api/roles', views.api_roles, name='api_roles'),
  path("api/questions/<int:role_id>/", views.api_questions, name='api_questions'),
  path('api/answer/', views.api_answer, name='api_answer'),
  path('api/answer-browsable/', views.api_answer_browsable, name='api_answer_browsable'),
  path("api/session/start", views.api_start_session, name="api_start_session"),
  path("api/session/<int:session_id>/summary", views.api_session_summary, name="api_session_summary"),

]