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
        received_amount = Student_received_Fee_Bank.objects.filter(credit_debit_category=c, added_by__batch_id=batch_id, student__status=1).aggregate(Sum('received_amount'))['received_amount__sum'] or 0
        received_amount += Student_received_Fee_Cash.objects.filter(credit_debit_category=c, added_by__batch_id=batch_id, student__status=1).aggregate(Sum('received_amount'))['received_amount__sum'] or 0
        credit_debit_category.append({
            'id': c.id, 
            'name': c.category_name,
            'total_amount': total_amount,
            'received_amount': received_amount,
            'pending_amount': total_amount - received_amount,
            
        })    
    
    return {
        'credit_debit_category': credit_debit_category,
        'total_amount': sum([c['total_amount'] for c in credit_debit_category]),
        'received_amount': sum([c['received_amount'] for c in credit_debit_category]),
        'pending_amount': sum([c['pending_amount'] for c in credit_debit_category]),
        }
    
@register.inclusion_tag('inclusion_tag/school_admin_student_details.html')
def school_admin_student_details(batch_id):
    school_class = []
    for s in School_class.objects.filter(batch_id=batch_id):
        total_students = Class_student.objects.filter(school_class=s, student__status=1).count()
        male_students = Class_student.objects.filter(school_class=s, student__status=1, student__gender='MALE').count()
        female_students = Class_student.objects.filter(school_class=s, student__status=1, student__gender='FEMALE').count()
        school_class.append({
            'class_name': s.name,
            'total_students': total_students,
            'male_students': male_students,
            'female_students': female_students,
        })

    return {
            'total_students':Student.objects.all().count(),
            'male_students':Student.objects.filter(gender='MALE').count(),
            'female_students':Student.objects.filter(gender='FEMALE').count(),
            'school_class': school_class,
            'total_teacher':Teacher.objects.all().count(),
            'male_teacher':Teacher.objects.filter(gender='MALE').count(),
            'female_teacher':Teacher.objects.filter(gender='FEMALE').count(),

        }
