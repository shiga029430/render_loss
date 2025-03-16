from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_display', 'order')  # category_displayをlist_displayに追加

    # カテゴリを表示名で表示
    def category_display(self, obj):
        return obj.get_category_display()

    category_display.short_description = 'カテゴリ'  # 表示名を設定
