from django.db import models

# Create your models here.
import uuid  # pour le sign up et login#

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager #pour la bdd des users#
from django.db import models

# Create your models here.
class CustomUserManager(UserManager):
  
  def _create_user_(self, name, email, password,**extra_fields):
    if not email:
      raise ValueError('Adresse Email non valide')
    email = self.normalize_email(email)#methode de UserManager#
    user = self.model(email=email, name=name, **extra_fields )
    user.set_password(password)
    user.save(using=self._db)
    return user
  
  def create_user(self, name=None, email=None, password=None, **extra_fields):
    extra_fields.setdefault('is_staff', False)
    extra_fields.setdefault('is_superuser', False)
    return self._create_user_(name, email, password, **extra_fields)
  
  def create_superuser(self, name=None, email=None, password=None, **extra_fields):
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)
    return self._create_user_(name, email, password, **extra_fields)
  
class User(AbstractBaseUser, PermissionsMixin):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  email = models.EmailField(unique=True)
  name = models.CharField(max_length=200, blank=True, null=True)

  is_active = models.BooleanField(default=True)
  is_superuser = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)

  date_joined = models.DateTimeField(auto_now_add=True)
  last_login = models.DateTimeField(blank=True, null=True)

  objects = CustomUserManager()

  USERNAME_FIELD = 'email'
  EMAIL_FIELD = 'email'
  REQUIRED_FIELDS =['name']

  def __str__(self):
    return self.email