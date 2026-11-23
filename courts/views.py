from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import User
from accounts.views import role_required

from .forms import CourtForm
from .models import Court

admin_only = role_required(User.Role.ADMIN)


@admin_only
def court_list(request):
    return render(request, 'courts/court_list.html', {'courts': Court.objects.all()})


@admin_only
def court_create(request):
    form = CourtForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            court = form.save()
            messages.success(request, f"{court.name} was added.")
            return redirect('courts:list')
        messages.error(request, "Please fix the errors below.")
    return render(request, 'courts/court_form.html', {'form': form, 'title': 'Add court'})


@admin_only
def court_update(request, pk):
    court = get_object_or_404(Court, pk=pk)
    form = CourtForm(request.POST or None, instance=court)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f"{court.name} was updated.")
            return redirect('courts:list')
        messages.error(request, "Please fix the errors below.")
    return render(request, 'courts/court_form.html', {'form': form, 'title': f'Edit {court.name}'})


@admin_only
@require_POST
def court_delete(request, pk):
    court = get_object_or_404(Court, pk=pk)
    name = court.name
    try:
        court.delete()
        messages.success(request, f"{name} was deleted.")
    except ProtectedError:
        messages.error(request, f"{name} has bookings and can't be deleted. Set it to Maintenance instead.")
    return redirect('courts:list')