import os
import img2pdf
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyPDF2 import PdfReader, PdfWriter


def collect_images(root_folder):
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff', '*.bmp', '*.gif']
    images = []
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for ext in image_extensions:
            images.extend(Path(dirpath).glob(ext))
    return sorted([str(f) for f in images])

def compress_single_image(img_path, temp_folder, quality=60, max_size=(1024, 1024)):
    img = Image.open(img_path)
    img = img.convert("RGB")
    img.thumbnail(max_size)
    out_path = os.path.join(temp_folder, os.path.basename(img_path) + ".jpg")
    img.save(out_path, "JPEG", quality=quality)
    return out_path

def compress_images_threaded(images, temp_folder="compressed_images", quality=60, max_size=(1024, 1024), max_workers=8):
    os.makedirs(temp_folder, exist_ok=True)
    compressed_paths = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(compress_single_image, img_path, temp_folder, quality, max_size) for img_path in images]
        for future in as_completed(futures):
            compressed_paths.append(future.result())
    return compressed_paths

def images_to_pdf(images, output_pdf="merged.pdf"):
    if images:
        with open(output_pdf, "wb") as f:
            f.write(img2pdf.convert(images))
        print(f"Created {output_pdf}")

def split_pdf_by_size(input_pdf, max_size_mb=100, output_prefix="split_"):
    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)
    part = 1
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        writer.add_page(page)
        # Write to temp file to check size
        temp_path = f"{output_prefix}{part}.pdf"
        with open(temp_path, "wb") as f:
            writer.write(f)
        size_mb = os.path.getsize(temp_path) / (1024 * 1024)
        if size_mb >= max_size_mb or i == total_pages - 1:
            print(f"Created {temp_path} ({size_mb:.2f} MB)")
            part += 1
            writer = PdfWriter()
        else:
            os.remove(temp_path)

if __name__ == "__main__":
    all_images = collect_images("IMAGES")
    compressed_images = compress_images_threaded(all_images)
    images_to_pdf(compressed_images, "merged_small.pdf")
    split_pdf_by_size("merged_small.pdf", max_size_mb=90)