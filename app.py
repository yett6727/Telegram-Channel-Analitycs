from flask import Flask, render_template, jsonify
from database import Database
import config
from datetime import datetime

app = Flask(__name__)
db = Database(config.DATABASE_PATH)

@app.route('/')
def index():
    '''Render main page'''
    return render_template('index.html')

@app.route('/api/overview')
def get_overview():
    '''Get overview statistics'''
    stats = db.get_overview_stats()
    return jsonify(stats)

@app.route('/api/greeting')
def get_greeting():
    '''Get greeting with channel name'''
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    stats = db.get_overview_stats()
    channel_name = config.CHANNEL_USERNAME
    
    return jsonify({
        'greeting': greeting,
        'channel_name': channel_name
    })

@app.route('/api/daily-stats')
def get_daily_stats():
    '''Get daily statistics for charts'''
    stats = db.get_recent_stats(days=30)
    
    data = {
        'dates': [row[0] for row in reversed(stats)],
        'messages': [row[1] for row in reversed(stats)],
        'views': [row[2] for row in reversed(stats)],
        'forwards': [row[3] for row in reversed(stats)],
        'avg_views': [row[4] for row in reversed(stats)]
    }
    
    return jsonify(data)

@app.route('/api/weekly-stats')
def get_weekly_stats():
    '''Get last 7 days statistics'''
    stats = db.get_recent_stats(days=7)
    
    data = {
        'dates': [row[0] for row in reversed(stats)],
        'members': [0] * len(stats)  # Will be filled by growth data
    }
    
    # Get growth data
    growth = db.get_channel_growth()
    if growth:
        # Match dates with member counts
        growth_dict = {row[0]: row[1] for row in growth}
        data['members'] = [growth_dict.get(date, 0) for date in data['dates']]
    
    return jsonify(data)

@app.route('/api/top-messages')
def get_top_messages():
    '''Get top performing messages'''
    messages = db.get_top_messages(limit=10)
    
    data = [{
        'message_id': row[0],
        'date': row[1],
        'text': row[2][:150] + '...' if len(row[2]) > 150 else row[2],
        'views': row[3],
        'forwards': row[4],
        'replies': row[5]
    } for row in messages]
    
    return jsonify(data)

@app.route('/api/growth')
def get_growth():
    '''Get member growth data'''
    growth = db.get_channel_growth()
    
    data = {
        'dates': [row[0] for row in growth],
        'members': [row[1] for row in growth]
    }
    
    return jsonify(data)

@app.route('/api/views-today')
def get_views_today():
    '''Get today's views with comparison'''
    data = db.get_views_today()
    return jsonify(data)

@app.route('/api/hourly-activity')
def get_hourly_activity():
    '''Get peak activity hours'''
    data = db.get_hourly_activity()
    return jsonify(data)

@app.route('/api/weekly-pattern')
def get_weekly_pattern():
    '''Get average views by day of week'''
    pattern = db.get_weekly_pattern()
    
    data = {
        'days': [row[0] for row in pattern],
        'avg_views': [row[1] for row in pattern]
    }
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)