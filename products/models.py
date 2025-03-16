from django.db import models

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
    quantity = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # 新規作成の場合のみorderを設定
        if not self.pk:
            # 最大order値を取得して+1を設定
            max_order = Product.objects.filter(category=self.category).aggregate(models.Max('order'))['order__max']
            self.order = max_order + 1 if max_order is not None else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"  # カテゴリー名を表示

    @staticmethod
    def update_order_for_category(category):
        """特定のカテゴリ内の商品のorderを整理するメソッド"""
        products = Product.objects.filter(category=category).order_by('order')
        for idx, product in enumerate(products):
            product.order = idx + 1
            product.save()
