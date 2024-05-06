from typing import List

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import JSONField, Q
from django.db.models.signals import post_save
from django.dispatch import receiver

from magplan.models.abc import AbstractBase

UserModel = get_user_model()


class User(UserModel):
    class Meta:
        proxy = True

    meta = JSONField(default=dict)

    def __str__(self):
        return self.display_name_default

    @property
    def display_name_default(self):
        p: Profile = self.profile
        if p.l_name and p.f_name:
            return "%s %s" % (p.f_name, p.l_name)
        elif p.n_name:
            return p.n_name
        else:
            return self.email

    @property
    def display_name_generic(self):
        p: Profile = self.profile
        if p.l_name_generic and p.f_name_generic:
            return "%s %s" % (p.f_name_generic, p.l_name_generic)
        elif p.n_name:
            return p.n_name
        else:
            return self.email

    @property
    def str_reverse(self):
        return self.__str__()

    @property
    def str_employee(self):
        return self.__str__()

    class Meta:
        permissions = (
            ("access_magplan", "Can access magplan"),
            ("manage_authors", "Can manage authors"),
        )

    def is_member(self, group_name: str) -> bool:
        """Check if user is member of group

        :param group_name: Group name to check user belongs to
        :return: True if a memeber, otherwise False
        """
        return self.groups.filter(name=group_name).exists()


class Profile(AbstractBase):
    is_public = models.BooleanField(null=False, blank=False, default=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    f_name = models.CharField("Имя", max_length=255, blank=True, null=True)
    m_name = models.CharField("Отчество", max_length=255, blank=True, null=True)
    l_name = models.CharField("Фамилия", max_length=255, blank=True, null=True)
    n_name = models.CharField("Ник", max_length=255, blank=True, null=True)
    bio = models.TextField("Био", blank=True, null=True)

    # Global fields
    f_name_generic = models.CharField(
        "Имя латинницей", max_length=255, blank=True, null=True
    )
    l_name_generic = models.CharField(
        "Фамилия латинницей", max_length=255, blank=True, null=True
    )
    bio_generic = models.TextField("Био латинницей", blank=True, null=True)

    RUSSIA = 0
    UKRAINE = 1
    BELARUS = 2
    KAZAKHSTAN = 3
    COUNTRY_CHOICES = (
        (RUSSIA, "Россия"),
        (UKRAINE, "Украина"),
        (BELARUS, "Беларусь"),
        (KAZAKHSTAN, "Казахстан"),
    )
    country = models.SmallIntegerField(
        "Страна", choices=COUNTRY_CHOICES, default=RUSSIA
    )
    city = models.CharField(
        "Город или поселок", max_length=255, blank=True, null=True
    )
    notes = models.TextField("Примечания", blank=True, null=True)


def users_with_perm(
    perm_name: str, include_superuser: bool = True
) -> List[User]:
    """Get all users by full permission name

    :param perm_name: permission name without app name
    :param include_superuser:
    :return:
    """
    return User.objects.filter(
        Q(is_superuser=include_superuser)
        | Q(user_permissions__codename=perm_name)
        | Q(groups__permissions__codename=perm_name)
    ).distinct()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
