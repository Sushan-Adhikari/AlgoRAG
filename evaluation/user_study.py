"""
User Study Framework for AlgoRAG Research

Implements:
- Pre/post assessment questionnaires
- Student comprehension tests
- Likert scale surveys
- Learning outcome measurement
- Data collection and analysis
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import csv


@dataclass
class Question:
    """Single assessment question."""
    question_id: str
    text: str
    question_type: str  # 'multiple_choice', 'short_answer', 'proof', 'likert'
    topic: str
    difficulty: str  # 'easy', 'medium', 'hard'
    correct_answer: Optional[str] = None
    options: Optional[List[str]] = None
    points: int = 1


@dataclass
class StudentResponse:
    """Student's response to a question."""
    student_id: str
    question_id: str
    answer: str
    timestamp: str
    time_spent_seconds: float
    score: Optional[float] = None


@dataclass
class SurveyQuestion:
    """Likert scale or opinion survey question."""
    question_id: str
    text: str
    scale_type: str  # 'likert_5', 'likert_7', 'yes_no', 'text'


class UserStudy:
    """
    Manages user study for research paper evaluation.

    Study Design:
    1. Pre-assessment (baseline knowledge)
    2. Intervention (use AlgoRAG system)
    3. Post-assessment (knowledge gain)
    4. Satisfaction survey
    """

    def __init__(self, study_id: str, output_dir: str = './user_study_data'):
        """
        Initialize user study.

        Args:
            study_id: Unique identifier for this study
            output_dir: Directory to store study data
        """
        self.study_id = study_id
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.participants = []
        self.pre_assessment = []
        self.post_assessment = []
        self.survey_questions = []

        self.responses = {
            'pre': [],
            'post': [],
            'survey': []
        }

    # ==================== Assessment Design ====================

    def create_pre_assessment(self) -> List[Question]:
        """
        Create pre-intervention assessment questions.

        Covers all major topics to establish baseline.
        """
        questions = [
            # Asymptotic Analysis
            Question(
                question_id='pre_1',
                text='What is the definition of Big-O notation?',
                question_type='short_answer',
                topic='asymptotic_analysis',
                difficulty='easy',
                points=5
            ),
            Question(
                question_id='pre_2',
                text='Prove that 2n^2 + 3n = O(n^2)',
                question_type='proof',
                topic='asymptotic_analysis',
                difficulty='medium',
                points=10
            ),
            Question(
                question_id='pre_3',
                text='What is the time complexity of the following code?\n\n```\nfor i in range(n):\n    for j in range(i, n):\n        print(i, j)\n```',
                question_type='multiple_choice',
                topic='complexity_analysis',
                difficulty='medium',
                options=['O(n)', 'O(n log n)', 'O(n^2)', 'O(2^n)'],
                correct_answer='O(n^2)',
                points=5
            ),

            # Recurrence Relations
            Question(
                question_id='pre_4',
                text='Solve the recurrence T(n) = 2T(n/2) + n using the Master Theorem',
                question_type='short_answer',
                topic='recurrence_relations',
                difficulty='medium',
                points=10
            ),

            # Dynamic Programming
            Question(
                question_id='pre_5',
                text='Explain the principle of optimal substructure in dynamic programming',
                question_type='short_answer',
                topic='dynamic_programming',
                difficulty='medium',
                points=5
            ),
            Question(
                question_id='pre_6',
                text='What is the time complexity of the standard dynamic programming solution to the 0/1 Knapsack problem?',
                question_type='multiple_choice',
                topic='dynamic_programming',
                difficulty='medium',
                options=['O(n)', 'O(n^2)', 'O(nW)', 'O(2^n)'],
                correct_answer='O(nW)',
                points=5
            ),

            # Graph Algorithms
            Question(
                question_id='pre_7',
                text='What is the time complexity of Dijkstra\'s algorithm with a binary heap?',
                question_type='multiple_choice',
                topic='graph_algorithms',
                difficulty='medium',
                options=['O(V^2)', 'O(E log V)', 'O(V log V)', 'O(VE)'],
                correct_answer='O(E log V)',
                points=5
            ),

            # NP-Completeness
            Question(
                question_id='pre_8',
                text='Define what it means for a problem to be NP-complete',
                question_type='short_answer',
                topic='np_completeness',
                difficulty='hard',
                points=10
            ),
        ]

        self.pre_assessment = questions
        return questions

    def create_post_assessment(self) -> List[Question]:
        """
        Create post-intervention assessment.

        Parallel questions to pre-assessment but different instances.
        """
        questions = [
            # Asymptotic Analysis (parallel to pre_1, pre_2)
            Question(
                question_id='post_1',
                text='Explain the difference between O, Ω, and Θ notations',
                question_type='short_answer',
                topic='asymptotic_analysis',
                difficulty='easy',
                points=5
            ),
            Question(
                question_id='post_2',
                text='Prove that 5n^2 + 2n + 10 = O(n^2)',
                question_type='proof',
                topic='asymptotic_analysis',
                difficulty='medium',
                points=10
            ),
            Question(
                question_id='post_3',
                text='What is the time complexity of the following code?\n\n```\nfor i in range(n):\n    j = 1\n    while j < n:\n        print(i, j)\n        j *= 2\n```',
                question_type='multiple_choice',
                topic='complexity_analysis',
                difficulty='medium',
                options=['O(n)', 'O(n log n)', 'O(n^2)', 'O(log n)'],
                correct_answer='O(n log n)',
                points=5
            ),

            # Recurrence Relations
            Question(
                question_id='post_4',
                text='Solve the recurrence T(n) = 3T(n/3) + n using the Master Theorem',
                question_type='short_answer',
                topic='recurrence_relations',
                difficulty='medium',
                points=10
            ),

            # Dynamic Programming
            Question(
                question_id='post_5',
                text='What is memoization and how does it relate to dynamic programming?',
                question_type='short_answer',
                topic='dynamic_programming',
                difficulty='medium',
                points=5
            ),
            Question(
                question_id='post_6',
                text='What is the time complexity of computing the nth Fibonacci number using dynamic programming?',
                question_type='multiple_choice',
                topic='dynamic_programming',
                difficulty='medium',
                options=['O(n)', 'O(n^2)', 'O(log n)', 'O(2^n)'],
                correct_answer='O(n)',
                points=5
            ),

            # Graph Algorithms
            Question(
                question_id='post_7',
                text='What is the time complexity of Breadth-First Search (BFS)?',
                question_type='multiple_choice',
                topic='graph_algorithms',
                difficulty='medium',
                options=['O(V)', 'O(E)', 'O(V + E)', 'O(V * E)'],
                correct_answer='O(V + E)',
                points=5
            ),

            # NP-Completeness
            Question(
                question_id='post_8',
                text='Explain the P vs NP problem in your own words',
                question_type='short_answer',
                topic='np_completeness',
                difficulty='hard',
                points=10
            ),
        ]

        self.post_assessment = questions
        return questions

    def create_satisfaction_survey(self) -> List[SurveyQuestion]:
        """
        Create satisfaction survey using Likert scales.

        Measures perceived usefulness and ease of use.
        """
        questions = [
            SurveyQuestion(
                question_id='survey_1',
                text='The AlgoRAG system helped me understand algorithm concepts better',
                scale_type='likert_5'
            ),
            SurveyQuestion(
                question_id='survey_2',
                text='The explanations provided by AlgoRAG were clear and easy to follow',
                scale_type='likert_5'
            ),
            SurveyQuestion(
                question_id='survey_3',
                text='The step-by-step proofs were helpful for my learning',
                scale_type='likert_5'
            ),
            SurveyQuestion(
                question_id='survey_4',
                text='I would use AlgoRAG again for studying algorithms',
                scale_type='likert_5'
            ),
            SurveyQuestion(
                question_id='survey_5',
                text='AlgoRAG is better than using a traditional textbook',
                scale_type='likert_5'
            ),
            SurveyQuestion(
                question_id='survey_6',
                text='The mathematical notation in answers was accurate and well-formatted',
                scale_type='likert_5'
            ),
            SurveyQuestion(
                question_id='survey_7',
                text='The system responded quickly enough for my needs',
                scale_type='likert_5'
            ),
            SurveyQuestion(
                question_id='survey_8',
                text='What did you like most about AlgoRAG?',
                scale_type='text'
            ),
            SurveyQuestion(
                question_id='survey_9',
                text='What could be improved about AlgoRAG?',
                scale_type='text'
            ),
        ]

        self.survey_questions = questions
        return questions

    # ==================== Data Collection ====================

    def register_participant(
        self,
        student_id: str,
        demographics: Optional[Dict[str, Any]] = None
    ):
        """
        Register a new study participant.

        Args:
            student_id: Unique student identifier
            demographics: Optional demographic data (year, major, etc.)
        """
        participant = {
            'student_id': student_id,
            'registration_time': datetime.now().isoformat(),
            'demographics': demographics or {},
            'status': 'registered'
        }

        self.participants.append(participant)
        self._save_participants()

    def collect_pre_response(
        self,
        student_id: str,
        question_id: str,
        answer: str,
        time_spent_seconds: float
    ):
        """Collect pre-assessment response."""
        response = StudentResponse(
            student_id=student_id,
            question_id=question_id,
            answer=answer,
            timestamp=datetime.now().isoformat(),
            time_spent_seconds=time_spent_seconds
        )

        self.responses['pre'].append(response)
        self._save_responses('pre')

    def collect_post_response(
        self,
        student_id: str,
        question_id: str,
        answer: str,
        time_spent_seconds: float
    ):
        """Collect post-assessment response."""
        response = StudentResponse(
            student_id=student_id,
            question_id=question_id,
            answer=answer,
            timestamp=datetime.now().isoformat(),
            time_spent_seconds=time_spent_seconds
        )

        self.responses['post'].append(response)
        self._save_responses('post')

    def collect_survey_response(
        self,
        student_id: str,
        question_id: str,
        answer: str
    ):
        """Collect survey response."""
        response = {
            'student_id': student_id,
            'question_id': question_id,
            'answer': answer,
            'timestamp': datetime.now().isoformat()
        }

        self.responses['survey'].append(response)
        self._save_responses('survey')

    # ==================== Scoring ====================

    def score_response(self, response: StudentResponse, correct_answer: str) -> float:
        """
        Score a student response.

        For multiple choice: exact match
        For short answer/proof: manual grading (return 0 for now)

        Args:
            response: Student's response
            correct_answer: Correct answer

        Returns:
            Score (0.0 to 1.0)
        """
        if response.answer.strip().lower() == correct_answer.strip().lower():
            return 1.0
        else:
            # Manual grading required
            return 0.0

    def calculate_pre_post_gain(self, student_id: str) -> Dict[str, float]:
        """
        Calculate learning gain for a student.

        Uses normalized gain: (post - pre) / (max - pre)

        Args:
            student_id: Student identifier

        Returns:
            Dictionary with scores and gain
        """
        # Get student's responses
        pre_responses = [r for r in self.responses['pre'] if r.student_id == student_id]
        post_responses = [r for r in self.responses['post'] if r.student_id == student_id]

        # Calculate scores (requires manual grading for open-ended)
        pre_score = sum(r.score or 0 for r in pre_responses)
        post_score = sum(r.score or 0 for r in post_responses)

        max_pre = len(self.pre_assessment) * 1.0
        max_post = len(self.post_assessment) * 1.0

        pre_normalized = pre_score / max_pre if max_pre > 0 else 0
        post_normalized = post_score / max_post if max_post > 0 else 0

        # Normalized gain
        if pre_normalized < 1.0:
            gain = (post_normalized - pre_normalized) / (1.0 - pre_normalized)
        else:
            gain = 0.0

        return {
            'pre_score': pre_normalized,
            'post_score': post_normalized,
            'absolute_gain': post_normalized - pre_normalized,
            'normalized_gain': gain
        }

    # ==================== Analysis ====================

    def analyze_results(self) -> Dict[str, Any]:
        """
        Analyze study results across all participants.

        Returns:
            Aggregate statistics
        """
        import numpy as np

        # Calculate per-student gains
        gains = []
        for participant in self.participants:
            student_id = participant['student_id']
            try:
                gain_data = self.calculate_pre_post_gain(student_id)
                gains.append(gain_data)
            except Exception as e:
                print(f"Error calculating gain for {student_id}: {e}")

        if not gains:
            return {'error': 'No complete data for analysis'}

        # Aggregate statistics
        analysis = {
            'participants_count': len(self.participants),
            'mean_pre_score': np.mean([g['pre_score'] for g in gains]),
            'mean_post_score': np.mean([g['post_score'] for g in gains]),
            'mean_absolute_gain': np.mean([g['absolute_gain'] for g in gains]),
            'mean_normalized_gain': np.mean([g['normalized_gain'] for g in gains]),
            'std_normalized_gain': np.std([g['normalized_gain'] for g in gains]),

            # Survey analysis
            'survey_results': self._analyze_survey()
        }

        return analysis

    def _analyze_survey(self) -> Dict[str, Any]:
        """Analyze Likert scale responses."""
        likert_responses = {}

        for response in self.responses['survey']:
            qid = response['question_id']
            answer = response['answer']

            if qid not in likert_responses:
                likert_responses[qid] = []

            # Convert Likert response to number (1-5)
            try:
                likert_responses[qid].append(int(answer))
            except ValueError:
                # Text responses
                pass

        # Calculate means
        import numpy as np
        survey_stats = {}
        for qid, values in likert_responses.items():
            if values:
                survey_stats[qid] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'count': len(values)
                }

        return survey_stats

    # ==================== Export ====================

    def export_to_csv(self, filename: str = 'user_study_results.csv'):
        """Export results to CSV for statistical analysis."""
        filepath = self.output_dir / filename

        with open(filepath, 'w', newline='') as f:
            fieldnames = [
                'student_id', 'pre_score', 'post_score',
                'absolute_gain', 'normalized_gain'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for participant in self.participants:
                student_id = participant['student_id']
                try:
                    gain_data = self.calculate_pre_post_gain(student_id)
                    writer.writerow({
                        'student_id': student_id,
                        **gain_data
                    })
                except Exception:
                    pass

        print(f"Results exported to: {filepath}")

    def _save_participants(self):
        """Save participant data to JSON."""
        filepath = self.output_dir / f'{self.study_id}_participants.json'
        with open(filepath, 'w') as f:
            json.dump(self.participants, f, indent=2)

    def _save_responses(self, assessment_type: str):
        """Save responses to JSON."""
        filepath = self.output_dir / f'{self.study_id}_{assessment_type}_responses.json'
        data = [asdict(r) if hasattr(r, '__dict__') else r for r in self.responses[assessment_type]]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# ==================== Example Usage ====================

if __name__ == '__main__':
    # Create a user study
    study = UserStudy(study_id='algorag_pilot_study_2025')

    # Create assessments
    pre_questions = study.create_pre_assessment()
    post_questions = study.create_post_assessment()
    survey = study.create_satisfaction_survey()

    print(f"Pre-assessment: {len(pre_questions)} questions")
    print(f"Post-assessment: {len(post_questions)} questions")
    print(f"Survey: {len(survey)} questions")

    # Example: Register a student
    study.register_participant(
        student_id='student_001',
        demographics={'year': 'junior', 'major': 'CS'}
    )

    print("\nUser study framework ready!")
