// Function to get URL parameters
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Function to update the URL with current parameters
function updateURL(stock1, stock2, shiftDays) {
    const params = new URLSearchParams();
    params.set('portf1', stock1);
    params.set('portf2', stock2);
    params.set('shift_days', shiftDays);
    
    const newURL = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState({ path: newURL }, '', newURL);
}

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const stock1Input = document.getElementById('stock1');
    const stock2Input = document.getElementById('stock2');
    const updateButton = document.getElementById('update-stocks');
    const shiftSlider = document.getElementById('shift-days');
    const shiftInput = document.getElementById('shift-days-input');
    const plotContainer = document.getElementById('plot-container');
    
    // Set initial values from URL parameters if they exist
    const portf1 = getUrlParameter('portf1') || 'KO';
    const portf2 = getUrlParameter('portf2') || 'PEP';
    let shiftDays = parseInt(getUrlParameter('shift_days') || '0');
    
    // Validate shift days range
    shiftDays = Math.max(-3000, Math.min(3000, shiftDays));
    
    // Set initial values
    stock1Input.value = portf1;
    stock2Input.value = portf2;
    
    if (shiftSlider && shiftInput) {
        shiftSlider.value = shiftDays;
        shiftInput.value = shiftDays;
    }
    
    // Function to update the plot with current values
    function updatePlot(auto=false) {
        const stock1 = stock1Input.value.trim().toUpperCase();
        const stock2 = stock2Input.value.trim().toUpperCase();
        let shiftDaysValue = shiftSlider.value;
        if (auto) {
            shiftDaysValue = "AUTO";
        }
        
        if (!stock1 || !stock2) {
            showError('אנא הזן את שמות שתי המניות');
            return;
        }
        
        // Update URL without page reload
        updateURL(stock1, stock2, shiftDaysValue);
        
        // Show loading message
        plotContainer.innerHTML = '<div style="padding: 20px; text-align: center;">טוען נתונים עבור ' + 
                                stock1 + ' ו-' + stock2 + '...</div>';
        
        // Build the URL with all parameters
        const url = `portf1=${encodeURIComponent(stock1)}&portf2=${encodeURIComponent(stock2)}&shift_days=${shiftDaysValue}`;
        
        // Navigate to the new URL
        window.location.href = url;
    }
    
    // Function to show error message
    function showError(message) {
        plotContainer.innerHTML = `
            <div style="color: red; padding: 20px; text-align: center;">
                <h3>שגיאה</h3>
                <p>${message}</p>
            </div>`;
    }
    
    // Event listeners
    if (updateButton) {
        updateButton.addEventListener('click', function() {
            // Make sure we have valid values before updating
            updatePlot();
        });
    }
    
    // Update when pressing Enter in input fields
    [stock1Input, stock2Input].forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                updatePlot();
            }
        });
    });
    
    // Sync slider and text input for shift days
    if (shiftSlider && shiftInput) {
        // Update text input when slider changes
        shiftSlider.addEventListener('input', function() {
            shiftInput.value = this.value;
            updatePlot();
        });
        
        // Update slider when text input changes
        shiftInput.addEventListener('change', function() {
            // Ensure value is within range
            let value = parseInt(this.value) || 0;
            value = Math.max(-3000, Math.min(3000, value));
            this.value = value;
            shiftSlider.value = value;
            updatePlot();
        });
        
        // Handle find optimal button click
        const findOptimalBtn = document.getElementById('find-optimal-shift');
        if (findOptimalBtn) {
            findOptimalBtn.addEventListener('click', function() {
                // Set shift input to 'AUTO' and trigger change
                updatePlot(true);
            });
        }
        
        // Also update on Enter key in text input
        shiftInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.dispatchEvent(new Event('change'));
            }
        });
    }

});