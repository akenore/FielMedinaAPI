import os
import django
from io import BytesIO
from PIL import Image as PilImage
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from guard.models import Location, Image

def verify():
    # Setup
    loc = Location.objects.create(name="Cleanup Test Location", longitude=0.0, latitude=0.0)
    
    # Create dummy image
    img_data = BytesIO()
    image = PilImage.new('RGB', (100, 100), color='blue')
    image.save(img_data, format='JPEG')
    img_data.seek(0)
    
    # Create Image instance
    img_instance = Image(location=loc)
    img_instance.image.save('test_cleanup.jpg', ContentFile(img_data.read()))
    # img_instance.save() # Redundant, called by image.save()
    
    # Get paths
    path_main = img_instance.image.path
    path_mobile = img_instance.image_mobile.path
    
    print(f"Created files:\n{path_main}\n{path_mobile}")
    
    # Verify files exist
    assert os.path.exists(path_main)
    assert os.path.exists(path_mobile)
    
    # Delete Location via QuerySet (simulating Admin bulk delete)
    print("Deleting Location via QuerySet...")
    Location.objects.filter(id=loc.id).delete()
    
    # Verify files are gone
    if not os.path.exists(path_main):
        print("Main image deleted successfully.")
    else:
        print("ERROR: Main image still exists.")
        
    if not os.path.exists(path_mobile):
        print("Mobile image deleted successfully.")
    else:
        print("ERROR: Mobile image still exists.")
        
    assert not os.path.exists(path_main)
    assert not os.path.exists(path_mobile)
    
    # Verify directory is gone
    directory = os.path.dirname(path_main)
    if not os.path.exists(directory):
        print("Directory deleted successfully.")
    else:
        print("ERROR: Directory still exists.")
        # assert not os.path.exists(directory) # Optional: strict check
    
    print("Verification successful!")

if __name__ == "__main__":
    verify()
