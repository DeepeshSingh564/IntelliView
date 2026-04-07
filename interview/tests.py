from django.test import TestCase
from unittest.mock import patch
from .ai_engine import ai_evaluate_answer

class AiEngineTests(TestCase):

    @patch("interview.ai_engine.openai.ChatCompletion.create")
    def test_ai_evaluate_answer_parses_json(self, mock_create):
        # Mock OpenAI response
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": '{"strengths": ["good"], "weaknesses": ["short"], "improvements": ["expand answer"], "score": 6}'
                    }
                }
            ]
        }
        mock_create.return_value = mock_response

        # Call your function
        result = ai_evaluate_answer("What is Django?", "It is a Python web framework.")

        # Assertions
        self.assertEqual(result["score"], 6)
        self.assertIn("good", result["strengths"])
        self.assertIn("short", result["weaknesses"])
        self.assertIn("expand answer", result["improvements"])
