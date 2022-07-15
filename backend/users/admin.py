from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    list_filter = ('username', 'email')


admin.site.register(Follow)
