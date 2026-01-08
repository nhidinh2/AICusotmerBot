"""
QA System Improvement Utilities

This module contains helper functions and classes to improve the QA system.
"""

import asyncio
from typing import Dict, List, Optional, Any
import pandas as pd
from graphrag.query.context_builder.conversation_history import ConversationHistory, ConversationRole


def format_sources_with_context(context_data: Dict[str, pd.DataFrame]) -> str:
    """
    Format source citations in a user-friendly way.
    
    Args:
        context_data: Dictionary containing context data from search result
        
    Returns:
        Formatted string with source citations
    """
    sources_text = []
    
    if "sources" in context_data:
        sources_df = context_data["sources"]
        for idx, row in sources_df.iterrows():
            # Get first 150 characters as preview
            text_preview = row["text"][:150] + "..." if len(row["text"]) > 150 else row["text"]
            sources_text.append(f"[{idx}] {text_preview}")
    
    if "entities" in context_data:
        entities_df = context_data["entities"]
        if len(entities_df) > 0:
            sources_text.append(f"\nCác thực thể liên quan: {', '.join(entities_df.head(5)['title'].tolist())}")
    
    if sources_text:
        return "\n\n📚 Nguồn tham khảo:\n" + "\n".join(sources_text)
    
    return "\n\n📚 Nguồn tham khảo: Không có thông tin"


async def validate_answer_quality(
    question: str,
    answer: str,
    context_data: Dict[str, pd.DataFrame],
    llm,
) -> Dict[str, Any]:
    """
    Validate answer quality and grounding.
    
    Args:
        question: User question
        answer: Generated answer
        context_data: Context data used for answer
        llm: LLM instance for validation
        
    Returns:
        Dictionary with validation scores and issues
    """
    # Extract source texts
    source_texts = []
    if "sources" in context_data:
        source_texts = context_data["sources"]["text"].tolist()
    
    validation_prompt = f"""
Bạn là chuyên gia đánh giá chất lượng câu trả lời. Hãy đánh giá câu trả lời sau:

Câu hỏi: {question}
Câu trả lời: {answer}
Nguồn tài liệu: {' '.join(source_texts[:3])}

Hãy đánh giá theo các tiêu chí (0-10):
1. Tính chính xác (Factual Accuracy): Câu trả lời có chính xác không?
2. Tính đầy đủ (Completeness): Câu trả lời có đầy đủ thông tin không?
3. Tính liên quan (Relevance): Câu trả lời có liên quan đến câu hỏi không?
4. Tính dựa trên nguồn (Source Grounding): Câu trả lời có dựa trên nguồn tài liệu không?
5. Phát hiện ảo tưởng (Hallucination): Có thông tin không có trong nguồn không?

Trả về JSON:
{{
    "accuracy": <score 0-10>,
    "completeness": <score 0-10>,
    "relevance": <score 0-10>,
    "grounding": <score 0-10>,
    "hallucination": <score 0-10>,
    "issues": ["list of issues if any"],
    "overall_score": <average score>
}}
"""
    
    try:
        result = await llm(validation_prompt)
        # Parse JSON result
        import json
        validation = json.loads(result.output)
        return validation
    except Exception as e:
        return {
            "accuracy": -1,
            "completeness": -1,
            "relevance": -1,
            "grounding": -1,
            "hallucination": -1,
            "issues": [f"Validation failed: {str(e)}"],
            "overall_score": -1
        }


class ConversationManager:
    """Enhanced conversation management with summarization."""
    
    def __init__(self, max_tokens: int = 12000):
        self.history = ConversationHistory()
        self.max_tokens = max_tokens
        self.entity_tracker = {}  # Track entities mentioned in conversation
    
    def add_turn(self, question: str, answer: str):
        """Add a turn to the conversation."""
        self.history.add_turn(ConversationRole.USER, question)
        self.history.add_turn(ConversationRole.ASSISTANT, answer)
    
    def should_summarize(self, token_encoder) -> bool:
        """Check if conversation history should be summarized."""
        if len(self.history.turns) == 0:
            return False
        
        context, _ = self.history.build_context(
            token_encoder=token_encoder,
            max_tokens=self.max_tokens
        )
        
        tokens = token_encoder.encode(context)
        return len(tokens) > self.max_tokens * 0.8
    
    def summarize_old_turns(self, llm, token_encoder):
        """Summarize old conversation turns to save tokens."""
        if len(self.history.turns) <= 4:
            return
        
        # Get old turns (except last 2)
        old_turns = self.history.turns[:-2]
        summary_prompt = f"""
Hãy tóm tắt cuộc hội thoại sau một cách ngắn gọn, giữ lại các thông tin quan trọng:
{chr(10).join(str(turn) for turn in old_turns)}

Tóm tắt:
"""
        
        # This would need async implementation
        # For now, just truncate old turns
        self.history.turns = self.history.turns[-2:]
    
    def get_relevant_entities(self) -> List[str]:
        """Get entities mentioned in conversation."""
        return list(self.entity_tracker.keys())


class HybridSearch:
    """Hybrid search that combines local and global search."""
    
    def __init__(self, local_search, global_search, llm=None):
        self.local_search = local_search
        self.global_search = global_search
        self.llm = llm
    
    async def classify_query(self, query: str) -> str:
        """Classify query as 'local' or 'global'."""
        if not self.llm:
            # Simple heuristic: if query contains entity names, use local
            # Otherwise use global
            if len(query.split()) < 5:
                return "local"
            return "global"
        
        classification_prompt = f"""
Phân loại câu hỏi sau:
- "local": Câu hỏi cụ thể về một thực thể/topic cụ thể
- "global": Câu hỏi tổng quan, so sánh, hoặc liên quan đến nhiều topics

Câu hỏi: {query}

Trả về chỉ một từ: "local" hoặc "global"
"""
        
        try:
            result = await self.llm(classification_prompt)
            return result.output.strip().lower()
        except:
            return "local"  # Default to local
    
    async def search(self, query: str, **kwargs):
        """Search using hybrid approach."""
        query_type = await self.classify_query(query)
        
        if query_type == "global":
            return await self.global_search.asearch(query, **kwargs)
        else:
            return await self.local_search.asearch(query, **kwargs)


def enhance_response_with_metadata(
    response: str,
    context_data: Dict[str, pd.DataFrame],
    validation_score: Optional[Dict[str, Any]] = None
) -> str:
    """
    Enhance response with metadata, sources, and confidence.
    
    Args:
        response: Original response
        context_data: Context data used
        validation_score: Optional validation scores
        
    Returns:
        Enhanced response with metadata
    """
    enhanced = response
    
    # Add sources
    enhanced += format_sources_with_context(context_data)
    
    # Add confidence if available
    if validation_score and validation_score.get("overall_score", -1) >= 0:
        score = validation_score["overall_score"]
        confidence = "Cao" if score >= 8 else "Trung bình" if score >= 5 else "Thấp"
        enhanced += f"\n\n✅ Độ tin cậy: {confidence} ({score:.1f}/10)"
        
        if validation_score.get("issues"):
            enhanced += f"\n⚠️ Lưu ý: {', '.join(validation_score['issues'][:2])}"
    
    return enhanced


async def search_with_fallback(
    query: str,
    local_search,
    global_search,
    max_retries: int = 3
):
    """
    Search with fallback strategy.
    
    Args:
        query: User question
        local_search: Local search instance
        global_search: Global search instance
        max_retries: Maximum retry attempts
        
    Returns:
        Search result with fallback handling
    """
    # Try local search first
    try:
        result = await local_search.asearch(query)
        
        # Check if result is meaningful (has entities/context)
        if result.context_data and len(result.context_data.get("entities", [])) > 0:
            return result
        
        # If no entities found, fallback to global
        raise ValueError("No entities found in local search")
        
    except Exception as e:
        print(f"Local search failed: {e}, trying global search...")
        
        # Fallback to global search
        try:
            return await global_search.asearch(query)
        except Exception as e2:
            # Final fallback: return a helpful error message
            from graphrag.query.structured_search.base import SearchResult
            return SearchResult(
                response="Xin lỗi, tôi không thể tìm thấy thông tin về câu hỏi này trong tài liệu. Vui lòng thử lại với câu hỏi khác hoặc diễn đạt lại câu hỏi.",
                context_data={},
                prompt_tokens=0,
                completion_tokens=0,
            )


def expand_vietnamese_query(query: str) -> str:
    """
    Expand query with Vietnamese synonyms (simple implementation).
    
    Args:
        query: Original query
        
    Returns:
        Expanded query
    """
    # Simple synonym expansion (you could use a Vietnamese wordnet or embedding-based expansion)
    synonyms = {
        "thời gian": ["giờ", "lúc", "khung giờ"],
        "phí": ["chi phí", "giá", "lệ phí"],
        "giao dịch": ["mua bán", "trao đổi", "thực hiện"],
        "chứng khoán": ["cổ phiếu", "trái phiếu"],
    }
    
    expanded_terms = []
    words = query.lower().split()
    
    for word in words:
        expanded_terms.append(word)
        if word in synonyms:
            expanded_terms.extend(synonyms[word][:1])  # Add first synonym
    
    return " ".join(expanded_terms)

