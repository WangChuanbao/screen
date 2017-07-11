# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import models


# Create your models here.
class Follow(models.Model):
    host_id = models.IntegerField()
    host_name = models.CharField(max_length=255)
    item_id = models.IntegerField()
    item_name = models.CharField(max_length=255)

    class Meta:
        ordering = ('id',)

    def toDICT(self):
        return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]])