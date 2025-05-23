from django.shortcuts import render, redirect, get_object_or_404
from home.models import *
from school.models import *
from school_admin.models import *
from django.contrib import messages
from datetime import date
from django.db.models import *
from django.db.models import Avg, Sum, Min, Max
from django.db.models import F
# Create your views here.
def check_new_visitor(request):

    v = 1
    if request.session.has_key('admin_mobile'):
        v = 0
    if request.session.has_key('school_mobile'):
        v = 0
    if request.session.has_key('parent_mobile'):
        v = 0
    if request.session.has_key('teacher_mobile'):
        v = 0
    if not web_visitor.objects.all().first():
        web_visitor.objects.create(
            count=v
        )
    else:
        web_visitor.objects.all().update(
            count=F('count') + v
        )
    return web_visitor.objects.all().first().count

def check_clerk_available_amount(request, batch):
    clerks = []
    for c in Clerk.objects.filter(status=1, batch=batch):     
        available_cash = Student_received_Fee_Cash.objects.filter(added_by=c).aggregate(Sum('received_amount'))['received_amount__sum'] or 0
        available_cash -= Cash_Transfer_To_Bank.objects.filter(batch=batch, from_clerk=c).aggregate(Sum('amount'))['amount__sum'] or 0
        available_cash -= Cash_Transfer_To_Admin.objects.filter(batch=batch, from_clerk=c).aggregate(Sum('amount'))['amount__sum'] or 0
        available_cash -= Expenses.objects.filter(batch=batch, type='cash', added_by=c).aggregate(Sum('amount'))['amount__sum'] or 0
        if available_cash > 0:
            clerks.append({
                'clerk': c,
                'available_cash': available_cash
            })
    return clerks

def check_banks_available_amount(request, batch):
    banks=[]
    for b in Bank_Account.objects.filter(status=1):               
        avalable_cash = Cash_Transfer_To_Bank.objects.filter(batch=batch, to_bank=b).aggregate(Sum('amount'))['amount__sum'] or 0
        avalable_cash += Student_received_Fee_Bank.objects.filter(added_by__batch=batch, account=b).aggregate(Sum('received_amount'))['received_amount__sum'] or 0
        banks.append({
            'bank_name': b.bank_name,
            'account_number': b.account_number,
            'avalable_amount': avalable_cash
        })
    return banks



def index(request):
    Student_received_Fee_Cash.objects.all().delete()
    
    context = {
        'visitor': check_new_visitor(request),
    }
    return render(request, 'index.html', context)

def logout(request):
    if request.session.has_key('admin_mobile'):
        del request.session['admin_mobile']
        
    if request.session.has_key('school_mobile'):
        del request.session['school_mobile']
        
    if request.session.has_key('parent_mobile'):
        del request.session['parent_mobile']
        
    if request.session.has_key('teacher_mobile'):
        del request.session['teacher_mobile']
        
    return redirect('/')
def school_login(request):
    if request.method == "POST":
        batch_id=request.POST ['batch_id']
        number=request.POST ['mobile']
        pin=request.POST ['pin']
        c= Clerk.objects.filter(batch_id=batch_id,mobile=number,secret_pin=pin,status=1)
        if c:
            request.session['school_mobile'] = request.POST["mobile"]
            return redirect('school_home')
        else:
            messages.error(request,f"Mobile Number or Secret Pin invalid.")
            return redirect('/school_login/')
    context = {
        'batch':Batch.objects.all(),
  
    }
    return render(request, 'school_login.html', context)


def admin_login(request):
    if request.session.has_key('admin_mobile'):
        return redirect('admin_home')
    if request.method == "POST":
        batch_id=request.POST ['batch_id']
        number=request.POST ['mobile']
        pin=request.POST ['pin']
        c= Admin_detail.objects.filter(batch_id=batch_id,mobile=number,pin=pin,status=1)
        if c:
            request.session['admin_mobile'] = request.POST["mobile"]
            return redirect('admin_home')
        else:
            messages.error(request,f"Mobile Number or Secret Pin invalid.")
            return redirect('/admin_login/')
    context = {
        'batch':Batch.objects.all(),
    }
    return render(request, 'admin_login.html',context)



def parent_login(request):
    # batch = Batch.objects.filter(status=1, start_date__lte=date.today()).first()  
    # if request.session.has_key('parent_mobile'):
    #      return redirect('student_home', batch.id)
    # if request.method == "POST":
    #     number=request.POST ['mobile']
    #     pin=request.POST ['pin']
    #     s= Student.objects.filter(mobile=number,secret_pin=pin,status=1)
    #     if s:
    #         request.session['parent_mobile'] = request.POST["mobile"]
    #         return redirect('student_home', batch.id)
    #     else:
    #         messages.error(request,f"Mobile Number or Secret Pin invalid.")
    #         return redirect('/parent_login/')
    context={
        
    }
    return render(request, 'parent_login.html', context)

def teacher_login(request):
    # if request.session.has_key('teacher_mobile'):
    #     print('yes')
    #     return redirect('teacher_home')
    # if request.method == "POST":
    #     batch_id=request.POST ['batch_id']
    #     number=request.POST ['mobile']
    #     pin=request.POST ['pin']
    #     c= Teacher.objects.filter(batch_id=batch_id,mobile=number,pin=pin,status=1)
    #     if c:
    #         request.session['teacher_mobile'] = request.POST["mobile"]
    #         return redirect('teacher_home')
    #     else:
    #         messages.error(request,f"Mobile Number or Secret Pin invalid.")
    #         return redirect('/teacher_login/')
    context = {
        # 'batch':Batch.objects.all(),
        
    }
    return render(request, 'teacher_login.html',context)