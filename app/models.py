from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from os import path
import uuid
from django.contrib.postgres.fields import ArrayField


class Docs(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)    
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.TextField(blank=True)
    short_summary = models.TextField(blank=True)
    messages = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.__class__.__name__}: {str(self.id)}"

