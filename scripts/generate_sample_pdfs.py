"""
Generate sample PDF datasets for algorithm and complexity theory questions.
Creates sample exam questions across different topics and difficulty levels.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from pathlib import Path
from datetime import datetime


SAMPLE_QUESTIONS = {
    "asymptotic_analysis": [
        {
            "question": "Prove that 3n² + 5n + 2 = O(n²). Use the formal definition of Big-O notation.",
            "difficulty": "foundation",
            "solution": """
            To prove f(n) = O(g(n)), we need to show: ∃c > 0, n₀ > 0 such that f(n) ≤ c·g(n) for all n ≥ n₀

            Let f(n) = 3n² + 5n + 2 and g(n) = n²

            For n ≥ 1:
            - 3n² ≤ 3n²
            - 5n ≤ 5n²  (since n ≤ n² for n ≥ 1)
            - 2 ≤ 2n²   (since 1 ≤ n² for n ≥ 1)

            Therefore: 3n² + 5n + 2 ≤ 3n² + 5n² + 2n² = 10n²

            Choose c = 10 and n₀ = 1
            Then f(n) ≤ 10·g(n) for all n ≥ 1

            ∴ 3n² + 5n + 2 = O(n²) ∎
            """
        },
        {
            "question": "Show that n log n ≠ O(n). Prove by contradiction.",
            "difficulty": "conceptual",
            "solution": """
            Proof by contradiction:

            Assume n log n = O(n)
            Then ∃c > 0, n₀ > 0 such that n log n ≤ cn for all n ≥ n₀

            Dividing both sides by n (valid for n > 0):
            log n ≤ c for all n ≥ n₀

            But log n is unbounded as n → ∞
            For any constant c, we can find n₁ such that log n₁ > c
            (e.g., n₁ = 2^(c+1))

            This contradicts our assumption that log n ≤ c for all n ≥ n₀

            Therefore, our assumption was false
            ∴ n log n ≠ O(n) ∎
            """
        },
    ],
    "recurrence_relations": [
        {
            "question": "Solve the recurrence T(n) = 2T(n/2) + n using the recursion tree method.",
            "difficulty": "conceptual",
            "solution": """
            Recursion Tree Method:

            Level 0: n                          Cost: n
            Level 1: 2·(n/2)                    Cost: n
            Level 2: 4·(n/4)                    Cost: n
            Level 3: 8·(n/8)                    Cost: n
            ...
            Level i: 2^i·(n/2^i)                Cost: n

            Tree height: log₂(n) (when we reach T(1))

            Total cost = sum of costs at each level
                       = n + n + n + ... + n  (log n times)
                       = n·log n

            Therefore, T(n) = Θ(n log n) ∎
            """
        },
        {
            "question": "Use the Master Theorem to solve T(n) = 4T(n/2) + n².",
            "difficulty": "application",
            "solution": """
            Master Theorem for T(n) = aT(n/b) + f(n):

            Given: T(n) = 4T(n/2) + n²
            - a = 4
            - b = 2
            - f(n) = n²

            Calculate: log_b(a) = log₂(4) = 2

            Compare f(n) = n² with n^(log_b(a)) = n²:

            Case 2 applies: f(n) = Θ(n^(log_b(a)) · log^k(n)) where k = 0

            Therefore: T(n) = Θ(n² log n) ∎
            """
        },
    ],
    "dynamic_programming": [
        {
            "question": "Explain the optimal substructure property of the longest common subsequence (LCS) problem.",
            "difficulty": "conceptual",
            "solution": """
            Optimal Substructure of LCS:

            Let X = x₁x₂...xₘ and Y = y₁y₂...yₙ be two sequences
            Let L[i,j] = length of LCS of X[1..i] and Y[1..j]

            Property:
            If xᵢ = yⱼ:
                L[i,j] = L[i-1,j-1] + 1

            If xᵢ ≠ yⱼ:
                L[i,j] = max(L[i-1,j], L[i,j-1])

            Proof that this is optimal:

            Case 1: If xᵢ = yⱼ and both are in the LCS
            - The LCS must end with xᵢ = yⱼ
            - Remove this character: remaining is LCS of X[1..i-1] and Y[1..j-1]
            - If it wasn't optimal, we could construct a longer LCS - contradiction

            Case 2: If xᵢ ≠ yⱼ
            - At least one is not in the LCS
            - LCS is either LCS of X[1..i-1],Y[1..j] or X[1..i],Y[1..j-1]
            - We take the maximum of both

            This recursive structure leads to the DP solution ∎
            """
        },
    ],
    "graph_algorithms": [
        {
            "question": "Prove the correctness of Dijkstra's algorithm for finding shortest paths.",
            "difficulty": "advanced",
            "solution": """
            Dijkstra's Algorithm Correctness Proof:

            Claim: When a vertex v is added to the set S of processed vertices,
                   d[v] equals the shortest path distance from source s to v.

            Proof by induction on |S|:

            Base case: |S| = 1
            - S = {s}, d[s] = 0
            - Shortest path from s to s is 0 ✓

            Inductive hypothesis: Assume true for |S| = k

            Inductive step: Prove for |S| = k+1
            - Let u be the next vertex added to S
            - u has minimum d[u] among all vertices not in S

            We need to show: d[u] is the true shortest path distance

            Proof by contradiction:
            - Suppose ∃ shorter path P from s to u
            - Let y be the first vertex on P not in S
            - Let x be the predecessor of y on P (x is in S)

            Since edge weights are non-negative:
            - distance(s → y → u) ≥ distance(s → y)
            - By IH, d[x] = distance(s → x)
            - d[y] ≤ d[x] + weight(x,y) = distance(s → y)

            But u was chosen because d[u] ≤ d[y]
            Therefore: d[u] ≤ d[y] ≤ distance(s → y) ≤ distance(s → u via P)

            This contradicts our assumption that P is shorter
            ∴ d[u] is the true shortest path distance ∎
            """
        },
    ],
    "np_completeness": [
        {
            "question": "Prove that if P = NP, then every NP-complete problem can be solved in polynomial time.",
            "difficulty": "conceptual",
            "solution": """
            Proof:

            Definitions:
            - P = class of problems solvable in polynomial time
            - NP = class of problems verifiable in polynomial time
            - NP-complete = hardest problems in NP (all NP problems reduce to them)

            Assume: P = NP

            Let L be any NP-complete problem

            By definition of NP-complete:
            (1) L ∈ NP
            (2) For every problem L' ∈ NP, there exists a polynomial-time reduction
                from L' to L (L' ≤_p L)

            Since P = NP:
            - L ∈ NP implies L ∈ P
            - Therefore, L can be solved in polynomial time

            For any other NP-complete problem L':
            - L' ≤_p L (by definition of NP-complete)
            - L can be solved in polynomial time
            - A polynomial-time reduction composed with a polynomial-time algorithm
              gives a polynomial-time algorithm
            - Therefore, L' ∈ P

            Conclusion: If P = NP, then every NP-complete problem is in P ∎

            Note: This is why P vs NP is so important - solving one NP-complete
            problem in polynomial time would solve them all!
            """
        },
    ]
}


def create_exam_pdf(filename: str, topic: str, questions: list):
    """
    Create a PDF with exam questions.

    Args:
        filename: Output PDF filename
        topic: Topic name
        questions: List of question dictionaries
    """
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkblue',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading_style = styles['Heading2']
    normal_style = styles['BodyText']
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=12
    )

    # Title
    title = Paragraph(f"Algorithm Analysis & Complexity Theory<br/>Sample Exam: {topic.replace('_', ' ').title()}", title_style)
    story.append(title)
    story.append(Spacer(1, 0.2*inch))

    # Metadata
    metadata = Paragraph(f"<i>Generated: {datetime.now().strftime('%B %d, %Y')}<br/>Difficulty Levels: Foundation, Conceptual, Application, Advanced</i>", normal_style)
    story.append(metadata)
    story.append(Spacer(1, 0.3*inch))

    # Questions
    for i, q in enumerate(questions, 1):
        # Question number and difficulty
        q_header = Paragraph(
            f"<b>Question {i}</b> [Difficulty: {q['difficulty'].title()}]",
            heading_style
        )
        story.append(q_header)
        story.append(Spacer(1, 0.1*inch))

        # Question text
        q_text = Paragraph(q['question'], normal_style)
        story.append(q_text)
        story.append(Spacer(1, 0.3*inch))

        # Solution
        sol_header = Paragraph("<b>Solution:</b>", heading_style)
        story.append(sol_header)
        story.append(Spacer(1, 0.1*inch))

        # Format solution (preserve structure)
        solution_lines = q['solution'].strip().split('\n')
        for line in solution_lines:
            if line.strip():
                sol_line = Paragraph(line, code_style if line.startswith(' ') else normal_style)
                story.append(sol_line)

        story.append(Spacer(1, 0.5*inch))

        # Page break between questions
        if i < len(questions):
            story.append(PageBreak())

    # Build PDF
    doc.build(story)
    print(f"✓ Created: {filename}")


def main():
    """Generate sample PDFs for testing."""
    print("\n" + "="*60)
    print("Generating Sample PDF Datasets")
    print("="*60)

    output_dir = Path(__file__).parent / "sample_pdfs"
    output_dir.mkdir(exist_ok=True)

    print(f"\nOutput directory: {output_dir}")
    print(f"Topics: {len(SAMPLE_QUESTIONS)}")

    total_pdfs = 0

    for topic, questions in SAMPLE_QUESTIONS.items():
        filename = output_dir / f"sample_exam_{topic}.pdf"
        create_exam_pdf(str(filename), topic, questions)
        total_pdfs += 1

    # Create a combined PDF with all topics
    all_questions = []
    for topic, questions in SAMPLE_QUESTIONS.items():
        all_questions.extend(questions)

    combined_filename = output_dir / "sample_exam_all_topics.pdf"
    create_exam_pdf(str(combined_filename), "All Topics", all_questions)
    total_pdfs += 1

    print("\n" + "="*60)
    print(f"✓ Generated {total_pdfs} PDF files")
    print(f"  Total questions: {sum(len(q) for q in SAMPLE_QUESTIONS.values())}")
    print(f"  Location: {output_dir}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
