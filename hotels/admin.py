from django.contrib import admin
from .models import Hotel, Review, UserProfile, Amenity, Contact

# Register your models here.

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'description', 'image', 'display_amenities', 'price_per_night', 'rating')
    search_fields = ('name', 'location')

    def display_amenities(self, obj):
        return ", ".join([amenity.name for amenity in obj.amenities.all()])

    display_amenities.short_description = 'Amenities'

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'user', 'rating', 'comment', 'created_at')
    search_fields = ('hotel__name', 'user__username')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferences', 'image')
    search_fields = ('user__username', 'preferences')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'message', 'created_at')
    search_fields =('name', 'name')
