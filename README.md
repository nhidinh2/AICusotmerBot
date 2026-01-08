# GraphRAG Q&A System - AICustomerBot

Intelligent question-answering system based on GraphRAG (Graph-based Retrieval Augmented Generation) that allows asking questions in Vietnamese and receiving answers based on indexed documents.

---

## Overview

This project uses Microsoft's GraphRAG to:
- Build knowledge graphs from text documents
- Extract entities, relationships, and claims from documents
- Support intelligent semantic search and querying
- Answer questions with clear source citations

## Features

- Automatic extraction of entities and relationships from documents
- Knowledge graph construction with embeddings
- Vietnamese question-answering
- Enhanced source citations with actual text excerpts
- Automatic fallback between local and global search
- Better error handling with user-friendly messages
- Optional graph visualization with Neo4j

## Requirements

- Python 3.10 or higher
- OpenAI API key (set in environment variable `GRAPHRAG_API_KEY`)
- Poetry (for dependency management)
- Text documents (.txt) for indexing

## Installation

### 1. Clone repository

```bash
git clone <repository-url>
cd AICusotmerBot
```

### 2. Install dependencies

```bash
# Install Poetry if not already installed
python -m pip install --user pipx
python -m pipx install poetry

# Install packages
poetry install
```

### 3. Set environment variable

```bash
export GRAPHRAG_API_KEY='your-openai-api-key-here'
```

Or create a `.env` file:
```
GRAPHRAG_API_KEY=your-openai-api-key-here
```

### 4. Prepare documents

Place your document files (.txt) in the `input/` directory:

```bash
mkdir -p input
# Copy your documents into the input/ directory
```

## View Actual Results

There are several ways to see the system in action and the actual results it produces:

1. **View Pre-run Results**: See the `examples/ACTUAL_RESULTS.md` file to view actual questions and answers from the system. These are real results, not hypothetical examples.

2. **Run Web Application**: If you already have indexed data, you can run the web application to query the system:
   ```bash
   # Install streamlit (if not already installed)
   poetry add streamlit pandas
   
   # Run the application
   streamlit run demo_app.py
   ```
   The application will open in your browser at `http://localhost:8501` where you can ask real questions and receive answers from the system.

3. **Run Notebook**: Open `COMPLETE_WORKFLOW.ipynb` in Jupyter Notebook to see the complete workflow and run actual queries.

## Usage

### Quick Start

Open the `COMPLETE_WORKFLOW.ipynb` file in Jupyter Notebook and run all cells.

### Detailed Process

#### Step 1: Setup

Run the cells in Section 1 to check your environment and configuration.

#### Step 2: Indexing (Run once)

Run Section 2 to build the knowledge graph from documents:
- Uncomment the `run_indexing()` line in the indexing cell
- This process takes 10-30 minutes depending on document size
- Results are saved in the `output/` directory

Note: Only need to run this step once or when you have new documents.

#### Step 3: Querying

Run Section 3 to:
- Load the indexed knowledge graph
- Set up search engines
- Ask questions and receive answers

Example:
```python
question = "What are the trading hours for government bonds at the Hanoi Stock Exchange?"
result = await ask_question(question)
```

#### Step 4: Visualization (Optional)

Run Section 4 if you want to visualize the knowledge graph with Neo4j.

## Project Structure

```
AICusotmerBot/
├── COMPLETE_WORKFLOW.ipynb    # Main notebook containing complete workflow
├── utils/                      # Improvement utilities
│   ├── qa_improvements.py     # QA improvement functions
│   └── evaluation.py          # System evaluation framework
├── examples/                   # Actual results
│   ├── ACTUAL_RESULTS.md      # Actual results - questions and answers from system
│   └── README.md              # Guide to view results
├── demo_app.py                # Web application to query the system (Streamlit)
├── input/                      # Directory containing input documents
│   └── book.txt
├── output/                     # Indexing results
│   └── YYYYMMDD-HHMMSS/
│       └── artifacts/
├── cache/                      # Cache for processing
├── prompts/                    # Prompt templates
│   ├── entity_extraction.txt
│   ├── claim_extraction.txt
│   └── ...
├── settings.yaml               # Configuration file
├── pyproject.toml              # Poetry configuration and dependencies
└── graphrag/                   # GraphRAG library (source code)
```

## Configuration

Edit the `settings.yaml` file to customize:
- LLM model (GPT-3.5, GPT-4, etc.)
- Embedding model
- Entity extraction parameters
- Parallelization configuration

Example upgrading to GPT-4:
```yaml
llm:
  model: gpt-4-turbo-preview  # Change from gpt-3.5-turbo-0125
```

## Integrated Improvements

The system includes the following improvements (automatically enabled when `utils/qa_improvements.py` is available):

1. **Enhanced source citations**: Display actual text excerpts from sources
2. **Automatic fallback**: Automatically switch from local to global search if needed
3. **Better error handling**: User-friendly error messages
4. **Response formatting**: Clear response structure with metadata

## Usage Examples

### Ask a question

```python
# In notebook
question = "What are the trading fees at MBS?"
result = await ask_question(question)
```

### Use search directly

```python
# Local search (for specific questions)
result = await local_search.asearch("Your question")

# Global search (for broad topics)
result = await global_search.asearch("Your question")
```

## Troubleshooting

### Indexing errors

- Check OpenAI API key: `echo $GRAPHRAG_API_KEY`
- Check input files in the `input/` directory
- Check remaining OpenAI API credits

### Query errors

- Verify indexing completed successfully
- Check that the `output/` directory has data
- Update `INPUT_DIR` in the notebook if needed

### Improvements not working

- Check that `utils/qa_improvements.py` exists
- Check if import works: `from utils.qa_improvements import *`
- System will automatically fallback to standard mode if improvements are not available

## View Actual Results

Read the `examples/ACTUAL_RESULTS.md` file to view actual questions and answers from the system. These are real results from the system query process.

## References

- [GraphRAG Documentation](https://github.com/microsoft/graphrag)
- [GraphRAG Research Paper](https://arxiv.org/abs/2408.16130)
- [OpenAI API Documentation](https://platform.openai.com/docs)

## License

This project uses the MIT license. See the LICENSE file for more details.

## Author

This project is based on Microsoft's GraphRAG and customized for Vietnamese question-answering system.

---

# Hệ Thống Hỏi Đáp GraphRAG - AICustomerBot

Hệ thống hỏi đáp thông minh dựa trên GraphRAG (Graph-based Retrieval Augmented Generation) cho phép đặt câu hỏi bằng tiếng Việt và nhận câu trả lời dựa trên tài liệu đã được lập chỉ mục.

---

## Tổng Quan

Dự án này sử dụng GraphRAG của Microsoft để:
- Xây dựng đồ thị tri thức từ tài liệu văn bản
- Trích xuất các thực thể, mối quan hệ và claims từ tài liệu
- Hỗ trợ tìm kiếm và truy vấn ngữ nghĩa thông minh
- Trả lời câu hỏi với trích dẫn nguồn rõ ràng

## Tính Năng

- Tự động trích xuất thực thể và mối quan hệ từ tài liệu
- Xây dựng đồ thị tri thức với embeddings
- Hỏi đáp bằng tiếng Việt
- Trích dẫn nguồn nâng cao với đoạn văn bản
- Tự động fallback giữa tìm kiếm cục bộ và toàn cục
- Xử lý lỗi tốt với thông báo thân thiện
- Hỗ trợ trực quan hóa đồ thị với Neo4j (tùy chọn)

## Yêu Cầu

- Python 3.10 trở lên
- Khóa API OpenAI (đặt trong biến môi trường `GRAPHRAG_API_KEY`)
- Poetry (để quản lý dependencies)
- Tài liệu văn bản (.txt) để lập chỉ mục

## Cài Đặt

### 1. Clone repository

```bash
git clone <repository-url>
cd AICusotmerBot
```

### 2. Cài đặt dependencies

```bash
# Cài đặt Poetry nếu chưa có
python -m pip install --user pipx
python -m pipx install poetry

# Cài đặt các package
poetry install
```

### 3. Thiết lập biến môi trường

```bash
export GRAPHRAG_API_KEY='your-openai-api-key-here'
```

Hoặc tạo file `.env`:
```
GRAPHRAG_API_KEY=your-openai-api-key-here
```

### 4. Chuẩn bị tài liệu

Đặt các file tài liệu (.txt) vào thư mục `input/`:

```bash
mkdir -p input
# Copy tài liệu của bạn vào thư mục input/
```

## Xem Kết Quả Thực Tế

Có nhiều cách để xem hệ thống hoạt động và các kết quả thực tế mà nó tạo ra:

1. **Xem Kết Quả Đã Chạy**: Xem file `examples/ACTUAL_RESULTS.md` để xem các câu hỏi và câu trả lời thực tế từ hệ thống. Đây là kết quả thực sự, không phải ví dụ giả định.

2. **Chạy Ứng Dụng Web**: Nếu bạn đã có dữ liệu đã lập chỉ mục, bạn có thể chạy ứng dụng web để truy vấn hệ thống:
   ```bash
   # Cài đặt streamlit (nếu chưa có)
   poetry add streamlit pandas
   
   # Chạy ứng dụng
   streamlit run demo_app.py
   ```
   Ứng dụng sẽ mở trong trình duyệt tại `http://localhost:8501` nơi bạn có thể đặt câu hỏi thực tế và nhận câu trả lời từ hệ thống.

3. **Chạy Notebook**: Mở `COMPLETE_WORKFLOW.ipynb` trong Jupyter Notebook để xem quy trình đầy đủ và chạy các truy vấn thực tế.

## Sử Dụng

### Cách Nhanh Nhất

Mở file `COMPLETE_WORKFLOW.ipynb` trong Jupyter Notebook và chạy tất cả các cell.

### Quy Trình Chi Tiết

#### Bước 1: Thiết Lập

Chạy các cell trong Phần 1 để kiểm tra môi trường và cấu hình.

#### Bước 2: Lập Chỉ Mục (Chỉ chạy một lần)

Chạy Phần 2 để xây dựng đồ thị tri thức từ tài liệu:
- Bỏ comment dòng `run_indexing()` trong cell lập chỉ mục
- Quá trình này mất 10-30 phút tùy thuộc vào kích thước tài liệu
- Kết quả được lưu trong thư mục `output/`

Lưu ý: Chỉ cần chạy bước này một lần hoặc khi có tài liệu mới.

#### Bước 3: Truy Vấn

Chạy Phần 3 để:
- Tải đồ thị tri thức đã lập chỉ mục
- Thiết lập các công cụ tìm kiếm
- Đặt câu hỏi và nhận câu trả lời

Ví dụ:
```python
question = "Thời gian giao dịch trái phiếu chính phủ tại Sở Giao dịch Chứng khoán Hà Nội như thế nào?"
result = await ask_question(question)
```

#### Bước 4: Trực Quan Hóa (Tùy chọn)

Chạy Phần 4 nếu bạn muốn trực quan hóa đồ thị tri thức bằng Neo4j.

## Cấu Trúc Dự Án

```
AICusotmerBot/
├── COMPLETE_WORKFLOW.ipynb    # Notebook chính chứa toàn bộ quy trình
├── utils/                      # Các tiện ích cải tiến
│   ├── qa_improvements.py     # Các hàm cải tiến cho QA
│   └── evaluation.py          # Framework đánh giá hệ thống
├── examples/                   # Kết quả thực tế
│   ├── ACTUAL_RESULTS.md      # Kết quả thực tế - câu hỏi và câu trả lời từ hệ thống
│   └── README.md              # Hướng dẫn xem kết quả
├── demo_app.py                # Ứng dụng web để truy vấn hệ thống (Streamlit)
├── input/                      # Thư mục chứa tài liệu đầu vào
│   └── book.txt
├── output/                     # Kết quả lập chỉ mục
│   └── YYYYMMDD-HHMMSS/
│       └── artifacts/
├── cache/                      # Cache cho quá trình xử lý
├── prompts/                    # Các prompt templates
│   ├── entity_extraction.txt
│   ├── claim_extraction.txt
│   └── ...
├── settings.yaml               # File cấu hình
├── pyproject.toml              # Cấu hình Poetry và dependencies
└── graphrag/                   # Thư viện GraphRAG (source code)
```

## Cấu Hình

Chỉnh sửa file `settings.yaml` để tùy chỉnh:
- Mô hình LLM (GPT-3.5, GPT-4, etc.)
- Mô hình embedding
- Các tham số trích xuất thực thể
- Cấu hình parallelization

Ví dụ nâng cấp lên GPT-4:
```yaml
llm:
  model: gpt-4-turbo-preview  # Thay đổi từ gpt-3.5-turbo-0125
```

## Các Cải Tiến Đã Tích Hợp

Hệ thống đã bao gồm các cải tiến sau (tự động bật khi có `utils/qa_improvements.py`):

1. **Trích dẫn nguồn nâng cao**: Hiển thị các đoạn văn bản thực tế từ nguồn
2. **Fallback tự động**: Tự động chuyển từ tìm kiếm cục bộ sang toàn cục nếu cần
3. **Xử lý lỗi tốt hơn**: Thông báo lỗi thân thiện với người dùng
4. **Định dạng phản hồi**: Cấu trúc phản hồi rõ ràng với metadata

## Ví Dụ Sử Dụng

### Đặt một câu hỏi

```python
# Trong notebook
question = "Phí giao dịch chứng khoán tại MBS là bao nhiêu?"
result = await ask_question(question)
```

### Sử dụng tìm kiếm trực tiếp

```python
# Tìm kiếm cục bộ (cho câu hỏi cụ thể)
result = await local_search.asearch("Câu hỏi của bạn")

# Tìm kiếm toàn cục (cho chủ đề rộng)
result = await global_search.asearch("Câu hỏi của bạn")
```

## Khắc Phục Sự Cố

### Lỗi khi lập chỉ mục

- Kiểm tra khóa API OpenAI: `echo $GRAPHRAG_API_KEY`
- Kiểm tra file đầu vào trong thư mục `input/`
- Kiểm tra tín dụng API OpenAI còn lại

### Lỗi khi truy vấn

- Xác minh lập chỉ mục đã hoàn tất thành công
- Kiểm tra thư mục `output/` có dữ liệu
- Cập nhật `INPUT_DIR` trong notebook nếu cần

### Các cải tiến không hoạt động

- Kiểm tra file `utils/qa_improvements.py` tồn tại
- Kiểm tra có thể import: `from utils.qa_improvements import *`
- Hệ thống sẽ tự động fallback về chế độ tiêu chuẩn nếu không có cải tiến

## Xem Kết Quả Thực Tế

Đọc file `examples/ACTUAL_RESULTS.md` để xem các câu hỏi và câu trả lời thực tế từ hệ thống. Đây là kết quả thực sự từ quá trình truy vấn hệ thống.

## Tài Liệu Tham Khảo

- [GraphRAG Documentation](https://github.com/microsoft/graphrag)
- [GraphRAG Research Paper](https://arxiv.org/abs/2408.16130)
- [OpenAI API Documentation](https://platform.openai.com/docs)

## Giấy Phép

Dự án này sử dụng giấy phép MIT. Xem file LICENSE để biết thêm chi tiết.

## Tác Giả

Dự án này dựa trên GraphRAG của Microsoft và được tùy chỉnh cho hệ thống hỏi đáp tiếng Việt.
