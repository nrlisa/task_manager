from django import forms
from django.core.validators import RegexValidator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.http import HttpResponseForbidden
from .models import Task
from .forms import TaskForm

# Custom Form to restrict username length
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=8, 
        help_text="Required. 8 characters or fewer.",
        validators=[RegexValidator(r'^[\w.@+-]+$', "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.")]
    )

# 0. AUTH: User Registration
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('task_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# 1. READ: List tasks (Access Control implemented)
@login_required
def task_list(request):
    # Security: Users only see their own tasks (IDOR Protection)
    tasks = Task.objects.filter(owner=request.user)
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

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
    # unless they have the 'change_task' permission (RBAC).
    queryset = Task.objects.all() if request.user.has_perm('tasks.change_task') else Task.objects.filter(owner=request.user)
    task = get_object_or_404(queryset, pk=pk)
    
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
@permission_required('tasks.delete_task', raise_exception=True)
def delete_task(request, pk):
    # IDOR Prevention: Queryset filtering restricts access at the database level.
    queryset = Task.objects.all() if request.user.has_perm('tasks.delete_task') else Task.objects.filter(owner=request.user)
    task = get_object_or_404(queryset, pk=pk)
    
    if request.method == "POST":
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

# 5. RBAC: Admin-only view for Audit Logs
@permission_required('admin.view_logentry', raise_exception=True)
def admin_audit_log(request):
    # [Inference]: Using Django's built-in LogEntry for the Audit Log requirement
    from django.contrib.admin.models import LogEntry
    logs = LogEntry.objects.all().order_by('-action_time')[:50]
    return render(request, 'tasks/audit_log.html', {'logs': logs})

# 6. Admin Task Management
@permission_required('tasks.view_task', raise_exception=True)
def admin_task_list(request):
    tasks = Task.objects.all().order_by('-created_at')
    return render(request, 'tasks/admin_task_list.html', {'tasks': tasks})

# 7. Conditional Redirect after Login
@login_required
def login_success_redirect(request):
    if request.user.is_staff:
        return redirect('admin:index')
    return redirect('task_list')