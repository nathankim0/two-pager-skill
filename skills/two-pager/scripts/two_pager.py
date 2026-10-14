#!/usr/bin/env python3
"""Scaffold, crop, and validate/export a two-page executive brief."""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import importlib.util
import json
import mimetypes
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def ensure_runtime():
    """Reuse installed dependencies or a persistent, requirements-keyed venv."""
    if all(importlib.util.find_spec(name) for name in ('playwright', 'pypdf', 'PIL')):
        return
    if os.environ.get('TWO_PAGER_RUNTIME'):
        raise ValueError('Cached runtime is incomplete. Remove the reported cache directory and retry.')
    requirements = SCRIPT_DIR / 'requirements.txt'
    digest = hashlib.sha256(requirements.read_bytes()).hexdigest()[:10]
    cache_base = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache'))
    cache = cache_base / 'two-pager' / f'py{sys.version_info.major}.{sys.version_info.minor}-{digest}'
    python = cache / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    stamp = cache / '.ready'
    if not stamp.exists() or not python.exists():
        print(f'Preparing reusable runtime: {cache}', flush=True)
        cache.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, '-m', 'venv', str(cache)], check=True)
        subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(requirements)], check=True)
        stamp.write_text(digest, encoding='utf-8')
    env = {**os.environ, 'TWO_PAGER_RUNTIME': str(cache)}
    raise SystemExit(subprocess.call([str(python), str(Path(__file__).resolve()), *sys.argv[1:]], env=env))


def embed_images(markup: str, base: Path) -> str:
    """Embed quoted local img sources; do not fetch remote image URLs."""
    def replace_tag(match):
        tag = match.group()
        source = re.search(r'\bsrc\s*=\s*([\'"])(.*?)\1', tag, re.I | re.S)
        if not source:
            raise ValueError('Every image must have a quoted src attribute.')
        value = html.unescape(source.group(2))
        if value.startswith('data:image/'):
            return tag
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc:
            raise ValueError(f'Use a local image instead of a URL: {value}')
        path = (base / unquote(parsed.path)).resolve()
        if not path.is_file():
            raise ValueError(f'Image does not exist: {path}')
        mime = mimetypes.guess_type(path.name)[0] or ''
        if not mime.startswith('image/'):
            raise ValueError(f'Unsupported image type: {path.name}')
        data = 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')
        return tag[:source.start(2)] + data + tag[source.end(2):]
    return re.sub(r'<img\b[^>]*>', replace_tag, markup, flags=re.I | re.S)


def scaffold(output: Path, title: str, brand: str):
    target = output / 'two-pager.html'
    if target.exists():
        raise ValueError(f'Will not overwrite an existing draft: {target}')
    template = (SKILL_DIR / 'assets/two-pager.html').read_text(encoding='utf-8')
    template = template.replace('__TITLE__', html.escape(title)).replace('__BRAND__', html.escape(brand))
    output.mkdir(parents=True, exist_ok=True)
    target.write_text(template, encoding='utf-8')
    print(f'Created {target}\nReplace the fictional example copy, then run render.')


def crop_image(source: Path, box: list[int], output: Path):
    from PIL import Image
    x, y, width, height = box
    if output.resolve() == source.resolve():
        raise ValueError('Crop output must differ from the original image.')
    with Image.open(source) as image:
        if x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > image.width or y + height > image.height:
            raise ValueError(f'Crop {box} is outside {image.width}×{image.height}.')
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.png', delete=False) as file:
            temporary = Path(file.name)
        try:
            image.crop((x, y, x + width, y + height)).save(temporary, format='PNG')
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)
    print(f'Cropped {output} ({width}×{height})')


def browser_options(runtime, explicit: str | None):
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file():
            raise ValueError(f'Browser does not exist: {path}')
        return {'executable_path': str(path)}
    candidates = [shutil.which(name) for name in ('google-chrome', 'chromium', 'chromium-browser')]
    candidates += ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                   '/Applications/Chromium.app/Contents/MacOS/Chromium']
    for env_name in ('PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA'):
        if os.environ.get(env_name):
            candidates.append(str(Path(os.environ[env_name]) / 'Google/Chrome/Application/chrome.exe'))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return {'executable_path': candidate}
    if not Path(runtime.chromium.executable_path).is_file():
        print('Installing Chromium once for future exports.', flush=True)
        subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'], check=True)
    return {}


def render(source: Path, output: Path, browser: str | None):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader

    source = source.resolve()
    if source.suffix.lower() not in ('.html', '.htm') or not source.is_file():
        raise ValueError('Input must be an existing HTML file.')
    markup = embed_images(source.read_text(encoding='utf-8'), source.parent)
    if re.search(r'__[A-Z][A-Z_]*__|\{\{[^}]+\}\}', markup):
        raise ValueError('Replace unfinished template placeholders before rendering.')
    output.mkdir(parents=True, exist_ok=True)
    qa = output / '.qa' / source.stem
    qa.mkdir(parents=True, exist_ok=True)
    report = {'source': str(source), 'issues': []}
    with tempfile.TemporaryDirectory(prefix='.two-pager-', dir=output) as build_dir:
        build = Path(build_dir)
        candidate_html = build / source.name
        candidate_pdf = build / f'{source.stem}.pdf'
        candidate_html.write_text(markup, encoding='utf-8')
        with sync_playwright() as runtime:
            instance = runtime.chromium.launch(headless=True, **browser_options(runtime, browser))
            try:
                page = instance.new_page(viewport={'width':1840, 'height':1080},
                                         device_scale_factor=1, java_script_enabled=False)
                page.set_default_timeout(30000)
                network = []
                def route_request(route):
                    if urlsplit(route.request.url).scheme in ('http', 'https'):
                        network.append(route.request.url)
                        route.abort()
                    else:
                        route.continue_()
                page.route('**/*', route_request)
                page.goto(candidate_html.as_uri(), wait_until='load', timeout=30000)
                page.emulate_media(media='print')
                page.evaluate('document.fonts.ready')
                report.update(page.evaluate((SCRIPT_DIR / 'check_layout.js').read_text(encoding='utf-8')))
                count = page.locator('article.page').count()
                for index in range(count):
                    page.locator('article.page').nth(index).screenshot(path=str(qa / f'page-{index+1}.png'))
                if network:
                    report['issues'].append({'type': 'external-assets', 'urls': sorted(set(network))})
                if report['issues']:
                    report['passed'] = False
                    (qa / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
                    details = json.dumps(report['issues'][:5], ensure_ascii=False)
                    raise ValueError(f"Layout check failed ({len(report['issues'])} issues): {details}. Inspect {qa}")
                page.pdf(path=str(candidate_pdf), prefer_css_page_size=True, print_background=True, display_header_footer=False)
            finally:
                instance.close()
        reader = PdfReader(candidate_pdf)
        if len(reader.pages) != 2:
            report['issues'].append({'type':'pdf-page-count', 'expected':2, 'actual':len(reader.pages)})
        else:
            for index, pdf_page in enumerate(reader.pages):
                expected = report['sizes'][index]
                if abs(float(pdf_page.mediabox.width) - expected['width'] * .75) > 2 or abs(float(pdf_page.mediabox.height) - expected['height'] * .75) > 2:
                    report['issues'].append({'type':'pdf-size-mismatch', 'page':index+1})
                if len((pdf_page.extract_text() or '').strip()) < 10:
                    report['issues'].append({'type':'missing-pdf-text', 'page':index+1})
        report['pdfPages'] = len(reader.pages)
        report['passed'] = not report['issues']
        (qa / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        if report['issues']:
            raise ValueError(f'PDF check failed. Inspect {qa}')
        candidate_pdf.replace(output / candidate_pdf.name)
        candidate_html.replace(output / candidate_html.name)
    print(f'HTML: {output / source.name}\nPDF: {output / (source.stem + ".pdf")}\nQA: {qa}')
    print('Two pages validated. Inspect both preview PNGs before delivery.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('scaffold', help='Create an editable HTML draft with fictional example copy')
    init.add_argument('output_dir', type=Path)
    init.add_argument('--title', default='동네 도서관 예약·알림 서비스 개선')
    init.add_argument('--brand', default='example')
    export = commands.add_parser('render', help='Embed images, check layout, export PDF and two page previews')
    export.add_argument('source', type=Path)
    export.add_argument('--output-dir', type=Path, required=True)
    export.add_argument('--browser', help='Optional Chrome/Chromium executable path')
    crop = commands.add_parser('crop', help='Crop a supplied image to PNG without changing the original')
    crop.add_argument('source', type=Path)
    crop.add_argument('--box', nargs=4, type=int, metavar=('X', 'Y', 'WIDTH', 'HEIGHT'), required=True)
    crop.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'scaffold':
        scaffold(args.output_dir, args.title, args.brand)
    else:
        ensure_runtime()
        if args.command == 'crop':
            if args.output.suffix.lower() != '.png':
                parser.error('Crop output must use .png')
            crop_image(args.source, args.box, args.output)
        else:
            render(args.source, args.output_dir, args.browser)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        raise SystemExit(1)
