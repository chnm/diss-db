import datetime

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.text import slugify
from simple_history.models import HistoricalRecords

class Source(models.Model):
    """Track the source of the data"""

    id = models.BigAutoField(primary_key=True)

    name = models.CharField(
        max_length=200,
        help_text="Name of the source (organization, department, person, etc.)"
    )

    SOURCE_TYPE_CHOICES = [
        ('organization', 'Organization'),
        ('department', 'Department'),
        ('person', 'Person'),
        ('other', 'Other'),
    ]
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        help_text="Type of source"
    )

    contact_info = models.TextField(
        blank=True,
        default='',
        help_text="Contact information or additional details"
    )

    # Tracking
    date_added = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(
        blank=True,
        default='',
        help_text="Additional notes about this source"
    )

    history = HistoricalRecords()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"

class ThematicEmphasis(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True, help_text="e.g. Political, Race, Gender")
    slug = models.SlugField(max_length=200, unique=True, help_text="URL-friendly identifier")

    source = models.ForeignKey(
        Source,
        on_delete=models.PROTECT,
        default=1,
        help_text="The source for this record"
    )

    history = HistoricalRecords()

    class Meta:
        ordering = ['name']
        verbose_name_plural = "thematic emphases"

    def __str__(self):
        return self.name


class GeographicEmphasis(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True, help_text="e.g. North America, East Asia")
    slug = models.SlugField(max_length=200, unique=True, help_text="URL-friendly identifier")

    source = models.ForeignKey(
        Source,
        on_delete=models.PROTECT,
        default=1,
        help_text="The source for this record"
    )

    history = HistoricalRecords()

    class Meta:
        ordering = ['name']
        verbose_name_plural = "geographic emphases"

    def __str__(self):
        return self.name

# Create your models here.
class School(models.Model):
    id = models.BigAutoField(primary_key=True)
    aha_school_id = models.BigIntegerField(
        unique=True,
        verbose_name="AHA school ID",
        help_text="The identifier used by the AHA for a school",
    )
    name = models.CharField(help_text="The name of the school", max_length=200)

    source = models.ForeignKey(
        Source,
        on_delete=models.PROTECT,
        default=1,
        help_text="The source for this record"
    )

    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]

class Department(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(help_text="The name of the department", max_length=200)
    school = models.ForeignKey(School, on_delete=models.PROTECT)

# Ensure that the ORCID is in the correct format
orcid_validator = RegexValidator(r"\d{4}-\d{4}-\d{4}-\d{4}")


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
        null=True,
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
        null=True,
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

    affiliation = models.CharField(
        default=None,
        blank=True,
        null=True,
        verbose_name="Current University or other affiliation",
        help_text="The name of this scholar's current affiliation",
        max_length=200
    )

    source = models.ForeignKey(
        Source,
        on_delete=models.PROTECT,
        default=1,
        help_text="The source for this record"
    )

    history = HistoricalRecords()

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

    def get_absolute_url(self):
        from django.urls import reverse

        name_slug = slugify(f"{self.name_last}-{self.name_first}") or "scholar"
        return reverse("scholar-detail", kwargs={"pk": self.pk, "slug": name_slug})

    def __str__(self) -> str:
        return self.name_full_rev

    class Meta:
        ordering = ["name_last", "name_first", "name_middle"]

class ScholarWebsite(models.Model):
    PERSONAL = 'personal'
    DEPARTMENT = 'department'
    SOCIAL = 'social media'
    OTHER = 'other'

    WEBSITE_TYPE_CHOICES = [
        (PERSONAL, 'Personal Website'),
        (DEPARTMENT, 'Department Profile'),
        (SOCIAL, 'Social Media Profile'),
        (OTHER, 'Other'),
    ]

    scholar = models.ForeignKey(
        Scholar,
        on_delete=models.CASCADE,
        related_name='websites'
    )
    url = models.URLField(max_length=500)
    website_type = models.CharField(
        max_length=20,
        choices=WEBSITE_TYPE_CHOICES,
        default=OTHER,
    )
    label = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional custom label, e.g. 'GMU Faculty Page'"
    )

    source = models.ForeignKey(
        Source,
        on_delete=models.PROTECT,
        default=1,
        help_text="The source for this record"
    )

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.get_website_type_display()} - {self.url}"

    class Meta:
        ordering = ['website_type']

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
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)
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

    abstract = models.TextField(
        blank=True,
        null=True,
        default=None,
        help_text="Abstract of the dissertation"
    )

    source = models.ForeignKey(
        Source,
        on_delete=models.PROTECT,
        default=1,
        help_text="The source for this record"
    )

    # Inside the Dissertation model, add these fields:
    thematic_emphases = models.ManyToManyField(
        ThematicEmphasis,
        blank=True,
        related_name='dissertations',
        help_text="Thematic tags for this dissertation"
    )
    
    geographic_emphases = models.ManyToManyField(
        GeographicEmphasis,
        blank=True,
        related_name='dissertations',
        help_text="Geographic tags for this dissertation"
    )

    history = HistoricalRecords()

    @property
    def main_title(self) -> str:
        return self.title.split(":")[0]

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("diss-detail", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return f"{self.main_title} ({self.author})"

class DissertationLink(models.Model):
    PROQUEST = 'proquest'
    INSTITUTIONAL = 'institutional'
    PDF = 'pdf'
    OTHER = 'other'

    LINK_TYPE_CHOICES = [
        (PROQUEST, 'ProQuest'),
        (INSTITUTIONAL, 'Institutional Repository'),
        (PDF, 'PDF'),
        (OTHER, 'Other'),
    ]

    dissertation = models.ForeignKey(
        Dissertation,
        on_delete=models.CASCADE,
        related_name='links'
    )
    url = models.URLField(max_length=500)
    link_type = models.CharField(
        max_length=20,
        choices=LINK_TYPE_CHOICES,
        default=OTHER,
    )
    label = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional custom label, e.g. 'GMU Institutional Repository'"
    )

    source = models.ForeignKey(
        Source,
        on_delete=models.PROTECT,
        default=1,
        help_text="The source for this record"
    )

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.get_link_type_display()} - {self.url}"

    class Meta:
        ordering = ['link_type']
        # Prevent storing the same URL twice for the same dissertation
        unique_together = ['dissertation', 'url']

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

    source = models.ForeignKey(
        Source,
        on_delete=models.PROTECT,
        default=1,
        help_text="The source for this record"
    )

    history = HistoricalRecords()

    class Meta:
        indexes = [
            models.Index(fields=['role', 'scholar'], name='idx_cm_role_scholar'),
            models.Index(fields=['role', 'dissertation'], name='idx_cm_role_diss'),
        ]

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

    history = HistoricalRecords()

    class Meta:
        unique_together = ["scholar_1", "scholar_2"]
        ordering = ["-confidence_score", "-created_at"]

    def __str__(self):
        return f"{self.scholar_1.name_full} ~ {self.scholar_2.name_full} ({self.confidence_score:.2f})"
