// Investment Goals Form Interactivity
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('goalsForm');
    const riskSlider = document.getElementById('risk_slider');
    const riskOut = document.getElementById('riskOut');
    const riskHidden = document.getElementById('risk');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnLoading = document.getElementById('btnLoading');
    const formPreview = document.getElementById('formPreview');
    const previewContent = document.getElementById('previewContent');

    // Risk slider functionality
    function updateRiskDisplay(value) {
        const riskLevels = ['Conservative', 'Moderate', 'Aggressive'];
        const riskValues = ['low', 'medium', 'high'];
        
        riskOut.textContent = riskLevels[value];
        riskHidden.value = riskValues[value];
        
        // Update preview if visible
        updateFormPreview();
    }

    // Form preview functionality
    function updateFormPreview() {
        const goal = document.getElementById('goal').value;
        const risk = riskHidden.value;
        const amount = document.getElementById('investment_amount').value;
        const timeline = document.getElementById('time_horizon').value;
        const custom = document.getElementById('custom_goal').value;

        if (goal || amount || timeline || custom) {
            let preview = '<div class="preview-item"><strong>Goal:</strong> ';
            preview += goal ? document.getElementById('goal').selectedOptions[0].text : 'Not specified';
            preview += '</div>';

            preview += '<div class="preview-item"><strong>Risk Tolerance:</strong> ';
            preview += riskOut.textContent;
            preview += '</div>';

            if (amount) {
                const parsedAmount = parseInvestmentAmount(amount);
                if (parsedAmount) {
                    preview += '<div class="preview-item"><strong>Investment Amount:</strong> $';
                    preview += parsedAmount.toLocaleString();
                    preview += '</div>';
                }
            }

            if (timeline) {
                preview += '<div class="preview-item"><strong>Timeline:</strong> ';
                preview += document.getElementById('time_horizon').selectedOptions[0].text;
                preview += '</div>';
            }

            if (custom) {
                preview += '<div class="preview-item"><strong>Custom Goal:</strong> ';
                preview += custom;
                preview += '</div>';
            }

            previewContent.innerHTML = preview;
            formPreview.style.display = 'block';
        } else {
            formPreview.style.display = 'none';
        }
    }

    // Add event listeners
    if (riskSlider) {
        riskSlider.addEventListener('input', function() {
            updateRiskDisplay(this.value);
        });
    }

    // Add listeners to form inputs for preview
    const formInputs = form.querySelectorAll('select, input, textarea');
    formInputs.forEach(input => {
        input.addEventListener('change', updateFormPreview);
        input.addEventListener('input', updateFormPreview);
    });

    // Form submission with loading state
    if (form) {
        form.addEventListener('submit', function(e) {
            // Validate form before submission
            if (!validateForm()) {
                e.preventDefault();
                return false;
            }
            
            // Show loading state
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline';
            submitBtn.disabled = true;
            
            // Add a small delay to show the loading state
            setTimeout(() => {
                // Form will submit normally after this
            }, 500);
        });
    }

    // Form validation
    function validateForm() {
        const goal = document.getElementById('goal').value;
        const requiredFields = ['goal'];
        
        // Validate required fields
        for (let field of requiredFields) {
            const element = document.getElementById(field);
            if (!element.value) {
                element.style.borderColor = '#ff4444';
                return false;
            } else {
                element.style.borderColor = '#2a2d35';
            }
        }
        
        // Validate investment amount if provided
        if (!validateInvestmentAmount()) {
            return false;
        }
        
        return true;
    }

    // Real-time validation
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            if (!this.value) {
                this.style.borderColor = '#ff4444';
            } else {
                this.style.borderColor = '#2a2d35';
            }
        });
        
        field.addEventListener('input', function() {
            if (this.value) {
                this.style.borderColor = '#2a2d35';
            }
        });
    });

    // Add CSS for preview items
    const style = document.createElement('style');
    style.textContent = `
        .preview-item {
            margin: 8px 0;
            padding: 8px;
            background: var(--bg);
            border-radius: 4px;
            border-left: 3px solid var(--accent);
        }
    `;
    document.head.appendChild(style);
});

// Global function for risk slider (called from HTML)
function updateRiskDisplay(value) {
    const riskLevels = ['Conservative', 'Moderate', 'Aggressive'];
    const riskValues = ['low', 'medium', 'high'];
    
    const riskOut = document.getElementById('riskOut');
    const riskHidden = document.getElementById('risk');
    
    if (riskOut) riskOut.textContent = riskLevels[value];
    if (riskHidden) riskHidden.value = riskValues[value];
}

// Investment amount formatting and validation
function formatNumberInput(input) {
    // Remove all non-numeric characters except commas and periods
    let value = input.value.replace(/[^0-9,.]/g, '');
    
    // Handle multiple commas or periods - keep only the last one
    const commaCount = (value.match(/,/g) || []).length;
    const periodCount = (value.match(/\./g) || []).length;
    
    if (commaCount > 1) {
        // Keep only the last comma
        const lastCommaIndex = value.lastIndexOf(',');
        value = value.substring(0, lastCommaIndex).replace(/,/g, '') + value.substring(lastCommaIndex);
    }
    
    if (periodCount > 1) {
        // Keep only the last period
        const lastPeriodIndex = value.lastIndexOf('.');
        value = value.substring(0, lastPeriodIndex).replace(/\./g, '') + value.substring(lastPeriodIndex);
    }
    
    // Convert to number for validation
    const numericValue = parseFloat(value.replace(/,/g, ''));
    
    // Validate range
    if (numericValue && (numericValue < 100 || numericValue > 10000000)) {
        input.style.borderColor = '#ff4444';
        input.title = 'Amount must be between $100 and $10,000,000';
    } else {
        input.style.borderColor = '#2a2d35';
        input.title = '';
    }
    
    // Update the input value
    input.value = value;
    
    // Update form preview
    updateFormPreview();
}

// Function to parse investment amount for calculations
function parseInvestmentAmount(amountString) {
    if (!amountString) return null;
    
    // Remove commas and convert to number
    const numericValue = parseFloat(amountString.replace(/,/g, ''));
    
    // Validate range
    if (numericValue >= 100 && numericValue <= 10000000) {
        return numericValue;
    }
    
    return null;
}

// Enhanced form validation
function validateInvestmentAmount() {
    const amountInput = document.getElementById('investment_amount');
    const amount = parseInvestmentAmount(amountInput.value);
    
    if (amountInput.value && !amount) {
        amountInput.style.borderColor = '#ff4444';
        amountInput.title = 'Amount must be between $100 and $10,000,000';
        return false;
    } else {
        amountInput.style.borderColor = '#2a2d35';
        amountInput.title = '';
        return true;
    }
}