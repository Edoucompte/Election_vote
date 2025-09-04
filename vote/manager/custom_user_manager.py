from django.contrib.auth.base_user import BaseUserManager
from vote.encryption import hashPassword

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fileds):
        if not email:
            raise ValueError("Email non fourni")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fileds)
        #user.set_password(password)
        user.password = hashPassword(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, **extra_fileds):
        extra_fileds.setdefault("is_staff", True)
        extra_fileds.setdefault("is_superuser", True)
        extra_fileds.setdefault("is_active", True)
        extra_fileds.setdefault("is_superviseur", True)
        #extra_fileds.setdefault("date_naissance", )

        if extra_fileds.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff to True")
        
        if extra_fileds.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser to True")
        return self.create_user(email, password, **extra_fileds)
