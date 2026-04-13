from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(r"c:\Users\user\fiilthy")
CEO_ROOT = ROOT / "ceo"
REVIEW_ROOT = CEO_ROOT / "review_assets"
SOURCE_ROOT = REVIEW_ROOT / "source"
SLIDES_ROOT = REVIEW_ROOT / "slides"
SEGMENTS_ROOT = REVIEW_ROOT / "segments"
OUTPUT_ROOT = REVIEW_ROOT / "output"

PRODUCT_VIDEO = CEO_ROOT / "backend" / "data" / "videos" / "product_2b2bf110.mp4"
SANDBOX_SCREENSHOT = ROOT / ".playwright-mcp" / "page-2026-04-12T18-46-53-238Z.png"


def ensure_dirs() -> None:
    for directory in [SOURCE_ROOT, SLIDES_ROOT, SEGMENTS_ROOT, OUTPUT_ROOT]:
        directory.mkdir(parents=True, exist_ok=True)


def pick_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if bold:
        candidates.extend(
            [
                Path(r"C:\Windows\Fonts\bahnschrift.ttf"),
                Path(r"C:\Windows\Fonts\arialbd.ttf"),
                Path(r"C:\Windows\Fonts\segoeuib.ttf"),
            ]
        )
    candidates.extend(
        [
            Path(r"C:\Windows\Fonts\arial.ttf"),
            Path(r"C:\Windows\Fonts\segoeui.ttf"),
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def ffmpeg_bin() -> str:
    binary = shutil.which("ffmpeg")
    if binary:
        return binary
    fallback = Path(
        r"C:\Users\user\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"
    )
    if fallback.exists():
        return str(fallback)
    raise FileNotFoundError("ffmpeg was not found")


def draw_centered_text(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, font, fill) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    x = box[0] + ((box[2] - box[0]) - width) / 2
    y = box[1] + ((box[3] - box[1]) - height) / 2
    draw.text((x, y), text, font=font, fill=fill)


def create_icon() -> Path:
    output = OUTPUT_ROOT / "fiilthy_tiktok_icon.png"
    canvas = Image.new("RGBA", (1024, 1024), "#05060a")
    draw = ImageDraw.Draw(canvas)

    for index in range(24):
        alpha = max(0, 90 - index * 3)
        inset = 40 + index * 8
        draw.rounded_rectangle(
            [inset, inset, 1024 - inset, 1024 - inset],
            radius=180,
            outline=(255, 0, 108, alpha),
            width=2,
        )

    glow = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle([184, 184, 840, 840], radius=180, fill="#ff005f")
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    canvas.alpha_composite(glow)

    draw.rounded_rectangle([200, 200, 824, 824], radius=164, fill="#ff005f")
    draw.rounded_rectangle([228, 228, 796, 796], radius=144, outline=(255, 255, 255, 60), width=3)

    title_font = pick_font(480, bold=True)
    badge_font = pick_font(66, bold=True)

    draw_centered_text(draw, (240, 160, 784, 820), "F", title_font, "#05060a")
    draw.rounded_rectangle([612, 684, 776, 764], radius=32, fill="#05060a")
    draw_centered_text(draw, (612, 684, 776, 764), "AI", badge_font, "#ffffff")

    canvas.save(output)
    return output


def copy_source_images() -> None:
    if SANDBOX_SCREENSHOT.exists():
        shutil.copyfile(SANDBOX_SCREENSHOT, SOURCE_ROOT / "sandbox.png")


def make_background() -> Image.Image:
    image = Image.new("RGB", (1920, 1080), "#06070d")
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, 1920, 1080], fill="#06070d")
    draw.ellipse([-200, -240, 760, 500], fill="#1e1130")
    draw.ellipse([1120, 540, 2140, 1380], fill="#101f31")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle([72, 64, 1848, 1016], radius=42, fill=(8, 12, 22, 220), outline=(255, 255, 255, 18), width=2)
    image = image.convert("RGBA")
    image.alpha_composite(overlay)
    return image.convert("RGB")


def place_screenshot(base: Image.Image, screenshot_path: Path, top: int = 300) -> None:
    if not screenshot_path.exists():
        return
    frame = Image.open(screenshot_path).convert("RGB")
    fitted = Image.new("RGB", (1480, 620), "#111827")
    shot = frame.copy()
    shot.thumbnail((1440, 580))
    x = (1480 - shot.width) // 2
    y = (620 - shot.height) // 2
    fitted.paste(shot, (x, y))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle([220, top, 1700, top + 620], radius=28, fill="#0d1322", outline=(255, 255, 255, 28), width=2)
    base.paste(fitted, (220, top + 20))


def create_slide(index: int, title: str, subtitle: str, caption: str, screenshot: Path | None = None) -> Path:
    output = SLIDES_ROOT / f"slide_{index:02d}.png"
    slide = make_background()
    draw = ImageDraw.Draw(slide)
    eyebrow_font = pick_font(32, bold=True)
    title_font = pick_font(78, bold=True)
    subtitle_font = pick_font(36)
    caption_font = pick_font(32)

    draw.rounded_rectangle([120, 104, 330, 158], radius=27, fill="#ff005f")
    draw.text((152, 116), "FiiLTHY.ai", font=eyebrow_font, fill="#ffffff")
    draw.text((120, 190), title, font=title_font, fill="#ffffff")
    draw.text((120, 276), subtitle, font=subtitle_font, fill="#98a2b3")

    if screenshot and screenshot.exists():
      place_screenshot(slide, screenshot)
      draw.text((220, 952), caption, font=caption_font, fill="#d2e4ff")
    else:
      draw.rounded_rectangle([160, 420, 1760, 830], radius=34, fill="#0d1322", outline=(255, 255, 255, 24), width=2)
      draw_centered_text(draw, (250, 500, 1670, 750), caption, pick_font(44, bold=True), "#f4f7fb")

    slide.save(output)
    return output


def make_slide_segments(slides: list[Path]) -> list[Path]:
    ffmpeg = ffmpeg_bin()
    segments = []
    for slide in slides:
        segment = SEGMENTS_ROOT / f"{slide.stem}.mp4"
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-loop",
                "1",
                "-i",
                str(slide),
                "-t",
                "4",
                "-vf",
                "fps=30,format=yuv420p",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(segment),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        segments.append(segment)
    return segments


def make_product_segment() -> Path:
    ffmpeg = ffmpeg_bin()
    segment = SEGMENTS_ROOT / "product_video.mp4"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(PRODUCT_VIDEO),
            "-vf",
            "scale=607:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps=30,format=yuv420p",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(segment),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return segment


def concat_segments(segments: list[Path]) -> Path:
    ffmpeg = ffmpeg_bin()
    concat_file = SEGMENTS_ROOT / "segments.txt"
    concat_file.write_text("\n".join([f"file '{segment.as_posix()}'" for segment in segments]), encoding="utf-8")
    output = OUTPUT_ROOT / "fiilthy_tiktok_review_demo.mp4"
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(output),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return output


def create_demo_video() -> Path:
    copy_source_images()
    slides = [
        create_slide(
            1,
            "TikTok Integration Review Demo",
            "FiiLTHY.ai connects creator accounts, generates promo content, and publishes through TikTok APIs.",
            "End-to-end sandbox review flow for Login Kit and Content Posting API.",
        ),
        create_slide(
            2,
            "1. Creator opens the dashboard",
            "The live FiiLTHY.ai app is available on the existing Vercel deployment.",
            "Users start inside the dashboard to manage products, growth, and social workflows.",
            SOURCE_ROOT / "dashboard.png",
        ),
        create_slide(
            3,
            "2. Connect TikTok from Social Media",
            "Login Kit is used to authorize the creator and grant the required TikTok scopes.",
            "The app triggers the OAuth flow before any publishing action is enabled.",
            SOURCE_ROOT / "social-media.png",
        ),
        create_slide(
            4,
            "3. Configure the social stack",
            "Operators manage TikTok keys, account settings, and backend sync inside the app settings screen.",
            "This is where the TikTok connection is prepared before automated publishing starts.",
            SOURCE_ROOT / "settings.png",
        ),
        create_slide(
            5,
            "4. AI generates the promo video",
            "The backend creates a vertical short-form ad using product data, script generation, and media assembly.",
            "The next segment is the generated MP4 that the app uploads to TikTok.",
        ),
        create_slide(
            6,
            "5. Sandbox account is configured",
            "The TikTok developer sandbox includes Login Kit, Content Posting API, and the test user for verification.",
            "Scopes enabled: user.info.basic, video.upload, and video.publish.",
            SOURCE_ROOT / "sandbox.png",
        ),
        create_slide(
            7,
            "Review Summary",
            "OAuth login, video generation, and publishing are all configured for the sandbox environment.",
            "FiiLTHY.ai is ready to authenticate creators and submit AI-generated promo videos to TikTok.",
        ),
    ]
    segments = make_slide_segments(slides[:4])
    segments.append(make_slide_segments([slides[4]])[0])
    segments.append(make_product_segment())
    segments.extend(make_slide_segments(slides[5:]))
    return concat_segments(segments)


def main() -> None:
    ensure_dirs()
    icon = create_icon()
    video = create_demo_video()
    print(f"Icon: {icon}")
    print(f"Demo video: {video}")


if __name__ == "__main__":
    main()