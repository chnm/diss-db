from django.core.cache import cache
from django.db import connection
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from dissdb.models import (
    CommitteeMember,
    Dissertation,
    GeographicEmphasis,
    Scholar,
    School,
    Source,
)

# The test DB is pre-populated by the seed data migrations (0002/0004/0006/0008),
# which bulk_create rows with explicit ids without advancing the pk sequences.
# Reset the sequences before we create fixtures, then isolate assertions to our
# own rows (a fresh school / unique names) rather than global counts.
_SEEDED_TABLES = [
    "dissdb_source",
    "dissdb_school",
    "dissdb_scholar",
    "dissdb_dissertation",
    "dissdb_committeemember",
    "dissdb_geographicemphasis",
    "dissdb_thematicemphasis",
]


def _reset_sequences():
    with connection.cursor() as cur:
        for table in _SEEDED_TABLES:
            cur.execute(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {table}), 1))"
            )


class ApiV1TestCase(APITestCase):
    ADVISOR_ORCID = "0000-0002-1825-0097"

    @classmethod
    def setUpTestData(cls):
        _reset_sequences()
        cls.source = Source.objects.create(name="Test Source", source_type="other")
        cls.school = School.objects.create(
            name="Test University", aha_school_id=999999, source=cls.source
        )
        cls.geo = GeographicEmphasis.objects.create(
            name="North America", slug="north-america", aha_id=500, source=cls.source
        )

        cls.author = Scholar.objects.create(
            name_first="Ada", name_last="Author", source=cls.source
        )
        cls.advisor = Scholar.objects.create(
            name_first="Vic", name_last="Advisor", orcid=cls.ADVISOR_ORCID,
            source=cls.source,
        )
        cls.reader = Scholar.objects.create(
            name_first="Rey", name_last="Reader", source=cls.source
        )

        cls.diss = Dissertation.objects.create(
            title="A Study of Something Zzyzx-Particular",
            year=2018,
            author=cls.author,
            school=cls.school,
            source=cls.source,
        )
        cls.diss.geographic_emphases.add(cls.geo)

        cls.older = Dissertation.objects.create(
            title="An Earlier Zzyzx Work",
            year=1995,
            author=cls.reader,
            school=cls.school,
            source=cls.source,
        )

        CommitteeMember.objects.create(
            scholar=cls.advisor, dissertation=cls.diss,
            role=CommitteeMember.CHAIR, source=cls.source,
        )
        CommitteeMember.objects.create(
            scholar=cls.reader, dissertation=cls.diss,
            role=CommitteeMember.READER, source=cls.source,
        )

    def setUp(self):
        cache.clear()  # keep the scoped rate throttle from bleeding across tests

    # ── Dissertations ────────────────────────────────────────────────

    def test_dissertation_list_paginated_shape(self):
        resp = self.client.get(reverse("apiv1:dissertation-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for key in ("count", "next", "previous", "results"):
            self.assertIn(key, resp.data)
        self.assertGreaterEqual(resp.data["count"], 2)

    def test_dissertation_list_item_fields(self):
        resp = self.client.get(
            reverse("apiv1:dissertation-list"), {"school": self.school.id}
        )
        item = next(r for r in resp.data["results"] if r["id"] == self.diss.id)
        self.assertEqual(item["author"]["name_full"], "Ada Author")
        self.assertEqual(item["advisor"]["name_full"], "Vic Advisor")
        self.assertEqual(item["school"]["name"], "Test University")
        self.assertIn("api_url", item)
        self.assertIn("site_url", item)

    def test_dissertation_detail_committee_chair_first(self):
        url = reverse("apiv1:dissertation-detail", kwargs={"pk": self.diss.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["committee"][0]["role"], "chair")
        roles = {m["role"] for m in resp.data["committee"]}
        self.assertEqual(roles, {"chair", "reader"})
        self.assertEqual(resp.data["geographic_emphases"][0]["slug"], "north-america")
        self.assertIn("abstract", resp.data)

    def test_dissertation_filter_year_range(self):
        resp = self.client.get(
            reverse("apiv1:dissertation-list"),
            {"school": self.school.id, "year_min": 2000, "year_max": 2020},
        )
        ids = [r["id"] for r in resp.data["results"]]
        self.assertIn(self.diss.id, ids)
        self.assertNotIn(self.older.id, ids)

    def test_dissertation_filter_by_advisor(self):
        resp = self.client.get(
            reverse("apiv1:dissertation-list"), {"advisor": self.advisor.id}
        )
        ids = [r["id"] for r in resp.data["results"]]
        self.assertEqual(ids, [self.diss.id])

    def test_dissertation_filter_title_search(self):
        resp = self.client.get(
            reverse("apiv1:dissertation-list"),
            {"school": self.school.id, "q": "Zzyzx-Particular"},
        )
        ids = [r["id"] for r in resp.data["results"]]
        self.assertEqual(ids, [self.diss.id])

    def test_page_size_respected(self):
        resp = self.client.get(reverse("apiv1:dissertation-list"), {"page_size": 1})
        self.assertEqual(len(resp.data["results"]), 1)
        self.assertGreaterEqual(resp.data["count"], 2)
        self.assertIsNotNone(resp.data["next"])

    # ── Scholars ─────────────────────────────────────────────────────

    def test_scholar_list_counts_isolated_by_orcid(self):
        resp = self.client.get(
            reverse("apiv1:scholar-list"), {"orcid": self.ADVISOR_ORCID}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 1)
        row = resp.data["results"][0]
        self.assertEqual(row["id"], self.advisor.id)
        self.assertEqual(row["advised_count"], 1)
        self.assertEqual(row["dissertation_count"], 0)

    def test_scholar_detail_authored_and_advised(self):
        advisor_url = reverse("apiv1:scholar-detail", kwargs={"pk": self.advisor.pk})
        resp = self.client.get(advisor_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        advised_ids = [d["id"] for d in resp.data["dissertations_advised"]]
        self.assertEqual(advised_ids, [self.diss.id])
        self.assertEqual(resp.data["dissertations_authored"], [])
        self.assertEqual(
            resp.data["orcid_url"], f"https://orcid.org/{self.ADVISOR_ORCID}"
        )

        author_url = reverse("apiv1:scholar-detail", kwargs={"pk": self.author.pk})
        authored = self.client.get(author_url).data["dissertations_authored"]
        self.assertEqual([d["id"] for d in authored], [self.diss.id])

    def test_has_orcid_false_excludes_scholar_with_orcid(self):
        resp = self.client.get(
            reverse("apiv1:scholar-list"),
            {"orcid": self.ADVISOR_ORCID, "has_orcid": "false"},
        )
        self.assertEqual(resp.data["results"], [])

    # ── Contract ─────────────────────────────────────────────────────

    def test_read_only_rejects_post(self):
        resp = self.client.post(reverse("apiv1:dissertation-list"), {"title": "x"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
