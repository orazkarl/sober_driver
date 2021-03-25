from django.db import models
from ckeditor.fields import RichTextField

class TechInstructions(models.Model):
    content = RichTextField('Контент')

    class Meta:
        verbose_name = 'Техинструкция'
        verbose_name_plural = 'Техинструкция'