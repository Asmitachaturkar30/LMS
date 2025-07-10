from django.db import models

class FieldKeyMapping(models.Model):
    field_id = models.AutoField(primary_key=True)
    model_name = models.CharField(max_length=100)
    field_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('model_name', 'field_name')
        db_table = 'FieldKeyMapping'

    def __str__(self):
        return f"{self.model_name}.{self.field_name} -> {self.display_name}"


# class