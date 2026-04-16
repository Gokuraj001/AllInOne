import re

with open("templates/pdf_converter.html", "r", encoding="utf-8") as f:
    pdf_content = f.read()

with open("templates/qr_generator.html", "r", encoding="utf-8") as f:
    qr_content = f.read()

# 1. Extract CSS
header_css = re.search(
    r"(        /\* HEADER \*/.*?)(?=        /\* HERO \*/)", pdf_content, re.DOTALL
).group(1)
footer_css = re.search(
    r"(        /\* FOOTER \*/.*?)(?=\s*</style>)", pdf_content, re.DOTALL
).group(1)

# Extract FLOAT CSS from pdf_converter
float_css_match = re.search(
    r"(        /\* FLOAT \*/.*?)(?=        /\* FOOTER \*/)", pdf_content, re.DOTALL
)
float_css = float_css_match.group(1) if float_css_match else ""

# Replace CSS in qr_generator
# Find where to insert Header CSS: after .bg-grid { ... }
qr_content = re.sub(
    r"(    \.bg-grid \{.*?    \})", r"\1\n\n" + header_css, qr_content, flags=re.DOTALL
)
# Replace existing float-mode CSS and add footer CSS at the end of style
qr_content = re.sub(r"    \.float-mode \{.*?\s*\}\n", "", qr_content, flags=re.DOTALL)

qr_content = re.sub(
    r"(\s*@media\(max-width: 900px\))",
    r"\n" + float_css + "\n" + footer_css + r"\1",
    qr_content,
)

# 2. Extract HTML
header_html = re.search(
    r"(    <!-- HEADER -->.*?)(?=    <!-- HERO -->|<\s*main>)", pdf_content, re.DOTALL
)
if header_html:
    header_html = header_html.group(1)
else:
    header_html = re.search(
        r'(    <!-- HEADER -->.*?)(?=    <div class="hero">)', pdf_content, re.DOTALL
    ).group(1)

footer_html = re.search(
    r"(    <!-- FOOTER -->.*?)(?=    <script>)", pdf_content, re.DOTALL
).group(1)

# Replace existing Header HTML
qr_content = re.sub(
    r"  <header>.*?</header>\n", header_html, qr_content, flags=re.DOTALL
)

# Delete existing Float button and replace with Footer HTML
qr_content = re.sub(
    r'  <button class="float-mode".*?</button>\n',
    footer_html,
    qr_content,
    flags=re.DOTALL,
)

# 3. Handle JS
# The JS in qr_generator is simple. We prepend the language/nav logic from pdf_converter.
js_block = re.search(r"    <script>\n(.*?)\s*</script>", pdf_content, re.DOTALL).group(
    1
)

# Extract the parts of JS related to Language, Drawer, Modal, Mode, Particles from pdf_converter
# We can just extract from "const T =" up to "/* FORMAT CARD SELECTOR"
js_core = re.search(
    r"(        const T = \{.*?)(?=        /\* FORMAT CARD SELECTOR)",
    pdf_content,
    re.DOTALL,
).group(1)

qr_js = re.search(r"  <script>\n(.*?)\s*</script>", qr_content, re.DOTALL).group(1)
# Remove the simple toggleMode from qr_js
qr_js = re.sub(
    r"    function toggleMode\(\) \{.*?\n    \}\n", "", qr_js, flags=re.DOTALL
)

new_js = js_core + "\n" + qr_js
qr_content = re.sub(
    r"  <script>\n.*?</script>",
    "  <script>\n" + new_js + "\n  </script>",
    qr_content,
    flags=re.DOTALL,
)

# Fix indentation in js_core if needed (it's fine as is)

with open("templates/qr_generator.html", "w", encoding="utf-8") as f:
    f.write(qr_content)

print("Done")
