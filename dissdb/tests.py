from django.test import SimpleTestCase

from .models import GeographicEmphasis


class GeographicEmphasisDisplayNameTests(SimpleTestCase):
    def test_removes_imported_numeric_prefix(self):
        emphasis = GeographicEmphasis(name="500 The Americas")

        self.assertEqual(emphasis.display_name, "The Americas")

    def test_preserves_label_without_numeric_prefix(self):
        emphasis = GeographicEmphasis(name="North America")

        self.assertEqual(emphasis.display_name, "North America")
