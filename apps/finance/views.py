from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from apps.users.mixins import AdminRequiredMixin
from apps.students.models import Student

from .forms import InvoiceItemFormset, InvoiceReceiptFormSet, Invoices
from .models import Invoice, InvoiceItem, Receipt


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "finance/invoice_list.html"
    paginate_by = 25

    def get_queryset(self):
        # Recupere recherche
        search_query = self.request.GET.get('search', '').strip()
        
        # Filtration
        if hasattr(self.request.user, 'role'):
            if self.request.user.role == 'student':
                # Étudiant : ne voit que ses propre facturet
                queryset = Invoice.objects.filter(
                    student=self.request.user.student_profile
                )
            elif self.request.user.role in ['admin', 'staff']:
                # Admin/Staff : voir toutes les factures
                queryset = super().get_queryset()
            else:
                queryset = Invoice.objects.none()
        else:
            queryset = super().get_queryset()
        
        # Appliquer ny recherche raha misy
        if search_query:
            queryset = queryset.filter(
                student__surname__icontains=search_query
            ) | queryset.filter(
                student__firstname__icontains=search_query
            ) | queryset.filter(
                student__other_name__icontains=search_query
            )
        
        return queryset


class InvoiceCreateView(AdminRequiredMixin, LoginRequiredMixin, CreateView):
    model = Invoice
    fields = "__all__"
    success_url = "/finance/list"

    def get_context_data(self, **kwargs):
        context = super(InvoiceCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["items"] = InvoiceItemFormset(
                self.request.POST, prefix="invoiceitem_set"
            )
        else:
            context["items"] = InvoiceItemFormset(prefix="invoiceitem_set")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["items"]
        self.object = form.save()
        if self.object.id != None:
            if form.is_valid() and formset.is_valid():
                formset.instance = self.object
                formset.save()
        return super().form_valid(form)


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = "finance/invoice_detail.html"

    def get_object(self):
        invoice = super().get_object()
        
        # Vérifier les permissions : étudiant ne peut voir que ses factures
        if hasattr(self.request.user, 'role') and self.request.user.role == 'student':
            if invoice.student != self.request.user.student_profile:
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied("Vous n'avez pas l'autorisation de voir cette facture.")
        
        return invoice

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        context["items"] = InvoiceItem.objects.filter(invoice=self.object)
        context["receipts"] = Receipt.objects.filter(invoice=self.object)
        return context


class InvoiceUpdateView(AdminRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Invoice
    fields = "__all__"
    success_url = "/finance/list"

    def get_context_data(self, **kwargs):
        context = super(InvoiceUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["receipts"] = InvoiceReceiptFormSet(
                self.request.POST, prefix="receipt_set"
            )
            context["items"] = InvoiceItemFormset(
                self.request.POST, prefix="invoiceitem_set"
            )
        else:
            context["receipts"] = InvoiceReceiptFormSet(
                instance=self.object, prefix="receipt_set"
            )
            context["items"] = InvoiceItemFormset(
                instance=self.object, prefix="invoiceitem_set"
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["receipts"]
        itemsformset = context["items"]
        if form.is_valid() and formset.is_valid() and itemsformset.is_valid():
            form.save()
            formset.save()
            itemsformset.save()
        return super().form_valid(form)


class InvoiceDeleteView(AdminRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Invoice
    success_url = reverse_lazy("invoice-list")
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        from django.contrib import messages
        messages.success(request, f"La facture de {obj.student} a été supprimée avec succès.")
        return super().delete(request, *args, **kwargs)


class ReceiptCreateView(LoginRequiredMixin, CreateView):
    model = Receipt
    fields = ["amount_paid", "date_paid", "comment"]
    success_url = reverse_lazy("invoice-list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        invoice = Invoice.objects.get(pk=self.request.GET["invoice"])
        obj.invoice = invoice
        obj.save()
        return redirect("invoice-list")

    def get_context_data(self, **kwargs):
        context = super(ReceiptCreateView, self).get_context_data(**kwargs)
        invoice = Invoice.objects.get(pk=self.request.GET["invoice"])
        context["invoice"] = invoice
        return context


class ReceiptUpdateView(LoginRequiredMixin, UpdateView):
    model = Receipt
    fields = ["amount_paid", "date_paid", "comment"]
    success_url = reverse_lazy("invoice-list")


class ReceiptDeleteView(LoginRequiredMixin, DeleteView):
    model = Receipt
    success_url = reverse_lazy("invoice-list")


@login_required
def bulk_invoice(request):
    return render(request, "finance/bulk_invoice.html")
