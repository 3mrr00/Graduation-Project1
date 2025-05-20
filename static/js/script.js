// University Appointment System JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize any tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize any popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Calendar initialization (if on a page with calendar)
    initializeCalendars();
});

// Function to initialize calendars
function initializeCalendars() {
    const calendarEl = document.getElementById('appointment-calendar');
    if (calendarEl) {
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'timeGridWeek',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            slotMinTime: '08:00:00',
            slotMaxTime: '20:00:00',
            slotDuration: '00:30:00',
            navLinks: true,
            selectable: true,
            selectMirror: true,
            dayMaxEvents: true,
            businessHours: {
                daysOfWeek: [1, 2, 3, 4, 5], // Monday - Friday
                startTime: '08:00',
                endTime: '18:00',
            },
            select: function(info) {
                handleDateSelection(info);
            },
            eventClick: function(info) {
                handleEventClick(info);
            },
            events: '/api/appointments', // This would be your endpoint to fetch appointments
        });
        calendar.render();
    }
}

// Handle date selection on calendar
function handleDateSelection(info) {
    const startTime = info.startStr;
    const endTime = info.endStr;
    
    // Check if the selected time is already in the past
    if (new Date(startTime) < new Date()) {
        showAlert('You cannot book appointments in the past.', 'warning');
        return;
    }
    
    // Check if it's outside business hours or on weekends
    const day = new Date(startTime).getDay();
    const hour = new Date(startTime).getHours();
    if (day === 0 || day === 6 || hour < 8 || hour >= 18) {
        showAlert('Please select a time during business hours (Monday-Friday, 8:00 AM - 6:00 PM).', 'warning');
        return;
    }
    
    // Open modal to create a new appointment
    const modal = new bootstrap.Modal(document.getElementById('appointmentModal'));
    document.getElementById('appointment-start').value = startTime;
    document.getElementById('appointment-end').value = endTime;
    modal.show();
}

// Handle clicking on an event in the calendar
function handleEventClick(info) {
    const eventId = info.event.id;
    const eventTitle = info.event.title;
    const eventStart = info.event.startStr;
    const eventEnd = info.event.endStr;
    
    // Populate and show the modal
    const modal = new bootstrap.Modal(document.getElementById('viewAppointmentModal'));
    document.getElementById('view-appointment-title').textContent = eventTitle;
    document.getElementById('view-appointment-time').textContent = formatDateRange(eventStart, eventEnd);
    document.getElementById('appointment-id').value = eventId;
    modal.show();
}

// Helper function to show alerts
function showAlert(message, type = 'info') {
    const alertPlaceholder = document.getElementById('alert-placeholder');
    if (alertPlaceholder) {
        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        alertPlaceholder.append(wrapper);
        
        // Auto close after 5 seconds
        setTimeout(() => {
            const alert = bootstrap.Alert.getInstance(wrapper.querySelector('.alert'));
            if (alert) {
                alert.close();
            }
        }, 5000);
    }
}

// Format date range for display
function formatDateRange(start, end) {
    const startDate = new Date(start);
    const endDate = new Date(end);
    
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return `${startDate.toLocaleDateString('en-US', options)} - ${endDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`;
}

// Dark mode toggle
const darkModeToggle = document.getElementById('darkModeToggle');
if (darkModeToggle) {
    darkModeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        const isDarkMode = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
        
        // Update icon
        const icon = this.querySelector('i');
        if (isDarkMode) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
        }
    });
    
    // Check for saved preference
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    if (savedDarkMode) {
        document.body.classList.add('dark-mode');
        const icon = darkModeToggle.querySelector('i');
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    }
} 