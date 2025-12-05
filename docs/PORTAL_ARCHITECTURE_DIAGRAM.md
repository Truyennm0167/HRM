# 🏗️ Portal System Architecture Diagram

## 📊 System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HRM PORTAL SYSTEM                           │
│                     http://localhost:8000/                          │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴──────────────┐
                    │    MIDDLEWARE STACK        │
                    │  (Request Processing)      │
                    └─────────────┬──────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   PUBLIC     │         │   PORTAL     │         │  MANAGEMENT  │
│   /careers/  │         │   /portal/   │         │ /management/ │
│              │         │              │         │              │
│ 3 URLs       │         │ 31 URLs      │         │ 100+ URLs    │
│ No Auth      │         │ Employee     │         │ Staff Only   │
└──────────────┘         └──────────────┘         └──────────────┘
```

---

## 🔄 Request Flow

```
┌─────────┐
│ Browser │
└────┬────┘
     │ HTTP Request
     ▼
┌──────────────────────────────────────┐
│  Django Middleware Stack             │
├──────────────────────────────────────┤
│ 1. SecurityMiddleware                │
│ 2. SessionMiddleware                 │
│ 3. CommonMiddleware                  │
│ 4. AuthenticationMiddleware          │
├──────────────────────────────────────┤
│ 5. PortalRedirectMiddleware     ✨   │  ← Auto redirect to /portal/
│ 6. ManagementAccessMiddleware  ✨   │  ← Block /management/ non-staff
│ 7. PortalSwitchMiddleware      ✨   │  ← Handle portal switching
├──────────────────────────────────────┤
│ 8. MessageMiddleware                 │
│ 9. ClickjackingMiddleware            │
└──────────────┬───────────────────────┘
               │
               ▼
      ┌────────────────┐
      │  URL Routing   │
      │   (hrm/urls)   │
      └────────┬───────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Career  │ │Portal  │ │Mgmt    │
│URLs    │ │URLs    │ │URLs    │
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Career  │ │Portal  │ │Mgmt    │
│Views   │ │Views   │ │Views   │
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    └──────────┼──────────┘
               ▼
       ┌───────────────┐
       │   Templates   │
       └───────┬───────┘
               │
               ▼
       ┌───────────────┐
       │   Response    │
       └───────┬───────┘
               │
               ▼
           Browser
```

---

## 🧩 Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PORTAL COMPONENTS                           │
└─────────────────────────────────────────────────────────────────┘

┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   VIEWS       │───▶│  PERMISSIONS  │───▶│   MODELS      │
│               │    │               │    │               │
│ portal_views  │    │ Helper funcs  │    │ Employee      │
│ - dashboard   │    │ - get_employee│    │ Leave         │
│ - leaves      │    │ - is_manager  │    │ Attendance    │
│ - payroll     │    │ - can_access  │    │ Payroll       │
│ - attendance  │    │               │    │ Expense       │
│ - expenses    │    │ Decorators    │    │               │
│ - profile     │    │ @require_mgr  │    │               │
│ - approvals   │    │               │    │               │
└───────┬───────┘    └───────────────┘    └───────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────┐
│                  TEMPLATES                            │
├───────────────────────────────────────────────────────┤
│  portal_base.html  (Base layout)                      │
│  ├── dashboard.html                                   │
│  ├── leaves/                                          │
│  │   ├── list.html                                    │
│  │   ├── create.html                                  │
│  │   └── detail.html                                  │
│  ├── payroll/                                         │
│  │   ├── list.html                                    │
│  │   └── detail.html                                  │
│  ├── attendance/                                      │
│  │   └── list.html                                    │
│  ├── expenses/                                        │
│  │   ├── list.html                                    │
│  │   ├── create.html                                  │
│  │   └── detail.html                                  │
│  ├── profile/                                         │
│  │   └── view.html                                    │
│  └── approvals/                                       │
│      ├── dashboard.html                               │
│      ├── team_leaves.html                             │
│      └── team_expenses.html                           │
└───────────────────────────────────────────────────────┘
```

---

## 🔐 Permission Flow

```
┌──────────────┐
│ User Login   │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────┐
│ PortalRedirectMiddleware    │
├─────────────────────────────┤
│ If authenticated:           │
│   - Check if URL is bypass  │
│   - If not → /portal/       │
└─────────────┬───────────────┘
              │
              ▼
     ┌────────────────┐
     │ Request URL?   │
     └────┬───────────┘
          │
    ┌─────┼──────────┐
    │     │          │
    ▼     ▼          ▼
/portal/ /mgmt/   /careers/
    │     │          │
    │     │          └─── Public (No auth)
    │     │
    │     ▼
    │  ┌──────────────────────────┐
    │  │ManagementAccessMiddleware│
    │  ├──────────────────────────┤
    │  │ If not staff:            │
    │  │   → Redirect /portal/    │
    │  │   + Error message        │
    │  └──────────────────────────┘
    │
    ▼
┌────────────────────────┐
│ Portal Views           │
├────────────────────────┤
│ Check permissions:     │
│ - get_user_employee()  │
│ - user_is_manager()    │
│                        │
│ Render template with:  │
│ - Permission filters   │
│ - Dynamic menu         │
└────────────────────────┘
```

---

## 📋 URL Namespace Structure

```
Root URL: /
│
├── /admin/                    (Django Admin)
│
├── /careers/                  (Public Recruitment)
│   ├── /careers/jobs/
│   ├── /careers/apply/<id>/
│   └── /careers/status/<id>/
│
├── /portal/                   (Employee Self-Service) ✨
│   ├── /portal/                       → Dashboard
│   ├── /portal/leaves/                → Leave list
│   │   ├── /create/                   → Create leave
│   │   ├── /<id>/                     → Leave detail
│   │   └── /<id>/cancel/              → Cancel (AJAX)
│   ├── /portal/payroll/               → Payroll list
│   │   ├── /<id>/                     → Payroll detail
│   │   └── /<id>/download/            → Download PDF
│   ├── /portal/attendance/            → Attendance list
│   │   └── /calendar/                 → Calendar view
│   ├── /portal/expenses/              → Expense list
│   │   ├── /create/                   → Create expense
│   │   ├── /<id>/                     → Expense detail
│   │   └── /<id>/cancel/              → Cancel (AJAX)
│   ├── /portal/profile/               → Profile view
│   │   ├── /edit/                     → Edit profile
│   │   └── /password/                 → Change password
│   ├── /portal/approvals/             → Approvals dashboard
│   └── /portal/team/                  → Manager features
│       ├── /leaves/                   → Team leaves
│       │   ├── /<id>/approve/         → Approve (AJAX)
│       │   └── /<id>/reject/          → Reject (AJAX)
│       ├── /expenses/                 → Team expenses
│       │   ├── /<id>/approve/         → Approve (AJAX)
│       │   └── /<id>/reject/          → Reject (AJAX)
│       └── /reports/                  → Team reports
│
└── /management/               (Admin/HR Management) 👔
    ├── /management/                   → Admin home
    ├── /management/contracts/         → Contracts
    ├── /management/employees/         → Employees
    ├── /management/departments/       → Departments
    ├── /management/leave/requests/    → Leave requests
    └── ... (100+ more URLs)

Total: 150+ URLs
```

---

## 🎨 UI Component Tree

```
portal_base.html (Base Layout)
│
├── <head>
│   ├── CSS: AdminLTE 3, Bootstrap 4, DataTables, SweetAlert2
│   └── Fonts: Font Awesome 5, Google Fonts
│
├── <body class="hold-transition sidebar-mini">
│   │
│   ├── Navbar (Top)
│   │   ├── Hamburger toggle
│   │   ├── Portal Switch button (staff only)
│   │   └── User dropdown
│   │       ├── Profile
│   │       ├── Settings
│   │       └── Logout
│   │
│   ├── Sidebar (Left)
│   │   ├── Brand logo
│   │   ├── User panel (avatar + name)
│   │   └── Navigation menu
│   │       ├── 📊 Dashboard
│   │       ├── 🏖️  Nghỉ phép
│   │       ├── 💰 Bảng lương
│   │       ├── ⏰ Chấm công
│   │       ├── 💳 Chi phí
│   │       ├── 👤 Hồ sơ
│   │       └── ✅ Duyệt đơn (manager)
│   │
│   └── Content wrapper (Main)
│       ├── Breadcrumb
│       ├── {% block content %}
│       │   │
│       │   ├── Stats cards (Small Box)
│       │   ├── Filter buttons
│       │   ├── DataTable
│       │   └── Action buttons
│       │
│       └── Footer
│
└── <script>
    ├── jQuery, Bootstrap, AdminLTE
    ├── DataTables, SweetAlert2
    └── Custom AJAX functions
```

---

## 🔄 Data Flow Example: Leave Request

```
1. USER CLICKS "Tạo đơn nghỉ phép"
   │
   ▼
2. Browser → GET /portal/leaves/create/
   │
   ▼
3. Middleware Stack
   ├── Check authentication ✓
   ├── Check if redirect needed ✗
   └── Check management access N/A
   │
   ▼
4. URL Routing: urls_portal.py
   path('leaves/create/', portal_views.leave_create, name='portal_leave_create')
   │
   ▼
5. View: portal_views.leave_create()
   ├── @login_required decorator
   ├── Get employee = get_user_employee(request.user)
   ├── Get leave types, leave balance
   └── Render template
   │
   ▼
6. Template: portal/leaves/create.html
   ├── Extends portal_base.html
   ├── Display form with date pickers
   └── JavaScript: Calculate total days
   │
   ▼
7. USER FILLS FORM & SUBMITS
   │
   ▼
8. Browser → POST /portal/leaves/create/
   │
   ▼
9. View: portal_views.leave_create() (POST)
   ├── Validate form data
   ├── Check leave balance
   ├── Create Leave object
   ├── Save to database
   └── Redirect to /portal/leaves/
   │
   ▼
10. Show success message
    "Đơn nghỉ phép đã được gửi thành công!"
```

---

## 🧪 Testing Architecture

```
┌─────────────────────────────────────────┐
│         TESTING LAYERS                  │
└─────────────────────────────────────────┘

Layer 1: URL Pattern Testing
├── check_urls.py
│   ├── List all URL patterns
│   ├── Verify URL names
│   └── Check namespace conflicts
│
Layer 2: Middleware Testing
├── Test PortalRedirectMiddleware
│   ├── Authenticated → /portal/
│   └── Bypass URLs work
├── Test ManagementAccessMiddleware
│   ├── Staff access allowed
│   └── Non-staff blocked
└── Test PortalSwitchMiddleware
    ├── Valid switch_to parameter
    └── Permission checks

Layer 3: Permission Testing
├── Test helper functions
│   ├── get_user_employee()
│   ├── user_is_manager()
│   └── user_can_access_management()
└── Test template filters
    ├── {{ user|can_access_management }}
    └── {{ user|is_manager }}

Layer 4: View Testing
├── Test portal views
│   ├── Dashboard loads
│   ├── Lists display data
│   ├── Detail pages work
│   └── AJAX endpoints respond
└── Test management views
    ├── Admin home loads
    └── Backward URLs work

Layer 5: Integration Testing
├── User workflows
│   ├── Login → Portal → Logout
│   ├── Create leave → View → Cancel
│   └── Manager approve/reject
└── Permission scenarios
    ├── Employee access portal only
    ├── Manager access approvals
    └── Admin access all
```

---

## 📊 Database Schema (Portal-related)

```
┌─────────────────┐
│     Users       │
│  (Django Auth)  │
└────────┬────────┘
         │ 1:1
         ▼
┌─────────────────┐         ┌──────────────────┐
│   Employee      │────────▶│   Department     │
├─────────────────┤ N:1     └──────────────────┘
│ - admin (FK)    │
│ - employee_code │         ┌──────────────────┐
│ - is_manager    │────────▶│   JobTitle       │
│ - manager (FK)  │ N:1     └──────────────────┘
│ - avatar        │
└────────┬────────┘
         │
    ┌────┼────┬────┬────┐
    │    │    │    │    │
    ▼    ▼    ▼    ▼    ▼
┌───────┐ ┌──────┐ ┌─────┐ ┌───────┐ ┌────────┐
│ Leave │ │Attend│ │Payrl│ │Expense│ │Apprais│
│       │ │ance  │ │     │ │       │ │   al  │
├───────┤ ├──────┤ ├─────┤ ├───────┤ ├────────┤
│emp(FK)│ │emp FK│ │emp  │ │emp FK │ │emp FK  │
│type   │ │date  │ │month│ │amount │ │period  │
│start  │ │in/out│ │base │ │type   │ │rating  │
│end    │ │hours │ │bonus│ │receipt│ │status  │
│status │ │status│ │net  │ │status │ │        │
└───────┘ └──────┘ └─────┘ └───────┘ └────────┘
```

---

## 🚀 Deployment Flow

```
Development          Staging            Production
    │                   │                   │
    ▼                   ▼                   ▼
┌─────────┐       ┌─────────┐       ┌─────────┐
│ SQLite  │       │ SQLite  │       │PostgreSQL│
│ Debug=T │       │ Debug=T │       │ Debug=F │
│ localhost│       │ test.hrm│       │ hrm.com │
└────┬────┘       └────┬────┘       └────┬────┘
     │                 │                  │
     │  git push       │  git pull        │
     ├────────────────▶│  python manage   │
     │                 │  .py migrate     │
     │                 │  collectstatic   │
     │                 │                  │
     │                 │  Deploy          │
     │                 ├─────────────────▶│
     │                 │                  │
     │                 │  ✅ Test         │
     │                 │  ✅ Verify       │
     │                 │                  │
     ▼                 ▼                  ▼
  Develop          Test users         Go Live
```

---

_Generated on November 17, 2025_
