"""Test suite for the CareerPath app.

Covers resume parsing, the live-job-search fallback, the ML classifier,
authentication (incl. legacy-hash upgrade), the seed command, and key views.
"""
from django.test import TestCase, Client
from django.core.management import call_command
from django.contrib.auth.hashers import make_password

from webapp import resume_parser, job_api
from webapp.models import Users, dataset, SkillsDataset
from webapp.GetHash import get_hash


class ResumeParserTests(TestCase):
    def test_skill_word_boundaries(self):
        skills = resume_parser.extract_skills("Proficient in JavaScript and Node.js")
        self.assertIn("JavaScript", skills)
        self.assertIn("Node.js", skills)
        # "Java" must not be matched inside "JavaScript"
        self.assertNotIn("Java", skills)

    def test_single_letter_skills_need_boundaries(self):
        # "R" should only match as a standalone token, not inside words.
        self.assertNotIn("R", resume_parser.extract_skills("Strong leadership and rigour"))
        skills = resume_parser.extract_skills("Languages: R, C++, Python")
        self.assertIn("R", skills)
        self.assertIn("C++", skills)
        self.assertIn("Python", skills)

    def test_vocabulary_is_deduplicated_case_insensitively(self):
        vocab = resume_parser.load_skill_vocabulary()
        lowered = [s.lower() for s in vocab]
        self.assertEqual(len(lowered), len(set(lowered)))
        self.assertGreater(len(vocab), 50)

    def test_email_and_phone(self):
        text = "Contact me at jane.doe@example.com or +1 415 555 1234."
        self.assertEqual(resume_parser.extract_email(text), "jane.doe@example.com")
        self.assertIsNotNone(resume_parser.extract_phone_number(text))

    def test_total_experience(self):
        self.assertEqual(resume_parser.extract_total_experience("I have 6 years of work"), "6 years")
        self.assertEqual(resume_parser.extract_total_experience("no number here"), "Experience Not Found")


class JobApiTests(TestCase):
    def setUp(self):
        dataset.objects.create(
            job_id="JOBTEST", skills="Python, Django", years_of_experience=3,
            predicted_job_title="Full Stack Developer", company_name="Acme",
            company_location="Boston", industry="Tech", salary_usd=100000,
            education_level="BTech",
        )

    def test_local_fallback_when_providers_fail(self):
        # Force both live providers to fail -> local dataset fallback.
        def boom(*a, **k):
            raise RuntimeError("network blocked")
        orig = job_api.requests.get
        job_api.requests.get = boom
        try:
            jobs, source = job_api.search_jobs("Full Stack Developer")
        finally:
            job_api.requests.get = orig
        self.assertTrue(jobs)
        self.assertEqual(jobs[0]["company"], "Acme")
        self.assertIn("Sample dataset", source)

    def test_remotive_parsing(self):
        class FakeResp:
            def raise_for_status(self): pass
            def json(self):
                return {"jobs": [{
                    "title": "Backend Engineer", "company_name": "Globex",
                    "candidate_required_location": "Remote", "salary": "$120k",
                    "url": "https://example.com/job", "description": "<p>build</p>",
                }]}
        orig = job_api.requests.get
        job_api.requests.get = lambda *a, **k: FakeResp()
        try:
            jobs, source = job_api.search_jobs("backend")
        finally:
            job_api.requests.get = orig
        self.assertEqual(source, "Remotive")
        self.assertEqual(jobs[0]["title"], "Backend Engineer")
        self.assertEqual(jobs[0]["company"], "Globex")


class ClassificationTests(TestCase):
    def test_train_and_predict(self):
        from webapp.Classification import Classification
        from sklearn.ensemble import RandomForestClassifier
        model = Classification(RandomForestClassifier(random_state=42))
        metrics = model.train()
        self.assertEqual(len(metrics), 4)
        for m in metrics:
            self.assertGreaterEqual(m, 0.0)
            self.assertLessEqual(m, 1.0)
        prediction = model.predict("Python, Django, React", 5, "BTech")
        # Prediction must be a non-empty job title string.
        self.assertIsInstance(prediction, str)
        self.assertTrue(prediction)


class AuthTests(TestCase):
    def test_register_creates_pbkdf2_user(self):
        c = Client()
        c.post("/register/", {"name": "Jane", "contact": "123",
                              "email": "jane@example.com", "password": "secret123"})
        user = Users.objects.get(username="jane@example.com")
        self.assertNotEqual(user.password, "secret123")
        self.assertTrue(user.password.startswith("pbkdf2_"))

    def test_login_success(self):
        Users.objects.create(name="J", contact="1", username="j@x.com",
                             email="j@x.com", password=make_password("pw12345"))
        c = Client()
        resp = c.post("/login/", {"email": "j@x.com", "password": "pw12345"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(c.session.get("email"), "j@x.com")

    def test_legacy_md5_login_upgrades_hash(self):
        Users.objects.create(name="Old", contact="1", username="old@x.com",
                             email="old@x.com", password=get_hash("legacypw"))
        c = Client()
        resp = c.post("/login/", {"email": "old@x.com", "password": "legacypw"})
        self.assertEqual(resp.status_code, 302)
        upgraded = Users.objects.get(username="old@x.com")
        self.assertTrue(upgraded.password.startswith("pbkdf2_"))


class SeedCommandTests(TestCase):
    def test_seed_data_populates_tables(self):
        call_command("seed_data")
        self.assertEqual(dataset.objects.count(), 520)
        self.assertGreater(SkillsDataset.objects.count(), 0)
        # Idempotent: a second run keeps the same counts.
        call_command("seed_data")
        self.assertEqual(dataset.objects.count(), 520)


class ViewTests(TestCase):
    def test_home_ok(self):
        self.assertEqual(Client().get("/").status_code, 200)

    def test_jobsearch_requires_login(self):
        self.assertEqual(Client().get("/jobsearch/").status_code, 302)

    def test_jobsearch_with_session(self):
        c = Client()
        s = c.session; s["email"] = "user@x.com"; s.save()
        self.assertEqual(c.get("/jobsearch/").status_code, 200)
