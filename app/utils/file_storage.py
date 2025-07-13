import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image
import shutil
from datetime import datetime

class LocalFileStorage:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the file storage with Flask app"""
        self.upload_folder = app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
        self.max_file_size = app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        self.allowed_extensions = {
            'images': {'png', 'jpg', 'jpeg', 'gif'},
            'documents': {'pdf', 'doc', 'docx', 'txt'}
        }
        
        # Ensure upload directories exist
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create upload directories if they don't exist"""
        directories = [
            'profile_pictures',
            'resumes',
            'documents'
        ]
        
        for directory in directories:
            dir_path = os.path.join(self.upload_folder, directory)
            os.makedirs(dir_path, exist_ok=True)
            print(f"✅ Directory ensured: {dir_path}")
    
    def allowed_file(self, filename, file_type='images'):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions.get(file_type, set())
    
    def save_profile_picture(self, file, user_id):
        """Save profile picture with proper naming and resizing"""
        if not self.allowed_file(file.filename, 'images'):
            return None, "Invalid file type. Please upload an image."
        
        try:
            # Generate unique filename
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{file_ext}"
            
            # Full file path
            file_path = os.path.join(self.upload_folder, 'profile_pictures', filename)
            
            # Save original file temporarily
            temp_path = file_path + '.temp'
            file.save(temp_path)
            
            # Resize and optimize image
            self.resize_image(temp_path, file_path, max_size=(300, 300))
            
            # Remove temporary file
            os.remove(temp_path)
            
            # Return relative path for database storage
            relative_path = os.path.join('profile_pictures', filename).replace('\\', '/')
            return relative_path, None
            
        except Exception as e:
            return None, f"Failed to save file: {str(e)}"
    
    def save_resume(self, file, user_id):
        """Save resume file"""
        if not self.allowed_file(file.filename, 'documents'):
            return None, "Invalid file type. Please upload a PDF or DOC file."
        
        try:
            # Generate unique filename with timestamp
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{user_id}_resume_{timestamp}.{file_ext}"
            
            # Full file path
            file_path = os.path.join(self.upload_folder, 'resumes', filename)
            
            # Save file
            file.save(file_path)
            
            # Return relative path for database storage
            relative_path = os.path.join('resumes', filename).replace('\\', '/')
            return relative_path, None
            
        except Exception as e:
            return None, f"Failed to save file: {str(e)}"
    
    def resize_image(self, input_path, output_path, max_size=(300, 300)):
        """Resize image to maximum dimensions while maintaining aspect ratio"""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Resize image while maintaining aspect ratio
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save optimized image
                img.save(output_path, optimize=True, quality=85)
                
        except Exception as e:
            # If image processing fails, copy original file
            shutil.copy2(input_path, output_path)
    
    def delete_file(self, relative_path):
        """Delete a file from the upload directory"""
        try:
            full_path = os.path.join(self.upload_folder, relative_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception:
            return False
    
    def get_file_url(self, relative_path):
        """Get the URL for accessing the file"""
        if not relative_path or relative_path == 'default.jpg':
            return None
        return f"/static/uploads/{relative_path}"
    
    def file_exists(self, relative_path):
        """Check if file exists in upload directory"""
        if not relative_path:
            return False
        full_path = os.path.join(self.upload_folder, relative_path)
        return os.path.exists(full_path)

# Initialize storage instance
file_storage = LocalFileStorage()
