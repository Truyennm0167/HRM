/**
 * AJAX Approval Handlers for Manager Portal
 * Handles leave and expense approval/rejection with AJAX requests
 */

// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

/**
 * Approve Leave Request
 * @param {number} leaveId - ID of the leave request
 * @param {function} onSuccess - Callback function on success
 * @param {function} onError - Callback function on error
 */
function approveLeave(leaveId, onSuccess, onError) {
    fetch(`/portal/team/leaves/${leaveId}/approve/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Leave approved:', data.leave);
            if (onSuccess) onSuccess(data);
        } else {
            console.error('Approval failed:', data.message);
            if (onError) onError(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (onError) onError({message: 'Network error occurred'});
    });
}

/**
 * Reject Leave Request
 * @param {number} leaveId - ID of the leave request
 * @param {string} reason - Reason for rejection
 * @param {function} onSuccess - Callback function on success
 * @param {function} onError - Callback function on error
 */
function rejectLeave(leaveId, reason, onSuccess, onError) {
    if (!reason || reason.trim() === '') {
        if (onError) onError({message: 'Vui lòng nhập lý do từ chối'});
        return;
    }

    fetch(`/portal/team/leaves/${leaveId}/reject/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            reason: reason
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Leave rejected:', data.leave);
            if (onSuccess) onSuccess(data);
        } else {
            console.error('Rejection failed:', data.message);
            if (onError) onError(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (onError) onError({message: 'Network error occurred'});
    });
}

/**
 * Approve Expense Request
 * @param {number} expenseId - ID of the expense request
 * @param {function} onSuccess - Callback function on success
 * @param {function} onError - Callback function on error
 */
function approveExpense(expenseId, onSuccess, onError) {
    fetch(`/portal/team/expenses/${expenseId}/approve/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Expense approved:', data.expense);
            if (onSuccess) onSuccess(data);
        } else {
            console.error('Approval failed:', data.message);
            if (onError) onError(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (onError) onError({message: 'Network error occurred'});
    });
}

/**
 * Reject Expense Request
 * @param {number} expenseId - ID of the expense request
 * @param {string} reason - Reason for rejection
 * @param {function} onSuccess - Callback function on success
 * @param {function} onError - Callback function on error
 */
function rejectExpense(expenseId, reason, onSuccess, onError) {
    if (!reason || reason.trim() === '') {
        if (onError) onError({message: 'Vui lòng nhập lý do từ chối'});
        return;
    }

    fetch(`/portal/team/expenses/${expenseId}/reject/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            reason: reason
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Expense rejected:', data.expense);
            if (onSuccess) onSuccess(data);
        } else {
            console.error('Rejection failed:', data.message);
            if (onError) onError(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (onError) onError({message: 'Network error occurred'});
    });
}

/**
 * Example usage with Bootstrap modals and SweetAlert2
 */

// Example: Approve leave with confirmation
function handleLeaveApprove(leaveId, employeeName) {
    Swal.fire({
        title: 'Xác nhận phê duyệt',
        text: `Phê duyệt đơn nghỉ phép của ${employeeName}?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Phê duyệt',
        cancelButtonText: 'Hủy',
        confirmButtonColor: '#28a745',
        cancelButtonColor: '#6c757d'
    }).then((result) => {
        if (result.isConfirmed) {
            approveLeave(leaveId, 
                (data) => {
                    Swal.fire('Thành công!', data.message, 'success');
                    // Update UI - remove from pending list or refresh page
                    location.reload();
                },
                (error) => {
                    Swal.fire('Lỗi!', error.message, 'error');
                }
            );
        }
    });
}

// Example: Reject leave with reason
function handleLeaveReject(leaveId, employeeName) {
    Swal.fire({
        title: 'Từ chối đơn nghỉ phép',
        text: `Từ chối đơn của ${employeeName}`,
        input: 'textarea',
        inputPlaceholder: 'Nhập lý do từ chối...',
        inputAttributes: {
            'aria-label': 'Nhập lý do từ chối',
            'required': 'required'
        },
        showCancelButton: true,
        confirmButtonText: 'Từ chối',
        cancelButtonText: 'Hủy',
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        inputValidator: (value) => {
            if (!value) {
                return 'Vui lòng nhập lý do từ chối!';
            }
        }
    }).then((result) => {
        if (result.isConfirmed) {
            rejectLeave(leaveId, result.value,
                (data) => {
                    Swal.fire('Đã từ chối!', data.message, 'success');
                    location.reload();
                },
                (error) => {
                    Swal.fire('Lỗi!', error.message, 'error');
                }
            );
        }
    });
}

// Example: Approve expense
function handleExpenseApprove(expenseId, employeeName, amount) {
    Swal.fire({
        title: 'Xác nhận phê duyệt',
        html: `Phê duyệt đơn hoàn tiền của <b>${employeeName}</b><br>Số tiền: <b>${amount}</b>?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Phê duyệt',
        cancelButtonText: 'Hủy',
        confirmButtonColor: '#28a745',
        cancelButtonColor: '#6c757d'
    }).then((result) => {
        if (result.isConfirmed) {
            approveExpense(expenseId,
                (data) => {
                    Swal.fire('Thành công!', data.message, 'success');
                    location.reload();
                },
                (error) => {
                    Swal.fire('Lỗi!', error.message, 'error');
                }
            );
        }
    });
}

// Example: Reject expense with reason
function handleExpenseReject(expenseId, employeeName) {
    Swal.fire({
        title: 'Từ chối đơn hoàn tiền',
        text: `Từ chối đơn của ${employeeName}`,
        input: 'textarea',
        inputPlaceholder: 'Nhập lý do từ chối...',
        inputAttributes: {
            'aria-label': 'Nhập lý do từ chối',
            'required': 'required'
        },
        showCancelButton: true,
        confirmButtonText: 'Từ chối',
        cancelButtonText: 'Hủy',
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        inputValidator: (value) => {
            if (!value) {
                return 'Vui lòng nhập lý do từ chối!';
            }
        }
    }).then((result) => {
        if (result.isConfirmed) {
            rejectExpense(expenseId, result.value,
                (data) => {
                    Swal.fire('Đã từ chối!', data.message, 'success');
                    location.reload();
                },
                (error) => {
                    Swal.fire('Lỗi!', error.message, 'error');
                }
            );
        }
    });
}

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        approveLeave,
        rejectLeave,
        approveExpense,
        rejectExpense,
        handleLeaveApprove,
        handleLeaveReject,
        handleExpenseApprove,
        handleExpenseReject
    };
}
