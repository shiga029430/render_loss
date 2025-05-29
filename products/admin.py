from django.contrib import admin
from .models import Product, LossRecord, LossDetail

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_display', 'order')  # category_displayをlist_displayに追加

    # カテゴリを表示名で表示
    def category_display(self, obj):
        return obj.get_category_display()

    category_display.short_description = 'カテゴリ'  # 表示名を設定

@admin.register(LossRecord)
class LossAdmin(admin.ModelAdmin):
    list_display = ('date',)  # カスタムメソッドをlist_displayに追加
    list_display_links = ('date',)  # リンクとして扱うフィールドを指定
    # list_editable = ()  # 日付を編集可能に設定

    def get_products(self, obj):
        return ", ".join([product.name for product in obj.products.all()])  # 関連する商品の名前を表示

    get_products.short_description = '商品'

    def get_quantities(self, obj):
        # 中間テーブルを使用している場合、数量を取得するロジックを記述
        return ", ".join([str(product.quantity) for product in obj.products.all()])

    get_quantities.short_description = '数量'
    
admin.site.register(LossDetail)
