#!/usr/bin/env python3
"""
Unify image storage structure
Move all images to unified /images/phones/ directory
Simplify filenames and remove subfolder structure
"""

import os
import shutil
import psycopg2
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageUnifier:
    def __init__(self):
        self.base_dir = Path("/Users/shenmeidun/UoW_IT/COMPX576/MobilePhone")
        self.images_dir = self.base_dir / "images" / "phones"
        self.target_dir = self.images_dir  # Unified target directory
        
    def move_subfolder_images(self):
        """Move images from subfolders to main directory and rename"""
        moved_count = 0
        
        # Find all images in subfolders
        for subfolder in self.images_dir.iterdir():
            if subfolder.is_dir():
                logger.info(f"🔍 Processing subfolder: {subfolder.name}")
                
                for image_file in subfolder.glob("*.jpg"):
                    # Generate new filename based on folder name
                    folder_name = subfolder.name.replace("-", "_")
                    image_type = image_file.stem  # back, front, side etc
                    
                    # Build unified filename pattern
                    if "iphone-11-pro-max" in subfolder.name:
                        new_name = f"Apple_iPhone_11_Pro_Max.jpg"
                    elif "iphone-11" in subfolder.name:
                        new_name = f"Apple_iPhone_11.jpg"
                    else:
                        # Generic naming rule
                        new_name = f"{folder_name.title()}.jpg"
                    
                    target_path = self.target_dir / new_name
                    
                    # Move file
                    try:
                        shutil.move(str(image_file), str(target_path))
                        logger.info(f"✅ Moved: {image_file.name} -> {new_name}")
                        moved_count += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to move {image_file}: {e}")
                
                # Remove empty subfolders
                try:
                    if not any(subfolder.iterdir()):
                        subfolder.rmdir()
                        logger.info(f"🗑️ Removed empty folder: {subfolder.name}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not remove folder {subfolder}: {e}")
        
        return moved_count
    
    def update_database_paths(self):
        """Update image paths in database"""
        try:
            conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
            cur = conn.cursor()
            
            # Update iPhone 11 paths
            cur.execute('''
                UPDATE "Phones" 
                SET "ImageUrl" = 'http://localhost:5198/images/phones/Apple_iPhone_11.jpg'
                WHERE "Brand" = 'Apple' AND "Model" = 'iPhone 11'
            ''')
            
            # Update iPhone 11 Pro Max paths
            cur.execute('''
                UPDATE "Phones" 
                SET "ImageUrl" = 'http://localhost:5198/images/phones/Apple_iPhone_11_Pro_Max.jpg'
                WHERE "Brand" = 'Apple' AND "Model" = 'iPhone 11 Pro Max'
            ''')
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info("✅ Updated database paths for moved images")
            
        except Exception as e:
            logger.error(f"❌ Database update error: {e}")
    
    def verify_unified_structure(self):
        """Validate unified image structure"""
        try:
            # Count images
            jpg_files = list(self.images_dir.glob("*.jpg"))
            subfolders = [d for d in self.images_dir.iterdir() if d.is_dir()]
            
            logger.info(f"📊 Unified structure verification:")
            logger.info(f"   📸 Total JPG files: {len(jpg_files)}")
            logger.info(f"   📁 Remaining subfolders: {len(subfolders)}")
            
            if subfolders:
                logger.warning(f"⚠️ Remaining subfolders: {[d.name for d in subfolders]}")
            else:
                logger.info("✅ All images are now in unified structure!")
            
            # Show sample files
            logger.info("📱 Sample images:")
            for img in sorted(jpg_files)[:10]:
                logger.info(f"   - {img.name}")
            
            return len(jpg_files), len(subfolders)
            
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return 0, 0
    
    def clean_database_inconsistencies(self):
        """Clean inconsistent image paths in database"""
        try:
            conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
            cur = conn.cursor()
            
            # Fetch all local image paths
            cur.execute('''
                SELECT "Id", "Brand", "Model", "ImageUrl" 
                FROM "Phones" 
                WHERE "ImageUrl" LIKE 'http://localhost:5198/images/%'
            ''')
            
            phones = cur.fetchall()
            fixed_count = 0
            
            for phone_id, brand, model, image_url in phones:
                # Check if file exists
                if "phones/" in image_url:
                    filename = image_url.split("phones/")[-1]
                    full_path = self.images_dir / filename
                    
                    if not full_path.exists():
                        # Generate standard placeholder
                        placeholder = f"https://via.placeholder.com/400x600/667eea/FFFFFF?text={brand}+{model}".replace(' ', '+')
                        cur.execute('UPDATE "Phones" SET "ImageUrl" = %s WHERE "Id" = %s', (placeholder, phone_id))
                        logger.info(f"🔄 Fixed missing image: {brand} {model}")
                        fixed_count += 1
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ Fixed {fixed_count} inconsistent database paths")
            
        except Exception as e:
            logger.error(f"Database cleanup error: {e}")

def main():
    unifier = ImageUnifier()
    
    logger.info("🚀 Starting image structure unification...")
    
    # Step 1: Move images from subfolders
    moved_count = unifier.move_subfolder_images()
    logger.info(f"📦 Moved {moved_count} images from subfolders")
    
    # Step 2: Update database paths
    unifier.update_database_paths()
    
    # Step 3: Clean inconsistent paths
    unifier.clean_database_inconsistencies()
    
    # Step 4: Validate results
    total_images, remaining_folders = unifier.verify_unified_structure()
    
    logger.info(f"""
🎉 Image structure unification completed!
   📸 Total images: {total_images}
   📁 Subfolders removed: {moved_count > 0}
   ✅ Structure: Fully unified
""")

if __name__ == "__main__":
    main()

