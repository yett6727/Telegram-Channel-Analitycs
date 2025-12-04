// Load data on page load
window.addEventListener('DOMContentLoaded', loadData);

async function loadData() {
    updateLastUpdate();
    await loadOverview();
    await loadDailyStats();
    await loadTopMessages();
    await loadGrowth();
}

function updateLastUpdate() {
    document.getElementById('last-update').textContent = new Date().toLocaleString();
}

async function loadOverview() {
    try {
        const response = await fetch('/api/overview');
        const data = await response.json();
        
        document.getElementById('channel-title').textContent = data.channel_title;
        document.getElementById('members-count').textContent = data.members_count.toLocaleString();
        document.getElementById('total-messages').textContent = data.total_messages.toLocaleString();
        document.getElementById('total-views').textContent = data.total_views.toLocaleString();
        document.getElementById('avg-views').textContent = data.avg_views.toLocaleString();
    } catch (error) {
        console.error('Error loading overview:', error);
    }
}

async function loadDailyStats() {
    try {
        const response = await fetch('/api/daily-stats');
        const data = await response.json();
        
        // Views chart
        const viewsTrace = {
            x: data.dates,
            y: data.views,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Total Views',
            line: {color: '#667eea', width: 3},
            marker: {size: 8}
        };
        
        const viewsLayout = {
            xaxis: {title: 'Date'},
            yaxis: {title: 'Views'},
            margin: {t: 20, r: 20, b: 50, l: 60}
        };
        
        Plotly.newPlot('views-chart', [viewsTrace], viewsLayout, {responsive: true});
        
        // Messages chart
        const messagesTrace = {
            x: data.dates,
            y: data.messages,
            type: 'bar',
            name: 'Posts',
            marker: {color: '#764ba2'}
        };
        
        const messagesLayout = {
            xaxis: {title: 'Date'},
            yaxis: {title: 'Number of Posts'},
            margin: {t: 20, r: 20, b: 50, l: 60}
        };
        
        Plotly.newPlot('messages-chart', [messagesTrace], messagesLayout, {responsive: true});
        
    } catch (error) {
        console.error('Error loading daily stats:', error);
    }
}

async function loadTopMessages() {
    try {
        const response = await fetch('/api/top-messages');
        const data = await response.json();
        
        const container = document.getElementById('top-messages');
        container.innerHTML = '';
        
        data.forEach((msg, index) => {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message-item';
            messageDiv.innerHTML = `
                <div class="message-text"><strong>#${index + 1}</strong> ${msg.text || 'No text'}</div>
                <div class="message-stats">
                    <span>👁️ ${msg.views.toLocaleString()} views</span>
                    <span>↗️ ${msg.forwards.toLocaleString()} forwards</span>
                    <span>💬 ${msg.replies.toLocaleString()} replies</span>
                    <span>📅 ${new Date(msg.date).toLocaleDateString()}</span>
                </div>
            `;
            container.appendChild(messageDiv);
        });
        
    } catch (error) {
        console.error('Error loading top messages:', error);
    }
}

async function loadGrowth() {
    try {
        const response = await fetch('/api/growth');
        const data = await response.json();
        
        if (data.timestamps.length === 0) {
            document.getElementById('growth-chart').innerHTML = '<p style="text-align: center; color: #666;">No growth data available yet. Data will appear after multiple collections.</p>';
            return;
        }
        
        const growthTrace = {
            x: data.timestamps,
            y: data.members,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Members',
            line: {color: '#10b981', width: 3},
            marker: {size: 8},
            fill: 'tozeroy',
            fillcolor: 'rgba(16, 185, 129, 0.1)'
        };
        
        const growthLayout = {
            xaxis: {title: 'Date'},
            yaxis: {title: 'Members'},
            margin: {t: 20, r: 20, b: 50, l: 60}
        };
        
        Plotly.newPlot('growth-chart', [growthTrace], growthLayout, {responsive: true});
        
    } catch (error) {
        console.error('Error loading growth data:', error);
    }
}