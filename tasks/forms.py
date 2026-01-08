from django import forms
from .models import Task
import re

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        # [Whitelisting] Allow only alphanumeric and spaces
        if not re.match(r'^[a-zA-Z0-9\s]+$', title):
            raise forms.ValidationError("Invalid characters! Only letters and numbers allowed.")
        return title