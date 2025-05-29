from datetime import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.core.management import call_command
from django.db import transaction
from django.db import models
from .models import Product, CATEGORY_CHOICES, LossRecord, LossDetail

class ProductListView(View):
    def get(self, request, *args, **kwargs):
        categories = {key: [] for key, _ in CATEGORY_CHOICES}
        products = Product.objects.all().order_by('order')
        for product in products:
            categories[product.category].append(product)
        return render(request, 'products/product_list.html', {
            'categories': categories,
            'category_choices': dict(CATEGORY_CHOICES)  # カテゴリ選択肢を渡す
        })

    def post(self, request, *args, **kwargs):
            # フォームからのデータでProduct.quantityを更新（これ足りないかも）
        for key, value in request.POST.items():
            if key.startswith('quantity_') and value:
                product_id = key.split('_')[1]
                try:
                    product = Product.objects.get(id=product_id)
                    product.quantity = int(value)
                    product.save()
                except (Product.DoesNotExist, ValueError):
                    continue
        # ロスレコード作成
        loss_record = LossRecord.objects.create()
        
        # 数量が入力されている商品だけ記録
        for product in Product.objects.all():
            if product.quantity > 0:  # Productモデルに記録されたロス数を使う
                LossDetail.objects.create(
                    loss_record=loss_record,
                    product_name=product.name,
                    product_category=product.category,
                    quantity=product.quantity
                )
                # ロス記録後はリセット(しない)
                # product.quantity = 0
                # product.save()
        
        return redirect('products:product_display')
    

class ProductDisplayView(TemplateView):
    template_name = 'products/product_display.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 最新のロスレコードを取得
        latest_loss = LossRecord.objects.order_by('-date').first()
        
        if latest_loss:
            # 最新ロスレコードの詳細を取得
            context['loss_record'] = latest_loss
            context['loss_details'] = latest_loss.details.all().order_by('product_category')
        else:
            # ロスレコードがない場合は通常通りProductの数量で表示
            context['products'] = Product.objects.filter(quantity__gte=1).order_by('category', 'order')
        
        return context

class DisplayEditView(View):
    def get(self, request):
        products = Product.objects.all().order_by('order')
        categories = {key: [] for key, _ in CATEGORY_CHOICES}

        for product in products:
            categories[product.category].append(product)

        return render(request, 'products/display_edit.html', {
            'products': products,
            'categories': categories,
            'category_choices': dict(CATEGORY_CHOICES),
        })

    # @transaction.atomic
    def post(self, request):
        print("postデータ",request.POST)
        action = request.POST.get('action')
        category = request.POST.get('category')
        product_name = request.POST.get('product_name')
        
        if action == 'add' and category and product_name:
            max_order = Product.objects.filter(category=category).aggregate(models.Max('order'))['order__max'] or 0
            new_product = Product.objects.create(name=product_name, category=category, order=max_order + 1)
            print(f"new_product: {new_product}")
            return redirect('products:display_edit')
            
        
        if action == 'reorder':
            with transaction.atomic():
                for key, value in request.POST.items():
                    if not key.startswith('orders[') or not key.endswith(']'):
                        continue
                    try:
                        product_id = int(key.replace('orders[','').replace(']',''))
                        new_order_input = int(value)
                        
                        product = Product.objects.get(id=product_id)
                        old_order = product.order
                        category = product.category
                        
                        max_order = Product.objects.filter(category=category).count()
                        
                        want_last_position = (new_order_input >= max_order)
                        # new_order = max(1,min(new_order, max_order))
                       
                        if want_last_position:
                            if old_order == max_order:
                                continue
                            Product.objects.filter(
                                category=category,
                                order__gt=old_order,
                                order__lte=max_order
                            ).update(order=models.F('order') - 1)
                            
                            product.order = max_order
                            product.save()
                        else:
                            new_order = max(1,min(new_order_input, max_order))
                            
                            if old_order == new_order:
                                continue
                            
                            if old_order > new_order:
                                Product.objects.filter(
                                    category=category,
                                    order__lt=old_order,
                                    order__gte=new_order
                                ).update(order=models.F('order') + 1)
                            elif old_order < new_order:
                                Product.objects.filter(
                                    category=category,
                                    order__gt=old_order,
                                    order__lte=new_order
                                ).update(order=models.F('order') - 1)
                            product.order = new_order
                            product.save()
                    except(ValueError, Product.DoesNotExist):
                        continue
                # call_command('export_products', 'products.txt')
            return redirect('products:display_edit')
        
        if '-' in action:
            action, product_id = action.split('-')
        else:
            product_id = request.POST.get('product_id')
        # product_id = request.POST.get('product_id')
            
        category = request.POST.get('category')
        product_name = request.POST.get('product_name')
        new_order = request.POST.get('new_order')

        try:
            product = Product.objects.get(id=product_id)

            # 上下移動の処理
            if action == 'up' and product.order > 1:
                swap_product = Product.objects.filter(
                    category=product.category,
                    order__lt=product.order
                ).order_by('-order').first()
                if swap_product:
                    product.order, swap_product.order = swap_product.order, product.order
                    product.save()
                    swap_product.save()

            elif action == 'down':
                swap_product = Product.objects.filter(
                    category=product.category,
                    order__gt=product.order
                ).order_by('order').first()
                if swap_product:
                    product.order, swap_product.order = swap_product.order, product.order
                    product.save()
                    swap_product.save()

            # 順番変更処理（直接入力対応）
            elif action == 'reorder' and new_order:
                try:
                    new_order = int(new_order)
                except ValueError:
                    new_order = product.order
                    
                max_order = Product.objects.filter(category=product.category).count()
                if new_order < 1:
                    new_order = 1
                elif new_order > max_order:
                    new_order = max_order

                with transaction.atomic():
                    # 他の商品をシフトする
                    if product.order > new_order:
                        Product.objects.filter(
                            category=product.category,
                            order__lt=product.order,
                            order__gte=new_order
                        ).update(order=models.F('order') + 1)
                    elif product.order < new_order:
                        Product.objects.filter(
                            category=product.category,
                            order__gt=product.order,
                            order__lte=new_order
                        ).update(order=models.F('order') - 1)

                    # 商品の順番を更新
                    product.order = new_order
                    product.save()

            # 商品追加処理
            elif action == 'add' and category and product_name:
                max_order = Product.objects.filter(category=category).aggregate(models.Max('order'))['order__max'] or 0
                new_product = Product.objects.create(name=product_name, category=category, order=max_order + 1)
                print(f"new_product: {new_product}")
                return redirect('products:display_edit')

            # 商品削除処理
            elif action == 'delete' and product_id:
                product.delete()

        except Product.DoesNotExist:
            pass

        call_command('export_products', 'products.txt')
        return redirect('products:display_edit')

    
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    category = product.category
    product.delete()
    product.update_order_for_category(category)
    call_command('export_products', 'products.txt')
    return redirect('products:display_edit')