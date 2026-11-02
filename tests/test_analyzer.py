import unittest

from src.analyzer import analyze_match, extract_skills


class AnalyzerTests(unittest.TestCase):
    def test_extract_skills_aliases(self):
        text = "I use Python, PowerBI, SQL, and machine learning for data analytics."
        found = extract_skills(text)
        self.assertIn("Python", found)
        self.assertIn("Power BI", found)
        self.assertIn("SQL", found)
        self.assertIn("Machine Learning", found)
        self.assertIn("Data Analysis", found)

    def test_match_scores_and_missing_skills(self):
        resume = (
            "Python developer with SQL and Power BI experience. "
            "Built data analysis dashboards and automated reports for business teams."
        )
        job = (
            "Looking for a data analyst with Python, SQL, Power BI, Excel, and Tableau skills. "
            "The role includes data analysis, reporting, and dashboard development."
        )
        result = analyze_match(resume, job)
        self.assertGreaterEqual(result.overall_score, 0)
        self.assertLessEqual(result.overall_score, 100)
        self.assertIn("Python", result.matched_skills)
        self.assertIn("Excel", result.missing_skills)
        self.assertIn("Tableau", result.missing_skills)

    def test_ambiguous_words_not_counted_as_skills(self):
        found = extract_skills("We want people who excel in teams and react quickly.")
        self.assertNotIn("Excel", found)
        self.assertNotIn("React", found)
        self.assertIn("Excel", extract_skills("Skills: Python, Excel, SQL."))

    def test_plain_communication_detected(self):
        self.assertIn("Communication", extract_skills("Python, SQL, communication, teamwork"))

    def test_shared_terms_include_phrases(self):
        result = analyze_match(
            "Built Power BI dashboards. Data analysis with Python.",
            "Need Power BI dashboards and data analysis using Python.",
        )
        self.assertTrue(any(" " in term for term in result.top_shared_terms))

    def test_rejects_too_short_text(self):
        with self.assertRaises(ValueError):
            analyze_match("short", "This is a sufficiently long job description for testing purposes.")


if __name__ == "__main__":
    unittest.main()
