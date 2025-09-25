#!/usr/bin/env python3
"""
Initialize directories and database for Velayne project.

This script creates the necessary directories (logs/, data/, models/) 
and initializes the database using SQLAlchemy's Base.metadata.create_all.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from infra.config import settings
from infra.db import create_tables, init_db
from infra.encryption import generate_encryption_key


def create_directories():
    """Create necessary directories for the application."""
    directories = [
        settings.logs_dir,
        settings.data_dir,
        settings.models_dir,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def check_env_file():
    """Check if .env file exists and create it if needed."""
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists():
        print("⚠️  .env file not found")
        
        if env_example.exists():
            print("📋 Copying .env.example to .env")
            with open(env_example, 'r') as example:
                content = example.read()
            
            # Generate a new encryption key if not present
            if "your-fernet-encryption-key-here" in content:
                new_key = generate_encryption_key()
                content = content.replace("your-fernet-encryption-key-here", new_key)
                print(f"🔐 Generated new encryption key: {new_key}")
            
            with open(env_file, 'w') as env:
                env.write(content)
            
            print("✓ Created .env file from .env.example")
        else:
            print("❌ No .env.example file found to copy from")
            return False
    else:
        print("✓ .env file exists")
    
    return True


async def initialize_database():
    """Initialize the database by creating all tables."""
    try:
        print("🗄️  Initializing database...")
        
        # For initialization, use synchronous SQLite to ensure it's written to disk
        if "sqlite" in settings.database_url:
            # Extract path from the URL
            db_path = settings.database_url.split("///")[-1]
            
            # Create database using synchronous SQLite
            import sqlite3
            from sqlalchemy import create_engine
            
            # Create synchronous engine for initialization
            sync_url = settings.database_url.replace("sqlite+aiosqlite://", "sqlite://")
            sync_engine = create_engine(sync_url)
            
            # Import models to register them with Base
            from infra.models import Base
            
            # Create tables synchronously
            Base.metadata.create_all(sync_engine)
            sync_engine.dispose()
            
            # Verify the database file was created
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                print(f"✓ Database tables created successfully")
                print(f"✓ Database file created at: {db_path} ({size} bytes)")
            else:
                print(f"⚠️  Database file not found at: {db_path}")
                return False
        else:
            # For non-SQLite databases, use async method
            init_db()
            await create_tables()
            print("✓ Database tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_success_message():
    """Print success message with next steps."""
    print("\n" + "="*60)
    print("🎉 Velayne initialization completed successfully!")
    print("="*60)
    print("📁 Created directories:")
    print(f"   • {settings.logs_dir}")
    print(f"   • {settings.data_dir}")
    print(f"   • {settings.models_dir}")
    print("\n🗄️  Database initialized with tables:")
    print("   • users")
    print("   • subscriptions")
    print("   • payments")
    print("   • settings")
    print("   • api_keys")
    print("   • workers")
    print("   • event_logs")
    print("   • achievements")
    print(f"\n📋 Configuration loaded from: {settings.database_url}")
    print("\n🚀 Next steps:")
    print("   1. Review and update your .env file")
    print("   2. Install dependencies: pip install -r requirements.txt")
    print("   3. Run tests to verify setup")
    print("="*60)


async def main():
    """Main initialization function."""
    print("🚀 Starting Velayne initialization...")
    print(f"📂 Working directory: {project_root}")
    
    # Check and create .env file
    if not check_env_file():
        print("❌ Environment setup failed")
        return False
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Initialize database
    print(f"\n🗄️  Database URL: {settings.database_url}")
    success = await initialize_database()
    
    if success:
        print_success_message()
        return True
    else:
        print("❌ Initialization failed")
        return False


if __name__ == "__main__":
    # Run the initialization
    success = asyncio.run(main())
    sys.exit(0 if success else 1)