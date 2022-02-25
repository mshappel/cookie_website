from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DeleteView

from .forms import TroopForm
from .models import Troop


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
            return redirect('troops:troops')

    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'new_troop.html', context)


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
            return HttpResponseRedirect(reverse_lazy('troops:troops'))

    context = {'troop': troop, 'form': form}
    return render(request, 'edit_troop.html', context)


class TroopDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    """Delete an existing booth location"""
    permission_required = 'users.troop_deletion'
    model = Troop
    template_name = 'troop_confirm_delete.html'
    success_url = reverse_lazy('troops:troops')


# -----------------------------------------------------------------------
# Troop User Functions
# -----------------------------------------------------------------------
@login_required
def troops(request):
    """Display all booths for admins to edit"""
    troops = Troop.objects.order_by('troop_number')
    context = {'troops': troops}
    return render(request, 'troops.html', context)
