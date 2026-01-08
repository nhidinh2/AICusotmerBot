"""
QA System Evaluation Framework

This module provides evaluation metrics and test cases for the QA system.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass


@dataclass
class TestCase:
    """Test case for QA evaluation."""
    question: str
    expected_answer: Optional[str] = None
    expected_entities: Optional[List[str]] = None
    expected_sources: Optional[List[int]] = None
    category: str = "general"


class QAEvaluator:
    """Evaluator for QA system performance."""
    
    def __init__(self):
        self.test_cases: List[TestCase] = []
        self.results: List[Dict[str, Any]] = []
    
    def add_test_case(self, test_case: TestCase):
        """Add a test case."""
        self.test_cases.append(test_case)
    
    def load_test_cases_from_file(self, filepath: str):
        """Load test cases from CSV file."""
        df = pd.read_csv(filepath)
        for _, row in df.iterrows():
            test_case = TestCase(
                question=row['question'],
                expected_answer=row.get('expected_answer'),
                expected_entities=row.get('expected_entities', '').split(',') if row.get('expected_entities') else None,
                expected_sources=[int(x) for x in row.get('expected_sources', '').split(',')] if row.get('expected_sources') else None,
                category=row.get('category', 'general'),
            )
            self.add_test_case(test_case)
    
    async def evaluate(
        self,
        search_engine,
        test_cases: Optional[List[TestCase]] = None,
    ) -> pd.DataFrame:
        """
        Evaluate QA system on test cases.
        
        Args:
            search_engine: Search engine instance
            test_cases: Optional list of test cases (uses all if None)
            
        Returns:
            DataFrame with evaluation results
        """
        if test_cases is None:
            test_cases = self.test_cases
        
        results = []
        
        for test_case in test_cases:
            try:
                # Get answer from system
                result = await search_engine.asearch(test_case.question)
                answer = result.response
                
                # Calculate metrics
                metrics = self._calculate_metrics(
                    test_case,
                    answer,
                    result.context_data if hasattr(result, 'context_data') else {},
                )
                
                results.append({
                    'question': test_case.question,
                    'category': test_case.category,
                    'answer': answer,
                    **metrics,
                })
                
            except Exception as e:
                results.append({
                    'question': test_case.question,
                    'category': test_case.category,
                    'answer': f"Error: {str(e)}",
                    'relevance_score': 0,
                    'entity_match_score': 0,
                    'source_match_score': 0,
                    'overall_score': 0,
                    'error': str(e),
                })
        
        self.results = results
        return pd.DataFrame(results)
    
    def _calculate_metrics(
        self,
        test_case: TestCase,
        answer: str,
        context_data: Dict[str, Any],
    ) -> Dict[str, float]:
        """Calculate evaluation metrics."""
        metrics = {
            'relevance_score': 0.0,
            'entity_match_score': 0.0,
            'source_match_score': 0.0,
            'overall_score': 0.0,
        }
        
        # Entity matching
        if test_case.expected_entities and 'entities' in context_data:
            found_entities = context_data['entities']
            found_entity_names = found_entities['title'].tolist() if isinstance(found_entities, pd.DataFrame) else []
            
            matched = sum(1 for e in test_case.expected_entities if e in found_entity_names)
            metrics['entity_match_score'] = matched / len(test_case.expected_entities) if test_case.expected_entities else 0
        
        # Source matching
        if test_case.expected_sources and 'sources' in context_data:
            sources = context_data['sources']
            found_source_ids = sources.index.tolist() if isinstance(sources, pd.DataFrame) else []
            
            matched = sum(1 for s in test_case.expected_sources if s in found_source_ids)
            metrics['source_match_score'] = matched / len(test_case.expected_sources) if test_case.expected_sources else 0
        
        # Simple relevance score (length of answer as proxy)
        # In practice, use semantic similarity or LLM-based scoring
        if answer and len(answer) > 10:
            metrics['relevance_score'] = min(1.0, len(answer) / 500)  # Normalize
        
        # Overall score (weighted average)
        metrics['overall_score'] = (
            metrics['relevance_score'] * 0.4 +
            metrics['entity_match_score'] * 0.3 +
            metrics['source_match_score'] * 0.3
        )
        
        return metrics
    
    def generate_report(self) -> str:
        """Generate evaluation report."""
        if not self.results:
            return "No results to report."
        
        df = pd.DataFrame(self.results)
        
        report = []
        report.append("=" * 80)
        report.append("QA System Evaluation Report")
        report.append("=" * 80)
        report.append(f"\nTotal Test Cases: {len(df)}")
        report.append(f"Average Overall Score: {df['overall_score'].mean():.2f}")
        report.append(f"Average Relevance Score: {df['relevance_score'].mean():.2f}")
        report.append(f"Average Entity Match Score: {df['entity_match_score'].mean():.2f}")
        report.append(f"Average Source Match Score: {df['source_match_score'].mean():.2f}")
        
        # By category
        if 'category' in df.columns:
            report.append("\nScores by Category:")
            for category in df['category'].unique():
                cat_df = df[df['category'] == category]
                report.append(f"  {category}: {cat_df['overall_score'].mean():.2f} ({len(cat_df)} tests)")
        
        # Errors
        if 'error' in df.columns:
            errors = df[df['error'].notna()]
            if len(errors) > 0:
                report.append(f"\nErrors: {len(errors)}/{len(df)} tests failed")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)


# Sample test cases for Vietnamese stock market domain
SAMPLE_TEST_CASES = [
    TestCase(
        question="Thời gian giao dịch trái phiếu chính phủ tại Sở Giao dịch Chứng khoán Hà Nội như thế nào?",
        expected_entities=["SỞ GIAO DỊCH CHỨNG KHOÁN HÀ NỘI", "TRÁI PHIẾU CHÍNH PHỦ"],
        category="trading_hours",
    ),
    TestCase(
        question="Phí giao dịch chứng khoán tại MBS là bao nhiêu?",
        expected_entities=["MBS"],
        category="fees",
    ),
    TestCase(
        question="MBS cung cấp những dịch vụ gì?",
        expected_entities=["MBS"],
        category="services",
    ),
    TestCase(
        question="Có thể giao dịch cổ phiếu lô lẻ tại MBS không?",
        expected_entities=["MBS", "CỔ PHIẾU LÔ LẺ"],
        category="services",
    ),
]


def create_sample_test_file(filename: str = "test_cases.csv"):
    """Create a sample test cases CSV file."""
    test_cases = [
        {
            'question': 'Thời gian giao dịch trái phiếu chính phủ tại Sở Giao dịch Chứng khoán Hà Nội như thế nào?',
            'expected_entities': 'SỞ GIAO DỊCH CHỨNG KHOÁN HÀ NỘI,TRÁI PHIẾU CHÍNH PHỦ',
            'expected_sources': '200,228',
            'category': 'trading_hours',
        },
        {
            'question': 'Phí giao dịch chứng khoán tại MBS là bao nhiêu?',
            'expected_entities': 'MBS',
            'category': 'fees',
        },
        {
            'question': 'MBS cung cấp những dịch vụ gì?',
            'expected_entities': 'MBS',
            'category': 'services',
        },
    ]
    
    df = pd.DataFrame(test_cases)
    df.to_csv(filename, index=False)
    print(f"Created test cases file: {filename}")


if __name__ == "__main__":
    # Create sample test file
    create_sample_test_file("test_cases.csv")

