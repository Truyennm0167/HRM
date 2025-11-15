# Contract Management Module - Complete Guide

## Overview

The Contract Management module provides comprehensive functionality for managing employment contracts throughout their lifecycle. Features include contract creation, editing, renewal, termination, and tracking with expiration alerts.

## Module Structure

### 1. Model (`app/models.py` - Contract)

#### Contract Model

**Purpose**: Represent employment contracts with full lifecycle management

**Key Fields**:

- **Basic Info**: contract_number, employee (FK), contract_type, status
- **Dates**: start_date, end_date, signed_date, termination_date
- **Financial**: salary, salary_coefficient, allowances
- **Job Details**: job_title (FK), job_description, workplace, working_hours
- **Terms**: terms, benefits, insurance_info, notes
- **Tracking**: created_by (FK), created_at, updated_at
- **Renewal**: renewed_from (self FK) - tracks renewal chain
- **File**: contract_file (uploaded PDF/DOC)

**Contract Types**:

1. `probation` - Hợp đồng thử việc
2. `definite` - Hợp đồng xác định thời hạn
3. `indefinite` - Hợp đồng không xác định thời hạn
4. `seasonal` - Hợp đồng theo mùa vụ
5. `project` - Hợp đồng theo dự án

**Status Types**:

1. `draft` - Nháp (can edit/delete)
2. `active` - Đang hiệu lực (can edit/renew/terminate)
3. `expired` - Hết hạn (read-only)
4. `terminated` - Đã chấm dứt (read-only)
5. `renewed` - Đã gia hạn (read-only, has successor contract)

**Helper Methods**:

- `is_active()` - Check if contract is currently valid
- `days_until_expiration()` - Calculate days remaining
- `is_expiring_soon(days=30)` - Check if expiring within N days
- `can_be_renewed()` - Check if renewal is allowed
- `can_be_terminated()` - Check if termination is allowed

---

### 2. Form (`app/forms.py` - ContractForm)

#### ContractForm

**Purpose**: Validate and process contract data with comprehensive validation

**Fields** (19 fields):

- contract_number, employee, contract_type
- start_date, end_date, signed_date
- salary, salary_coefficient, allowances
- job_title, job_description, workplace, working_hours
- terms, benefits, insurance_info, notes
- contract_file, status

**Validation Rules**:

1. **Date Validation**:

   - Start date cannot be before signed date
   - End date must be after start date
   - Indefinite contracts should not have end date
   - Definite contracts must have end date

2. **Financial Validation**:

   - Salary must be > 0
   - Coefficient and allowances >= 0

3. **Uniqueness**:
   - Contract number must be unique (checked for new/edit)

**Widgets**:

- Date inputs: HTML5 date picker
- Number inputs: Step validation (100,000 for salary)
- Text areas: Rich text for descriptions
- File input: Accept PDF/DOC only

---

### 3. Views (`app/HodViews.py`)

#### `list_contracts(request)`

**Purpose**: Display all contracts with filtering and search

**Features**:

- **Statistics**: Total, active, expiring contracts
- **Filters**:
  - Status (draft/active/expired/terminated/renewed)
  - Contract type (probation/definite/indefinite/etc.)
  - Department
  - Search (employee name, code, contract number)
  - Expiring soon (within 30 days)
- **Pagination**: 15 contracts per page
- **Display**: Table with key info and action buttons

**Context Data**:

- contracts (paginated queryset)
- departments (for filter dropdown)
- Statistics (total, active, expiring counts)
- Filter parameters (for preserving state)
- Choice lists (for dropdowns)

**URL**: `/contracts/`

---

#### `contract_detail(request, contract_id)`

**Purpose**: Display full contract details with action buttons

**Features**:

- Full contract information display
- Expiration alerts (if within 30 days)
- Action buttons based on status:
  - Edit (draft/active)
  - Renew (active, if eligible)
  - Terminate (active)
  - Delete (draft only)
  - Download file (if uploaded)
- Renewal history:
  - Show original contract (if renewed from)
  - Show successor contracts (if renewed to)
- Metadata (creator, dates)

**Layout**: 2-column responsive

- **Left**: Basic info, employee info, financial info
- **Right**: Job info, terms, termination info (if any), metadata

**URL**: `/contracts/<id>/`

---

#### `create_contract(request)`

**Purpose**: Create new employment contract

**Features**:

- Full form with all contract fields
- Auto-set created_by to current user
- File upload support
- Comprehensive validation
- Success redirect to detail page

**Form Behavior**:

- GET: Display empty form
- POST: Validate and save, redirect to detail

**URL**: `/contracts/create/`

---

#### `edit_contract(request, contract_id)`

**Purpose**: Edit existing contract

**Restrictions**:

- Only draft or active contracts can be edited
- Expired/terminated/renewed contracts are read-only

**Features**:

- Pre-filled form with current values
- Same validation as create
- File replacement support
- Success redirect to detail page

**URL**: `/contracts/<id>/edit/`

---

#### `renew_contract(request, contract_id)`

**Purpose**: Create new contract as renewal of existing one

**Process**:

1. Check if old contract can be renewed
2. Pre-fill form with old contract data
3. Adjust start date to day after old end date
4. Create new contract with `renewed_from` reference
5. Update old contract status to 'renewed'
6. Redirect to new contract detail

**Features**:

- Maintains continuity (dates, terms, salary)
- Allows modifications before saving
- Links renewal chain (old → new)
- Auto-updates old contract status

**Pre-filled Data**:

- employee, contract_type, job details
- salary, coefficient, allowances
- terms, benefits, insurance info
- start_date = old_end_date + 1 day

**URL**: `/contracts/<id>/renew/`

---

#### `terminate_contract(request, contract_id)`

**Purpose**: Terminate active contract before end date

**Restrictions**:

- Only active contracts can be terminated

**Required Input**:

- Termination date (date picker)
- Termination reason (textarea, required)

**Process**:

1. Validate contract can be terminated
2. Collect termination info via modal
3. Update contract status to 'terminated'
4. Save termination date and reason
5. Redirect back to detail page

**URL**: `/contracts/<id>/terminate/` (POST only)

---

#### `delete_contract(request, contract_id)`

**Purpose**: Permanently delete draft contract

**Restrictions**:

- Only draft contracts can be deleted
- Active/expired/terminated/renewed contracts cannot be deleted

**Process**:

1. Check status is 'draft'
2. Confirm via modal
3. Delete contract record
4. Redirect to contract list

**URL**: `/contracts/<id>/delete/` (POST only)

---

### 4. Templates

#### `list_contracts.html`

**Components**:

1. **Statistics Row** (3 small-boxes):

   - Total contracts (blue)
   - Active contracts (green)
   - Expiring contracts (yellow, clickable)

2. **Filter Card**:

   - Search input (name/code/contract number)
   - Status dropdown
   - Contract type dropdown
   - Department dropdown
   - Filter/Clear buttons

3. **Contracts Table**:

   - Columns: STT, Số HĐ, Nhân viên, Phòng ban, Loại HĐ, Ngày bắt đầu, Ngày kết thúc, Trạng thái, Thao tác
   - Status badges (colored by status)
   - Expiring warning badge
   - Action buttons (view/edit)

4. **Pagination**:
   - Page numbers with filter preservation
   - First/Previous/Next/Last buttons

**Features**:

- Collapsible filter section
- "Tạo hợp đồng mới" button (top-right)
- Empty state message
- Responsive table

---

#### `contract_detail.html`

**Components**:

1. **Action Buttons Bar**:

   - Quay lại (back to list)
   - Sửa hợp đồng (if editable)
   - Gia hạn hợp đồng (if renewable)
   - Chấm dứt hợp đồng (if active)
   - Xóa hợp đồng (if draft)
   - Tải file HĐ (if file exists)

2. **Expiration Alert** (if expiring soon):

   - Warning banner with days remaining
   - Recommendation to renew or terminate

3. **Information Cards** (2-column layout):

   - **Left Column**:

     - Basic Information (primary card)
     - Employee Information (info card)
     - Financial Information (success card)

   - **Right Column**:
     - Job Information (warning card)
     - Terms & Conditions (default card)
     - Termination Info (danger card, if terminated)
     - Metadata (default card)

4. **Renewal History** (if applicable):

   - Original contract link (if renewed from)
   - Successor contracts list (if renewed to)

5. **Modals**:
   - Terminate Contract Modal (form with date + reason)
   - Delete Contract Modal (confirmation)

**Features**:

- Color-coded status badges
- Formatted currency (VNĐ)
- Date formatting (d/m/Y)
- File download links
- Responsive 2-column → 1-column on mobile

---

#### `create_edit_contract.html`

**Layout**: Single form with 2-column field arrangement

**Components**:

1. **Renewal Alert** (if action='renew'):

   - Info box showing old contract details

2. **Left Column Cards**:

   - Basic Information (contract number, employee, type, status, file)
   - Dates (signed, start, end)
   - Financial (salary, coefficient, allowances)

3. **Right Column Cards**:

   - Job Information (job title, description, workplace, working hours)
   - Terms & Conditions (terms, benefits, insurance, notes)

4. **Error Display**:

   - Field-level errors (below each field)
   - Non-field errors (alert box at bottom)

5. **Action Buttons**:
   - Submit (Tạo/Cập nhật/Gia hạn based on action)
   - Hủy (cancel, back to list/detail)
   - Xem HĐ cũ (if action='renew')

**JavaScript Features**:

- Auto-disable end_date for indefinite contracts
- Dynamic help text based on contract type
- Form validation hints

**Form Attributes**:

- `enctype="multipart/form-data"` (for file upload)
- CSRF token
- Method: POST

---

### 5. URLs (`hrm/urls.py`)

```python
# Contract Management URLs
path('contracts/', list_contracts, name='list_contracts'),
path('contracts/create/', create_contract, name='create_contract'),
path('contracts/<int:contract_id>/', contract_detail, name='contract_detail'),
path('contracts/<int:contract_id>/edit/', edit_contract, name='edit_contract'),
path('contracts/<int:contract_id>/renew/', renew_contract, name='renew_contract'),
path('contracts/<int:contract_id>/terminate/', terminate_contract, name='terminate_contract'),
path('contracts/<int:contract_id>/delete/', delete_contract, name='delete_contract'),
```

**URL Pattern**: RESTful-style with resource-based routing

---

### 6. Sidebar Navigation

**Menu Location**: Between "Portal Nhân Viên" and "Khen thưởng - Kỷ luật"

**Menu Structure**:

```
Quản lý hợp đồng (fas fa-file-contract)
├── Danh sách hợp đồng (fas fa-list)
└── Tạo hợp đồng mới (fas fa-plus-circle)
```

**Active State**: Highlights when `/contracts` in URL path

---

## Business Logic

### Contract Lifecycle

```
Draft → Active → Expired/Terminated/Renewed
```

**State Transitions**:

1. **Draft** → **Active**: Admin activates contract (manual status change)
2. **Active** → **Expired**: End date passes (manual or automated)
3. **Active** → **Terminated**: Early termination by admin
4. **Active** → **Renewed**: Renewal creates new contract

**State Rules**:

- Draft: Can edit all fields, can delete
- Active: Can edit some fields, can renew, can terminate
- Expired: Read-only
- Terminated: Read-only
- Renewed: Read-only, links to successor

---

### Renewal Chain

**Example**:

```
Contract A (2023-01-01 to 2023-12-31, status=renewed)
    └─> Contract B (2024-01-01 to 2024-12-31, status=active, renewed_from=A)
```

**Features**:

- Maintains employment continuity
- Preserves contract history
- Tracks succession linearly

**Implementation**:

- `renewed_from` field (self FK)
- Old contract status changed to 'renewed'
- New contract links back to old via `renewed_from`

---

### Expiration Alerts

**Threshold**: 30 days before end_date

**Alert Locations**:

1. Contract detail page (yellow alert banner)
2. List page (yellow badge on expiring row)
3. Statistics box (expiring count)
4. Filter (show only expiring)

**Alert Message**: "Hợp đồng này sẽ hết hạn sau X ngày (DD/MM/YYYY)"

---

## Usage Guide

### For HR Administrators

#### 1. Creating a New Contract

1. Navigate to **Quản lý hợp đồng** → **Tạo hợp đồng mới**
2. Fill in all required fields (\* marked)
3. Select contract type:
   - If indefinite: Leave end date empty
   - If definite: Set end date
4. Enter financial details (salary, coefficient, allowances)
5. Fill in job description and workplace
6. Enter contract terms and benefits
7. Upload contract file (PDF/DOC) - optional
8. Set status (usually 'active' for new contracts)
9. Click **Tạo hợp đồng**
10. Review on detail page

#### 2. Viewing Contracts

1. Go to **Danh sách hợp đồng**
2. Use filters to narrow down:
   - Search by name/code/contract number
   - Filter by status/type/department
   - Show only expiring contracts
3. Click eye icon to view details
4. Review all information on detail page

#### 3. Editing a Contract

1. Open contract detail page
2. Verify status is 'draft' or 'active'
3. Click **Sửa hợp đồng** button
4. Update necessary fields
5. Click **Cập nhật**
6. Changes saved immediately

**Note**: Only draft and active contracts can be edited.

#### 4. Renewing a Contract

1. Open contract detail page (must be active)
2. Check if contract is eligible for renewal
3. Click **Gia hạn hợp đồng** button
4. Review pre-filled form (data from old contract)
5. Adjust contract number (must be unique)
6. Update start date (defaults to day after old end date)
7. Modify salary/terms if needed
8. Click **Gia hạn**
9. Old contract status changes to 'renewed'
10. New contract created and displayed

#### 5. Terminating a Contract

1. Open active contract detail page
2. Click **Chấm dứt hợp đồng** button
3. In modal:
   - Select termination date
   - Enter detailed termination reason
4. Click **Xác nhận chấm dứt**
5. Contract status changes to 'terminated'
6. Termination info saved and displayed

#### 6. Deleting a Contract

1. Open draft contract detail page
2. Click **Xóa hợp đồng** button
3. Confirm deletion in modal
4. Contract permanently removed
5. Redirected to contract list

**Warning**: Only draft contracts can be deleted. This action cannot be undone.

---

## Database Schema

### Contract Table Fields

| Field              | Type             | Constraints       | Description              |
| ------------------ | ---------------- | ----------------- | ------------------------ |
| id                 | Integer          | PK, Auto          | Primary key              |
| contract_number    | CharField(50)    | Unique, Required  | Contract number          |
| employee_id        | ForeignKey       | Required          | Employee reference       |
| contract_type      | CharField(20)    | Choices, Required | Contract type            |
| start_date         | Date             | Required          | Contract start date      |
| end_date           | Date             | Nullable          | Contract end date        |
| signed_date        | Date             | Required          | Date contract was signed |
| salary             | Float            | Required, >0      | Base salary              |
| salary_coefficient | Float            | Default 1.0       | Salary multiplier        |
| allowances         | Float            | Default 0         | Additional allowances    |
| job_title_id       | ForeignKey       | Nullable          | Job title reference      |
| job_description    | Text             | Optional          | Job responsibilities     |
| workplace          | CharField(300)   | Required          | Work location            |
| working_hours      | CharField(100)   | Required          | Working schedule         |
| terms              | Text             | Required          | Contract terms           |
| benefits           | Text             | Optional          | Employee benefits        |
| insurance_info     | Text             | Optional          | Insurance details        |
| status             | CharField(20)    | Choices, Required | Current status           |
| termination_reason | Text             | Optional          | Why terminated           |
| termination_date   | Date             | Nullable          | When terminated          |
| notes              | Text             | Optional          | Additional notes         |
| contract_file      | FileField        | Optional          | Uploaded contract        |
| renewed_from_id    | ForeignKey(self) | Nullable          | Previous contract        |
| created_by_id      | ForeignKey       | Nullable          | Creator employee         |
| created_at         | DateTime         | Auto              | Creation timestamp       |
| updated_at         | DateTime         | Auto              | Last update timestamp    |

### Indexes

- `contract_number` (unique)
- `employee_id` (foreign key)
- `status` (frequent filtering)
- `end_date` (expiration queries)
- `created_at` (ordering)

---

## Common Issues & Solutions

### Issue 1: Cannot edit contract

**Symptom**: Edit button not visible or error when trying to edit

**Cause**: Contract status is not 'draft' or 'active'

**Solution**:

- Check contract status on detail page
- Only draft and active contracts can be edited
- Expired/terminated/renewed contracts are read-only

---

### Issue 2: Renewal fails

**Symptom**: Error when trying to renew contract

**Cause**:

1. Contract is not active
2. Contract type doesn't support renewal
3. Contract already renewed

**Solution**:

- Verify contract status is 'active'
- Check contract type (indefinite contracts may not need renewal)
- Check if contract already has successor (renewed status)

---

### Issue 3: Expiration alerts not showing

**Symptom**: No warning for contracts nearing expiration

**Cause**:

1. End date > 30 days away
2. Contract is not active
3. End date not set (indefinite)

**Solution**:

- Alerts only show for active contracts within 30 days of expiration
- Indefinite contracts have no expiration alerts
- Adjust alert threshold in code if needed (default 30 days)

---

### Issue 4: Cannot delete contract

**Symptom**: Delete button not visible

**Cause**: Contract status is not 'draft'

**Solution**:

- Only draft contracts can be deleted
- Active contracts must be terminated first
- Terminated contracts cannot be deleted (for record keeping)

---

### Issue 5: File upload fails

**Symptom**: Error when uploading contract file

**Cause**:

1. File too large
2. Invalid file type
3. Media directory permissions

**Solution**:

- Check file size (max configured in settings)
- Only upload PDF or DOC/DOCX files
- Verify `MEDIA_ROOT` directory exists and is writable
- Check file upload limits in server configuration

---

## Testing Checklist

### Model Testing

- [x] Contract creation with all fields
- [x] Unique contract number constraint
- [x] Date validation (start < end)
- [x] Status transitions
- [x] Renewal chain (renewed_from FK)
- [x] Helper methods (is_active, days_until_expiration, etc.)

### Form Testing

- [x] All fields display correctly
- [x] Required field validation
- [x] Date logic validation
- [x] Salary > 0 validation
- [x] Contract number uniqueness
- [x] File upload validation

### View Testing

- [ ] List view displays all contracts
- [ ] Filters work correctly
- [ ] Search finds contracts
- [ ] Pagination works
- [ ] Detail view shows all info
- [ ] Create form submits successfully
- [ ] Edit form updates correctly
- [ ] Renew creates new contract and updates old
- [ ] Terminate updates status and saves reason
- [ ] Delete removes draft contracts only

### Template Testing

- [ ] All pages render without errors
- [ ] Responsive layout works
- [ ] Buttons display based on status
- [ ] Modals open and close correctly
- [ ] Forms submit properly
- [ ] Alerts show when appropriate
- [ ] File download links work

### Integration Testing

- [ ] End-to-end contract lifecycle
- [ ] Renewal chain maintains integrity
- [ ] Expiration alerts trigger correctly
- [ ] Permissions enforce correctly
- [ ] File uploads save to correct location

---

## Future Enhancements

### Potential Features

1. **Email Notifications**:

   - Alert HR when contracts expiring
   - Notify employees before contract ends
   - Confirmation emails on status changes

2. **Digital Signatures**:

   - E-signature integration
   - Digital signing workflow
   - Signature verification

3. **Contract Templates**:

   - Pre-defined contract templates by type
   - Auto-fill clauses and terms
   - Template library management

4. **Bulk Operations**:

   - Bulk contract creation
   - Batch renewals
   - Mass status updates

5. **Advanced Reporting**:

   - Contract expiration calendar
   - Financial reports (total salary commitments)
   - Contract type distribution charts
   - Department-wise contract summary

6. **Workflow Approvals**:

   - Multi-level approval for new contracts
   - Approval history tracking
   - Rejection with feedback

7. **Document Generation**:

   - Auto-generate contract PDF from template
   - Populate contract with employee data
   - Export to Word/PDF format

8. **Audit Trail**:
   - Log all contract changes
   - Track who changed what and when
   - History timeline view

---

## File Summary

### Python Files

- `app/models.py`: Contract model (130 lines)
- `app/forms.py`: ContractForm (130 lines)
- `app/HodViews.py`: 7 contract views (280 lines)

### HTML Templates

- `list_contracts.html`: 300 lines
- `contract_detail.html`: 420 lines
- `create_edit_contract.html`: 350 lines
- **Total**: ~1,070 lines

### Configuration

- `hrm/urls.py`: 7 new URL patterns
- `sidebar_template.html`: 1 new menu section (2 items)

### Database

- 1 new table: `app_contract`
- 1 new migration: `0014_contract.py`

---

## Module Statistics

**Total Implementation**:

- **Model**: 1 (Contract with 25 fields + 5 helper methods)
- **Form**: 1 (ContractForm with 19 fields + custom validation)
- **Views**: 7 (list, detail, create, edit, renew, terminate, delete)
- **Templates**: 3 (list, detail, create/edit shared)
- **URLs**: 7 routes
- **Lines of Code**: ~1,600 lines total

**Features**:

- Full CRUD operations
- Lifecycle management (draft → active → expired/terminated/renewed)
- Renewal chain tracking
- Expiration alerts (30-day threshold)
- File upload support
- Comprehensive filtering and search
- Responsive AdminLTE UI

---

## Conclusion

The Contract Management module provides a complete solution for managing employment contracts with:

- ✅ Full contract lifecycle support
- ✅ Renewal chain tracking
- ✅ Expiration monitoring and alerts
- ✅ Comprehensive validation
- ✅ File attachment support
- ✅ Rich filtering and search
- ✅ Status-based permissions
- ✅ Responsive AdminLTE interface

This module enables HR departments to efficiently manage all employment contracts from creation through termination, with built-in safeguards and tracking for compliance and record-keeping.

---

**Module Status**: ✅ Complete (Ready for testing)

**Created**: November 15, 2025

**Last Updated**: November 15, 2025
