from django.shortcuts import render,redirect,reverse, get_object_or_404
from . import forms,models
from .models import Question
from .resources import QuestionResource
from django.contrib import messages
from tablib import Dataset
from django.http import HttpResponse
from .forms import CourseForm
from exam.models import Course
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Q
from django.views.generic import RedirectView
from django.core.mail import send_mail
from student import models as SMODEL
from django.utils.decorators import method_decorator
from student import forms as SFORM
from .models import Student
from django.views.generic import ListView
from .forms import QuestionForm
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views import View
from django.contrib.auth.models import User
from exam import models as QMODEL

class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('afterlogin')
        return render(request, 'eexam/index.html')

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


def simple_upload(request):
    if request.method == 'POST':
        question_resource = QuestionResource()
        dataset = Dataset()
        new_question = request.FILES['myfile']

        if not new_question.name.endswith('xlsx'):
            messages.error(request, 'wrong format')
            return render(request, 'exam/upload.html')
        

        imported_data = dataset.load(new_question.read(), format='xlsx', headers=True)

        expected_columns = 9  # number of columns in the Excel file
        for data in imported_data:
            if len(data) != expected_columns:
                messages.info(request, f"Wrong number of columns in row {imported_data.index(data)+1}")
                return render(request, 'eexam/upload.html')
            if Question.objects.filter(question=data[3]).exists():
                continue
            value = Question(
                data[0],
                data[1],
                data[2],
                data[3],
                data[4],
                data[5],
                data[6],
                data[7],
                data[8],
                
            )
            value.save()

    return render(request, 'eexam/upload.html')

class AfterLoginView(View):
    def get(self, request, *args, **kwargs):
        if is_student(request.user):      
            return redirect('student/studentdashboard')
        else:
            return redirect('admin-dashboard')


@method_decorator(login_required(login_url='adminlogin'), name='dispatch')
class AdminDashboardView(View):
    def get(self, request):
        dict={
            'total_student': SMODEL.Student.objects.all().count(),
            'total_course': models.Course.objects.all().count(),
            'total_question': models.Question.objects.all().count(),
        }
        return render(request, 'eexam/admin_dashboard.html', context=dict)



@method_decorator(login_required(login_url='adminlogin'), name='dispatch')
class ViewStudentView(View):
    def get(self, request):
        students = SMODEL.Student.objects.all()
        return render(request,'eexam/view_student.html',{'students':students})

@login_required(login_url='adminlogin')
def admin_view_student_view(request):
    students= SMODEL.Student.objects.all()
    return render(request,'eexam/view_student.html',{'students':students})


@method_decorator(login_required(login_url='adminlogin'), name='dispatch')
class AdminStudentView(View):
    def get(self, request, *args, **kwargs):
        dict={
            'total_student': SMODEL.Student.objects.all().count(),
        }
        return render(request, 'eexam/admin_student.html', context=dict)

@login_required(login_url='adminlogin')
def delete_student_view(request,pk):
    student=SMODEL.Student.objects.get(id=pk)
    user=User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return HttpResponseRedirect('/admin-view-student')

    
class CoursesView(LoginRequiredMixin, View):
    login_url = 'adminlogin'
    template_name = 'eexam/courses.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


@login_required(login_url='adminlogin')
def add_exam(request):
    courseForm=forms.CourseForm()
    if request.method=='POST':
        courseForm=forms.CourseForm(request.POST)
        if courseForm.is_valid():        
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/view-exam')
    return render(request,'eexam/add_exam.html',{'courseForm':courseForm})


@method_decorator(login_required(login_url='adminlogin'), name='dispatch')
class ViewExamView(TemplateView):
    template_name = 'eexam/view_exam.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = models.Course.objects.all()
        return context


@login_required(login_url='adminlogin')
def delete_course_view(request,pk):
    course=models.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/view-exam')

@method_decorator(login_required(login_url='adminlogin'), name='dispatch')
class UpdateCourseView(View):
    template_name = 'eexam/update_course.html'
    form_class = CourseForm
    success_url = '/view-exam'

    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        form = self.form_class(instance=course)
        return render(request, self.template_name, {'form': form, 'course': course})

    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        form = self.form_class(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form, 'course': course})
   

@method_decorator(login_required(login_url='adminlogin'), name='dispatch')
class ManageQuestionView(TemplateView):
    template_name = 'eexam/manage_question.html'


@login_required(login_url='adminlogin')
def add_questions(request):
    questionForm=forms.QuestionForm()
    if request.method=='POST':
        questionForm=forms.QuestionForm(request.POST)
        if questionForm.is_valid():
            question=questionForm.save(commit=False)
            course=models.Course.objects.get(id=request.POST.get('courseID'))
            question.course=course
            question.save()       
        else:
            print("form is invalid")
        return HttpResponseRedirect('/dash-view-question')
    return render(request,'eexam/add_questions.html',{'questionForm':questionForm})


@method_decorator(login_required(login_url='adminlogin'), name='dispatch')
class DashViewQuestionView(View):
    def get(self, request):
        courses = models.Course.objects.all()
        return render(request, 'eexam/dash_view_question.html', {'courses': courses})

@method_decorator(login_required(login_url='adminlogin'), name='dispatch')
class ViewQuestionView(ListView):
    model = models.Question
    context_object_name = 'questions'
    template_name = 'eexam/view_question.html'

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return self.model.objects.filter(course_id=pk)

@login_required(login_url='adminlogin')
def delete_question_view(request,pk):
    question=models.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/dash-view-question')

@method_decorator(login_required(login_url='adminlogin'), name='dispatch')
class AdminViewStudentMarks(TemplateView):
    template_name = 'eexam/admin_view_student_marks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = Student.objects.all()
        return context

@login_required(login_url='adminlogin')
def view_marks_view(request,pk):
    courses = models.Course.objects.all()
    response =  render(request,'eexam/view_marks.html',{'courses':courses})
    response.set_cookie('student_id',str(pk))
    return response

class CheckMarksView(View):
    @method_decorator(login_required(login_url='adminlogin'))
    def get(self, request, pk):
        course = models.Course.objects.get(id=pk)
        student_id = request.COOKIES.get('student_id')
        student = Student.objects.get(id=student_id)

        results = models.Result.objects.all().filter(exam=course).filter(student=student)
        return render(request, 'eexam/adcheck_marks.html', {'results': results})
    

@login_required(login_url='adminlogin')
def update_student_view(request,pk):
    student=SMODEL.Student.objects.get(id=pk)
    user=SMODEL.User.objects.get(id=student.user_id)
    userForm=SFORM.StudentUserForm(instance=user)
    studentForm=SFORM.StudentForm(request.FILES,instance=student)
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=SFORM.StudentUserForm(request.POST,instance=user)
        studentForm=SFORM.StudentForm(request.POST,request.FILES,instance=student)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            studentForm.save()
            return redirect('admin-view-student')
    return render(request,'eexam/update_student.html',context=mydict)


