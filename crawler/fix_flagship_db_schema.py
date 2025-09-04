#!/usr/bin/env python3
"""
Fix database schema for flagship phones
Expand field lengths to accommodate detailed specifications from GSMArena
"""

import psycopg2

def fix_database_schema():
    """Fix database field lengths for flagship phone specifications"""
    print("🔧 Fixing database schema for flagship phones")
    
    connection_string = "host=localhost dbname=mobilephone_db user=postgres password=postgres"
    
    # Updated field lengths based on GSMArena data
    alter_commands = [
        'ALTER TABLE "Phones" ALTER COLUMN "Processor" TYPE VARCHAR(200)',
        'ALTER TABLE "Phones" ALTER COLUMN "Os" TYPE VARCHAR(150)', 
        'ALTER TABLE "Phones" ALTER COLUMN "NetworkType" TYPE VARCHAR(200)',
        'ALTER TABLE "Phones" ALTER COLUMN "ChargingPower" TYPE VARCHAR(100)',
        'ALTER TABLE "Phones" ALTER COLUMN "WaterResistance" TYPE VARCHAR(150)',
        'ALTER TABLE "Phones" ALTER COLUMN "Material" TYPE VARCHAR(300)',
        'ALTER TABLE "Phones" ALTER COLUMN "Colors" TYPE VARCHAR(500)',
        'ALTER TABLE "Phones" ALTER COLUMN "Dimensions" TYPE VARCHAR(150)',
        'ALTER TABLE "Phones" ALTER COLUMN "Storage" TYPE VARCHAR(200)',
        'ALTER TABLE "Phones" ALTER COLUMN "Ram" TYPE VARCHAR(100)',
        'ALTER TABLE "Phones" ALTER COLUMN "Camera" TYPE VARCHAR(300)',
        'ALTER TABLE "Phones" ALTER COLUMN "Battery" TYPE VARCHAR(150)',
        'ALTER TABLE "Phones" ALTER COLUMN "ScreenSize" TYPE VARCHAR(150)',
        'ALTER TABLE "Phones" ALTER COLUMN "ImageFront" TYPE VARCHAR(500)',
        'ALTER TABLE "Phones" ALTER COLUMN "ImageBack" TYPE VARCHAR(500)',
        'ALTER TABLE "Phones" ALTER COLUMN "ImageSide" TYPE VARCHAR(500)',
    ]
    
    try:
        with psycopg2.connect(connection_string) as conn:
            with conn.cursor() as cur:
                print("Expanding field lengths...")
                
                for i, command in enumerate(alter_commands, 1):
                    try:
                        cur.execute(command)
                        field_name = command.split('"')[1]
                        new_length = command.split('VARCHAR(')[1].split(')')[0]
                        print(f"  ✅ {i:2d}. {field_name}: expanded to VARCHAR({new_length})")
                    except Exception as e:
                        field_name = command.split('"')[1] if '"' in command else "unknown"
                        print(f"  ❌ {i:2d}. {field_name}: {e}")
                
                conn.commit()
                print("\n🎉 Database schema updated successfully!")
                
                # Verify current schema
                cur.execute('''
                    SELECT column_name, data_type, character_maximum_length 
                    FROM information_schema.columns 
                    WHERE table_name = 'Phones' 
                    AND data_type = 'character varying'
                    ORDER BY column_name
                ''')
                
                print("\n📊 Current field lengths:")
                for row in cur.fetchall():
                    column_name, data_type, max_length = row
                    print(f"  {column_name}: {data_type}({max_length})")
                
    except Exception as e:
        print(f"❌ Database operation failed: {e}")

if __name__ == "__main__":
    fix_database_schema()
