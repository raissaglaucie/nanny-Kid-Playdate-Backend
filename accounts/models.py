from django.contrib.auth.models import User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

"""
User extends user model (first name, last name, phone number, email, id), following (many to one field to Profile)
"""

class ModifiedUser(User):
    phone_num = PhoneNumberField(null=True, blank=True, unique=False)




#user nao e criado do zero, ele ta fazendo heranca de clase padrao do django (user)