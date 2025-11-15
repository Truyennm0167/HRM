## **Đặc tả Yêu cầu Phần mềm (SRS)**

## **Hệ thống Quản lý Nguồn Nhân lực (HRMS)**

**Phiên bản:** 1.0 **Ngày:** 14/11/2025 **Tác giả:** Nguyễn Minh Truyền (Đồ án Niên luận)

### **Phần 1: Giới thiệu**

#### **1.1. Mục đích**

Tài liệu này đặc tả các yêu cầu về chức năng và phi chức năng cho **Hệ thống Quản lý Nguồn Nhân lực (HRMS)**. Mục tiêu của hệ thống là tin học hóa và tối ưu hóa các quy trình nhân sự cốt lõi, bao gồm tuyển dụng, quản lý hồ sơ, chấm công, nghỉ phép và tính lương. Hệ thống được xây dựng dựa trên cảm hứng từ mô hình nghiệp vụ của Odoo.

#### **1.2. Phạm vi**

Hệ thống là một ứng dụng web cho phép ba nhóm người dùng chính (Nhân viên, Quản lý, và Bộ phận Nhân sự) tương tác trên một nền tảng duy nhất. Phạm vi bao gồm toàn bộ vòng đời của nhân viên, từ khi là ứng viên (Tuyển dụng) đến khi nghỉ việc (Offboarding).

#### **1.3. Định nghĩa & Thuật ngữ**

* **HRMS:** Human Resource Management System (Hệ thống Quản lý Nguồn Nhân lực).  
* **HR:** Human Resources (Bộ phận Nhân sự).  
* **Kanban:** Giao diện quản lý công việc dạng kéo-thả theo trạng thái.  
* **Quy trình nghiệp vụ:** Luồng công việc và dữ liệu trong một tổ chức.

---

### **Phần 2: Mô tả Tổng quan**

#### **2.1. Bối cảnh & Mục tiêu**

Dự án này là một phần của Đồ án Niên luận, nhằm xây dựng một hệ thống HRMS hoàn chỉnh, có khả năng mở rộng (modular). Mục tiêu là tạo ra một sản phẩm phần mềm cho phép các doanh nghiệp vừa và nhỏ quản lý nhân sự một cách hiệu quả, giảm thiểu giấy tờ và tự động hóa các tác vụ lặp lại.

#### **2.2. Người dùng mục tiêu (Actors)**

* **Quản trị viên (Admin):** Cấu hình hệ thống, tạo vai trò, quản lý phân quyền.  
* **Quản lý Nhân sự (HR Manager):** Quản lý toàn bộ quy trình tuyển dụng, hợp đồng, tính lương và xem báo cáo tổng thể.  
* **Quản lý Trực tiếp (Manager):** Duyệt đơn nghỉ phép/chi phí của team, đánh giá nhân viên, tham gia phỏng vấn.  
* **Nhân viên (Employee):** Tự cập nhật thông tin cá nhân, chấm công, nộp đơn xin nghỉ, xem phiếu lương.

#### **2.3. Sơ đồ quy trình nghiệp vụ**

Hệ thống sẽ được xây dựng xoay quanh 5 quy trình nghiệp vụ chính:

1. **Tuyển dụng:** Từ tạo tin tuyển dụng đến sàng lọc và nhận việc.  
2. **Hội nhập (Onboarding):** Từ ứng viên trở thành nhân viên, tạo hồ sơ và hợp đồng.  
3. **Vận hành:** Tác vụ hàng ngày (chấm công, nghỉ phép, chi phí).  
4. **Lương & Đánh giá:** Tổng hợp dữ liệu vận hành để tính lương và đánh giá hiệu suất.  
5. **Nghỉ việc (Offboarding):** Xử lý quy trình khi nhân viên rời công ty.

### **Phần 3: Yêu cầu Chức năng (Functional Requirements)**

#### **3.1. Phân hệ Tuyển dụng (Recruitment)**

*(Phần này được điều chỉnh và bổ sung nhiều nhất để tích hợp AI và tự động hóa)*

* **REQ-REC-001 (Điều chỉnh):** Hệ thống cho phép HR tạo các "Vị trí tuyển dụng" (Job Positions) với mô tả công việc chi tiết. **Hệ thống phải cung cấp chức năng đăng tải (post) vị trí này lên trang web tuyển dụng của công ty để ứng viên có thể nộp hồ sơ.**  
* **REQ-REC-002 (Điều chỉnh):** Hệ thống phải có khả năng tự động tạo "Hồ sơ Ứng viên" (Applicant) **từ form ứng tuyển trên website. Hệ thống phải có khả năng bóc tách thông tin (parse) từ CV (PDF, DOCX) mà ứng viên đính kèm để tự động điền vào các trường (Học vấn, Kỹ năng, Kinh nghiệm).**  
* **REQ-REC-003 (Mới):** Ngay sau khi ứng viên nộp hồ sơ thành công (kích hoạt REQ-REC-002), **hệ thống phải tự động gửi một email xác nhận** cho ứng viên ("Cảm ơn bạn đã ứng tuyển...").  
* **REQ-REC-004 (Mới):** Hệ thống phải **gửi thông báo (notification) thời gian thực** (hoặc tóm tắt) cho Quản lý Nhân sự (HR) khi có một hồ sơ ứng viên mới vừa ứng tuyển.  
* **REQ-REC-005 (Mới \- Sàng lọc AI):** Hệ thống phải có tính năng **tự động phân tích và so khớp CV của ứng viên với Mô tả công việc chi tiết** (từ REQ-REC-001) của Vị trí tuyển dụng.  
* **REQ-REC-006 (Mới \- Xếp hạng AI):** Dựa trên kết quả của REQ-REC-005, hệ thống phải **tự động tính điểm và xếp hạng (ranking) các ứng viên** theo mức độ phù hợp. HR có thể lọc và xem các ứng viên có điểm số cao nhất.  
* **REQ-REC-007** (Nguyên bản REQ-REC-003): HR có thể quản lý các hồ sơ ứng viên trên giao diện Kanban (ví dụ: Kéo-thả từ "Hồ sơ mới" \-\> "Sàng lọc AI" \-\> "Phỏng vấn" \-\> "Trúng tuyển").  
* **REQ-REC-008** (Nguyên bản REQ-REC-004): Hệ thống phải có nút "Tạo Nhân viên" trên hồ sơ ứng viên trúng tuyển, tự động chuyển thông tin của ứng viên sang phân hệ Nhân viên.

#### **3.2. Phân hệ Quản lý Nhân viên & Hợp đồng (Core HR)**

* **REQ-EMP-001 (Điều chỉnh):** Hệ thống (được kích hoạt bởi REQ-REC-008) phải tạo một "Hồ sơ Nhân viên" (Employee Profile) mới. **Quá trình này phải tự động sao chép toàn bộ thông tin liên quan từ Hồ sơ Ứng viên (bao gồm nhưng không giới hạn: Thông tin cá nhân, Kinh nghiệm, Học vấn, Kỹ năng và các Chứng chỉ).**  
* **REQ-EMP-002:** HR có thể bổ sung thông tin chi tiết cho hồ sơ nhân viên (Địa chỉ, CCCND, Thông tin ngân hàng, Liên hệ khẩn cấp).  
* **REQ-EMP-003:** Nhân viên có thể tự xem và đề xuất chỉnh sửa thông tin cá nhân của mình.  
* **REQ-EMP-004:** Hệ thống cho phép tạo và lưu trữ các "Hợp đồng" (Contracts) liên kết với hồ sơ nhân viên.  
* **REQ-EMP-005:** Hợp đồng phải bao gồm các thông tin chính: Lương cơ bản, phụ cấp, ngày bắt đầu, ngày kết thúc.  
* **REQ-EMP-006:** Hệ thống phải tự động thông báo cho HR trước 30 ngày khi hợp đồng sắp hết hạn.

#### **3.3. Phân hệ Vận hành (Operations)**

##### **3.3.1. Quản lý Chấm công (Attendance)**

* **REQ-ATT-001 (Điều chỉnh):** Nhân viên có thể thực hiện "Check-in" và "Check-out" trên giao diện web. **Hệ thống cũng phải cho phép Cán bộ nhân sự (HR) thực hiện chấm công thay (hoặc điều chỉnh) cho nhân viên trong các trường hợp đặc biệt (quên chấm công, đi công tác...).**  
* **REQ-ATT-002:** Quản lý có thể xem báo cáo chấm công (giờ vào, giờ ra, số giờ làm việc) của nhân viên dưới quyền.

##### ***3.3.2. Quản lý Nghỉ phép (Time Off)***

* ***REQ-TOF-001:** Nhân viên có thể tạo "Yêu cầu nghỉ phép" và chọn loại nghỉ (phép năm, nghỉ ốm...).*  
* ***REQ-TOF-002:** Yêu cầu phải được tự động gửi đến Quản lý trực tiếp để "Duyệt" (Approve) hoặc "Từ chối" (Reject).*  
* ***REQ-TOF-003:** Hệ thống phải tự động tính toán và hiển thị số ngày phép còn lại của nhân viên.*

##### ***3.3.3. Quản lý Chi phí (Expenses)***

* ***REQ-EXP-001:** Nhân viên có thể tạo "Yêu cầu hoàn tiền" (ví dụ: chi phí công tác) và đính kèm ảnh chụp hóa đơn.*  
* ***REQ-EXP-002:** Yêu cầu phải được gửi đến Quản lý để duyệt.*  
* ***REQ-EXP-003:** Các yêu cầu đã duyệt được chuyển cho Kế toán để xử lý thanh toán.*

#### **3.4. Phân hệ Lương & Đánh giá**

##### ***3.4.1. Đánh giá (Appraisal)***

* ***REQ-APP-001:** HR có thể thiết lập các "Kỳ đánh giá" (ví dụ: Đánh giá thử việc, Đánh giá cuối năm).*  
* ***REQ-APP-002:** Nhân viên và Quản lý có thể điền vào biểu mẫu đánh giá và gửi phản hồi cho nhau.*

##### ***3.4.2. Bảng lương (Payroll)***

* ***REQ-PAY-001:** Hệ thống phải có khả năng chạy "Quy trình tính lương" hàng loạt vào cuối tháng.*  
* ***REQ-PAY-002 (Tính liên kết):** Khi tính lương, hệ thống phải tự động lấy dữ liệu từ các phân hệ khác:*  
  * *Lương cơ bản & Phụ cấp (từ module **Hợp đồng**).*  
  * *Số ngày công thực tế (từ module **Chấm công**).*  
  * *Số ngày nghỉ có lương/không lương (từ module **Nghỉ phép**).*  
* ***REQ-PAY-003:** Hệ thống cho phép HR định nghĩa các "Quy tắc lương" (Salary Rules) để tính các khoản giảm trừ (BHXH, Thuế TNCN).*  
* ***REQ-PAY-004:** Nhân viên có thể xem và tải về "Phiếu lương" (Payslip) hàng tháng của mình.*

#### **3.5. Phân hệ Bảo mật & Offboarding**

* ***REQ-SEC-001:** Hệ thống phải có cơ chế phân quyền dựa trên vai trò (Role-Based Access Control).*  
  * *Ví dụ: Nhân viên chỉ thấy hồ sơ của mình, Quản lý thấy hồ sơ team mình, HR thấy tất cả.*  
* ***REQ-SEC-002:** Khi nhân viên nghỉ việc (Offboarding), Quản trị viên phải có khả năng "Vô hiệu hóa" (Archive/Deactivate) tài khoản của nhân viên đó để chặn mọi quyền truy cập.*

#### **3.6. Phân hệ Quản lý Tổ chức (NEW)**

* **REQ-ORG-001:** Hệ thống cho phép Quản trị viên (Admin) và HR tạo, sửa, xóa các "Phòng ban" (Departments) trong công ty (ví dụ: Phòng Kỹ thuật, Phòng Kinh doanh).  
* **REQ-ORG-002:** Mỗi "Hồ sơ Nhân viên" (REQ-EMP-001) phải được gán vào một Phòng ban.  
* **REQ-ORG-003:** Mỗi "Hồ sơ Nhân viên" phải có một trường "Quản lý trực tiếp" (Manager), trường này cũng liên kết đến một Hồ sơ Nhân viên khác.  
* **REQ-ORG-004:** Dựa trên dữ liệu Phòng ban (REQ-ORG-002) và Quản lý trực tiếp (REQ-ORG-003), **hệ thống phải có khả năng tự động tạo và hiển thị một "Sơ đồ tổ chức" (Organization Chart) trực quan.**

#### **3.7. Phân hệ Báo cáo & Thống kê (NEW)**

* **REQ-RPT-001:** Hệ thống phải cung cấp một "Bảng điều khiển" (Dashboard) trung tâm cho HR, hiển thị các thông tin quan trọng (ví dụ: số nhân viên mới, số hồ sơ đang tuyển, số nhân viên đang nghỉ phép).  
* **REQ-RPT-002 (Thống kê Tuyển dụng):** Cung cấp các báo cáo về:  
  * Số lượng hồ sơ ứng tuyển theo từng Vị trí tuyển dụng.  
  * Thời gian tuyển dụng trung bình (từ lúc đăng tin đến lúc trúng tuyển).  
  * Hiệu quả nguồn ứng viên (ví dụ: bao nhiêu % ứng viên từ website).  
* **REQ-RPT-003 (Thống kê Nhân sự):** Cung cấp các báo cáo về:  
  * Thống kê biến động nhân sự (tỷ lệ nghỉ việc, số nhân viên tuyển mới).  
  * Thống kê nhân sự theo độ tuổi, thâm niên, phòng ban.  
* **REQ-RPT-004 (Thống kê Vận hành):** Cung cấp các báo cáo về:  
  * Tình trạng đi trễ, về sớm, vắng mặt (từ module Chấm công).  
  * Thống kê số ngày nghỉ đã sử dụng/còn lại của toàn công ty (từ module Nghỉ phép).

### **Phần 4: Yêu cầu Phi chức năng (Non-Functional Requirements)**

* **Yêu cầu về Hiệu năng:**  
  * Thời gian tải trang chính (dashboard) phải dưới 3 giây.  
  * Quy trình tính lương cho 100 nhân viên phải hoàn thành dưới 5 phút.  
* **Yêu cầu về Bảo mật:**  
  * Mật khẩu người dùng phải được băm (hashed) bằng thuật toán mạnh (ví dụ: bcrypt).  
  * Các thông tin nhạy cảm (Lương, Số CCCD) phải được mã hóa khi lưu trữ hoặc hạn chế quyền truy cập tối đa.  
* **Yêu cầu về Tính khả dụng (Usability):**  
  * Giao diện phải tương thích (responsive) trên các trình duyệt web phổ biến (Chrome, Firefox) và thiết bị di động.  
  * Quy trình nghiệp vụ (ví dụ: xin nghỉ phép) phải hoàn thành trong tối đa 3 bước (click).  
* **Yêu cầu về Khả năng mở rộng (Scalability):**  
  * Hệ thống phải được thiết kế theo kiến trúc module (giống Odoo), cho phép dễ dàng thêm/bớt các phân hệ (ví dụ: thêm module Quản lý Tài sản) trong tương lai mà không ảnh hưởng đến các module hiện có.  
* **Yêu cầu về Tính toàn vẹn dữ liệu:**  
  * Hệ thống phải đảm bảo dữ liệu được nhất quán. Ví dụ: Khi một đơn nghỉ phép được duyệt, số ngày phép còn lại *phải* được cập nhật ngay lập tức.

