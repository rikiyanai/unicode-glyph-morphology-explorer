from contextlib import redirect_stdout
from email.message import Message
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import artwork_workflow_audit as audit


class Capture(unittest.TestCase):
    def fetch_fixture(self, raw, content_type):
        class Response(io.BytesIO):
            url = "https://example.org/source"
            status = 200
            headers = Message()
        Response.headers["Content-Type"] = content_type
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(audit, "ROOT", root), patch.object(audit, "WORK", root / ".run"), \
                 patch.object(audit.urllib.request, "urlopen", return_value=Response(raw)), \
                 redirect_stdout(io.StringIO()):
                audit.fetch("fixture=https://example.org/source")
            receipt = json.loads((root / ".run/fixture.json").read_text())
            self.assertNotIn("error", receipt)
            self.assertEqual((root / ".run/fixture.raw").read_bytes(), raw)
            return (root / ".run/fixture.txt").read_text(), receipt

    def test_plain_mlt_keeps_angle_brackets_and_literal_entities(self):
        source = "[SPLIT]\nγ⌒ヽ ヾ<:;_ &#8202;\n乂__ノ\n"
        text, receipt = self.fetch_fixture(source.encode("cp932"), "text/plain; charset=UTF-8")
        self.assertEqual(text, source)
        self.assertEqual(receipt["encoding"], "cp932")

    def test_html_decodes_art_entities_but_not_scripts(self):
        raw = '<script>do not treat as evidence</script><pre>γ⌒ヽ&lt;\n乂__ノ</pre>'.encode()
        text, _ = self.fetch_fixture(raw, "text/html; charset=utf-8")
        self.assertIn("γ⌒ヽ<\n乂__ノ", text)
        self.assertNotIn("do not treat as evidence", text)

    def test_links_are_extracted_without_assigning_artist_identity(self):
        parser = audit.Text()
        parser.feed('<a href="/post/610">◆poster</a><p>reused drawing</p>')
        self.assertEqual(parser.links, [("/post/610", "◆poster")])
        self.assertFalse(hasattr(parser, "creator"))


if __name__ == "__main__":
    unittest.main()
