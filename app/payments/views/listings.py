from constants import CURRENCY_SYMBOL_MAP, USD_TO_NGN_RATE
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, F, Q, Case, When, DecimalField
from django.views.generic import ListView
from payments.domain.enums import PaymentStatus
from registry_utils import get_registered_model
from template_map.payments import Payments as PaymentTemplates


class UserPaymentsListView(LoginRequiredMixin, ListView):
    model = get_registered_model("payments", "Payment")
    template_name = PaymentTemplates.PAYMENT_SUMMARY
    context_object_name = "transactions"
    paginate_by = 7
    RATE = Decimal(str(USD_TO_NGN_RATE))
    
    def get_queryset(self):
        return super().get_queryset().filter(
            user=self.request.user
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usd_equivalent = Case(
            When(currency='NGN', then=F('amount_decimal') / self.RATE),
            default=F('amount_decimal'),
            output_field=DecimalField()
        )

        stats = self.get_queryset().aggregate(
            all_total=Sum(
                usd_equivalent,
                filter=Q(status__in=[
                    PaymentStatus.SUCCESS, 
                    PaymentStatus.PENDING, 
                    PaymentStatus.ABANDONED
                ])
            ),
            completed_total=Sum(
                Case(
                    When(status=PaymentStatus.SUCCESS, then=usd_equivalent), 
                    output_field=DecimalField()
                )
            ),
            pending_total=Sum(
                Case(
                    When(status=PaymentStatus.PENDING, then=usd_equivalent), 
                    output_field=DecimalField()
                )
            ),
            abandoned_total=Sum(
                Case(
                    When(status=PaymentStatus.ABANDONED, then=usd_equivalent), 
                    output_field=DecimalField()
                )
            ),
        )

        context['stats'] = {
            'all': self.format_currency_human(stats['all_total']),
            'completed': self.format_currency_human(stats['completed_total']),
            'pending': self.format_currency_human(stats['pending_total']),
            'abandoned': self.format_currency_human(stats['abandoned_total']),
        }
        context['currency_map'] = CURRENCY_SYMBOL_MAP
        return context

    def format_currency_human(self, amount):
        """
        Formats Decimal numbers into k, M, or B suffixes.
        """
        if amount is None or amount == 0:
            return "0.00"
        
        abs_amount = abs(amount)
        
        if abs_amount >= Decimal('1000000000'):
            return f"{amount / Decimal('1000000000'):.2f}B"
        if abs_amount >= Decimal('1000000'):
            return f"{amount / Decimal('1000000'):.2f}M"
        if abs_amount >= Decimal('1000'):
            return f"{amount / Decimal('1000'):.1f}k"
        return f"{amount:,.2f}"