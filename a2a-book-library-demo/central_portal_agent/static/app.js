// Indian University Library Federation - Frontend App
// Educational Flow Visualization

// Check library status on load
document.addEventListener('DOMContentLoaded', async () => {
    await checkLibraryStatus();

    // Add enter key listener to search input
    document.getElementById('search-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
});

// Check status of connected libraries
async function checkLibraryStatus() {
    try {
        const response = await fetch('/libraries');
        const libraries = await response.json();

        libraries.forEach(lib => {
            if (lib.name.includes('Delhi')) {
                updateLibraryStatus('iit-delhi', lib.status === 'online');
            } else if (lib.name.includes('Bombay')) {
                updateLibraryStatus('iit-bombay', lib.status === 'online');
            }
        });
    } catch (error) {
        console.error('Failed to check library status:', error);
    }
}

function updateLibraryStatus(libraryId, isOnline) {
    const statusEl = document.getElementById(`${libraryId}-status`);
    const dot = statusEl.querySelector('.status-dot');
    const text = statusEl.querySelector('.status-text');

    dot.className = `status-dot ${isOnline ? 'online' : 'offline'}`;
    text.textContent = isOnline ? 'Online' : 'Offline';
}

// Quick search handler
function quickSearch(query) {
    document.getElementById('search-input').value = query;
    performSearch();
}

// Flow Log Functions
function addLog(message, type = 'info') {
    const logEl = document.getElementById('flow-log');
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });

    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.innerHTML = `
        <span class="log-time">${time}</span>
        <span class="log-msg">${message}</span>
    `;

    logEl.appendChild(entry);
    logEl.scrollTop = logEl.scrollHeight;
}

function clearFlowLog() {
    const logEl = document.getElementById('flow-log');
    logEl.innerHTML = `
        <div class="log-entry info">
            <span class="log-time">--:--:--</span>
            <span class="log-msg">Log cleared. Enter a search query to see the AI-powered A2A flow!</span>
        </div>
    `;
}

// Update the current step indicator
function setCurrentStep(stepNum, label) {
    document.getElementById('current-step').textContent = stepNum;
    document.getElementById('current-step-label').textContent = label;
}

// Reset all visual states
function resetVisualStates() {
    // Reset nodes
    document.getElementById('user-node').classList.remove('active');
    document.getElementById('portal-node').parentElement.classList.remove('active', 'complete');
    document.getElementById('iit-delhi-node').classList.remove('active', 'searching', 'complete');
    document.getElementById('iit-bombay-node').classList.remove('active', 'searching', 'complete');

    // Reset connection lines
    document.getElementById('line-user').classList.remove('active');
    document.getElementById('line-delhi').classList.remove('active');
    document.getElementById('line-bombay').classList.remove('active');

    // Reset packets
    document.querySelectorAll('.data-packet').forEach(p => {
        p.classList.remove('animate-out', 'animate-in');
    });

    // Reset action labels
    document.getElementById('delhi-action').textContent = '';
    document.getElementById('bombay-action').textContent = '';
    document.getElementById('portal-action').textContent = '';
}

// Helper function for delays
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Main search function with animated flow
async function performSearch() {
    const query = document.getElementById('search-input').value.trim();
    if (!query) {
        alert('Please enter a search term');
        return;
    }

    // Disable search button
    const searchBtn = document.getElementById('search-btn');
    searchBtn.disabled = true;

    // Reset visual states
    resetVisualStates();
    document.getElementById('results-section').classList.remove('visible');

    try {
        // ============================================
        // STEP 1: User initiates search
        // ============================================
        setCurrentStep(1, `User searches for "${query}"`);
        addLog(`STEP 1: User initiates search for "${query}"`, 'step1');

        document.getElementById('user-node').classList.add('active');
        await delay(500);

        // Animate packet going up from user
        document.getElementById('line-user').classList.add('active');
        document.getElementById('packet-user-out').classList.add('animate-out');
        addLog(`→ Request sent to Central Portal (POST /api/search)`, 'step1');
        await delay(600);

        // ============================================
        // STEP 2: Central Portal receives request
        // ============================================
        setCurrentStep(2, 'Central Portal processing request');
        addLog(`STEP 2: Central Portal receives request`, 'step2');

        document.getElementById('user-node').classList.remove('active');
        document.getElementById('portal-node').parentElement.classList.add('active');
        document.getElementById('portal-action').textContent = 'Processing...';
        await delay(400);

        addLog(`→ Portal identifies connected libraries: IIT Delhi, IIT Bombay`, 'step2');
        addLog(`→ Preparing parallel requests to both libraries...`, 'step2');
        await delay(400);

        // ============================================
        // STEP 3: Fan out to libraries (parallel)
        // ============================================
        setCurrentStep(3, 'Querying libraries in parallel');
        addLog(`STEP 3: Sending parallel requests to libraries`, 'step3');

        // Activate both connection lines
        document.getElementById('line-delhi').classList.add('active');
        document.getElementById('line-bombay').classList.add('active');

        // Send packets to both libraries
        document.getElementById('packet-delhi-out').classList.add('animate-out');
        document.getElementById('packet-bombay-out').classList.add('animate-out');

        addLog(`→ POST http://localhost:8003/api/search (IIT Delhi)`, 'step3');
        addLog(`→ POST http://localhost:8004/api/search (IIT Bombay)`, 'step3');
        await delay(700);

        // Libraries start AI processing
        document.getElementById('iit-delhi-node').classList.add('active', 'searching');
        document.getElementById('iit-bombay-node').classList.add('active', 'searching');
        document.getElementById('delhi-action').textContent = 'AI Processing...';
        document.getElementById('bombay-action').textContent = 'AI Processing...';
        document.getElementById('portal-action').textContent = 'Waiting for AI responses...';

        addLog(`→ IIT Delhi: AI analyzing query "${query}"`, 'step3');
        addLog(`→ IIT Bombay: AI analyzing query "${query}"`, 'step3');
        await delay(400);

        addLog(`→ IIT Delhi: AI calling search_catalog tool...`, 'step3');
        addLog(`→ IIT Bombay: AI calling search_catalog tool...`, 'step3');
        document.getElementById('delhi-action').textContent = 'Searching catalog...';
        document.getElementById('bombay-action').textContent = 'Searching catalog...';

        // ============================================
        // ACTUAL API CALL
        // ============================================
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        const data = await response.json();

        // ============================================
        // STEP 4: AI generates responses
        // ============================================
        setCurrentStep(4, 'AI generating responses');
        addLog(`STEP 4: AI generates responses from search results`, 'step4');
        addLog(`→ IIT Delhi: AI formatting response...`, 'step4');
        addLog(`→ IIT Bombay: AI formatting response...`, 'step4');

        // Clear outgoing packets
        document.getElementById('packet-delhi-out').classList.remove('animate-out');
        document.getElementById('packet-bombay-out').classList.remove('animate-out');

        // Get result counts
        const delhiResult = data.results.find(r => r.library.includes('Delhi'));
        const bombayResult = data.results.find(r => r.library.includes('Bombay'));
        const delhiCount = delhiResult?.books?.length || 0;
        const bombayCount = bombayResult?.books?.length || 0;

        // Animate response packets
        document.getElementById('packet-delhi-in').classList.add('animate-in');
        document.getElementById('packet-bombay-in').classList.add('animate-in');

        // Update library statuses
        document.getElementById('iit-delhi-node').classList.remove('searching');
        document.getElementById('iit-delhi-node').classList.add('complete');
        document.getElementById('delhi-action').textContent = `Found ${delhiCount} books`;

        document.getElementById('iit-bombay-node').classList.remove('searching');
        document.getElementById('iit-bombay-node').classList.add('complete');
        document.getElementById('bombay-action').textContent = `Found ${bombayCount} books`;

        addLog(`← IIT Delhi responds: ${delhiCount} book(s) found`, 'step4');
        addLog(`← IIT Bombay responds: ${bombayCount} book(s) found`, 'step4');
        await delay(700);

        // ============================================
        // STEP 5: Portal aggregates and responds to user
        // ============================================
        setCurrentStep(5, 'Portal sends aggregated results to user');
        addLog(`STEP 5: Portal aggregates results`, 'step5');

        document.getElementById('portal-node').parentElement.classList.remove('active');
        document.getElementById('portal-node').parentElement.classList.add('complete');
        document.getElementById('portal-action').textContent = `Total: ${delhiCount + bombayCount} books`;

        // Clear incoming packets
        document.getElementById('packet-delhi-in').classList.remove('animate-in');
        document.getElementById('packet-bombay-in').classList.remove('animate-in');

        // Send response back to user
        document.getElementById('packet-user-in').classList.add('animate-in');
        addLog(`← Sending aggregated response to user`, 'step5');
        await delay(600);

        // Complete!
        addLog(`✓ Search complete! Found ${delhiCount + bombayCount} total books`, 'success');

        // Display results
        displayResults(data);

        // Final state
        setCurrentStep('✓', `Found ${delhiCount + bombayCount} books across 2 libraries`);

    } catch (error) {
        console.error('Search failed:', error);
        addLog(`✗ Error: ${error.message}`, 'error');
        setCurrentStep('!', 'Search failed');
        alert('Search failed. Please make sure all services are running.');
    } finally {
        searchBtn.disabled = false;
    }
}

function displayResults(data) {
    const resultsSection = document.getElementById('results-section');
    resultsSection.classList.add('visible');

    // Find results for each library
    const delhiResult = data.results.find(r => r.library.includes('Delhi'));
    const bombayResult = data.results.find(r => r.library.includes('Bombay'));

    // Display Delhi results
    displayLibraryBooks('delhi', delhiResult);

    // Display Bombay results
    displayLibraryBooks('bombay', bombayResult);

    // Update total count
    const delhiCount = delhiResult?.books?.length || 0;
    const bombayCount = bombayResult?.books?.length || 0;
    const totalBooks = delhiCount + bombayCount;

    document.getElementById('results-count').textContent =
        `Found ${totalBooks} book(s) across ${data.libraries_queried} libraries`;
}

function displayLibraryBooks(libraryId, result) {
    const booksListEl = document.getElementById(`${libraryId}-books`);
    const countEl = document.getElementById(`${libraryId}-count`);

    // Handle missing result
    if (!result) {
        countEl.textContent = '0 book(s)';
        booksListEl.innerHTML = `
            <div class="no-results">
                <p>Library not available</p>
            </div>
        `;
        return;
    }

    // Handle errors
    if (!result.success) {
        countEl.textContent = '0 book(s)';
        booksListEl.innerHTML = `
            <div class="no-results error">
                <p>Error connecting to library</p>
                <p class="error-detail">${escapeHtml(result.error || 'Unknown error')}</p>
            </div>
        `;
        return;
    }

    const books = result.books || [];
    countEl.textContent = `${books.length} book(s)`;

    // Handle no results
    if (books.length === 0) {
        booksListEl.innerHTML = `
            <div class="no-results">
                <p>No matching books found in this library</p>
            </div>
        `;
        return;
    }

    // Display books
    booksListEl.innerHTML = books.map(book => `
        <div class="book-card">
            <div class="book-title">${escapeHtml(book.title)}</div>
            <div class="book-author">by ${escapeHtml(book.author)}</div>
            <div class="book-meta">
                <span>${escapeHtml(book.genre)}</span>
                <span>${book.year}</span>
                <span class="availability ${book.available_copies > 0 ? 'available' : 'unavailable'}">
                    ${book.available_copies > 0 ? 'Available' : 'Checked Out'}
                    (${book.available_copies}/${book.total_copies})
                </span>
            </div>
        </div>
    `).join('');
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
