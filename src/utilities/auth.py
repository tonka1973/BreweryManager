"""
User Authentication Module for Brewery Management System
Handles user login, session management, and basic security
"""

import hashlib
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict

from ..config.constants import DATETIME_FORMAT, USER_ROLES, PERMISSIONS

logger = logging.getLogger(__name__)


class User:
    """Represents a user in the system"""
    
    def __init__(self, user_id: str, username: str, full_name: str, 
                 role: str, is_active: bool = True):
        self.user_id = user_id
        self.username = username
        self.full_name = full_name
        self.role = role
        self.is_active = is_active
        self.permissions = PERMISSIONS.get(role, [])
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        return "all" in self.permissions or permission in self.permissions
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active
        }


class AuthManager:
    """
    Manages user authentication and sessions.
    Stores users in SQLite database.
    """
    
    def __init__(self, cache_manager):
        """
        Initialize the auth manager.
        
        Args:
            cache_manager: SQLiteCacheManager instance
        """
        self.cache = cache_manager
        self.current_user: Optional[User] = None
        self.session_start = None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA-256.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, full_name: str, 
                    role: str = "office") -> Optional[str]:
        """
        Create a new user.
        
        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            full_name: User's full name
            role: User role (admin, brewer, office, sales)
        
        Returns:
            User ID if successful, None if failed
        """
        try:
            self.cache.connect()
            
            # Check if username already exists
            existing = self.cache.get_all_records(
                'users', 
                f"username = '{username}'"
            )
            
            if existing:
                logger.error(f"Username '{username}' already exists")
                return None
            
            # Create new user
            user_id = str(uuid.uuid4())
            password_hash = self.hash_password(password)
            
            user_data = {
                'user_id': user_id,
                'username': username,
                'password_hash': password_hash,
                'full_name': full_name,
                'role': role,
                'is_active': 1,
                'created_date': datetime.now().strftime(DATETIME_FORMAT),
                'sync_status': 'pending'
            }
            
            self.cache.insert_record('users', user_data)
            self.cache.close()
            
            logger.info(f"User created: {username} ({role})")
            return user_id
            
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            return None
    
    def login(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user and create a session.
        
        Args:
            username: Username
            password: Plain text password
        
        Returns:
            User object if successful, None if failed
        """
        try:
            self.cache.connect()
            
            # Get user from database
            users = self.cache.get_all_records(
                'users',
                f"username = '{username}' AND is_active = 1"
            )
            
            if not users:
                logger.warning(f"Login failed: User '{username}' not found")
                self.cache.close()
                return None
            
            user_data = users[0]
            
            # Verify password
            password_hash = self.hash_password(password)
            if password_hash != user_data['password_hash']:
                logger.warning(f"Login failed: Invalid password for '{username}'")
                self.cache.close()
                return None
            
            # Create User object
            self.current_user = User(
                user_id=user_data['user_id'],
                username=user_data['username'],
                full_name=user_data['full_name'],
                role=user_data['role'],
                is_active=bool(user_data['is_active'])
            )
            
            # Update last login time
            self.cache.update_record(
                'users',
                user_data['user_id'],
                {'last_login': datetime.now().strftime(DATETIME_FORMAT)}
            )
            
            self.session_start = datetime.now()
            self.cache.close()
            
            logger.info(f"User logged in: {username} ({self.current_user.role})")
            return self.current_user
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return None
    
    def logout(self):
        """Log out the current user"""
        if self.current_user:
            logger.info(f"User logged out: {self.current_user.username}")
            self.current_user = None
            self.session_start = None
    
    def is_logged_in(self) -> bool:
        """Check if a user is currently logged in"""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[User]:
        """Get the currently logged in user"""
        return self.current_user
    
    def change_password(self, username: str, old_password: str, 
                       new_password: str) -> bool:
        """
        Change a user's password.
        
        Args:
            username: Username
            old_password: Current password
            new_password: New password
        
        Returns:
            True if successful, False if failed
        """
        try:
            # Verify old password by attempting login
            test_user = self.login(username, old_password)
            if not test_user:
                return False
            
            # Update password
            self.cache.connect()
            new_password_hash = self.hash_password(new_password)
            
            users = self.cache.get_all_records(
                'users',
                f"username = '{username}'"
            )
            
            if users:
                user_id = users[0]['user_id']
                self.cache.update_record(
                    'users',
                    user_id,
                    {
                        'password_hash': new_password_hash,
                        'sync_status': 'pending'
                    }
                )
                self.cache.close()
                logger.info(f"Password changed for user: {username}")
                return True
            
            self.cache.close()
            return False
            
        except Exception as e:
            logger.error(f"Failed to change password: {str(e)}")
            return False
    
    def get_all_users(self) -> list:
        """
        Get all users in the system.
        
        Returns:
            List of user dictionaries
        """
        try:
            self.cache.connect()
            users = self.cache.get_all_records('users', order_by='username')
            self.cache.close()
            
            # Remove password hashes before returning
            for user in users:
                user.pop('password_hash', None)
            
            return users
        except Exception as e:
            logger.error(f"Failed to get users: {str(e)}")
            return []
    
    def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID to deactivate
        
        Returns:
            True if successful, False if failed
        """
        try:
            self.cache.connect()
            self.cache.update_record(
                'users',
                user_id,
                {
                    'is_active': 0,
                    'sync_status': 'pending'
                }
            )
            self.cache.close()
            logger.info(f"User deactivated: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to deactivate user: {str(e)}")
            return False
    
    def create_default_admin(self) -> bool:
        """
        Create default admin user if no users exist.
        Username: admin
        Password: admin (should be changed after first login)
        
        Returns:
            True if created, False if users already exist
        """
        try:
            self.cache.connect()
            existing_users = self.cache.get_all_records('users')
            self.cache.close()
            
            if existing_users:
                return False
            
            # Create default admin
            user_id = self.create_user(
                username="admin",
                password="admin",
                full_name="System Administrator",
                role="admin"
            )
            
            if user_id:
                logger.info("Default admin user created (username: admin, password: admin)")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to create default admin: {str(e)}")
            return False
