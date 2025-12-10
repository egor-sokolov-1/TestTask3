from celery import shared_task
import time
from .models import Payout


@shared_task
def process_payout(payout_id):
    """
    Целери таска для обработки заявки на выплату
    1)Статус в 'processing'
    2)Задержка (10 секунд)
    3)Проводит простую проверку (если сумма > 1000 то фейл)
    4)Обновим статус
    """
    try:
        payout = Payout.objects.get(id=payout_id)
        payout.status = Payout.Status.PROCESSING
        payout.save()

        time.sleep(10)
        # Простая проверка для демонстрации
        if payout.amount > 1000:
            payout.status = Payout.Status.FAILED
        else:
            payout.status = Payout.Status.COMPLETED
        payout.save()
    except Payout.DoesNotExist:
        print(f"Payout id {payout_id} not found")
    except Exception as e:
        print(f"Error {payout_id}: {str(e)}")
