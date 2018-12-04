from django.db import models
from main.models import User, AbstractBase
from django.utils import timezone


# Create your models here.
class Period(AbstractBase):
    JAN = 1
    FEB = 2
    MAR = 3
    APR = 4
    MAY = 5
    JUN = 6
    JUL = 7
    AUG = 8
    SEP = 9
    OCT = 0
    NOV = 11
    DEC = 12
    MONTHS_CHOICES = (
        (JAN, 'Январь'),
        (FEB, 'Февраль'),
        (MAR, 'Март'),
        (APR, 'Апрель'),
        (MAY, 'Май'),
        (JUN, 'Июнь'),
        (JUL, 'Июль'),
        (AUG, 'Август'),
        (SEP, 'Сентябрь'),
        (OCT, 'Октябрь'),
        (NOV, 'Ноябрь'),
        (DEC, 'Декабрь'),
    )

    month = models.SmallIntegerField('Месяц', choices=MONTHS_CHOICES, default=DEC)
    year = models.SmallIntegerField('Год', blank=False, null=False, default=2018)
    is_finished = models.BooleanField('Закрыт?', null=False, default=False)
    created_at = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['-year', '-month']
        verbose_name = 'Период'
        verbose_name_plural = 'Периоды'

    def __str__(self):
        return '%s %s' % (self.MONTHS_CHOICES[self.month - 1][1], self.year)


class Notation(AbstractBase):
    class Meta:
        verbose_name = 'Нотация'
        verbose_name_plural = 'Нотации'

    title = models.CharField('Название', max_length=255, blank=True, null=True)
    sort = models.SmallIntegerField('Сортировка', blank=False, null=False, default=0)
    created_at = models.DateField(default=timezone.now)

    def __str__(self):
        return self.title


class Fee(AbstractBase):
    class Meta:
        verbose_name = 'Начисление'
        verbose_name_plural = 'Начисления'

    BUDGET = 0
    NON_BUDGET = 1
    ADVERT = 2
    FORMAT_CHOICES = (
        (BUDGET, 'Бюджетное'),
        (NON_BUDGET, 'Внебюджетное'),
        (ADVERT, 'Рекламное'),
    )
    format = models.SmallIntegerField('Тип начисления', choices=FORMAT_CHOICES, default=BUDGET)
    sum = models.IntegerField('Сумма', blank=False, null=False, default=6000)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fee = models.ForeignKey('Fee', on_delete=models.CASCADE, related_name='editable', null=True, blank=True)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    notation = models.ForeignKey(Notation, on_delete=models.CASCADE)
    notified_at = models.DateTimeField('Уведомлен?', null=True, blank=True)
    notes = models.TextField('За что', blank=True, null=True)
    created_at = models.DateField(default=timezone.now)

    def __str__(self):
        return '%s, %s' % (self.sum, self.user)


class Payment(AbstractBase):
    class Meta:
        verbose_name = 'Выплата'
        verbose_name_plural = 'Выплаты'

    FORMAT_CASH = 0
    FORMAT_ACCOUNT = 1
    FORMAT_TRANSFER = 2
    FORMAT_CHOICES = (
        (FORMAT_CASH, 'Наличными'),
        (FORMAT_ACCOUNT, 'Банковский счет'),
        (FORMAT_TRANSFER, 'Перевод через платежную систему'),
    )
    format = models.SmallIntegerField('Тип начисления', choices=FORMAT_CHOICES, default=FORMAT_CASH)
    sum = models.IntegerField('Сумма', blank=False, null=False, default=10000)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField('Комментарий к выплате', blank=True, null=True)
    notified_at = models.DateTimeField('Уведомлен?', null=True, blank=True)
    created_at = models.DateField(default=timezone.now)
