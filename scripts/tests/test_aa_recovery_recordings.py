from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import aa_recovery_recordings as recordings


class RecoveryRecordingRetention(unittest.TestCase):
    def test_only_real_browser_capture_remains_active(self):
        manifest = json.loads((recordings.OUT / "recordings.v1.json").read_text())
        self.assertEqual(len(manifest["artifacts"]), 1)
        record = manifest["artifacts"][0]
        path = ROOT / record["path"]
        self.assertEqual(path.name, "luna-aaj-viewer.gif")
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record["sha256"])
        with Image.open(path) as image:
            self.assertEqual(image.n_frames, record["frames"])
            for i in range(image.n_frames):
                image.seek(i)
                image.load()

    def test_five_rejected_files_are_absent_and_not_linked_from_readme(self):
        manifest = json.loads((recordings.OUT / "recordings.v1.json").read_text())
        rejected = {record["filename"] for record in manifest["rejected_artifacts"]}
        self.assertEqual(rejected, set(recordings.REJECTED))
        readme = (ROOT / "README.md").read_text()
        for name in recordings.REJECTED:
            self.assertFalse((recordings.OUT / name).exists(), name)
            self.assertNotIn(name, readme)


if __name__ == "__main__":
    unittest.main()
