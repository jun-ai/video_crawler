"""发音评测失败语义：无真实结果时不得伪造固定分数。"""
import pytest


@pytest.mark.asyncio
async def test_speech_recognized_but_evaluation_unavailable_has_no_score(
    client, auth_headers, monkeypatch
):
    import app.routers.learning as learning

    monkeypatch.setattr(learning, "check_ffmpeg_available", lambda: True)

    async def fake_convert(_audio):
        return b"wav"

    async def fake_recognize(*_args, **_kwargs):
        return {"success": True, "text": "hello world", "confidence": 0.91}

    async def fail_evaluation(*_args, **_kwargs):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(learning, "convert_webm_to_wav", fake_convert)
    monkeypatch.setattr(learning.speech_service, "recognize_audio", fake_recognize)
    monkeypatch.setattr(learning, "ai_evaluate_pronunciation", fail_evaluation)

    response = await client.post(
        "/api/learning/speech/recognize",
        headers=auth_headers,
        files={"audio": ("recording.webm", b"audio", "audio/webm")},
        data={"expected_text": "hello world"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["recognized_text"] == "hello world"
    assert body["pronunciation_result"] is None
    assert "暂时不可用" in body["error"]


@pytest.mark.asyncio
async def test_direct_pronunciation_unavailable_returns_503(
    client, auth_headers, monkeypatch
):
    import app.routers.learning as learning

    async def fail_evaluation(*_args, **_kwargs):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(learning, "ai_evaluate_pronunciation", fail_evaluation)
    response = await client.post(
        "/api/learning/pronunciation/evaluate",
        headers=auth_headers,
        json={"spoken_text": "hello", "expected_text": "hello"},
    )
    assert response.status_code == 503
    assert "暂时不可用" in response.json()["detail"]