
let latestResult = null;

// File upload handling
const fileInput = document.getElementById('file_upload');
const fileLabel = document.querySelector('.file-text');

fileInput.addEventListener('change', function(e) {
    const fileName = e.target.files[0]?.name;
    if (fileName) {
        fileLabel.textContent = fileName;
        fileLabel.style.color = '#667eea';
        fileLabel.style.fontWeight = '600';
    } else {
        fileLabel.textContent = 'Choose file or drag here';
        fileLabel.style.color = '#4a5568';
        fileLabel.style.fontWeight = '500';
    }
});

// Form submission with loading state
document.getElementById("disputeForm").addEventListener("submit", async function(e) {
    e.preventDefault();
    
    const submitBtn = document.querySelector('.submit-btn');
    const originalContent = submitBtn.innerHTML;
    
    // Show loading state
    submitBtn.innerHTML = '<div class="loading"></div> Analyzing...';
    submitBtn.disabled = true;
    
    // Clear previous results
    const resultContainer = document.getElementById('result');
    resultContainer.innerHTML = '<div class="empty-state"><div class="loading"></div><p>Analyzing dispute case...</p></div>';
    
    try {
        const formData = new FormData(this);

        const response = await fetch("http://localhost:8002/submit", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        latestResult = data;

        // Display results with modern formatting
        displayResults(data);
        
        // Enable override button
        document.querySelector('.override-btn').disabled = false;
        
    } catch (error) {
        console.error('Error submitting form:', error);
        console.error('Error details:', error.message);
        document.getElementById('result').innerHTML = `
            <div class="result-item">
                <div class="result-label">Error</div>
                <div class="result-value">Failed to analyze case. Please try again.</div>
                <div style="font-size: 12px; color: #718096; margin-top: 8px;">Check browser console for details</div>
            </div>
        `;
    } finally {
        // Restore button state
        submitBtn.innerHTML = originalContent;
        submitBtn.disabled = false;
    }
});

function displayResults(data) {
    const decisionClass = data.decision.toLowerCase() === 'accept' ? 'decision-accept' : 'decision-reject';
    const confidencePercent = parseFloat(data.confidence) || 0;
    
    const resultHtml = `
        <div class="result-item">
            <div class="result-label">Decision</div>
            <div class="result-value">
                <span class="decision-badge ${decisionClass}">${data.decision}</span>
            </div>
        </div>
        
        <div class="result-item">
            <div class="result-label">Confidence Score</div>
            <div class="result-value">
                ${data.confidence}
                <div class="confidence-meter">
                    <div class="confidence-fill" style="width: ${confidencePercent}%"></div>
                </div>
            </div>
        </div>
        
        <div class="result-item">
            <div class="result-label">AI Reasoning</div>
            <div class="result-value">${data.reasoning}</div>
        </div>
    `;
    
    document.getElementById('result').innerHTML = resultHtml;
}

function applyOverride() {
    const override = document.getElementById('overrideDecision').value;
    if (!override || !latestResult) return;

    const overrideClass = override === 'ACCEPT' ? 'decision-accept' : 'decision-reject';
    const overrideText = override === 'ACCEPT' ? 'Accepted' : 'Rejected';
    
    // Add override result to the display
    const resultContainer = document.getElementById('result');
    const overrideHtml = `
        <div class="result-item" style="border-left-color: #f56565; margin-top: 24px;">
            <div class="result-label" style="color: #f56565;">Final Decision (Analyst Override)</div>
            <div class="result-value">
                <span class="decision-badge ${overrideClass}">${overrideText}</span>
                <p style="margin-top: 8px; font-size: 14px; color: #718096;">
                    <i class="fas fa-user-shield"></i> Applied by human analyst
                </p>
            </div>
        </div>
    `;
    
    resultContainer.innerHTML += overrideHtml;
    
    // Disable override button after use
    document.querySelector('.override-btn').disabled = true;
    document.getElementById('overrideDecision').value = '';
    
    // Scroll to show the override result
    resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Enable/disable override button based on selection
document.getElementById('overrideDecision').addEventListener('change', function() {
    const overrideBtn = document.querySelector('.override-btn');
    overrideBtn.disabled = !this.value || !latestResult;
});

// Add drag and drop functionality
const fileWrapper = document.querySelector('.file-upload-wrapper');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    fileWrapper.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    fileWrapper.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    fileWrapper.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    fileLabel.style.borderColor = '#667eea';
    fileLabel.style.background = '#edf2f7';
}

function unhighlight(e) {
    fileLabel.style.borderColor = '#cbd5e0';
    fileLabel.style.background = '#f7fafc';
}

fileWrapper.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        fileInput.files = files;
        const event = new Event('change', { bubbles: true });
        fileInput.dispatchEvent(event);
    }
}
