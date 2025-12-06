// Map-Reduce NL2SQL Frontend JavaScript

function setQuestion(question) {
    document.getElementById('question-input').value = question;
    document.getElementById('question-input').focus();
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
        
        // Hide loading
        document.getElementById('loading').style.display = 'none';
        
        // Display results based on query type
        if (data.query_type === 'simple') {
            displaySimpleResult(data);
        } else if (data.query_type === 'complex') {
            displayComplexResult(data);
        } else {
            displayError('Unknown query type: ' + data.query_type);
        }
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loading').style.display = 'none';
        displayError(error.message);
    }
}

function displaySimpleResult(data) {
    const container = document.getElementById('results-container');
    
    let html = `
        <div class="result-card">
            <div class="result-header">
                <h2>📊 Query Result</h2>
                <span class="badge badge-simple">SIMPLE QUERY</span>
            </div>
            
            <div class="result-content">
                <p><strong>Question:</strong> ${escapeHtml(data.question)}</p>
    `;
    
    // Visualization (if applicable)
    if (data.should_visualize && data.plot) {
        html += `
            <div class="visualization-section">
                <h3>📊 Visualization</h3>
                <p class="viz-reason"><em>${escapeHtml(data.viz_reason)}</em></p>
                <div id="plot-simple"></div>
            </div>
        `;
    } else if (!data.should_visualize) {
        html += `
            <div class="no-viz-section">
                <p class="viz-reason">💡 <strong>No visualization:</strong> ${escapeHtml(data.viz_reason)}</p>
            </div>
        `;
    }
    
    // SQL Query
    html += `
                <div class="sql-section">
                    <h3>🔍 Generated SQL Query</h3>
                    <pre><code>${escapeHtml(data.sql)}</code></pre>
                    <p class="reasoning">${escapeHtml(data.reasoning)}</p>
                </div>
    `;
    
    // Results Table
    if (data.results && data.results.length > 0) {
        html += `
                <div class="results-table-section">
                    <h3>📋 Query Results (${data.results.length} rows)</h3>
                    ${generateTable(data.results, data.columns)}
                </div>
        `;
    } else {
        html += `<p class="no-results">No results returned</p>`;
    }
    
    html += `
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Render plot if applicable
    if (data.should_visualize && data.plot) {
        Plotly.newPlot('plot-simple', data.plot.data, data.plot.layout, {responsive: true});
    }
}

function displayComplexResult(data) {
    const container = document.getElementById('results-container');
    
    let html = `
        <div class="result-card">
            <div class="result-header">
                <h2>📊 Query Result</h2>
                <span class="badge badge-complex">COMPLEX QUERY</span>
            </div>
            
            <div class="result-content">
                <p><strong>Original Question:</strong> ${escapeHtml(data.original_question)}</p>
                
                <!-- Unified Answer Section -->
                <div class="unified-answer-section">
                    <h3>✨ Unified Answer</h3>
                    <p class="unified-answer">${escapeHtml(data.unified_answer)}</p>
                </div>
                
                <!-- Key Insights Section -->
                <div class="insights-section">
                    <h3>💡 Key Insights</h3>
                    <ul class="insights-list">
                        ${data.insights.map(insight => `<li>${escapeHtml(insight)}</li>`).join('')}
                    </ul>
                </div>
                
                <!-- Execution Plan -->
                <div class="execution-plan">
                    <h3>📋 Execution Plan</h3>
                    <p>${escapeHtml(data.execution_plan)}</p>
                    <p><strong>Sub-Queries:</strong> ${data.sub_queries.length}</p>
                </div>
                
                <!-- Sub-Queries -->
                <div class="sub-queries-section">
                    <h3>🔍 Sub-Query Details</h3>
    `;
    
    data.sub_queries.forEach((sq, index) => {
        html += `
                    <div class="sub-query-card">
                        <h4>Sub-Query ${index + 1}: ${escapeHtml(sq.question)}</h4>
        `;
        
        // Visualization for this sub-query
        if (sq.should_visualize && sq.plot) {
            html += `
                        <div class="visualization-section">
                            <p class="viz-reason"><em>${escapeHtml(sq.viz_reason)}</em></p>
                            <div id="plot-sub-${index}"></div>
                        </div>
            `;
        } else if (!sq.should_visualize) {
            html += `
                        <p class="viz-reason">💡 <strong>No visualization:</strong> ${escapeHtml(sq.viz_reason)}</p>
            `;
        }
        
        // SQL
        html += `
                        <div class="sql-section">
                            <strong>SQL:</strong>
                            <pre><code>${escapeHtml(sq.sql)}</code></pre>
                            <p class="reasoning">${escapeHtml(sq.reasoning)}</p>
                        </div>
        `;
        
        // Results
        if (sq.results && sq.results.length > 0) {
            html += `
                        <div class="results-table-section">
                            <strong>Results (${sq.results.length} rows):</strong>
                            ${generateTable(sq.results, sq.columns)}
                        </div>
            `;
        }
        
        html += `
                    </div>
        `;
    });
    
    html += `
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Render plots for sub-queries
    data.sub_queries.forEach((sq, index) => {
        if (sq.should_visualize && sq.plot) {
            Plotly.newPlot(`plot-sub-${index}`, sq.plot.data, sq.plot.layout, {responsive: true});
        }
    });
}

function generateTable(results, columns) {
    if (!results || results.length === 0) {
        return '<p>No results</p>';
    }
    
    let html = '<table><thead><tr>';
    
    // Header
    columns.forEach(col => {
        html += `<th>${escapeHtml(col)}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    // Rows
    results.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            const value = row[col];
            const formatted = typeof value === 'number' ? value.toLocaleString() : (value || '');
            html += `<td>${escapeHtml(String(formatted))}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    return html;
}

function displayError(message) {
    const container = document.getElementById('results-container');
    container.innerHTML = `
        <div class="error-card">
            <h3>❌ Error</h3>
            <p>${escapeHtml(message)}</p>
        </div>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Allow Enter key to submit
document.getElementById('question-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        askQuestion();
    }
});
