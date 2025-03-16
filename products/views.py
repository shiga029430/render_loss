from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from .models import Product, CATEGORY_CHOICES

class ProductListView(View):
    def get(self, request, *args, **kwargs):
        categories = {key: [] for key, _ in CATEGORY_CHOICES}
        products = Product.objects.all()
        for product in products:
            categories[product.category].append(product)
        return render(request, 'products/product_list.html', {'categories': categories})

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
        # 数量が1以上の商品をフィルタリング
        context['products'] = Product.objects.filter(quantity__gte=1)
        return context

class DisplayEditView(View):
    def get(self, request):
        products = Product.objects.all().order_by('order')  # 商品をorder順に並べる
        return render(request, 'products/display_edit.html', {'products': products})

    def post(self, request):
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')

        try:
            product = Product.objects.get(id=product_id)

            # 並べ替えの対象商品を正しく取得できているか確認
            print(f"Product selected: {product.name} (ID: {product.id}, order: {product.order})")

            # 上に移動する処理
            if action == 'up' and product.order > 1:
                # 上の位置にある商品を取得
                swap_product = Product.objects.filter(order__lt=product.order).order_by('-order').first()
                if swap_product:
                    print(f"Swapping {product.name} (ID: {product.id}) with {swap_product.name} (ID: {swap_product.id})")
                    # 並べ替え
                    product.order, swap_product.order = swap_product.order, product.order
                    product.save()
                    swap_product.save()

            # 下に移動する処理
            elif action == 'down':
                # 下の位置にある商品を取得
                swap_product = Product.objects.filter(order__gt=product.order).order_by('order').first()
                if swap_product:
                    print(f"Swapping {product.name} (ID: {product.id}) with {swap_product.name} (ID: {swap_product.id})")
                    # 並べ替え
                    product.order, swap_product.order = swap_product.order, product.order
                    product.save()
                    swap_product.save()

        except Product.DoesNotExist:
            pass

        return redirect('display_edit')  # 並べ替え後にこのページを再表示