from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.db import transaction
from django.db import models
from .models import Product, CATEGORY_CHOICES

class ProductListView(View):
    def get(self, request, *args, **kwargs):
        categories = {key: [] for key, _ in CATEGORY_CHOICES}
        products = Product.objects.all()
        for product in products:
            categories[product.category].append(product)
        return render(request, 'products/product_list.html', {
            'categories': categories,
            'category_choices': dict(CATEGORY_CHOICES)  # カテゴリ選択肢を渡す
        })

    def post(self, request, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            quantity = request.POST.get(f'quantity_{product.id}')
            if quantity:
                product.quantity = int(quantity)
            else:
                product.quantity = 0
            product.save()  # 数量を更新
        return redirect('products:product_display')
    

class ProductDisplayView(TemplateView):
    template_name = 'products/product_display.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 数量が1以上の商品をフィルタリングして表示
        context['products'] = Product.objects.filter(quantity__gte=1)
        return context

class DisplayEditView(View):
    def get(self, request):
        products = Product.objects.all().order_by('order')  # 商品をorder順に並べる
        categories = {key: [] for key, _ in CATEGORY_CHOICES}
        
        for product in products:
            categories[product.category].append(product)

        return render(request, 'products/display_edit.html', {
            'products': products,
            'categories': categories,
            'category_choices': dict(CATEGORY_CHOICES),
        })
    

    def post(self, request):
        # 隠しフィールドで送信された product_id と action を受け取る
        product_id = request.POST.get('product_id')  # 商品ID
        action = request.POST.get('action')  # 'up' または 'down'
        category = request.POST.get('category')  # カテゴリ
        product_name = request.POST.get('product_name')
        
        if action == 'add' and category and product_name:
            max_order = Product.objects.filter(category=category).aggregate(models.Max('order'))['order__max'] or 0
            Product.objects.create(name=product_name, category=category, order=max_order + 1)
            return redirect('products:display_edit')

        try:
            product = Product.objects.get(id=product_id)

            # カテゴリ内の商品だけを対象に並べ替えを行う
            if category:
                # 上に移動する処理
                if action == 'up' and product.order > 1:
                    swap_product = Product.objects.filter(category=category, order__lt=product.order).order_by('-order').first()
                    if swap_product:
                        product.order, swap_product.order = swap_product.order, product.order
                        product.save()
                        swap_product.save()

                # 下に移動する処理
                elif action == 'down':
                    swap_product = Product.objects.filter(category=category, order__gt=product.order).order_by('order').first()
                    if swap_product:
                        product.order, swap_product.order = swap_product.order, product.order
                        product.save()
                        swap_product.save()

        except Product.DoesNotExist:
            pass

        return redirect('products:display_edit')  # 並べ替え後にこのページを再表示