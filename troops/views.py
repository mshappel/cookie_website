
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView

from .forms import TroopForm
from .models import Troop


# -----------------------------------------------------------------------
# Troop General User Functions
# -----------------------------------------------------------------------
class TroopListView(LoginRequiredMixin, ListView):
    model = Troop
    template_name = 'troops.html'


# -----------------------------------------------------------------------
# Troop Admin Functions
# -----------------------------------------------------------------------
class TroopCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = 'troops.add_troop'
    form_class = TroopForm
    success_url = reverse_lazy('troops:troops')
    template_name = 'new_troop.html'


class TroopUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = 'troops.change_troop'
    model = Troop
    fields = ['troop_number', 'troop_cookie_coordinator', 'troop_level', 'super_troop']
    success_url = reverse_lazy('troops:troops')
    template_name = 'edit_troop.html'


class TroopDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    """Delete an existing booth location"""
    permission_required = 'troops.delete_troop'
    model = Troop
    template_name = 'troop_confirm_delete.html'
    success_url = reverse_lazy('troops:troops')
