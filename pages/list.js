const container = document.getElementById('lawyer-container');

// --- 1. RENDER FUNCTION (Draws the HTML) ---
function renderLawyers(data) {
    container.innerHTML = ""; // Clear existing content
    
    if(data.length === 0) {
        container.innerHTML = "<h3>No lawyers found matching your criteria.</h3>";
        return;
    }

    container.innerHTML += `<p class="result-count">Found ${data.length} lawyers</p>`;

    data.forEach(lawyer => {
        let eduHTML = "";
        lawyer.education.forEach(edu => {
            eduHTML += `<li><strong>${edu.school}</strong><span>${edu.degree} | ${edu.year}</span></li>`;
        });

        let badgeHTML = lawyer.verified 
            ? `<span class="verified-badge"><i class="fas fa-check-circle"></i> Verified</span>` 
            : ``;

        const cardHTML = `
        <div class="lawyer-card">
            <div class="card-left">
                <img src="${lawyer.image}" alt="${lawyer.name}">
                <div class="rating"><i class="fas fa-star"></i> ${lawyer.rating} <span>(${lawyer.reviewCount})</span></div>
            </div>
            <div class="card-body">
                <div class="card-header">
                    <h2>${lawyer.name}</h2>
                    ${badgeHTML}
                </div>
                <p class="specialty">${lawyer.specialty}</p>
                <p class="location"><i class="fas fa-map-marker-alt"></i> ${lawyer.location} • ${lawyer.experience} Yrs Exp.</p>
                <hr>
                <div class="education-section">
                    <h4><i class="fas fa-graduation-cap"></i> Education</h4>
                    <ul class="education-list">${eduHTML}</ul>
                </div>
            </div>
            <div class="card-actions">
                <span class="price">₹${lawyer.price}/hr</span>
                <button class="btn btn-primary" onclick="sendRequestToLawyer('${lawyer.id}', '${lawyer.name}')">Send Request</button>
                <button class="btn btn-outline" onclick="viewLawyerProfile('${lawyer.id}')">Profile</button>
            </div>
        </div>`;

        container.innerHTML += cardHTML;
    });
}

// --- 2. FILTER FUNCTION (Logic) ---
function filterLawyers() {
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const isVerifiedChecked = document.getElementById('verifiedCheck').checked;
    const isExpChecked = document.getElementById('expCheck').checked;

    const checkedBoxes = document.querySelectorAll('.cat-check:checked');
    const selectedCategories = Array.from(checkedBoxes).map(box => box.value);

    const filteredData = lawyersData.filter(lawyer => {
        // A. Search Text
        const matchesText = lawyer.name.toLowerCase().includes(searchInput) || 
                            lawyer.specialty.toLowerCase().includes(searchInput);
        
        // B. Checkboxes
        const matchesVerified = isVerifiedChecked ? lawyer.verified === true : true;
        const matchesExp = isExpChecked ? lawyer.experience >= 10 : true;

        // C. Categories
        const matchesCategory = selectedCategories.length === 0 || selectedCategories.includes(lawyer.specialty);

        return matchesText && matchesVerified && matchesExp && matchesCategory;
    });

    renderLawyers(filteredData);
}

// --- 3. URL PARAMETER HANDLING ---
function applyUrlFilters() {
    // Reads URL like: lawyers.html?category=Family%20Law
    const params = new URLSearchParams(window.location.search);
    const categoryFromHome = params.get('category');

    if (categoryFromHome) {
        const checkboxes = document.querySelectorAll('.cat-check');
        checkboxes.forEach(box => {
            if (box.value === categoryFromHome) {
                box.checked = true;
            }
        });
        filterLawyers(); // Run filter immediately
    } else {
        renderLawyers(lawyersData); // Show all
    }
}

// Run on load
applyUrlFilters();

// --- 4. LAWYER REQUEST FUNCTIONALITY ---

// Check if user is logged in
function checkClientAuth() {
    const token = localStorage.getItem('access_token');
    const userType = localStorage.getItem('userType');
    
    if (!token || userType !== 'client') {
        alert('Please login as a client to send requests to lawyers.');
        window.location.href = 'client-login.html';
        return false;
    }
    return true;
}

// Send request to lawyer
function sendRequestToLawyer(lawyerId, lawyerName) {
    if (!checkClientAuth()) return;
    
    // Show request modal
    showRequestModal(lawyerId, lawyerName);
}

// View lawyer profile
function viewLawyerProfile(lawyerId) {
    alert(`View profile for lawyer ID: ${lawyerId} - This would open a detailed profile page`);
}

// Show request modal
function showRequestModal(lawyerId, lawyerName) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Send Request to ${lawyerName}</h3>
                <button class="close-btn" onclick="closeRequestModal()">&times;</button>
            </div>
            <form id="requestForm">
                <div class="form-group">
                    <label>Case Title *</label>
                    <input type="text" id="requestTitle" required placeholder="Brief title for your legal matter">
                </div>
                <div class="form-group">
                    <label>Description *</label>
                    <textarea id="requestDescription" required rows="4" placeholder="Describe your legal issue in detail..."></textarea>
                </div>
                <div class="form-group">
                    <label>Category *</label>
                    <select id="requestCategory" required>
                        <option value="">Select category</option>
                        <option value="Property Law">Property Law</option>
                        <option value="Family Law">Family Law</option>
                        <option value="Corporate Law">Corporate Law</option>
                        <option value="Contract and Agreement Law">Contract and Agreement Law</option>
                        <option value="Consumer Protection Law">Consumer Protection Law</option>
                        <option value="Labour and Employment Law">Labour and Employment Law</option>
                        <option value="IPR Law">IPR Law</option>
                        <option value="Criminal Defense">Criminal Defense</option>
                        <option value="Real Estate">Real Estate</option>
                        <option value="Intellectual Property">Intellectual Property</option>
                    </select>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Urgency Level</label>
                        <select id="requestUrgency">
                            <option value="low">Low</option>
                            <option value="medium" selected>Medium</option>
                            <option value="high">High</option>
                            <option value="urgent">Urgent</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Preferred Meeting</label>
                        <select id="requestMeeting">
                            <option value="">No preference</option>
                            <option value="online">Online</option>
                            <option value="in-person">In-person</option>
                            <option value="phone">Phone</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Budget Min (₹)</label>
                        <input type="number" id="requestBudgetMin" min="0" placeholder="5000">
                    </div>
                    <div class="form-group">
                        <label>Budget Max (₹)</label>
                        <input type="number" id="requestBudgetMax" min="0" placeholder="15000">
                    </div>
                </div>
                <div class="form-group">
                    <label>Location</label>
                    <input type="text" id="requestLocation" placeholder="City, State">
                </div>
                <div class="form-group">
                    <label>Additional Notes</label>
                    <textarea id="requestNotes" rows="3" placeholder="Any additional information..."></textarea>
                </div>
                <div class="modal-actions">
                    <button type="submit" class="btn btn-primary">Send Request</button>
                    <button type="button" class="btn btn-outline" onclick="closeRequestModal()">Cancel</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Handle form submission
    document.getElementById('requestForm').addEventListener('submit', function(e) {
        e.preventDefault();
        submitLawyerRequest(lawyerId);
    });
}

// Close request modal
function closeRequestModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) {
        modal.remove();
    }
}

// Submit lawyer request
async function submitLawyerRequest(lawyerId) {
    const requestData = {
        lawyer_id: lawyerId,
        title: document.getElementById('requestTitle').value,
        description: document.getElementById('requestDescription').value,
        category: document.getElementById('requestCategory').value,
        urgency_level: document.getElementById('requestUrgency').value,
        preferred_meeting_type: document.getElementById('requestMeeting').value || null,
        budget_min: parseFloat(document.getElementById('requestBudgetMin').value) || null,
        budget_max: parseFloat(document.getElementById('requestBudgetMax').value) || null,
        location: document.getElementById('requestLocation').value || null,
        additional_notes: document.getElementById('requestNotes').value || null
    };
    
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://localhost:8001/api/requests/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(requestData)
        });
        
        if (response.ok) {
            const result = await response.json();
            alert('Request sent successfully! The lawyer will be notified.');
            closeRequestModal();
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail || 'Failed to send request'}`);
        }
    } catch (error) {
        console.error('Error sending request:', error);
        alert('Error sending request. Please try again.');
    }
}