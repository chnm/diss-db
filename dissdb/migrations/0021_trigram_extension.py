from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dissdb", "0020_department_dissertation_department_and_more"),
    ]

    operations = [
        TrigramExtension(),
    ]