import os
import zipfile

from tests.helpers.youtube_fakes import install_flow_import_stubs

install_flow_import_stubs()

from youtube import components


def test_deno_partial_file_is_not_ready(tmp_path, monkeypatch):
    deno = tmp_path / "deno.exe"
    deno.write_bytes(b"")
    monkeypatch.setattr(components, "DENO_EXE", str(deno))

    assert components.deno_readiness()["state"] != components.HELPER_READY
    assert not components.has_deno()


def test_atomic_deno_replacement_preserves_previous_valid_binary_on_failure(tmp_path, monkeypatch):
    old_deno = tmp_path / "deno.exe"
    old_deno.write_bytes(b"old-valid")
    broken_zip = tmp_path / "deno.zip"
    with zipfile.ZipFile(broken_zip, "w") as zf:
        zf.writestr("readme.txt", "no executable")
    monkeypatch.setattr(components, "APP_DIR", str(tmp_path))
    monkeypatch.setattr(components, "DENO_EXE", str(old_deno))

    try:
        components._extract_deno_zip(str(broken_zip), components.CancelFlag())
    except RuntimeError:
        pass

    assert old_deno.read_bytes() == b"old-valid"


def test_canceled_deno_setup_removes_temporary_files(tmp_path, monkeypatch):
    archive = tmp_path / "deno.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("deno.exe", b"new")
    monkeypatch.setattr(components, "APP_DIR", str(tmp_path))
    monkeypatch.setattr(components, "DENO_EXE", str(tmp_path / "deno.exe"))
    cancel = components.CancelFlag()
    cancel.set()

    try:
        components._extract_deno_zip(str(archive), cancel)
    except components.CancelledError:
        pass

    assert not list(tmp_path.glob("sap_deno_*.tmp"))
    assert not os.path.exists(components.DENO_EXE)


def test_missing_or_broken_helpers_produce_recovery_guidance(tmp_path, monkeypatch):
    monkeypatch.setattr(components, "YT_EXE", str(tmp_path / "yt-dlp.exe"))
    monkeypatch.setattr(components, "DENO_EXE", str(tmp_path / "deno.exe"))

    message = components.recovery_message()

    assert "YouTube components" in message
    assert "install" in message.lower() or "repair" in message.lower()
