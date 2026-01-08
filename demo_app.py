"""
Ứng Dụng Web Hỏi Đáp GraphRAG

Giao diện web để truy vấn hệ thống hỏi đáp GraphRAG.
Chạy: streamlit run demo_app.py

Lưu ý: Cần chạy notebook COMPLETE_WORKFLOW.ipynb phần 2 (Lập Chỉ Mục) trước để có dữ liệu đã lập chỉ mục.
"""

import os
import sys
import asyncio
import glob
import pandas as pd
import tiktoken
from pathlib import Path

# Thêm đường dẫn vào sys.path
sys.path.append('utils')

import streamlit as st
from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.query.indexer_adapters import (
    read_indexer_covariates,
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.input.loaders.dfs import store_entity_semantic_embeddings
from graphrag.query.llm.oai.chat_openai import ChatOpenAI
from graphrag.query.llm.oai.embedding import OpenAIEmbedding
from graphrag.query.llm.oai.typing import OpenaiApiType
from graphrag.query.structured_search.local_search.mixed_context import LocalSearchMixedContext
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag.query.structured_search.global_search.search import GlobalSearch
from graphrag.query.structured_search.global_search.community_context import GlobalCommunityContext
from graphrag.vector_stores.lancedb import LanceDBVectorStore

# Import các tiện ích cải tiến
try:
    from qa_improvements import (
        enhance_response_with_metadata,
        search_with_fallback,
        HybridSearch,
    )
    IMPROVEMENTS_AVAILABLE = True
except ImportError:
    IMPROVEMENTS_AVAILABLE = False


# Cấu hình trang
st.set_page_config(
    page_title="Hệ Thống Hỏi Đáp GraphRAG",
    page_icon="",
    layout="wide"
)

# Tiêu đề
st.title("Hệ Thống Hỏi Đáp GraphRAG")
st.markdown("Hệ thống hỏi đáp thông minh dựa trên đồ thị tri thức. Đặt câu hỏi bằng tiếng Việt và nhận câu trả lời thực tế với trích dẫn nguồn từ tài liệu đã lập chỉ mục.")


@st.cache_resource
def load_search_system():
    """Tải và khởi tạo hệ thống tìm kiếm."""
    try:
        # Tự động tìm thư mục output mới nhất
        output_dirs = sorted(glob.glob("output/*/"), key=os.path.getctime, reverse=True)
        if not output_dirs:
            return None, "Không tìm thấy dữ liệu đã lập chỉ mục. Vui lòng chạy COMPLETE_WORKFLOW.ipynb phần 2 trước."
        
        INPUT_DIR = f"{output_dirs[0]}artifacts/"
        
        if not os.path.exists(INPUT_DIR):
            return None, f"Thư mục đầu vào không tồn tại: {INPUT_DIR}"
        
        # Kiểm tra API key
        api_key = os.environ.get("GRAPHRAG_API_KEY")
        if not api_key:
            return None, "Khóa API OpenAI chưa được đặt. Vui lòng đặt biến môi trường GRAPHRAG_API_KEY."
        
        LANCEDB_URI = f"{INPUT_DIR}/lancedb"
        
        # Định nghĩa tên bảng
        COMMUNITY_REPORT_TABLE = "create_final_community_reports"
        ENTITY_TABLE = "create_final_nodes"
        ENTITY_EMBEDDING_TABLE = "create_final_entities"
        RELATIONSHIP_TABLE = "create_final_relationships"
        COVARIATE_TABLE = "create_final_covariates"
        TEXT_UNIT_TABLE = "create_final_text_units"
        COMMUNITY_LEVEL = 2
        
        # Tải dữ liệu
        entity_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_TABLE}.parquet")
        entity_embedding_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_EMBEDDING_TABLE}.parquet")
        entities = read_indexer_entities(entity_df, entity_embedding_df, COMMUNITY_LEVEL)
        
        relationship_df = pd.read_parquet(f"{INPUT_DIR}/{RELATIONSHIP_TABLE}.parquet")
        relationships = read_indexer_relationships(relationship_df)
        
        covariate_df = pd.read_parquet(f"{INPUT_DIR}/{COVARIATE_TABLE}.parquet")
        claims = read_indexer_covariates(covariate_df)
        covariates = {"claims": claims}
        
        report_df = pd.read_parquet(f"{INPUT_DIR}/{COMMUNITY_REPORT_TABLE}.parquet")
        reports = read_indexer_reports(report_df, entity_df, COMMUNITY_LEVEL)
        
        text_unit_df = pd.read_parquet(f"{INPUT_DIR}/{TEXT_UNIT_TABLE}.parquet")
        text_units = read_indexer_text_units(text_unit_df)
        
        # Thiết lập embeddings
        description_embedding_store = LanceDBVectorStore(
            collection_name="entity_description_embeddings",
        )
        description_embedding_store.connect(db_uri=LANCEDB_URI)
        store_entity_semantic_embeddings(
            entities=entities, vectorstore=description_embedding_store
        )
        
        # Thiết lập LLM
        llm_model = "gpt-3.5-turbo-0125"
        embedding_model = "text-embedding-3-small"
        
        llm = ChatOpenAI(
            api_key=api_key,
            model=llm_model,
            api_type=OpenaiApiType.OpenAI,
            max_retries=20,
        )
        
        token_encoder = tiktoken.get_encoding("cl100k_base")
        
        text_embedder = OpenAIEmbedding(
            api_key=api_key,
            api_base=None,
            api_type=OpenaiApiType.OpenAI,
            model=embedding_model,
            deployment_name=embedding_model,
            max_retries=20,
        )
        
        # Tạo context builders
        local_context_builder = LocalSearchMixedContext(
            community_reports=reports,
            text_units=text_units,
            entities=entities,
            relationships=relationships,
            covariates=covariates,
            entity_text_embeddings=description_embedding_store,
            embedding_vectorstore_key=EntityVectorStoreKey.ID,
            text_embedder=text_embedder,
            token_encoder=token_encoder,
        )
        
        global_context_builder = GlobalCommunityContext(
            community_reports=reports,
            entities=entities,
            token_encoder=token_encoder,
        )
        
        # Cấu hình tham số
        local_context_params = {
            "text_unit_prop": 0.5,
            "community_prop": 0.1,
            "conversation_history_max_turns": 5,
            "conversation_history_user_turns_only": True,
            "top_k_mapped_entities": 10,
            "top_k_relationships": 10,
            "include_entity_rank": True,
            "include_relationship_weight": True,
            "include_community_rank": False,
            "return_candidate_context": False,
            "embedding_vectorstore_key": EntityVectorStoreKey.ID,
            "max_tokens": 12_000,
        }
        
        llm_params = {
            "max_tokens": 2_000,
            "temperature": 0.0,
        }
        
        # Tạo search engines
        local_search = LocalSearch(
            llm=llm,
            context_builder=local_context_builder,
            token_encoder=token_encoder,
            llm_params=llm_params,
            context_builder_params=local_context_params,
            response_type="multiple paragraphs",
        )
        
        global_search = GlobalSearch(
            llm=llm,
            context_builder=global_context_builder,
            token_encoder=token_encoder,
            llm_params=llm_params,
            response_type="multiple paragraphs",
        )
        
        # Tạo hybrid search nếu có cải tiến
        if IMPROVEMENTS_AVAILABLE:
            hybrid_search = HybridSearch(local_search, global_search, llm)
        else:
            hybrid_search = local_search
        
        stats = {
            "entities": len(entity_df),
            "relationships": len(relationship_df),
            "claims": len(claims),
            "reports": len(report_df),
            "text_units": len(text_unit_df),
            "input_dir": INPUT_DIR,
        }
        
        return (local_search, global_search, hybrid_search, stats), None
        
    except Exception as e:
        return None, f"Lỗi khi tải hệ thống: {str(e)}"


def main():
    # Sidebar với thông tin
    with st.sidebar:
        st.header("Thông Tin Hệ Thống")
        
        # Thống kê nếu đã load
        if 'system_loaded' not in st.session_state:
            st.info("Đang tải hệ thống...")
        else:
            if st.session_state.system_loaded:
                stats = st.session_state.stats
                st.success("Hệ thống đã sẵn sàng!")
                st.metric("Thực thể", stats["entities"])
                st.metric("Mối quan hệ", stats["relationships"])
                st.metric("Khẳng định", stats["claims"])
                st.metric("Báo cáo cộng đồng", stats["reports"])
                st.metric("Đơn vị văn bản", stats["text_units"])
            else:
                st.error(st.session_state.error_message)
        
        st.markdown("---")
        st.markdown("### Cải Tiến")
        if IMPROVEMENTS_AVAILABLE:
            st.success("Các cải tiến đã được bật")
        else:
            st.warning("Chế độ tiêu chuẩn (không có cải tiến)")
        
        st.markdown("---")
        st.markdown("### Ví Dụ Câu Hỏi")
        example_questions = [
            "Thời gian giao dịch trái phiếu chính phủ tại Sở Giao dịch Chứng khoán Hà Nội như thế nào?",
            "Phí giao dịch chứng khoán tại MBS là bao nhiêu?",
            "MBS cung cấp những dịch vụ gì?",
            "Có thể giao dịch cổ phiếu lô lẻ tại MBS không?",
            "Những rủi ro nào có thể phát sinh từ giao dịch trực tuyến?",
        ]
        
        for i, q in enumerate(example_questions, 1):
            if st.button(f"Ví dụ {i}", key=f"example_{i}"):
                st.session_state.example_question = q
    
    # Tải hệ thống (chỉ một lần)
    if 'system_loaded' not in st.session_state:
        with st.spinner("Đang tải hệ thống tìm kiếm..."):
            result, error = load_search_system()
            if error:
                st.session_state.system_loaded = False
                st.session_state.error_message = error
            else:
                local_search, global_search, hybrid_search, stats = result
                st.session_state.local_search = local_search
                st.session_state.global_search = global_search
                st.session_state.hybrid_search = hybrid_search
                st.session_state.stats = stats
                st.session_state.system_loaded = True
        
        # Reload để cập nhật sidebar
        if st.session_state.system_loaded:
            st.rerun()
    
    # Main content area
    if not st.session_state.system_loaded:
        st.error(f"**Không thể tải hệ thống:** {st.session_state.error_message}")
        st.info("""
        **Hướng dẫn khắc phục:**
        1. Đảm bảo đã chạy COMPLETE_WORKFLOW.ipynb phần 2 (Lập chỉ mục)
        2. Kiểm tra biến môi trường GRAPHRAG_API_KEY đã được đặt
        3. Kiểm tra thư mục output/ có dữ liệu
        """)
        return
    
    # Form nhập câu hỏi
    st.header("Đặt Câu Hỏi")
    
    # Sử dụng câu hỏi ví dụ nếu có
    default_question = st.session_state.get('example_question', '')
    if default_question:
        del st.session_state.example_question
    
    question = st.text_area(
        "Nhập câu hỏi của bạn (bằng tiếng Việt):",
        value=default_question,
        height=100,
        placeholder="Ví dụ: Thời gian giao dịch trái phiếu chính phủ tại Sở Giao dịch Chứng khoán Hà Nội như thế nào?"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        search_button = st.button("Tìm Kiếm", type="primary", use_container_width=True)
    
    with col2:
        search_mode = st.radio(
            "Chế độ tìm kiếm:",
            ["Tự động (Hybrid)", "Cục bộ (Local)", "Toàn cục (Global)"],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    # Xử lý tìm kiếm
    if search_button and question:
        with st.spinner("Đang tìm kiếm và tạo câu trả lời..."):
            try:
                # Chọn search engine
                if search_mode == "Tự động (Hybrid)" and IMPROVEMENTS_AVAILABLE:
                    result = asyncio.run(
                        search_with_fallback(
                            question,
                            st.session_state.local_search,
                            st.session_state.global_search
                        )
                    )
                    enhanced_response = enhance_response_with_metadata(
                        result.response,
                        result.context_data,
                    )
                elif search_mode == "Cục bộ (Local)":
                    result = asyncio.run(
                        st.session_state.local_search.asearch(question)
                    )
                    if IMPROVEMENTS_AVAILABLE:
                        enhanced_response = enhance_response_with_metadata(
                            result.response,
                            result.context_data,
                        )
                    else:
                        enhanced_response = result.response
                else:  # Global
                    result = asyncio.run(
                        st.session_state.global_search.asearch(question)
                    )
                    enhanced_response = result.response
                
                # Hiển thị kết quả
                st.markdown("### Câu Trả Lời")
                st.markdown("---")
                st.markdown(enhanced_response)
                
                # Hiển thị metadata
                if IMPROVEMENTS_AVAILABLE and hasattr(result, 'context_data'):
                    with st.expander("Thông tin chi tiết về nguồn"):
                        if 'entities' in result.context_data:
                            st.markdown(f"**Thực thể liên quan:** {len(result.context_data['entities'])}")
                        if 'relationships' in result.context_data:
                            st.markdown(f"**Mối quan hệ:** {len(result.context_data['relationships'])}")
                        if 'sources' in result.context_data:
                            st.markdown(f"**Nguồn văn bản:** {len(result.context_data['sources'])}")
                            if len(result.context_data['sources']) > 0:
                                st.markdown("**Các đoạn văn bản tham khảo:**")
                                for idx, row in result.context_data['sources'].head(5).iterrows():
                                    st.text_area(
                                        f"Nguồn {idx}",
                                        value=row['text'][:500] + "..." if len(row['text']) > 500 else row['text'],
                                        height=100,
                                        key=f"source_{idx}",
                                        disabled=True
                                    )
                
            except Exception as e:
                st.error(f"Lỗi khi tìm kiếm: {str(e)}")
                import traceback
                with st.expander("Chi tiết lỗi"):
                    st.code(traceback.format_exc())
    
    elif search_button and not question:
        st.warning("Vui lòng nhập câu hỏi trước khi tìm kiếm.")
    
    # Thông tin thêm
    st.markdown("---")
    with st.expander("Về hệ thống này"):
        st.markdown("""
        **Hệ Thống Hỏi Đáp GraphRAG** sử dụng đồ thị tri thức để trả lời câu hỏi.
        
        - **Tìm kiếm Cục bộ**: Tìm kiếm dựa trên các thực thể cụ thể trong đồ thị
        - **Tìm kiếm Toàn cục**: Tìm kiếm dựa trên các báo cáo cộng đồng
        - **Tìm kiếm Tự động**: Tự động chọn phương pháp tốt nhất
        
        Hệ thống đã được cải tiến với:
        - Trích dẫn nguồn nâng cao
        - Xử lý fallback tự động
        - Định dạng phản hồi tốt hơn
        """)


if __name__ == "__main__":
    main()

