import os
from io import BytesIO
from PIL import Image as PilImage
from django.core.files.base import ContentFile


def optimize_image(image_field, resize_width=None):
    """
    Optimizes a django ImageField file:
    - Converts to RGB
    - Optionally resizes (if resize_width provided and width > resize_width)
    - Compresses to JPEG (quality=80)

    Args:
        image_field: The Django ImageField file object
        resize_width: Optional integer width to resize down to

    Returns:
        tuple (filename, ContentFile) if optimized successfully
        None if no processing needed or error
    """
    if not image_field:
        return None

    try:
        # Open image using Pillow
        img = PilImage.open(image_field)

        # Convert to RGB (standard for JPEG)
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Resize if requested and needed
        if resize_width and img.width > resize_width:
            ratio = resize_width / float(img.width)
            height = int((float(img.height) * float(ratio)))
            img = img.resize((resize_width, height), PilImage.Resampling.LANCZOS)

        # Save to buffer
        output = BytesIO()
        img.save(output, format="JPEG", quality=80, optimize=True)
        output.seek(0)

        # Generate new filename
        original_name = os.path.basename(image_field.name)
        name_base, _ = os.path.splitext(original_name)

        # Clean up filename (avoid double extensions like image.png.jpg)
        if name_base.lower().endswith(".jpg") or name_base.lower().endswith(".jpeg"):
            pass

        new_filename = f"{name_base}.jpg"

        return new_filename, ContentFile(output.read())

    except Exception as e:
        # In case of error (e.g. invalid image file), return None
        print(f"Error optimizing image: {e}")
        return None
