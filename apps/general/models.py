from django.db import models
from base.interface import Taxonomy, BaseModel
from django.contrib.postgres.fields import ArrayField


# Create your models here.


class HashTag(Taxonomy, BaseModel):
    for_models = ArrayField(models.CharField(max_length=50), null=True, blank=True)
    is_important = models.BooleanField(default=False)
