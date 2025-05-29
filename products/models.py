from django.db import models
# from datetime import datetime
from django.utils import timezone

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
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default='1')
    order = models.IntegerField(default=0, editable=False)  # 並べ替え用
    quantity = models.PositiveIntegerField(default=0)  # ロス数！編集可能にした！

    def save(self, *args, **kwargs):
        # 新規作成の場合のみorderを設定
        if not self.pk:
            # 最大order値を取得して+1を設定
            max_order = Product.objects.filter(category=self.category).aggregate(models.Max('order'))['order__max']
            self.order = max_order + 1 if max_order is not None else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})*{self.quantity}"
    
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
            
class LossRecord(models.Model):
    date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"ロス記録 ({self.date.strftime('%Y-%m-%d %H:%M')})"
            
class LossDetail(models.Model):
    loss_record = models.ForeignKey(LossRecord, on_delete=models.CASCADE, related_name='details')
    product_name = models.CharField(max_length=100)  # 商品名コピー
    product_category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)  # カテゴリコピー
    quantity = models.PositiveIntegerField()  # ロス数
    
    def __str__(self):
        category_display = dict(CATEGORY_CHOICES).get(self.product_category, '')
        return f"{self.product_name} ({category_display})*{self.quantity}"
    
    def get_product_category_display(self):
        return dict(CATEGORY_CHOICES).get(self.product_category, '')
