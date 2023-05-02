from django.urls import path
from student import views
from django.contrib.auth.views import LoginView
from . import views
from .views import *

urlpatterns = [
path('studentlogin', LoginView.as_view(template_name='students/studentlogin.html'),name='studentlogin'),
path('studentstart/', StudentStart.as_view(), name='studentstart'),
path('studentsignup/', StudentSignUpView.as_view(), name='studentsignup'),
path('view-progress',views.view_progress_view,name='view-progress-view'),
path('studentdashboard/', StudentDashboardView.as_view(),name='studentdashboard'),
path('exam', ExamView.as_view(),name='exam'),
path('take-exam/<int:pk>', TakeExamView.as_view(),name='take-exam'),
path('begin/<int:pk>', BeginView.as_view(),name='begin-exam'),
path('calculatemarks', CalculateMarksView.as_view(),name='calculatemarks'),
path('my-result', MyResultView.as_view(),name='my-result'),
path('view-wrong-questions/<int:exam_id>/', ViewWrongQuestionsView.as_view(), name='view_wrong_questions'),
path('check-marks/<int:pk>/', CheckMarksView.as_view(),name='check-marks'),
path('my-marks', MyMarksView.as_view(),name='my-marks'),
]