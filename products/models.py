from django.db import models
from datetime import date

CATEGORY_CHOICES = [
    ('1', '菓子パン'),
    ('2', '食パン'),
    ('3', 'ブレッド他'),
    ('4', '惣菜・デニ'),
    ('5', 'ドーナツ'),
    ('6', '常温サンド'),
    ('7', '冷蔵サンド'),
    ('8', 'その他'),
]

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default='1')  # CharFieldを使用
    order = models.IntegerField(default=0, editable=False)  # 並べ替え用の順番フィールド
    quantity = models.PositiveIntegerField(default=0, editable=False)  # 在庫数

    def save(self, *args, **kwargs):
        # 新規作成の場合のみorderを設定
        if not self.pk:
            # 最大order値を取得して+1を設定
            max_order = Product.objects.filter(category=self.category).aggregate(models.Max('order'))['order__max']
            self.order = max_order + 1 if max_order is not None else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})*{self.quantity}"  # カテゴリー名を表示
    
    def delete(self, *args, **kwargs):
        # 削除時にorderを整理
        category = self.category
        super().delete(*args, **kwargs)
        Product.update_order_for_category(category)

    @staticmethod
    def update_order_for_category(category):
        """特定のカテゴリ内の商品のorderを整理するメソッド"""
        products = Product.objects.filter(category=category).order_by('order')
        for idx, product in enumerate(products):
            product.order = idx + 1
            product.save()
            
class Loss(models.Model):
    products = models.ManyToManyField(Product, related_name='losses')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        # 関連する商品の名前をカンマ区切りで表示
        product_names = ", ".join([product.name for product in self.products.all()])
        return f"ロス記録 ({self.date}): {product_names}"
