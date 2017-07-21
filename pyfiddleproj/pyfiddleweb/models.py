# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Script(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fiddle_name = models.CharField(
        default="myfiddle", max_length=100, blank=False)
    code = models.TextField(max_length=10000000, blank=False)
    commands = models.TextField(default='', max_length=1000, blank=True)
    inputs = models.TextField(default='', max_length=1000, blank=True)
    packages = models.TextField(default='', max_length=1000, blank=True)
    private = models.BooleanField(default=False, blank=True)
    version = models.BooleanField(default=False, blank=False)
    upload = models.FileField(
        db_index=False, default='', upload_to='', blank=True)
    runs = models.BigIntegerField(default=0, blank=True)
    active = models.BooleanField(default=True, blank=True)


class ScriptFiles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class SavedScripts(models.Model):
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class StarredScripts(models.Model):
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ScriptRuns(models.Model):
    token = models.CharField(default='', max_length=200)
    code = models.TextField(max_length=10000000, blank=True, null=True)
