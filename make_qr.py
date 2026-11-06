import argparse
from urllib.parse import urlparse

def main():
    parser = argparse.ArgumentParser(description="Generate a QR code for the deployed Smart Energy Meter website.")
    parser.add_argument("url", help="Final public HTTPS dashboard URL (include ?api=...)")
    parser.add_argument("--output", default="smart_energy_meter_qr.png")
    args = parser.parse_args()
    parsed = urlparse(args.url)
    if parsed.scheme != "https" or not parsed.netloc:
        parser.error("Use the final public HTTPS website URL, including the deployed API URL query parameter.")
    try:
        import qrcode
    except ImportError:
        parser.error("Install the dependency first: python -m pip install 'qrcode[pil]'")
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=4)
    qr.add_data(args.url)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(args.output)
    print(f"QR saved to {args.output}\nEncoded URL: {args.url}")

if __name__ == "__main__": main()
