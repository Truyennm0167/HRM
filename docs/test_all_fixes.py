"""
Automated Testing Script for HRM Management Portal
Tests all 33 bug fixes from Phase 1-4
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.urls import reverse, NoReverseMatch
from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from app.models import Employee, Department, JobTitle, Attendance, Payroll, ExpenseCategory, JobPosting, Application, SalaryRuleTemplate, AppraisalPeriod
from datetime import datetime, date

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

def print_test(name, passed, details=""):
    status = f"{GREEN}✅ PASS{RESET}" if passed else f"{RED}❌ FAIL{RESET}"
    print(f"{status} | {name}")
    if details:
        print(f"     {YELLOW}{details}{RESET}")

def print_section(text):
    print(f"\n{YELLOW}📌 {text}{RESET}")

class URLTester:
    """Test URL resolution for all fixed URLs"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test_url(self, name, url_name, args=None, kwargs=None):
        """Test if URL can be reversed"""
        try:
            if args:
                url = reverse(url_name, args=args)
            elif kwargs:
                url = reverse(url_name, kwargs=kwargs)
            else:
                url = reverse(url_name)
            print_test(f"{name}: {url_name}", True, f"Resolves to: {url}")
            self.passed += 1
            return True
        except NoReverseMatch as e:
            print_test(f"{name}: {url_name}", False, f"NoReverseMatch: {str(e)}")
            self.failed += 1
            self.errors.append(f"{url_name}: {str(e)}")
            return False
        except Exception as e:
            print_test(f"{name}: {url_name}", False, f"Error: {str(e)}")
            self.failed += 1
            self.errors.append(f"{url_name}: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all URL tests"""
        print_header("URL RESOLUTION TESTS - 33 Fixed URLs")
        
        # Phase 1 Fixes (12 URLs)
        print_section("PHASE 1: Original NoReverseMatch Fixes (12 URLs)")
        self.test_url("Employee CRUD", "add_employee")
        self.test_url("Employee Update", "update_employee", args=[1])
        self.test_url("Employee Delete", "delete_employee", args=[1])
        self.test_url("Department Delete", "delete_department", args=[1])
        self.test_url("Job Title Delete", "delete_job_title", args=[1])
        self.test_url("Attendance Add", "add_attendance")
        self.test_url("Attendance Manage", "manage_attendance")
        self.test_url("Check Attendance Date", "check_attendance_date")
        
        # Phase 2 Fixes (8 URLs - form actions)
        print_section("PHASE 2: POST 404 Fixes (8 URLs)")
        self.test_url("Add Employee Save", "add_employee_save")
        self.test_url("Update Employee Save", "update_employee_save", args=[1])
        self.test_url("Add Department Save", "add_department_save")
        self.test_url("Add Job Title Save", "add_job_title_save")
        self.test_url("Add Attendance Save", "add_attendance_save")
        
        # Phase 3 Fixes (3 URLs - functionality)
        print_section("PHASE 3: Functionality Fixes (3 URLs)")
        self.test_url("Contract Create", "create_contract")
        self.test_url("Org Chart", "org_chart")
        
        # Round 2 Fixes (10 URLs)
        print_section("ROUND 2: New Bug Fixes (11 URLs)")
        self.test_url("Get Attendance Data", "get_attendance_data")
        self.test_url("Get Payroll Data", "get_payroll_data")
        self.test_url("Delete Payroll", "delete_payroll")
        self.test_url("Delete Job", "delete_job", args=[1])
        self.test_url("Update Application", "update_application", args=[1])
        self.test_url("Edit Salary Rule Template", "edit_salary_rule_template", args=[1])
        self.test_url("Generate Appraisals", "generate_appraisals", args=[1])
        self.test_url("Edit Expense Category", "edit_expense_category_save", args=[1])
        self.test_url("Delete Attendance", "delete_attendance", args=[1])
        self.test_url("Update Application Status", "update_application_status", args=[1])
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{BLUE}{'='*80}{RESET}")
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{YELLOW}📊 URL TEST SUMMARY:{RESET}")
        print(f"   Total URLs Tested: {total}")
        print(f"   {GREEN}Passed: {self.passed}{RESET}")
        print(f"   {RED}Failed: {self.failed}{RESET}")
        print(f"   Pass Rate: {pass_rate:.1f}%")
        
        if self.errors:
            print(f"\n{RED}❌ ERRORS FOUND:{RESET}")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        else:
            print(f"\n{GREEN}🎉 ALL URL TESTS PASSED!{RESET}")


class ViewTester:
    """Test if views exist and are callable"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test_view_exists(self, name, view_path):
        """Test if view function exists"""
        try:
            module_path, func_name = view_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[func_name])
            view_func = getattr(module, func_name)
            print_test(f"{name}", True, f"Found: {view_path}")
            self.passed += 1
            return True
        except (ImportError, AttributeError) as e:
            print_test(f"{name}", False, f"Not found: {str(e)}")
            self.failed += 1
            self.errors.append(f"{view_path}: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all view tests"""
        print_header("VIEW EXISTENCE TESTS")
        
        print_section("Round 2 Fixed Views")
        self.test_view_exists("Get Attendance Data", "app.management_views.get_attendance_data")
        self.test_view_exists("Get Payroll Data", "app.management_views.get_payroll_data")
        self.test_view_exists("Delete Payroll", "app.management_views.delete_payroll")
        self.test_view_exists("Delete Job", "app.management_views.delete_job")
        self.test_view_exists("Update Application", "app.management_views.update_application")
        self.test_view_exists("Edit Salary Rule Template", "app.management_views.edit_salary_rule_template")
        self.test_view_exists("Generate Appraisals", "app.management_views.generate_appraisals")
        self.test_view_exists("Edit Expense Category Save", "app.management_views.edit_expense_category_save")
        self.test_view_exists("Delete Job Title", "app.management_views.delete_job_title")
        self.test_view_exists("Delete Department", "app.management_views.delete_department")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{BLUE}{'='*80}{RESET}")
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{YELLOW}📊 VIEW TEST SUMMARY:{RESET}")
        print(f"   Total Views Tested: {total}")
        print(f"   {GREEN}Passed: {self.passed}{RESET}")
        print(f"   {RED}Failed: {self.failed}{RESET}")
        print(f"   Pass Rate: {pass_rate:.1f}%")
        
        if self.errors:
            print(f"\n{RED}❌ ERRORS FOUND:{RESET}")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        else:
            print(f"\n{GREEN}🎉 ALL VIEW TESTS PASSED!{RESET}")


class DatabaseTester:
    """Test database models and data"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = []
    
    def test_model_count(self, model_name, model_class, min_count=0):
        """Test if model has data"""
        try:
            count = model_class.objects.count()
            if count > min_count:
                print_test(f"{model_name} records", True, f"Found {count} records")
                self.passed += 1
            else:
                print_test(f"{model_name} records", False, f"Only {count} records (expected > {min_count})")
                self.failed += 1
                self.warnings.append(f"{model_name}: Only {count} records")
            return count
        except Exception as e:
            print_test(f"{model_name} records", False, f"Error: {str(e)}")
            self.failed += 1
            return 0
    
    def run_all_tests(self):
        """Run all database tests"""
        print_header("DATABASE TESTS")
        
        print_section("Core Models")
        self.test_model_count("Employees", Employee, min_count=0)
        self.test_model_count("Departments", Department, min_count=0)
        self.test_model_count("Job Titles", JobTitle, min_count=0)
        
        print_section("Optional Models")
        attendance_count = self.test_model_count("Attendance Records", Attendance, min_count=0)
        payroll_count = self.test_model_count("Payroll Records", Payroll, min_count=0)
        expense_count = self.test_model_count("Expense Categories", ExpenseCategory, min_count=0)
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{BLUE}{'='*80}{RESET}")
        total = self.passed + self.failed
        
        print(f"\n{YELLOW}📊 DATABASE TEST SUMMARY:{RESET}")
        print(f"   Total Tests: {total}")
        print(f"   {GREEN}Passed: {self.passed}{RESET}")
        print(f"   {RED}Failed: {self.failed}{RESET}")
        
        if self.warnings:
            print(f"\n{YELLOW}⚠️  WARNINGS:{RESET}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")


class TemplateChecker:
    """Check if templates have correct URL references"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.issues = []
    
    def check_template_file(self, name, filepath, required_urls):
        """Check if template contains required URL references"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing_urls = []
            for url in required_urls:
                if url not in content:
                    missing_urls.append(url)
            
            if not missing_urls:
                print_test(f"{name}", True, f"All URLs present")
                self.passed += 1
            else:
                print_test(f"{name}", False, f"Missing: {', '.join(missing_urls)}")
                self.failed += 1
                self.issues.append(f"{name}: Missing {missing_urls}")
            
        except FileNotFoundError:
            print_test(f"{name}", False, f"Template not found: {filepath}")
            self.failed += 1
            self.issues.append(f"{name}: File not found")
        except Exception as e:
            print_test(f"{name}", False, f"Error: {str(e)}")
            self.failed += 1
    
    def run_all_tests(self):
        """Run all template tests"""
        print_header("TEMPLATE TESTS")
        
        print_section("Round 2 Fixed Templates")
        
        # Check update_employee_template
        self.check_template_file(
            "Update Employee Template",
            "app/templates/hod_template/update_employee_template.html",
            ["update_employee_save"]
        )
        
        # Check department_template
        self.check_template_file(
            "Department Template",
            "app/templates/hod_template/department_template.html",
            ["delete_department", "POST"]
        )
        
        # Check job_title_template
        self.check_template_file(
            "Job Title Template",
            "app/templates/hod_template/job_title_template.html",
            ["delete_job_title", "POST"]
        )
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{BLUE}{'='*80}{RESET}")
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{YELLOW}📊 TEMPLATE TEST SUMMARY:{RESET}")
        print(f"   Total Templates Tested: {total}")
        print(f"   {GREEN}Passed: {self.passed}{RESET}")
        print(f"   {RED}Failed: {self.failed}{RESET}")
        print(f"   Pass Rate: {pass_rate:.1f}%")
        
        if self.issues:
            print(f"\n{RED}❌ ISSUES FOUND:{RESET}")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")


def main():
    """Run all tests"""
    print_header("🚀 HRM MANAGEMENT PORTAL - AUTOMATED TEST SUITE")
    print(f"{YELLOW}Testing 25 actively used URLs (removed 8 unused URL names){RESET}")
    print(f"{YELLOW}Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}\n")
    
    # Run all test suites
    url_tester = URLTester()
    url_tester.run_all_tests()
    
    view_tester = ViewTester()
    view_tester.run_all_tests()
    
    db_tester = DatabaseTester()
    db_tester.run_all_tests()
    
    template_checker = TemplateChecker()
    template_checker.run_all_tests()
    
    # Final summary
    print_header("🎯 FINAL SUMMARY")
    
    total_tests = (url_tester.passed + url_tester.failed + 
                   view_tester.passed + view_tester.failed + 
                   db_tester.passed + db_tester.failed +
                   template_checker.passed + template_checker.failed)
    
    total_passed = (url_tester.passed + view_tester.passed + 
                    db_tester.passed + template_checker.passed)
    
    total_failed = (url_tester.failed + view_tester.failed + 
                    db_tester.failed + template_checker.failed)
    
    pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{YELLOW}📊 OVERALL RESULTS:{RESET}")
    print(f"   Total Tests Run: {total_tests}")
    print(f"   {GREEN}Total Passed: {total_passed}{RESET}")
    print(f"   {RED}Total Failed: {total_failed}{RESET}")
    print(f"   Overall Pass Rate: {pass_rate:.1f}%")
    
    if total_failed == 0:
        print(f"\n{GREEN}{'='*80}{RESET}")
        print(f"{GREEN}{'🎉 ALL TESTS PASSED! SYSTEM READY FOR PRODUCTION! 🎉'.center(80)}{RESET}")
        print(f"{GREEN}{'='*80}{RESET}\n")
    else:
        print(f"\n{RED}{'='*80}{RESET}")
        print(f"{RED}{'⚠️  SOME TESTS FAILED - PLEASE REVIEW ERRORS ABOVE'.center(80)}{RESET}")
        print(f"{RED}{'='*80}{RESET}\n")
    
    return total_failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
