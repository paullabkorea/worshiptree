from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CommentForm, RegisterForm, WorshipRecordForm
from .models import Like, WorshipRecord


# --- Auth ---

class CustomLoginView(LoginView):
    template_name = 'worship/login.html'


class CustomLogoutView(LogoutView):
    pass


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('worship:home')
    else:
        form = RegisterForm()
    return render(request, 'worship/register.html', {'form': form})


# --- Home ---

@login_required
def home(request):
    records = request.user.worship_records.all()
    return render(request, 'worship/home.html', {'records': records})


# --- Worship Record CRUD ---

@login_required
def record_create(request):
    if request.method == 'POST':
        form = WorshipRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            return redirect('worship:home')
    else:
        form = WorshipRecordForm()
    return render(request, 'worship/record_form.html', {'form': form, 'edit': False})


@login_required
def record_edit(request, pk):
    record = get_object_or_404(WorshipRecord, pk=pk, user=request.user)
    if request.method == 'POST':
        form = WorshipRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('worship:home')
    else:
        form = WorshipRecordForm(instance=record)
    return render(request, 'worship/record_form.html', {'form': form, 'edit': True})


@login_required
@require_POST
def record_delete(request, pk):
    record = get_object_or_404(WorshipRecord, pk=pk, user=request.user)
    record.delete()
    return redirect('worship:home')


# --- Board ---

@login_required
def board_list(request):
    records = WorshipRecord.objects.filter(is_shared=True).select_related('user')
    # simple pagination
    page = int(request.GET.get('page', 1))
    per_page = 10
    total = records.count()
    records = records[(page - 1) * per_page:page * per_page]
    total_pages = (total + per_page - 1) // per_page
    return render(request, 'worship/board_list.html', {
        'records': records,
        'page': page,
        'total_pages': total_pages,
        'page_range': range(1, total_pages + 1),
    })


@login_required
def board_detail(request, pk):
    record = get_object_or_404(
        WorshipRecord.objects.select_related('user'),
        pk=pk,
        is_shared=True,
    )
    comments = record.comments.select_related('user')
    comment_form = CommentForm()
    user_liked = record.likes.filter(user=request.user).exists()
    return render(request, 'worship/board_detail.html', {
        'record': record,
        'comments': comments,
        'comment_form': comment_form,
        'user_liked': user_liked,
    })


# --- Comments & Likes ---

@login_required
@require_POST
def comment_create(request, pk):
    record = get_object_or_404(WorshipRecord, pk=pk, is_shared=True)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.record = record
        comment.user = request.user
        comment.save()
    return redirect('worship:board_detail', pk=pk)


@login_required
@require_POST
def like_toggle(request, pk):
    record = get_object_or_404(WorshipRecord, pk=pk, is_shared=True)
    like, created = Like.objects.get_or_create(record=record, user=request.user)
    if not created:
        like.delete()
    return redirect('worship:board_detail', pk=pk)


# --- API ---

@login_required
def tree_data(request):
    records = request.user.worship_records.all()
    fruits = []
    for r in records:
        fruits.append({
            'id': r.id,
            'date': r.date.isoformat(),
            'type': r.worship_type,
            'title': r.title,
        })
    return JsonResponse({'fruits': fruits})
