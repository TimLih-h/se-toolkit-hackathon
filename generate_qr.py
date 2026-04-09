#!/usr/bin/env python3
"""Generate QR codes for the presentation slides."""

try:
    import qrcode
except ImportError:
    print("Installing qrcode...")
    import subprocess
    subprocess.check_call(["pip", "install", "qrcode[pil]"])
    import qrcode

import os

# Links
links = {
    "github_repo": "https://github.com/TimLih-h/se-toolkit-hackathon",
    "deployed_product": "http://<VM_IP>:8083",
}

# Output directory
output_dir = os.path.join(os.path.dirname(__file__), "docs", "qr")
os.makedirs(output_dir, exist_ok=True)

for name, url in links.items():
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    path = os.path.join(output_dir, f"{name}.png")
    img.save(path)
    print(f"Generated: {path}")

print(f"\nQR codes saved to: {output_dir}")
print("Insert them into Slide 5 of the presentation.")
