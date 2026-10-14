import os
import re
import subprocess
import markdown

base_dir = os.path.dirname(os.path.abspath(__file__))
md_path = os.path.join(base_dir, "report.md")
html_path = os.path.join(base_dir, "report.html")
pdf_path = os.path.join(base_dir, "report.pdf")

with open(md_path, "r", encoding="utf-8") as f:
    text = f.read()

# Replace image paths with file:/// absolute paths so Chrome loads them without error
def fix_img_src(match):
    alt = match.group(1)
    src = match.group(2)
    if not src.startswith("http") and not src.startswith("file:"):
        abs_src = os.path.abspath(os.path.join(base_dir, src)).replace("\\", "/")
        return f"![{alt}](file:///{abs_src})"
    return match.group(0)

text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', fix_img_src, text)

# Convert Markdown to HTML
html_body = markdown.markdown(
    text,
    extensions=["extra", "codehilite", "tables", "toc"]
)

# Full HTML template with clean GitHub styling & Print-to-PDF optimizations
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>VNUHCM-US CS433 - Project 1 Report</title>
<style>
  @page {{
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    font-size: 11pt;
    line-height: 1.6;
    color: #24292f;
    background-color: #ffffff;
    max-width: 100%;
    margin: 0;
    padding: 0;
  }}
  h1, h2, h3, h4, h5, h6 {{
    margin-top: 24px;
    margin-bottom: 12px;
    font-weight: 600;
    line-height: 1.25;
    color: #0969da;
    page-break-after: avoid;
  }}
  h1 {{ font-size: 20pt; border-bottom: 2px solid #eaecef; padding-bottom: 6px; color: #1f2328; }}
  h2 {{ font-size: 15pt; border-bottom: 1px solid #eaecef; padding-bottom: 4px; }}
  h3 {{ font-size: 13pt; color: #333; }}
  h4 {{ font-size: 11.5pt; color: #444; }}
  p, ul, ol, dl, table, pre, blockquote {{
    margin-top: 0;
    margin-bottom: 14px;
  }}
  code {{
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    font-size: 85%;
    padding: 0.2em 0.4em;
    margin: 0;
    background-color: rgba(175, 184, 193, 0.2);
    border-radius: 4px;
  }}
  pre {{
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    font-size: 8.5pt;
    line-height: 1.45;
    background-color: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 12px;
    overflow: auto;
    page-break-inside: avoid;
    white-space: pre-wrap;
    word-break: break-all;
  }}
  pre code {{
    background-color: transparent;
    padding: 0;
    font-size: 100%;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
    font-size: 9.5pt;
    page-break-inside: avoid;
  }}
  table th, table td {{
    padding: 8px 12px;
    border: 1px solid #d0d7de;
  }}
  table th {{
    background-color: #f6f8fa;
    font-weight: 600;
    text-align: left;
  }}
  table tr:nth-child(2n) {{
    background-color: #fcfcfc;
  }}
  img {{
    max-width: 90%;
    height: auto;
    display: block;
    margin: 12px auto;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    page-break-inside: avoid;
  }}
  em {{
    display: block;
    text-align: center;
    font-size: 9pt;
    color: #57606a;
    margin-top: 4px;
    margin-bottom: 16px;
  }}
  blockquote {{
    padding: 0 1em;
    color: #57606a;
    border-left: 0.25em solid #d0d7de;
    margin: 0 0 16px 0;
  }}
  hr {{
    height: 0.25em;
    padding: 0;
    margin: 24px 0;
    background-color: #d0d7de;
    border: 0;
  }}
</style>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
</script>
</head>
<body>
{html_body}
</body>
</html>
"""

# Replace ```mermaid with <pre class="mermaid">
html_content = re.sub(r'<pre><code class="language-mermaid">([\s\S]*?)</code></pre>', r'<pre class="mermaid">\1</pre>', html_content)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated HTML at: {html_path}")

# Run Chrome Headless to compile PDF
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if os.path.exists(chrome_path):
    print("Running Google Chrome to generate PDF...")
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        f"file:///{html_path.replace(os.sep, '/')}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
        print(f"SUCCESS: Generated PDF at {pdf_path} (Size: {os.path.getsize(pdf_path)} bytes)")
    else:
        print("Chrome error:", res.stderr)
else:
    print("Chrome not found at specified path.")
