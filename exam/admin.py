from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Question

@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    list_display = ('course', 'marks', 'question', 'option1', 'option2', 'option3','option4','answer','cat')
