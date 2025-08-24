#!/usr/bin/env python3
"""
Script to create an admin user for the Upwork Proposal Generator system.
Run this script after setting up the database to create the first admin user.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User, UserRole

def create_admin_user():
    """Create an admin user"""
    
    # Load environment variables
    load_dotenv()
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Check if admin already exists
            existing_admin = User.objects(role=UserRole.ADMIN.value).first()
            if existing_admin:
                print(f"✅ Admin user already exists: {existing_admin.username}")
                return
            
            # Get admin details
            print("Creating admin user for Upwork Proposal Generator...")
            username = input("Enter admin username: ").strip()
            email = input("Enter admin email: ").strip()
            password = input("Enter admin password: ").strip()
            
            if not username or not email or not password:
                print("❌ All fields are required!")
                return
            
            # Check if username or email already exists
            if User.objects(username=username).first():
                print("❌ Username already exists!")
                return
            
            if User.objects(email=email).first():
                print("❌ Email already exists!")
                return
            
            # Create admin user
            admin_user = User(
                username=username,
                email=email,
                role=UserRole.ADMIN.value,
                is_active=True
            )
            admin_user.set_password(password)
            admin_user.save()
            
            print(f"✅ Admin user created successfully!")
            print(f"📧 Username: {username}")
            print(f"📧 Email: {email}")
            print(f"🔐 Password: [HIDDEN]")
            print(f"👑 Role: {UserRole.ADMIN.value}")
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")

def create_sample_bd_user():
    """Create a sample Business Developer user for testing"""
    
    with app.app_context():
        try:
            # Check if BD user already exists
            existing_bd = User.objects(username='bd_demo').first()
            if existing_bd:
                print(f"✅ Sample BD user already exists: {existing_bd.username}")
                return
            
            # Create sample BD user
            bd_user = User(
                username='bd_demo',
                email='bd@example.com',
                role=UserRole.BUSINESS_DEVELOPER.value,
                is_active=True
            )
            bd_user.set_password('demo123')
            bd_user.save()
            
            print(f"✅ Sample BD user created!")
            print(f"📧 Username: bd_demo")
            print(f"📧 Email: bd@example.com")
            print(f"🔐 Password: demo123")
            print(f"👤 Role: {UserRole.BUSINESS_DEVELOPER.value}")
            
        except Exception as e:
            print(f"❌ Error creating BD user: {e}")

if __name__ == '__main__':
    print("🚀 Upwork Proposal Generator - Admin Setup")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    try:
        create_admin_user()
        
        # Ask if user wants to create a sample BD user
        create_bd = input("\nCreate sample BD user for testing? (y/n): ").strip().lower()
        if create_bd == 'y':
            create_sample_bd_user()
        
        print("\n🎉 Setup completed!")
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")