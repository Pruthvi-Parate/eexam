import io
from io import BytesIO
from . import forms,models
from exam.models import Course, Question
from exam.resources import QuestionResource
from django.contrib import messages
from tablib import Dataset
from django.shortcuts import render,redirect,reverse
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from django.contrib import messages
from django.views import View
from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import ast
import json
from .models import Student
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage
import base64
from PIL import Image
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from io import BytesIO
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import base64
from django.utils.decorators import method_decorator
from . import models

  
class StudentStart(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('afterlogin'))
        return render(request, 'students/student_start.html')
    

class StudentSignUpView(View):
    def get(self, request, *args, **kwargs):
        user_form = forms.StudentUserForm()
        student_form = forms.StudentForm()
        context = {'user_form': user_form, 'student_form': student_form}
        return render(request, 'students/studentsignup.html', context=context)

    def post(self, request, *args, **kwargs):
        user_form = forms.StudentUserForm(request.POST)
        student_form = forms.StudentForm(request.POST, request.FILES)
        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.email = user_form.cleaned_data['email']  # Add this line to set email value
            user.save()
            student = student_form.save(commit=False)
            student.user = user
            student.save()
            my_student_group, created = Group.objects.get_or_create(name='STUDENT')
            my_student_group.user_set.add(user)
            user = authenticate(username=user_form.cleaned_data['username'],
                                password=user_form.cleaned_data['password'])
            login(request, user)
            return HttpResponseRedirect('../studentlogin')
      
        context = {'user_form': user_form, 'student_form': student_form}
        return render(request, 'students/studentsignup.html', context=context)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


@method_decorator(login_required(login_url='studentlogin'), name='dispatch')
@method_decorator(user_passes_test(is_student), name='dispatch')
class StudentDashboardView(View):
    def get(self, request, *args, **kwargs):
        dict={
            'total_course': Course.objects.all().count(),
            'total_question': Question.objects.all().count(),
        }
        return render(request, 'students/student_dashboard.html', context=dict)

@method_decorator(login_required(login_url='studentlogin'), name='dispatch')
@method_decorator(user_passes_test(is_student), name='dispatch')
class ExamView(TemplateView):
    template_name = 'students/exam.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.all()
        return context


@method_decorator(login_required(login_url='studentlogin'), name='dispatch')
@method_decorator(user_passes_test(is_student), name='dispatch')
class TakeExamView(View):
    def get(self, request, pk):
        course = get_object_or_404(Course, id=pk)
        total_questions = Question.objects.filter(course=course).count()
        questions = Question.objects.filter(course=course)
        total_marks = sum(q.marks for q in questions)
        context = {'course': course, 'total_questions': total_questions, 'total_marks': total_marks}
        return render(request, 'students/take_exam.html', context)
    

class BeginView(View):
    template_name = 'students/begin.html'

    @method_decorator(login_required(login_url='studentlogin'))
    @method_decorator(user_passes_test(is_student))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        course = Course.objects.get(id=self.kwargs['pk'])
        questions = Question.objects.filter(course=course)
        recipient = request.user.email
        send_mail(
            'E-Exam',
            'Your exam has started',
            settings.EMAIL_HOST_USER,
            [recipient],
            fail_silently=False,
        )
        response = render(request, self.template_name, {'course': course, 'questions': questions})
        response.set_cookie('course_id', course.id)
        return response

    def post(self, request, *args, **kwargs):
        pass
    
class CalculateMarksView(View):
    @method_decorator(login_required(login_url='studentlogin'), name='dispatch')
    @method_decorator(user_passes_test(is_student))
    def get(self, request, *args, **kwargs):
        return render(request, 'students/student_dashboard.html')

    def post(self, request, *args, **kwargs):
        print("Function is being executed")
        if request.COOKIES.get('course_id') is not None:
            course_id = request.COOKIES.get('course_id')
            course = QMODEL.Course.objects.get(id=course_id)
            student = models.Student.objects.get(user_id=request.user.id)
            questions = QMODEL.Question.objects.filter(course=course)
           
            total_marks = 0
            wrong_answers = 0
            
            questions = QMODEL.Question.objects.all().filter(course=course)

            for i in range(len(questions)):
                selected_ans = request.COOKIES.get(str(i + 1))
                actual_answer = questions[i].answer

                if not selected_ans:  # check if option is not selected
                    wrong_answers += 1
                elif str(selected_ans).strip() == str(actual_answer).strip():
                    total_marks = total_marks + questions[i].marks
                else:
                    wrong_answers += 1
                
            

            result = QMODEL.Result()
            result.marks = total_marks
            result.wrong_answers = wrong_answers
            result.exam = course
            result.student = student
            
            result.save()
         
            
           
            questions = Question.objects.filter(course=course)
            results = QMODEL.Result.objects.filter(student=student).order_by('-date')
            
            context = {
                'results': results,
            }
    

            
            
            labels = [f'{result.exam.course_name} {result.marks} marks' for result in results]
            data = [result.marks for result in results]

            fig, ax = plt.subplots(figsize=(8, 4), subplot_kw=dict(aspect="equal"))
            wedges, *_ = ax.pie(data, wedgeprops=dict(width=0.5), startangle=-40, autopct='%1.1f%%')

            ax.legend(wedges, labels, title="Results", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

            # Save the chart image as a bytes object
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            chart_image = base64.b64encode(buffer.read()).decode('utf-8')

            # Render the HTML content of the email
            html_content = render_to_string('students/view_progress.html', context)

            # Strip the HTML tags to create a plain text version of the email content
            text_content = strip_tags(html_content)

            # Create the email message object
            recipient = request.user.email
            subject = 'Your Progress Chart'
            to = [recipient]
            message = EmailMessage(subject, to=to)
            text_content

            # Attach the chart image to the email message
            message.attach('chart.png', base64.b64decode(chart_image), 'image/png')

            # Send the email
            message.send()

            return redirect('my-result')
        else:
            return render(request, 'students/student_dashboard.html',context)


@method_decorator(login_required(login_url='studentlogin'), name='dispatch')
@method_decorator(user_passes_test(is_student), name='dispatch')
class MyResultView(TemplateView):
    template_name = 'students/my_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = QMODEL.Course.objects.all()
        return context

@method_decorator(login_required(login_url='studentlogin'), name='dispatch')
@method_decorator(login_required(login_url='adminlogin'), name='dispatch')
@method_decorator(user_passes_test(is_student), name='dispatch')
class CheckMarksView(TemplateView):
    template_name = 'students/check_marks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        course = get_object_or_404(QMODEL.Course, id=pk)
        student = self.request.user.student
        results = QMODEL.Result.objects.filter(exam=course, student=student)
        context['results'] = results
        return context
    


class MyMarksView(TemplateView):
    template_name = 'students/my_marks.html'
    
    @method_decorator(login_required(login_url='studentlogin'))
    @method_decorator(user_passes_test(is_student))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = QMODEL.Course.objects.all()
        context['courses'] = courses
        return context
  


class ViewWrongQuestionsView(View):
    
    @method_decorator(login_required(login_url='studentlogin'))
    @method_decorator(user_passes_test(is_student))
    def get(self, request, exam_id):
        exam = QMODEL.Course.objects.get(id=exam_id)
        questions = QMODEL.Question.objects.filter(course=exam)
        wrong_questions = []
        for i in range(len(questions)):
            selected_ans = request.COOKIES.get(str(i+1))
            actual_answer = questions[i].answer
            if selected_ans != actual_answer:
                wrong_questions.append(questions[i])
        return render(request, 'students/view_wrong_questions.html', {'exam': exam, 'wrong_questions': wrong_questions})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_progress_view(request):
    student = models.Student.objects.get(user_id=request.user.id)
    results = QMODEL.Result.objects.filter(student=student).order_by('-date')

    progress = []
    for result in results:
        wrong_answers = []
        questions = QMODEL.Question.objects.filter(course=result.exam)
        for i in range(len(questions)):
            selected_ans = request.COOKIES.get(str(result.id) + '_' + str(i+1))
            actual_answer = questions[i].answer
            if selected_ans != actual_answer:
                wrong_answers.append(i+1)
        progress.append({'exam': result.exam, 'marks': result.marks, 'wrong_answers': wrong_answers, 'date': result.date})

    context = {
            'progress': progress,
            'results': results
        }
    return render(request, 'students/view_progress.html', context)



