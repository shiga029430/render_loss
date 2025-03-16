from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'order')

    # カテゴリを表示名で表示
    def category_display(self, obj):
        return obj.get_category_display()

    category_display.short_description = 'カテゴリ'
