from django.contrib import admin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
# Register your models here.
from .models import Period, Fee, Payment, Notation
from .mailers import FeeNotifyMailer, PaymentNotifyMailer
import datetime


def mark_fees_notified(modeladmin, request, queryset):
    queryset.update(notified_at=datetime.datetime.now())


mark_fees_notified.short_description = "Пометить уведомленными"


def notify_fee(modeladmin, request, queryset):
    for fee in queryset.all():
        mailer = FeeNotifyMailer(fee, )
        mailer.send()
        fee.notified_at = datetime.datetime.now()
        fee.save()


notify_fee.short_description = "Уведомить о начислении"


def notify_payment(modeladmin, request, queryset):
    for payment in queryset.all():
        mailer = PaymentNotifyMailer(payment, )
        mailer.send()
        payment.notified_at = datetime.datetime.now()
        payment.save()


notify_payment.short_description = "Уведомить о выплате"


class PeriodListFilter(admin.SimpleListFilter):
    title = 'Период'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'period'

    def lookups(self, request, model_admin):
        periods = [(p.id, p) for p in Period.objects.all()]
        return periods

    def queryset(self, request, queryset):
        return queryset.filter(period=self.value())


class PeriodAdmin(admin.ModelAdmin):

    def get_ordering(self, request):
        return ['-year', '-month', ]


class FeeInline(admin.TabularInline):
    model = Fee
    exclude = ('notified_at', 'created_at')
    max_num = 1


class FeeAdmin(admin.ModelAdmin):
    list_display = ('format', 'user', 'sum', 'notation', 'notes', 'period', 'notified_at')
    list_filter = (
        ('period', RelatedDropdownFilter),
        ('user', RelatedDropdownFilter),
        ('notation', RelatedDropdownFilter),
        ('notified_at'),
    )
    exclude = ('fee', 'created_at', 'notified_at')

    inlines = [
        FeeInline,
    ]

    actions = [mark_fees_notified, notify_fee]

    def get_ordering(self, request):
        return ['-period__year', '-period__month']


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('format', 'user', 'sum', 'notified_at',)
    list_filter = (
        ('user', RelatedDropdownFilter),
        ('notified_at'),
    )

    actions = [notify_payment]

    def get_ordering(self, request):
        return ['-created_at']


class UserAdmin(admin.ModelAdmin):
    list_display = ('l_name', 'f_name', 'm_name', 'country', 'city')
    search_fields = ['email', 'l_name']

    def get_ordering(self, request):
        return ['l_name']


admin.site.register(Period, PeriodAdmin)
admin.site.register(Fee, FeeAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Notation)
