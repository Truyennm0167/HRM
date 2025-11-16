# APPRAISAL MODULE - TESTING GUIDE

## 📋 Test Data Created

### Period

- **Name**: Đánh giá Q4 2024
- **Status**: Active
- **Duration**: 90 days (from past to future)
- **Deadlines**:
  - Self-assessment: 7 days from now
  - Manager review: 14 days from now

### Criteria (Total Weight: 100%)

1. **Hoàn thành công việc đúng hạn** - Performance - 25%
2. **Chất lượng công việc** - Performance - 25%
3. **Kỹ năng chuyên môn** - Competency - 20%
4. **Tinh thần làm việc nhóm** - Behavior - 15%
5. **Chủ động và sáng tạo** - Behavior - 15%

### Appraisals

- **Total**: 7 appraisals created
- **Status**: All `pending_self` (waiting for employee self-assessment)
- **Employees**: Nguyễn Minh Truyền, Nguyễn Thị Hồng, Nguyễn Sơn Tùng, HR Manager, IT Manager, Sales Manager, IT Staff Member

---

## 🧪 Test Workflow

### Test 1: Employee Self-Assessment

**Objective**: Test employee can self-assess their performance

**Steps**:

1. Login as employee (e.g., Nguyễn Minh Truyền)
2. Go to Dashboard → Notice pending appraisals widget
3. Click **"Đánh giá hiệu suất"** in sidebar → **"Đánh giá của tôi"**
4. Click **"Tự đánh giá"** button
5. Fill in scores for all 5 criteria (0-10 points)
6. Fill in comments for each criteria
7. Fill in overall self-assessment sections:
   - Tự đánh giá chung
   - Thành tích đạt được
   - Khó khăn gặp phải (optional)
   - Kế hoạch phát triển (optional)
8. Click **"Gửi tự đánh giá"**

**Expected Results**:

- ✅ Form validation works (all scores required)
- ✅ Weighted average calculated automatically
- ✅ Status changes from `pending_self` → `pending_manager`
- ✅ `self_assessment_date` is set
- ✅ Manager receives notification (check their dashboard)
- ✅ Employee cannot edit anymore

**Verification**:

```sql
SELECT employee_id, status, self_overall_score, self_assessment_date
FROM app_appraisal
WHERE employee_id = <employee_id>;
```

---

### Test 2: Manager Review

**Objective**: Test manager can review employee performance

**Steps**:

1. Login as manager (e.g., IT Manager)
2. Go to Dashboard → Notice pending team appraisals widget
3. Click **"Đánh giá hiệu suất"** → **"Đánh giá team"**
4. See list of employees with status `pending_manager`
5. Click **"Đánh giá ngay"** for an employee
6. Review employee's self-assessment
7. Give manager scores for all 5 criteria
8. Fill in manager review sections:
   - Nhận xét chung
   - Điểm mạnh
   - Điểm cần cải thiện
   - Đề xuất phát triển
9. Check **"Đề xuất thăng chức"** or fill **"Đề xuất đào tạo"** if needed
10. Click **"Hoàn thành đánh giá"**

**Expected Results**:

- ✅ Can see employee's self-assessment
- ✅ Form validation works
- ✅ Manager scores calculated
- ✅ Status changes from `pending_manager` → `pending_hr`
- ✅ `manager_review_date` is set
- ✅ HR receives notification

**Verification**:

```sql
SELECT employee_id, status, manager_overall_score, manager_review_date,
       promotion_recommended, training_recommended
FROM app_appraisal
WHERE manager_id = <manager_id>;
```

---

### Test 3: HR Final Review

**Objective**: Test HR can finalize appraisals

**Steps**:

1. Login as HR
2. Go to Dashboard → Notice pending HR appraisals widget
3. Click **"Đánh giá hiệu suất"** → **"Quản lý đánh giá (HR)"**
4. Filter by **"Chờ phê duyệt"**
5. Click **"Phê duyệt"** for an appraisal
6. Review all information:
   - Employee self-assessment
   - Manager review
   - Scores comparison
7. Select **"Xếp loại tổng thể"** (Outstanding / Exceeds / Meets / Needs Improvement / Unsatisfactory)
8. Fill **"Nhận xét của HR"**
9. Enter **"Điều chỉnh lương"** (optional, e.g., 1000000 = +1M VND)
10. Click **"Hoàn tất đánh giá"**

**Expected Results**:

- ✅ Can see full appraisal details
- ✅ Overall rating required
- ✅ Salary adjustment preview works
- ✅ Status changes to `completed`
- ✅ `final_review_date` is set
- ✅ Employee's salary updated if adjustment provided
- ✅ Appraisal appears in "Recent Completed Appraisals" on dashboard

**Verification**:

```sql
-- Check appraisal
SELECT employee_id, status, final_score, overall_rating,
       salary_adjustment, final_review_date
FROM app_appraisal
WHERE status = 'completed';

-- Check employee salary
SELECT id, name, salary
FROM app_employee
WHERE id = <employee_id>;
```

---

### Test 4: View Appraisal Detail

**Objective**: Test read-only appraisal detail view

**Steps**:

1. Login as any user
2. Go to any appraisal list page
3. Click **"Xem chi tiết"** or **"Xem"**
4. Review all sections:
   - Employee info
   - Period info
   - Scores table (Self / Manager / Final)
   - Self-assessment text
   - Manager review text
   - HR final review (if completed)
   - Comments (if any)
5. Click **"In đánh giá"** to test print view

**Expected Results**:

- ✅ All data displays correctly
- ✅ No edit buttons (read-only)
- ✅ Print view hides unnecessary elements
- ✅ Scores formatted properly
- ✅ Badges show correct colors

---

## 🔍 Test Cases

### Functional Tests

#### TC-01: Weighted Score Calculation

**Given**: Period with 5 criteria (25%, 25%, 20%, 15%, 15%)
**When**: Employee scores (8, 9, 7, 10, 8)
**Then**: `self_overall_score` = (8×25 + 9×25 + 7×20 + 10×15 + 8×15) / 100 = 8.35

#### TC-02: Permission Check - Self Assessment

**Given**: Employee A's appraisal
**When**: Employee B tries to self-assess
**Then**: Access denied / Redirect

#### TC-03: Permission Check - Manager Review

**Given**: Appraisal with Manager A
**When**: Manager B tries to review
**Then**: Access denied / Redirect

#### TC-04: Status Workflow

**Given**: Appraisal in `pending_self`
**When**: Try to manager review
**Then**: Error / Not allowed

#### TC-05: Deadline Validation

**Given**: Self-assessment deadline passed
**When**: Employee tries to self-assess
**Then**: Warning message / Disabled

#### TC-06: Unique Constraint

**Given**: Period P, Employee E
**When**: Try to create duplicate appraisal
**Then**: Error / Already exists

#### TC-07: Salary Adjustment

**Given**: Employee salary = 10,000,000
**When**: HR sets adjustment = 1,000,000
**Then**: New salary = 11,000,000

#### TC-08: Manager Assignment

**Given**: Employee in Department D
**When**: Generate appraisals
**Then**: Manager = Employee with `is_manager=True` in Department D

---

## 📊 Test Data Validation

### Database Queries

```sql
-- Check period setup
SELECT * FROM app_appraisalperiod WHERE status = 'active';

-- Check criteria totals
SELECT period_id, SUM(weight) as total_weight
FROM app_appraisalcriteria
GROUP BY period_id;
-- Should be 100

-- Check appraisal counts by status
SELECT status, COUNT(*) as count
FROM app_appraisal
GROUP BY status;

-- Check appraisals with no scores
SELECT a.id, a.employee_id
FROM app_appraisal a
LEFT JOIN app_appraisalscore s ON s.appraisal_id = a.id
WHERE s.id IS NULL;
-- Should be empty

-- Check score counts per appraisal
SELECT appraisal_id, COUNT(*) as score_count
FROM app_appraisalscore
GROUP BY appraisal_id;
-- Should all be 5 (one per criteria)
```

---

## 🐛 Known Issues & Edge Cases

### Issue 1: Missing Manager

**Scenario**: Employee has no manager
**Impact**: `manager = NULL` in appraisal
**Solution**: HR should assign manager before activating period

### Issue 2: Criteria Weight ≠ 100%

**Scenario**: Total weight = 95% or 105%
**Impact**: Final score calculation inaccurate
**Solution**: Validation warning when total ≠ 100%

### Issue 3: Decimal Rounding

**Scenario**: Weighted score = 8.346
**Impact**: Displayed as 8.35
**Solution**: Using `ROUND(x, 2)`

---

## ✅ Test Completion Checklist

- [ ] Employee can self-assess
- [ ] Manager can review team
- [ ] HR can finalize appraisals
- [ ] Weighted calculations correct
- [ ] Status workflow enforced
- [ ] Permissions checked
- [ ] Salary adjustment works
- [ ] Dashboard widgets display
- [ ] Menu navigation works
- [ ] Templates render correctly
- [ ] Forms validate properly
- [ ] Django Admin accessible
- [ ] Print view works

---

## 🚀 Performance Tests

### Load Test

- **Scenario**: 1000 employees, 100 appraisals
- **Expected**: Page load < 2s
- **Tool**: Django Debug Toolbar

### Database Optimization

```sql
-- Add indexes (already done in models.py)
CREATE INDEX idx_appraisal_period_status ON app_appraisal(period_id, status);
CREATE INDEX idx_appraisal_employee_created ON app_appraisal(employee_id, created_at DESC);
```

---

## 📝 Test Report Template

```
# Appraisal Module Test Report
Date: [YYYY-MM-DD]
Tester: [Name]

## Test Environment
- Django Version: 4.2.16
- Database: SQLite / PostgreSQL
- Browser: Chrome / Firefox

## Test Results
| Test ID | Test Case | Status | Notes |
|---------|-----------|--------|-------|
| TC-01 | Weighted Calculation | ✅ PASS | |
| TC-02 | Self Assessment Permission | ✅ PASS | |
| TC-03 | Manager Review Permission | ✅ PASS | |
| ... | ... | ... | ... |

## Issues Found
1. [Issue description]
2. [Issue description]

## Overall Assessment
- Pass Rate: XX%
- Critical Issues: X
- Ready for Production: YES/NO
```

---

## 🎯 Next Steps After Testing

1. **If tests pass**:

   - Deploy to staging
   - Train users
   - Create user manual
   - Monitor first real usage

2. **If issues found**:
   - Log issues in bug tracker
   - Prioritize by severity
   - Fix critical bugs
   - Re-test affected areas

---

**Testing Complete?** 🎉
Update COMPREHENSIVE_ANALYSIS_REPORT.md:

- Appraisal: 0% → 100%
- Overall: 81.5% → 92%+
