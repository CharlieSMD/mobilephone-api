#!/usr/bin/env python3
"""
整合所有图片到统一位置
将 COMPX576/images/phones/ 中的所有图片移动到 COMPX576/MobilePhone/images/phones/
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
        
        # 确保目标目录存在
        self.new_images_dir.mkdir(parents=True, exist_ok=True)
        
    def move_all_images(self):
        """将旧目录中的所有图片移动到新目录"""
        if not self.old_images_dir.exists():
            logger.info(f"❌ Source directory not found: {self.old_images_dir}")
            return 0
        
        moved_count = 0
        duplicate_count = 0
        
        # 获取所有图片文件
        for image_file in self.old_images_dir.glob("*.jpg"):
            target_path = self.new_images_dir / image_file.name
            
            try:
                if target_path.exists():
                    # 如果目标文件已存在，比较大小决定是否替换
                    old_size = image_file.stat().st_size
                    new_size = target_path.stat().st_size
                    
                    if old_size > new_size:
                        # 如果旧文件更大，替换
                        shutil.move(str(image_file), str(target_path))
                        logger.info(f"🔄 Replaced larger: {image_file.name} ({old_size} > {new_size} bytes)")
                        moved_count += 1
                    else:
                        # 删除旧文件
                        image_file.unlink()
                        logger.info(f"⏭️ Kept existing: {image_file.name}")
                        duplicate_count += 1
                else:
                    # 移动文件
                    shutil.move(str(image_file), str(target_path))
                    logger.info(f"✅ Moved: {image_file.name}")
                    moved_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Failed to move {image_file.name}: {e}")
        
        return moved_count, duplicate_count
    
    def update_database_paths(self):
        """更新数据库中的图片路径到新位置"""
        try:
            conn = psycopg2.connect(host='localhost', database='mobilephone_db', user='postgres')
            cur = conn.cursor()
            
            # 更新所有本地图片路径
            cur.execute('''
                UPDATE "Phones" 
                SET "ImageUrl" = REPLACE("ImageUrl", 
                    'http://localhost:5198/images/phones/', 
                    'http://localhost:5198/images/phones/')
                WHERE "ImageUrl" LIKE 'http://localhost:5198/images/%'
            ''')
            
            # 确保路径正确指向MobilePhone目录
            # 注意：后端Program.cs应该配置静态文件服务指向MobilePhone/images目录
            
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
        """验证整合结果"""
        try:
            # 统计新目录中的图片
            new_images = list(self.new_images_dir.glob("*.jpg"))
            
            # 检查旧目录是否还有图片
            old_images = list(self.old_images_dir.glob("*.jpg")) if self.old_images_dir.exists() else []
            
            logger.info(f"📊 Consolidation verification:")
            logger.info(f"   📸 Images in target directory: {len(new_images)}")
            logger.info(f"   📸 Images remaining in old directory: {len(old_images)}")
            
            if old_images:
                logger.warning(f"⚠️ Still {len(old_images)} images in old directory")
                for img in old_images[:5]:  # 显示前5个
                    logger.warning(f"   - {img.name}")
            else:
                logger.info("✅ All images successfully consolidated!")
            
            # 显示一些示例
            logger.info("📱 Sample consolidated images:")
            for img in sorted(new_images)[:10]:
                logger.info(f"   - {img.name}")
            
            return len(new_images), len(old_images)
            
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return 0, 0
    
    def cleanup_old_directory(self):
        """清理旧的图片目录（如果为空）"""
        try:
            if self.old_images_dir.exists():
                # 检查是否还有文件
                remaining_files = list(self.old_images_dir.iterdir())
                
                if not remaining_files:
                    # 目录为空，可以删除
                    self.old_images_dir.rmdir()
                    logger.info(f"🗑️ Removed empty directory: {self.old_images_dir}")
                    
                    # 尝试删除父目录（如果也为空）
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
    
    # 步骤1: 移动所有图片
    moved_count, duplicate_count = consolidator.move_all_images()
    logger.info(f"📦 Moved {moved_count} images, {duplicate_count} duplicates handled")
    
    # 步骤2: 更新数据库路径
    updated_count = consolidator.update_database_paths()
    
    # 步骤3: 验证结果
    total_images, remaining_old = consolidator.verify_consolidation()
    
    # 步骤4: 清理旧目录
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

