/**
 * AI Appointment Assistant
 * 
 * This script handles the AI recommendation system for student appointments,
 * including fetching recommendations from the server, handling user preferences,
 * and integrating auto-rebooking functionality.
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const aiAssistToggle = document.getElementById('aiAssistToggle');
    const personalizedScheduleBtn = document.getElementById('getPersonalizedScheduleBtn');
    const setPreferencesBtn = document.getElementById('setPreferencesBtn');
    const savePreferencesBtn = document.getElementById('savePreferencesBtn');
    const notificationToast = document.getElementById('notificationToast');
    const toastMessage = document.getElementById('toastMessage');
    
    // Bootstrap components
    const preferencesModal = new bootstrap.Modal(document.getElementById('aiPreferencesModal'), {
        backdrop: 'static'
    });
    const toast = new bootstrap.Toast(notificationToast, {
        delay: 5000
    });
    
    // Initialize
    loadUserPreferences();
    updateNotificationBadge();
    
    // Event Listeners
    if (aiAssistToggle) {
        aiAssistToggle.addEventListener('change', function() {
            toggleAIAssistance(this.checked);
        });
    }
    
    if (personalizedScheduleBtn) {
        personalizedScheduleBtn.addEventListener('click', function() {
            getPersonalizedRecommendations();
        });
    }
    
    if (setPreferencesBtn) {
        setPreferencesBtn.addEventListener('click', function() {
            // Load any saved preferences before showing modal
            loadUserPreferences();
            showPreferencesModal();
        });
    }
    
    if (savePreferencesBtn) {
        savePreferencesBtn.addEventListener('click', function() {
            savePreferences();
            preferencesModal.hide();
            showToast('Preferences saved successfully!', 'success');
        });
    }
    
    /**
     * Show the preferences modal
     */
    function showPreferencesModal() {
        // Load current preferences before showing modal
        loadUserPreferences();
        preferencesModal.show();
    }
    
    /**
     * Load user preferences from localStorage
     */
    function loadUserPreferences() {
        // Get saved preferences from localStorage
        const savedPreferences = JSON.parse(localStorage.getItem('aiPreferences')) || {};
        
        // Set preferred days
        if (savedPreferences.preferredDays && savedPreferences.preferredDays.length > 0) {
            document.querySelectorAll('[name="preferred_days"]').forEach(checkbox => {
                checkbox.checked = savedPreferences.preferredDays.includes(checkbox.value);
            });
        }
        
        // Set time range
        if (savedPreferences.startTime) {
            document.getElementById('startTime').value = savedPreferences.startTime;
        }
        
        if (savedPreferences.endTime) {
            document.getElementById('endTime').value = savedPreferences.endTime;
        }
        
        // Set preferred professors
        if (savedPreferences.preferredProfessors && savedPreferences.preferredProfessors.length > 0) {
            const professorSelect = document.getElementById('preferredProfessors');
            if (professorSelect) {
                Array.from(professorSelect.options).forEach(option => {
                    option.selected = savedPreferences.preferredProfessors.includes(option.value);
                });
            }
        }
        
        // Set switches
        if (savedPreferences.hasOwnProperty('autoRebook')) {
            document.getElementById('autoRebookToggle').checked = savedPreferences.autoRebook;
        }
        
        if (savedPreferences.hasOwnProperty('notifications')) {
            document.getElementById('notificationsToggle').checked = savedPreferences.notifications;
        }
        
        if (savedPreferences.hasOwnProperty('suggestions')) {
            document.getElementById('suggestionsToggle').checked = savedPreferences.suggestions;
        }
        
        if (savedPreferences.hasOwnProperty('autoPlan')) {
            document.getElementById('autoPlanToggle').checked = savedPreferences.autoPlan;
        }
        
        // Set AI toggle
        if (savedPreferences.hasOwnProperty('aiAssistance')) {
            document.getElementById('aiAssistToggle').checked = savedPreferences.aiAssistance;
        }
    }
    
    /**
     * Toggle AI assistance and update server
     */
    function toggleAIAssistance(enabled) {
        // Save to preferences
        const savedPreferences = JSON.parse(localStorage.getItem('aiPreferences')) || {};
        savedPreferences.aiAssistance = enabled;
        localStorage.setItem('aiPreferences', JSON.stringify(savedPreferences));
        
        // Send to server
        fetch('/student/update_ai_preference', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ enabled: enabled })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(`AI assistance ${enabled ? 'enabled' : 'disabled'} successfully!`, 'success');
            } else {
                showToast('Failed to update AI assistance preference', 'danger');
                // Revert toggle if failed
                aiAssistToggle.checked = !enabled;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('An error occurred', 'danger');
        });
    }
    
    /**
     * Get personalized recommendations from server
     */
    function getPersonalizedRecommendations() {
        const savedPreferences = JSON.parse(localStorage.getItem('aiPreferences')) || {};
        
        // If no preferences set, prompt user to set them
        if (!savedPreferences || Object.keys(savedPreferences).length === 0) {
            showToast('Please set your preferences first', 'warning');
            preferencesModal.show();
            return;
        }
        
        showToast('Generating personalized recommendations...', 'info');
        
        // Generate mock recommendations based on preferences
        setTimeout(() => {
            // Sample mock data based on preferences
            const recommendations = [
                {
                    id: 1,
                    professor_id: savedPreferences.preferredProfessors[0] || "1",
                    professor_name: "Dr. Ahmed Mohamed",
                    date: "Monday, May 15, 2025",
                    time_slot: "10:00 AM",
                    reason: "Based on your preferred days and availability of the professor."
                },
                {
                    id: 2,
                    professor_id: savedPreferences.preferredProfessors[1] || "2",
                    professor_name: "Dr. Sarah Hassan",
                    date: "Wednesday, May 17, 2025",
                    time_slot: "2:00 PM",
                    reason: "Matches your schedule pattern and professor's office hours."
                },
                {
                    id: 3,
                    professor_id: savedPreferences.preferredProfessors[2] || "3",
                    professor_name: "Dr. Mohamed Ibrahim",
                    date: "Thursday, May 18, 2025",
                    time_slot: "11:00 AM",
                    reason: "Optimal time based on your historical meeting patterns."
                }
            ];
            
            updateRecommendationDisplay(recommendations);
            showToast('Recommendations updated!', 'success');
            
            // Auto-book if enabled
            if (savedPreferences.autoPlan) {
                autoBookAppointments(recommendations);
            }
        }, 1500);
    }
    
    /**
     * Auto-book appointments from recommendations
     */
    function autoBookAppointments(recommendations) {
        if (!recommendations || recommendations.length === 0) {
            return;
        }
        
        // Get first recommendation and book it
        const firstRecommendation = recommendations[0];
        
        // Add notification
        addNotification(
            "Appointment Auto-Booked", 
            `An appointment has been automatically booked with ${firstRecommendation.professor_name} on ${firstRecommendation.date} at ${firstRecommendation.time_slot}.`,
            "success"
        );
        
        // Simulate booking process
        setTimeout(() => {
            scheduleAppointmentBasedOnPreferences(firstRecommendation);
        }, 1500);
    }
    
    /**
     * Save user preferences to localStorage and server
     */
    function savePreferences() {
        // Collect form data
        const preferredDays = Array.from(document.querySelectorAll('[name="preferred_days"]:checked'))
            .map(checkbox => checkbox.value);
            
        const startTime = document.getElementById('startTime').value;
        const endTime = document.getElementById('endTime').value;
        
        const preferredProfessors = Array.from(document.getElementById('preferredProfessors').selectedOptions)
            .map(option => option.value);
            
        const autoRebook = document.getElementById('autoRebookToggle').checked;
        const notifications = document.getElementById('notificationsToggle').checked;
        const suggestions = document.getElementById('suggestionsToggle').checked;
        const autoPlan = document.getElementById('autoPlanToggle').checked;
        
        // Create preferences object
        const preferences = {
            preferredDays,
            startTime,
            endTime,
            preferredProfessors,
            autoRebook,
            notifications,
            suggestions,
            autoPlan,
            aiAssistance: document.getElementById('aiAssistToggle').checked
        };
        
        // Save to localStorage
        localStorage.setItem('aiPreferences', JSON.stringify(preferences));
        
        // Add notification
        addNotification("Preferences Saved", "Your AI assistant preferences have been successfully saved.", "success");
        
        // Return preferences object for further processing
        return preferences;
    }
    
    /**
     * Schedule an appointment based on user preferences
     */
    function scheduleAppointmentBasedOnPreferences(recommendation) {
        if (!recommendation) {
            showToast('No suitable time slots found', 'warning');
            return;
        }
        
        // Simulation of booking process
        showToast('Scheduling appointment...', 'info');
        
        // Make API call to schedule appointment
        fetch('/student/schedule_appointment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                professor_id: recommendation.professor_id,
                date: recommendation.date,
                time_slot: recommendation.time_slot,
                auto_booked: true
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Appointment scheduled successfully!', 'success');
                
                // Update UI to show newly booked appointment
                // (This would depend on your specific UI implementation)
                
                // Refresh recommendations
                setTimeout(() => {
                    getPersonalizedRecommendations();
                }, 2000);
            } else {
                showToast('Failed to schedule appointment: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('An error occurred while scheduling appointment', 'danger');
        });
    }
    
    /**
     * Update recommendations display in UI
     */
    function updateRecommendationDisplay(recommendations) {
        const recommendationsContainer = document.getElementById('aiRecommendations');
        if (!recommendationsContainer) return;
        
        // Clear previous recommendations
        recommendationsContainer.innerHTML = '';
        
        if (!recommendations || recommendations.length === 0) {
            recommendationsContainer.innerHTML = '<div class="alert alert-info">No recommendations available based on your preferences.</div>';
            return;
        }
        
        // Create HTML for each recommendation
        recommendations.forEach(rec => {
            const recCard = document.createElement('div');
            recCard.className = 'card mb-3 recommendation-card';
            recCard.innerHTML = `
                <div class="card-body">
                    <h5 class="card-title">${rec.professor_name}</h5>
                    <h6 class="card-subtitle mb-2 text-muted">${rec.date} at ${rec.time_slot}</h6>
                    <p class="card-text">${rec.reason}</p>
                    <button class="btn btn-sm btn-primary book-btn" data-id="${rec.id}">
                        <i class="fas fa-calendar-check me-1"></i> Book Appointment
                    </button>
                </div>
            `;
            
            recommendationsContainer.appendChild(recCard);
            
            // Add event listener to book button
            recCard.querySelector('.book-btn').addEventListener('click', function() {
                scheduleAppointmentBasedOnPreferences(rec);
            });
        });
    }
    
    /**
     * Show a toast notification
     */
    function showToast(message, type = 'success') {
        // Set toast color based on type
        notificationToast.className = notificationToast.className.replace(/bg-\w+/, '');
        notificationToast.classList.add(`bg-${type}`);
        
        // Set message
        toastMessage.textContent = message;
        
        // Show toast
        toast.show();
    }
    
    /**
     * Get CSRF token from cookies
     */
    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
    
    // Add notification functions
    /**
     * Update the notification badge count
     */
    function updateNotificationBadge() {
        const notificationCount = document.getElementById('notificationCount');
        if (notificationCount) {
            // Get notifications from localStorage or set default
            const notifications = JSON.parse(localStorage.getItem('notifications')) || defaultNotifications();
            const unreadCount = notifications.filter(n => !n.read).length;
            
            // Update count
            notificationCount.textContent = unreadCount;
            
            // Show/hide badge
            const badge = notificationCount.closest('.notification-badge');
            if (badge) {
                badge.style.display = unreadCount > 0 ? 'block' : 'none';
            }
        }
    }
    
    /**
     * Add a new notification
     */
    function addNotification(title, message, type = 'info') {
        // Get existing notifications
        const notifications = JSON.parse(localStorage.getItem('notifications')) || defaultNotifications();
        
        // Add new notification
        const newNotification = {
            id: Date.now(),
            title: title,
            message: message,
            type: type,
            read: false,
            timestamp: new Date().toISOString()
        };
        
        notifications.unshift(newNotification);
        
        // Keep only latest 10 notifications
        if (notifications.length > 10) {
            notifications.pop();
        }
        
        // Save to localStorage
        localStorage.setItem('notifications', JSON.stringify(notifications));
        
        // Update badge
        updateNotificationBadge();
        
        // Show toast
        showToast(message, type);
    }
    
    /**
     * Default notifications for new users
     */
    function defaultNotifications() {
        return [
            {
                id: 1,
                title: "Welcome to AI Assistant",
                message: "AI Assistant is ready to help you schedule appointments",
                type: "success",
                read: false,
                timestamp: new Date().toISOString()
            },
            {
                id: 2,
                title: "Set Your Preferences",
                message: "Configure your preferences to get personalized recommendations",
                type: "info",
                read: false,
                timestamp: new Date().toISOString()
            }
        ];
    }
}); 