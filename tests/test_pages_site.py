from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from unittest import mock

from scripts import build_pages_site as pages


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "pages.yml"
OWNER = "example-owner"
REPO = "academy-repo"
REF = "0123456789abcdef0123456789abcdef01234567"


def write_text(root: Path, relative: str, value: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return path


def write_bytes(root: Path, relative: str, value: bytes) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)
    return path


def create_fixture(root: Path) -> None:
    write_text(root, ".nojekyll", "static\n")
    write_text(
        root,
        "index.html",
        '<a href="academy.html">Academy</a>'
        '<a href="docs/">Docs</a>'
        '<a href="beta/">Beta</a>',
    )
    write_text(
        root,
        "academy.html",
        '<a href="index.html#home">Home</a>'
        '<a href="https://example.com/course.zip">External</a>'
        '<a href="mailto:academy@example.com">Mail</a>'
        '<a href="javascript:void(0)">Script</a>'
        '<a href="#catalog">Catalog</a>'
        '<img src="data:image/gif;base64,R0lGODlhAQABAIAAAAUEBA==">',
    )
    write_text(root, "docs/index.html", '<a href="../tools/demo.html">Tool</a>')
    write_text(root, "tools/demo.html", "<h1>Repository tool</h1>")
    write_text(root, "agents/template.py", "print('template')\n")
    write_text(root, "reports/report.html", '<a href="../index.html">Home</a>')
    write_text(root, "state/metrics.json", "{}\n")
    write_text(root, "academy/catalog.json", '{"schema":"fixture"}\n')
    write_text(root, "skills/easy/SKILL.md", "# Easy\n")
    write_text(
        root,
        "beta/index.html",
        '<a href="../index.html">Home</a><img src="build/icon.svg">',
    )
    write_text(root, "beta/build/icon.svg", "<svg></svg>\n")

    courses = []
    for index in range(pages.EXPECTED_ACADEMY_COURSES):
        slug = f"course-{index + 1:02d}"
        base = f"solutions/{slug}"
        skill = f"{base}/manual/skills/main/SKILL.md"
        quest_links = (
            '<a href="field-guide.html?mode=easy#start">Field guide</a>'
            '<a href="manual-tutorial.html">Manual</a>'
            '<a href="evidence-report.html">Evidence</a>'
            '<a href="manual/skills/main/SKILL.md">Skill</a>'
        )
        if index == 0:
            quest_links += (
                f'<a href="exports/{slug}-source.zip?download=1#bundle">'
                "Source bundle</a>"
                "<img src=screenshots/walkthrough.gif?autoplay=1#frame>"
                '<a href="../../agents/template.py">Agent template</a>'
                '<a href="../../skills/easy/SKILL.md">Easy skill</a>'
            )
            write_bytes(root, f"{base}/exports/{slug}-source.zip", b"zip-fixture")
            write_bytes(
                root,
                f"{base}/screenshots/walkthrough.gif",
                b"GIF89a-fixture",
            )
        write_text(root, f"{base}/quest.html", quest_links)
        write_text(
            root,
            f"{base}/field-guide.html",
            '<a href="quest.html">Quest</a>',
        )
        write_text(
            root,
            f"{base}/manual-tutorial.html",
            '<a href="quest.html">Quest</a>',
        )
        write_text(
            root,
            f"{base}/evidence-report.html",
            '<a href="quest.html">Quest</a>',
        )
        write_text(root, skill, f"# {slug} skill\n")
        courses.append(
            {
                "slug": slug,
                "quest_url": f"{base}/quest.html",
                "field_guide_url": f"{base}/field-guide.html",
                "manual_url": f"{base}/manual-tutorial.html",
                "evidence_url": f"{base}/evidence-report.html",
                "skills": [{"name": f"{slug}-main", "path": skill}],
            }
        )

    academy = {
        "schema": "fixture-academy/1.0",
        "summary": {
            "courses": len(courses),
            "skills": sum(len(course["skills"]) for course in courses),
        },
        "courses": courses,
    }
    write_text(root, "academy.json", json.dumps(academy, indent=2) + "\n")


@contextmanager
def fixture_root():
    with tempfile.TemporaryDirectory(prefix=".pages-fixture-", dir=ROOT) as directory:
        root = Path(directory) / "repo"
        root.mkdir()
        create_fixture(root)
        yield root


def build_fixture(root: Path) -> tuple[Path, dict[str, object]]:
    output = root / "_site"
    manifest = pages.build_site(root, output, OWNER, REPO, REF)
    return output, manifest


class PagesBuilderFixtureTests(unittest.TestCase):
    def test_community_manifest_is_served_for_catalog_rendering_and_export(self):
        with fixture_root() as root:
            document = '{"schema":"aibast-community-tools/1.0","tools":[],"count":0}\n'
            write_text(root, "community_tools.json", document)
            output, _manifest = build_fixture(root)
            self.assertEqual(
                (output / "community_tools.json").read_text(encoding="utf-8"),
                document,
            )

    def test_rewrites_zip_gif_and_repository_only_links(self):
        with fixture_root() as root:
            output, manifest = build_fixture(root)
            quest = (
                output / "solutions" / "course-01" / "quest.html"
            ).read_text(encoding="utf-8")
            docs = (output / "docs" / "index.html").read_text(encoding="utf-8")

            raw = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{REF}"
            self.assertIn(
                f"{raw}/solutions/course-01/exports/"
                "course-01-source.zip?download=1#bundle",
                quest,
            )
            self.assertIn(
                f"src={raw}/solutions/course-01/screenshots/"
                "walkthrough.gif?autoplay=1#frame",
                quest,
            )
            self.assertIn(f"{raw}/agents/template.py", quest)
            self.assertIn(f"{raw}/tools/demo.html", docs)
            self.assertEqual(manifest["rewritten_link_count"], 4)

    def test_preserves_safe_and_external_links(self):
        with fixture_root() as root:
            output, _manifest = build_fixture(root)
            quest = (
                output / "solutions" / "course-01" / "quest.html"
            ).read_text(encoding="utf-8")
            academy = (output / "academy.html").read_text(encoding="utf-8")

            self.assertIn('href="field-guide.html?mode=easy#start"', quest)
            self.assertIn('href="https://example.com/course.zip"', academy)
            self.assertIn('href="mailto:academy@example.com"', academy)
            self.assertIn('href="javascript:void(0)"', academy)
            self.assertIn('href="#catalog"', academy)
            self.assertIn('src="data:image/gif;base64,', academy)

    def test_manifest_reports_actual_counts_and_bytes(self):
        with fixture_root() as root:
            output, manifest = build_fixture(root)
            files = [path for path in output.rglob("*") if path.is_file()]
            total_bytes = sum(path.stat().st_size for path in files)

            self.assertEqual(manifest["schema"], pages.MANIFEST_SCHEMA)
            self.assertEqual(manifest["file_count"], len(files))
            self.assertEqual(manifest["total_bytes"], total_bytes)
            self.assertEqual(
                manifest["source"],
                {"owner": OWNER, "repo": REPO, "ref": REF},
            )
            self.assertEqual(
                manifest["excluded"][".zip"],
                {"count": 1, "bytes": len(b"zip-fixture")},
            )
            self.assertEqual(
                manifest["excluded"][".gif"],
                {"count": 1, "bytes": len(b"GIF89a-fixture")},
            )

    def test_rebuild_is_deterministic_and_cleans_only_output(self):
        with fixture_root() as root:
            output, _manifest = build_fixture(root)
            first_manifest = (output / pages.MANIFEST_NAME).read_bytes()
            first_quest = (
                output / "solutions" / "course-01" / "quest.html"
            ).read_bytes()
            write_text(output, "stale.txt", "stale\n")
            sibling = write_text(root, "_site-neighbor/keep.txt", "keep\n")

            pages.build_site(root, output, OWNER, REPO, REF)

            self.assertFalse((output / "stale.txt").exists())
            self.assertEqual(sibling.read_text(encoding="utf-8"), "keep\n")
            self.assertEqual(
                (output / pages.MANIFEST_NAME).read_bytes(), first_manifest
            )
            self.assertEqual(
                (output / "solutions" / "course-01" / "quest.html").read_bytes(),
                first_quest,
            )

    def test_git_inventory_handles_sparse_missing_excluded_blobs(self):
        with fixture_root() as root:
            commands = (
                ["git", "init", "--quiet"],
                ["git", "config", "user.name", "Pages Test"],
                ["git", "config", "user.email", "pages-test@example.invalid"],
                ["git", "add", "."],
                ["git", "commit", "--quiet", "-m", "fixture"],
            )
            for command in commands:
                subprocess.run(command, cwd=root, check=True)
            git_entries = pages.collect_git_entries(root)
            zip_path = PurePosixPath(
                "solutions/course-01/exports/course-01-source.zip"
            )
            gif_path = PurePosixPath(
                "solutions/course-01/screenshots/walkthrough.gif"
            )
            self.assertIsNone(git_entries[zip_path].size)
            remote_metadata = {
                zip_path: (
                    git_entries[zip_path].object_id,
                    len(b"zip-fixture"),
                ),
                gif_path: (
                    git_entries[gif_path].object_id,
                    len(b"GIF89a-fixture"),
                ),
            }
            for relative in (
                "solutions/course-01/exports/course-01-source.zip",
                "solutions/course-01/screenshots/walkthrough.gif",
                "agents/template.py",
                "tools/demo.html",
            ):
                (root / relative).unlink()

            with (
                mock.patch.object(
                    pages, "repository_uses_promisor_remote", return_value=True
                ),
                mock.patch.object(
                    pages,
                    "fetch_github_tree_metadata",
                    return_value=remote_metadata,
                ) as fetch_metadata,
            ):
                output, manifest = build_fixture(root)

            fetch_metadata.assert_called_once_with(OWNER, REPO, REF)
            self.assertEqual(manifest["excluded"][".zip"]["count"], 1)
            self.assertEqual(manifest["excluded"][".gif"]["count"], 1)
            self.assertEqual(manifest["rewritten_link_count"], 4)
            self.assertFalse(
                (output / "solutions/course-01/exports/course-01-source.zip").exists()
            )

    def test_output_outside_root_is_refused(self):
        with fixture_root() as root:
            with self.assertRaisesRegex(pages.BuildError, "inside repository root"):
                pages.build_site(
                    root,
                    root.parent / "escaped-site",
                    OWNER,
                    REPO,
                    REF,
                )

    def test_output_root_and_source_overlap_are_refused(self):
        with fixture_root() as root:
            with self.assertRaisesRegex(pages.BuildError, "repository root"):
                pages.build_site(root, root, OWNER, REPO, REF)
            with self.assertRaisesRegex(pages.BuildError, "protected source"):
                pages.build_site(root, root / "solutions", OWNER, REPO, REF)

    def test_output_symlink_is_refused(self):
        with fixture_root() as root:
            target = root / "_site-target"
            target.mkdir()
            link = root / "_site-link"
            try:
                link.symlink_to(target, target_is_directory=True)
            except (NotImplementedError, OSError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            with self.assertRaisesRegex(pages.BuildError, "symlink"):
                pages.build_site(root, link, OWNER, REPO, REF)

    def test_source_symlink_is_refused(self):
        with fixture_root() as root:
            skill = (
                root
                / "solutions"
                / "course-01"
                / "manual"
                / "skills"
                / "main"
                / "SKILL.md"
            )
            target = root / "skill-target.md"
            target.write_text("# target\n", encoding="utf-8")
            skill.unlink()
            try:
                skill.symlink_to(target)
            except (NotImplementedError, OSError) as exc:
                self.skipTest(f"symlinks unavailable: {exc}")
            with self.assertRaisesRegex(pages.BuildError, "symlink source"):
                pages.build_site(root, root / "_site", OWNER, REPO, REF)

    def test_path_traversal_link_is_refused(self):
        with fixture_root() as root:
            write_text(root, "academy.html", '<a href="../outside.html">Escape</a>')
            with self.assertRaisesRegex(pages.BuildError, "escapes the artifact"):
                pages.build_site(root, root / "_site", OWNER, REPO, REF)

    def test_oversized_included_file_is_refused(self):
        with fixture_root() as root:
            oversized = root / "state" / "oversized.json"
            with oversized.open("wb") as stream:
                stream.truncate(pages.FILE_BYTE_LIMIT + 1)
            with self.assertRaisesRegex(pages.BuildError, "exceeds"):
                pages.build_site(root, root / "_site", OWNER, REPO, REF)

    def test_no_check_links_flag_is_available(self):
        arguments = pages.parse_args(
            [
                "--owner",
                OWNER,
                "--repo",
                REPO,
                "--ref",
                REF,
                "--no-check-links",
            ]
        )
        self.assertFalse(arguments.check_links)

    def test_mutation_removing_academy_file_fails(self):
        with fixture_root() as root:
            (root / "solutions" / "course-01" / "quest.html").unlink()
            with self.assertRaisesRegex(pages.BuildError, "Academy page is missing"):
                pages.build_site(root, root / "_site", OWNER, REPO, REF)

    def test_mutation_disabling_rewrite_fails(self):
        with fixture_root() as root:
            with mock.patch.object(pages, "_can_rewrite", return_value=False):
                with self.assertRaisesRegex(
                    pages.BuildError, "Broken or unclassified Pages links"
                ):
                    pages.build_site(root, root / "_site", OWNER, REPO, REF)

    def test_mutation_including_zip_fails(self):
        with fixture_root() as root:
            output, _manifest = build_fixture(root)
            write_bytes(
                output,
                "solutions/course-01/exports/injected.zip",
                b"injected",
            )
            with self.assertRaisesRegex(pages.BuildError, "blob included"):
                pages.validate_artifact(output)

    def test_mutation_creating_broken_link_fails(self):
        with fixture_root() as root:
            write_text(
                root,
                "academy.html",
                '<a href="missing/learner-asset.png?x=1#proof">Missing</a>',
            )
            with self.assertRaisesRegex(
                pages.BuildError, "missing/learner-asset.png"
            ):
                pages.build_site(root, root / "_site", OWNER, REPO, REF)


INSTALLER_SH = (
    "#!/bin/bash\n"
    "# Usage: curl -fsSL https://microsoft.github.io/aibast-agents-library/install.sh | bash\n"
    'REPO_URL="${BRAINSTEM_REPO_URL:-https://github.com/microsoft/aibast-agents-library.git}"\n'
    'REPO_REF="${BRAINSTEM_REPO_REF:-main}"\n'
    'REMOTE_VERSION_URL="${BRAINSTEM_VERSION_URL:-https://raw.githubusercontent.com/'
    'microsoft/aibast-agents-library/main/rapp_brainstem/VERSION}"\n'
)
INSTALLER_PS1 = (
    "\ufeff# Usage: irm https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.ps1 | iex\r\n"
    '$REPO_URL = if ($env:BRAINSTEM_REPO_URL) { $env:BRAINSTEM_REPO_URL } else { "https://github.com/microsoft/aibast-agents-library.git" }\r\n'
    '$REPO_REF = if ($env:BRAINSTEM_REPO_REF) { $env:BRAINSTEM_REPO_REF } else { "main" }\r\n'
    '$REMOTE_VERSION_URL = if ($env:BRAINSTEM_VERSION_URL) { $env:BRAINSTEM_VERSION_URL } else { "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/rapp_brainstem/VERSION" }\r\n'
)
INSTALLER_CMD = (
    '@echo off\r\n'
    'powershell -ExecutionPolicy Bypass -Command "& { irm https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/install.ps1 | iex }"\r\n'
)


def write_installers(root: Path) -> None:
    for prefix in ("", "docs/"):
        write_text(root, f"{prefix}install.sh", INSTALLER_SH)
        write_bytes(root, f"{prefix}install.ps1", INSTALLER_PS1.encode("utf-8"))
        write_bytes(root, f"{prefix}install.cmd", INSTALLER_CMD.encode("utf-8"))


LANE_SKILL = (
    "---\nname: lane\n---\n\n## Public source\n\n"
    "- Repository: `microsoft/aibast-agents-library`\n"
    "- Workshop branch: `main`\n- Registry path: `registry.json`\n"
)


def write_lane_skills(root: Path) -> None:
    for name in ("aibast-easy-mode-brainstem", "aibast-easy-mode-copilot"):
        write_text(root, f"skills/{name}/SKILL.md", LANE_SKILL)


class RingLaneSkillRenderTests(unittest.TestCase):
    """The served lane skills must pull workshops from the ring that serves them."""

    def test_production_identity_leaves_lane_skills_byte_identical(self):
        with fixture_root() as root:
            write_installers(root)
            write_lane_skills(root)
            output = root / "_site"
            manifest = pages.build_site(
                root, output, pages.CANONICAL_OWNER, pages.CANONICAL_REPO, REF,
                ring_branch=pages.CANONICAL_BRANCH,
            )
            self.assertEqual(manifest["ring"]["rendered_installers"], [])
            for name in sorted(pages.RING_SKILL_PATHS):
                self.assertEqual((output / name).read_bytes(), (root / name).read_bytes())

    def test_staging_ring_renders_lane_skills_to_the_fork(self):
        with fixture_root() as root:
            write_installers(root)
            write_lane_skills(root)
            output = root / "_site"
            manifest = pages.build_site(
                root, output, "staging-owner", "staging-repo", REF, ring_branch="staging"
            )
            for name in pages.RING_SKILL_PATHS:
                self.assertIn(name, manifest["ring"]["rendered_installers"])
                rendered = (output / name).read_text(encoding="utf-8")
                self.assertIn("- Repository: `staging-owner/staging-repo`", rendered)
                self.assertIn("- Workshop branch: `staging`", rendered)
                self.assertNotIn("microsoft/aibast-agents-library", rendered)
                self.assertIn("- Registry path: `registry.json`", rendered)

    def test_lane_skill_that_drops_its_source_lines_fails_the_ring_build(self):
        with fixture_root() as root:
            write_installers(root)
            write_lane_skills(root)
            write_text(root, "skills/aibast-easy-mode-copilot/SKILL.md", "---\nname: lane\n---\n")
            with self.assertRaises(pages.BuildError):
                pages.build_site(
                    root, root / "_site", "staging-owner", "staging-repo", REF, ring_branch="staging"
                )


class RingInstallerRenderTests(unittest.TestCase):
    """The published one-liner must install the ring that serves it."""

    def test_production_identity_leaves_installers_byte_identical(self):
        with fixture_root() as root:
            write_installers(root)
            output = root / "_site"
            manifest = pages.build_site(
                root, output, pages.CANONICAL_OWNER, pages.CANONICAL_REPO, REF,
                ring_branch=pages.CANONICAL_BRANCH,
            )
            self.assertEqual(manifest["ring"], {"branch": "main", "rendered_installers": []})
            for name in ("install.sh", "install.ps1", "install.cmd", "docs/install.sh"):
                self.assertEqual((output / name).read_bytes(), (root / name).read_bytes())

    def test_staging_ring_renders_every_installer_to_the_fork(self):
        with fixture_root() as root:
            write_installers(root)
            output = root / "_site"
            manifest = pages.build_site(
                root, output, "staging-owner", "staging-repo", REF, ring_branch="staging"
            )
            self.assertEqual(manifest["ring"]["branch"], "staging")
            self.assertEqual(
                manifest["ring"]["rendered_installers"],
                ["docs/install.cmd", "docs/install.ps1", "docs/install.sh",
                 "install.cmd", "install.ps1", "install.sh"],
            )
            sh = (output / "install.sh").read_text(encoding="utf-8")
            self.assertIn('REPO_URL="${BRAINSTEM_REPO_URL:-https://github.com/staging-owner/staging-repo.git}"', sh)
            self.assertIn('REPO_REF="${BRAINSTEM_REPO_REF:-staging}"', sh)
            self.assertIn("https://raw.githubusercontent.com/staging-owner/staging-repo/staging/rapp_brainstem/VERSION", sh)
            self.assertIn("https://staging-owner.github.io/staging-repo/install.sh", sh)
            self.assertNotIn("microsoft/aibast-agents-library", sh)
            ps1 = (output / "install.ps1").read_bytes()
            self.assertTrue(ps1.startswith("\ufeff".encode("utf-8")), "BOM must survive rendering")
            self.assertIn(b'else { "https://github.com/staging-owner/staging-repo.git" }', ps1)
            self.assertIn(b'else { "staging" }', ps1)
            self.assertIn(b"\r\n", ps1, "CRLF must survive rendering")
            cmd = (output / "install.cmd").read_text(encoding="utf-8")
            self.assertIn("https://raw.githubusercontent.com/staging-owner/staging-repo/staging/install.ps1", cmd)
            self.assertEqual((output / "docs/install.sh").read_bytes(), (output / "install.sh").read_bytes())
            # Source files are never touched.
            self.assertEqual((root / "install.sh").read_text(encoding="utf-8"), INSTALLER_SH)

    def test_installer_refactor_that_drops_the_default_fails_the_build(self):
        with fixture_root() as root:
            write_installers(root)
            write_text(root, "install.sh", INSTALLER_SH.replace('REPO_REF="${BRAINSTEM_REPO_REF:-main}"', 'REPO_REF=main'))
            with self.assertRaisesRegex(pages.BuildError, "install.sh no longer contains"):
                pages.build_site(root, root / "_site", "staging-owner", "staging-repo", REF, ring_branch="staging")

    def test_invalid_ring_branch_is_refused(self):
        with fixture_root() as root:
            write_installers(root)
            with self.assertRaisesRegex(pages.BuildError, "Invalid GitHub branch"):
                pages.build_site(root, root / "_site", "staging-owner", "staging-repo", REF, ring_branch="../evil")


class FullRepositoryArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configured = os.environ.get("PAGES_SITE_DIR")
        cls._temporary_directory = None
        if configured:
            cls.site = Path(configured).resolve()
        else:
            cls._temporary_directory = tempfile.TemporaryDirectory(
                prefix=".pages-full-", dir=ROOT
            )
            cls.site = Path(cls._temporary_directory.name) / "_site"
            pages.build_site(ROOT, cls.site, OWNER, REPO, REF)
        cls.manifest = pages.validate_artifact(cls.site)

    @classmethod
    def tearDownClass(cls):
        if cls._temporary_directory is not None:
            cls._temporary_directory.cleanup()

    def test_artifact_size_exclusions_and_required_entry_points(self):
        files = [path for path in self.site.rglob("*") if path.is_file()]
        total_bytes = sum(path.stat().st_size for path in files)
        largest = max(path.stat().st_size for path in files)

        self.assertLess(total_bytes, pages.ARTIFACT_BYTE_LIMIT)
        self.assertLessEqual(largest, pages.FILE_BYTE_LIMIT)
        self.assertEqual(self.manifest["file_count"], len(files))
        self.assertEqual(self.manifest["total_bytes"], total_bytes)
        self.assertGreater(self.manifest["excluded"][".zip"]["count"], 0)
        self.assertGreater(self.manifest["excluded"][".zip"]["bytes"], 0)
        self.assertGreater(self.manifest["excluded"][".gif"]["count"], 0)
        self.assertGreater(self.manifest["excluded"][".gif"]["bytes"], 0)
        for relative in (
            ".nojekyll",
            "index.html",
            "academy.html",
            "academy.json",
            "beta/index.html",
            "rapp_brainstem/README.md",
            "rapp_brainstem/VERSION",
        ):
            self.assertTrue((self.site / relative).is_file(), relative)

    def test_artifact_has_all_academy_pages_and_skills(self):
        academy = json.loads((self.site / "academy.json").read_text(encoding="utf-8"))
        self.assertEqual(
            len(academy["courses"]), pages.EXPECTED_ACADEMY_COURSES
        )
        for field, filename in pages.ACADEMY_PAGE_FIELDS.items():
            paths = {course[field] for course in academy["courses"]}
            self.assertEqual(len(paths), pages.EXPECTED_ACADEMY_COURSES)
            self.assertTrue(all(Path(path).name == filename for path in paths))
            self.assertTrue(all((self.site / path).is_file() for path in paths))
        skills = [
            skill["path"]
            for course in academy["courses"]
            for skill in course["skills"]
        ]
        self.assertEqual(len(skills), academy["summary"]["skills"])
        self.assertEqual(len(set(skills)), len(skills))
        self.assertTrue(all((self.site / path).is_file() for path in skills))

    def test_artifact_contains_no_forbidden_tree_or_solution_blob(self):
        relative_files = [
            path.relative_to(self.site).as_posix()
            for path in self.site.rglob("*")
            if path.is_file()
        ]
        forbidden_top_levels = {
            ".git",
            ".github",
            "agents",
            "browser-audit",
            "tests",
            "tools",
        }
        self.assertFalse(
            any(path.split("/", 1)[0] in forbidden_top_levels for path in relative_files)
        )
        self.assertFalse(
            any(
                path.startswith("solutions/")
                and Path(path).suffix.lower() in pages.FORBIDDEN_PAGES_SUFFIXES
                for path in relative_files
            )
        )
        self.assertFalse(any("/node_modules/" in f"/{path}/" for path in relative_files))
        self.assertFalse(any(path.startswith("beta/electron/") for path in relative_files))
        self.assertFalse(any(path.startswith("beta/tests/") for path in relative_files))

    def test_complete_artifact_has_no_broken_relative_links(self):
        self.assertEqual(pages.validate_html_links(self.site), [])

    def test_served_installers_match_the_manifest_ring(self):
        manifest = json.loads((self.site / pages.MANIFEST_NAME).read_text(encoding="utf-8"))
        ring = manifest["ring"]
        owner, repo = manifest["source"]["owner"], manifest["source"]["repo"]
        sh = (self.site / "install.sh").read_text(encoding="utf-8")
        self.assertIn(f'REPO_URL="${{BRAINSTEM_REPO_URL:-https://github.com/{owner}/{repo}.git}}"', sh)
        self.assertIn(f'REPO_REF="${{BRAINSTEM_REPO_REF:-{ring["branch"]}}}"', sh)
        self.assertEqual((self.site / "docs/install.sh").read_bytes(), (self.site / "install.sh").read_bytes())
        if (owner, repo, ring["branch"]) == (pages.CANONICAL_OWNER, pages.CANONICAL_REPO, pages.CANONICAL_BRANCH):
            self.assertEqual(ring["rendered_installers"], [])
        else:
            self.assertIn("install.sh", ring["rendered_installers"])

    def test_library_dynamic_solution_download_uses_immutable_raw_url(self):
        library = (self.site / "index.html").read_text(encoding="utf-8")
        source = self.manifest["source"]
        raw = (
            "https://raw.githubusercontent.com/"
            f"{source['owner']}/{source['repo']}/{source['ref']}"
        )
        self.assertNotIn(pages.LIBRARY_DYNAMIC_ZIP_SOURCE, library)
        self.assertIn(
            f"zip: `{raw}/${{base}}-copilot-studio-solution.zip`",
            library,
        )


class PagesWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_trigger_and_repository_ref_guard(self):
        self.assertRegex(self.text, r"(?m)^\s+- staging$")
        self.assertRegex(self.text, r"(?m)^\s+- main$")
        self.assertIn("workflow_dispatch:", self.text)
        self.assertRegex(
            self.text,
            r"kody-w/aibast-agents-library' &&\s+"
            r"github\.ref == 'refs/heads/staging'",
        )
        self.assertRegex(
            self.text,
            r"microsoft/aibast-agents-library' &&\s+"
            r"github\.ref == 'refs/heads/main'",
        )
        self.assertNotRegex(
            self.text,
            r"kody-w/aibast-agents-library' &&\s+"
            r"github\.ref == 'refs/heads/main'",
        )

    def test_permissions_and_concurrency(self):
        for permission in ("contents: read", "pages: write", "id-token: write"):
            self.assertIn(permission, self.text)
        self.assertRegex(self.text, r"(?m)^\s+group: pages$")
        self.assertRegex(self.text, r"(?m)^\s+cancel-in-progress: true$")

    def test_sparse_checkout_uses_blob_filter_and_exclusions(self):
        self.assertIn("filter: blob:none", self.text)
        self.assertIn("sparse-checkout-cone-mode: false", self.text)
        self.assertIn("!/solutions/**/*.zip", self.text)
        self.assertIn("!/solutions/**/*.gif", self.text)
        self.assertIn("!/browser-audit/", self.text)
        self.assertIn("!/agents/", self.text)
        self.assertIn("!/tools/", self.text)
        for required in (
            "/scripts/build_pages_site.py",
            "/tests/test_pages_site.py",
            "/.github/workflows/pages.yml",
            "/solutions/",
            "/academy/",
            "/skills/",
            "/beta/index.html",
        ):
            self.assertIn(required, self.text)
        self.assertNotRegex(self.text, r"(?m)^\s+/beta/\s*$")

    def test_every_action_is_sha_pinned(self):
        actions = re.findall(r"(?m)^\s*uses:\s*([^\s#]+)", self.text)
        self.assertEqual(len(actions), 5)
        for action in actions:
            self.assertRegex(action, r"^actions/[a-z0-9-]+@[0-9a-f]{40}$")

    def test_build_tests_upload_and_deploy_site_directory(self):
        self.assertIn("python-version: '3.11'", self.text)
        self.assertIn("python scripts/build_pages_site.py", self.text)
        self.assertIn("GITHUB_TOKEN: ${{ github.token }}", self.text)
        self.assertIn("--out _site", self.text)
        self.assertIn("--ref \"${{ github.sha }}\"", self.text)
        self.assertIn("python -m unittest -v tests/test_pages_site.py", self.text)
        self.assertRegex(
            self.text,
            r"actions/upload-pages-artifact@[0-9a-f]{40}[\s\S]+?"
            r"with:\s+path: _site",
        )
        self.assertRegex(
            self.text, r"actions/deploy-pages@[0-9a-f]{40}"
        )
        self.assertNotRegex(
            self.text,
            r"actions/upload-pages-artifact@[0-9a-f]{40}[\s\S]+?"
            r"with:\s+path: \.$",
        )


if __name__ == "__main__":
    unittest.main()
