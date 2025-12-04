from flask import Flask, render_template, jsonify
from database import Database
import config

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

@app.route('/api/top-messages')
def get_top_messages():
    '''Get top performing messages'''
    messages = db.get_top_messages(limit=10)
    
    data = [{
        'message_id': row[0],
        'date': row[1],
        'text': row[2][:100] + '...' if len(row[2]) > 100 else row[2],
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
        'timestamps': [row[0] for row in growth],
        'members': [row[1] for row in growth]
    }
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)