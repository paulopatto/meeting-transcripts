import sys
from unittest.mock import MagicMock, call

import pytest

from src.teams import teams_check


class TestAuthenticate:

    def test_missing_client_id_exits(self):
        original_client_id = teams_check.CLIENT_ID
        teams_check.CLIENT_ID = ""
        mock_print = MagicMock()
        original_print = teams_check.console.print
        teams_check.console.print = mock_print

        try:
            with pytest.raises(SystemExit) as exc:
                teams_check.authenticate()
            assert exc.value.code == 1
            mock_print.assert_any_call(
                "[bold red]❌ TEAMS_CLIENT_ID não configurado no .env[/bold red]"
            )
        finally:
            teams_check.CLIENT_ID = original_client_id
            teams_check.console.print = original_print

    def test_device_code_flow_success(self, mocker):
        mocker.patch.object(teams_check, "CLIENT_ID", "test-client-id")
        mocker.patch.object(teams_check, "load_cached_token", return_value=None)
        mocker.patch.object(teams_check.console, "print")
        mocker.patch.object(
            teams_check.console, "status", return_value=mocker.MagicMock()
        )
        mocker.patch("src.teams.teams_check.time.sleep")
        mocker.patch("src.teams.teams_check.webbrowser.open")

        mock_device_code = mocker.MagicMock()
        mock_device_code.status_code = 200
        mock_device_code.json.return_value = {
            "device_code": "dev123",
            "user_code": "ABC123",
            "verification_uri": "https://microsoft.com/link",
            "interval": 2,
            "expires_in": 900,
        }

        mock_token_resp = mocker.MagicMock()
        mock_token_resp.status_code = 200
        mock_token_resp.json.return_value = {
            "access_token": "test-access-token",
            "expires_in": 3600,
            "refresh_token": "refresh123",
        }

        mock_post = mocker.patch("src.teams.teams_check.requests.post")
        mock_post.side_effect = [mock_device_code, mock_token_resp]

        token = teams_check.authenticate()

        assert token == "test-access-token"
        assert mock_post.call_count == 2


class TestGraphGet:

    def test_success(self, mocker):
        mock_resp = mocker.MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"value": []}'
        mock_resp.json.return_value = {"value": []}

        mocker.patch("src.teams.teams_check.requests.get", return_value=mock_resp)

        result = teams_check.graph_get("fake-token", "/me/onlineMeetings")

        assert result["status"] == 200
        assert result["body"] == {"value": []}

    def test_error_403(self, mocker):
        mock_resp = mocker.MagicMock()
        mock_resp.status_code = 403
        mock_resp.content = b'{"error": {"code": "Forbidden"}}'
        mock_resp.json.return_value = {"error": {"code": "Forbidden"}}

        mocker.patch("src.teams.teams_check.requests.get", return_value=mock_resp)

        result = teams_check.graph_get("fake-token", "/me/onlineMeetings")

        assert result["status"] == 403


class TestListMyMeetings:

    def test_empty_list(self, mocker):
        mock_print = mocker.MagicMock()
        mocker.patch.object(teams_check.console, "print", mock_print)
        mocker.patch.object(teams_check.console, "rule")

        mock_resp = mocker.MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b'{"value": []}'
        mock_resp.json.return_value = {"value": []}

        mocker.patch("src.teams.teams_check.requests.get", return_value=mock_resp)

        teams_check.list_my_meetings("fake-token")

        printed_texts = [str(a[0]) for a in mock_print.call_args_list if a[0]]
        assert any("Nenhuma reunião encontrada" in t for t in printed_texts)
