## 1) Tóm tắt nhanh (1 câu)

Dự án là một hệ thống HRM trên Django 4.2, UI AdminLTE, gồm chức năng quản lý nhân viên/phòng ban/chấm công/bảng lương + module AI tuyển dụng (JD/CV upload + scoring). Gần đây đã tập trung vào hardening (auth decorators, validation, logging) và đã tích hợp trang login AdminLTE.

---

## 2) Những điểm mạnh hiện tại

- Kiến trúc Django tiêu chuẩn: project (hrm) + app (app) + module AI (ai_recruitment, `hrm_ai_module/`).
- Templates AdminLTE đã tích hợp tốt, giao diện nhất quán.
- Nhiều view quan trọng đã được bảo vệ bởi `@login_required` và `@require_POST` — tăng an toàn.
- Validation utilities tập trung trong validators.py.
- Logging đã được thêm, nhiều `logger.info/error`.
- Query tối ưu hóa ở vài chỗ bằng `select_related()`; export Excel đã có.
- AI module tách rõ phần parsing/scorer ra `hrm_ai_module/`.

---

## 3) Các rủi ro & vấn đề cần khắc phục (chi tiết, có ví dụ)

1. Logging encoding (thực tế đã thấy UnicodeEncodeError): console/handler không cấu hình encoding → lỗi khi log chuỗi Unicode (tên tiếng Việt).

   - Hiện tượng: UnicodeEncodeError khi ghi log; hrm.log có thể không dùng UTF-8.
   - Hậu quả: crash background logging, loss logs.

2. Không đủ kiểm tra input/format cho một số endpoint (ví dụ `save_payroll`): đã thấy ValueError khi `month` hoặc `year` rỗng.

   - Nên validate/parse an toàn trước convert int() và trả lỗi người dùng rõ ràng.

3. Phân quyền chưa chi tiết (authorization): nhiều view đã require login nhưng không kiểm tra role/permission (is_staff, is_superuser, or specific perms).

   - Hậu quả: user bình thường vẫn có thể thao tác sensitive actions nếu có session.

4. Upload file: cần harden lưu file (tên file duy nhất, path traversal, virus scan, size/type limit).

   - validators.py đã có phép kiểm tra cơ bản, nhưng lưu file còn dùng FileSystemStorage với raw filename; nên dùng unique names + storage safe.

5. CSRF cho AJAX: templates dùng csrf token trong forms; nhưng các AJAX calls có header X-CSRFToken ở vài nơi, không đồng nhất.

   - Nên chuẩn hóa JS helper (lấy cookie và set header) hoặc dùng jQuery setup.

6. Thiếu tests tự động: không có (hoặc ít) unit/integration tests.

   - Rủi ro regressions khi refactor.

7. Lưu trữ mật khẩu / secrets: đã di chuyển đến env, nhưng cần hướng dẫn triển khai (dotenv / production secrets manager) và kiểm tra `.env` không commit.

8. Performance / async:

   - AI scoring có khả năng chậm/blocking — nên làm async (Celery/RQ) hoặc cache kết quả.
   - Một vài query còn gây UnorderedObjectListWarning (paginator nhận queryset chưa order_by) — cần order_by trước khi paginate.

9. Logging structure / audit trail:

   - Hiện logging hữu dụng nhưng không có audit/log DB cho sensitive ops (xóa bảng lương, sửa nhân viên). Mối quan hệ audit vs logger nên tách.

10. Lint & formatting / CI:
    - Nên add flake8/ruff, black and pre-commit, CI để catch style & lint + tests.

---

## 4) Những sửa/nghiên cứu ngắn gọn & ví dụ code (ưu tiên)

Priority A — Khẩn cấp / dễ làm (1–2 giờ)

1. Fix logging file handler encoding (ngăn UnicodeEncodeError):

   - Trong settings.py `LOGGING['handlers']['file']` thêm `'encoding': 'utf-8'`.
   - Ví dụ:
     ```py
     'file': {
         'level': 'INFO',
         'class': 'logging.FileHandler',
         'filename': os.path.join(BASE_DIR, 'hrm.log'),
         'formatter': 'verbose',
         'encoding': 'utf-8',
     },
     ```
   - Lý do: tránh crash logger và mất log Unicode.

2. Hardening `save_payroll` và các parser int() không an toàn:
   - Kiểm tra `month`/`year` trước, trả JsonResponse lỗi hoặc messages nếu thiếu/không hợp lệ.
   - Ví dụ:
     ```py
     try:
         month = int(request.POST.get("month") or 0)
         year = int(request.POST.get("year") or 0)
         if month < 1 or month > 12:
             raise ValueError("Invalid month")
     except (TypeError, ValueError):
         messages.error(request, "Dữ liệu tháng/năm không hợp lệ.")
         return redirect("calculate_payroll")
     ```

Priority B — Nên làm sớm (2–8 giờ) 3. File upload: generate safe unique filenames and use Django storage:

- Use `default_storage.save()` with `get_valid_filename()` and a hash/timestamp:
  ```py
  from django.utils.text import get_valid_filename
  import uuid
  filename = get_valid_filename(f"{uuid.uuid4().hex}_{uploaded.name}")
  path = default_storage.save(f"resumes/{filename}", uploaded)
  ```
- Optionally move to S3 (django-storages) in prod.

4. Normalize AJAX CSRF:
   - Add small JS in base template:
     ```js
     function getCookie(name) {
       // read cookie...
     }
     $.ajaxSetup({
       headers: { "X-CSRFToken": getCookie("csrftoken") },
     });
     ```
   - Or use fetch wrapper to include header.

Priority C — Medium/Architectural (1–3 days) 5. Role-based permissions:

- Use `user_passes_test` or `@permission_required('app.change_payroll')` or Django groups. Add decorator for sensitive views.

6. Add tests:

   - Add Django testcases for:
     - Login redirect behavior
     - POST-only endpoints return 405 on GET
     - Payroll delete/confirm permission + behavior
     - Resume upload with invalid file type (unit tests)
   - Use fixtures or factories (factory_boy).

7. Add CI & pre-commit:
   - GitHub Actions: run flake8/ruff, black, pytest.
   - pre-commit hooks: black, isort, ruff.

Priority D — Longer term improvements 8. Async AI scoring using Celery + Redis or background worker. 9. Audit trail DB model (AuditLog) for sensitive ops. 10. Dockerfile & production deployment docs; configure HTTPS, CORS, security headers.

---

## 5) Concrete checklist (short-term roadmap, prioritized)

Immediate (this session — I can apply these now if bạn đồng ý)

- [ ] Add `'encoding': 'utf-8'` to file logging handler (fix Unicode log errors).
- [ ] Add safe parsing and validation for `month`/`year` in payroll views.
- [ ] Add unique filename logic for resume/avatar save.

Short-term (1–3 days)

- [ ] Centralize AJAX CSRF helper + update JS templates.
- [ ] Add unit tests for payroll delete/confirm and upload/resume.
- [ ] Ensure `.env` never committed and add README for env vars.

Medium-term (1–2 weeks)

- [ ] Introduce role-based permission checks.
- [ ] Add CI (GitHub Actions) and pre-commit hooks.
- [ ] Move heavy AI scoring to async worker, add caching.

Long-term (optional)

- [ ] S3 for media + signed URLs for downloads.
- [ ] Audit logging DB, rate-limiting, monitoring.

---

## 6) Minimal tests to add first (file names + description)

- tests/test_auth.py
  - test_login_redirects, test_login_success
- tests/test_payroll.py
  - test_get_payroll_data_requires_post, test_save_payroll_invalid_month
- tests/test_uploads.py
  - test_resume_upload_blocked_extension, test_avatar_too_large

---

## 7) Quick wins I can implement now (choose any, I will apply immediately)

- Fix logging encoding in settings.py.
- Add safe parsing & validation to `save_payroll` to avoid ValueError.
- Replace raw FileSystemStorage save with unique filename using `default_storage` for resumes/avatars.
- Add small JS snippet to base_template.html to set CSRF header for AJAX.

Say which of the immediate fixes you want me to apply now (I recommend the first two). If you want all four immediate fixes, I’ll apply them in one patch and run `manage.py check` + a quick run to validate.

---

## 8) Notes / mentoring tips

- Work in small PRs: each of above fixes should be a single commit with tests.
- Keep changes backward-compatible; add deprecation notes if you change public APIs.
- For production, use environment-specific settings (separate settings module), and enable secure cookies/HTTPS options.
- Keep AI API keys out of repo; restrict access and monitor usage.

---

Bạn muốn tôi bắt tay làm ngay:
A) Thêm encoding=utf-8 vào logger + vá `save_payroll` parsing (khuyến nghị),  
B) Thêm cả unique filename lưu file + CSRF JS, hoặc  
C) Chỉ tạo PR danh sách các tests/CI (không sửa code) — chọn A/B/C?

Nếu chọn A hoặc B tôi sẽ apply thay đổi, chạy quick checks và report kết quả.
