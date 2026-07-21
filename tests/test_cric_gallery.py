import json
import hashlib
import unittest
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "web-react" / "public" / "cric-gallery" / "index.json"


class CricReferenceGalleryTests(unittest.TestCase):
    def test_gallery_has_twenty_real_unique_source_examples_per_supported_class(self):
        self.assertTrue(MANIFEST.exists(), "generate the CRIC gallery manifest")
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        hashes = json.loads((MANIFEST.parent / "sha256.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["dataset"], "CRIC Cervix Cell Classification")
        self.assertEqual(payload["license"], "CC BY 4.0")
        self.assertEqual(payload["intended_use"], "external_reference_atlas_not_model_evaluation")
        self.assertEqual(payload["count"], 80)

        counts = Counter(item["class"] for item in payload["items"])
        self.assertEqual(counts, Counter({"NILM": 20, "LSIL": 20, "HSIL": 20, "SCC": 20}))

        sources_by_class = defaultdict(set)
        for item in payload["items"]:
            sources_by_class[item["class"]].add(item["source_image_id"])
            self.assertNotIn("prediction", item)
            self.assertTrue(item["source_doi"].startswith("10.6084/m9.figshare."))
            image_path = ROOT / "web-react" / "public" / item["image"]
            self.assertTrue(image_path.exists(), item["image"])
            self.assertEqual(hashes[image_path.name], hashlib.sha256(image_path.read_bytes()).hexdigest())
            with Image.open(image_path) as image:
                self.assertEqual(image.size, (256, 256))

        self.assertTrue(all(len(source_ids) == 20 for source_ids in sources_by_class.values()))


if __name__ == "__main__":
    unittest.main()
