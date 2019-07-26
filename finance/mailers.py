import html2text
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader

from main.email_backends import FinanceEmailBackend
from .models import Payment


class AbstractAdminMailer(object):
    """docstring for AbstractMailer"""

    def __init__(self, *args, **kwargs):
        super(AbstractAdminMailer, self).__init__()

        self.html = ''
        self.plain = ''
        self.prepare_full_content()

    def prepare_full_content(self):
        layout_tpl_path = '%s/finance/mailers/layout.html' % settings.TEMPLATES[0]['DIRS'][0]

        t = loader.get_template(layout_tpl_path)
        self.html = t.render({
            'content': self.content
        })

        # create plain-text version
        self.plain = html2text.html2text(self.content)

    def send(self):
        with FinanceEmailBackend() as connection:
            msg = EmailMultiAlternatives(self.subject, self.plain, None, [self.to], connection=connection)
            msg.attach_alternative(self.html, "text/html")
            msg.send()


class FeeNotifyMailer(AbstractAdminMailer):
    def __init__(self, fee, *args, **kwargs):
        self.TEMPLATE = 'fee_notify'
        self.fee = fee

        self.content = ''
        self.prepare_content()
        self.to = fee.user.email

        super(FeeNotifyMailer, self).__init__(fee)

        self.to = fee.user.email
        self.subject = 'Новое начисление на сумму %s₽ от %s' % (fee.sum, fee.created_at)

    def prepare_content(self):
        tpl_path = '%s/finance/mailers/%s.html' % (
            settings.TEMPLATES[0]['DIRS'][0],
            self.TEMPLATE,
        )

        t = loader.get_template(tpl_path)
        self.content = t.render({
            'fee': self.fee,
        })


class PaymentNotifyMailer(AbstractAdminMailer):
    def __init__(self, payment, *args, **kwargs):
        self.TEMPLATE = 'payment_notify'
        self.payment = payment

        self.content = ''
        self.prepare_content()
        self.to = payment.user.email

        super(PaymentNotifyMailer, self).__init__(payment)

        self.to = payment.user.email
        self.subject = 'Доступна выплата на сумму %s₽ от %s' % (payment.sum, payment.created_at)

    def prepare_content(self):
        tpl_path = '%s/finance/mailers/%s.html' % (
            settings.TEMPLATES[0]['DIRS'][0],
            self.TEMPLATE,
        )

        t = loader.get_template(tpl_path)
        self.content = t.render({
            'payment': self.payment,
            'Payment': Payment,
        })
