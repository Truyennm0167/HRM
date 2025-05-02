from django.http import HttpResponse, HttpResponseRedirect

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import JobTitle, Department, Employee, Attendance, Reward, Discipline, Payroll
from .forms import EmployeeForm

from django.http import JsonResponse
from datetime import datetime, timedelta
import json
import xlwt
import calendar
from django.db.models import Sum
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def admin_home(request):
    employees = Employee.objects.all()
    departments = Department.objects.all()
    payrolls = Payroll.objects.all()
    context = {
        "employees": employees,
        "departments": departments,
        "payrolls": payrolls
    }
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

            # Xử lý avatar nếu có
            avatar_url = None
            if 'employee_avatar' in request.FILES:
                avatar = request.FILES['employee_avatar']
                fs = FileSystemStorage(location='media/avatars')  # Tạo thư mục 'avatars' trong 'media'
                filename = fs.save(avatar.name, avatar)
                avatar_url = 'avatars/' + filename  # lưu đường dẫn tương đối trong DB

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
            messages.success(request, "Thêm Nhân viên thành công.")

            return redirect("/add_employee")
        except Exception as e:
            print("Lỗi khi thêm nhân viên:", e)
            messages.error(request, "Thêm Nhân viên không thành công")
            return redirect("/add_employee")


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



def delete_department(request, department_id):
    try:
        department = Department.objects.get(id=department_id)
        if Employee.objects.filter(department=department).exists():
            messages.error(request, "Không thể xóa phòng ban vì vẫn còn nhân viên trực thuộc.")
            return redirect('department_page')  # hoặc đường dẫn tương ứng
        department.delete()
        messages.success(request, "Xóa phòng ban thành công.")
    except Department.DoesNotExist:
        messages.error(request, "Không tìm thấy phòng ban.")
    except Exception as e:
        messages.error(request, f"Lỗi khi xóa phòng ban: {e}")

    return redirect('department_page')

def job_title(request):
    job_titles = JobTitle.objects.all()
    context = {
        'job_titles': job_titles
    }
    return render(request, "hod_template/job_title_template.html", context)

def view_job_title(request, job_title_id):
    job_titles = JobTitle.objects.all()
    job = get_object_or_404(JobTitle, id=job_title_id)
    context = {
        "job_titles": job_titles,
        "selected_job": job
    }
    return render(request, "hod_template/job_title_template.html", context)

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


def delete_job_title(request, job_title_id):
    try:
        job = JobTitle.objects.get(id=job_title_id)
        job.delete()
        messages.success(request, "Xóa chức vụ thành công.")
    except JobTitle.DoesNotExist:
        messages.error(request, "Chức vụ không tồn tại.")
    return redirect("/job_title")

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
            employee.avatar.save(avatar.name, avatar)

        # Lưu thay đổi vào cơ sở dữ liệu
        employee.save()

        messages.success(request, 'Cập nhật hồ sơ thành công.')
        return redirect('employee_detail', employee_id=employee.id)

    else:
        return redirect('employee_list')

def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')  # hoặc nơi bạn muốn chuyển hướng sau khi xóa

def manage_attendance(request):
    attendances = Attendance.objects.all().order_by('-date')
    departments = Department.objects.all()
    return render(request, "hod_template/manage_attendance.html", {
        "attendances": attendances,
        "departments": departments
    })

def add_attendance(request):
    employees = Employee.objects.all()
    return render(request, "hod_template/add_attendance.html", {"employees": employees})

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

def check_attendance_date(request):
    if request.method == "POST":
        date = request.POST.get("date")
        exists = Attendance.objects.filter(date=date).exists()
        return JsonResponse({"status": "exists" if exists else "new"})

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

def edit_attendance(request, attendance_id):
    attendance = Attendance.objects.get(id=attendance_id)
    employees = Employee.objects.all()
    return render(request, "hod_template/add_attendance.html", {
        "attendance": attendance,
        "employees": employees,
        "edit_mode": True,
        "attendance_date": attendance.date.strftime('%Y-%m-%d')
    })

def delete_attendance(request):
    if request.method == "POST":
        attendance_id = request.POST.get("id")
        try:
            attendance = Attendance.objects.get(id=attendance_id)
            attendance.delete()
            return JsonResponse({"status": "success"})
        except:
            return JsonResponse({"status": "error"})

def export_attendance(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.xls"'
    
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

def calculate_payroll(request):
    employees = Employee.objects.all()
    current_year = datetime.now().year
    years = range(current_year, current_year - 5, -1)
    return render(request, "hod_template/calculate_payroll.html", {
        "employees": employees,
        "years": years
    })

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

            # Tính lương theo giờ
            hourly_rate = (employee.salary * employee.job_title.salary_coefficient) / (standard_working_days * 8)

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

            # Tính tổng lương
            total_salary = (hourly_rate * total_hours) + bonus - penalty

            data = {
                "base_salary": employee.salary,
                "salary_coefficient": employee.job_title.salary_coefficient,
                "hourly_rate": hourly_rate,
                "total_working_hours": total_hours,
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

def save_payroll(request):
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

            messages.success(request, "Bảng lương đã được lưu thành công")
            return redirect("manage_payroll")
        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra: {str(e)}")
            return redirect("calculate_payroll")

def manage_payroll(request):
    payrolls = Payroll.objects.all().order_by('-year', '-month')
    departments = Department.objects.all()
    current_year = datetime.now().year
    years = range(current_year, current_year - 5, -1)
    return render(request, "hod_template/manage_payroll.html", {
        "payrolls": payrolls,
        "departments": departments,
        "years": years
    })

def edit_payroll(request, payroll_id):
    try:
        payroll = Payroll.objects.get(id=payroll_id)
        if payroll.status == 'confirmed':
            messages.error(request, "Không thể chỉnh sửa bảng lương đã xác nhận")
            return redirect("manage_payroll")

        employees = Employee.objects.all()
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

def delete_payroll(request):
    if request.method == "POST":
        payroll_id = request.POST.get("id")
        try:
            payroll = Payroll.objects.get(id=payroll_id)
            if payroll.status == 'pending':
                payroll.delete()
                return JsonResponse({"status": "success"})
            return JsonResponse({"status": "error", "message": "Không thể xóa bảng lương đã xác nhận"})
        except:
            return JsonResponse({"status": "error"})

def confirm_payroll(request):
    if request.method == "POST":
        payroll_id = request.POST.get("id")
        try:
            payroll = Payroll.objects.get(id=payroll_id)
            payroll.status = 'confirmed'
            payroll.save()
            return JsonResponse({"status": "success"})
        except:
            return JsonResponse({"status": "error"})

def view_payroll(request, payroll_id):
    payroll = Payroll.objects.get(id=payroll_id)
    return render(request, "hod_template/view_payroll.html", {
        "payroll": payroll
    })

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
