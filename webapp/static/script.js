// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadSchema();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Form submission
    document.getElementById('queryForm').addEventListener('submit', handleQuerySubmit);
    
    // Example button clicks
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            document.getElementById('questionInput').value = question;
            handleQuerySubmit(new Event('submit'));
        });
    });
}

// Handle query form submission
async function handleQuerySubmit(e) {
    e.preventDefault();
    
    const question = document.getElementById('questionInput').value.trim();
    if (!question) return;
    
    // Show loading state
    setLoading(true);
    hideResults();
    hideError();
    
    try {
        const formData = new FormData();
        formData.append('question', question);
        
        const response = await fetch('/query', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            displayError(data.error);
        }
    } catch (error) {
        displayError('Failed to execute query: ' + error.message);
    } finally {
        setLoading(false);
    }
}

// Display query results
function displayResults(data) {
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
    
    // Display question
    document.getElementById('resultQuestion').textContent = data.question;
    
    // Display SQL
    document.getElementById('resultSQL').textContent = data.sql;
    
    // Display reasoning
    document.getElementById('resultReasoning').textContent = data.reasoning;
    
    // Display data results
    const resultData = document.getElementById('resultData');
    if (data.results && data.results.length > 0) {
        resultData.innerHTML = createTable(data.results);
    } else {
        resultData.innerHTML = '<p>No results found.</p>';
    }
    
    // Display metadata
    const metadataHtml = `
        <div class="metadata-item">
            <span class="metadata-label">Relevant Tables:</span> 
            ${data.metadata.relevant_tables.join(', ')}
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Example Queries Used:</span> 
            ${data.metadata.example_queries_used}
        </div>
    `;
    document.getElementById('resultMetadata').innerHTML = metadataHtml;
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

// Create HTML table from results
function createTable(results) {
    if (!results || results.length === 0) {
        return '<p>No data to display.</p>';
    }
    
    const keys = Object.keys(results[0]);
    
    let html = '<table>';
    
    // Header
    html += '<thead><tr>';
    keys.forEach(key => {
        html += `<th>${escapeHtml(key)}</th>`;
    });
    html += '</tr></thead>';
    
    // Body
    html += '<tbody>';
    results.forEach(row => {
        html += '<tr>';
        keys.forEach(key => {
            const value = row[key];
            html += `<td>${escapeHtml(String(value))}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody>';
    
    html += '</table>';
    return html;
}

// Display error message
function displayError(message) {
    document.getElementById('errorSection').style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorSection').scrollIntoView({ behavior: 'smooth' });
}

// Hide results
function hideResults() {
    document.getElementById('resultsSection').style.display = 'none';
}

// Hide error
function hideError() {
    document.getElementById('errorSection').style.display = 'none';
}

// Set loading state
function setLoading(isLoading) {
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    
    if (isLoading) {
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-block';
    } else {
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// Load database statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('totalCustomers').textContent = 
                formatNumber(data.stats.total_customers);
            document.getElementById('activeSubscriptions').textContent = 
                formatNumber(data.stats.active_subscriptions);
            document.getElementById('churnedSubscriptions').textContent = 
                formatNumber(data.stats.churned_subscriptions);
            document.getElementById('totalRevenue').textContent = 
                formatNumber(data.stats.total_revenue);
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Load database schema
async function loadSchema() {
    try {
        const response = await fetch('/api/tables');
        const data = await response.json();
        
        if (data.success) {
            displaySchema(data.tables);
        }
    } catch (error) {
        console.error('Failed to load schema:', error);
        document.getElementById('schemaContainer').innerHTML = 
            '<p class="error">Failed to load schema.</p>';
    }
}

// Display database schema
function displaySchema(tables) {
    const container = document.getElementById('schemaContainer');
    container.innerHTML = '';
    
    tables.forEach(table => {
        const tableDiv = document.createElement('div');
        tableDiv.className = 'table-schema';
        
        let html = `<h3>${table.name}</h3>`;
        html += '<ul class="column-list">';
        
        table.columns.forEach(col => {
            html += `
                <li>
                    <span class="column-name">${col.name}</span>
                    <span class="column-type">(${col.type})</span>
                    ${col.primary_key ? '<span class="badge">PK</span>' : ''}
                    ${col.not_null ? '<span class="badge">NOT NULL</span>' : ''}
                </li>
            `;
        });
        
        html += '</ul>';
        
        // Add sample data
        if (table.sample_data && table.sample_data.length > 0) {
            html += '<h4>Sample Data:</h4>';
            html += createTable(table.sample_data);
        }
        
        tableDiv.innerHTML = html;
        container.appendChild(tableDiv);
    });
}

// Utility functions
function formatNumber(num) {
    if (num === undefined || num === null) return '-';
    return num.toLocaleString();
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
