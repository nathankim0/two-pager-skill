"""Behavior checks; run with the reusable runtime or installed requirements."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import shutil

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('two_pager', ROOT / 'skills/two-pager/scripts/two_pager.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class TwoPagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_local_unicode_image_embeds_and_remote_image_is_rejected(self):
        from PIL import Image
        image = self.root / '퀘스트 & 시안.png'
        Image.new('RGB', (12, 8), '#369').save(image)
        markup = '<img src="퀘스트 &amp; 시안.png" alt="시안">'
        embedded = tool.embed_images(markup, self.root)
        self.assertIn('data:image/png;base64,', embedded)
        self.assertIn('alt="시안"', embedded)
        with self.assertRaises(ValueError):
            tool.embed_images('<img src="https://example.com/image.png">', self.root)
        with self.assertRaises(ValueError):
            tool.embed_images('<img src="missing.png">', self.root)

    def test_crop_checks_bounds_and_preserves_original(self):
        from PIL import Image
        image = self.root / 'original.png'
        output = self.root / 'crop.png'
        Image.new('RGB', (40, 20), '#fff').save(image)
        original = image.read_bytes()
        tool.crop_image(image, [5, 4, 20, 10], output)
        with Image.open(output) as result:
            self.assertEqual(result.size, (20, 10))
        self.assertEqual(image.read_bytes(), original)
        previous = output.read_bytes()
        with self.assertRaises(ValueError):
            tool.crop_image(image, [30, 0, 20, 10], output)
        self.assertEqual(output.read_bytes(), previous)
        with self.assertRaises(ValueError):
            tool.crop_image(image, [0, 0, 40, 20], image)

    def test_two_pages_render_and_invalid_revision_keeps_final_files(self):
        from pypdf import PdfReader
        source_dir, output = self.root / 'draft', self.root / 'final'
        tool.scaffold(source_dir, '도서관 예약 개선', 'LIBRARY')
        source = source_dir / 'two-pager.html'
        try:
            tool.render(source, output, None)
        except ValueError:
            shutil.copytree(output / '.qa/two-pager', ROOT / 'output/test-failure', dirs_exist_ok=True)
            raise
        pdf, html = output / 'two-pager.pdf', output / 'two-pager.html'
        self.assertEqual(len(PdfReader(pdf).pages), 2)
        self.assertIn('도서관 예약 개선', PdfReader(pdf).pages[0].extract_text())
        self.assertTrue((output / '.qa/two-pager/page-2.png').exists())
        previous_pdf, previous_html = pdf.read_bytes(), html.read_bytes()
        source.write_text(source.read_text().replace('</main>', '<article class="page"><p>Third page</p></article></main>'))
        with self.assertRaises(ValueError):
            tool.render(source, output, None)
        self.assertEqual(pdf.read_bytes(), previous_pdf)
        self.assertEqual(html.read_bytes(), previous_html)

    def test_overflow_blocks_delivery_and_draft_is_not_overwritten(self):
        source_dir, output = self.root / 'draft', self.root / 'final'
        tool.scaffold(source_dir, '한글 검증', 'LIBRARY')
        with self.assertRaises(ValueError):
            tool.scaffold(source_dir, 'replace', 'replace')
        source = source_dir / 'two-pager.html'
        source.write_text(source.read_text().replace('</style>', '.strategy-text {font-size:80px;}\n</style>'))
        with self.assertRaises(ValueError):
            tool.render(source, output, None)
        self.assertFalse((output / 'two-pager.pdf').exists())
        self.assertTrue((output / '.qa/two-pager/report.json').exists())


if __name__ == '__main__':
    unittest.main()
