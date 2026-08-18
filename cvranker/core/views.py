# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm, UploadCVForm
from .models import UploadedCV
from .utils import extract_cv_text, score_cv_and_get_jobs

def home(request):
    # show simple landing with upload form if logged in redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials")
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard_view(request):
    # dashboard shows uploaded CVs, latest highlight, top jobs from latest CV
    user = request.user
    cvs = UploadedCV.objects.filter(user=user).order_by('-uploaded_at')
    form = UploadCVForm()
    top_jobs = []
    latest_cv = cvs.first() if cvs.exists() else None
    if latest_cv and latest_cv.parsed_text:
        _, top_jobs = score_cv_and_get_jobs(latest_cv.parsed_text)
    return render(request, 'core/dashboard.html', {
        'form': form,
        'cvs': cvs,
        'latest_cv': latest_cv,
        'top_jobs': top_jobs,
    })

@login_required
def upload_cv(request):
    if request.method == 'POST':
        form = UploadCVForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_cv = form.save(commit=False)
            uploaded_cv.user = request.user
            uploaded_cv.save()

            # extract and score
            text = extract_cv_text(uploaded_cv.file.path)
            uploaded_cv.parsed_text = text
            score, top_jobs = score_cv_and_get_jobs(text)
            uploaded_cv.score = score
            uploaded_cv.top_jobs = top_jobs
            uploaded_cv.save()
            messages.success(request, "CV uploaded and scored.")
            return redirect('dashboard')
        else:
            messages.error(request, "Upload failed. Make sure file selected.")
    return redirect('dashboard')
