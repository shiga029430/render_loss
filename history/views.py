from django.shortcuts import render, get_object_or_404
from products.models import LossRecord, LossDetail

def loss_history(request):
    # 日付フィルタ処理
    date_filter = request.GET.get('date')
    
    # クエリセット取得
    losses = LossRecord.objects.all().prefetch_related('details')
    if date_filter:
        losses = losses.filter(date__date=date_filter)
    
    # 新しい順に並べ替え
    losses = losses.order_by('-date')
    
    return render(request, 'history/loss_history.html', {
        'losses': losses,
    })

def loss_detail(request, loss_id):
    # 指定されたIDのロスレコードを取得
    loss = get_object_or_404(LossRecord, id=loss_id)
    
    # 関連するロス詳細を取得（カテゴリでソート）
    details = loss.details.all().order_by('product_category')
    
    return render(request, 'history/loss_detail.html', {
        'loss': loss,
        'details': details,
    })
