// Generic NL2SQL Frontend JavaScript

function displayResults(data) {
    const container = document.getElementById('results-container');
    let html = '';

    // Check if simple or complex query
    const isSimple = data.query_type === 'simple';
    
    if (isSimple) {
        // Simple query - single SQL, results, plot
        html += displaySimpleQuery(data);
    } else {
        // Complex query - multiple sub-queries
        html += displayComplexQuery(data);
    }

    container.innerHTML = html;

    // Render plots if any
    if (isSimple && data.plot) {
        renderPlot('plot-0', data.plot);
    } else if (!isSimple && data.sub_queries) {
        data.sub_queries.forEach((sq, index) => {
            if (sq.plot) {
                renderPlot(`plot-${index}`, sq.plot);
            }
        });
    }
}

function displaySimpleQuery(data) {
    let html = `
        <div class="execution-plan">
            <div class="execution-plan-title">
                📋 Query Result <span class="simple-badge">SIMPLE QUERY</span>
            </div>
            <p><strong>Question:</strong> ${data.question}</p>
        </div>
    `;

    html += '<div class="sub-query-result">';

    // Visualization
    if (data.plot) {
        html += `
            <div class="section">
                <h3>📊 Visualization</h3>
                <div id="plot-0" class="plot-container"></div>
            </div>
        `;
    }

    // SQL Query
    html += `
        <div class="section">
            <h3>🔍 Generated SQL Query</h3>
            <pre class="sql-query">${escapeHtml(data.sql)}</pre>
            ${data.reasoning ? `<p class="reasoning">${escapeHtml(data.reasoning)}</p>` : ''}
        </div>
    `;

    // Results Table
    html += `
        <div class="section">
            <h3>📋 Query Results (${data.results.length} rows)</h3>
    `;

    if (data.results && data.results.length > 0) {
        html += '<div class="results-table-container"><table class="results-table">';
        
        // Table header
        html += '<thead><tr>';
        const columns = data.columns || Object.keys(data.results[0]);
        columns.forEach(col => {
            html += `<th>${escapeHtml(col)}</th>`;
        });
        html += '</tr></thead>';

        // Table body
        html += '<tbody>';
        data.results.forEach(row => {
            html += '<tr>';
            columns.forEach(col => {
                const value = row[col];
                html += `<td>${formatValue(value)}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table></div>';
    } else {
        html += '<p class="no-results">No results found.</p>';
    }

    html += '</div>'; // Close section
    html += '</div>'; // Close sub-query-result

    return html;
}

function displayComplexQuery(data) {
    let html = `
        <div class="execution-plan">
            <div class="execution-plan-title">
                📋 Execution Plan <span class="complex-badge">COMPLEX QUERY</span>
            </div>
            <p><strong>Original Question:</strong> ${escapeHtml(data.question)}</p>
            <p><strong>Strategy:</strong> ${escapeHtml(data.plan.reasoning || 'Execute sub-queries in parallel')}</p>
            <p><strong>Sub-Queries:</strong> ${data.sub_queries.length}</p>
        </div>
    `;

    // Display each sub-query
    data.sub_queries.forEach((sq, index) => {
        html += `<div class="sub-query-result">`;
        
        // Sub-query header
        html += `
            <div class="sub-query-header">
                Sub-Query ${index + 1}: ${escapeHtml(sq.question)}
            </div>
        `;

        // Visualization
        if (sq.plot) {
            html += `
                <div class="section">
                    <h3>📊 Visualization</h3>
                    <div id="plot-${index}" class="plot-container"></div>
                </div>
            `;
        }

        // SQL Query
        html += `
            <div class="section">
                <h3>🔍 Generated SQL Query</h3>
                <pre class="sql-query">${escapeHtml(sq.sql)}</pre>
                ${sq.reasoning ? `<p class="reasoning">${escapeHtml(sq.reasoning)}</p>` : ''}
            </div>
        `;

        // Results Table
        html += `
            <div class="section">
                <h3>📋 Query Results (${sq.results.length} rows)</h3>
        `;

        if (sq.results && sq.results.length > 0) {
            html += '<div class="results-table-container"><table class="results-table">';
            
            // Table header
            html += '<thead><tr>';
            const columns = sq.columns || Object.keys(sq.results[0]);
            columns.forEach(col => {
                html += `<th>${escapeHtml(col)}</th>`;
            });
            html += '</tr></thead>';

            // Table body
            html += '<tbody>';
            sq.results.forEach(row => {
                html += '<tr>';
                columns.forEach(col => {
                    const value = row[col];
                    html += `<td>${formatValue(value)}</td>`;
                });
                html += '</tr>';
            });
            html += '</tbody></table></div>';
        } else {
            html += '<p class="no-results">No results found.</p>';
        }

        html += '</div>'; // Close section
        html += '</div>'; // Close sub-query-result
    });

    return html;
}

function renderPlot(elementId, plotData) {
    try {
        Plotly.newPlot(elementId, plotData.data, plotData.layout, {responsive: true});
    } catch (error) {
        console.error('Error rendering plot:', error);
        document.getElementById(elementId).innerHTML = '<p class="error">Failed to render visualization</p>';
    }
}

function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

function formatValue(value) {
    if (value === null || value === undefined) {
        return '<span class="null-value">NULL</span>';
    }
    if (typeof value === 'number') {
        if (Number.isInteger(value)) {
            return value.toLocaleString();
        } else {
            return value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }
    }
    return escapeHtml(value);
}

async function askQuestion() {
    const questionInput = document.getElementById('question-input');
    const question = questionInput.value.trim();

    if (!question) {
        alert('Please enter a question');
        return;
    }

    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results-container').innerHTML = '';

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        document.getElementById('results-container').innerHTML = `
            <div class="error-message">
                <h3>❌ Error</h3>
                <p>${error.message}</p>
            </div>
        `;
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

// Example button handlers
function setExample(question) {
    document.getElementById('question-input').value = question;
}

// Set question function (for onclick handlers)
function setQuestion(question) {
    document.getElementById('question-input').value = question;
    document.getElementById('question-input').focus();
}

// Enter key handler
document.addEventListener('DOMContentLoaded', function() {
    const questionInput = document.getElementById('question-input');
    if (questionInput) {
        questionInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                askQuestion();
            }
        });
    }
});
