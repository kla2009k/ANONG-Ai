import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "web-react" / "public" / "koil-gallery" / "index.json"


class KoilReferenceGalleryTests(unittest.TestCase):
    def test_gallery_has_twenty_center_focus_cccid_koilocytes(self):
        self.assertTrue(MANIFEST.exists(), "generate the CCCID KOIL gallery")
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        hashes = json.loads((MANIFEST.parent / "sha256.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["dataset"], "CCCID v2")
        self.assertEqual(payload["dataset_doi"], "10.5281/zenodo.20807462")
        self.assertEqual(payload["license"], "CC BY-NC 4.0")
        self.assertEqual(payload["archive_md5"], "6e2f6bf468addd80b698318d87c16123")
        self.assertEqual(payload["intended_use"], "external_koil_reference_and_preselected_positive_challenge")
        self.assertFalse(payload["model_predictions_included"])
        self.assertEqual(payload["count"], 20)

        subtype_counts = Counter(item["subtype"] for item in payload["items"])
        self.assertEqual(subtype_counts, Counter({
            "Superficial-type koilocyte": 10,
            "Intermediate-type koilocyte": 10,
        }))
        self.assertEqual(len({item["source_member"] for item in payload["items"]}), 20)

        for item in payload["items"]:
            self.assertEqual(item["class"], "KOIL")
            self.assertEqual(item["focus_plane"], 5)
            self.assertNotIn("prediction", item)
            image_path = ROOT / "web-react" / "public" / item["image"]
            self.assertTrue(image_path.exists(), item["image"])
            self.assertEqual(hashes[image_path.name], hashlib.sha256(image_path.read_bytes()).hexdigest())
            with Image.open(image_path) as image:
                self.assertEqual(image.size, (384, 384))


if __name__ == "__main__":
    unittest.main()
