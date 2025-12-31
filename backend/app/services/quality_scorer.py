"""
Quality scoring service for survey responses.
Evaluates response quality based on multiple factors.
"""
from typing import Dict, List
from datetime import datetime


class QualityScorer:
    """Calculate quality scores for survey responses"""

    def __init__(self):
        self.weights = {
            "attention": 0.25,
            "speed": 0.20,
            "consistency": 0.20,
            "completion": 0.20,
            "engagement": 0.15,
        }

    def calculate_attention_score(
        self, answers: List[Dict], attention_checks: List[Dict]
    ) -> float:
        """
        Score based on attention check questions.
        Returns 0-100 score.
        """
        if not attention_checks:
            return 100.0

        correct = 0
        total = len(attention_checks)

        for check in attention_checks:
            question_id = check["question_id"]
            expected = check["expected_answer"]

            # Find answer for this question
            for answer in answers:
                if answer["question_id"] == question_id:
                    if answer.get("answer_text") == expected or answer.get(
                        "answer_choice"
                    ) == expected:
                        correct += 1
                    break

        return (correct / total * 100) if total > 0 else 100.0

    def calculate_speed_score(self, time_spent: int, expected_time: int) -> float:
        """
        Score based on response time.
        Penalize too fast (rushed) or too slow (distracted).
        Returns 0-100 score.
        """
        if not expected_time or not time_spent:
            return 50.0

        ratio = time_spent / expected_time

        # Ideal is 0.8 to 1.5x expected time
        if 0.8 <= ratio <= 1.5:
            return 100.0
        elif ratio < 0.5:  # Too fast - likely rushed
            return max(0, ratio / 0.5 * 50)
        elif ratio < 0.8:
            return 50 + (ratio - 0.5) / 0.3 * 50
        elif ratio < 3.0:  # Too slow - likely distracted
            return max(30, 100 - (ratio - 1.5) / 1.5 * 70)
        else:
            return 30.0

    def calculate_consistency_score(self, answers: List[Dict]) -> float:
        """
        Score based on internal consistency of answers.
        Returns 0-100 score.
        """
        # This is a simplified version
        # In production, you'd check for contradictory answers
        # For now, give full marks if answers exist
        return 100.0 if answers else 0.0

    def calculate_completion_score(
        self, answers: List[Dict], total_questions: int
    ) -> float:
        """
        Score based on completeness.
        Returns 0-100 score.
        """
        if total_questions == 0:
            return 100.0

        answered = len(answers)
        return (answered / total_questions) * 100

    def calculate_engagement_score(self, answers: List[Dict]) -> float:
        """
        Score based on depth of open-ended responses.
        Returns 0-100 score.
        """
        open_ended_answers = [
            a for a in answers if a.get("answer_text") and len(a.get("answer_text", "")) > 0
        ]

        if not open_ended_answers:
            return 75.0  # Neutral score if no open-ended questions

        total_score = 0
        for answer in open_ended_answers:
            text = answer.get("answer_text", "")
            word_count = len(text.split())

            # Score based on response length
            if word_count >= 20:
                total_score += 100
            elif word_count >= 10:
                total_score += 80
            elif word_count >= 5:
                total_score += 60
            elif word_count >= 2:
                total_score += 40
            else:
                total_score += 20

        return total_score / len(open_ended_answers)

    def detect_fraud_indicators(self, answers: List[Dict], metadata: Dict) -> List[str]:
        """
        Detect potential fraud indicators.
        Returns list of fraud indicator strings.
        """
        indicators = []

        # Check for extremely short time spent
        time_spent = metadata.get("time_spent_seconds", 0)
        if time_spent < 30:
            indicators.append("extremely_short_time")

        # Check for pattern responses (all same answer)
        if len(answers) > 3:
            choices = [a.get("answer_choice") for a in answers if a.get("answer_choice")]
            if len(set(choices)) == 1 and len(choices) > 3:
                indicators.append("uniform_pattern")

        # Check for gibberish in text responses
        text_answers = [a.get("answer_text", "") for a in answers if a.get("answer_text")]
        for text in text_answers:
            if len(text) > 5 and len(set(text)) < 3:  # Too many repeated characters
                indicators.append("gibberish_text")
                break

        return indicators

    def calculate_overall_score(
        self,
        answers: List[Dict],
        time_spent: int,
        expected_time: int,
        total_questions: int,
        attention_checks: List[Dict] = None,
    ) -> Dict:
        """
        Calculate overall quality score.
        Returns dict with all scores.
        """
        attention_checks = attention_checks or []

        attention_score = self.calculate_attention_score(answers, attention_checks)
        speed_score = self.calculate_speed_score(time_spent, expected_time)
        consistency_score = self.calculate_consistency_score(answers)
        completion_score = self.calculate_completion_score(answers, total_questions)
        engagement_score = self.calculate_engagement_score(answers)

        # Weighted overall score
        overall = (
            attention_score * self.weights["attention"]
            + speed_score * self.weights["speed"]
            + consistency_score * self.weights["consistency"]
            + completion_score * self.weights["completion"]
            + engagement_score * self.weights["engagement"]
        )

        # Detect fraud
        fraud_indicators = self.detect_fraud_indicators(
            answers, {"time_spent_seconds": time_spent}
        )
        is_suspicious = len(fraud_indicators) > 0 or overall < 50

        return {
            "attention_score": round(attention_score, 2),
            "speed_score": round(speed_score, 2),
            "consistency_score": round(consistency_score, 2),
            "completion_score": round(completion_score, 2),
            "engagement_score": round(engagement_score, 2),
            "overall_score": round(overall, 2),
            "is_suspicious": is_suspicious,
            "fraud_indicators": fraud_indicators,
        }
