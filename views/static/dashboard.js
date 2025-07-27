function showSection(id, btn) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
}
// Copium Fix lol to enable 'windows' 
function showSection(id, btn) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));

    document.getElementById(id).classList.add('active');
    btn.classList.add('active');

    const windows = ['overview_window', 'visuals_window'];
    windows.forEach(w => {
        const el = document.querySelector(`.${w}`);
        if (el) el.style.display = 'none';
    });

    const targetWindow = document.querySelector(`.${id}_window`);
    if (targetWindow) targetWindow.style.display = 'flex';
}

document.addEventListener('DOMContentLoaded', () => {
    // hide all windows
    const windows = ['overview_window', 'visuals_window', 'models_window', 'dataset_window'];
    windows.forEach(w => {
        const el = document.querySelector(`.${w}`);
        if (el) el.style.display = 'none';
    });

    const defaultWindow = document.querySelector('.overview_window');
    if (defaultWindow) defaultWindow.style.display = 'flex';
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById('overview')?.classList.add('active');

    document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
    document.querySelector('.nav button[onclick*="overview"]')?.classList.add('active');

    // Get Overview Data
    fetch("/api/dashboard_stats")
        .then(response => response.json())
        .then(data => {
            document.getElementById("totalPatients").textContent = data.totalPatients;
            document.getElementById("tbCases").textContent = data.tbCases;
            document.getElementById("accuracy").textContent = data.accuracy;
        })
        .catch(error => console.error('Failed to fetch dashboard stats:', error));
});

function showSection(id, btn) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));

    document.getElementById(id).classList.add('active');
    btn.classList.add('active');

    const windows = ['overview_window', 'visuals_window', 'models_window', 'dataset_window'];
    windows.forEach(w => {
        const el = document.querySelector(`.${w}`);
        if (el) el.style.display = 'none';
    });

    const targetWindow = document.querySelector(`.${id}_window`);
    if (targetWindow) targetWindow.style.display = 'flex';
}

/* Visualization */
document.addEventListener('DOMContentLoaded', () => {
    const windows = ['overview_window', 'visuals_window', 'models_window', 'dataset_window'];
    windows.forEach(w => {
        const el = document.querySelector(`.${w}`);
        if (el) el.style.display = 'none';
    });

    const defaultWindow = document.querySelector('.overview_window');
    if (defaultWindow) defaultWindow.style.display = 'flex';
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById('overview')?.classList.add('active');

    document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
    document.querySelector('.nav button[onclick*="overview"]')?.classList.add('active');

    // Fetch Dashboard Stats
    fetch("/api/dashboard_stats")
        .then(response => response.json())
        .then(data => {
            document.getElementById("totalPatients").textContent = data.totalPatients;
            document.getElementById("tbCases").textContent = data.tbCases;
            document.getElementById("accuracy").textContent = data.accuracy;
        })
        .catch(error => console.error('Failed to fetch dashboard stats:', error));

    // Fetch TB Assessment Data
    fetch('/api/assessment_data')
        .then(response => response.json())
        .then(data => {
            let tbCount = 0;
            let nonTbCount = 0;
            let maleCount = 0;
            let femaleCount = 0;
            let dateTrendChart; // For global chart instance reuse

            const ageGroups = {};
            const tbAgeValues = [];
            const nonTbAgeValues = [];

            const symptomFields = ['cough', 'cold', 'fever', 'dizziness', 'chestpain', 'jointpain', 'napepain', 'backpain', 'lossap', 'sputum'];
            const systemFields = ['circulatory_system', 'digestive_system', 'endocrine', 'eye_and_adnexa', 'genitourinary_system', 'infectious_and_parasitic', 'mental', 'musculoskeletal_system', 'nervous_system', 'pregnancy', 'respiratory_system', 'skin'];

            const symptomCounts = {};
            const systemCounts = {};

            const tbDateCounts = {};

            const groupByDateRange = (records, range) => {
                const groups = {};

                records.forEach(record => {
                    if (record.tuberculosis === 1 && record.assessment_date) {
                        const date = new Date(record.assessment_date);
                        let key = '';

                        if (range === 'day') {
                            key = date.toISOString().split('T')[0];
                        } else if (range === 'week') {
                            const year = date.getFullYear();
                            const oneJan = new Date(date.getFullYear(), 0, 1);
                            const week = Math.ceil((((date - oneJan) / 86400000) + oneJan.getDay() + 1) / 7);
                            key = `${year}-W${week.toString().padStart(2, '0')}`;
                        } else if (range === 'year') {
                            key = date.getFullYear().toString();
                        }

                        groups[key] = (groups[key] || 0) + 1;
                    }
                });

                const sortedKeys = Object.keys(groups).sort();
                const counts = sortedKeys.map(k => groups[k]);

                return { labels: sortedKeys, data: counts };
            };

            const renderDateTrendChart = (range = 'day') => {
                const { labels, data: counts } = groupByDateRange(data, range);

                if (dateTrendChart) dateTrendChart.destroy(); // Remove old chart

                dateTrendChart = new Chart(document.getElementById('dateTrendChart'), {
                    type: 'line',
                    data: {
                        labels,
                        datasets: [{
                            label: `TB Admissions per ${range}`,
                            data: counts,
                            borderColor: '#007bff',
                            backgroundColor: 'rgba(0,123,255,0.1)',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: { display: true, text: 'Cases' }
                            },
                            x: {
                                title: { display: true, text: `${range.charAt(0).toUpperCase() + range.slice(1)}` }
                            }
                        },
                        plugins: {
                            legend: { position: 'top' },
                            tooltip: { mode: 'index', intersect: false }
                        }
                    }
                });
            };

            renderDateTrendChart();

            // Change event
            document.getElementById('dateRangeSelect').addEventListener('change', (e) => {
                renderDateTrendChart(e.target.value);
            });

            symptomFields.forEach(symptom => symptomCounts[symptom] = 0);
            systemFields.forEach(system => systemCounts[system] = 0);

            data.forEach(record => {
                const age = record.age;

                if (record.tuberculosis === 1 && record.assessment_date) {
                    const date = new Date(record.assessment_date).toISOString().split('T')[0]; // format: YYYY-MM-DD
                    tbDateCounts[date] = (tbDateCounts[date] || 0) + 1;
                }
                if (record.tuberculosis === 1) {
                    tbCount++;
                    if (record.gender?.toLowerCase() === 'male') maleCount++;
                    else if (record.gender?.toLowerCase() === 'female') femaleCount++;

                    if (age !== null) {
                        const group = Math.floor(age / 10) * 10 + 's';
                        ageGroups[group] = (ageGroups[group] || 0) + 1;
                        tbAgeValues.push(age);
                    }

                    symptomFields.forEach(symptom => {
                        if (record[symptom] === 1) symptomCounts[symptom]++;
                    });

                    systemFields.forEach(system => {
                        if (record[system] === 1) systemCounts[system]++;
                    });
                } else {
                    nonTbCount++;
                    if (age !== null) nonTbAgeValues.push(age);
                }
            });

            // Pie: TB vs Non-TB
            new Chart(document.getElementById('tbChart'), {
                type: 'pie',
                data: {
                    labels: ['TB Positive', 'Non-TB'],
                    datasets: [{
                        data: [tbCount, nonTbCount],
                        backgroundColor: ['#ff6384', '#36a2eb']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                generateLabels: function(chart) {
                                    const data = chart.data;
                                    return data.labels.map((label, i) => {
                                        const value = data.datasets[0].data[i];
                                        return {
                                            text: `${label} (${value})`,
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            strokeStyle: data.datasets[0].backgroundColor[i],
                                            index: i
                                        };
                                    });
                                }
                            }
                        }
                    }
                }
            });
            document.getElementById('tbChartDetails').innerText = '';

            // Pie: Gender
            new Chart(document.getElementById('genderChart'), {
                type: 'pie',
                data: {
                    labels: ['Male', 'Female'],
                    datasets: [{
                        data: [maleCount, femaleCount],
                        backgroundColor: ['#ff6384', '#36a2eb']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                generateLabels: function(chart) {
                                    const data = chart.data;
                                    return data.labels.map((label, i) => {
                                        const value = data.datasets[0].data[i];
                                        return {
                                            text: `${label} (${value})`,
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            strokeStyle: data.datasets[0].backgroundColor[i],
                                            index: i
                                        };
                                    });
                                }
                            }
                        }
                    }
                }
            });
            document.getElementById('genderChartDetails').innerText = '';

            // Bar: Age Distribution
            new Chart(document.getElementById('ageChart'), {
                type: 'bar',
                data: {
                    labels: Object.keys(ageGroups),
                    datasets: [{ label: 'TB Cases', data: Object.values(ageGroups), backgroundColor: '#ff6384' }]
                },
                options: { responsive: true, scales: { y: { beginAtZero: true } } }
            });

            // Bar: Symptoms
            new Chart(document.getElementById('symptomChart'), {
                type: 'bar',
                data: {
                    labels: symptomFields.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
                    datasets: [{ label: 'Reported in TB Cases', data: Object.values(symptomCounts), backgroundColor: '#e9c604ff' }]
                },
                options: { responsive: true, scales: { y: { beginAtZero: true } } }
            });

            // Bar: Systems
            new Chart(document.getElementById('systemChart'), {
                type: 'bar',
                data: {
                    labels: systemFields.map(s => s.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())),
                    datasets: [{ label: 'TB Involvement', data: Object.values(systemCounts), backgroundColor: '#ff6384' }]
                },
                options: { responsive: true, scales: { y: { beginAtZero: true } } }
            });

            // Line: Age vs TB Likelihood
            const ageRanges = [...Array(10).keys()].map(i => `${i * 10}-${i * 10 + 9}`);
            const tbAgeDist = Array(10).fill(0);
            const nonTbAgeDist = Array(10).fill(0);

            tbAgeValues.forEach(age => { if (age < 100) tbAgeDist[Math.floor(age / 10)]++; });
            nonTbAgeValues.forEach(age => { if (age < 100) nonTbAgeDist[Math.floor(age / 10)]++; });

            const tbLikelihood = tbAgeDist.map((tb, i) => {
                const total = tb + nonTbAgeDist[i];
                return total === 0 ? 0 : (tb / total) * 100;
            });

            new Chart(document.getElementById('ageVsTBChart'), {
                type: 'line',
                data: {
                    labels: ageRanges,
                    datasets: [{
                        label: 'TB Likelihood (%)',
                        data: tbLikelihood,
                        backgroundColor: '#0596683d',
                        borderColor: '#059669',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } }
            });

            const sortedDates = Object.keys(tbDateCounts).sort();
            const countsByDate = sortedDates.map(date => tbDateCounts[date]);

            new Chart(document.getElementById('dateTrendChart'), {
                type: 'line',
                data: {
                    labels: sortedDates,
                    datasets: [{
                        label: 'TB Admissions',
                        data: countsByDate,
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0,123,255,0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: { display: true, text: 'Number of TB Cases' }
                        },
                        x: {
                            title: { display: true, text: 'Date' }
                        }
                    },
                    plugins: {
                        legend: { position: 'top' },
                        tooltip: { mode: 'index', intersect: false }
                    }
                }
            });

        })
        .catch(error => console.error('Error fetching assessment data:', error));
});