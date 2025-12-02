from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from django.core.files.storage import FileSystemStorage, default_storage
from django.utils.text import get_valid_filename
import uuid
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.views.decorators.http import require_http_methods, require_POST
from django.core.exceptions import ValidationError

from .models import (
    JobTitle, Department, Employee, Attendance, Reward, Discipline, Payroll, 
    LeaveType, LeaveRequest, LeaveBalance, ExpenseCategory, Expense, 
    SalaryComponent, EmployeeSalaryRule, PayrollCalculationLog, SalaryRuleTemplate, 
    SalaryRuleTemplateItem, Contract, ContractHistory,
    AppraisalPeriod, AppraisalCriteria, Appraisal, AppraisalScore, AppraisalComment
)
from .forms import (
    EmployeeForm, LeaveTypeForm, LeaveRequestForm, ExpenseCategoryForm, ExpenseForm, ContractForm,
    AppraisalPeriodForm, AppraisalCriteriaForm, SelfAssessmentForm, ManagerReviewForm, HRFinalReviewForm,
    RewardForm, DisciplineForm
)
from .permissions import require_hr, require_hr_or_manager, can_manage_contract
from .validators import (
    validate_image_file, 
    validate_document_file, 
    validate_salary,
    validate_phone_number,
    validate_email
)
# Import security decorators
from .decorators import (
    hr_required, manager_or_hr_required, check_employee_access, 
    check_salary_access, check_appraisal_access, group_required,
    hr_only, is_hr_staff
)

from django.http import JsonResponse
from datetime import datetime, timedelta
import json
import xlwt
import calendar
import re
import logging
from django.db.models import Sum, Avg, Count
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import logging

# Configure logger
logger = logging.getLogger(__name__)

@login_required
def admin_home(request):
    employees = Employee.objects.all()
    departments = Department.objects.all()
    payrolls = Payroll.objects.all()
    
    # ========== STATISTICS ==========
    # Active employees (status 1=Thử việc, 2=Nhân viên chính thức)
    active_employees = employees.filter(status__in=[1, 2]).count()
    
    # Total salary this month
    current_month = timezone.localtime(timezone.now()).month
    current_year = timezone.localtime(timezone.now()).year
    total_salary = Payroll.objects.filter(
        month=current_month, 
        year=current_year
    ).aggregate(total=Sum('total_salary'))['total'] or 0
    
    # ========== CHART DATA ==========
    # 1. Employees by Department (Pie Chart)
    dept_labels = []
    dept_values = []
    for dept in departments:
        count = employees.filter(department=dept, status__in=[1, 2]).count()
        if count > 0:
            dept_labels.append(dept.name)
            dept_values.append(count)
    dept_employee_data = {'labels': dept_labels, 'values': dept_values}
    
    # 2. Employee Status Distribution (Doughnut Chart)
    STATUS_LABELS = {
        0: 'Onboarding',
        1: 'Thử việc', 
        2: 'Chính thức',
        3: 'Đã nghỉ việc',
        4: 'Bị sa thải'
    }
    status_labels = []
    status_values = []
    for status_val, status_label in STATUS_LABELS.items():
        count = employees.filter(status=status_val).count()
        if count > 0:
            status_labels.append(status_label)
            status_values.append(count)
    status_data = {'labels': status_labels, 'values': status_values}
    
    # 3. Average Salary by Department (Bar Chart)
    salary_labels = []
    salary_values = []
    for dept in departments:
        avg_salary = employees.filter(
            department=dept, 
            status__in=[1, 2]
        ).aggregate(avg=Avg('salary'))['avg']
        if avg_salary:
            salary_labels.append(dept.name)
            salary_values.append(round(avg_salary))
    dept_salary_data = {'labels': salary_labels, 'values': salary_values}
    
    # 4. Monthly Hiring Trend (Line Chart) - Last 6 months
    trend_labels = []
    trend_values = []
    for i in range(5, -1, -1):
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1
        
        count = employees.filter(
            contract_start_date__month=month,
            contract_start_date__year=year
        ).count()
        
        trend_labels.append(f'T{month}')
        trend_values.append(count)
    hiring_trend = {'labels': trend_labels, 'values': trend_values}
    
    # ========== RECENT ACTIVITIES ==========
    # New employees (last 5)
    new_employees = employees.order_by('-created_at')[:5]
    
    # Pending leave requests
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()
    
    # Pending expenses
    pending_expenses = Expense.objects.filter(status='pending').count()
    
    # Expiring contracts (next 30 days)
    from datetime import timedelta
    today = timezone.localtime(timezone.now()).date()
    expiring_contracts_count = Contract.objects.filter(
        end_date__lte=today + timedelta(days=30),
        end_date__gte=today,
        status='active'
    ).count()
    expiring_contracts_list = Contract.objects.filter(
        end_date__lte=today + timedelta(days=30),
        end_date__gte=today,
        status='active'
    ).select_related('employee').order_by('end_date')[:5]
    
    # ========== APPRAISAL STATISTICS ==========
    appraisal_notifications = []
    try:
        user_employee = Employee.objects.get(email=request.user.email)
        
        my_pending_appraisals = Appraisal.objects.filter(
            employee=user_employee,
            status='pending_self'
        ).count()
        
        team_pending_appraisals = 0
        if user_employee.is_manager:
            team_pending_appraisals = Appraisal.objects.filter(
                manager=user_employee,
                status='pending_manager'
            ).count()
            
            # Get appraisal notifications for manager's team
            pending_appraisals = Appraisal.objects.filter(
                manager=user_employee,
                status='pending_manager'
            ).select_related('employee', 'period')[:5]
            
            for appraisal in pending_appraisals:
                appraisal_notifications.append({
                    'employee': appraisal.employee,
                    'message': f'Cần đánh giá - {appraisal.period.name}'
                })
        
        hr_pending_appraisals = Appraisal.objects.filter(
            status='pending_hr'
        ).count()
        
        # HR gets all pending HR reviews
        if request.user.groups.filter(name='HR').exists():
            hr_pending = Appraisal.objects.filter(
                status='pending_hr'
            ).select_related('employee', 'period')[:5]
            
            for appraisal in hr_pending:
                appraisal_notifications.append({
                    'employee': appraisal.employee,
                    'message': f'Chờ duyệt HR - {appraisal.period.name}'
                })
        
        recent_appraisals = Appraisal.objects.filter(
            status='completed'
        ).order_by('-final_review_date')[:5]
        
    except Employee.DoesNotExist:
        my_pending_appraisals = 0
        team_pending_appraisals = 0
        hr_pending_appraisals = 0
        recent_appraisals = []
    
    # ========== REWARDS & DISCIPLINES ==========
    total_rewards_year = Reward.objects.filter(date__year=current_year).count()
    total_disciplines_year = Discipline.objects.filter(date__year=current_year).count()
    
    context = {
        "employees": employees,
        "departments": departments,
        "payrolls": payrolls,
        "total_employees": employees.count(),
        "total_departments": departments.count(),
        "active_employees": active_employees,
        "total_salary": total_salary,
        "current_month": current_month,
        "current_year": current_year,
        
        # Chart data (JSON)
        "dept_employee_data": json.dumps(dept_employee_data),
        "status_data": json.dumps(status_data),
        "dept_salary_data": json.dumps(dept_salary_data),
        "hiring_trend": json.dumps(hiring_trend),
        
        # Recent activities
        "new_employees": new_employees,
        "pending_leaves": pending_leaves,
        "pending_expenses": pending_expenses,
        "expiring_contracts": expiring_contracts_count,
        "expiring_contracts_list": expiring_contracts_list,
        
        # Appraisals
        "appraisal_notifications": appraisal_notifications,
        "my_pending_appraisals": my_pending_appraisals,
        "team_pending_appraisals": team_pending_appraisals,
        "hr_pending_appraisals": hr_pending_appraisals,
        "recent_appraisals": recent_appraisals,
        
        # Rewards/Disciplines
        "total_rewards_year": total_rewards_year,
        "total_disciplines_year": total_disciplines_year,
    }
    logger.info(f"Admin home accessed by {request.user.username}")
    return render(request, "hod_template/home_content.html", context)

def generate_employee_code():
    """Generate next employee code in format NV0001, NV0002, etc."""
    try:
        last_employee = Employee.objects.order_by('-id').first()
        if last_employee and last_employee.employee_code:
            last_code = last_employee.employee_code
            # Extract number from code (e.g., "NV0001" -> 1, "EMP001" -> 1)
            # Try to find digits in the code
            match = re.search(r'(\d+)$', last_code)
            if match:
                number = int(match.group(1))
                new_number = number + 1
            else:
                # If no number found, start from 1
                new_number = 1
        else:
            new_number = 1
    except (ValueError, AttributeError) as e:
        logger.warning(f"Error generating employee code: {e}. Starting from 1.")
        new_number = 1
    
    return f"NV{new_number:04d}"  # định dạng NV0001, NV0002,...

@login_required
@hr_required
@require_http_methods(["GET", "POST"])
def add_employee(request):
    employee_code = generate_employee_code()
    job_titles = JobTitle.objects.all()
    departments = Department.objects.all()
    context = {
        "employee_code": employee_code,
        'job_titles': job_titles,
        'departments': departments,
    }

    return render(request, "hod_template/add_employee_template.html", context)

@login_required
@hr_required
@require_POST
def add_employee_save(request):
    if request.method != "POST":
        return HttpResponse("Phương thức không cho phép")
    else:
        try:
            employee_code = request.POST.get("employee_code")
            employee_name = request.POST.get("employee_name")
            employee_gender = request.POST.get("employee_gender")
            employee_birthday = request.POST.get("employee_birthday")
            employee_place_of_birth = request.POST.get("employee_place_of_birth")
            employee_place_of_origin = request.POST.get("employee_place_of_origin")
            employee_place_of_residence = request.POST.get("employee_place_of_residence")
            employee_identification = request.POST.get("employee_identification")
            employee_date_of_issue = request.POST.get("employee_date_of_issue")
            employee_place_of_issue = request.POST.get("employee_place_of_issue")
            employee_nationality = request.POST.get("employee_nationality")
            employee_nation = request.POST.get("employee_nation")
            employee_religion = request.POST.get("employee_religion")
            employee_email = request.POST.get("employee_email")
            employee_phone = request.POST.get("employee_phone")
            employee_address = request.POST.get("employee_address")
            employee_marital_status = request.POST.get("employee_marital_status")
            job_title_id = request.POST.get("employee_job_title")
            employee_job_position = request.POST.get("employee_job_position")
            department_id = request.POST.get("employee_department")
            employee_salary = request.POST.get("employee_salary")

            # Convert IDs to int if not empty
            if job_title_id:
                try:
                    job_title_id = int(job_title_id)
                except (ValueError, TypeError):
                    messages.error(request, f"ID chức danh không hợp lệ: {job_title_id}")
                    logger.error(f"Invalid job_title_id: {job_title_id}")
                    return redirect('add_employee')
            
            if department_id:
                try:
                    department_id = int(department_id)
                except (ValueError, TypeError):
                    messages.error(request, f"ID phòng ban không hợp lệ: {department_id}")
                    logger.error(f"Invalid department_id: {department_id}")
                    return redirect('add_employee')

            employee_contract_start_date = request.POST.get("employee_contract_start_date")
            employee_contract_duration = request.POST.get("employee_contract_duration")
            employee_status = request.POST.get("employee_status")
            employee_education_level = request.POST.get("employee_education_level")
            employee_major = request.POST.get("employee_major")
            employee_school = request.POST.get("employee_school")
            employee_certificate = request.POST.get("employee_certificate")

            # Validate inputs
            try:
                validate_email(employee_email)
                validate_phone_number(employee_phone)
                employee_salary = validate_salary(employee_salary)
            except ValidationError as e:
                messages.error(request, str(e))
                logger.warning(f"Validation error in add_employee: {e}")
                return redirect('add_employee')

            # Xử lý avatar nếu có
            avatar_url = None
            if 'employee_avatar' in request.FILES:
                avatar = request.FILES['employee_avatar']
                try:
                    validate_image_file(avatar)
                    # sanitize and generate unique filename
                    filename = get_valid_filename(avatar.name)
                    unique_name = f"{uuid.uuid4().hex}_{filename}"
                    saved_path = default_storage.save(f"avatars/{unique_name}", avatar)
                    avatar_url = saved_path
                except ValidationError as e:
                    messages.error(request, str(e))
                    logger.warning(f"Avatar validation error: {e}")
                    return redirect('add_employee')

            employee = Employee(
                employee_code=employee_code,
                name=employee_name,
                gender=employee_gender,
                birthday=employee_birthday,
                place_of_birth=employee_place_of_birth,
                place_of_origin=employee_place_of_origin,
                place_of_residence=employee_place_of_residence,
                identification=employee_identification,
                date_of_issue=employee_date_of_issue,
                place_of_issue=employee_place_of_issue,
                nationality=employee_nationality,
                nation=employee_nation,
                religion=employee_religion,
                email=employee_email,
                phone=employee_phone,
                address=employee_address,
                avatar=avatar_url,
                marital_status=employee_marital_status,
                job_title=JobTitle.objects.get(id=job_title_id) if job_title_id else None,
                job_position=employee_job_position,
                department=Department.objects.get(id=department_id) if department_id else None,
                salary=employee_salary,
                contract_start_date=employee_contract_start_date,
                contract_duration=employee_contract_duration,
                status=employee_status,
                education_level=employee_education_level,
                major=employee_major,
                school=employee_school,
                certificate=employee_certificate,
            )
            employee.save()
            logger.info(f"Employee {employee.name} ({employee.employee_code}) created by {request.user.username}")
            
            # Send welcome email
            try:
                from .email_service import EmailService
                EmailService.send_welcome_email(employee)
            except Exception as email_error:
                logger.warning(f"Failed to send welcome email: {email_error}")
            
            messages.success(request, "Thêm Nhân viên thành công.")

            return redirect("/add_employee")
        except ValidationError as e:
            logger.error(f"Validation error adding employee: {e}")
            messages.error(request, f"Lỗi validation: {str(e)}")
            return redirect("/add_employee")
        except Exception as e:
            logger.error(f"Error adding employee: {e}", exc_info=True)
            messages.error(request, "Thêm Nhân viên không thành công. Vui lòng kiểm tra lại thông tin.")
            return redirect("/add_employee")


@login_required
def department_page(request):
    departments = Department.objects.all()
    employees = Employee.objects.all()

    department_data = []

    for dept in departments:
        manager = Employee.objects.filter(department=dept, is_manager=True).first()
        department_data.append({
            "id": dept.id,
            "name": dept.name,
            "description": dept.description,
            "date_establishment": dept.date_establishment,
            "manager_id": manager.id if manager else "",
            "manager_name": manager.name if manager else "Chưa có"
        })

    context = {
        'departments': department_data,
        'employees': employees
    }
    return render(request, "hod_template/department_template.html", context)

@login_required
@require_POST
def add_department_save(request):
    if request.method != "POST":
        return HttpResponse("Phương thức không cho phép")

    department_id_hidden = request.POST.get("department_id_hidden")
    department_name = request.POST.get("department_name")
    department_description = request.POST.get("department_description")
    department_date_establishment = request.POST.get("department_date_establishment")

    try:
        if department_id_hidden:
            # Cập nhật phòng ban
            department = Department.objects.get(id=department_id_hidden)
            department.name = department_name
            department.description = department_description
            department.date_establishment = department_date_establishment
            department.save()

            # Cập nhật trưởng phòng (nếu có)
            department_manager_id = request.POST.get("department_manager")
            Employee.objects.filter(department=department, is_manager=True).update(is_manager=False)
            if department_manager_id:
                manager = Employee.objects.get(id=department_manager_id)
                manager.department = department
                manager.is_manager = True
                manager.save()

            messages.success(request, "Cập nhật phòng ban thành công.")
        else:
            # Thêm mới phòng ban
            department = Department(
                name=department_name,
                description=department_description,
                date_establishment=department_date_establishment
            )
            department.save()
            messages.success(request, "Thêm phòng ban thành công.")

        return redirect("department_page")

    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy nhân viên làm trưởng phòng.")
        return redirect("department_page")

    except Exception as e:
        print("Lỗi khi lưu phòng ban:", e)
        messages.error(request, "Đã xảy ra lỗi khi lưu phòng ban.")
        return redirect("department_page")



@login_required
@require_POST
def delete_department(request, department_id):
    try:
        department = Department.objects.get(id=department_id)
        if Employee.objects.filter(department=department).exists():
            messages.error(request, "Không thể xóa phòng ban vì vẫn còn nhân viên trực thuộc.")
            logger.warning(f"Attempt to delete department {department.name} with existing employees by {request.user.username}")
            return redirect('department_page')
        department_name = department.name
        department.delete()
        logger.info(f"Department {department_name} deleted by {request.user.username}")
        messages.success(request, "Xóa phòng ban thành công.")
    except Department.DoesNotExist:
        messages.error(request, "Không tìm thấy phòng ban.")
    except Exception as e:
        messages.error(request, f"Lỗi khi xóa phòng ban: {e}")

    return redirect('department_page')

@login_required
def job_title(request):
    job_titles = JobTitle.objects.all()
    context = {
        'job_titles': job_titles
    }
    return render(request, "hod_template/job_title_template.html", context)

@login_required
def view_job_title(request, job_title_id):
    job_titles = JobTitle.objects.all()
    job = get_object_or_404(JobTitle, id=job_title_id)
    context = {
        "job_titles": job_titles,
        "selected_job": job
    }
    return render(request, "hod_template/job_title_template.html", context)

@login_required
@require_POST
def add_job_title_save(request):
    if request.method == "POST":
        job_title_id = request.POST.get("id_job_title")
        name = request.POST.get("name_job_title")
        coefficient = request.POST.get("salary_coefficient")
        description = request.POST.get("description")

        if job_title_id:  # Nếu có ID thì cập nhật
            job_title = JobTitle.objects.get(id=job_title_id)
            job_title.name = name
            job_title.salary_coefficient = coefficient
            job_title.description = description
            job_title.save()
            messages.success(request, "Cập nhật chức vụ thành công")
        else:  # Ngược lại thì thêm mới
            JobTitle.objects.create(
                name=name,
                salary_coefficient=coefficient,
                description=description
            )
            messages.success(request, "Thêm chức vụ thành công")

        return redirect("job_title")


@login_required
@require_POST
def delete_job_title(request, job_title_id):
    try:
        job = JobTitle.objects.get(id=job_title_id)
        job_name = job.name
        job.delete()
        logger.info(f"Job title {job_name} deleted by {request.user.username}")
        messages.success(request, "Xóa chức vụ thành công.")
    except JobTitle.DoesNotExist:
        messages.error(request, "Chức vụ không tồn tại.")
    return redirect("/job_title")

@login_required
def employee_list(request):
    # Lấy các tham số lọc từ request
    search_query = request.GET.get('search', '')
    department_id = request.GET.get('department', '')
    status = request.GET.get('status', '')

    # Khởi tạo queryset
    employees = Employee.objects.all()

    # Áp dụng các bộ lọc
    if search_query:
        employees = employees.filter(name__icontains=search_query)
    if department_id:
        employees = employees.filter(department_id=department_id)
    if status:
        employees = employees.filter(status=status)

    # Phân trang
    employees = employees.order_by('employee_code')  # Add ordering to avoid warning
    paginator = Paginator(employees, 10)  # Hiển thị 10 nhân viên mỗi trang
    page = request.GET.get('page')
    try:
        employees = paginator.page(page)
    except PageNotAnInteger:
        employees = paginator.page(1)
    except EmptyPage:
        employees = paginator.page(paginator.num_pages)

    # Lấy danh sách phòng ban cho bộ lọc
    departments = Department.objects.all()

    context = {
        "employees": employees,
        "departments": departments,
    }
    return render(request, "hod_template/employee_list_template.html", context)

@login_required
def employee_detail_view(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)

    if request.method == 'POST':
        if 'update' in request.POST:
            form = EmployeeForm(request.POST, request.FILES, instance=employee)
            if form.is_valid():
                form.save()
                messages.success(request, 'Cập nhật hồ sơ thành công.')
                return redirect('employee_detail', employee_id=employee.id)

        elif 'delete' in request.POST:
            employee.delete()
            messages.success(request, 'Xóa nhân viên thành công.')
            return redirect('employee_list')

    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'hod_template/employee_detail_template.html', {
        'employee': employee,
        'form': form,
    })

@login_required
def update_employee(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    departments = Department.objects.all()
    job_titles = JobTitle.objects.all()

    context = {
        "employee": employee,
        "departments": departments,
        "job_titles": job_titles
    }

    return render(request, "hod_template/update_employee_template.html", context)

@login_required
@require_POST
def update_employee_save(request, employee_id):
    if request.method == "POST":
        employee = get_object_or_404(Employee, pk=employee_id)

        # Cập nhật các trường cơ bản
        employee.name = request.POST.get("employee_name")
        employee.gender = request.POST.get("employee_gender")
        employee.birthday = request.POST.get("employee_birthday")
        employee.place_of_birth = request.POST.get("employee_place_of_birth")
        employee.place_of_origin = request.POST.get("employee_place_of_origin")
        employee.place_of_residence = request.POST.get("employee_place_of_residence")
        employee.identification = request.POST.get("employee_identification")
        employee.date_of_issue = request.POST.get("employee_date_of_issue")
        employee.place_of_issue = request.POST.get("employee_place_of_issue")
        employee.nationality = request.POST.get("employee_nationality")
        employee.nation = request.POST.get("employee_nation")
        employee.religion = request.POST.get("employee_religion")
        employee.marital_status = request.POST.get("employee_marital_status")
        employee.phone = request.POST.get("employee_phone")
        employee.email = request.POST.get("employee_email")
        employee.address = request.POST.get("employee_address")
        employee.job_position = request.POST.get("employee_job_position")
        employee.salary = request.POST.get("employee_salary")
        employee.contract_start_date = request.POST.get("employee_contract_start_date")
        employee.contract_duration = request.POST.get("employee_contract_duration")
        employee.status = request.POST.get("employee_status")
        employee.education_level = request.POST.get("employee_education_level")
        employee.major = request.POST.get("employee_major")
        employee.school = request.POST.get("employee_school")
        employee.certificate = request.POST.get("employee_certificate")

        # Cập nhật khóa ngoại
        department_id = request.POST.get("employee_department")
        job_title_id = request.POST.get("employee_job_title")
        employee.department = Department.objects.get(pk=department_id) if department_id else None
        employee.job_title = JobTitle.objects.get(pk=job_title_id) if job_title_id else None

        # Cập nhật ảnh đại diện nếu có
        if "employee_avatar" in request.FILES:
            avatar = request.FILES["employee_avatar"]
            try:
                validate_image_file(avatar)
                filename = get_valid_filename(avatar.name)
                unique_name = f"{uuid.uuid4().hex}_{filename}"
                employee.avatar.save(unique_name, avatar)
            except ValidationError as e:
                messages.error(request, str(e))
                logger.warning(f"Avatar validation error during update: {e}")
                return redirect('edit_employee', employee_id=employee_id)

        # Lưu thay đổi vào cơ sở dữ liệu
        employee.save()

        messages.success(request, 'Cập nhật hồ sơ thành công.')
        return redirect('employee_detail', employee_id=employee.id)

    else:
        return redirect('employee_list')

@login_required
@hr_required
@require_POST
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        employee_name = employee.name
        employee_code = employee.employee_code
        logger.info(f"Employee {employee_name} ({employee_code}) deleted by {request.user.username}")
        employee.delete()
        return redirect('employee_list')

@login_required
def manage_attendance(request):
    # Optimize query with select_related to avoid N+1 problem
    attendances = Attendance.objects.select_related('employee', 'employee__department').all().order_by('-date')
    departments = Department.objects.all()
    return render(request, "hod_template/manage_attendance.html", {
        "attendances": attendances,
        "departments": departments
    })

@login_required
def add_attendance(request):
    employees = Employee.objects.select_related('department').all()
    today = datetime.now().date()
    return render(request, "hod_template/add_attendance.html", {
        "employees": employees,
        "today": today
    })

@login_required
@require_POST
def add_attendance_save(request):
    if request.method == "POST":
        attendance_date = request.POST.get("attendance_date")
        employees = Employee.objects.all()
        
        # Xóa dữ liệu cũ nếu có
        Attendance.objects.filter(date=attendance_date).delete()
        
        for employee in employees:
            status = request.POST.get(f"status_{employee.id}")
            working_hours = request.POST.get(f"working_hours_{employee.id}")
            notes = request.POST.get(f"notes_{employee.id}")
            
            if status and working_hours:  # Kiểm tra dữ liệu trước khi lưu
                attendance = Attendance(
                    employee=employee,
                    date=attendance_date,
                    status=status,
                    working_hours=float(working_hours),
                    notes=notes
                )
                attendance.save()
            
        messages.success(request, "Bảng chấm công đã được lưu thành công")
        return redirect("manage_attendance")
    else:
        return redirect("add_attendance")

@login_required
@require_POST
def check_attendance_date(request):
    if request.method == "POST":
        date = request.POST.get("date")
        exists = Attendance.objects.filter(date=date).exists()
        return JsonResponse({"status": "exists" if exists else "new"})

@login_required
@require_POST
def get_attendance_data(request):
    if request.method == "POST":
        date = request.POST.get("date")
        attendances = Attendance.objects.filter(date=date)
        data = []
        for attendance in attendances:
            data.append({
                "employee_id": attendance.employee.id,
                "status": attendance.status,
                "working_hours": attendance.working_hours,
                "notes": attendance.notes
            })
        return JsonResponse({"data": data})

@login_required
def edit_attendance(request, attendance_id):
    attendance = Attendance.objects.select_related('employee').get(id=attendance_id)
    employees = Employee.objects.select_related('department').all()
    return render(request, "hod_template/add_attendance.html", {
        "attendance": attendance,
        "employees": employees,
        "edit_mode": True,
        "attendance_date": attendance.date.strftime('%Y-%m-%d')
    })

@login_required
@require_POST
def delete_attendance(request, attendance_id):
    try:
        logger.info(f"Deleting attendance ID {attendance_id} by {request.user.username}")
        attendance = Attendance.objects.get(id=attendance_id)
        attendance.delete()
        return JsonResponse({"status": "success"})
    except Attendance.DoesNotExist:
        logger.error(f"Attendance {attendance_id} not found")
        return JsonResponse({"status": "error", "message": "Không tìm thấy bảng chấm công"})
    except Exception as e:
        logger.error(f"Error deleting attendance: {e}")
        return JsonResponse({"status": "error", "message": str(e)})

@login_required
def export_attendance(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.xls"'
    logger.info(f"Attendance report exported by {request.user.username}")
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Bảng Chấm Công')
    
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    columns = ['STT', 'Ngày', 'Mã NV', 'Tên NV', 'Phòng Ban', 'Trạng Thái', 'Số Giờ', 'Ghi Chú']
    
    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)
    
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    
    rows = Attendance.objects.all().values_list(
        'date', 'employee__employee_code', 'employee__name',
        'employee__department__name', 'status', 'working_hours', 'notes'
    ).order_by('-date')
    
    for row in rows:
        row_num += 1
        ws.write(row_num, 0, row_num, font_style)
        ws.write(row_num, 1, row[0].strftime('%d/%m/%Y'), font_style)
        ws.write(row_num, 2, row[1], font_style)
        ws.write(row_num, 3, row[2], font_style)
        ws.write(row_num, 4, row[3], font_style)
        ws.write(row_num, 5, row[4], font_style)
        ws.write(row_num, 6, row[5], font_style)
        ws.write(row_num, 7, row[6], font_style)
    
    wb.save(response)
    return response

@login_required
def calculate_payroll(request):
    employees = Employee.objects.select_related('job_title', 'department').all()
    current_year = datetime.now().year
    years = range(current_year, current_year - 5, -1)
    return render(request, "hod_template/calculate_payroll.html", {
        "employees": employees,
        "years": years
    })

@login_required
@require_POST
def get_payroll_data(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        month = int(request.POST.get("month"))
        year = int(request.POST.get("year"))

        try:
            employee = Employee.objects.get(id=employee_id)
            
            # Kiểm tra bảng lương đã tồn tại
            existing_payroll = Payroll.objects.filter(
                employee=employee,
                month=month,
                year=year
            ).first()

            if existing_payroll and existing_payroll.status == 'confirmed':
                return JsonResponse({
                    "status": "error",
                    "message": "Bảng lương này đã được xác nhận. Không thể tính lại."
                })

            # Tính số ngày làm việc chuẩn
            cal = calendar.monthcalendar(year, month)
            standard_working_days = sum(1 for week in cal for day in week[0:5] if day != 0)

            # Tính tổng số giờ làm việc
            total_hours = Attendance.objects.filter(
                employee=employee,
                date__year=year,
                date__month=month,
                status="Có làm việc"
            ).aggregate(total=Sum('working_hours'))['total'] or 0

            # Tính số ngày nghỉ phép có lương (approved paid leave)
            paid_leave_days = LeaveRequest.objects.filter(
                employee=employee,
                status='approved',
                leave_type__is_paid=True,
                start_date__year=year,
                start_date__month=month
            ).aggregate(total=Sum('total_days'))['total'] or 0
            
            # Tính số ngày nghỉ phép không lương
            unpaid_leave_days = LeaveRequest.objects.filter(
                employee=employee,
                status='approved',
                leave_type__is_paid=False,
                start_date__year=year,
                start_date__month=month
            ).aggregate(total=Sum('total_days'))['total'] or 0

            # Tính lương theo giờ
            try:
                if standard_working_days > 0:
                    hourly_rate = float(employee.salary * employee.job_title.salary_coefficient) / float(standard_working_days * 8)
                else:
                    hourly_rate = 0
            except (ValueError, ZeroDivisionError):
                hourly_rate = 0

            # Tính lương cho ngày nghỉ phép có lương (8 giờ/ngày)
            paid_leave_salary = paid_leave_days * 8 * hourly_rate

            # Tính thưởng/phạt
            bonus = Reward.objects.filter(
                employee=employee,
                date__year=year,
                date__month=month
            ).aggregate(total=Sum('amount'))['total'] or 0

            penalty = Discipline.objects.filter(
                employee=employee,
                date__year=year,
                date__month=month
            ).aggregate(total=Sum('amount'))['total'] or 0

            # Tính tổng lương: lương làm việc + lương nghỉ phép có lương + thưởng - phạt
            total_salary = (hourly_rate * total_hours) + paid_leave_salary + bonus - penalty

            data = {
                "base_salary": employee.salary,
                "salary_coefficient": employee.job_title.salary_coefficient,
                "hourly_rate": hourly_rate,
                "total_working_hours": total_hours,
                "paid_leave_days": paid_leave_days,
                "unpaid_leave_days": unpaid_leave_days,
                "paid_leave_salary": paid_leave_salary,
                "bonus": bonus,
                "penalty": penalty,
                "total_salary": total_salary,
                "notes": existing_payroll.notes if existing_payroll else ""
            }

            return JsonResponse({"status": "success", "data": data})
        except Employee.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Không tìm thấy nhân viên"
            })
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })

@login_required
@require_POST
def save_payroll(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        # Validate month and year safely to avoid ValueError on empty/invalid input
        month_raw = request.POST.get("month")
        year_raw = request.POST.get("year")
        try:
            month = int(month_raw)
            year = int(year_raw)
            if month < 1 or month > 12:
                raise ValueError("Invalid month")
        except (TypeError, ValueError):
            messages.error(request, "Dữ liệu tháng/năm không hợp lệ. Vui lòng kiểm tra lại.")
            return redirect("calculate_payroll")

        try:
            employee = Employee.objects.select_related('job_title').get(id=employee_id)

            # Kiểm tra bảng lương đã tồn tại
            existing_payroll = Payroll.objects.filter(
                employee=employee,
                month=month,
                year=year
            ).first()

            if existing_payroll and existing_payroll.status == 'confirmed':
                messages.error(request, "Bảng lương này đã được xác nhận. Không thể lưu lại.")
                return redirect("manage_payroll")

            # Tính số ngày làm việc chuẩn
            cal = calendar.monthcalendar(year, month)
            standard_working_days = sum(1 for week in cal for day in week[0:5] if day != 0)

            # Lấy dữ liệu từ form
            base_salary = float(request.POST.get("base_salary").replace(",", "").replace(".", ""))
            salary_coefficient = float(request.POST.get("salary_coefficient"))
            hourly_rate = float(request.POST.get("hourly_rate").replace(",", "").replace(".", ""))
            total_working_hours = float(request.POST.get("total_working_hours"))
            bonus = float(request.POST.get("bonus"))
            penalty = float(request.POST.get("penalty"))
            total_salary = float(request.POST.get("total_salary").replace(",", "").replace(".", ""))
            notes = request.POST.get("notes")

            # Cập nhật hoặc tạo mới bảng lương
            if existing_payroll:
                existing_payroll.base_salary = base_salary
                existing_payroll.salary_coefficient = salary_coefficient
                existing_payroll.standard_working_days = standard_working_days
                existing_payroll.hourly_rate = hourly_rate
                existing_payroll.total_working_hours = total_working_hours
                existing_payroll.bonus = bonus
                existing_payroll.penalty = penalty
                existing_payroll.total_salary = total_salary
                existing_payroll.notes = notes
                existing_payroll.save()
            else:
                payroll = Payroll(
                    employee=employee,
                    month=month,
                    year=year,
                    base_salary=base_salary,
                    salary_coefficient=salary_coefficient,
                    standard_working_days=standard_working_days,
                    hourly_rate=hourly_rate,
                    total_working_hours=total_working_hours,
                    bonus=bonus,
                    penalty=penalty,
                    total_salary=total_salary,
                    notes=notes
                )
                payroll.save()
                logger.info(f"Payroll created for {employee.name} ({month}/{year}) by {request.user.username}")

            messages.success(request, "Bảng lương đã được lưu thành công")
            return redirect("manage_payroll")
        except Exception as e:
            logger.error(f"Error saving payroll: {e}", exc_info=True)
            messages.error(request, f"Có lỗi xảy ra: {str(e)}")
            return redirect("calculate_payroll")

@login_required
@login_required
@require_hr_or_manager
def manage_payroll(request):
    """Quản lý bảng lương (HR: all, Manager: all, Employee: own only)"""
    # Get current user's employee record
    is_hr = request.user.groups.filter(name='HR').exists()
    is_manager = request.user.groups.filter(name='Manager').exists() or request.user.is_superuser
    
    # Optimize query with select_related
    payrolls = Payroll.objects.select_related('employee', 'employee__department').all().order_by('-year', '-month')
    
    # Row-level filtering: Only regular employees see their own payroll
    if not is_hr and not is_manager:
        # Regular employee: see only their own
        try:
            user_employee = Employee.objects.get(email=request.user.email)
            payrolls = payrolls.filter(employee=user_employee)
        except Employee.DoesNotExist:
            messages.error(request, "Không tìm thấy hồ sơ nhân viên của bạn")
            return redirect('admin_home')
    # HR and Managers can see all payrolls
    
    departments = Department.objects.all()
    current_year = datetime.now().year
    years = range(current_year, current_year - 5, -1)
    
    return render(request, "hod_template/manage_payroll.html", {
        "payrolls": payrolls,
        "departments": departments,
        "years": years,
        "is_hr": is_hr
    })

@login_required
@require_hr
def edit_payroll(request, payroll_id):
    """Chỉnh sửa bảng lương (HR only)"""
    try:
        payroll = Payroll.objects.select_related('employee', 'employee__job_title').get(id=payroll_id)
        if payroll.status == 'confirmed':
            messages.error(request, "Không thể chỉnh sửa bảng lương đã xác nhận")
            return redirect("manage_payroll")

        employees = Employee.objects.select_related('job_title', 'department').all()
        current_year = datetime.now().year
        years = range(current_year, current_year - 5, -1)
        
        return render(request, "hod_template/calculate_payroll.html", {
            "payroll": payroll,
            "employees": employees,
            "years": years,
            "edit_mode": True,
            "selected_employee": payroll.employee.id,
            "selected_month": payroll.month,
            "selected_year": payroll.year
        })
    except Payroll.DoesNotExist:
        messages.error(request, "Không tìm thấy bảng lương")
        return redirect("manage_payroll")

@login_required
@require_POST
@require_hr
def delete_payroll(request):
    """Xóa bảng lương (HR only)"""
    payroll_id = request.POST.get("id")
    try:
        payroll = Payroll.objects.get(id=payroll_id)
        if payroll.status == 'pending':
            payroll.delete()
            logger.info(f"Payroll {payroll_id} deleted by {request.user.username}")
            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "error", "message": "Không thể xóa bảng lương đã xác nhận"})
    except Exception as e:
        logger.error(f"Error deleting payroll: {e}")
        return JsonResponse({"status": "error"})

@login_required
@require_POST
@require_hr
def confirm_payroll(request):
    """Xác nhận bảng lương (HR only)"""
    payroll_id = request.POST.get("id")
    try:
        payroll = Payroll.objects.get(id=payroll_id)
        payroll.status = 'confirmed'
        payroll.save()
        logger.info(f"Payroll ID {payroll_id} confirmed by {request.user.username}")
        return JsonResponse({"status": "success"})
    except Exception as e:
        logger.error(f"Error confirming payroll: {e}")
        return JsonResponse({"status": "error"})

@login_required
@require_hr_or_manager
def view_payroll(request, payroll_id):
    """Xem chi tiết bảng lương (HR: full info, Manager/Superuser: all, Employee: own only)"""
    from .permissions import can_view_employee_salary
    
    payroll = get_object_or_404(Payroll, id=payroll_id)
    
    # Check permissions - only restrict for regular employees
    is_hr = request.user.groups.filter(name='HR').exists()
    is_manager = request.user.groups.filter(name='Manager').exists() or request.user.is_superuser
    
    if not is_hr and not is_manager:
        # Regular employee: can only view their own payroll
        try:
            user_employee = Employee.objects.get(email=request.user.email)
            if payroll.employee != user_employee:
                messages.error(request, "Bạn chỉ có thể xem bảng lương của chính mình")
                return redirect('manage_payroll')
        except Employee.DoesNotExist:
            messages.error(request, "Không tìm thấy hồ sơ nhân viên của bạn")
            return redirect('manage_payroll')
    # HR and Managers can view all payrolls (no restriction)
    
    # Check if user can view salary information
    can_view_salary = can_view_employee_salary(request.user, payroll.employee)
    
    return render(request, "hod_template/view_payroll.html", {
        "payroll": payroll,
        "can_view_salary": can_view_salary
    })

@login_required
def export_payroll(request):
    # Get filter parameters from request
    month = request.GET.get('month')
    year = request.GET.get('year')
    department = request.GET.get('department')  # This is now department NAME, not ID
    status = request.GET.get('status')
    
    # Build dynamic filename based on filters
    filename_parts = ['BangLuong']
    if month:
        filename_parts.append(f'Thang{month}')
    if year:
        filename_parts.append(f'Nam{year}')
    if department:
        filename_parts.append(department.replace(' ', '_'))
    if status:
        status_map = {'pending': 'ChuaXacNhan', 'confirmed': 'DaXacNhan'}
        filename_parts.append(status_map.get(status, status.replace(' ', '_')))
    
    filename = '_'.join(filename_parts) + '.xls'
    
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Bảng Lương')
    
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    columns = ['STT', 'Tháng/Năm', 'Mã NV', 'Tên NV', 'Phòng Ban', 'Lương CB', 'Hệ Số', 'Lương/Giờ', 'Tổng Giờ', 'Thưởng', 'Phạt', 'Tổng Lương', 'Trạng Thái']
    
    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)
    
    # Sheet body, remaining rows - Apply filters
    font_style = xlwt.XFStyle()
    
    payrolls = Payroll.objects.all()
    
    # Apply filters
    if month:
        payrolls = payrolls.filter(month=month)
    if year:
        payrolls = payrolls.filter(year=year)
    if department:
        payrolls = payrolls.filter(employee__department__name=department)  # Filter by NAME
    if status:
        payrolls = payrolls.filter(status=status)
    
    rows = payrolls.values_list(
        'month', 'year', 'employee__employee_code', 'employee__name',
        'employee__department__name', 'base_salary', 'salary_coefficient',
        'hourly_rate', 'total_working_hours', 'bonus', 'penalty',
        'total_salary', 'status'
    ).order_by('-year', '-month')
    
    for row in rows:
        row_num += 1
        ws.write(row_num, 0, row_num, font_style)
        ws.write(row_num, 1, f"{row[0]}/{row[1]}", font_style)
        ws.write(row_num, 2, row[2], font_style)
        ws.write(row_num, 3, row[3], font_style)
        ws.write(row_num, 4, row[4], font_style)
        ws.write(row_num, 5, row[5], font_style)
        ws.write(row_num, 6, row[6], font_style)
        ws.write(row_num, 7, row[7], font_style)
        ws.write(row_num, 8, row[8], font_style)
        ws.write(row_num, 9, row[9], font_style)
        ws.write(row_num, 10, row[10], font_style)
        ws.write(row_num, 11, row[11], font_style)
        ws.write(row_num, 12, "Đã xác nhận" if row[12] == 'confirmed' else "Chưa xác nhận", font_style)
    
    wb.save(response)
    return response


# ============================================================================
# LEAVE MANAGEMENT VIEWS
# ============================================================================

@login_required
def manage_leave_types(request):
    """Quản lý các loại nghỉ phép (HR only)"""
    leave_types = LeaveType.objects.all()
    return render(request, "hod_template/manage_leave_types.html", {
        "leave_types": leave_types
    })

@login_required
@require_POST
def add_leave_type_save(request):
    """Thêm/sửa loại nghỉ phép"""
    leave_type_id = request.POST.get("leave_type_id")
    
    try:
        if leave_type_id:
            # Update existing
            leave_type = LeaveType.objects.get(id=leave_type_id)
            form = LeaveTypeForm(request.POST, instance=leave_type)
        else:
            # Create new
            form = LeaveTypeForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Lưu loại nghỉ phép thành công")
            logger.info(f"Leave type saved by {request.user.username}")
        else:
            messages.error(request, "Dữ liệu không hợp lệ")
            
    except Exception as e:
        logger.error(f"Error saving leave type: {e}")
        messages.error(request, f"Lỗi: {str(e)}")
    
    return redirect("manage_leave_types")

@login_required
@require_POST
def delete_leave_type(request, leave_type_id):
    """Xóa loại nghỉ phép"""
    try:
        leave_type = LeaveType.objects.get(id=leave_type_id)
        leave_type_name = leave_type.name
        leave_type.delete()
        logger.info(f"Leave type {leave_type_name} deleted by {request.user.username}")
        messages.success(request, "Xóa loại nghỉ phép thành công")
    except LeaveType.DoesNotExist:
        messages.error(request, "Không tìm thấy loại nghỉ phép")
    except Exception as e:
        messages.error(request, f"Lỗi: {str(e)}")
    
    return redirect("manage_leave_types")

@login_required
def request_leave(request):
    """Nhân viên tạo đơn xin nghỉ phép"""
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            
            # Gán employee từ user hiện tại
            try:
                employee = Employee.objects.get(email=request.user.email)
                leave_request.employee = employee
            except Employee.DoesNotExist:
                messages.error(request, "Không tìm thấy hồ sơ nhân viên của bạn")
                return redirect("request_leave")
            
            # Tính số ngày nghỉ
            leave_request.total_days = leave_request.calculate_working_days()
            
            # Kiểm tra số ngày phép còn lại
            try:
                leave_balance = LeaveBalance.objects.get(
                    employee=employee,
                    leave_type=leave_request.leave_type,
                    year=leave_request.start_date.year
                )
                
                if leave_balance.remaining_days < leave_request.total_days:
                    messages.error(request, f"Bạn chỉ còn {leave_balance.remaining_days} ngày phép, không đủ để xin nghỉ {leave_request.total_days} ngày")
                    return redirect("request_leave")
                    
            except LeaveBalance.DoesNotExist:
                # Tạo leave balance mới nếu chưa có
                LeaveBalance.objects.create(
                    employee=employee,
                    leave_type=leave_request.leave_type,
                    year=leave_request.start_date.year,
                    total_days=leave_request.leave_type.max_days_per_year,
                    used_days=0,
                    remaining_days=leave_request.leave_type.max_days_per_year
                )
            
            leave_request.save()
            logger.info(f"Leave request created by {employee.name}: {leave_request.total_days} days")
            messages.success(request, "Đơn xin nghỉ phép đã được gửi thành công")
            return redirect("leave_history")
    else:
        form = LeaveRequestForm()
    
    # Lấy leave balance của nhân viên
    try:
        employee = Employee.objects.get(email=request.user.email)
        leave_balances = LeaveBalance.objects.filter(
            employee=employee,
            year=datetime.now().year
        )
    except Employee.DoesNotExist:
        employee = None
        leave_balances = []
    
    return render(request, "hod_template/request_leave.html", {
        "form": form,
        "leave_balances": leave_balances
    })

@login_required
def leave_history(request):
    """Xem lịch sử đơn xin nghỉ phép của nhân viên"""
    try:
        employee = Employee.objects.get(email=request.user.email)
        leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')
    except Employee.DoesNotExist:
        leave_requests = []
    
    return render(request, "hod_template/leave_history.html", {
        "leave_requests": leave_requests
    })

@login_required
@login_required
@require_hr_or_manager
def manage_leave_requests(request):
    """HR/Manager xem tất cả đơn xin nghỉ phép (HR: all, Manager: department only)"""
    from .permissions import can_approve_leave
    
    # Get current user's employee record
    try:
        user_employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy hồ sơ nhân viên của bạn")
        return redirect('admin_home')
    
    # Filter options
    status_filter = request.GET.get('status', '')
    employee_filter = request.GET.get('employee', '')
    
    leave_requests = LeaveRequest.objects.select_related('employee', 'leave_type', 'approved_by').all()
    
    # Row-level filtering: Managers see only their department's leave requests
    if not request.user.groups.filter(name='HR').exists():
        leave_requests = leave_requests.filter(employee__department=user_employee.department)
    
    if status_filter:
        leave_requests = leave_requests.filter(status=status_filter)
    if employee_filter:
        leave_requests = leave_requests.filter(employee_id=employee_filter)
    
    leave_requests = leave_requests.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(leave_requests, 20)
    page = request.GET.get('page')
    try:
        leave_requests_page = paginator.page(page)
    except PageNotAnInteger:
        leave_requests_page = paginator.page(1)
    except EmptyPage:
        leave_requests_page = paginator.page(paginator.num_pages)
    
    # Filter employees based on department (for managers)
    if request.user.groups.filter(name='HR').exists():
        employees = Employee.objects.all()
    else:
        employees = Employee.objects.filter(department=user_employee.department)
    
    return render(request, "hod_template/manage_leave_requests.html", {
        "leave_requests": leave_requests_page,
        "employees": employees
    })

@login_required
@require_hr_or_manager
def view_leave_request(request, request_id):
    """Xem chi tiết đơn xin nghỉ phép (with row-level permission check)"""
    from .permissions import can_approve_leave
    
    leave_request = get_object_or_404(LeaveRequest, id=request_id)
    
    # Check row-level permission
    if not can_approve_leave(request.user, leave_request):
        messages.error(request, "Bạn không có quyền xem đơn xin nghỉ này")
        return redirect('manage_leave_requests')
    
    # Get leave balance
    try:
        leave_balance = LeaveBalance.objects.get(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            year=leave_request.start_date.year
        )
    except LeaveBalance.DoesNotExist:
        leave_balance = None
    
    return render(request, "hod_template/view_leave_request.html", {
        "leave_request": leave_request,
        "leave_balance": leave_balance
    })

@login_required
@require_POST
@login_required
@require_POST
@require_hr_or_manager
def approve_leave_request(request, request_id):
    """Duyệt đơn xin nghỉ phép (HR/Manager only with row-level check)"""
    from .permissions import can_approve_leave
    
    try:
        leave_request = LeaveRequest.objects.get(id=request_id)
        
        # Check row-level permission
        if not can_approve_leave(request.user, leave_request):
            messages.error(request, "Bạn không có quyền duyệt đơn này")
            logger.warning(f"Permission denied: {request.user.username} tried to approve leave request {request_id}")
            return redirect("manage_leave_requests")
        
        if leave_request.status != 'pending':
            messages.error(request, "Đơn này đã được xử lý rồi")
            return redirect("manage_leave_requests")
        
        # Get approver employee
        try:
            approver = Employee.objects.get(email=request.user.email)
        except Employee.DoesNotExist:
            messages.error(request, "Không tìm thấy hồ sơ nhân viên của bạn")
            return redirect("manage_leave_requests")
        
        # Update status
        leave_request.status = 'approved'
        leave_request.approved_by = approver
        leave_request.approved_at = timezone.now()
        leave_request.save()
        
        # Update leave balance
        leave_balance, created = LeaveBalance.objects.get_or_create(
            employee=leave_request.employee,
            leave_type=leave_request.leave_type,
            year=leave_request.start_date.year,
            defaults={
                'total_days': leave_request.leave_type.max_days_per_year,
                'used_days': 0,
                'remaining_days': leave_request.leave_type.max_days_per_year
            }
        )
        
        leave_balance.used_days += leave_request.total_days
        leave_balance.save()  # Auto-calculate remaining_days
        
        # Send email notification
        try:
            from .email_service import EmailService
            EmailService.send_leave_approved(leave_request)
        except Exception as email_error:
            logger.warning(f"Failed to send leave approval email: {email_error}")
        
        logger.info(f"Leave request {request_id} approved by {approver.name}")
        messages.success(request, "Đã duyệt đơn xin nghỉ phép")
        
    except LeaveRequest.DoesNotExist:
        messages.error(request, "Không tìm thấy đơn xin nghỉ phép")
    except Exception as e:
        logger.error(f"Error approving leave request: {e}")
        messages.error(request, f"Lỗi: {str(e)}")
    
    return redirect("manage_leave_requests")

@login_required
@require_POST
@require_hr_or_manager
def reject_leave_request(request, request_id):
    """Từ chối đơn xin nghỉ phép (HR/Manager only with row-level check)"""
    from .permissions import can_approve_leave
    
    try:
        leave_request = LeaveRequest.objects.get(id=request_id)
        
        # Check row-level permission
        if not can_approve_leave(request.user, leave_request):
            messages.error(request, "Bạn không có quyền từ chối đơn này")
            logger.warning(f"Permission denied: {request.user.username} tried to reject leave request {request_id}")
            return redirect("manage_leave_requests")
        
        if leave_request.status != 'pending':
            messages.error(request, "Đơn này đã được xử lý rồi")
            return redirect("manage_leave_requests")
        
        # Get approver employee
        try:
            approver = Employee.objects.get(email=request.user.email)
        except Employee.DoesNotExist:
            messages.error(request, "Không tìm thấy hồ sơ nhân viên của bạn")
            return redirect("manage_leave_requests")
        
        # Update status
        leave_request.status = 'rejected'
        leave_request.approved_by = approver
        leave_request.approved_at = timezone.now()
        leave_request.rejection_reason = request.POST.get('rejection_reason', '')
        leave_request.save()
        
        # Send email notification
        try:
            from .email_service import EmailService
            EmailService.send_leave_rejected(leave_request)
        except Exception as email_error:
            logger.warning(f"Failed to send leave rejection email: {email_error}")
        
        logger.info(f"Leave request {request_id} rejected by {approver.name}")
        messages.success(request, "Đã từ chối đơn xin nghỉ phép")
        
    except LeaveRequest.DoesNotExist:
        messages.error(request, "Không tìm thấy đơn xin nghỉ phép")
    except Exception as e:
        logger.error(f"Error rejecting leave request: {e}")
        messages.error(request, f"Lỗi: {str(e)}")
    
    return redirect("manage_leave_requests")

@login_required
@require_POST
def cancel_leave_request(request, request_id):
    """Nhân viên hủy đơn xin nghỉ phép của mình"""
    try:
        employee = Employee.objects.get(email=request.user.email)
        leave_request = LeaveRequest.objects.get(id=request_id, employee=employee)
        
        if leave_request.status != 'pending':
            messages.error(request, "Chỉ có thể hủy đơn đang chờ duyệt")
            return redirect("leave_history")
        
        leave_request.status = 'cancelled'
        leave_request.save()
        
        logger.info(f"Leave request {request_id} cancelled by {employee.name}")
        messages.success(request, "Đã hủy đơn xin nghỉ phép")
        
    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy hồ sơ nhân viên")
    except LeaveRequest.DoesNotExist:
        messages.error(request, "Không tìm thấy đơn xin nghỉ phép")
    except Exception as e:
        logger.error(f"Error cancelling leave request: {e}")
        messages.error(request, f"Lỗi: {str(e)}")
    
    return redirect("leave_history")

# ====================== Expense Management Views ======================

@login_required
def manage_expense_categories(request):
    """Quản lý danh mục chi phí"""
    categories = ExpenseCategory.objects.all().order_by('name')
    form = ExpenseCategoryForm()
    
    context = {
        'categories': categories,
        'form': form,
    }
    logger.info(f"Expense categories viewed by {request.user.username}")
    return render(request, 'hod_template/manage_expense_categories.html', context)

@login_required
@require_POST
def add_expense_category_save(request):
    """Thêm danh mục chi phí mới"""
    try:
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info(f"Expense category {form.cleaned_data['name']} created")
            messages.success(request, "Đã thêm danh mục chi phí thành công")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    except Exception as e:
        logger.error(f"Error adding expense category: {e}")
        messages.error(request, f"Lỗi: {str(e)}")
    
    return redirect("manage_expense_categories")

@login_required
@require_POST
def edit_expense_category_save(request, category_id):
    """Chỉnh sửa danh mục chi phí"""
    try:
        category = ExpenseCategory.objects.get(id=category_id)
        
        form = ExpenseCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            logger.info(f"Expense category {category.name} updated")
            messages.success(request, "Đã cập nhật danh mục chi phí")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    except ExpenseCategory.DoesNotExist:
        messages.error(request, "Không tìm thấy danh mục chi phí")
    except Exception as e:
        logger.error(f"Error editing expense category: {e}")
        messages.error(request, f"Lỗi: {str(e)}")
    
    return redirect("manage_expense_categories")

@login_required
@require_POST
def delete_expense_category(request, category_id):
    """Xóa danh mục chi phí"""
    try:
        category = ExpenseCategory.objects.get(id=category_id)
        
        # Kiểm tra xem có expense nào sử dụng category này không
        if Expense.objects.filter(category=category).exists():
            messages.error(request, "Không thể xóa danh mục chi phí đang được sử dụng")
        else:
            category_name = category.name
            category.delete()
            logger.info(f"Expense category {category_name} deleted")
            messages.success(request, "Đã xóa danh mục chi phí")
    except ExpenseCategory.DoesNotExist:
        messages.error(request, "Không tìm thấy danh mục chi phí")
    except Exception as e:
        logger.error(f"Error deleting expense category: {e}")
        messages.error(request, f"Lỗi: {str(e)}")
    
    return redirect("manage_expense_categories")

@login_required
def create_expense(request):
    """Nhân viên tạo yêu cầu chi phí"""
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy hồ sơ nhân viên")
        return redirect("admin_home")
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.employee = employee
            expense.save()
            
            logger.info(f"Expense created by {employee.name}: {expense.amount} VND")
            messages.success(request, "Đã tạo yêu cầu chi phí thành công")
            return redirect("expense_history")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ExpenseForm()
    
    categories = ExpenseCategory.objects.filter(is_active=True)
    context = {
        'form': form,
        'categories': categories,
        'employee': employee,
    }
    return render(request, 'hod_template/create_expense.html', context)

@login_required
def expense_history(request):
    """Lịch sử yêu cầu chi phí của nhân viên"""
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy hồ sơ nhân viên")
        return redirect("admin_home")
    
    # Lấy danh sách expenses
    expenses = Expense.objects.filter(employee=employee).order_by('-created_at')
    
    # Phân trang
    paginator = Paginator(expenses, 10)  # 10 expenses per page
    page = request.GET.get('page')
    try:
        expenses = paginator.page(page)
    except PageNotAnInteger:
        expenses = paginator.page(1)
    except EmptyPage:
        expenses = paginator.page(paginator.num_pages)
    
    # Thống kê
    total_expenses = Expense.objects.filter(employee=employee).aggregate(Sum('amount'))['amount__sum'] or 0
    approved_expenses = Expense.objects.filter(employee=employee, status='approved').aggregate(Sum('amount'))['amount__sum'] or 0
    paid_expenses = Expense.objects.filter(employee=employee, status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_expenses = Expense.objects.filter(employee=employee, status='pending').aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'expenses': expenses,
        'employee': employee,
        'total_expenses': total_expenses,
        'approved_expenses': approved_expenses,
        'paid_expenses': paid_expenses,
        'pending_expenses': pending_expenses,
    }
    logger.info(f"Expense history viewed by {employee.name}")
    return render(request, 'hod_template/expense_history.html', context)

@login_required
@require_hr_or_manager
def manage_expenses(request):
    """HR/Manager quản lý tất cả yêu cầu chi phí (HR: all, Manager: department only)"""
    # Get current user's employee record
    try:
        user_employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy hồ sơ nhân viên của bạn")
        return redirect('admin_home')
    
    # Lọc theo status
    status_filter = request.GET.get('status', '')
    expenses = Expense.objects.all().order_by('-created_at')
    
    # Row-level filtering: Managers see only their department's expenses
    if not request.user.groups.filter(name='HR').exists():
        expenses = expenses.filter(employee__department=user_employee.department)
    
    if status_filter:
        expenses = expenses.filter(status=status_filter)
    
    # Lọc theo nhân viên
    employee_filter = request.GET.get('employee', '')
    if employee_filter:
        expenses = expenses.filter(employee__id=employee_filter)
    
    # Lọc theo danh mục
    category_filter = request.GET.get('category', '')
    if category_filter:
        expenses = expenses.filter(category__id=category_filter)
    
    # Lọc theo ngày
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    if from_date:
        expenses = expenses.filter(date__gte=from_date)
    if to_date:
        expenses = expenses.filter(date__lte=to_date)
    
    # Phân trang
    paginator = Paginator(expenses, 10)
    page = request.GET.get('page')
    try:
        expenses_page = paginator.page(page)
    except PageNotAnInteger:
        expenses_page = paginator.page(1)
    except EmptyPage:
        expenses = paginator.page(paginator.num_pages)
    
    # Thống kê
    total_amount = Expense.objects.all().aggregate(Sum('amount'))['amount__sum'] or 0
    pending_count = Expense.objects.filter(status='pending').count()
    approved_count = Expense.objects.filter(status='approved').count()
    paid_count = Expense.objects.filter(status='paid').count()
    
    employees = Employee.objects.all()
    categories = ExpenseCategory.objects.filter(is_active=True)
    
    context = {
        'expenses': expenses,
        'employees': employees,
        'categories': categories,
        'status_filter': status_filter,
        'employee_filter': employee_filter,
        'category_filter': category_filter,
        'from_date': from_date,
        'to_date': to_date,
        'total_amount': total_amount,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'paid_count': paid_count,
    }
    logger.info(f"All expenses viewed by {request.user.username}")
    return render(request, 'hod_template/manage_expenses.html', context)

@login_required
@require_hr_or_manager
def view_expense(request, expense_id):
    """Xem chi tiết yêu cầu chi phí (with row-level permission check)"""
    from .permissions import can_approve_expense
    
    try:
        expense = Expense.objects.get(id=expense_id)
        
        # Check row-level permission
        if not can_approve_expense(request.user, expense):
            messages.error(request, "Bạn không có quyền xem yêu cầu chi phí này")
            return redirect('manage_expenses')
        
        context = {
            'expense': expense,
        }
        logger.info(f"Expense {expense_id} viewed by {request.user.username}")
        return render(request, 'hod_template/view_expense.html', context)
    except Expense.DoesNotExist:
        messages.error(request, "Không tìm thấy yêu cầu chi phí")
        return redirect("manage_expenses")

@login_required
@require_POST
@require_hr_or_manager
def approve_expense(request, expense_id):
    """Duyệt yêu cầu chi phí (HR/Manager only with row-level check)"""
    from .permissions import can_approve_expense
    
    try:
        expense = Expense.objects.get(id=expense_id)
        approver = Employee.objects.get(email=request.user.email)
        
        # Check row-level permission
        if not can_approve_expense(request.user, expense):
            messages.error(request, "Bạn không có quyền duyệt yêu cầu chi phí này")
            logger.warning(f"Permission denied: {request.user.username} tried to approve expense {expense_id}")
            return redirect("manage_expenses")
        
        if expense.status != 'pending':
            messages.error(request, "Yêu cầu chi phí này đã được xử lý")
            return redirect("manage_expenses")
        
        expense.status = 'approved'
        expense.approved_by = approver
        expense.approved_at = timezone.now()
        expense.save()
        
        # Send email notification
        try:
            from .email_service import EmailService
            EmailService.send_expense_approved(expense)
        except Exception as email_error:
            logger.warning(f"Failed to send expense approval email: {email_error}")
        
        logger.info(f"Expense {expense_id} approved by {approver.name}")
        messages.success(request, "Đã duyệt yêu cầu chi phí")
        
    except Expense.DoesNotExist:
        messages.error(request, "Không tìm thấy yêu cầu chi phí")
    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy hồ sơ người duyệt")
    except Exception as e:
        logger.error(f"Error approving expense: {e}")
        messages.error(request, f"Lỗi: {str(e)}")
    
    return redirect("manage_expenses")

@login_required
@require_POST
@require_hr_or_manager
def reject_expense(request, expense_id):
    """Từ chối yêu cầu chi phí (HR/Manager only with row-level check)"""
    from .permissions import can_approve_expense
    
    try:
        expense = Expense.objects.get(id=expense_id)
        rejector = Employee.objects.get(email=request.user.email)
        
        # Check row-level permission
        if not can_approve_expense(request.user, expense):
            messages.error(request, "Bạn không có quyền từ chối yêu cầu chi phí này")
            logger.warning(f"Permission denied: {request.user.username} tried to reject expense {expense_id}")
            return redirect("manage_expenses")
        
        if expense.status != 'pending':
            messages.error(request, "Yêu cầu chi phí này đã được xử lý")
            return redirect("manage_expenses")
        
        rejection_reason = request.POST.get('rejection_reason', '')
        
        expense.status = 'rejected'
        expense.approved_by = rejector
        expense.approved_at = timezone.now()
        if rejection_reason:
            expense.description += f"\n\nLý do từ chối: {rejection_reason}"
        expense.save()
        
        # Send email notification
        try:
            from .email_service import EmailService
            EmailService.send_expense_rejected(expense, rejection_reason)
        except Exception as email_error:
            logger.warning(f"Failed to send expense rejection email: {email_error}")
        
        logger.info(f"Expense {expense_id} rejected by {rejector.name}")
        messages.success(request, "Đã từ chối yêu cầu chi phí")
        
    except Expense.DoesNotExist:
        messages.error(request, "Không tìm thấy yêu cầu chi phí")
    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy hồ sơ người từ chối")
    except Exception as e:
        logger.error(f"Error rejecting expense: {e}")
        messages.error(request, f"Lỗi: {str(e)}")
    
    return redirect("manage_expenses")

@login_required
@require_POST
def mark_expense_as_paid(request, expense_id):
    """Đánh dấu chi phí đã thanh toán (cho Kế toán)"""
    try:
        expense = Expense.objects.get(id=expense_id)
        payer = Employee.objects.get(email=request.user.email)
        
        if expense.status != 'approved':
            messages.error(request, "Chỉ có thể thanh toán chi phí đã được duyệt")
            return redirect("manage_expenses")
        
        expense.status = 'paid'
        expense.paid_by = payer
        expense.paid_at = timezone.now()
        expense.save()
        
        logger.info(f"Expense {expense_id} marked as paid by {payer.name}")
        messages.success(request, "Đã đánh dấu chi phí đã thanh toán")
        
    except Expense.DoesNotExist:
        messages.error(request, "Không tìm thấy yêu cầu chi phí")
    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy hồ sơ người thanh toán")
    except Exception as e:
        logger.error(f"Error marking expense as paid: {e}")
        messages.error(request, f"Lỗi: {str(e)}")
    
    return redirect("manage_expenses")

@login_required
@require_POST
def cancel_expense(request, expense_id):
    """Nhân viên hủy yêu cầu chi phí của mình"""
    try:
        employee = Employee.objects.get(email=request.user.email)
        expense = Expense.objects.get(id=expense_id, employee=employee)
        
        if expense.status != 'pending':
            messages.error(request, "Chỉ có thể hủy yêu cầu chi phí đang chờ duyệt")
            return redirect("expense_history")
        
        expense.status = 'cancelled'
        expense.save()
        
        logger.info(f"Expense {expense_id} cancelled by {employee.name}")
        messages.success(request, "Đã hủy yêu cầu chi phí")
        
    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy hồ sơ nhân viên")
    except Expense.DoesNotExist:
        messages.error(request, "Không tìm thấy yêu cầu chi phí")
    except Exception as e:
        logger.error(f"Error cancelling expense: {e}")
        messages.error(request, f"Lỗi: {str(e)}")
    
    return redirect("expense_history")

# ====================== Self-Service Portal Views ======================

@login_required
def employee_dashboard(request):
    """Dashboard tổng quan cho nhân viên"""
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy hồ sơ nhân viên")
        return redirect("admin_home")
    
    # Lấy tháng/năm hiện tại
    now = timezone.now()
    current_month = now.month
    current_year = now.year
    
    # Thống kê chấm công tháng này
    attendance_this_month = Attendance.objects.filter(
        employee=employee,
        date__year=current_year,
        date__month=current_month
    )
    total_working_days = attendance_this_month.filter(status="Có làm việc").count()
    total_working_hours = attendance_this_month.filter(status="Có làm việc").aggregate(Sum('working_hours'))['working_hours__sum'] or 0
    
    # Lương tháng này
    current_payroll = Payroll.objects.filter(
        employee=employee,
        month=current_month,
        year=current_year
    ).first()
    
    # Nghỉ phép
    leave_balance = LeaveBalance.objects.filter(
        employee=employee,
        year=current_year
    ).first()
    
    pending_leave_requests = LeaveRequest.objects.filter(
        employee=employee,
        status='pending'
    ).count()
    
    # Chi phí
    pending_expenses = Expense.objects.filter(
        employee=employee,
        status='pending'
    ).count()
    
    total_expenses_this_month = Expense.objects.filter(
        employee=employee,
        date__year=current_year,
        date__month=current_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Hoạt động gần đây
    recent_activities = []
    
    # Leave requests
    recent_leaves = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')[:5]
    for leave in recent_leaves:
        recent_activities.append({
            'type': 'leave',
            'icon': 'fa-umbrella-beach',
            'color': 'info',
            'title': f'Xin nghỉ phép {leave.leave_type.name}',
            'description': f'{leave.start_date.strftime("%d/%m/%Y")} - {leave.end_date.strftime("%d/%m/%Y")}',
            'status': leave.status,
            'time': leave.created_at
        })
    
    # Expenses
    recent_expenses = Expense.objects.filter(employee=employee).order_by('-created_at')[:5]
    for expense in recent_expenses:
        recent_activities.append({
            'type': 'expense',
            'icon': 'fa-receipt',
            'color': 'warning',
            'title': f'Chi phí {expense.category.name}',
            'description': f'{expense.amount:,.0f} VND',
            'status': expense.status,
            'time': expense.created_at
        })
    
    # Sắp xếp theo thời gian
    recent_activities = sorted(recent_activities, key=lambda x: x['time'], reverse=True)[:10]
    
    context = {
        'employee': employee,
        'total_working_days': total_working_days,
        'total_working_hours': total_working_hours,
        'current_payroll': current_payroll,
        'leave_balance': leave_balance,
        'pending_leave_requests': pending_leave_requests,
        'pending_expenses': pending_expenses,
        'total_expenses_this_month': total_expenses_this_month,
        'recent_activities': recent_activities,
        'current_month': current_month,
        'current_year': current_year,
    }
    
    logger.info(f"Employee dashboard accessed by {employee.name}")
    return render(request, 'hod_template/employee_dashboard.html', context)

@login_required
def employee_profile(request):
    """Xem hồ sơ cá nhân"""
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy hồ sơ nhân viên")
        return redirect("admin_home")
    
    context = {
        'employee': employee,
    }
    logger.info(f"Profile viewed by {employee.name}")
    return render(request, 'hod_template/employee_profile.html', context)

@login_required
def edit_employee_profile(request):
    """Chỉnh sửa thông tin cá nhân (giới hạn)"""
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy hồ sơ nhân viên")
        return redirect("admin_home")
    
    if request.method == 'POST':
        try:
            # Chỉ cho phép cập nhật một số trường nhất định
            employee.phone = request.POST.get('phone', employee.phone)
            employee.address = request.POST.get('address', employee.address)
            employee.place_of_residence = request.POST.get('place_of_residence', employee.place_of_residence)
            
            # Upload avatar
            if 'avatar' in request.FILES:
                avatar = request.FILES['avatar']
                # Validate file
                try:
                    validate_image_file(avatar)
                    # Generate unique filename
                    ext = avatar.name.split('.')[-1]
                    filename = f"{uuid.uuid4()}.{ext}"
                    
                    # Save file
                    file_path = default_storage.save(f'avatars/{filename}', avatar)
                    employee.avatar = file_path
                except ValidationError as e:
                    messages.error(request, str(e))
                    return redirect('edit_employee_profile')
            
            employee.save()
            logger.info(f"Profile updated by {employee.name}")
            messages.success(request, "Đã cập nhật thông tin cá nhân")
            return redirect("employee_profile")
            
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            messages.error(request, f"Lỗi: {str(e)}")
    
    context = {
        'employee': employee,
    }
    return render(request, 'hod_template/edit_employee_profile.html', context)

@login_required
def my_payrolls(request):
    """Xem bảng lương của nhân viên"""
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy hồ sơ nhân viên")
        return redirect("admin_home")
    
    # Lọc theo năm
    year_filter = request.GET.get('year', '')
    payrolls = Payroll.objects.filter(employee=employee).order_by('-year', '-month')
    
    if year_filter:
        payrolls = payrolls.filter(year=int(year_filter))
    
    # Phân trang
    paginator = Paginator(payrolls, 12)  # 12 tháng per page
    page = request.GET.get('page')
    try:
        payrolls = paginator.page(page)
    except PageNotAnInteger:
        payrolls = paginator.page(1)
    except EmptyPage:
        payrolls = paginator.page(paginator.num_pages)
    
    # Thống kê
    total_salary = Payroll.objects.filter(employee=employee).aggregate(Sum('total_salary'))['total_salary__sum'] or 0
    avg_salary = Payroll.objects.filter(employee=employee).aggregate(avg=Sum('total_salary'))['avg'] or 0
    if Payroll.objects.filter(employee=employee).count() > 0:
        avg_salary = avg_salary / Payroll.objects.filter(employee=employee).count()
    
    # Danh sách năm để filter
    years = Payroll.objects.filter(employee=employee).values_list('year', flat=True).distinct().order_by('-year')
    
    context = {
        'employee': employee,
        'payrolls': payrolls,
        'years': years,
        'year_filter': year_filter,
        'total_salary': total_salary,
        'avg_salary': avg_salary,
    }
    logger.info(f"Payrolls viewed by {employee.name}")
    return render(request, 'hod_template/my_payrolls.html', context)

@login_required
def my_attendance(request):
    """Xem chấm công của nhân viên"""
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, "Không tìm thấy hồ sơ nhân viên")
        return redirect("admin_home")
    
    # Lọc theo tháng/năm
    month_filter = request.GET.get('month', '')
    year_filter = request.GET.get('year', '')
    
    attendances = Attendance.objects.filter(employee=employee).order_by('-date')
    
    if month_filter:
        attendances = attendances.filter(date__month=int(month_filter))
    if year_filter:
        attendances = attendances.filter(date__year=int(year_filter))
    
    # Phân trang
    paginator = Paginator(attendances, 31)  # 1 tháng per page
    page = request.GET.get('page')
    try:
        attendances = paginator.page(page)
    except PageNotAnInteger:
        attendances = paginator.page(1)
    except EmptyPage:
        attendances = paginator.page(paginator.num_pages)
    
    # Thống kê
    if month_filter and year_filter:
        month_attendances = Attendance.objects.filter(
            employee=employee,
            date__month=int(month_filter),
            date__year=int(year_filter)
        )
    else:
        # Tháng hiện tại
        now = timezone.now()
        month_attendances = Attendance.objects.filter(
            employee=employee,
            date__month=now.month,
            date__year=now.year
        )
    
    total_days = month_attendances.filter(status="Có làm việc").count()
    total_hours = month_attendances.filter(status="Có làm việc").aggregate(Sum('working_hours'))['working_hours__sum'] or 0
    leave_days = month_attendances.filter(status="Nghỉ phép").count()
    absent_days = month_attendances.filter(status="Nghỉ không phép").count()
    
    # Danh sách tháng/năm để filter
    years = Attendance.objects.filter(employee=employee).values_list('date__year', flat=True).distinct().order_by('-date__year')
    months = range(1, 13)
    
    context = {
        'employee': employee,
        'attendances': attendances,
        'years': years,
        'months': months,
        'month_filter': month_filter,
        'year_filter': year_filter,
        'total_days': total_days,
        'total_hours': total_hours,
        'leave_days': leave_days,
        'absent_days': absent_days,
    }
    logger.info(f"Attendance viewed by {employee.name}")
    return render(request, 'hod_template/my_attendance.html', context)


# ============= Recruitment Admin Views =============

@login_required
def list_jobs_admin(request):
    """Admin - Danh sách tất cả tin tuyển dụng"""
    from app.models import JobPosting, Department
    from django.db.models import Q, Count
    
    jobs = JobPosting.objects.select_related('department', 'job_title', 'created_by').annotate(
        applications_total=Count('applications')
    ).all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        jobs = jobs.filter(status=status_filter)
    
    # Filter by department
    department_filter = request.GET.get('department')
    if department_filter:
        jobs = jobs.filter(department_id=department_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    jobs = jobs.order_by('-created_at')  # Fix UnorderedObjectListWarning
    paginator = Paginator(jobs, 15)
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)
    
    # Statistics
    total_jobs = JobPosting.objects.count()
    open_jobs = JobPosting.objects.filter(status='open').count()
    from django.utils import timezone
    closing_soon = JobPosting.objects.filter(
        status='open',
        deadline__gte=timezone.now().date(),
        deadline__lte=timezone.now().date() + timedelta(days=7)
    ).count()
    
    departments = Department.objects.all()
    
    context = {
        'jobs': jobs,
        'departments': departments,
        'total_jobs': total_jobs,
        'open_jobs': open_jobs,
        'closing_soon': closing_soon,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'search_query': search_query,
        'STATUS_CHOICES': JobPosting.STATUS_CHOICES,
    }
    return render(request, 'hod_template/list_jobs_admin.html', context)


@login_required
def create_job(request):
    """Admin - Tạo tin tuyển dụng mới"""
    from app.models import JobPosting, Department, JobTitle, Employee
    from app.forms import JobPostingForm
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            # Set created_by to current employee
            try:
                employee = Employee.objects.get(email=request.user.username)
                job.created_by = employee
            except Employee.DoesNotExist:
                pass
            job.save()
            messages.success(request, f'Tin tuyển dụng {job.code} đã được tạo thành công!')
            logger.info(f"Job posting {job.code} created by {request.user.username}")
            return redirect('job_detail_admin', job_id=job.id)
    else:
        form = JobPostingForm()
    
    departments = Department.objects.all()
    job_titles = JobTitle.objects.all()
    
    context = {
        'form': form,
        'departments': departments,
        'job_titles': job_titles,
        'action': 'create',
    }
    return render(request, 'hod_template/create_edit_job.html', context)


@login_required
def job_detail_admin(request, job_id):
    """Admin - Chi tiết tin tuyển dụng"""
    from app.models import JobPosting
    from django.db.models import Count, Q
    
    job = get_object_or_404(JobPosting.objects.select_related('department', 'job_title', 'created_by'), pk=job_id)
    
    # Get applications statistics
    applications_stats = job.applications.aggregate(
        total=Count('id'),
        new=Count('id', filter=Q(status='new')),
        screening=Count('id', filter=Q(status='screening')),
        interview=Count('id', filter=Q(status='interview')),
        offer=Count('id', filter=Q(status='offer')),
        accepted=Count('id', filter=Q(status='accepted')),
        rejected=Count('id', filter=Q(status='rejected')),
    )
    
    # Recent applications
    recent_applications = job.applications.select_related('assigned_to').order_by('-created_at')[:5]
    
    context = {
        'job': job,
        'applications_stats': applications_stats,
        'recent_applications': recent_applications,
    }
    return render(request, 'hod_template/job_detail_admin.html', context)


@login_required
def edit_job(request, job_id):
    """Admin - Sửa tin tuyển dụng"""
    from app.models import JobPosting, Department, JobTitle
    from app.forms import JobPostingForm
    
    job = get_object_or_404(JobPosting, pk=job_id)
    
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save()
            messages.success(request, f'Tin tuyển dụng {job.code} đã được cập nhật!')
            logger.info(f"Job posting {job.code} updated by {request.user.username}")
            return redirect('job_detail_admin', job_id=job.id)
    else:
        form = JobPostingForm(instance=job)
    
    departments = Department.objects.all()
    job_titles = JobTitle.objects.all()
    
    context = {
        'form': form,
        'job': job,
        'departments': departments,
        'job_titles': job_titles,
        'action': 'edit',
    }
    return render(request, 'hod_template/create_edit_job.html', context)


@login_required
def delete_job(request, job_id):
    """Admin - Xóa tin tuyển dụng"""
    from app.models import JobPosting
    
    job = get_object_or_404(JobPosting, pk=job_id)
    
    if job.applications.exists():
        messages.error(request, 'Không thể xóa tin tuyển dụng đã có người ứng tuyển!')
        return redirect('job_detail_admin', job_id=job_id)
    
    if request.method == 'POST':
        job_code = job.code
        job.delete()
        messages.success(request, f'Tin tuyển dụng {job_code} đã được xóa!')
        logger.info(f"Job posting {job_code} deleted")
        return redirect('list_jobs_admin')
    
    return redirect('job_detail_admin', job_id=job_id)


@login_required
def applications_kanban(request):
    """Admin - Quản lý applications với chế độ xem List và Kanban"""
    from app.models import Application, JobPosting
    from django.db.models import Q
    from collections import defaultdict
    
    # Get view mode (list or kanban)
    view_mode = request.GET.get('view', 'list')
    
    # Filter by job
    job_filter = request.GET.get('job')
    if job_filter:
        applications = Application.objects.filter(job_id=job_filter)
    else:
        applications = Application.objects.all()
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        applications = applications.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(application_code__icontains=search_query)
        )
    
    applications = applications.select_related('job', 'assigned_to', 'interviewer').order_by('-created_at')
    
    # Group applications by status for kanban view
    kanban_columns = defaultdict(list)
    for app in applications:
        kanban_columns[app.status].append(app)
    
    # Get all jobs for filter
    jobs = JobPosting.objects.filter(status='open').order_by('-created_at')
    
    # Statistics
    total_applications = Application.objects.count()
    new_applications = Application.objects.filter(status='new').count()
    interview_scheduled = Application.objects.filter(status__in=['phone_interview', 'interview']).count()
    
    context = {
        'applications': applications,
        'kanban_columns': dict(kanban_columns),
        'STATUS_CHOICES': Application.STATUS_CHOICES,
        'jobs': jobs,
        'job_filter': job_filter,
        'search_query': search_query,
        'total_applications': total_applications,
        'new_applications': new_applications,
        'interview_scheduled': interview_scheduled,
        'view_mode': view_mode,
    }
    return render(request, 'hod_template/manage_applications.html', context)


@login_required
@require_POST
def update_application_status(request, application_id):
    """Admin - AJAX endpoint để update trạng thái application"""
    from app.models import Application
    import json
    
    application = get_object_or_404(Application, pk=application_id)
    
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status not in dict(Application.STATUS_CHOICES):
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
        
        old_status = application.status
        application.status = new_status
        application.save()
        
        # TODO: Send email notification to candidate
        
        logger.info(f"Application {application.application_code} status changed from {old_status} to {new_status}")
        
        return JsonResponse({
            'success': True,
            'message': f'Trạng thái đã được cập nhật thành {application.get_status_display()}'
        })
    except Exception as e:
        logger.error(f"Error updating application status: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def application_detail(request, application_id):
    """Admin - Chi tiết đơn ứng tuyển"""
    from app.models import Application, Employee
    
    application = get_object_or_404(
        Application.objects.select_related('job', 'assigned_to', 'interviewer', 'employee'),
        pk=application_id
    )
    
    # Get application notes
    notes = application.application_notes.select_related('author').order_by('-created_at')
    
    # Get all employees for assignment
    employees = Employee.objects.filter(is_manager=True).order_by('name')
    
    context = {
        'application': application,
        'notes': notes,
        'employees': employees,
    }
    return render(request, 'hod_template/application_detail.html', context)


@login_required
def update_application(request, application_id):
    """Admin - Cập nhật thông tin application"""
    from app.models import Application, Employee
    from app.forms import ApplicationReviewForm
    
    application = get_object_or_404(Application, pk=application_id)
    
    if request.method == 'POST':
        form = ApplicationReviewForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save()
            messages.success(request, f'Đơn ứng tuyển {application.application_code} đã được cập nhật!')
            logger.info(f"Application {application.application_code} updated by {request.user.username}")
            
            # TODO: Send email if status changed or interview scheduled
            
            return redirect('application_detail', application_id=application.id)
    else:
        form = ApplicationReviewForm(instance=application)
    
    employees = Employee.objects.filter(is_manager=True).order_by('name')
    
    context = {
        'form': form,
        'application': application,
        'employees': employees,
    }
    return render(request, 'hod_template/update_application.html', context)


@login_required
@require_POST
def add_application_note(request, application_id):
    """Admin - Thêm ghi chú cho application"""
    from app.models import Application, ApplicationNote, Employee
    
    application = get_object_or_404(Application, pk=application_id)
    note_text = request.POST.get('note')
    is_important = request.POST.get('is_important') == 'on'
    
    if note_text:
        try:
            employee = Employee.objects.get(email=request.user.username)
            ApplicationNote.objects.create(
                application=application,
                author=employee,
                note=note_text,
                is_important=is_important
            )
            messages.success(request, 'Ghi chú đã được thêm!')
        except Employee.DoesNotExist:
            messages.error(request, 'Không tìm thấy thông tin nhân viên!')
    
    return redirect('application_detail', application_id=application_id)


@login_required
@require_POST
def convert_to_employee(request, application_id):
    """Admin - Chuyển đổi ứng viên thành nhân viên"""
    from app.models import Application, Employee
    from django.db import transaction
    
    application = get_object_or_404(Application, pk=application_id)
    
    if not application.can_convert_to_employee():
        messages.error(request, 'Chỉ có thể chuyển đổi ứng viên đã chấp nhận offer!')
        return redirect('application_detail', application_id=application_id)
    
    try:
        with transaction.atomic():
            # Create new employee from application data
            employee = Employee()
            employee.name = application.full_name
            employee.email = application.email
            employee.phone = application.phone
            employee.birthday = application.date_of_birth if application.date_of_birth else timezone.now().date()
            employee.gender = application.gender if application.gender is not None else 0
            employee.address = application.address or ''
            employee.education_level = application.education_level if application.education_level is not None else 3
            employee.major = application.major or ''
            employee.school = application.school or ''
            
            # Required fields with defaults
            employee.place_of_birth = ''
            employee.place_of_origin = ''
            employee.place_of_residence = application.address or ''
            
            # Generate temporary identification (needs manual update)
            import uuid
            employee.identification = f'TEMP{uuid.uuid4().hex[:10].upper()}'  # Temporary, need to update manually
            
            employee.date_of_issue = timezone.now().date()
            employee.place_of_issue = ''
            employee.nationality = 'Việt Nam'
            employee.nation = 'Kinh'
            employee.religion = ''
            employee.marital_status = 0
            
            # Job related - from job posting
            employee.job_title = application.job.job_title  # Can be null
            employee.job_position = application.job.title
            employee.department = application.job.department
            employee.salary = application.expected_salary or application.job.salary_min or 10000000
            
            # Contract information
            employee.contract_start_date = application.available_start_date or application.job.start_date or timezone.now().date()
            employee.contract_duration = 12  # Default 12 months, can update later
            
            # Status
            employee.status = 0  # Onboarding
            
            # Generate employee code
            employee.employee_code = generate_employee_code()
            
            employee.save()
            
            # Link application to employee
            application.employee = employee
            application.converted_to_employee = True
            application.save()
            
            messages.success(
                request,
                f'Ứng viên {application.full_name} đã được chuyển thành nhân viên với mã {employee.employee_code}! '
                f'Vui lòng cập nhật thông tin CMND/CCCD và các thông tin còn thiếu.'
            )
            logger.info(f"Application {application.application_code} converted to employee {employee.employee_code}")
            
            return redirect('employee_detail', employee_id=employee.id)
            
    except Exception as e:
        logger.error(f"Error converting application to employee: {str(e)}")
        messages.error(request, f'Có lỗi xảy ra: {str(e)}')
        return redirect('application_detail', application_id=application_id)


@login_required
def org_chart(request):
    """Admin - Biểu đồ cơ cấu tổ chức"""
    from app.models import Employee, Department
    import json
    
    # Get all departments with employee counts
    departments = Department.objects.prefetch_related('employee_set').all().order_by('name')
    
    # Get all employees with their relationships
    employees = Employee.objects.select_related('department', 'job_title').filter(
        status__in=[0, 1, 2]  # Only active employees
    ).order_by('department', '-is_manager', 'name')
    
    # Build org chart data structure
    org_data = []
    
    # Add CEO/Directors (managers without department or top-level managers)
    top_managers = employees.filter(is_manager=True, department__isnull=True)
    for manager in top_managers:
        org_data.append({
            'id': f'emp_{manager.id}',
            'name': manager.name,
            'title': manager.job_position or 'N/A',
            'department': 'Ban Giám Đốc',
            'employee_code': manager.employee_code,
            'email': manager.email,
            'phone': manager.phone,
            'is_manager': True,
            'avatar': manager.avatar.url if manager.avatar else None,
            'parent': None,
        })
    
    # Add departments and their employees
    for dept in departments:
        dept_employees = employees.filter(department=dept)
        
        # Add department node
        dept_manager = dept_employees.filter(is_manager=True).first()
        dept_id = f'dept_{dept.id}'
        
        org_data.append({
            'id': dept_id,
            'name': dept.name,
            'title': f'{dept_employees.count()} nhân viên',
            'department': dept.name,
            'is_department': True,
            'parent': 'emp_1' if top_managers.exists() else None,  # Link to CEO if exists
        })
        
        # Add department manager
        if dept_manager:
            org_data.append({
                'id': f'emp_{dept_manager.id}',
                'name': dept_manager.name,
                'title': dept_manager.job_position or 'Trưởng phòng',
                'department': dept.name,
                'employee_code': dept_manager.employee_code,
                'email': dept_manager.email,
                'phone': dept_manager.phone,
                'is_manager': True,
                'avatar': dept_manager.avatar.url if dept_manager.avatar else None,
                'parent': dept_id,
            })
            
            # Add department staff (non-managers)
            staff = dept_employees.filter(is_manager=False)
            for emp in staff:
                org_data.append({
                    'id': f'emp_{emp.id}',
                    'name': emp.name,
                    'title': emp.job_position or 'N/A',
                    'department': dept.name,
                    'employee_code': emp.employee_code,
                    'email': emp.email,
                    'phone': emp.phone,
                    'is_manager': False,
                    'avatar': emp.avatar.url if emp.avatar else None,
                    'parent': f'emp_{dept_manager.id}',
                })
        else:
            # No manager, add all staff directly under department
            for emp in dept_employees:
                org_data.append({
                    'id': f'emp_{emp.id}',
                    'name': emp.name,
                    'title': emp.job_position or 'N/A',
                    'department': dept.name,
                    'employee_code': emp.employee_code,
                    'email': emp.email,
                    'phone': emp.phone,
                    'is_manager': False,
                    'avatar': emp.avatar.url if emp.avatar else None,
                    'parent': dept_id,
                })
    
    # Statistics
    total_employees = employees.count()
    total_departments = departments.count()
    total_managers = employees.filter(is_manager=True).count()
    
    context = {
        'org_data_json': json.dumps(org_data),
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_managers': total_managers,
        'departments': departments,
    }
    
    return render(request, 'hod_template/org_chart.html', context)


# ============================================================================
# SALARY RULES ENGINE
# ============================================================================

@login_required
@require_hr
def salary_components(request):
    """List all salary components with CRUD operations (HR only)"""
    components = SalaryComponent.objects.all().order_by('component_type', 'name')
    
    context = {
        'components': components,
        'active_count': components.filter(is_active=True).count(),
        'mandatory_count': components.filter(is_mandatory=True).count(),
    }
    
    return render(request, 'hod_template/salary_components.html', context)


@login_required
@require_hr
def create_salary_component(request):
    """Create new salary component (HR only)"""
    if request.method == 'POST':
        try:
            component = SalaryComponent(
                code=request.POST.get('code'),
                name=request.POST.get('name'),
                component_type=request.POST.get('component_type'),
                calculation_method=request.POST.get('calculation_method'),
                default_amount=float(request.POST.get('default_amount', 0)),
                percentage=float(request.POST.get('percentage', 0)),
                formula=request.POST.get('formula', ''),
                is_taxable=request.POST.get('is_taxable') == 'on',
                is_mandatory=request.POST.get('is_mandatory') == 'on',
                is_active=request.POST.get('is_active') == 'on',
                description=request.POST.get('description', ''),
            )
            component.save()
            messages.success(request, f'Đã tạo thành phần lương: {component.name}')
            return redirect('salary_components')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    context = {
        'component_types': SalaryComponent.COMPONENT_TYPES,
        'calculation_methods': SalaryComponent.CALCULATION_METHODS,
    }
    
    return render(request, 'hod_template/create_salary_component.html', context)


@login_required
@require_hr
def edit_salary_component(request, component_id):
    """Edit existing salary component (HR only)"""
    component = get_object_or_404(SalaryComponent, id=component_id)
    
    if request.method == 'POST':
        try:
            component.code = request.POST.get('code')
            component.name = request.POST.get('name')
            component.component_type = request.POST.get('component_type')
            component.calculation_method = request.POST.get('calculation_method')
            component.default_amount = float(request.POST.get('default_amount', 0))
            component.percentage = float(request.POST.get('percentage', 0))
            component.formula = request.POST.get('formula', '')
            component.is_taxable = request.POST.get('is_taxable') == 'on'
            component.is_mandatory = request.POST.get('is_mandatory') == 'on'
            component.is_active = request.POST.get('is_active') == 'on'
            component.description = request.POST.get('description', '')
            component.save()
            
            messages.success(request, f'Đã cập nhật: {component.name}')
            return redirect('salary_components')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    context = {
        'component': component,
        'component_types': SalaryComponent.COMPONENT_TYPES,
        'calculation_methods': SalaryComponent.CALCULATION_METHODS,
    }
    
    return render(request, 'hod_template/edit_salary_component.html', context)


@login_required
@require_hr
def delete_salary_component(request, component_id):
    """Delete salary component - soft delete by setting is_active=False (HR only)"""
    component = get_object_or_404(SalaryComponent, id=component_id)
    
    if request.method == 'POST':
        try:
            # Check if component is used
            rules_count = EmployeeSalaryRule.objects.filter(component=component, is_active=True).count()
            
            if rules_count > 0:
                messages.warning(request, f'Không thể xóa! Thành phần này đang được sử dụng bởi {rules_count} nhân viên.')
            else:
                component.is_active = False
                component.save()
                messages.success(request, f'Đã vô hiệu hóa: {component.name}')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    return redirect('salary_components')


@login_required
@require_hr
def employee_salary_rules(request, employee_id):
    """View and manage salary rules for specific employee (HR only)"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    # Get active rules
    active_rules = EmployeeSalaryRule.objects.filter(
        employee=employee,
        is_active=True
    ).select_related('component', 'created_by')
    
    # Get available components not assigned
    assigned_component_ids = active_rules.values_list('component_id', flat=True)
    available_components = SalaryComponent.objects.filter(
        is_active=True
    ).exclude(id__in=assigned_component_ids)
    
    # Get mandatory components that must be assigned
    mandatory_components = SalaryComponent.objects.filter(is_mandatory=True, is_active=True)
    missing_mandatory = mandatory_components.exclude(id__in=assigned_component_ids)
    
    context = {
        'employee': employee,
        'active_rules': active_rules,
        'available_components': available_components,
        'missing_mandatory': missing_mandatory,
    }
    
    return render(request, 'hod_template/employee_salary_rules.html', context)


@login_required
@require_hr
def assign_salary_rule(request, employee_id):
    """Assign new salary rule to employee (HR only)"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        try:
            component_id = request.POST.get('component_id')
            component = get_object_or_404(SalaryComponent, id=component_id)
            
            # Check if rule already exists
            existing = EmployeeSalaryRule.objects.filter(
                employee=employee,
                component=component,
                is_active=True
            ).first()
            
            if existing:
                messages.warning(request, f'{component.name} đã được gán cho nhân viên này!')
            else:
                rule = EmployeeSalaryRule(
                    employee=employee,
                    component=component,
                    custom_amount=request.POST.get('custom_amount') or None,
                    custom_percentage=request.POST.get('custom_percentage') or None,
                    custom_formula=request.POST.get('custom_formula', ''),
                    effective_from=request.POST.get('effective_from'),
                    effective_to=request.POST.get('effective_to') or None,
                    notes=request.POST.get('notes', ''),
                    created_by=Employee.objects.get(admin=request.user)
                )
                rule.save()
                messages.success(request, f'Đã gán {component.name} cho {employee.name}')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    return redirect('employee_salary_rules', employee_id=employee_id)


@login_required
@require_hr
def delete_salary_rule(request, rule_id):
    """Delete (deactivate) salary rule (HR only)"""
    rule = get_object_or_404(EmployeeSalaryRule, id=rule_id)
    employee_id = rule.employee.id
    
    if request.method == 'POST':
        try:
            rule.is_active = False
            rule.save()
            messages.success(request, f'Đã xóa quy tắc: {rule.component.name}')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    return redirect('employee_salary_rules', employee_id=employee_id)


@login_required
def calculate_salary_preview(request, employee_id):
    """Preview salary calculation with breakdown"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    # Get active rules
    active_rules = EmployeeSalaryRule.objects.filter(
        employee=employee,
        is_active=True
    ).select_related('component')
    
    # Base salary
    base_salary = employee.salary or 0
    
    # Calculate each component
    breakdown = []
    total_allowances = 0
    total_bonuses = 0
    total_deductions = 0
    total_overtime = 0
    
    for rule in active_rules:
        amount = rule.calculate(
            base_salary=base_salary,
            hours=float(request.GET.get('overtime_hours', 0)),
            days=float(request.GET.get('working_days', 22))
        )
        
        breakdown.append({
            'rule': rule,
            'amount': amount,
        })
        
        # Sum by type
        if rule.component.component_type == 'allowance':
            total_allowances += amount
        elif rule.component.component_type == 'bonus':
            total_bonuses += amount
        elif rule.component.component_type == 'deduction':
            total_deductions += amount
        elif rule.component.component_type == 'overtime':
            total_overtime += amount
    
    # Calculate insurance (simplified - 10.5% for employee)
    gross_salary = base_salary + total_allowances + total_bonuses + total_overtime
    social_insurance = gross_salary * 0.08
    health_insurance = gross_salary * 0.015
    unemployment_insurance = gross_salary * 0.01
    total_insurance = social_insurance + health_insurance + unemployment_insurance
    
    # Calculate tax (simplified progressive rate)
    taxable_income = gross_salary - total_insurance - 11000000  # 11M personal deduction
    if taxable_income <= 0:
        tax = 0
    elif taxable_income <= 5000000:
        tax = taxable_income * 0.05
    elif taxable_income <= 10000000:
        tax = taxable_income * 0.1 - 250000
    elif taxable_income <= 18000000:
        tax = taxable_income * 0.15 - 750000
    else:
        tax = taxable_income * 0.2 - 1650000
    
    # Net salary
    net_salary = gross_salary - total_deductions - total_insurance - tax
    
    context = {
        'employee': employee,
        'base_salary': base_salary,
        'breakdown': breakdown,
        'total_allowances': total_allowances,
        'total_bonuses': total_bonuses,
        'total_deductions': total_deductions,
        'total_overtime': total_overtime,
        'gross_salary': gross_salary,
        'social_insurance': social_insurance,
        'health_insurance': health_insurance,
        'unemployment_insurance': unemployment_insurance,
        'total_insurance': total_insurance,
        'taxable_income': max(0, taxable_income),
        'tax': max(0, tax),
        'net_salary': net_salary,
    }
    
    return render(request, 'hod_template/salary_calculation_preview.html', context)


@login_required
@require_hr
def bulk_assign_salary_rules(request):
    """Bulk assign salary rules to multiple employees (HR only)"""
    departments = Department.objects.all()
    components = SalaryComponent.objects.filter(is_active=True)
    
    if request.method == 'POST':
        try:
            employee_ids = request.POST.getlist('employee_ids[]')
            component_id = request.POST.get('component_id')
            custom_amount = request.POST.get('custom_amount') or None
            custom_percentage = request.POST.get('custom_percentage') or None
            custom_formula = request.POST.get('custom_formula', '')
            effective_from = request.POST.get('effective_from')
            effective_to = request.POST.get('effective_to') or None
            notes = request.POST.get('notes', '')
            
            component = get_object_or_404(SalaryComponent, id=component_id)
            created_by = Employee.objects.get(admin=request.user)
            
            created_count = 0
            skipped_count = 0
            
            for emp_id in employee_ids:
                employee = Employee.objects.get(id=emp_id)
                
                # Check if rule already exists
                existing = EmployeeSalaryRule.objects.filter(
                    employee=employee,
                    component=component,
                    is_active=True
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Create new rule
                EmployeeSalaryRule.objects.create(
                    employee=employee,
                    component=component,
                    custom_amount=custom_amount,
                    custom_percentage=custom_percentage,
                    custom_formula=custom_formula,
                    effective_from=effective_from,
                    effective_to=effective_to,
                    notes=notes,
                    created_by=created_by
                )
                created_count += 1
            
            messages.success(request, f'Đã gán quy tắc cho {created_count} nhân viên. Bỏ qua {skipped_count} nhân viên (đã có quy tắc).')
            return redirect('bulk_assign_salary_rules')
            
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    # Get employees with their current rules count
    employees = Employee.objects.all().select_related('department', 'job_title')
    
    context = {
        'departments': departments,
        'components': components,
        'employees': employees,
    }
    
    return render(request, 'hod_template/bulk_assign_salary_rules.html', context)


@login_required
@require_hr
def salary_rule_templates(request):
    """List all salary rule templates (HR only)"""
    templates = SalaryRuleTemplate.objects.all().select_related('job_title', 'department')
    
    context = {
        'templates': templates,
    }
    
    return render(request, 'hod_template/salary_rule_templates.html', context)


@login_required
@require_hr
def create_salary_rule_template(request):
    """Create new salary rule template (HR only)"""
    if request.method == 'POST':
        try:
            template = SalaryRuleTemplate(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                job_title_id=request.POST.get('job_title_id') or None,
                department_id=request.POST.get('department_id') or None,
                is_active=request.POST.get('is_active') == 'on'
            )
            template.save()
            messages.success(request, f'Đã tạo template: {template.name}')
            return redirect('edit_salary_rule_template', template_id=template.id)
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    job_titles = JobTitle.objects.all()
    departments = Department.objects.all()
    
    context = {
        'job_titles': job_titles,
        'departments': departments,
    }
    
    return render(request, 'hod_template/create_salary_rule_template.html', context)


@login_required
@require_hr
def edit_salary_rule_template(request, template_id):
    """Edit salary rule template and manage its items (HR only)"""
    template = get_object_or_404(SalaryRuleTemplate, id=template_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_template':
            try:
                template.name = request.POST.get('name')
                template.description = request.POST.get('description', '')
                template.job_title_id = request.POST.get('job_title_id') or None
                template.department_id = request.POST.get('department_id') or None
                template.is_active = request.POST.get('is_active') == 'on'
                template.save()
                messages.success(request, 'Đã cập nhật template')
            except Exception as e:
                messages.error(request, f'Lỗi: {str(e)}')
        
        elif action == 'add_component':
            try:
                component_id = request.POST.get('component_id')
                component = get_object_or_404(SalaryComponent, id=component_id)
                
                # Check if already exists
                existing = SalaryRuleTemplateItem.objects.filter(
                    template=template,
                    component=component
                ).first()
                
                if existing:
                    messages.warning(request, 'Component đã có trong template!')
                else:
                    item = SalaryRuleTemplateItem(
                        template=template,
                        component=component,
                        custom_amount=request.POST.get('custom_amount') or None,
                        custom_percentage=request.POST.get('custom_percentage') or None,
                        custom_formula=request.POST.get('custom_formula', ''),
                        order=template.template_items.count()
                    )
                    item.save()
                    messages.success(request, f'Đã thêm {component.name}')
            except Exception as e:
                messages.error(request, f'Lỗi: {str(e)}')
        
        return redirect('edit_salary_rule_template', template_id=template_id)
    
    job_titles = JobTitle.objects.all()
    departments = Department.objects.all()
    available_components = SalaryComponent.objects.filter(is_active=True).exclude(
        id__in=template.template_items.values_list('component_id', flat=True)
    )
    
    context = {
        'template': template,
        'job_titles': job_titles,
        'departments': departments,
        'available_components': available_components,
    }
    
    return render(request, 'hod_template/edit_salary_rule_template.html', context)


@login_required
@require_hr
def delete_template_item(request, item_id):
    """Delete component from template (HR only)"""
    item = get_object_or_404(SalaryRuleTemplateItem, id=item_id)
    template_id = item.template.id
    
    if request.method == 'POST':
        try:
            item.delete()
            messages.success(request, 'Đã xóa component khỏi template')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    return redirect('edit_salary_rule_template', template_id=template_id)


@login_required
@require_hr
def apply_template_to_employee(request, template_id, employee_id):
    """Apply a template to specific employee (HR only)"""
    template = get_object_or_404(SalaryRuleTemplate, id=template_id)
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        try:
            created_by = Employee.objects.get(admin=request.user)
            effective_from = request.POST.get('effective_from')
            
            if effective_from:
                from datetime import datetime
                effective_from = datetime.strptime(effective_from, '%Y-%m-d').date()
            
            count = template.apply_to_employee(employee, created_by, effective_from)
            messages.success(request, f'Đã áp dụng template. Tạo {count} quy tắc mới.')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
    
    return redirect('employee_salary_rules', employee_id=employee_id)


@login_required
@require_hr
def salary_calculation_history(request):
    """View calculation history/audit log (HR only)"""
    logs = PayrollCalculationLog.objects.all().select_related(
        'payroll__employee',
        'calculated_by'
    ).order_by('-calculated_at')
    
    # Filters
    employee_filter = request.GET.get('employee')
    month_filter = request.GET.get('month')
    year_filter = request.GET.get('year')
    
    if employee_filter:
        logs = logs.filter(payroll__employee_id=employee_filter)
    if month_filter:
        logs = logs.filter(payroll__month=month_filter)
    if year_filter:
        logs = logs.filter(payroll__year=year_filter)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 20)
    page = request.GET.get('page', 1)
    logs_page = paginator.get_page(page)
    
    employees = Employee.objects.all().order_by('name')
    months = list(range(1, 13))
    years = Payroll.objects.values_list('year', flat=True).distinct().order_by('-year')
    
    context = {
        'logs': logs_page,
        'employees': employees,
        'months': months,
        'years': years,
        'current_filters': {
            'employee': employee_filter,
            'month': month_filter,
            'year': year_filter,
        }
    }
    
    return render(request, 'hod_template/salary_calculation_history.html', context)


# ============================================================================
# CONTRACT MANAGEMENT
# ============================================================================

@login_required
@require_hr_or_manager
def manage_contracts(request):
    """List all contracts with filters (HR: all, Manager: department only)"""
    from django.db.models import Q
    
    # Filters
    employee_filter = request.GET.get('employee')
    status_filter = request.GET.get('status')
    contract_type_filter = request.GET.get('contract_type')
    expiring_soon = request.GET.get('expiring_soon')
    
    contracts = Contract.objects.select_related('employee', 'job_title', 'department', 'created_by').all()
    
    # Row-level filtering for Managers (only their department)
    if not request.user.is_superuser and not request.user.groups.filter(name='HR').exists():
        try:
            user_employee = request.user.employee
            if user_employee.is_manager:
                contracts = contracts.filter(employee__department=user_employee.department)
        except:
            contracts = Contract.objects.none()
    
    if employee_filter:
        contracts = contracts.filter(employee_id=employee_filter)
    
    if status_filter:
        contracts = contracts.filter(status=status_filter)
    
    if contract_type_filter:
        contracts = contracts.filter(contract_type=contract_type_filter)
    
    if expiring_soon == 'yes':
        # Contracts expiring in next 30 days
        today = timezone.now().date()
        thirty_days_later = today + timedelta(days=30)
        contracts = contracts.filter(
            status='active',
            end_date__isnull=False,
            end_date__lte=thirty_days_later,
            end_date__gte=today
        )
    
    # Pagination
    paginator = Paginator(contracts, 20)
    page = request.GET.get('page')
    contracts_page = paginator.get_page(page)
    
    # Statistics
    total_contracts = Contract.objects.count()
    active_contracts = Contract.objects.filter(status='active').count()
    expiring_contracts = Contract.objects.filter(
        status='active',
        end_date__isnull=False,
        end_date__lte=timezone.now().date() + timedelta(days=30),
        end_date__gte=timezone.now().date()
    ).count()
    
    employees = Employee.objects.filter(status__in=[0, 1, 2]).order_by('name')
    
    context = {
        'contracts': contracts_page,
        'employees': employees,
        'total_contracts': total_contracts,
        'active_contracts': active_contracts,
        'expiring_contracts': expiring_contracts,
        'CONTRACT_TYPE_CHOICES': Contract.CONTRACT_TYPE_CHOICES,
        'STATUS_CHOICES': Contract.STATUS_CHOICES,
        'current_filters': {
            'employee': employee_filter,
            'status': status_filter,
            'contract_type': contract_type_filter,
            'expiring_soon': expiring_soon,
        }
    }
    
    return render(request, 'hod_template/list_contracts.html', context)


@login_required
@require_hr
def create_contract(request):
    """Create new contract (HR only)"""
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES)
        if form.is_valid():
            contract = form.save(commit=False)
            # Set created_by
            try:
                creator = Employee.objects.get(email=request.user.email)
                contract.created_by = creator
            except Employee.DoesNotExist:
                pass
            
            contract.save()
            
            # Log history
            ContractHistory.objects.create(
                contract=contract,
                action='created',
                description=f"Hợp đồng {contract.contract_code} được tạo mới",
                performed_by=contract.created_by
            )
            
            messages.success(request, f'Hợp đồng {contract.contract_code} đã được tạo thành công!')
            logger.info(f"Contract {contract.contract_code} created by {request.user.email}")
            return redirect('contract_detail', contract_id=contract.id)
    else:
        form = ContractForm()
    
    employees = Employee.objects.filter(status__in=[0, 1, 2]).order_by('name')
    job_titles = JobTitle.objects.all()
    departments = Department.objects.all()
    
    context = {
        'form': form,
        'employees': employees,
        'job_titles': job_titles,
        'departments': departments,
    }
    
    return render(request, 'hod_template/create_edit_contract.html', context)


@login_required
@require_hr_or_manager
def contract_detail(request, contract_id):
    """View contract details (HR: all, Manager: department only)"""
    contract = get_object_or_404(Contract.objects.select_related(
        'employee', 'job_title', 'department', 'created_by'
    ), pk=contract_id)
    
    # Check row-level permission for managers
    if not can_manage_contract(request.user, contract):
        messages.error(request, 'Bạn không có quyền xem hợp đồng này.')
        return redirect('manage_contracts')
    
    # Get history
    history = contract.history.select_related('performed_by').all()[:10]
    
    # Check if expiring
    days_left = contract.days_until_expiry()
    is_expiring = contract.is_expiring_soon(30)
    
    context = {
        'contract': contract,
        'history': history,
        'days_left': days_left,
        'is_expiring': is_expiring,
    }
    
    return render(request, 'hod_template/contract_detail.html', context)


@login_required
@require_hr
def edit_contract(request, contract_id):
    """Edit existing contract (HR only)"""
    contract = get_object_or_404(Contract, pk=contract_id)
    
    # Save old values for history
    if request.method == 'POST':
        old_salary = contract.base_salary
        old_status = contract.status
        old_end_date = contract.end_date
        
        form = ContractForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            contract = form.save()
            
            # Log changes
            try:
                performer = Employee.objects.get(email=request.user.email)
            except Employee.DoesNotExist:
                performer = None
            
            # Log salary change
            if old_salary != contract.base_salary:
                ContractHistory.objects.create(
                    contract=contract,
                    action='salary_adjusted',
                    description=f"Lương thay đổi từ {old_salary:,.0f} VNĐ sang {contract.base_salary:,.0f} VNĐ",
                    old_value={'base_salary': float(old_salary)},
                    new_value={'base_salary': float(contract.base_salary)},
                    performed_by=performer
                )
            
            # Log status change
            if old_status != contract.status:
                ContractHistory.objects.create(
                    contract=contract,
                    action='status_changed',
                    description=f"Trạng thái thay đổi từ {contract.get_status_display()} sang {dict(Contract.STATUS_CHOICES)[contract.status]}",
                    old_value={'status': old_status},
                    new_value={'status': contract.status},
                    performed_by=performer
                )
            
            messages.success(request, f'Hợp đồng {contract.contract_code} đã được cập nhật!')
            logger.info(f"Contract {contract.contract_code} updated by {request.user.email}")
            return redirect('contract_detail', contract_id=contract.id)
    else:
        form = ContractForm(instance=contract)
    
    employees = Employee.objects.filter(status__in=[0, 1, 2]).order_by('name')
    job_titles = JobTitle.objects.all()
    departments = Department.objects.all()
    
    context = {
        'form': form,
        'contract': contract,
        'employees': employees,
        'job_titles': job_titles,
        'departments': departments,
    }
    
    return render(request, 'hod_template/create_edit_contract.html', context)


@login_required
@require_hr
@require_POST
def delete_contract(request, contract_id):
    """Delete contract (only if draft, HR only)"""
    contract = get_object_or_404(Contract, pk=contract_id)
    
    if contract.status != 'draft':
        messages.error(request, 'Chỉ có thể xóa hợp đồng ở trạng thái Nháp!')
        return redirect('contract_detail', contract_id=contract.id)
    
    contract_code = contract.contract_code
    contract.delete()
    
    messages.success(request, f'Hợp đồng {contract_code} đã được xóa!')
    logger.info(f"Contract {contract_code} deleted by {request.user.email}")
    return redirect('manage_contracts')


@login_required
@require_hr
@require_POST
def renew_contract(request, contract_id):
    """Renew contract - create new contract based on old one (HR only)"""
    old_contract = get_object_or_404(Contract, pk=contract_id)
    
    # Parse dates from request
    new_start_date = request.POST.get('new_start_date')
    new_end_date = request.POST.get('new_end_date')
    
    if not new_start_date:
        messages.error(request, 'Vui lòng nhập ngày bắt đầu hợp đồng mới!')
        return redirect('contract_detail', contract_id=contract_id)
    
    # Create new contract
    new_contract = Contract.objects.create(
        employee=old_contract.employee,
        contract_type=old_contract.contract_type,
        start_date=new_start_date,
        end_date=new_end_date if new_end_date else None,
        base_salary=old_contract.base_salary,
        allowances=old_contract.allowances,
        job_title=old_contract.job_title,
        department=old_contract.department,
        work_location=old_contract.work_location,
        working_hours=old_contract.working_hours,
        terms=old_contract.terms,
        notes=f"Gia hạn từ hợp đồng {old_contract.contract_code}",
        status='draft',
        renewed_from=old_contract,
        created_by=old_contract.created_by
    )
    
    # Update old contract status
    old_contract.status = 'renewed'
    old_contract.save()
    
    # Log history for both contracts
    try:
        performer = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        performer = None
    
    ContractHistory.objects.create(
        contract=old_contract,
        action='renewed',
        description=f"Hợp đồng được gia hạn thành {new_contract.contract_code}",
        performed_by=performer
    )
    
    ContractHistory.objects.create(
        contract=new_contract,
        action='created',
        description=f"Hợp đồng mới được tạo từ gia hạn {old_contract.contract_code}",
        performed_by=performer
    )
    
    messages.success(request, f'Đã tạo hợp đồng gia hạn {new_contract.contract_code}!')
    logger.info(f"Contract {old_contract.contract_code} renewed to {new_contract.contract_code}")
    return redirect('contract_detail', contract_id=new_contract.id)


@login_required
@require_hr_or_manager
def expiring_contracts(request):
    """List contracts expiring soon (HR: all, Manager: department only)"""
    days_ahead = int(request.GET.get('days', 30))
    
    today = timezone.now().date()
    future_date = today + timedelta(days=days_ahead)
    
    contracts = Contract.objects.filter(
        status='active',
        end_date__isnull=False,
        end_date__lte=future_date,
        end_date__gte=today
    ).select_related('employee', 'job_title', 'department').order_by('end_date')
    
    # Row-level filtering for managers
    if not request.user.is_superuser and not request.user.groups.filter(name='HR').exists():
        try:
            user_employee = request.user.employee
            if user_employee.is_manager:
                contracts = contracts.filter(employee__department=user_employee.department)
        except:
            contracts = Contract.objects.none()
    
    # Calculate statistics
    urgent_count = contracts.filter(end_date__lte=today + timedelta(days=7)).count()
    warning_count = contracts.filter(end_date__lte=today + timedelta(days=15), end_date__gt=today + timedelta(days=7)).count()
    notice_count = contracts.filter(end_date__gt=today + timedelta(days=15)).count()
    
    context = {
        'contracts': contracts,
        'days_ahead': days_ahead,
        'today': today,
        'urgent_count': urgent_count,
        'warning_count': warning_count,
        'notice_count': notice_count,
    }
    
    return render(request, 'hod_template/expiring_contracts.html', context)


@login_required
@require_hr_or_manager
def employee_contracts(request, employee_id):
    """View all contracts of an employee (HR: all, Manager: department only)"""
    employee = get_object_or_404(Employee, pk=employee_id)
    
    # Check row-level permission for managers
    if not request.user.is_superuser and not request.user.groups.filter(name='HR').exists():
        try:
            user_employee = request.user.employee
            if not user_employee.is_manager or employee.department != user_employee.department:
                messages.error(request, 'Bạn không có quyền xem hợp đồng của nhân viên này.')
                return redirect('manage_contracts')
        except:
            messages.error(request, 'Bạn không có quyền truy cập.')
            return redirect('manage_contracts')
    
    contracts = Contract.objects.filter(employee=employee).order_by('-start_date')
    
    # Calculate statistics
    active_count = contracts.filter(status='active').count()
    expired_count = contracts.filter(status='expired').count()
    renewed_count = contracts.filter(status='renewed').count()
    draft_count = contracts.filter(status='draft').count()
    
    # Get active contract
    active_contract = contracts.filter(status='active').first()
    
    context = {
        'employee': employee,
        'contracts': contracts,
        'active_contract': active_contract,
        'active_count': active_count,
        'expired_count': expired_count,
        'renewed_count': renewed_count,
        'draft_count': draft_count,
    }
    
    return render(request, 'hod_template/employee_contracts.html', context)


# ============================================================================
# PERFORMANCE APPRAISAL VIEWS
# ============================================================================

@login_required
def appraisal_periods(request):
    """HR quản lý các kỳ đánh giá"""
    periods = AppraisalPeriod.objects.all().prefetch_related('applicable_departments', 'applicable_job_titles')
    
    # Statistics
    active_periods = periods.filter(status='active').count()
    draft_periods = periods.filter(status='draft').count()
    
    context = {
        'periods': periods,
        'active_periods': active_periods,
        'draft_periods': draft_periods,
    }
    
    return render(request, 'hod_template/appraisal_periods.html', context)


@login_required
@hr_required
def create_appraisal_period(request):
    """Tạo kỳ đánh giá mới"""
    if request.method == 'POST':
        form = AppraisalPeriodForm(request.POST)
        if form.is_valid():
            try:
                period = form.save(commit=False)
                period.created_by = Employee.objects.get(email=request.user.email)
                period.save()
                form.save_m2m()  # Save ManyToMany relationships
                
                messages.success(request, f'Đã tạo kỳ đánh giá: {period.name}')
                logger.info(f"Created appraisal period: {period.name} by {request.user.username}")
                return redirect('appraisal_periods')
            except Exception as e:
                logger.error(f"Error creating appraisal period: {e}")
                messages.error(request, f'Lỗi: {str(e)}')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin')
    else:
        form = AppraisalPeriodForm()
    
    context = {'form': form}
    return render(request, 'hod_template/create_appraisal_period.html', context)


@login_required
def appraisal_period_detail(request, period_id):
    """Chi tiết kỳ đánh giá và quản lý tiêu chí"""
    period = get_object_or_404(AppraisalPeriod, id=period_id)
    criteria = period.criteria.all()
    appraisals = period.appraisals.select_related('employee', 'manager').all()
    
    # Statistics
    total_appraisals = appraisals.count()
    pending_self = appraisals.filter(status='pending_self').count()
    pending_manager = appraisals.filter(status='pending_manager').count()
    completed = appraisals.filter(status='completed').count()
    
    # Calculate total weight
    total_weight = sum(float(c.weight) for c in criteria)
    
    context = {
        'period': period,
        'criteria': criteria,
        'appraisals': appraisals,
        'total_appraisals': total_appraisals,
        'pending_self': pending_self,
        'pending_manager': pending_manager,
        'completed': completed,
        'total_weight': total_weight,
    }
    
    return render(request, 'hod_template/appraisal_period_detail.html', context)


@login_required
def add_appraisal_criteria(request, period_id):
    """Thêm tiêu chí đánh giá vào kỳ"""
    period = get_object_or_404(AppraisalPeriod, id=period_id)
    
    if request.method == 'POST':
        form = AppraisalCriteriaForm(request.POST)
        if form.is_valid():
            try:
                criteria = form.save(commit=False)
                criteria.period = period
                criteria.save()
                
                messages.success(request, f'Đã thêm tiêu chí: {criteria.name}')
                logger.info(f"Added criteria {criteria.name} to period {period.name}")
                return redirect('appraisal_period_detail', period_id=period.id)
            except Exception as e:
                logger.error(f"Error adding criteria: {e}")
                messages.error(request, f'Lỗi khi lưu: {str(e)}')
        else:
            # Show validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            logger.warning(f"Form validation failed: {form.errors}")
    else:
        form = AppraisalCriteriaForm()
    
    context = {
        'form': form,
        'period': period,
    }
    return render(request, 'hod_template/add_appraisal_criteria.html', context)


@login_required
@hr_required
def edit_appraisal_criteria(request, criteria_id):
    """Chỉnh sửa tiêu chí đánh giá"""
    criteria = get_object_or_404(AppraisalCriteria, id=criteria_id)
    period = criteria.period
    
    if request.method == 'POST':
        form = AppraisalCriteriaForm(request.POST, instance=criteria)
        if form.is_valid():
            try:
                criteria = form.save()
                messages.success(request, f'Đã cập nhật tiêu chí: {criteria.name}')
                logger.info(f"Updated criteria {criteria.name} in period {period.name}")
                return redirect('appraisal_period_detail', period_id=period.id)
            except Exception as e:
                logger.error(f"Error updating criteria: {e}")
                messages.error(request, f'Lỗi khi cập nhật: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = AppraisalCriteriaForm(instance=criteria)
    
    context = {
        'form': form,
        'period': period,
        'criteria': criteria,
        'is_edit': True,
    }
    return render(request, 'hod_template/add_appraisal_criteria.html', context)


@login_required
@hr_required
@require_POST
def delete_appraisal_criteria(request, criteria_id):
    """Xóa tiêu chí đánh giá"""
    try:
        criteria = AppraisalCriteria.objects.get(id=criteria_id)
        period_id = criteria.period.id
        criteria_name = criteria.name
        criteria.delete()
        
        logger.info(f"Deleted criteria {criteria_name}")
        return JsonResponse({
            "status": "success",
            "message": f"Đã xóa tiêu chí: {criteria_name}"
        })
    except AppraisalCriteria.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Không tìm thấy tiêu chí"
        }, status=404)
    except Exception as e:
        logger.error(f"Error deleting criteria: {e}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@login_required
@hr_required
@transaction.atomic
def generate_appraisals(request, period_id):
    """Tạo appraisal records cho tất cả nhân viên phù hợp"""
    period = get_object_or_404(AppraisalPeriod, id=period_id)
    
    if request.method == 'POST':
        try:
            # Get applicable employees
            employees = Employee.objects.filter(status__in=[1, 2])  # Thử việc và chính thức
            
            # Filter by department if specified
            if period.applicable_departments.exists():
                employees = employees.filter(department__in=period.applicable_departments.all())
            
            # Filter by job title if specified
            if period.applicable_job_titles.exists():
                employees = employees.filter(job_title__in=period.applicable_job_titles.all())
            
            created_count = 0
            for employee in employees:
                # Check if appraisal already exists
                if not Appraisal.objects.filter(period=period, employee=employee).exists():
                    # Find manager (employee with is_manager=True in same department)
                    manager = Employee.objects.filter(
                        department=employee.department,
                        is_manager=True
                    ).exclude(id=employee.id).first()
                    
                    appraisal = Appraisal.objects.create(
                        period=period,
                        employee=employee,
                        manager=manager,
                        status='pending_self'
                    )
                    
                    # Create AppraisalScore for each criteria
                    for criteria in period.criteria.all():
                        AppraisalScore.objects.create(
                            appraisal=appraisal,
                            criteria=criteria
                        )
                    
                    created_count += 1
            
            messages.success(request, f'Đã tạo {created_count} đánh giá cho nhân viên')
            logger.info(f"Generated {created_count} appraisals for period {period.name}")
            
        except Exception as e:
            logger.error(f"Error generating appraisals: {e}")
            messages.error(request, f'Lỗi: {str(e)}')
    
    return redirect('appraisal_period_detail', period_id=period.id)


@login_required
def my_appraisals(request):
    """Nhân viên xem các đánh giá của mình"""
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, 'Không tìm thấy hồ sơ nhân viên')
        return redirect('employee_dashboard')
    
    appraisals = Appraisal.objects.filter(employee=employee).select_related(
        'period', 'manager'
    ).order_by('-period__start_date')
    
    # Current appraisals (pending action)
    pending_appraisals = appraisals.filter(status='pending_self')
    
    context = {
        'appraisals': appraisals,
        'pending_appraisals': pending_appraisals,
    }
    
    return render(request, 'hod_template/my_appraisals.html', context)


@login_required
@transaction.atomic
def self_assessment(request, appraisal_id):
    """Nhân viên tự đánh giá"""
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, 'Không tìm thấy hồ sơ nhân viên')
        return redirect('employee_dashboard')
    
    appraisal = get_object_or_404(Appraisal, id=appraisal_id, employee=employee)
    
    # Check if can self assess
    if not appraisal.can_self_assess(employee):
        messages.error(request, 'Bạn không thể tự đánh giá lúc này')
        return redirect('my_appraisals')
    
    scores = appraisal.scores.select_related('criteria').all()
    
    if request.method == 'POST':
        try:
            # Save self assessment form
            form = SelfAssessmentForm(request.POST, instance=appraisal)
            if form.is_valid():
                form.save()
            
            # Save scores
            total_score = 0
            total_weight = 0
            for score in scores:
                self_score = request.POST.get(f'self_score_{score.id}')
                self_comment = request.POST.get(f'self_comment_{score.id}', '')
                
                if self_score:
                    score.self_score = int(self_score)
                    score.self_comment = self_comment
                    score.save()
                    
                    # Calculate weighted score
                    total_score += int(self_score) * float(score.criteria.weight)
                    total_weight += float(score.criteria.weight)
            
            # Update appraisal
            if total_weight > 0:
                appraisal.self_overall_score = round(total_score / total_weight, 2)
            appraisal.self_assessment_date = timezone.now()
            appraisal.status = 'pending_manager'
            appraisal.save()
            
            messages.success(request, 'Đã gửi tự đánh giá thành công!')
            logger.info(f"Self assessment completed by {employee.name} for period {appraisal.period.name}")
            return redirect('my_appraisals')
            
        except Exception as e:
            logger.error(f"Error in self assessment: {e}")
            messages.error(request, f'Lỗi: {str(e)}')
    else:
        form = SelfAssessmentForm(instance=appraisal)
    
    context = {
        'appraisal': appraisal,
        'scores': scores,
        'form': form,
    }
    
    return render(request, 'hod_template/self_assessment.html', context)


@login_required
def manager_appraisals(request):
    """Quản lý xem danh sách nhân viên cần đánh giá"""
    try:
        employee = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, 'Không tìm thấy hồ sơ nhân viên')
        return redirect('admin_home')
    
    if not employee.is_manager:
        messages.error(request, 'Bạn không có quyền truy cập')
        return redirect('admin_home')
    
    appraisals = Appraisal.objects.filter(manager=employee).select_related(
        'period', 'employee'
    ).order_by('-period__start_date', 'status')
    
    # Statistics
    pending = appraisals.filter(status='pending_manager').count()
    completed = appraisals.filter(status__in=['pending_hr', 'completed']).count()
    
    context = {
        'appraisals': appraisals,
        'pending': pending,
        'completed': completed,
    }
    
    return render(request, 'hod_template/manager_appraisals.html', context)


@login_required
@transaction.atomic
def manager_review(request, appraisal_id):
    """Quản lý đánh giá nhân viên"""
    try:
        manager = Employee.objects.get(email=request.user.email)
    except Employee.DoesNotExist:
        messages.error(request, 'Không tìm thấy hồ sơ nhân viên')
        return redirect('admin_home')
    
    appraisal = get_object_or_404(Appraisal, id=appraisal_id, manager=manager)
    
    # Check if can review
    if not appraisal.can_manager_review(manager):
        messages.error(request, 'Không thể đánh giá lúc này')
        return redirect('manager_appraisals')
    
    scores = appraisal.scores.select_related('criteria').all()
    
    if request.method == 'POST':
        try:
            # Save manager review form
            form = ManagerReviewForm(request.POST, instance=appraisal)
            if form.is_valid():
                form.save()
            
            # Save scores
            total_score = 0
            total_weight = 0
            for score in scores:
                manager_score = request.POST.get(f'manager_score_{score.id}')
                manager_comment = request.POST.get(f'manager_comment_{score.id}', '')
                
                if manager_score:
                    score.manager_score = int(manager_score)
                    score.manager_comment = manager_comment
                    score.final_score = int(manager_score)  # Default final = manager score
                    score.save()
                    
                    # Calculate weighted score
                    total_score += int(manager_score) * float(score.criteria.weight)
                    total_weight += float(score.criteria.weight)
            
            # Update appraisal
            if total_weight > 0:
                appraisal.manager_overall_score = round(total_score / total_weight, 2)
                appraisal.final_score = appraisal.manager_overall_score
            appraisal.manager_review_date = timezone.now()
            appraisal.status = 'pending_hr'
            appraisal.save()
            
            messages.success(request, 'Đã hoàn thành đánh giá!')
            logger.info(f"Manager review completed by {manager.name} for {appraisal.employee.name}")
            return redirect('manager_appraisals')
            
        except Exception as e:
            logger.error(f"Error in manager review: {e}")
            messages.error(request, f'Lỗi: {str(e)}')
    else:
        form = ManagerReviewForm(instance=appraisal)
    
    context = {
        'appraisal': appraisal,
        'scores': scores,
        'form': form,
    }
    
    return render(request, 'hod_template/manager_review.html', context)


@login_required
@hr_required
def hr_appraisals(request):
    """HR xem tất cả đánh giá cần phê duyệt"""
    appraisals = Appraisal.objects.select_related(
        'period', 'employee', 'manager'
    ).order_by('-period__start_date', 'status')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        appraisals = appraisals.filter(status=status_filter)
    
    # Statistics
    pending_hr = appraisals.filter(status='pending_hr').count()
    completed = appraisals.filter(status='completed').count()
    pending_self = appraisals.filter(status='pending_self').count()
    pending_manager = appraisals.filter(status='pending_manager').count()
    
    context = {
        'appraisals': appraisals,
        'pending_hr': pending_hr,
        'completed': completed,
        'pending_self': pending_self,
        'pending_manager': pending_manager,
        'status_filter': status_filter,
    }
    
    return render(request, 'hod_template/hr_appraisals.html', context)


@login_required
@hr_required
@transaction.atomic
def hr_final_review(request, appraisal_id):
    """HR phê duyệt cuối cùng"""
    appraisal = get_object_or_404(Appraisal, id=appraisal_id)
    scores = appraisal.scores.select_related('criteria').all()
    
    if request.method == 'POST':
        try:
            form = HRFinalReviewForm(request.POST, instance=appraisal)
            if form.is_valid():
                appraisal = form.save(commit=False)
                appraisal.status = 'completed'
                appraisal.final_review_date = timezone.now()
                
                # Apply salary adjustment if any
                if appraisal.salary_adjustment:
                    employee = appraisal.employee
                    employee.salary += float(appraisal.salary_adjustment)
                    employee.save()
                    logger.info(f"Salary adjusted for {employee.name}: +{appraisal.salary_adjustment}")
                
                appraisal.save()
                
                messages.success(request, 'Đã hoàn tất đánh giá!')
                logger.info(f"HR final review completed for {appraisal.employee.name}")
                return redirect('hr_appraisals')
                
        except Exception as e:
            logger.error(f"Error in HR final review: {e}")
            messages.error(request, f'Lỗi: {str(e)}')
    else:
        form = HRFinalReviewForm(instance=appraisal)
    
    context = {
        'appraisal': appraisal,
        'scores': scores,
        'form': form,
    }
    
    return render(request, 'hod_template/hr_final_review.html', context)


@login_required
def appraisal_detail(request, appraisal_id):
    """Xem chi tiết đánh giá (read-only)"""
    appraisal = get_object_or_404(Appraisal.objects.select_related(
        'period', 'employee', 'manager'
    ), id=appraisal_id)
    
    scores = appraisal.scores.select_related('criteria').all()
    comments = appraisal.comments.select_related('author').all()
    
    context = {
        'appraisal': appraisal,
        'scores': scores,
        'comments': comments,
    }
    
    return render(request, 'hod_template/appraisal_detail.html', context)


# ========================================
# USER MANAGEMENT VIEWS
# ========================================

@login_required
@hr_required
def manage_users(request):
    """Quản lý người dùng hệ thống"""
    users = User.objects.all().prefetch_related('groups').order_by('-date_joined')
    
    context = {
        'users': users,
    }
    return render(request, 'hod_template/manage_users.html', context)


@login_required
@hr_required
def create_user(request):
    """Tạo người dùng mới"""
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            is_active = request.POST.get('is_active') == 'on'
            group_ids = request.POST.getlist('groups')
            employee_id = request.POST.get('employee_id')
            
            # Validate
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username đã tồn tại!')
                return redirect('management_create_user')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email đã được sử dụng!')
                return redirect('management_create_user')
            
            if password != password2:
                messages.error(request, 'Mật khẩu xác nhận không khớp!')
                return redirect('management_create_user')
            
            if len(password) < 8:
                messages.error(request, 'Mật khẩu phải có ít nhất 8 ký tự!')
                return redirect('management_create_user')
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=is_active
            )
            
            # Assign groups
            if group_ids:
                groups = Group.objects.filter(id__in=group_ids)
                user.groups.set(groups)
            
            # Link to employee if specified
            if employee_id:
                try:
                    employee = Employee.objects.get(id=employee_id)
                    employee.email = email  # Update employee email to match
                    employee.save()
                except Employee.DoesNotExist:
                    pass
            
            messages.success(request, f'Đã tạo người dùng: {username}')
            logger.info(f"Created user {username} by {request.user.username}")
            return redirect('management_manage_users')
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            messages.error(request, f'Lỗi khi tạo người dùng: {str(e)}')
            return redirect('management_create_user')
    
    # GET request
    all_groups = Group.objects.all()
    employees = Employee.objects.filter(status__in=[1, 2]).select_related('department')
    
    context = {
        'all_groups': all_groups,
        'employees': employees,
        'is_edit': False,
    }
    return render(request, 'hod_template/user_form.html', context)


@login_required
@hr_required
def edit_user(request, user_id):
    """Chỉnh sửa người dùng"""
    user_obj = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            is_active = request.POST.get('is_active') == 'on'
            group_ids = request.POST.getlist('groups')
            employee_id = request.POST.get('employee_id')
            new_password = request.POST.get('new_password')
            new_password2 = request.POST.get('new_password2')
            
            # Validate email uniqueness (except current user)
            if User.objects.filter(email=email).exclude(id=user_id).exists():
                messages.error(request, 'Email đã được sử dụng bởi người dùng khác!')
                return redirect('management_edit_user', user_id=user_id)
            
            # Update basic info
            user_obj.email = email
            user_obj.first_name = first_name
            user_obj.last_name = last_name
            user_obj.is_active = is_active
            
            # Update password if provided
            if new_password:
                if new_password != new_password2:
                    messages.error(request, 'Mật khẩu xác nhận không khớp!')
                    return redirect('management_edit_user', user_id=user_id)
                
                if len(new_password) < 8:
                    messages.error(request, 'Mật khẩu phải có ít nhất 8 ký tự!')
                    return redirect('management_edit_user', user_id=user_id)
                
                user_obj.set_password(new_password)
            
            user_obj.save()
            
            # Update groups
            if group_ids:
                groups = Group.objects.filter(id__in=group_ids)
                user_obj.groups.set(groups)
            else:
                user_obj.groups.clear()
            
            # Link to employee
            if employee_id:
                try:
                    employee = Employee.objects.get(id=employee_id)
                    employee.email = email
                    employee.save()
                except Employee.DoesNotExist:
                    pass
            
            messages.success(request, f'Đã cập nhật người dùng: {user_obj.username}')
            logger.info(f"Updated user {user_obj.username} by {request.user.username}")
            return redirect('management_manage_users')
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            messages.error(request, f'Lỗi khi cập nhật: {str(e)}')
            return redirect('management_edit_user', user_id=user_id)
    
    # GET request
    all_groups = Group.objects.all()
    employees = Employee.objects.filter(status__in=[1, 2]).select_related('department')
    
    # Try to find linked employee
    try:
        user_obj.employee = Employee.objects.get(email=user_obj.email)
    except Employee.DoesNotExist:
        user_obj.employee = None
    
    context = {
        'user_obj': user_obj,
        'all_groups': all_groups,
        'employees': employees,
        'is_edit': True,
    }
    return render(request, 'hod_template/user_form.html', context)


@login_required
@hr_required
@require_POST
def delete_user(request, user_id):
    """Xóa người dùng"""
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent deleting superuser
        if user.is_superuser:
            return JsonResponse({
                "status": "error",
                "message": "Không thể xóa superuser!"
            }, status=403)
        
        # Prevent deleting self
        if user.id == request.user.id:
            return JsonResponse({
                "status": "error",
                "message": "Không thể xóa chính mình!"
            }, status=403)
        
        username = user.username
        user.delete()
        
        logger.info(f"Deleted user {username} by {request.user.username}")
        return JsonResponse({
            "status": "success",
            "message": f"Đã xóa người dùng: {username}"
        })
    except User.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Không tìm thấy người dùng"
        }, status=404)
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


# ======================== REWARD MANAGEMENT ========================

@login_required
@hr_only
def reward_list(request):
    """Danh sách khen thưởng"""
    from django.db import models as db_models
    
    rewards = Reward.objects.all().select_related('employee', 'employee__department').order_by('-date')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        rewards = rewards.filter(
            db_models.Q(employee__name__icontains=search_query) |
            db_models.Q(description__icontains=search_query) |
            db_models.Q(number__icontains=search_query)
        )
    
    # Filter by year
    year_filter = request.GET.get('year')
    if year_filter:
        rewards = rewards.filter(date__year=year_filter)
    
    # Filter by department
    dept_filter = request.GET.get('department')
    if dept_filter:
        rewards = rewards.filter(employee__department_id=dept_filter)
    
    # Pagination
    paginator = Paginator(rewards, 20)
    page = request.GET.get('page', 1)
    try:
        rewards = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        rewards = paginator.page(1)
    
    # Stats
    total_rewards = Reward.objects.count()
    total_amount = Reward.objects.aggregate(total=Sum('amount'))['total'] or 0
    this_year = timezone.localtime(timezone.now()).year
    year_rewards = Reward.objects.filter(date__year=this_year).count()
    year_amount = Reward.objects.filter(date__year=this_year).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get years for filter
    years = Reward.objects.dates('date', 'year', order='DESC')
    departments = Department.objects.all()
    
    context = {
        'rewards': rewards,
        'search_query': search_query,
        'year_filter': year_filter,
        'dept_filter': dept_filter,
        'years': [y.year for y in years],
        'departments': departments,
        'total_rewards': total_rewards,
        'total_amount': total_amount,
        'year_rewards': year_rewards,
        'year_amount': year_amount,
        'current_year': this_year,
    }
    return render(request, 'hod_template/rewards/list.html', context)


@login_required
@hr_only
def reward_create(request):
    """Tạo khen thưởng mới"""
    if request.method == 'POST':
        form = RewardForm(request.POST)
        if form.is_valid():
            reward = form.save()
            
            # Send email notification
            try:
                from .email_service import EmailService
                EmailService.send_reward_notification(reward)
            except Exception as email_error:
                logger.warning(f"Failed to send reward notification email: {email_error}")
            
            messages.success(request, f'Đã tạo khen thưởng #{reward.number} cho {reward.employee.name}')
            return redirect('reward_list')
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại.')
    else:
        # Auto generate next number
        last_reward = Reward.objects.order_by('-number').first()
        next_number = (last_reward.number + 1) if last_reward else 1
        form = RewardForm(initial={'number': next_number, 'date': timezone.localtime(timezone.now())})
    
    return render(request, 'hod_template/rewards/form.html', {
        'form': form,
        'title': 'Tạo khen thưởng mới',
        'action': 'create'
    })


@login_required
@hr_only
def reward_edit(request, pk):
    """Sửa khen thưởng"""
    reward = get_object_or_404(Reward, pk=pk)
    
    if request.method == 'POST':
        form = RewardForm(request.POST, instance=reward)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật khen thưởng #{reward.number}')
            return redirect('reward_list')
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại.')
    else:
        form = RewardForm(instance=reward)
    
    return render(request, 'hod_template/rewards/form.html', {
        'form': form,
        'reward': reward,
        'title': f'Sửa khen thưởng #{reward.number}',
        'action': 'edit'
    })


@login_required
@hr_only
def reward_delete(request, pk):
    """Xóa khen thưởng"""
    reward = get_object_or_404(Reward, pk=pk)
    
    if request.method == 'POST':
        number = reward.number
        employee_name = reward.employee.name
        reward.delete()
        messages.success(request, f'Đã xóa khen thưởng #{number} của {employee_name}')
        return redirect('reward_list')
    
    return render(request, 'hod_template/rewards/confirm_delete.html', {
        'reward': reward
    })


@login_required
@hr_only
def reward_detail(request, pk):
    """Chi tiết khen thưởng"""
    reward = get_object_or_404(Reward, pk=pk)
    return render(request, 'hod_template/rewards/detail.html', {
        'reward': reward
    })


# ======================== DISCIPLINE MANAGEMENT ========================

@login_required
@hr_only
def discipline_list(request):
    """Danh sách kỷ luật"""
    from django.db import models as db_models
    
    disciplines = Discipline.objects.all().select_related('employee', 'employee__department').order_by('-date')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        disciplines = disciplines.filter(
            db_models.Q(employee__name__icontains=search_query) |
            db_models.Q(description__icontains=search_query) |
            db_models.Q(number__icontains=search_query)
        )
    
    # Filter by year
    year_filter = request.GET.get('year')
    if year_filter:
        disciplines = disciplines.filter(date__year=year_filter)
    
    # Filter by department
    dept_filter = request.GET.get('department')
    if dept_filter:
        disciplines = disciplines.filter(employee__department_id=dept_filter)
    
    # Pagination
    paginator = Paginator(disciplines, 20)
    page = request.GET.get('page', 1)
    try:
        disciplines = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        disciplines = paginator.page(1)
    
    # Stats
    total_disciplines = Discipline.objects.count()
    total_amount = Discipline.objects.aggregate(total=Sum('amount'))['total'] or 0
    this_year = timezone.localtime(timezone.now()).year
    year_disciplines = Discipline.objects.filter(date__year=this_year).count()
    year_amount = Discipline.objects.filter(date__year=this_year).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get years for filter
    years = Discipline.objects.dates('date', 'year', order='DESC')
    departments = Department.objects.all()
    
    context = {
        'disciplines': disciplines,
        'search_query': search_query,
        'year_filter': year_filter,
        'dept_filter': dept_filter,
        'years': [y.year for y in years],
        'departments': departments,
        'total_disciplines': total_disciplines,
        'total_amount': total_amount,
        'year_disciplines': year_disciplines,
        'year_amount': year_amount,
        'current_year': this_year,
    }
    return render(request, 'hod_template/disciplines/list.html', context)


@login_required
@hr_only
def discipline_create(request):
    """Tạo kỷ luật mới"""
    if request.method == 'POST':
        form = DisciplineForm(request.POST)
        if form.is_valid():
            discipline = form.save()
            
            # Send email notification
            try:
                from .email_service import EmailService
                EmailService.send_discipline_notification(discipline)
            except Exception as email_error:
                logger.warning(f"Failed to send discipline notification email: {email_error}")
            
            messages.success(request, f'Đã tạo kỷ luật #{discipline.number} cho {discipline.employee.name}')
            return redirect('discipline_list')
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại.')
    else:
        # Auto generate next number
        last_discipline = Discipline.objects.order_by('-number').first()
        next_number = (last_discipline.number + 1) if last_discipline else 1
        form = DisciplineForm(initial={'number': next_number, 'date': timezone.localtime(timezone.now())})
    
    return render(request, 'hod_template/disciplines/form.html', {
        'form': form,
        'title': 'Tạo kỷ luật mới',
        'action': 'create'
    })


@login_required
@hr_only
def discipline_edit(request, pk):
    """Sửa kỷ luật"""
    discipline = get_object_or_404(Discipline, pk=pk)
    
    if request.method == 'POST':
        form = DisciplineForm(request.POST, instance=discipline)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật kỷ luật #{discipline.number}')
            return redirect('discipline_list')
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại.')
    else:
        form = DisciplineForm(instance=discipline)
    
    return render(request, 'hod_template/disciplines/form.html', {
        'form': form,
        'discipline': discipline,
        'title': f'Sửa kỷ luật #{discipline.number}',
        'action': 'edit'
    })


@login_required
@hr_only
def discipline_delete(request, pk):
    """Xóa kỷ luật"""
    discipline = get_object_or_404(Discipline, pk=pk)
    
    if request.method == 'POST':
        number = discipline.number
        employee_name = discipline.employee.name
        discipline.delete()
        messages.success(request, f'Đã xóa kỷ luật #{number} của {employee_name}')
        return redirect('discipline_list')
    
    return render(request, 'hod_template/disciplines/confirm_delete.html', {
        'discipline': discipline
    })


@login_required
@hr_only
def discipline_detail(request, pk):
    """Chi tiết kỷ luật"""
    discipline = get_object_or_404(Discipline, pk=pk)
    return render(request, 'hod_template/disciplines/detail.html', {
        'discipline': discipline
    })