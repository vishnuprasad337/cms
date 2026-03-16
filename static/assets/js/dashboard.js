// Dashboard JavaScript Module

// Initialize on document ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    
    // Load data from hidden div
    loadDashboardData();
    
    // Initialize charts
    initializeCharts();
    
    // Initialize today's overview
    initializeTodayOverview();
    
    // Start live time update
    startLiveTime();
    
    // Add animation classes
    addAnimations();
});

// ========== DATA LOADING ==========
function loadDashboardData() {
    const dataElement = document.getElementById('dashboard-data');
    if (!dataElement) return;
    
    window.dashboardData = {
        totalRooms: parseInt(dataElement.dataset.totalRooms) || 0,
        availableRooms: parseInt(dataElement.dataset.availableRooms) || 0,
        bookedRooms: parseInt(dataElement.dataset.bookedRooms) || 0,
        totalRevenue: parseFloat(dataElement.dataset.totalRevenue) || 0,
        overstayCount: parseInt(dataElement.dataset.overstayCount) || 0,
        chartLabels: JSON.parse(dataElement.dataset.chartLabels || '[]'),
        chartValues: JSON.parse(dataElement.dataset.chartValues || '[]')
    };
    
    console.log('Dashboard data loaded:', window.dashboardData);
}

// ========== CHART INITIALIZATION ==========
let bookingChart, distributionChart;

function initializeCharts() {
    initializeBookingChart();
    initializeDistributionChart();
}

function initializeBookingChart() {
    const chartElement = document.querySelector("#bookingChart");
    if (!chartElement) return;
    
    const data = window.dashboardData || {};
    const defaultLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const defaultValues = [4, 7, 5, 8, 6, 9, 7];
    
    const options = {
        series: [{
            name: "Bookings",
            data: data.chartValues && data.chartValues.length ? data.chartValues : defaultValues
        }],
        chart: {
            height: 350,
            type: "area",
            toolbar: { show: false },
            zoom: { enabled: false },
            animations: {
                enabled: true,
                easing: 'easeinout',
                speed: 800
            }
        },
        dataLabels: { enabled: false },
        stroke: { curve: 'smooth', width: 3 },
        colors: ['#3498db'],
        fill: {
            type: 'gradient',
            gradient: {
                shadeIntensity: 1,
                opacityFrom: 0.7,
                opacityTo: 0.3
            }
        },
        markers: { size: 5, hover: { size: 7 } },
        xaxis: {
            categories: data.chartLabels && data.chartLabels.length ? data.chartLabels : defaultLabels,
            labels: { style: { colors: '#64748b' } }
        },
        yaxis: {
            labels: { style: { colors: '#64748b' } }
        },
        grid: { borderColor: '#e2e8f0' },
        tooltip: {
            theme: 'light',
            y: {
                formatter: function(val) {
                    return val + ' bookings';
                }
            }
        }
    };

    bookingChart = new ApexCharts(chartElement, options);
    bookingChart.render();
}

function initializeDistributionChart() {
    const chartElement = document.querySelector("#distributionChart");
    if (!chartElement) return;
    
    const data = window.dashboardData || {};
    const available = data.availableRooms || 0;
    const booked = data.bookedRooms || 0;
    const overstay = data.overstayCount || 0;
    
    const options = {
        series: [available, booked, overstay],
        chart: {
            type: 'donut',
            height: 300,
            animations: {
                enabled: true,
                easing: 'easeinout',
                speed: 800
            }
        },
        labels: ['Available', 'Booked', 'Overstay'],
        colors: ['#2ecc71', '#e74c3c', '#f39c12'],
        legend: { show: false },
        responsive: [{
            breakpoint: 480,
            options: { chart: { width: 200 } }
        }],
        plotOptions: {
            pie: {
                donut: {
                    size: '70%',
                    labels: {
                        show: true,
                        total: {
                            show: true,
                            label: 'Total',
                            formatter: function(w) {
                                return data.totalRooms || 0;
                            }
                        }
                    }
                }
            }
        },
        tooltip: {
            y: {
                formatter: function(val) {
                    return val + ' rooms';
                }
            }
        }
    };

    distributionChart = new ApexCharts(chartElement, options);
    distributionChart.render();
    
    // Update legend
    updateDistributionLegend(available, booked, overstay);
}

function updateDistributionLegend(available, booked, overstay) {
    const legendContainer = document.getElementById('distributionLegend');
    if (!legendContainer) return;
    
    const total = available + booked + overstay;
    const availablePercent = total ? ((available / total) * 100).toFixed(1) : 0;
    const bookedPercent = total ? ((booked / total) * 100).toFixed(1) : 0;
    const overstayPercent = total ? ((overstay / total) * 100).toFixed(1) : 0;
    
    legendContainer.innerHTML = `
        <div class="distribution-legend">
            <div class="legend-item">
                <span>
                    <span class="legend-color" style="background: #2ecc71;"></span>
                    Available
                </span>
                <span class="fw-bold">${available} (${availablePercent}%)</span>
            </div>
            <div class="legend-item">
                <span>
                    <span class="legend-color" style="background: #e74c3c;"></span>
                    Booked
                </span>
                <span class="fw-bold">${booked} (${bookedPercent}%)</span>
            </div>
            <div class="legend-item">
                <span>
                    <span class="legend-color" style="background: #f39c12;"></span>
                    Overstay
                </span>
                <span class="fw-bold">${overstay} (${overstayPercent}%)</span>
            </div>
        </div>
    `;
}

// ========== CHART RANGE UPDATE ==========
function updateChartRange(days) {
    const dropdown = document.getElementById('chartRangeDropdown');
    if (dropdown) {
        dropdown.textContent = `Last ${days} Days`;
    }
    
    // Show loading state
    const chartContainer = document.querySelector("#bookingChart");
    chartContainer.classList.add('loading');
    
    // Simulate API call to fetch new data
    setTimeout(() => {
        // Generate random data for demo
        const newData = generateRandomData(days);
        
        bookingChart.updateSeries([{
            name: "Bookings",
            data: newData
        }]);
        
        chartContainer.classList.remove('loading');
    }, 1000);
}

function generateRandomData(days) {
    const data = [];
    for (let i = 0; i < days; i++) {
        data.push(Math.floor(Math.random() * 15) + 5);
    }
    return data;
}

// ========== TODAY'S OVERVIEW ==========
function initializeTodayOverview() {
    const container = document.getElementById('todayOverview');
    if (!container) return;
    
    // Generate random today's data for demo
    const todayData = {
        checkins: Math.floor(Math.random() * 10) + 2,
        checkouts: Math.floor(Math.random() * 8) + 1,
        revenue: (Math.random() * 50000 + 10000).toFixed(2),
        occupancy: Math.floor(Math.random() * 40) + 40
    };
    
    container.innerHTML = `
        <div class="col-6 mb-3">
            <div class="today-item">
                <small class="text-muted">Check-ins Today</small>
                <h3>${todayData.checkins}</h3>
            </div>
        </div>
        <div class="col-6 mb-3">
            <div class="today-item">
                <small class="text-muted">Check-outs Today</small>
                <h3>${todayData.checkouts}</h3>
            </div>
        </div>
        <div class="col-6">
            <div class="today-item">
                <small class="text-muted">Expected Revenue</small>
                <h3>₹${todayData.revenue}</h3>
            </div>
        </div>
        <div class="col-6">
            <div class="today-item">
                <small class="text-muted">Occupancy Rate</small>
                <h3>${todayData.occupancy}%</h3>
            </div>
        </div>
    `;
}

// ========== LIVE TIME UPDATE ==========
function startLiveTime() {
    updateTime();
    setInterval(updateTime, 1000);
}

function updateTime() {
    const timeElement = document.getElementById('liveTime');
    if (!timeElement) return;
    
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });
    timeElement.textContent = timeString;
}

// ========== NAVIGATION ==========
function navigateToSection(section) {
    console.log(`Navigating to ${section} section`);
    // Add your navigation logic here
    // For example: window.location.href = `/${section}`;
    
    // Show toast notification
    showNotification(`Navigating to ${section} section...`, 'info');
}

function generateReport() {
    console.log('Generating report...');
    
    // Show loading state
    const btn = event.target.closest('button');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="bx bx-loader-alt bx-spin me-2"></i>Generating...';
    btn.disabled = true;
    
    // Simulate report generation
    setTimeout(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
        
        // Show success message
        showNotification('Report generated successfully!', 'success');
    }, 2000);
}

// ========== NOTIFICATION SYSTEM ==========
function showNotification(message, type = 'info') {
    // Check if notification container exists
    let container = document.querySelector('.notification-container');
    
    if (!container) {
        container = document.createElement('div');
        container.className = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
        `;
        document.body.appendChild(container);
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.style.cssText = `
        margin-bottom: 10px;
        min-width: 300px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        animation: slideIn 0.3s ease;
    `;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    container.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
}

// ========== ANIMATIONS ==========
function addAnimations() {
    // Add fade-in animation to cards
    document.querySelectorAll('.card').forEach((card, index) => {
        card.style.animation = `fadeIn 0.5s ease ${index * 0.1}s both`;
    });
    
    // Add slide-in animation to quick stats
    document.querySelectorAll('.quick-stat-item').forEach((item, index) => {
        item.style.animation = `slideIn 0.3s ease ${index * 0.1}s both`;
    });
}

// ========== REFRESH DATA ==========
function refreshDashboard() {
    // Show loading state
    document.body.classList.add('loading');
    
    // Simulate API call
    setTimeout(() => {
        // Refresh charts with new random data
        const newBookingData = generateRandomData(7);
        bookingChart.updateSeries([{
            name: "Bookings",
            data: newBookingData
        }]);
        
        // Update today's overview
        initializeTodayOverview();
        
        // Remove loading state
        document.body.classList.remove('loading');
        
        // Show success message
        showNotification('Dashboard refreshed!', 'success');
    }, 1500);
}

// ========== EXPORT FUNCTIONS ==========
// Make functions globally available
window.showNotification = showNotification;
window.navigateToSection = navigateToSection;
window.generateReport = generateReport;
window.updateChartRange = updateChartRange;
window.refreshDashboard = refreshDashboard;