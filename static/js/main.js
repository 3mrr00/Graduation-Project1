// Main JavaScript for University Appointment System

document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltips initialization
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Flash messages auto-dismiss
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Appointment Booking Form
    const appointmentForm = document.getElementById('appointment-form');
    if (appointmentForm) {
        // Event listeners and form setup
        console.log('Appointment form initialized - static time slots mode');
        
        // The time slots are now loaded directly from the server
        // This JavaScript functionality is disabled
        
        // Initialize date picker if needed
        const dateInput = document.getElementById('date');
        if (dateInput) {
            // Set min date to today
            const today = new Date();
            const formattedDate = today.toISOString().split('T')[0];
            dateInput.setAttribute('min', formattedDate);
            
            // Add weekend day validation
            dateInput.addEventListener('change', function() {
                const selectedDate = new Date(this.value);
                const dayOfWeek = selectedDate.getDay();
                
                // Check if weekend (0 = Sunday, 6 = Saturday)
                if (dayOfWeek === 0 || dayOfWeek === 6) {
                    alert('الرجاء اختيار يوم من أيام الأسبوع (من الاثنين إلى الجمعة).');
                    this.value = '';
                }
            });
        }
    }

    // Initialize Calendar for Professor Availability
    const availabilityCalendar = document.getElementById('availability-calendar');
    if (availabilityCalendar) {
        var calendar = new FullCalendar.Calendar(availabilityCalendar, {
            initialView: 'timeGridWeek',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            slotMinTime: '08:00:00',
            slotMaxTime: '20:00:00',
            allDaySlot: false,
            height: 'auto',
            events: '/professor/get_availability_events',
            eventColor: '#1976d2'
        });
        calendar.render();
    }

    // Appointment Status Buttons
    const statusButtons = document.querySelectorAll('.status-btn');
    statusButtons.forEach(button => {
        button.addEventListener('click', function() {
            const appointmentId = this.getAttribute('data-appointment-id');
            const status = this.getAttribute('data-status');
            const form = document.getElementById('status-form-' + appointmentId);
            
            if (form) {
                const statusInput = form.querySelector('input[name="status"]');
                statusInput.value = status;
                form.submit();
            }
        });
    });

    // Confirmation for Deleting Availability
    const deleteAvailabilityForms = document.querySelectorAll('.delete-availability-form');
    deleteAvailabilityForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this availability?')) {
                e.preventDefault();
            }
        });
    });

    // Confirmation for Cancelling Appointment
    const cancelAppointmentForms = document.querySelectorAll('.cancel-appointment-form');
    cancelAppointmentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to cancel this appointment?')) {
                e.preventDefault();
            }
        });
    });

    // Toggle Password Visibility
    const togglePasswordBtns = document.querySelectorAll('.toggle-password');
    togglePasswordBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const passwordInput = document.querySelector(this.getAttribute('data-target'));
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                passwordInput.type = 'password';
                this.innerHTML = '<i class="fas fa-eye"></i>';
            }
        });
    });
}); 