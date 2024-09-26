from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class Amenity(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Hotel(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="hotel_images/",null=True, blank=True)
    amenities = models.ManyToManyField(Amenity)  # Could be a JSONField or a many-to-many relationship for structured data
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='Not provided')
    email = models.EmailField(default='Not provided')
    phone = models.CharField(max_length=15, default='Not provided')
    address = models.CharField(max_length=255,  default='Not provided')
    location = models.CharField(max_length=100, default='Not provided')
    amenities = models.ManyToManyField(Amenity)
    rating = models.DecimalField( default=0.0,max_digits=3, decimal_places=2,)
    preferences = models.JSONField(default=dict)  # Storing user preferences in JSON format
    image = models.ImageField(upload_to="user_images/", null=True, blank=True, default='default_image.jpg') # Set default image path

    
class Review(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} on {self.hotel.name}'



class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    