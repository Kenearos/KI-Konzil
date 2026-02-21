"""
Tests for agent tools (web search and PDF reader).

All external API calls are mocked — no real calls to Tavily or ChromaDB.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch, MagicMock


class TestWebSearchTool:
    """Tests for the Tavily web search tool."""

    @patch.dict(os.environ, {"TAVILY_API_KEY": ""}, clear=False)
    def test_web_search_returns_error_without_api_key(self):
        from tools.web_search import web_search

        result = web_search.invoke({"query": "test query"})
        assert "TAVILY_API_KEY" in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}, clear=False)
    @patch("tools.web_search.TavilyClient")
    def test_web_search_returns_formatted_results(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {
                    "title": "Test Result",
                    "url": "https://example.com",
                    "content": "Some content here",
                }
            ]
        }
        mock_client_cls.return_value = mock_client

        from tools.web_search import web_search

        result = web_search.invoke({"query": "test query"})
        assert "Test Result" in result
        assert "https://example.com" in result
        assert "Some content here" in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}, clear=False)
    @patch("tools.web_search.TavilyClient")
    def test_web_search_handles_empty_results(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.search.return_value = {"results": []}
        mock_client_cls.return_value = mock_client

        from tools.web_search import web_search

        result = web_search.invoke({"query": "obscure query"})
        assert "No results" in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}, clear=False)
    @patch("tools.web_search.TavilyClient")
    def test_web_search_handles_api_error(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.search.side_effect = Exception("API rate limit")
        mock_client_cls.return_value = mock_client

        from tools.web_search import web_search

        result = web_search.invoke({"query": "test"})
        assert "Error" in result
        assert "rate limit" in result


class TestCreateWebSearchTool:
    """Tests for the web search tool factory."""

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}, clear=False)
    def test_factory_returns_tool_when_key_set(self):
        from tools.web_search import create_web_search_tool

        tool = create_web_search_tool()
        assert tool is not None

    @patch.dict(os.environ, {}, clear=True)
    def test_factory_returns_none_when_key_missing(self):
        from tools.web_search import create_web_search_tool

        tool = create_web_search_tool()
        assert tool is None


class TestPdfSearchTool:
    """Tests for the PDF reader tool."""

    @patch("tools.pdf_reader._get_chroma_collection")
    def test_pdf_search_empty_collection(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_get_collection.return_value = mock_collection

        from tools.pdf_reader import pdf_search

        result = pdf_search.invoke({"query": "test query"})
        assert "No documents" in result

    @patch("tools.pdf_reader._get_chroma_collection")
    def test_pdf_search_returns_results(self, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.count.return_value = 3
        mock_collection.query.return_value = {
            "documents": [["First passage about AI.", "Second passage about ML."]],
            "metadatas": [[
                {"source": "paper.pdf", "page": 1},
                {"source": "paper.pdf", "page": 3},
            ]],
        }
        mock_get_collection.return_value = mock_collection

        from tools.pdf_reader import pdf_search

        result = pdf_search.invoke({"query": "AI concepts"})
        assert "paper.pdf" in result
        assert "First passage" in result
        assert "Page 1" in result

    @patch("tools.pdf_reader._get_chroma_collection")
    def test_pdf_search_handles_error(self, mock_get_collection):
        mock_get_collection.side_effect = Exception("ChromaDB unavailable")

        from tools.pdf_reader import pdf_search

        result = pdf_search.invoke({"query": "test"})
        assert "Error" in result


class TestPdfIngestion:
    """Tests for PDF ingestion into ChromaDB."""

    @patch("tools.pdf_reader._get_chroma_collection")
    @patch("tools.pdf_reader.PdfReader")
    def test_ingest_pdf_processes_pages(self, mock_pdf_reader_cls, mock_get_collection):
        # Mock PDF with 2 pages of text
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "This is the first page with some content " * 20
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Second page about machine learning " * 20
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader_cls.return_value = mock_reader

        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        from tools.pdf_reader import ingest_pdf

        chunks = ingest_pdf("/tmp/test.pdf")
        assert chunks > 0
        mock_collection.upsert.assert_called_once()

    @patch("tools.pdf_reader._get_chroma_collection")
    @patch("tools.pdf_reader.PdfReader")
    def test_ingest_pdf_empty_file(self, mock_pdf_reader_cls, mock_get_collection):
        mock_reader = MagicMock()
        mock_reader.pages = []
        mock_pdf_reader_cls.return_value = mock_reader

        from tools.pdf_reader import ingest_pdf

        chunks = ingest_pdf("/tmp/empty.pdf")
        assert chunks == 0
