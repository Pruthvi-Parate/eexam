"""eexam URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path,include
from django.contrib import admin
from exam import views

from django.contrib.auth.views import LogoutView,LoginView
from exam.views import *

urlpatterns = [
    path('',HomeView.as_view(),name=''),    
    path('admin/', admin.site.urls),
    path('student/',include('student.urls')),
    path('logout', LogoutView.as_view(template_name='eexam/logout.html'),name='logout'),
    path('afterlogin', AfterLoginView.as_view(),name='afterlogin'),
    path('adminlogin', LoginView.as_view(template_name='eexam/adminlogin.html'),name='adminlogin'),
    path('admin-dashboard', AdminDashboardView.as_view(),name='admin-dashboard'),
    path('admin-view-student', views.admin_view_student_view,name='admin-view-student'),
    path('view-student/', ViewStudentView.as_view(),name='view-student'),
    path('admin-view-student-marks', AdminViewStudentMarks.as_view(),name='admin-view-student-marks'),
    path('view-marks/<int:pk>', views.view_marks_view,name='view-marks'),
    path('update-student/<int:pk>', views.update_student_view,name='update-student'),
    path('delete-student/<int:pk>', views.delete_student_view,name='delete-student'),
    path('courses', CoursesView.as_view(),name='courses'),
    path('add-exam',views.add_exam,name='add-exam'),
    path('view-exam', ViewExamView.as_view(),name='view-exam'),
    path('update_course/<int:course_id>/',UpdateCourseView.as_view(),name='update_course'),
    path('delete-course/<int:pk>', views.delete_course_view,name='delete-course'),
    path('manage-question', ManageQuestionView.as_view(),name='manage-question'),
    path('add-questions', views.add_questions,name='add-questions'),
    path('upload.html',views.simple_upload),
    path('dash-view-question', DashViewQuestionView.as_view(),name='dash-view-question'),
    path('view-question/<int:pk>', ViewQuestionView.as_view(),name='view-question'),
    path('delete-question/<int:pk>', views.delete_question_view,name='delete-question'),

]

