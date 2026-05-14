"""
Suggest geographic and thematic emphases for dissertations based on title keywords.

Conservative keyword-matching approach — only tags when there's a clear signal.
Uses top-level emphasis categories only to avoid fragile sub-category guesses.

Usage:
    # Dry-run: show suggestions without saving
    python manage.py suggest_emphases

    # Show only dissertations with no emphases
    python manage.py suggest_emphases --untagged

    # Limit output
    python manage.py suggest_emphases --limit 50

    # Actually write to database
    python manage.py suggest_emphases --apply

    # Export suggestions to CSV
    python manage.py suggest_emphases --csv suggestions.csv
"""

import csv
import re
import sys

from django.core.management.base import BaseCommand

from dissdb.models import Dissertation, GeographicEmphasis, ThematicEmphasis


# ---------------------------------------------------------------------------
# Keyword → emphasis ID maps
#
# Each key is a regex pattern (case-insensitive) that, if found in the title,
# suggests the dissertation belongs to that emphasis category. Patterns are
# anchored with word boundaries to avoid false positives (e.g. "Iran" matching
# "hurricane").
#
# Only top-level categories are mapped. Sub-categories (e.g. "China" under
# "Asia") are left for manual review or future AHA data imports.
# ---------------------------------------------------------------------------

# Geographic emphasis name → list of keyword patterns
GEO_KEYWORDS = {
    "100 Asia": [
        r"\bchina\b", r"\bchinese\b", r"\bjapan\b", r"\bjapanese\b",
        r"\bkorea\b", r"\bkorean\b", r"\bindia\b", r"\bindian\b",
        r"\bbengal\b", r"\bmughal\b", r"\bqing\b", r"\bming\b",
        r"\btang\b", r"\bsong dynasty\b", r"\bhan dynasty\b",
        r"\bvietnam\b", r"\bvietnamese\b", r"\bsiam\b", r"\bthai\b",
        r"\bburma\b", r"\bmyanmar\b", r"\bphilippine\b", r"\bfilipino\b",
        r"\bindonesia\b", r"\bjava\b", r"\bmalaya\b", r"\bsingapore\b",
        r"\bcambodia\b", r"\blaos\b", r"\btibet\b", r"\bmongol\b",
        r"\bcentral asia\b", r"\bsilk road\b",
        r"\bsouth asia\b", r"\bsoutheast asia\b", r"\beast asia\b",
        r"\bpakistan\b", r"\bsri lanka\b", r"\bceylon\b",
        r"\bbangladesh\b", r"\bnepal\b", r"\bafghanistan\b",
    ],
    "180 Australasia and Oceania": [
        r"\baustralia\b", r"\baustralian\b", r"\bnew zealand\b",
        r"\bmaori\b", r"\bpacific island\b", r"\bpolynesia\b",
        r"\bmelanesia\b", r"\bmicronesia\b", r"\bsamoa\b",
        r"\bhawai\b", r"\bfiji\b",
    ],
    "200 Middle East (West Asia) and North Africa": [
        r"\bottoman\b", r"\bturk\b", r"\bturkish\b", r"\bturkey\b",
        r"\biran\b", r"\biranian\b", r"\bpersia\b", r"\bpersian\b",
        r"\barab\b", r"\barabic\b", r"\barabian\b",
        r"\bisrael\b", r"\bisraeli\b", r"\bpalestine\b", r"\bpalestinian\b",
        r"\bsyria\b", r"\bsyrian\b", r"\biraq\b", r"\biraqi\b",
        r"\beypt\b", r"\begyptian\b", r"\blevant\b",
        r"\bmaghreb\b", r"\bnorth africa\b",
        r"\bmoroc\b", r"\btunisi\b", r"\balgeri\b", r"\bliby\b",
        r"\bmiddle east\b", r"\bmesopotamia\b",
        r"\bjordan\b", r"\blebanon\b", r"\byemen\b",
        r"\bsafavid\b", r"\bseljuk\b", r"\bmamluk\b",
        r"\bzionist\b", r"\bzionism\b",
    ],
    "220 Africa": [
        r"\bafrica\b", r"\bafrican\b",
        r"\bnigeria\b", r"\bnigerian\b", r"\bghana\b", r"\bghanaian\b",
        r"\bkenya\b", r"\bkenyan\b", r"\btanzania\b",
        r"\bsouth africa\b", r"\bapartheid\b",
        r"\bethiopia\b", r"\bethiopian\b", r"\bsudan\b", r"\bsudanese\b",
        r"\bcongo\b", r"\bcongolese\b", r"\brwanda\b",
        r"\buganda\b", r"\bsenegal\b", r"\bcameroon\b",
        r"\bmozambique\b", r"\bzimbabwe\b", r"\brhodesia\b",
        r"\bsahara\b", r"\bsahel\b",
        r"\bwest africa\b", r"\beast africa\b", r"\bsouthern africa\b",
    ],
    "300 Europe": [
        r"\bbritain\b", r"\bbritish\b", r"\bengland\b", r"\benglish\b",
        r"\bscotland\b", r"\bscottish\b", r"\bwales\b", r"\bwelsh\b",
        r"\bireland\b", r"\birish\b",
        r"\bfrance\b", r"\bfrench\b", r"\bparis\b",
        r"\bgerman\b", r"\bgermany\b", r"\bprussia\b", r"\bprussian\b",
        r"\bweimar\b", r"\bberlin\b", r"\bbavaria\b",
        r"\bitaly\b", r"\bitalian\b", r"\brome\b", r"\broman\b",
        r"\bvenice\b", r"\bflorence\b", r"\bnaples\b",
        r"\bspain\b", r"\bspanish\b", r"\bcastile\b", r"\bcatalan\b",
        r"\bportugal\b", r"\bportuguese\b", r"\biberian\b",
        r"\brussia\b", r"\brussian\b", r"\bsoviet\b", r"\bussr\b",
        r"\bmoscow\b", r"\bbolshevik\b",
        r"\bpoland\b", r"\bpolish\b",
        r"\bnetherlands\b", r"\bdutch\b", r"\bholland\b",
        r"\bbelgi\b", r"\bswiss\b", r"\bswitzerland\b",
        r"\baustria\b", r"\baustrian\b", r"\bhabsburg\b",
        r"\bhungary\b", r"\bhungarian\b",
        r"\bczech\b", r"\bbohemi\b", r"\bslovak\b",
        r"\bscandinavi\b", r"\bswed\b", r"\bnorway\b", r"\bnorwegian\b",
        r"\bdenmark\b", r"\bdanish\b", r"\bfinland\b", r"\bfinnish\b",
        r"\bgreece\b", r"\bgreek\b", r"\bbyzantin\b",
        r"\bbalkan\b", r"\bserbi\b", r"\bcroati\b", r"\bbulgari\b",
        r"\bromani\b", r"\btransylvania\b",
        r"\beurope\b", r"\beuropean\b",
        r"\btudor\b", r"\bvictorian\b", r"\bedwardian\b",
        r"\bmerovingian\b", r"\bcarolingian\b", r"\bmedieval europe\b",
    ],
    "500 The Americas": [
        r"\bamerica\b", r"\bamerican\b", r"\bunited states\b",
        r"\bnew york\b", r"\bnew england\b", r"\bvirginia\b",
        r"\bcalifornia\b", r"\btexas\b", r"\bchicago\b",
        r"\bphiladelphia\b", r"\bboston\b", r"\bwashington\b",
        r"\bmississippi\b", r"\bgeorgia\b", r"\bcarolina\b",
        r"\bappalachia\b", r"\bmidwest\b", r"\bgreat plains\b",
        r"\bcanada\b", r"\bcanadian\b", r"\bquebec\b", r"\bontario\b",
        r"\bmexico\b", r"\bmexican\b", r"\baztec\b",
        r"\bbrazil\b", r"\bbrazilian\b",
        r"\bargentina\b", r"\bargentine\b",
        r"\bchile\b", r"\bchilean\b", r"\bperu\b", r"\bperuvian\b",
        r"\bandean\b", r"\binca\b",
        r"\bcolombia\b", r"\bcolombian\b",
        r"\bcuba\b", r"\bcuban\b", r"\bhaiti\b", r"\bhaitian\b",
        r"\bcaribbean\b", r"\bwest indies\b", r"\bjamaica\b",
        r"\bpuerto rico\b", r"\bguatemala\b", r"\bhonduras\b",
        r"\bnicaragua\b", r"\bel salvador\b", r"\bcosta rica\b",
        r"\bpanama\b", r"\bvenezuela\b", r"\becuador\b",
        r"\bbolivia\b", r"\bparaguay\b", r"\buruguay\b",
        r"\blatin america\b", r"\bcentral america\b",
        r"\bnative american\b", r"\bindigenous\b",
        r"\bcivil war\b", r"\breconstruction\b",
        r"\bcolonial america\b", r"\bantebellum\b",
        r"\bnew deal\b", r"\bcold war\b",
        r"\batlantic\b",
    ],
}

THEMATIC_KEYWORDS = {
    "African American": [r"\bafrican american\b", r"\bblack american\b", r"\bblack freedom\b"],
    "Agrarian/Rural": [r"\bagrarian\b", r"\brural\b", r"\bfarm\b", r"\bagricultur\b", r"\bpeasant\b"],
    "Art/Architecture/Design": [r"\bart\b", r"\barchitectur\b", r"\bdesign\b", r"\bmuseum\b", r"\bpainting\b", r"\bsculptur\b"],
    "Atlantic World": [r"\batlantic world\b", r"\btransatlantic\b", r"\batlantic history\b"],
    "Capitalism": [r"\bcapitalism\b", r"\bcapitalist\b"],
    "Citizenship/National Identity/Nationalism": [r"\bcitizenship\b", r"\bnationalism\b", r"\bnational identity\b", r"\bnation[\s-]building\b"],
    "Cultural": [r"\bcultural history\b", r"\bculture and\b"],
    "Diplomatic/International": [r"\bdiplomatic\b", r"\bdiplomacy\b", r"\binternational relations\b", r"\bforeign policy\b", r"\bforeign relations\b"],
    "Economic/Business": [r"\beconomic\b", r"\btrade\b", r"\bcommerce\b", r"\bmerchant\b", r"\bmarket\b", r"\bbusiness\b", r"\bindustri\b"],
    "Education": [r"\beducation\b", r"\buniversit\b", r"\bschool\b", r"\bteaching\b", r"\bacademic\b"],
    "Empire": [r"\bempire\b", r"\bimperial\b", r"\bcolonial\b", r"\bcolonialism\b", r"\bpostcolonial\b"],
    "Environmental": [r"\benvironmental\b", r"\bclimate\b", r"\bwater\b", r"\briver\b", r"\bforest\b", r"\bconservation\b", r"\bnature\b", r"\blandscape\b"],
    "Family": [r"\bfamily\b", r"\bfamilies\b", r"\bkinship\b", r"\bmarriage\b", r"\bdomestic\b"],
    "Gender": [r"\bgender\b", r"\bmasculinit\b", r"\bfeminism\b", r"\bfeminist\b"],
    "Intellectual": [r"\bintellectual\b", r"\bphilosoph\b", r"\bideas\b", r"\benlightenment\b"],
    "Jewish": [r"\bjewish\b", r"\bjews\b", r"\bjudaism\b", r"\bholocaust\b", r"\banti-semit\b", r"\bantisemit\b"],
    "Labor": [r"\blabor\b", r"\blabour\b", r"\bworker\b", r"\bworking[\s-]class\b", r"\bunion\b", r"\bstrike\b"],
    "Legal": [r"\blegal\b", r"\blaw\b", r"\bjuridical\b", r"\bjustice\b", r"\bcourt\b", r"\bconstitution\b"],
    "LGBTQ": [r"\blgbt\b", r"\bqueer\b", r"\bhomosexual\b", r"\bgay\b", r"\blesbian\b", r"\btransgender\b"],
    "Maritime": [r"\bmaritime\b", r"\bnaval\b", r"\bsailor\b", r"\bseafar\b", r"\bship\b"],
    "Medicine/Disease/Public Health": [r"\bmedicine\b", r"\bmedical\b", r"\bdisease\b", r"\bepidemic\b", r"\bpandemic\b", r"\bpublic health\b", r"\bhospital\b", r"\bplague\b"],
    "Migration/Immigration": [r"\bmigration\b", r"\bimmigra\b", r"\bemigra\b", r"\bdiaspora\b", r"\brefugee\b", r"\bexile\b"],
    "Military": [r"\bmilitary\b", r"\bwar\b", r"\barmy\b", r"\bnavy\b", r"\bsoldier\b", r"\bbattle\b", r"\bwarfare\b"],
    "Music": [r"\bmusic\b", r"\bmusician\b", r"\bcomposer\b", r"\bopera\b", r"\bjazz\b"],
    "Political": [r"\bpolitical\b", r"\bpolitics\b", r"\bdemocra\b", r"\brepublic\b", r"\bstate[\s-]building\b", r"\bgovernance\b"],
    "Race and Ethnicity": [r"\brace\b", r"\bracial\b", r"\bethnicit\b", r"\bethnic\b", r"\bsegregat\b"],
    "Religion": [r"\breligion\b", r"\breligious\b", r"\bchurch\b", r"\bchristian\b", r"\bprotestant\b", r"\bcatholic\b", r"\bmuslim\b", r"\bislam\b", r"\bbuddhis\b", r"\bmissionar\b", r"\btheolog\b"],
    "Science": [r"\bscience\b", r"\bscientific\b", r"\bphysic\b", r"\bchemist\b", r"\bastronom\b", r"\bnatural history\b"],
    "Slavery": [r"\bslaver\b", r"\bslave\b", r"\benslave\b", r"\babolition\b", r"\bplantation\b"],
    "Social Movements": [r"\bsocial movement\b", r"\bprotest\b", r"\bactivis\b", r"\bresistance\b", r"\brevolution\b"],
    "Technology": [r"\btechnolog\b", r"\binvention\b", r"\bindustrial\b", r"\brailroad\b", r"\btelegraph\b"],
    "Urban": [r"\burban\b", r"\bcity\b", r"\bcities\b", r"\bmetropolitan\b"],
    "Women": [r"\bwomen\b", r"\bwoman\b", r"\bfemale\b"],
    "World/Global": [r"\bworld history\b", r"\bglobal\b", r"\btransnational\b"],
}


class Command(BaseCommand):
    help = "Suggest geographic and thematic emphases for dissertations based on title keywords."

    def add_arguments(self, parser):
        parser.add_argument(
            "--untagged",
            action="store_true",
            help="Only process dissertations with no existing emphases",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit number of dissertations to process (0 = all)",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually write suggestions to the database (default is dry-run)",
        )
        parser.add_argument(
            "--csv",
            type=str,
            default="",
            help="Export suggestions to a CSV file",
        )
        parser.add_argument(
            "--min-confidence",
            type=int,
            default=1,
            help="Minimum number of keyword matches to suggest a category (default: 1)",
        )

    def handle(self, *args, **options):
        # Build compiled regex maps
        geo_map = self._build_emphasis_map(GEO_KEYWORDS, GeographicEmphasis)
        thematic_map = self._build_emphasis_map(THEMATIC_KEYWORDS, ThematicEmphasis)

        if not geo_map and not thematic_map:
            self.stderr.write("No emphasis records found in database matching keyword map names.")
            return

        # Query dissertations
        qs = Dissertation.objects.select_related("author", "school")

        if options["untagged"]:
            qs = qs.filter(
                geographic_emphases__isnull=True,
                thematic_emphases__isnull=True,
            ).distinct()

        if options["limit"]:
            qs = qs[: options["limit"]]

        min_conf = options["min_confidence"]
        suggestions = []
        applied_geo = 0
        applied_thematic = 0

        for diss in qs.iterator():
            title = diss.title.lower()

            geo_hits = self._match(title, geo_map, min_conf)
            thematic_hits = self._match(title, thematic_map, min_conf)

            if not geo_hits and not thematic_hits:
                continue

            suggestions.append({
                "id": diss.pk,
                "title": diss.title,
                "year": diss.year,
                "author": diss.author.name_full if diss.author else "",
                "geo_suggestions": [
                    {"name": name, "matches": matches, "count": count}
                    for name, matches, count in geo_hits
                ],
                "thematic_suggestions": [
                    {"name": name, "matches": matches, "count": count}
                    for name, matches, count in thematic_hits
                ],
            })

            if options["apply"]:
                for name, _, _ in geo_hits:
                    emphasis = geo_map[name]["obj"]
                    if not diss.geographic_emphases.filter(pk=emphasis.pk).exists():
                        diss.geographic_emphases.add(emphasis)
                        applied_geo += 1
                for name, _, _ in thematic_hits:
                    emphasis = thematic_map[name]["obj"]
                    if not diss.thematic_emphases.filter(pk=emphasis.pk).exists():
                        diss.thematic_emphases.add(emphasis)
                        applied_thematic += 1

        # Output
        if options["csv"]:
            self._write_csv(suggestions, options["csv"])
            self.stdout.write(f"Wrote {len(suggestions)} suggestions to {options['csv']}")
        else:
            self._print_report(suggestions)

        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write(f"Total dissertations with suggestions: {len(suggestions)}")

        if options["apply"]:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Applied: {applied_geo} geographic, {applied_thematic} thematic"
                )
            )
        else:
            total = sum(
                len(s["geo_suggestions"]) + len(s["thematic_suggestions"])
                for s in suggestions
            )
            self.stdout.write(f"Total suggested tags: {total}")
            self.stdout.write(
                self.style.WARNING("Dry run — use --apply to write to database")
            )

    def _build_emphasis_map(self, keyword_dict, model):
        """Build {name: {obj, patterns}} from keyword dict + DB lookup."""
        result = {}
        for name, patterns in keyword_dict.items():
            try:
                obj = model.objects.get(name=name)
            except model.DoesNotExist:
                continue
            compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
            result[name] = {"obj": obj, "patterns": compiled}
        return result

    def _match(self, title, emphasis_map, min_confidence):
        """Return list of (name, matched_keywords, count) for a title."""
        hits = []
        for name, data in emphasis_map.items():
            matched = []
            for pattern in data["patterns"]:
                if pattern.search(title):
                    matched.append(pattern.pattern)
            if len(matched) >= min_confidence:
                hits.append((name, matched, len(matched)))
        # Sort by number of matches (most confident first)
        hits.sort(key=lambda x: -x[2])
        return hits

    def _print_report(self, suggestions):
        for s in suggestions[:100]:  # Cap console output
            self.stdout.write(f"\n[{s['id']}] {s['title'][:80]}")
            self.stdout.write(f"       {s['year']} — {s['author']}")
            for g in s["geo_suggestions"]:
                kw = ", ".join(g["matches"][:3])
                self.stdout.write(
                    self.style.SUCCESS(f"   GEO: {g['name']} ({g['count']} match: {kw})")
                )
            for t in s["thematic_suggestions"]:
                kw = ", ".join(t["matches"][:3])
                self.stdout.write(
                    self.style.HTTP_INFO(f"   THE: {t['name']} ({t['count']} match: {kw})")
                )

    def _write_csv(self, suggestions, filepath):
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "diss_id", "title", "year", "author",
                "geo_suggestion", "geo_keywords", "geo_matches",
                "thematic_suggestion", "thematic_keywords", "thematic_matches",
            ])
            for s in suggestions:
                geo_names = "; ".join(g["name"] for g in s["geo_suggestions"])
                geo_kw = "; ".join(
                    ", ".join(g["matches"][:3]) for g in s["geo_suggestions"]
                )
                geo_counts = "; ".join(str(g["count"]) for g in s["geo_suggestions"])
                the_names = "; ".join(t["name"] for t in s["thematic_suggestions"])
                the_kw = "; ".join(
                    ", ".join(t["matches"][:3]) for t in s["thematic_suggestions"]
                )
                the_counts = "; ".join(
                    str(t["count"]) for t in s["thematic_suggestions"]
                )
                writer.writerow([
                    s["id"], s["title"], s["year"], s["author"],
                    geo_names, geo_kw, geo_counts,
                    the_names, the_kw, the_counts,
                ])
