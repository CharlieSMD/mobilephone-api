#!/usr/bin/env python3
"""
Consolidate all images to a unified location
Move all images from COMPX576/images/phones/ to COMPX576/MobilePhone/images/phones/
"""

import os
import shutil
import psycopg2
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageConsolidator:
    def __init__(self):
        self.base_dir = Path("/Users/shenmeidun/UoW_IT/COMPX576")
        self.old_images_dir = self.base_dir / "images" / "phones"
        self.new_images_dir = self.base_dir / "MobilePhone" / "images" / "phones"
        
        # Ensure destination directory exists
        self.new_images_dir.mkdir(parents=True, exist_ok=True)
        
    def move_all_images(self):
        """Move all images from old directory to new directory"""
        if not self.old_images_dir.exists():
            logger.info(f"❌ Source directory not found: {self.old_images_dir}")
            return 0
        
        moved_count = 0
        duplicate_count = 0
        
        # Get all image files
        for image_file in self.old_images_dir.glob("*.jpg"):
            target_path = self.new_images_dir / image_file.name
            
            try:
                if target_path.exists():
                    # If destination exists, compare size to decide replacement
                    old_size = image_file.stat().st_size
                    new_size = target_path.stat().st_size
                    
                    if old_size > new_size:
                        # Replace if old file is larger
                        shutil.move(str(image_file), str(target_path))
                        logger.info(f"🔄 Replaced larger: {image_file.name} ({old_size} > {new_size} bytes)")
                        moved_count += 1
                    else:
                        # Delete old file
                        image_file.unlink()
                        logger.info(f"⏭️ Kept existing: {image_file.name}")
                        duplicate_count += 1
                else:
                    # Move file
                    shutil.move(str(image_file), str(target_path))
                    logger.info(f"✅ Moved: {image_file.name}")
                    moved_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Failed to move {image_file.name}: {e}")
        
        return moved_count, duplicate_count
    
    def update_database_paths(self):
        """Update image paths in database to new location"""
        try:
            conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
            cur = conn.cursor()
            
            # Update all local image paths
            cur.execute('''
                UPDATE "Phones" 
                SET "ImageUrl" = REPLACE("ImageUrl", 
                    'http://localhost:5198/images/phones/', 
                    'http://localhost:5198/images/phones/')
                WHERE "ImageUrl" LIKE 'http://localhost:5198/images/%'
            ''')
            
            # Ensure path points to MobilePhone directory
            # Note: Backend Program.cs should serve static files from MobilePhone/images
            
            updated_count = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ Updated {updated_count} database paths")
            return updated_count
            
        except Exception as e:
            logger.error(f"❌ Database update error: {e}")
            return 0
    
    def verify_consolidation(self):
        """Verify consolidation results"""
        try:
            # Count images in new directory
            new_images = list(self.new_images_dir.glob("*.jpg"))
            
            # Check if old directory still has images
            old_images = list(self.old_images_dir.glob("*.jpg")) if self.old_images_dir.exists() else []
            
            logger.info(f"📊 Consolidation verification:")
            logger.info(f"   📸 Images in target directory: {len(new_images)}")
            logger.info(f"   📸 Images remaining in old directory: {len(old_images)}")
            
            if old_images:
                logger.warning(f"⚠️ Still {len(old_images)} images in old directory")
                for img in old_images[:5]:  # Show first 5
                    logger.warning(f"   - {img.name}")
            else:
                logger.info("✅ All images successfully consolidated!")
            
            # Show some examples
            logger.info("📱 Sample consolidated images:")
            for img in sorted(new_images)[:10]:
                logger.info(f"   - {img.name}")
            
            return len(new_images), len(old_images)
            
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return 0, 0
    
    def cleanup_old_directory(self):
        """Clean up old image directories (if empty)"""
        try:
            if self.old_images_dir.exists():
                # Check if any files remain
                remaining_files = list(self.old_images_dir.iterdir())
                
                if not remaining_files:
                    # Directory is empty, safe to delete
                    self.old_images_dir.rmdir()
                    logger.info(f"🗑️ Removed empty directory: {self.old_images_dir}")
                    
                    # Try deleting parent directory (if empty as well)
                    parent_dir = self.old_images_dir.parent
                    if parent_dir.name == "images" and not any(parent_dir.iterdir()):
                        parent_dir.rmdir()
                        logger.info(f"🗑️ Removed empty parent directory: {parent_dir}")
                else:
                    logger.info(f"📁 Old directory still contains {len(remaining_files)} items")
                    
        except Exception as e:
            logger.warning(f"⚠️ Cleanup warning: {e}")

def main():
    consolidator = ImageConsolidator()
    
    logger.info("🚀 Starting image consolidation...")
    logger.info(f"   📂 From: {consolidator.old_images_dir}")
    logger.info(f"   📂 To: {consolidator.new_images_dir}")
    
    # Step 1: Move all images
    moved_count, duplicate_count = consolidator.move_all_images()
    logger.info(f"📦 Moved {moved_count} images, {duplicate_count} duplicates handled")
    
    # Step 2: Update database paths
    updated_count = consolidator.update_database_paths()
    
    # Step 3: Verify results
    total_images, remaining_old = consolidator.verify_consolidation()
    
    # Step 4: Clean old directories
    consolidator.cleanup_old_directory()
    
    logger.info(f"""
🎉 Image consolidation completed!
   📸 Total images: {total_images}
   📦 Moved: {moved_count}
   🔄 Database updated: {updated_count}
   📁 All images now in: MobilePhone/images/phones/
""")

if __name__ == "__main__":
    main()

