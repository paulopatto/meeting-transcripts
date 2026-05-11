from unittest.mock import MagicMock

import pytest

from src.tldv import tldv_check


class TestTldvClientGet:

    def test_success(self, mocker):
        mock_resp = mocker.MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"data": "ok"}'
        mock_resp.json.return_value = {"data": "ok"}
        mock_resp.headers = {"content-type": "application/json"}

        mock_session_get = mocker.patch("requests.Session.get", return_value=mock_resp)

        client = tldv_check.TldvClient("test-api-key")
        result = client.get("/meetings")

        assert result["status"] == 200
        assert result["body"] == {"data": "ok"}
        mock_session_get.assert_called_once()


class TestCheckApiAccess:

    def test_invalid_api_key_returns_false(self, mocker):
        mock_get = mocker.patch.object(tldv_check.TldvClient, "get")
        mock_get.return_value = {
            "status": 401,
            "body": {"error": "Unauthorized"},
            "headers": {},
        }

        mocker.patch.object(tldv_check.console, "print")
        mocker.patch.object(tldv_check.console, "rule")

        client = tldv_check.TldvClient("invalid-key")
        result = tldv_check.check_api_access(client)

        assert result is False


class TestListMeetings:

    def test_returns_list(self, mocker):
        meetings_data = {
            "meetings": [
                {
                    "id": "meeting-1",
                    "title": "Test Meeting",
                    "duration": 3600,
                    "startedAt": "2024-01-01T00:00:00Z",
                    "attendeesCount": 3,
                }
            ]
        }

        mock_get = mocker.patch.object(tldv_check.TldvClient, "get")
        mock_get.return_value = {
            "status": 200,
            "body": meetings_data,
            "headers": {},
        }

        mocker.patch.object(tldv_check.console, "print")
        mocker.patch.object(tldv_check.console, "rule")

        client = tldv_check.TldvClient("test-key")
        meetings = tldv_check.list_meetings(client)

        assert len(meetings) == 1
        assert meetings[0]["id"] == "meeting-1"


class TestGetTranscript:

    def test_transcript_available_saves_file(self, mocker):
        transcript_text = "Speaker A: Hello\nSpeaker B: Hi there"

        mock_get = mocker.patch.object(tldv_check.TldvClient, "get")
        mock_get.return_value = {
            "status": 200,
            "body": {"transcript": transcript_text},
            "headers": {},
        }

        mocker.patch.object(tldv_check.console, "print")
        mocker.patch.object(tldv_check.console, "rule")

        mock_open = mocker.mock_open()
        mocker.patch("builtins.open", mock_open)

        client = tldv_check.TldvClient("test-key")
        tldv_check.get_transcript(client, "test-meeting")

        mock_open.assert_called_once_with(
            "transcript_test-meeting.txt", "w", encoding="utf-8"
        )
        mock_open().write.assert_called_once_with(transcript_text)
