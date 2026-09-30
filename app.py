import argparse
import json
import os
import re
import smtplib
import sys
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFilter, ImageFont


load_dotenv()

SERVICE_LIBRARY = {
    "business insurance": {
        "headline": "Business Protection",
        "body": "Secure your business, assets, and future with expert guidance.",
    },
    "home insurance": {
        "headline": "Home Protection",
        "body": "Protect your home, family, and valuables with smart coverage.",
    },
    "family protection": {
        "headline": "Family Security",
        "body": "Insurance solutions designed to protect what matters most.",
    },
    "motor insurance": {
        "headline": "Motor Insurance",
        "body": "Drive with confidence knowing your vehicle is covered.",
    },
    "life insurance": {
        "headline": "Life Insurance",
        "body": "Build long-term security for the people you care about most.",
    },
    "health insurance": {
        "headline": "Health Protection",
        "body": "Reliable care support for your health and peace of mind.",
    },
}


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(key)
    return default if value in (None, "") else value


def ensure_folder(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def safe_filename(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_\- ]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value.replace(" ", "_") or "impact_solution_post"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for font_path in candidates:
        if os.path.exists(font_path):
            if bold:
                return ImageFont.truetype(font_path, size=size)
            return ImageFont.truetype(font_path, size=size)
    return ImageFont.load_default()


def build_caption(service_name: str, company_name: str, custom_text: Optional[str] = None) -> str:
    service_key = service_name.lower().strip()
    if custom_text:
        return custom_text

    service_meta = SERVICE_LIBRARY.get(service_key, {
        "headline": service_name.title(),
        "body": "Custom insurance support with trust, care, and expert guidance.",
    })

    headline = service_meta["headline"]
    body = service_meta["body"]

    caption = (
        f"{headline} with {company_name} \n\n"
        f"{body} \n\n"
        "Trust matters. Protection matters. Your peace of mind matters.\n\n"
        "✅ Expert guidance\n"
        "✅ Personalized solutions\n"
        "✅ Reliable support when it matters most\n\n"
        "For smart insurance solutions, connect with us today."
    )
    return caption


def create_flyer(service_name: str, company_name: str, save_path: str, custom_title: Optional[str] = None) -> str:
    service_key = service_name.lower().strip()
    meta = SERVICE_LIBRARY.get(service_key, {
        "headline": service_name.title(),
        "body": "Protect what matters most with expert guidance and trusted support.",
    })

    width, height = 1080, 1080
    img = Image.new("RGB", (width, height), color=(245, 245, 242))
    draw = ImageDraw.Draw(img)

    # background blocks
    draw.rounded_rectangle((40, 40, 1040, 1040), radius=42, fill=(245, 245, 242), outline=(255, 115, 66), width=10)

    # left accent band
    draw.rectangle((60, 60, 120, 1020), fill=(255, 115, 66))
    draw.rectangle((920, 60, 1020, 1020), fill=(21, 104, 104))

    # header band
    header_color = (22, 121, 118)
    draw.rounded_rectangle((180, 90, 900, 220), radius=28, fill=header_color)
    draw.text((220, 122), company_name.upper(), fill=(255, 255, 255), font=load_font(46, bold=True))

    # title
    title_text = custom_title or meta["headline"]
    draw.text((190, 290), title_text.upper(), fill=(30, 30, 30), font=load_font(58, bold=True))

    # body text
    body_text = meta["body"]
    wrapped = wrap_text(body_text, 34, load_font(34, bold=False), 620)
    y = 420
    for line in wrapped:
        draw.text((190, y), line, fill=(50, 50, 50), font=load_font(34, bold=False))
        y += 42

    # badge area
    badge_x = 180
    badge_y = 560
    for idx, item in enumerate([
        "Trust",
        "Protection",
        "Expert Advice",
        "Family Security",
    ]):
        bx = badge_x + (idx % 2) * 250
        by = badge_y + (idx // 2) * 110
        draw.rounded_rectangle((bx, by, bx + 200, by + 70), radius=20, fill=(255, 255, 255), outline=(255, 115, 66), width=3)
        draw.text((bx + 20, by + 18), item, fill=(42, 42, 42), font=load_font(26, bold=True))

    # footer bar
    draw.rounded_rectangle((180, 850, 900, 930), radius=24, fill=(255, 115, 66))
    footer_text = "Trust. Protection. Peace of Mind."
    draw.text((300, 870), footer_text, fill=(255, 255, 255), font=load_font(30, bold=True))

    img.save(save_path)
    return save_path


def wrap_text(text: str, max_chars: int, font, max_width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def save_to_desktop(file_path: str) -> str:
    desktop_path = get_env("DESKTOP_PATH") or str(Path.home() / "Desktop")
    ensure_folder(desktop_path)
    destination = str(Path(desktop_path) / Path(file_path).name)
    Path(file_path).replace(destination)
    return destination


def send_email_update(subject: str, body: str) -> None:
    smtp_host = get_env("SMTP_HOST")
    if not smtp_host:
        return

    smtp_port = int(get_env("SMTP_PORT") or "587")
    username = get_env("SMTP_USERNAME")
    password = get_env("SMTP_PASSWORD")
    to_email = get_env("EMAIL_TO")

    if not (username and password and to_email):
        return

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = username
    message["To"] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(username, [to_email], message.as_string())


def post_to_meta(image_path: str, caption: str) -> Dict:
    page_id = get_env("META_PAGE_ID")
    access_token = get_env("META_ACCESS_TOKEN")
    if not (page_id and access_token):
        raise RuntimeError("META_PAGE_ID and META_ACCESS_TOKEN are required to post to Meta.")

    url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
    payload = {
        "url": "",
        "access_token": access_token,
        "caption": caption,
        "published": "false",
    }

    with open(image_path, "rb") as f:
        files = {"source": (os.path.basename(image_path), f, "image/png")}
        response = requests.post(url, data={"access_token": access_token, "caption": caption, "published": "false"}, files=files, timeout=60)

    if response.status_code >= 400:
        raise RuntimeError(f"Meta post failed: {response.status_code} {response.text}")

    return response.json()


def generate_summary(service_name: str, image_path: str, caption: str, status: str = "ready") -> str:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        f"Impact Solution social content summary\n"
        f"Time: {stamp}\n"
        f"Service: {service_name}\n"
        f"Status: {status}\n"
        f"Image: {image_path}\n"
        f"Caption:\n{caption}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Impact Solution social media automation")
    parser.add_argument("--service", default="Business Insurance", help="Service or campaign you want to promote")
    parser.add_argument("--save-only", action="store_true", help="Generate and save only, no Meta post")
    parser.add_argument("--dry-run", action="store_true", help="Generate local preview without saving to desktop")
    parser.add_argument("--post", action="store_true", help="Post to Meta when credentials exist")
    parser.add_argument("--custom-title", default=None, help="Optional flyer title")
    parser.add_argument("--custom-caption", default=None, help="Optional custom caption text")
    args = parser.parse_args()

    company_name = get_env("COMPANY_NAME") or "Impact Solution"
    output_folder = get_env("OUTPUT_FOLDER") or "output"
    ensure_folder(output_folder)

    safe_service = args.service.strip() or "Business Insurance"
    file_name = safe_filename(f"{company_name}_{safe_service}")
    local_file = str(Path(output_folder) / f"{file_name}.png")

    try:
        flyer_path = create_flyer(safe_service, company_name, local_file, args.custom_title)
    except Exception as exc:
        print(f"Flyer generation failed: {exc}")
        return 1

    caption = build_caption(safe_service, company_name, args.custom_caption)
    summary = generate_summary(safe_service, flyer_path, caption, "generated")

    summary_path = str(Path(output_folder) / f"{file_name}_summary.txt")
    Path(summary_path).write_text(summary, encoding="utf-8")

    desktop_target = flyer_path
    if not args.dry_run:
        desktop_target = save_to_desktop(flyer_path)
        caption_copy_target = str(Path(Path(desktop_target).parent) / f"{file_name}_caption.txt")
        Path(caption_copy_target).write_text(caption, encoding="utf-8")

    print(f"Flyer created: {flyer_path}")
    if not args.dry_run:
        print(f"Saved to Desktop: {desktop_target}")
    print("Caption:")
    print(caption)

    if args.post or (not args.save_only and not args.dry_run and get_env("META_PAGE_ID") and get_env("META_ACCESS_TOKEN")):
        try:
            result = post_to_meta(flyer_path, caption)
            print("Meta post result:")
            print(json.dumps(result, indent=2))
            summary = generate_summary(safe_service, flyer_path, caption, "posted to meta")
            Path(summary_path).write_text(summary, encoding="utf-8")
        except Exception as exc:
            print(f"Meta posting failed: {exc}")

    email_body = f"Impact Solution content ready.\n\nService: {safe_service}\n\nCaption:\n{caption}"
    send_email_update("Impact Solution social update", email_body)

    return 0


if __name__ == "__main__":
    sys.exit(main())
