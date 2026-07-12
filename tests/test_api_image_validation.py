import base64
import io
import unittest

from fastapi import HTTPException
from PIL import Image

from server.app import MAX_BYTES, _decode_image


def valid_png_data_url() -> str:
    buffer = io.BytesIO()
    Image.new("RGB", (32, 32), (180, 120, 160)).save(buffer, "PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


class ApiImageValidationTests(unittest.TestCase):
    def test_valid_png_is_accepted(self):
        self.assertGreater(len(_decode_image(valid_png_data_url())), 0)

    def test_invalid_base64_is_rejected(self):
        with self.assertRaises(HTTPException) as raised:
            _decode_image("data:image/png;base64,%%%not-base64%%")
        self.assertEqual(raised.exception.status_code, 400)

    def test_non_image_payload_is_rejected(self):
        payload = base64.b64encode(b"this is not an image").decode("ascii")
        with self.assertRaises(HTTPException) as raised:
            _decode_image("data:image/png;base64," + payload)
        self.assertEqual(raised.exception.status_code, 400)

    def test_unsupported_mime_is_rejected(self):
        payload = valid_png_data_url().split(",", 1)[1]
        with self.assertRaises(HTTPException) as raised:
            _decode_image("data:image/svg+xml;base64," + payload)
        self.assertEqual(raised.exception.status_code, 400)

    def test_oversized_payload_is_rejected(self):
        payload = base64.b64encode(b"0" * (MAX_BYTES + 1)).decode("ascii")
        with self.assertRaises(HTTPException) as raised:
            _decode_image("data:image/png;base64," + payload)
        self.assertEqual(raised.exception.status_code, 413)


if __name__ == "__main__":
    unittest.main()
