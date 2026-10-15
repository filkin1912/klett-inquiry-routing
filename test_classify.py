import unittest

from classify import ModelUnavailable, classify


class ClassifyTests(unittest.TestCase):
    def test_assignment_examples(self):
        cases = {
            "Не мога да вляза в профила си, въпреки че паролата е правилна.": "access_or_registration",
            "Видеоурокът по математика не се зарежда.": "technical_problem",
            "Къде мога да намеря упражненията за 5. клас?": "learning_content",
            "Как мога да променя имейла на профила си?": "access_or_registration",
        }
        for text, category in cases.items():
            result = classify(text, model=None)
            self.assertTrue(result["ok"])
            self.assertEqual(result["category"], category)
            self.assertEqual(result["method"], "rules")

    def test_english_examples_stay_other(self):
        cases = (
            "I cannot log in to my profile even though the password is correct.",
            "The math video lesson does not load.",
            "the math video lesson doesnt load",
            "Where can I find the exercises for grade 5?",
            "How can I change the email on my profile?",
        )
        for text in cases:
            result = classify(text, model=None)
            self.assertEqual(result["category"], "other")
            self.assertEqual(result["method"], "rules")

    def test_empty_and_invalid_input(self):
        for value in ("", "   ", None, 12, "???"):
            result = classify(value)
            self.assertFalse(result["ok"])
            self.assertIsNone(result["category"])
            self.assertIn("error", result)

    def test_unknown_text_uses_model(self):
        result = classify("When is the office closed?")
        self.assertEqual(result["category"], "other")
        self.assertEqual(result["method"], "model")

    def test_model_failure_keeps_rules_result(self):
        def down(_text):
            raise ModelUnavailable("timeout")

        result = classify("When is the office closed?", model=down)
        self.assertTrue(result["ok"])
        self.assertEqual(result["category"], "other")
        self.assertEqual(result["method"], "rules")


if __name__ == "__main__":
    unittest.main()
