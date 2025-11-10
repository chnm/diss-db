import datetime

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
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


# Ensure that the ORCID is in the correct format
orcid_validator = RegexValidator("\d{4}-\d{4}-\d{4}-\d{4}")


class Scholar(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    aha_scholar_id = models.BigIntegerField(
        unique=True,
        blank=True,
        null=True,
        verbose_name="AHA scholar ID",
        help_text="The identifier used by the AHA for a scholar",
    )
    aha_name = models.CharField(
        max_length=200,
        default=None,
        blank=True,
        null=True,
        verbose_name="AHA name",
        help_text="The name provided in the AHA dataset",
        editable=False,
    )
    name_first = models.CharField(
        max_length=200,
        blank=False,
        verbose_name="First name",
    )
    name_middle = models.CharField(
        max_length=200,
        default=None,
        blank=True,
        verbose_name="Middle name",
    )
    name_last = models.CharField(
        max_length=200,
        blank=False,
        verbose_name="Last name",
    )
    name_suffix = models.CharField(
        max_length=200,
        default=None,
        blank=True,
        verbose_name="Suffix",
    )
    orcid = models.CharField(
        max_length=19,
        default=None,
        blank=True,
        null=True,
        verbose_name="ORCID",
        help_text="ORCID in 0000-0000-0000-0000 format",
        validators=[orcid_validator],
    )

    @property
    def name_full(self) -> str:
        output = self.name_first
        if self.name_middle:
            output = output + " " + self.name_middle
        output = output + " " + self.name_last
        if self.name_suffix:
            output = output + " " + self.name_suffix
        return output

    @property
    def name_full_rev(self) -> str:
        output = self.name_last + ", " + self.name_first
        if self.name_middle:
            output = output + " " + self.name_middle
        if self.name_suffix:
            output = output + ", " + self.name_suffix
        return output

    @property
    def orcid_url(self) -> str:
        if self.orcid:
            return f"https://orcid.org/{self.orcid}"
        else:
            return None

    def __str__(self) -> str:
        return self.name_full_rev

    class Meta:
        ordering = ["name_last", "name_first", "name_middle"]


class Dissertation(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    aha_dissertation_id = models.BigIntegerField(
        unique=True,
        default=None,
        blank=True,
        null=True,
        verbose_name="AHA dissertation ID",
        help_text="The identifier used by the AHA for a dissertation",
    )
    title = models.CharField(max_length=2000, blank=False)
    year = models.PositiveSmallIntegerField(
        db_index=True,
        validators=[
            MinValueValidator(1700, "The year must be after 1700"),
            MaxValueValidator(
                datetime.date.today().year,
                "The year must be the current year or before",
            ),
        ],
    )
    author = models.ForeignKey(Scholar, on_delete=models.PROTECT)
    school = models.ForeignKey(School, on_delete=models.PROTECT)
    aha_author_id = models.BigIntegerField(
        verbose_name="AHA author ID",
        editable=False,
        blank=True,
        null=True,
        default=None,
    )
    aha_school_id = models.BigIntegerField(
        verbose_name="AHA school ID",
        editable=False,
        blank=True,
        null=True,
        default=None,
    )

    @property
    def main_title(self) -> str:
        return self.title.split(":")[0]

    def __str__(self) -> str:
        return f"{self.main_title} ({self.author})"


class CommitteeMember(models.Model):
    scholar = models.ForeignKey(Scholar, on_delete=models.PROTECT)

    CHAIR = "chair"
    READER = "reader"
    COMMITTEE_CHOICES = [
        (CHAIR, "chair"),
        (READER, "reader"),
    ]
    role = models.CharField(
        max_length=20,
        choices=COMMITTEE_CHOICES,
        default=READER,
    )

    dissertation = models.ForeignKey(Dissertation, on_delete=models.PROTECT)

    aha_scholar_id = models.BigIntegerField(
        verbose_name="AHA scholar ID",
        editable=False,
        blank=True,
        null=True,
        default=None,
    )
    aha_dissertation_id = models.BigIntegerField(
        verbose_name="AHA dissertation ID",
        editable=False,
        blank=True,
        null=True,
        default=None,
    )

    def __str__(self) -> str:
        return str(self.scholar)


class DuplicateCandidate(models.Model):
    """Store potential duplicate scholar pairs for review"""

    scholar_1 = models.ForeignKey(
        Scholar, on_delete=models.CASCADE, related_name="duplicate_candidate_1"
    )
    scholar_2 = models.ForeignKey(
        Scholar, on_delete=models.CASCADE, related_name="duplicate_candidate_2"
    )
    confidence_score = models.FloatField(
        help_text="Confidence score from dedupe algorithm (0-1)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    is_duplicate = models.BooleanField(
        null=True,
        blank=True,
        help_text="True if confirmed duplicate, False if not, None if not reviewed",
    )
    notes = models.TextField(blank=True, help_text="Review notes")

    class Meta:
        unique_together = ["scholar_1", "scholar_2"]
        ordering = ["-confidence_score", "-created_at"]

    def __str__(self):
        return f"{self.scholar_1.name_full} ~ {self.scholar_2.name_full} ({self.confidence_score:.2f})"
