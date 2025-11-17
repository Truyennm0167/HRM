# AJAX API Documentation - Manager Approval System

## Overview

This document describes the AJAX API endpoints for the manager approval system. All endpoints require authentication and manager permissions.

---

## Authentication

All requests must include:

- **Django Session Cookie** (automatic if logged in)
- **CSRF Token** in `X-CSRFToken` header

---

## Leave Approval Endpoints

### 1. Approve Leave Request

**Endpoint:** `POST /portal/team/leaves/<leave_id>/approve/`

**Description:** Approve a pending leave request from a team member.

**Permissions Required:**

- User must be logged in
- User must have manager permissions
- Leave request must be from same department

**Request:**

```javascript
POST /portal/team/leaves/123/approve/
Headers:
  Content-Type: application/json
  X-CSRFToken: <csrf_token>
Body: (empty)
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Đã phê duyệt đơn nghỉ phép thành công",
  "leave": {
    "id": 123,
    "employee_name": "Nguyễn Văn A",
    "leave_type": "Phép năm",
    "start_date": "20/11/2025",
    "end_date": "22/11/2025",
    "total_days": 3,
    "status": "approved",
    "approved_by": "Trần Thị B",
    "approved_at": "17/11/2025 14:30"
  }
}
```

**Error Responses:**

_400 - Already Processed:_

```json
{
  "success": false,
  "message": "Đơn nghỉ phép này đã được xử lý trước đó"
}
```

_405 - Method Not Allowed:_

```json
{
  "success": false,
  "message": "Method not allowed"
}
```

_500 - Server Error:_

```json
{
  "success": false,
  "message": "Lỗi: <error_details>"
}
```

**Notes:**

- Uses `approve_leave_request()` helper function
- Automatically updates leave balance
- Balance is NOT deducted again (already deducted on creation)

---

### 2. Reject Leave Request

**Endpoint:** `POST /portal/team/leaves/<leave_id>/reject/`

**Description:** Reject a pending leave request with a reason.

**Permissions Required:**

- User must be logged in
- User must have manager permissions
- Leave request must be from same department

**Request:**

```javascript
POST /portal/team/leaves/123/reject/
Headers:
  Content-Type: application/json
  X-CSRFToken: <csrf_token>
Body:
{
  "reason": "Thời điểm này đang bận, vui lòng chọn ngày khác"
}
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Đã từ chối đơn nghỉ phép và hoàn lại số ngày nghỉ",
  "leave": {
    "id": 123,
    "employee_name": "Nguyễn Văn A",
    "leave_type": "Phép năm",
    "status": "rejected",
    "rejection_reason": "Thời điểm này đang bận, vui lòng chọn ngày khác",
    "approved_by": "Trần Thị B",
    "approved_at": "17/11/2025 14:35"
  }
}
```

**Error Responses:**

_400 - Missing Reason:_

```json
{
  "success": false,
  "message": "Vui lòng nhập lý do từ chối"
}
```

_400 - Invalid JSON:_

```json
{
  "success": false,
  "message": "Invalid JSON data"
}
```

**Notes:**

- Uses `reject_leave_request()` helper function
- Automatically restores leave balance
- Rejection reason is required

---

## Expense Approval Endpoints

### 3. Approve Expense Request

**Endpoint:** `POST /portal/team/expenses/<expense_id>/approve/`

**Description:** Approve a pending expense reimbursement request.

**Permissions Required:**

- User must be logged in
- User must have manager permissions
- Expense must be from same department

**Request:**

```javascript
POST /portal/team/expenses/456/approve/
Headers:
  Content-Type: application/json
  X-CSRFToken: <csrf_token>
Body: (empty)
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Đã phê duyệt đơn hoàn tiền thành công",
  "expense": {
    "id": 456,
    "employee_name": "Nguyễn Văn A",
    "category": "Di chuyển",
    "amount": 500000,
    "amount_formatted": "500,000 VNĐ",
    "date": "15/11/2025",
    "description": "Taxi đi họp khách hàng",
    "status": "approved",
    "approved_by": "Trần Thị B",
    "approved_at": "17/11/2025 14:40"
  }
}
```

**Error Responses:**

_400 - Already Processed:_

```json
{
  "success": false,
  "message": "Đơn này không ở trạng thái chờ duyệt"
}
```

**Notes:**

- Updates status to 'approved'
- Does not automatically pay (requires separate payment process)
- After approval, accountant can mark as 'paid'

---

### 4. Reject Expense Request

**Endpoint:** `POST /portal/team/expenses/<expense_id>/reject/`

**Description:** Reject a pending expense request with a reason.

**Permissions Required:**

- User must be logged in
- User must have manager permissions
- Expense must be from same department

**Request:**

```javascript
POST /portal/team/expenses/456/reject/
Headers:
  Content-Type: application/json
  X-CSRFToken: <csrf_token>
Body:
{
  "reason": "Không có hóa đơn hợp lệ, vui lòng đính kèm hóa đơn"
}
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Đã từ chối đơn hoàn tiền",
  "expense": {
    "id": 456,
    "employee_name": "Nguyễn Văn A",
    "category": "Di chuyển",
    "status": "rejected",
    "rejection_reason": "Không có hóa đơn hợp lệ, vui lòng đính kèm hóa đơn",
    "approved_by": "Trần Thị B",
    "approved_at": "17/11/2025 14:45"
  }
}
```

**Error Responses:**

_400 - Missing Reason:_

```json
{
  "success": false,
  "message": "Vui lòng nhập lý do từ chối"
}
```

---

## Error Handling

### Common Error Codes

| Status Code | Meaning                                      |
| ----------- | -------------------------------------------- |
| 200         | Success                                      |
| 400         | Bad Request (missing data, validation error) |
| 403         | Forbidden (no permission)                    |
| 404         | Not Found (invalid ID)                       |
| 405         | Method Not Allowed (must use POST)           |
| 500         | Internal Server Error                        |

### Error Response Format

All errors follow this format:

```json
{
  "success": false,
  "message": "Error description in Vietnamese"
}
```

---

## Frontend Integration Examples

### Using Fetch API

```javascript
// Get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie("csrftoken");

// Approve leave
fetch("/portal/team/leaves/123/approve/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-CSRFToken": csrftoken,
  },
})
  .then((response) => response.json())
  .then((data) => {
    if (data.success) {
      alert(data.message);
      location.reload();
    } else {
      alert(data.message);
    }
  });

// Reject expense with reason
fetch("/portal/team/expenses/456/reject/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-CSRFToken": csrftoken,
  },
  body: JSON.stringify({
    reason: "Missing receipt",
  }),
})
  .then((response) => response.json())
  .then((data) => {
    if (data.success) {
      alert(data.message);
    }
  });
```

### Using jQuery

```javascript
// Approve leave
$.ajax({
  url: "/portal/team/leaves/123/approve/",
  type: "POST",
  headers: {
    "X-CSRFToken": csrftoken,
  },
  success: function (data) {
    if (data.success) {
      alert(data.message);
      location.reload();
    }
  },
  error: function (xhr) {
    var data = xhr.responseJSON;
    alert(data.message);
  },
});

// Reject leave
$.ajax({
  url: "/portal/team/leaves/123/reject/",
  type: "POST",
  headers: {
    "X-CSRFToken": csrftoken,
  },
  contentType: "application/json",
  data: JSON.stringify({
    reason: "Time conflict with project deadline",
  }),
  success: function (data) {
    alert(data.message);
  },
});
```

---

## Testing with cURL

### Approve Leave

```bash
curl -X POST http://localhost:8000/portal/team/leaves/123/approve/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <your_csrf_token>" \
  -H "Cookie: sessionid=<your_session_id>"
```

### Reject Leave

```bash
curl -X POST http://localhost:8000/portal/team/leaves/123/reject/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <your_csrf_token>" \
  -H "Cookie: sessionid=<your_session_id>" \
  -d '{"reason": "Not enough staff coverage"}'
```

### Approve Expense

```bash
curl -X POST http://localhost:8000/portal/team/expenses/456/approve/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <your_csrf_token>" \
  -H "Cookie: sessionid=<your_session_id>"
```

### Reject Expense

```bash
curl -X POST http://localhost:8000/portal/team/expenses/456/reject/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <your_csrf_token>" \
  -H "Cookie: sessionid=<your_session_id>" \
  -d '{"reason": "Receipt required"}'
```

---

## Security Considerations

1. **CSRF Protection**: All POST requests require valid CSRF token
2. **Authentication**: User must be logged in (checked by `@login_required`)
3. **Authorization**: Manager permission checked by `@require_manager_permission`
4. **Department Isolation**: Managers can only approve requests from their own department
5. **Status Validation**: Prevents double-approval of already processed requests
6. **Input Validation**: Rejection reason is required and validated

---

## Business Logic

### Leave Approval Flow

1. Manager approves → `approve_leave_request()` called
2. Checks status is 'pending'
3. Sets status='approved', approved_by, approved_at
4. Leave balance already updated on creation (no double deduction)
5. Returns success with leave details

### Leave Rejection Flow

1. Manager rejects with reason → `reject_leave_request()` called
2. Checks status is 'pending'
3. Sets status='rejected', rejection_reason
4. Restores leave balance (subtracts used_days)
5. Returns success with rejection details

### Expense Approval Flow

1. Manager approves → Status set to 'approved'
2. Records approved_by and approved_at
3. Expense awaits payment by accountant
4. Returns success with expense details

### Expense Rejection Flow

1. Manager rejects with reason
2. Sets status='rejected', rejection_reason
3. Records who rejected and when
4. Employee can view rejection reason
5. Returns success with rejection details

---

## Change Log

**Version 1.0 (November 17, 2025)**

- Initial implementation of 4 AJAX endpoints
- Leave approval/rejection using helper functions
- Expense approval/rejection with reason tracking
- JSON response format standardized
- Error handling implemented
- Documentation completed
