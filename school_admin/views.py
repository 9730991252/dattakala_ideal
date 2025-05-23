from dattakala_ideal.includes import * 

# Create your views here.
def save_admin_used_count():
    obj, created = Admin_used_count.objects.get_or_create(defaults={'used_count': 1})
    if not created:
        obj.used_count = F('used_count') + 1
        obj.save()
        
def admin_home(request):
    if request.session.has_key('admin_mobile'):
        mobile = request.session['admin_mobile']
        a = Admin_detail.objects.filter(mobile=mobile).first()
        classes = []
        save_admin_used_count()
        for c in School_class.objects.filter(batch=a.batch, status=1):
            check_ins = 0
            check_outs = 0
            list =[]
            for c_in in Student_Attendance.objects.filter(check_in__date=now().date()):
                stc = Class_student.objects.filter(student_id=c_in.student.id).first()
                if stc != None:
                    if stc.school_class == c:
                        check_ins += 1
                        list.append({
                            'student':c_in.student,
                            'check_in_by_teacher':c_in.check_in_by_teacher,
                            'check_out_by_teacher':c_in.check_out_by_teacher,
                            'check_in':c_in.check_in,
                            'check_out':c_in.check_out,
                            'check_in_type':c_in.check_in_type,
                            'check_out_type':c_in.check_out_type,
                        })
            for c_out in Student_Attendance.objects.filter(check_out__date=now().date()):
                stc = Class_student.objects.filter(student_id=c_out.student.id).first()
                if stc != None:
                    if stc.school_class == c:
                        check_outs += 1
            classes.append({
                'id':c.id,
                'name':c.name,
                'check_ins':check_ins,
                'check_outs':check_outs,
                'list':list
            })
        banks_available_amount = check_banks_available_amount(request, a.batch)
        clerk_available_amount = check_clerk_available_amount(request, a.batch)
        context={
            'a':a,
            'total_students':Student.objects.all().count(),
            'male_students':Student.objects.filter(gender='MALE').count(),
            'female_students':Student.objects.filter(gender='FEMALE').count(),
            'total_teacher':Teacher.objects.all().count(),
            'male_teacher':Teacher.objects.filter(gender='MALE').count(),
            'female_teacher':Teacher.objects.filter(gender='FEMALE').count(),
            'check_in':Student_Attendance.objects.filter(check_in__date=now().date()).count(),
            'check_out':Student_Attendance.objects.filter(check_out__date=now().date()).count(),
            'class':classes,
            'banks_avalable_amount':banks_available_amount,
        }
        return render(request, 'admin_home.html', context)
    else:
        return redirect('Admin_detail')
    
def admin_account(request):
    if request.session.has_key('admin_mobile'):
        mobile = request.session['admin_mobile']
        a = Admin_detail.objects.filter(mobile=mobile).first()
        context={
        }
        return render(request, 'admin_account.html', context)
    else:
        return redirect('Admin_detail')
    
def admin_view_student_detail(request, id):
    if request.session.has_key('admin_mobile'):
        mobile = request.session['admin_mobile']
        a = Admin_detail.objects.filter(mobile=mobile).first()
        student = get_object_or_404(Student, id=id)
        student_img = Student_Image.objects.filter(student=student).first()
        class_info = Class_student.objects.filter(student=student, batch=a.batch).select_related('batch', 'school_class').first()
        cash_fee = Student_received_Fee_Cash.objects.filter(student=student, added_by__batch=a.batch)
        bank_fee = Student_received_Fee_Bank.objects.filter(student=student, added_by__batch=a.batch)
        paid_fee = int(cash_fee.aggregate(Sum('received_amount'))['received_amount__sum'] or 0) + int(bank_fee.aggregate(Sum('received_amount'))['received_amount__sum'] or 0)
        total_fee = student_fee.objects.filter(student=student, batch=a.batch).aggregate(Sum('amount'))['amount__sum'] or 0
        print('total_fee', total_fee)
        student_fee_detail = []
        for cdt in Credit_Debit_category.objects.filter(status=1):
            detail_total_fee = student_fee.objects.filter(credit_debit_category=cdt, student=student).aggregate(Sum('amount'))['amount__sum'] or 0
            detail_paid_fee = Student_received_Fee_Cash.objects.filter(credit_debit_category=cdt, student=student).aggregate(Sum('received_amount'))['received_amount__sum'] or 0
            detail_paid_fee += Student_received_Fee_Bank.objects.filter(credit_debit_category=cdt, student=student).aggregate(Sum('received_amount'))['received_amount__sum'] or 0
            if detail_total_fee >0:
                student_fee_detail.append({
                    'category': cdt,
                    'total_fee': detail_total_fee,
                    'detail_paid_fee': detail_paid_fee,
                    'reamining_fee': detail_total_fee - detail_paid_fee
                })

        context = {
            'student_fee_detail': student_fee_detail,
            'student': student,
            'student_img': student_img,
            'class_info': class_info,
            'todayes_date':date.today(),
            'cash_fee':cash_fee,
            'bank_fee':bank_fee,
            'paid_fee':paid_fee,
            'remaining_fee':int(total_fee)-int(paid_fee),
            'accounts':Bank_Account.objects.filter(status=1),
            'total_fee': total_fee,
            'credit_debit_category': Credit_Debit_category.objects.filter(status=1),
            'student_fee': student_fee.objects.filter(student=student, batch=a.batch),
        }
        return render(request, 'admin_view_student_detail.html', context)
    else:
        return redirect('Admin_detail')
    
def admin_student_approval(request):
    if request.session.has_key('admin_mobile'):
        mobile = request.session['admin_mobile']
        a = Admin_detail.objects.filter(mobile=mobile).first()
        student_fees = []
        for s in Student.objects.filter(status=1):
            sf = student_fee.objects.filter(student_id=s.id, batch=a.batch)
            if sf:
                class_student = Class_student.objects.filter(student_id=s.id, added_by__batch=a.batch).first()
                if class_student:
                    class_name = class_student.school_class.name
                else:
                    class_name = 'Not Selected'
                student_fees.append({
                    'student':s,
                    'class_name':class_name,
                    'fee':sf
                })
        context={
            'student_fees':student_fees
        }
        return render(request, 'admin_student_approval.html', context)
    else:
        return redirect('Admin_detail')
    
def debit(request):
    if request.session.has_key('admin_mobile'):
        mobile = request.session['admin_mobile']
        a = Admin_detail.objects.filter(mobile=mobile).first()
        context={
            'expenses':Expenses.objects.filter(batch=a.batch).order_by('date')
        }
        return render(request, 'debit.html', context)
    else:
        return redirect('Admin_detail')
    
def get_bank_credits(batch_id, bank_id):
    bank_credits = []
    for sb in Student_received_Fee_Bank.objects.filter(account_id=bank_id):
        bank_credits.append({
            'credit_type':'Student_recived_Fee_Bank',
            'id':sb.id,
            'received_amount':sb.received_amount,
            'recived_date':sb.paid_date,
            'admin_verify_status':sb.admin_verify_status,
            'verify_date':sb.verify_date,
            'verify_by':sb.verify_by,
            'utr_number':sb.utr_number,
            'student':sb.student,
            'student_img':Student_Image.objects.filter(student=sb.student).first(),
            'category':sb.credit_debit_category,
        })
    for ctb in Cash_Transfer_To_Bank.objects.filter(to_bank_id=bank_id):
        bank_credits.append({
            'credit_type':'Cash_Transfer_To_Bank',
            'id':ctb.id,
            'received_amount':ctb.amount,
            'recived_date':ctb.transfer_date,
            'from_clerk':ctb.from_clerk,
            'from_admin':ctb.from_admin,
            'admin_verify_status':ctb.admin_verify_status,
            'verify_date':ctb.verify_date,
            
        })
    bank_credits = sorted(bank_credits, key=lambda k: k['recived_date'], reverse=True)
    return bank_credits

def get_cash_credits(batch_id):
    cash_credits = []
    for sb in Student_received_Fee_Cash.objects.all():
        cash_credits.append({
            'credit_type':'Student_received_Fee_Cash',
            'id':sb.id,
            'received_amount':sb.received_amount,
            'recived_date':sb.paid_date,
            'admin_verify_status':sb.admin_verify_status, 
            'verify_date':sb.veryfy_date,
            'verify_by':sb.veryfy_by,
            'student':sb.student,
            'student_img':Student_Image.objects.filter(student=sb.student).first(),
            'category':sb.credit_debit_category,
        })
    return cash_credits

@csrf_exempt
def credit(request):
    if request.session.has_key('admin_mobile'):
        mobile = request.session['admin_mobile']
        a = Admin_detail.objects.filter(mobile=mobile).first()
        selected_bank = ''
        bank_credits = []
        cash_credits = []
        if 'get_statment'in request.POST:
            bank_id = request.POST.get('bank_id')
            selected_bank = Bank_Account.objects.filter(id=bank_id).first()
            bank_credits = get_bank_credits(a.batch.id, bank_id)
        if 'get_statment_cash'in request.POST:
            cash_credits = get_cash_credits(a.batch.id)
        context={
            'bank_accounts':Bank_Account.objects.all(),
            'selected_bank':selected_bank,
            'bank_credits':bank_credits,
            'cash_credits':cash_credits,
            'a':a
        }
        return render(request, 'credit.html', context)
    else:
        return redirect('Admin_detail')

    
def todayes_attendence(request):
    if request.session.has_key('admin_mobile'):
        mobile = request.session['admin_mobile']
        a = Admin_detail.objects.filter(mobile=mobile).first()
        classes = []
        for c in School_class.objects.filter(batch=a.batch, status=1):
            check_ins = 0
            check_outs = 0
            list =[]
            for c_in in Student_Attendance.objects.filter(check_in__date=now().date()):
                stc = Class_student.objects.filter(student_id=c_in.student.id).first()
                if stc != None:
                    if stc.school_class == c:
                        check_ins += 1
                        list.append({
                            'student':c_in.student,
                            'check_in_by_teacher':c_in.check_in_by_teacher,
                            'check_out_by_teacher':c_in.check_out_by_teacher,
                            'check_in':c_in.check_in,
                            'check_out':c_in.check_out,
                            'check_in_type':c_in.check_in_type,
                            'check_out_type':c_in.check_out_type,
                        })
            for c_out in Student_Attendance.objects.filter(check_out__date=now().date()):
                stc = Class_student.objects.filter(student_id=c_out.student.id).first()
                if stc != None:
                    if stc.school_class == c:
                        check_outs += 1
            classes.append({
                'id':c.id,
                'name':c.name,
                'check_ins':check_ins,
                'check_outs':check_outs,
                'list':list
            })
        
        context={
            'total_students':Student.objects.all().count(),
            'male_students':Student.objects.filter(gender='MALE').count(),
            'female_students':Student.objects.filter(gender='FEMALE').count(),
            'total_teacher':Teacher.objects.all().count(),
            'male_teacher':Teacher.objects.filter(gender='MALE').count(),
            'female_teacher':Teacher.objects.filter(gender='FEMALE').count(),
            'check_in':Student_Attendance.objects.filter(check_in__date=now().date()).count(),
            'check_out':Student_Attendance.objects.filter(check_out__date=now().date()).count(),
            'class':classes
        }
        return render(request, 'todayes_attendence.html', context)
    else:
        return redirect('Admin_detail')
    
def admin_view_students(request):
    if request.session.has_key('admin_mobile'):
        mobile = request.session['admin_mobile']
        a = Admin_detail.objects.filter(mobile=mobile).first()
        s = []
        for i in Student.objects.all().order_by('name'):
             
            school_class = Class_student.objects.filter(student_id=i.id, added_by__batch=a.batch).first()
            
            total_fee = student_fee.objects.filter(student_id=i.id, batch=a.batch).aggregate(Sum('amount'))['amount__sum'] or 0

            
            total_fee_paid = Student_received_Fee_Cash.objects.filter(student_id=i.id, added_by__batch=a.batch).aggregate(Sum('received_amount'))['received_amount__sum'] or 0
            total_fee_paid += Student_received_Fee_Bank.objects.filter(student_id=i.id, added_by__batch=a.batch).aggregate(Sum('received_amount'))['received_amount__sum'] or 0
            
            reamining_fee = total_fee - total_fee_paid or 0
            
            s.append({
                'id':i.id,
                'name':i.name,
                'mobile':i.mobile,
                'aadhar_number':i.aadhar_number,
                'gender':i.gender,
                'img':Student_Image.objects.filter(student_id=i.id).first(),
                'class_name':school_class.school_class.name if school_class else 'Not Selected',
                'total_fee':total_fee,
                'total_fee_paid':total_fee_paid,
                'reamining_fee':reamining_fee,
            })
        s = sorted(s, key=lambda k: k['reamining_fee'], reverse=True)
        context={
            'students':s,
            'total_students':Student.objects.all().count(),
            'male_students':Student.objects.filter(gender='MALE').count(),
            'female_students':Student.objects.filter(gender='FEMALE').count(),
        }
        return render(request, 'admin_view_students.html', context)
    else:
        return redirect('Admin_detail')
    
def admin_school_notice(request):
    if request.session.has_key('admin_mobile'):
        mobile = request.session['admin_mobile']
        s = []
        admin = Admin_detail.objects.filter(mobile=mobile).first()
            
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get('about_you')
            n = Notice.objects.filter(batch=admin.batch).count()
            n += 1
            # Save the notice
            notice = Notice.objects.create(
                by_admin=1,    # admin sent
                to_school=1,   # whole school
                title=title,
                batch=admin.batch,
                description=description,
                notice_number=n,
            )
            notice.save()

            messages.success(request, "Notice sent successfully! 🎉")
            return redirect('admin_school_notice')  # after save, refresh page

        # Fetch last 10 notices sent by admin to whole school
        notices = Notice.objects.filter(by_admin=1, to_school=1, batch=admin.batch).order_by('-added_date')[:10]
        paginator = Paginator(notices, 6)  # 6 notices per page
        page = request.GET.get('page')
        notices = paginator.get_page(page)
        context = {
            'students': s,
            'total_students': Student.objects.all().count(),
            'male_students': Student.objects.filter(gender='MALE').count(),
            'female_students': Student.objects.filter(gender='FEMALE').count(),
            'notices': notices,
        }
        return render(request, 'admin_school_notice.html', context)
    else:
        return redirect('Admin_detail')

def admin_class_notice(request):
    if request.session.has_key('admin_mobile'):
        mobile = request.session['admin_mobile']
        admin = Admin_detail.objects.filter(mobile=mobile).first()
        
        # Fetch all classes and teachers for the dropdown
        classes = School_class.objects.filter(added_by__batch=admin.batch, status=1)
        class_ids = []
        for c in classes:
            class_ids.append(c.id)
        if request.method == 'POST':
            class_id = request.POST.get('class')
            title = request.POST.get('title')
            description = request.POST.get('description')
            n = Notice.objects.filter(batch=admin.batch).count()
            n += 1
            # Save the notice
            notice = Notice.objects.create(
                by_admin=1,    # admin sent
                to_class_id=class_id,   # whole school
                title=title,
                batch=admin.batch,
                description=description,
                notice_number=n,
            )
            notice.save()

            messages.success(request, "Notice sent successfully! 🎉")
            return redirect('admin_class_notice')  # after save, refresh page

        # Fetch last 10 notices sent by admin to whole school
        notices = Notice.objects.filter(by_admin=1, to_class__in=class_ids, batch=admin.batch).order_by('-added_date')[:10]
        paginator = Paginator(notices, 6)  # 6 notices per page
        page = request.GET.get('page')
        notices = paginator.get_page(page)

        context = {
            'classes': classes,  # pass classes to dropdown
            'total_students': Student.objects.all().count(),
            'male_students': Student.objects.filter(gender='MALE').count(),
            'female_students': Student.objects.filter(gender='FEMALE').count(),
            'notices': notices,
        }

        return render(request, 'admin_class_notice.html', context)
    else:
        return redirect('Admin_detail')

def admin_teacher_notice(request):
    if request.session.has_key('admin_mobile'):
        mobile = request.session['admin_mobile']
        admin = Admin_detail.objects.filter(mobile=mobile).first()
        
        
            
        # Fetch all classes and teachers for the dropdown
        teacher = Teacher.objects.filter(batch=admin.batch, status=1)
        teacher_ids = []
        for c in teacher:
            teacher_ids.append(c.id)
        if request.method == 'POST':
            teacher_id = request.POST.get('teacher')
            title = request.POST.get('title')
            description = request.POST.get('description')
            n = Notice.objects.filter(batch=admin.batch).count()
            n += 1
            # Save the notice
            if teacher_id == '0':
                notice = Notice.objects.create(
                    by_admin=1,    # admin sent
                    to_all_teachers=1,   # whole teacher
                    title=title,
                    batch=admin.batch,
                    description=description,
                    notice_number=n,
                )
            else:
                notice = Notice.objects.create(
                    by_admin=1,    # admin sent
                    to_teacher_id=teacher_id,   # whole school
                    title=title,
                    batch=admin.batch,
                    description=description,
                    notice_number=n,
                )
            notice.save()

            messages.success(request, "Notice sent successfully! 🎉")
            return redirect('admin_teacher_notice')  # after save, refresh page

        # Fetch last 10 notices sent by admin to whole school
        notices = list(Notice.objects.filter(by_admin=1, to_all_teachers=1, batch=admin.batch).order_by('-added_date'))
        notices += Notice.objects.filter(by_admin=1, to_teacher__in=teacher_ids, batch=admin.batch).order_by('-id')
        paginator = Paginator(notices, 6)  # 6 notices per page
        page = request.GET.get('page')
        notices = paginator.get_page(page)

        context = {
            'teachers':Teacher.objects.filter(status=1,batch=admin.batch),
            'notices': notices,
        }
        return render(request, 'admin_teacher_notice.html', context)
    else:
        return redirect('Admin_detail')
    
def admin_student_notice(request):
    return redirect('admin_received_notice')
    
def admin_received_notice(request):
    if request.session.has_key('admin_mobile'):
        mobile = request.session['admin_mobile']
        admin = Admin_detail.objects.filter(mobile=mobile).first()
        s = []
        for i in Notice.objects.filter(batch=admin.batch).order_by('-id'):
            s.append({
                'id':i.id,
                'notice_number':i.notice_number,
                'by_clerk':i.by_clerk,
                'by_teacher':i.by_teacher,
                'by_admin':i.by_admin,
                'batch':i.batch,
                'to_class':i.to_class,
                'to_student':i.to_student,
                'to_school':i.to_school,
                'to_teacher':i.to_teacher,
                'title':i.title,
                'description':i.description,
                'added_date':i.added_date,
                'readed_date':Readed_Notice.objects.filter(notice_id=i.id, read_by_admin=1).first(),
            })
        context={
            'all_notices':s,
        }
        return render(request, 'admin_received_notice.html', context)
    else:
        return redirect('Admin_detail')
    
def admin_view_teacher(request):
    if request.session.has_key('admin_mobile'):
        mobile = request.session['admin_mobile']

        context={
            'teachers':Teacher.objects.all(),
        }
        return render(request, 'admin_view_teacher.html', context)
    else:
        return redirect('Admin_detail')
    
def admin_notice(request):
    if request.session.has_key('admin_mobile'):
        mobile = request.session['admin_mobile']
        context={
        }
        return render(request, 'admin_notice.html', context)
    else:
        return redirect('Admin_detail')