from django import forms
from django.db.models import Q
from django.core.validators import RegexValidator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from .models import Task
from .forms import TaskForm
import logging

logger = logging.getLogger(__name__)

# Custom Form to restrict username length
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=8, 
        help_text="Required. 8 characters or fewer.",
        validators=[RegexValidator(r'^[a-zA-Z0-9]+$', "Usernames must be alphanumeric and max 8 characters.")]
    )

# 0. AUTH: User Registration
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('login_success_redirect')
        else:
            logger.warning(f"Registration failed: {form.errors.as_json()}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# 1. READ: List tasks (Access Control implemented)
@login_required
def task_list(request):
    # Restrict access: Admins go to the Admin Panel, not the Task List
    if request.user.is_staff:
        return redirect('admin:index')

    query = request.GET.get('q', '')
    # IDOR Prevention: Always start by filtering by the current user
    tasks = Task.objects.filter(owner=request.user)

    if query:
        # Parameterized Everything: Using ORM filters with Q objects prevents SQL Injection
        tasks = tasks.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    
    return render(request, 'tasks/task_list.html', {'tasks': tasks, 'query': query})

# 2. CREATE: Add new task (Input Validation via Forms)
@login_required
def create_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

# 3. UPDATE: Edit task (Ownership Verification)
@login_required
def edit_task(request, pk):
    # IDOR Prevention: Use a filtered queryset to ensure users can only access their own tasks
    if request.user.has_perm('tasks.change_task'):
        task = get_object_or_404(Task, pk=pk)
    else:
        # Ensure users can only retrieve tasks they own
        task = get_object_or_404(Task, pk=pk, owner=request.user)
    
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form})

# 4. DELETE: Secure deletion
@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    # Granular RBAC: Check if user is owner OR has the global delete permission
    if not (task.owner == request.user or request.user.has_perm('tasks.delete_task')):
        raise PermissionDenied
    
    if request.method == "POST":
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

# 7. Conditional Redirect after Login
@login_required
def login_success_redirect(request):
    if request.user.is_staff:
        logger.info(f"Admin login detected: Redirecting {request.user.username} to Admin Panel.")
        return redirect('admin:index')
    logger.info(f"Regular login detected: Redirecting {request.user.username} to Task List.")
    return redirect('task_list')

def custom_400(request, exception=None):
    return render(request, '400.html', status=400)

def custom_403(request, exception=None):
    return render(request, '403.html', status=403)

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)

@login_required
def profile(request):
    return render(request, 'profile.html')