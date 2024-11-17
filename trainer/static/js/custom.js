document.addEventListener('DOMContentLoaded', () => {
    // Chart.js setup
    const ctx = document.getElementById('bmiWeightChart')?.getContext('2d');
    if (ctx) {
        const bmiWeightChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [], // Add your dates array here
                datasets: [
                    { label: 'Weight (kg)', data: [], borderColor: 'blue', fill: false },
                    { label: 'BMI', data: [], borderColor: 'green', fill: false }
                ]
            },
            options: { scales: { y: { beginAtZero: true } } }
        });
    }

    // Toggle button functionality
    document.addEventListener('htmx:afterOnLoad', function (event) {
        const button = event.target.closest('button');
        if (button) {
            const locationCard = button.closest('li');
            const details = locationCard.querySelector('.location-details');

            if (details.style.display === 'none') {
                button.innerText = 'Hide Details';
                details.style.display = 'block';
            } else {
                button.innerText = 'Show Details';
                details.style.display = 'none';
            }
        }
    });
});

// Smooth scroll to next div
window.scrollToNextDiv = function(button) {
    const nextDiv = button.closest('div').nextElementSibling;
    if (nextDiv) {
        nextDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
};
