from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import (
    Dissertation,
    GeographicEmphasis,
    Scholar,
    School,
    Source,
    ThematicEmphasis,
)


class GeographicEmphasisDisplayNameTests(SimpleTestCase):
    def test_removes_imported_numeric_prefix(self):
        emphasis = GeographicEmphasis(name="500 The Americas")

        self.assertEqual(emphasis.display_name, "The Americas")

    def test_preserves_label_without_numeric_prefix(self):
        emphasis = GeographicEmphasis(name="North America")

        self.assertEqual(emphasis.display_name, "North America")


class UnifiedSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        source = Source.objects.create(
            id=900001,
            name="Test source",
            source_type="other",
        )
        cls.school = School.objects.create(
            id=900001,
            aha_school_id=900001,
            name="Test Institute of Atlantic Studies",
            source=source,
        )
        cls.scholar = Scholar.objects.create(
            id=900001,
            aha_scholar_id=900001,
            name_first="Jane",
            name_last="Smith",
            affiliation="Center for Atlantic History",
            source=source,
        )
        cls.dissertation = Dissertation.objects.create(
            id=900001,
            aha_dissertation_id=900001,
            title="Networks of Colonial Virginia",
            year=1998,
            author=cls.scholar,
            school=cls.school,
            source=source,
        )
        cls.geographic = GeographicEmphasis.objects.create(
            id=900001,
            aha_id=900001,
            name="500 Atlantic World",
            slug="atlantic-world",
            source=source,
        )
        cls.thematic = ThematicEmphasis.objects.create(
            id=900001,
            aha_id=900001,
            name="Political culture",
            slug="political-culture",
            source=source,
        )
        cls.dissertation.geographic_emphases.add(cls.geographic)
        cls.dissertation.thematic_emphases.add(cls.thematic)

    def test_blank_search_prompts_for_a_query(self):
        response = self.client.get(reverse("search"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["searched"])
        self.assertContains(response, "Enter a title, scholar, institution, or field")

    def test_groups_matches_across_record_types(self):
        response = self.client.get(reverse("search"), {"q": "Atlantic"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["search_counts"]["scholars"], 1)
        self.assertEqual(response.context["search_counts"]["fields"], 1)
        self.assertContains(response, "Jane Smith")
        self.assertContains(response, "Atlantic World")

    def test_title_and_institution_matches_link_to_catalogue(self):
        title_response = self.client.get(
            reverse("search"),
            {"q": "Networks of Colonial Virginia"},
        )
        school_response = self.client.get(reverse("search"), {"q": "Test Institute"})

        self.assertEqual(title_response.context["search_counts"]["dissertations"], 1)
        self.assertContains(title_response, self.dissertation.title)
        self.assertEqual(school_response.context["search_counts"]["schools"], 1)
        self.assertContains(school_response, self.school.name)
        self.assertContains(
            school_response,
            f"{reverse('dissertations')}?school=Test%20Institute%20of%20Atlantic%20Studies",
        )
