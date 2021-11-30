from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from .forms import CustomUserCreationForm, TroopForm
from .models import Troop

# Create your views here.
# -----------------------------------------------------------------------
# Troop Admin Functions
# -----------------------------------------------------------------------


@login_required
@permission_required('users.troop_creation', raise_exception=True)
def create_troop(request):
    """Create a new troop"""
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = TroopForm()
    else:
        # POST data submitted; process data.
        form = TroopForm(data=request.POST)
        if form.is_valid():
            loc = form.save()
            return redirect('users:troops')

    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'troops/new_troop.html', context)


@login_required
@permission_required('users.troop_updates', raise_exception=True)
def edit_troop(request, troop_number):
    """Edit an existing troop"""
    troop = Troop.objects.get(troop_number=troop_number)

    if request.method != 'POST':
        # Initial request; pre-fill with the current entry.
        form = TroopForm(instance=troop, troop_number=troop_number)
    else:
        # POST data submitted; process data.
        form = TroopForm(instance=troop, data=request.POST, troop_number=troop_number)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('users:troops'))

    context = {'troop': troop, 'form': form}
    return render(request, 'troops/edit_troop.html', context)

class TroopDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    """Delete an existing booth location"""
    permission_required = 'users.troop_deletion'
    model = Troop
    template_name = 'troops/troop_confirm_delete.html'
    success_url = reverse_lazy('users:troops')

# -----------------------------------------------------------------------
# Troop User Functions
# -----------------------------------------------------------------------


@login_required
def troops(request):
    """Display all booths for admins to edit"""
    troops = Troop.objects.order_by('troop_number')
    context = {'troops': troops}
    return render(request, 'troops/troops.html', context)


def register(request):
    """Register a new user"""
    if request.method != 'POST':
        # Display blank registration form.
        form = CustomUserCreationForm()
    else:
        # Process completed form.
        form = CustomUserCreationForm(data=request.POST)

        if form.is_valid():
            new_user = form.save()
            # Log the user in then redirect to home page.
            login(request, new_user)
            return redirect('cookie_booths:index')

    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'registration/register.html', context)
