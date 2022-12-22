from django.db import models

# Create your models here.
class School(models.Model):
    id = models.BigAutoField(primary_key=True)
    aha_school_id = models.BigIntegerField(
        unique=True,
        verbose_name="AHA school ID",
        help_text="The identifier used by the AHA for a school",
    )
    name = models.CharField(help_text="The name of the school", max_length=200)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]
