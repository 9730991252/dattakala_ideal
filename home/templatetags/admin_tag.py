from django import template
from django.db.models import Avg, Sum, Min, Max
from math import *
import math
import datetime
from datetime import datetime, date, time

from sunil.models import *
from school.models import *
from school_admin.models import *
register = template.Library()

# @register.simple_tag()
# def customer_selected_item_count(category_id):
#     return selected_item_category.objects.filter(category_id=category_id,status = 1).count()

# @register.inclusion_tag('inclusion_tag/home/customer_qr_code_cart_orders.html')
# def customer_qr_code_cart_orders(hotel_id):
#     return{'customer_cart':Customer_cart.objects.filter(table__hotel_id=hotel_id)}

@register.inclusion_tag('inclusion_tag/expenses_details.html')
def expenses_details(batch_id):
    print("batch_id", batch_id)
    credit_debit_category = []
    for c in Credit_Debit_category.objects.filter(added_by__batch_id=batch_id):
        total_amount = student_fee.objects.filter(credit_debit_category=c, batch_id=batch_id, student__status=1).aggregate(Sum('amount'))['amount__sum'] or 0
        
        print("total_amount", total_amount)
        credit_debit_category.append({
            'id': c.id, 
            'name': c.category_name,
            'total_amount': total_amount,
        })    
    return {
        'credit_debit_category': credit_debit_category
        }
