#!/usr/bin/env python3
"""Render quotation JSON to HTML, then optionally to PDF via Playwright."""
import json
import sys
import os
import base64
from pathlib import Path
from jinja2 import Environment

def get_base64_image(path):
    """Convert local image to base64 for embedding in HTML."""
    if not path:
        return None
    full_path = Path(path)
    if not full_path.exists():
        return None
    with open(full_path, "rb") as f:
        data = f.read()
    ext = full_path.suffix.lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "svg": "image/svg+xml"}.get(ext, "image/png")
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"

def render_html(data, template_path):
    """Render JSON data to HTML using Jinja2 template."""
    env = Environment()
    with open(template_path) as f:
        template = env.from_string(f.read())

    # Process logo - convert to base64 if local file
    if data.get("branding", {}).get("logo_path"):
        logo_b64 = get_base64_image(data["branding"]["logo_path"])
        if logo_b64:
            data["branding"]["logo_path"] = logo_b64

    return template.render(**data)

def render_to_pdf(html_path, pdf_path):
    """Convert HTML to PDF using Playwright."""
    from playwright.sync_api import sync_playwright

    abs_html = str(Path(html_path).resolve())
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{abs_html}", wait_until="networkidle")
        page.pdf(
            path=pdf_path,
            format="A4",
            margin={"top": "12mm", "right": "20%", "bottom": "12mm", "left": "20%"},
            print_background=True
        )
        browser.close()

def main():
    if len(sys.argv) < 3:
        print("Usage: python render_quotation.py <json_file> <template_file> [pdf_output]")
        sys.exit(1)

    json_file = sys.argv[1]
    template_file = sys.argv[2]
    pdf_output = sys.argv[3] if len(sys.argv) > 3 else None

    with open(json_file) as f:
        data = json.load(f)

    html = render_html(data, template_file)

    template_dir = Path(template_file).parent
    html_output = template_dir / "quotation_output.html"
    with open(html_output, "w") as f:
        f.write(html)
    print(f"HTML written to: {html_output}")

    if pdf_output:
        render_to_pdf(str(html_output), pdf_output)
        print(f"PDF written to: {pdf_output}")

if __name__ == "__main__":
    main()