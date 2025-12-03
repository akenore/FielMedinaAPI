import os
from io import BytesIO
from PIL import Image as PilImage
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class OptimizedImageModel(models.Model):
    """
    Abstract base model that provides automatic image optimization.
    Resizes images to 1920px max width for main image and 500px for mobile.
    Converts all images to JPEG format with 80% quality.
    """
    image = models.ImageField(upload_to='images/')
    image_mobile = models.ImageField(upload_to='images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if self.image and (not self.pk or hasattr(self.image, 'file')):
            try:
                img = PilImage.open(self.image)
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Process main image (max width 1920px)
                img_main = img.copy()
                if img_main.width > 1920:
                    ratio = 1920 / float(img_main.width)
                    height = int((float(img_main.height) * float(ratio)))
                    img_main = img_main.resize((1920, height), PilImage.Resampling.LANCZOS)
                
                output_main = BytesIO()
                img_main.save(output_main, format='JPEG', quality=80)
                output_main.seek(0)
                
                original_name = os.path.basename(self.image.name)
                name_base, _ = os.path.splitext(original_name)
                filename = f"{name_base}.jpg"
                
                self.image = ContentFile(output_main.read(), name=filename)

                # Process mobile image (max width 500px)
                img_mobile = img.copy()
                if img_mobile.width > 500:
                    ratio = 500 / float(img_mobile.width)
                    height = int((float(img_mobile.height) * float(ratio)))
                    img_mobile = img_mobile.resize((500, height), PilImage.Resampling.LANCZOS)
                
                output_mobile = BytesIO()
                img_mobile.save(output_mobile, format='JPEG', quality=80)
                output_mobile.seek(0)
                
                self.image_mobile = ContentFile(output_mobile.read(), name=f"mobile_{filename}")
                
                # Try to delete old file if it exists
                try:
                    if self.image.storage.exists(self.image.name):
                        self.image.storage.delete(self.image.name)
                except Exception:
                    pass
                
            except Exception as e:
                print(f"Error processing image: {e}")
                pass

        super().save(*args, **kwargs)


@receiver(post_delete)
def cleanup_optimized_image_files(sender, instance, **kwargs):
    """Delete image files when an OptimizedImageModel instance is deleted."""
    # Only process if the sender is a subclass of OptimizedImageModel
    if not issubclass(sender, OptimizedImageModel):
        return
    
    if hasattr(instance, 'image') and instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)
        
    if hasattr(instance, 'image_mobile') and instance.image_mobile and os.path.isfile(instance.image_mobile.path):
        os.remove(instance.image_mobile.path)
            
    try:
        if hasattr(instance, 'image') and instance.image:
            directory = os.path.dirname(instance.image.path)
            if os.path.exists(directory) and not os.listdir(directory):
                os.rmdir(directory)
    except Exception:
        pass
