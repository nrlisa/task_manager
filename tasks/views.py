from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.http import HttpResponseForbidden
from .models import Task
from .forms import TaskForm

# 0. AUTH: User Registration
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('task_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

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
    # Security: Ensure the task exists AND belongs to the user
    task = get_object_or_404(Task, pk=pk)
    if task.owner != request.user:
        return HttpResponseForbidden("You do not have permission to edit this task.")
    
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
    if task.owner != request.user:
        return HttpResponseForbidden()
    
    if request.method == "POST":
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

# 5. RBAC: Admin-only view for Audit Logs
@user_passes_test(lambda u: u.is_superuser)
def admin_audit_log(request):
    # [Inference]: Using Django's built-in LogEntry for the Audit Log requirement
    from django.contrib.admin.models import LogEntry
    logs = LogEntry.objects.all().order_by('-action_time')[:50]
    return render(request, 'tasks/audit_log.html', {'logs': logs})