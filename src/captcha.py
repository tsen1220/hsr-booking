
import ddddocr

class CaptchaSolver:
    def __init__(self):
        self.ocr = ddddocr.DdddOcr(show_ad=False)

    def solve_bytes(self, image_bytes):
        """
        Solve captcha from image bytes.
        """
        try:
            res = self.ocr.classification(image_bytes)
            return res
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

    def solve_file(self, image_path):
        """
        Solve captcha from image file path.
        """
        with open(image_path, 'rb') as f:
            img_bytes = f.read()
        return self.solve_bytes(img_bytes)
