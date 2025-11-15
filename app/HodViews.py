from django.http import HttpResponse, HttpResponseRedirect

from django.core.files.storage import FileSystemStorage, default_storage
from django.utils.text import get_valid_filename
import uuid
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.core.exceptions import ValidationError

from .models import JobTitle, Department, Employee, Attendance, Reward, Discipline, Payroll, LeaveType, LeaveRequest, LeaveBalance, ExpenseCategory, Expense
from .forms import EmployeeForm, LeaveTypeForm, LeaveRequestForm, ExpenseCategoryForm, ExpenseForm
from .validators import (
    validate_image_file, 
    validate_document_file, 
    validate_salary,
    validate_phone_number,
    validate_email
)

from django.http import JsonResponse
from datetime import datetime, timedelta
import json
import xlwt
import calendar
from django.db.models import Sum
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import logging

# Configure logger
logger = logging.getLogger(__name__)

@login_required
def admin_home(request):
    employees = Employee.objects.all()
    departments = Department.objects.all()
    payrolls = Payroll.objects.all()
    context = {
        "employees": employees,
        "departments": departments,
        "payrolls": payrolls
    }
    logger.info(f"Admin home accessed by {request.user.username}")
    return render(request, "hod_template/home_content.html", context)

def generate_employee_code():
    last_employee = Employee.objects.order_by('-id').first()
    if last_employee and last_employee.employee_code:
        last_code = last_employee.employee_code
        number = int(last_code.replace("NV", ""))
        new_number = number + 1
    else:
        new_number = 1
    return f"NV{new_number:04d}"  # định dạng NV0001, NV0002,...

@login_required
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
def update_employee_save(request):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
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
    return render(request, "hod_template/add_attendance.html", {"employees": employees})

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
def delete_attendance(request):
    if request.method == "POST":
        attendance_id = request.POST.get("id")
        try:
            logger.info(f"Deleting attendance ID {attendance_id} by {request.user.username}")
            attendance = Attendance.objects.get(id=attendance_id)
            attendance.delete()
            return JsonResponse({"status": "success"})
        except Exception as e:
            logger.error(f"Error deleting attendance: {e}")
            return JsonResponse({"status": "error"})

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
            hourly_rate = (employee.salary * employee.job_title.salary_coefficient) / (standard_working_days * 8)

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
def manage_payroll(request):
    # Optimize query with select_related
    payrolls = Payroll.objects.select_related('employee', 'employee__department').all().order_by('-year', '-month')
    departments = Department.objects.all()
    current_year = datetime.now().year
    years = range(current_year, current_year - 5, -1)
    return render(request, "hod_template/manage_payroll.html", {
        "payrolls": payrolls,
        "departments": departments,
        "years": years
    })

@login_required
def edit_payroll(request, payroll_id):
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
def delete_payroll(request):
    payroll_id = request.POST.get("id")
    try:
        payroll = Payroll.objects.get(id=payroll_id)
        if payroll.status == 'pending':
            payroll.delete()
            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "error", "message": "Không thể xóa bảng lương đã xác nhận"})
    except Exception as e:
        logger.error(f"Error deleting payroll: {e}")
        return JsonResponse({"status": "error"})

@login_required
@require_POST
def confirm_payroll(request):
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
def view_payroll(request, payroll_id):
    payroll = get_object_or_404(Payroll, id=payroll_id)
    return render(request, "hod_template/view_payroll.html", {
        "payroll": payroll
    })

@login_required
def export_payroll(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="payroll_report.xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Bảng Lương')
    
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    columns = ['STT', 'Tháng/Năm', 'Mã NV', 'Tên NV', 'Phòng Ban', 'Lương CB', 'Hệ Số', 'Lương/Giờ', 'Tổng Giờ', 'Thưởng', 'Phạt', 'Tổng Lương', 'Trạng Thái']
    
    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)
    
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    
    rows = Payroll.objects.all().values_list(
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
def manage_leave_requests(request):
    """HR/Manager xem tất cả đơn xin nghỉ phép"""
    # Filter options
    status_filter = request.GET.get('status', '')
    employee_filter = request.GET.get('employee', '')
    
    leave_requests = LeaveRequest.objects.select_related('employee', 'leave_type', 'approved_by').all()
    
    if status_filter:
        leave_requests = leave_requests.filter(status=status_filter)
    if employee_filter:
        leave_requests = leave_requests.filter(employee_id=employee_filter)
    
    leave_requests = leave_requests.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(leave_requests, 20)
    page = request.GET.get('page')
    try:
        leave_requests = paginator.page(page)
    except PageNotAnInteger:
        leave_requests = paginator.page(1)
    except EmptyPage:
        leave_requests = paginator.page(paginator.num_pages)
    
    employees = Employee.objects.all()
    
    return render(request, "hod_template/manage_leave_requests.html", {
        "leave_requests": leave_requests,
        "employees": employees
    })

@login_required
def view_leave_request(request, request_id):
    """Xem chi tiết đơn xin nghỉ phép"""
    leave_request = get_object_or_404(LeaveRequest, id=request_id)
    
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
def approve_leave_request(request, request_id):
    """Duyệt đơn xin nghỉ phép"""
    try:
        leave_request = LeaveRequest.objects.get(id=request_id)
        
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
def reject_leave_request(request, request_id):
    """Từ chối đơn xin nghỉ phép"""
    try:
        leave_request = LeaveRequest.objects.get(id=request_id)
        
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
def edit_expense_category_save(request):
    """Chỉnh sửa danh mục chi phí"""
    try:
        category_id = request.POST.get('category_id')
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
def manage_expenses(request):
    """HR/Manager quản lý tất cả yêu cầu chi phí"""
    # Lọc theo status
    status_filter = request.GET.get('status', '')
    expenses = Expense.objects.all().order_by('-created_at')
    
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
        expenses = paginator.page(page)
    except PageNotAnInteger:
        expenses = paginator.page(1)
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
def view_expense(request, expense_id):
    """Xem chi tiết yêu cầu chi phí"""
    try:
        expense = Expense.objects.get(id=expense_id)
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
def approve_expense(request, expense_id):
    """Duyệt yêu cầu chi phí"""
    try:
        expense = Expense.objects.get(id=expense_id)
        approver = Employee.objects.get(email=request.user.email)
        
        if expense.status != 'pending':
            messages.error(request, "Yêu cầu chi phí này đã được xử lý")
            return redirect("manage_expenses")
        
        expense.status = 'approved'
        expense.approved_by = approver
        expense.approved_at = timezone.now()
        expense.save()
        
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
def reject_expense(request, expense_id):
    """Từ chối yêu cầu chi phí"""
    try:
        expense = Expense.objects.get(id=expense_id)
        rejector = Employee.objects.get(email=request.user.email)
        
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

