import sqlite3
from datetime import datetime, timedelta
import json

class Database:
    def __init__(self, db_path='analytics.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        '''Initialize database tables'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Channel info table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channel_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT,
                channel_title TEXT,
                members_count INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                channel_id TEXT,
                date DATETIME,
                text TEXT,
                views INTEGER,
                forwards INTEGER,
                replies INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Daily stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                channel_id TEXT,
                total_messages INTEGER,
                total_views INTEGER,
                total_forwards INTEGER,
                avg_views REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, channel_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_channel_info(self, channel_id, title, members_count):
        '''Save channel information'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO channel_info (channel_id, channel_title, members_count)
            VALUES (?, ?, ?)
        ''', (str(channel_id), title, members_count))
        conn.commit()
        conn.close()
    
    def save_message(self, message_id, channel_id, date, text, views, forwards, replies):
        '''Save or update message statistics'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if message exists
        cursor.execute('SELECT id FROM messages WHERE message_id = ? AND channel_id = ?', 
                      (message_id, str(channel_id)))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing message
            cursor.execute('''
                UPDATE messages 
                SET views = ?, forwards = ?, replies = ?, timestamp = CURRENT_TIMESTAMP
                WHERE message_id = ? AND channel_id = ?
            ''', (views or 0, forwards or 0, replies or 0, message_id, str(channel_id)))
        else:
            # Insert new message
            cursor.execute('''
                INSERT INTO messages (message_id, channel_id, date, text, views, forwards, replies)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (message_id, str(channel_id), date, text, views or 0, forwards or 0, replies or 0))
        
        conn.commit()
        conn.close()
    
    def save_daily_stats(self, date, channel_id, total_messages, total_views, total_forwards, avg_views):
        '''Save daily statistics'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO daily_stats 
            (date, channel_id, total_messages, total_views, total_forwards, avg_views)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, str(channel_id), total_messages, total_views, total_forwards, avg_views))
        conn.commit()
        conn.close()
    
    def get_recent_stats(self, days=30):
        '''Get statistics for the last N days'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date, total_messages, total_views, total_forwards, avg_views
            FROM daily_stats
            ORDER BY date DESC
            LIMIT ?
        ''', (days,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_top_messages(self, limit=10):
        '''Get top messages by views'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT message_id, date, text, views, forwards, replies
            FROM messages
            ORDER BY views DESC
            LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_channel_growth(self):
        '''Get channel member growth over time'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DATE(timestamp) as date, MAX(members_count) as members
            FROM channel_info
            GROUP BY DATE(timestamp)
            ORDER BY date ASC
        ''')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_overview_stats(self):
        '''Get overview statistics'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Latest channel info
        cursor.execute('''
            SELECT channel_title, members_count
            FROM channel_info
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        channel_info = cursor.fetchone()
        
        # Total messages
        cursor.execute('SELECT COUNT(*) FROM messages')
        total_messages = cursor.fetchone()[0]
        
        # Total views
        cursor.execute('SELECT SUM(views) FROM messages')
        total_views = cursor.fetchone()[0] or 0
        
        # Average views per post
        cursor.execute('SELECT AVG(views) FROM messages')
        avg_views = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'channel_title': channel_info[0] if channel_info else 'N/A',
            'members_count': channel_info[1] if channel_info else 0,
            'total_messages': total_messages,
            'total_views': total_views,
            'avg_views': round(avg_views, 2)
        }
    
    def get_views_today(self):
        '''Get views for today and yesterday'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        cursor.execute('SELECT total_views FROM daily_stats WHERE date = ?', (today,))
        today_views = cursor.fetchone()
        today_views = today_views[0] if today_views else 0
        
        cursor.execute('SELECT total_views FROM daily_stats WHERE date = ?', (yesterday,))
        yesterday_views = cursor.fetchone()
        yesterday_views = yesterday_views[0] if yesterday_views else 0
        
        conn.close()
        
        return {
            'today': today_views,
            'yesterday': yesterday_views,
            'difference': today_views - yesterday_views
        }
    
    def get_hourly_activity(self):
        '''Get average posting and viewing activity by hour'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Posting activity by hour
        cursor.execute('''
            SELECT strftime('%H', date) as hour, COUNT(*) as count
            FROM messages
            GROUP BY hour
            ORDER BY count DESC
            LIMIT 1
        ''')
        post_peak = cursor.fetchone()
        
        # View activity (using message date as proxy)
        cursor.execute('''
            SELECT strftime('%H', date) as hour, AVG(views) as avg_views
            FROM messages
            GROUP BY hour
            ORDER BY avg_views DESC
            LIMIT 1
        ''')
        view_peak = cursor.fetchone()
        
        conn.close()
        
        return {
            'post_peak_hour': int(post_peak[0]) if post_peak else 0,
            'view_peak_hour': int(view_peak[0]) if view_peak else 0
        }
    
    def get_weekly_pattern(self):
        '''Get average views by day of week'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                CASE CAST(strftime('%w', date) AS INTEGER)
                    WHEN 0 THEN 'Sunday'
                    WHEN 1 THEN 'Monday'
                    WHEN 2 THEN 'Tuesday'
                    WHEN 3 THEN 'Wednesday'
                    WHEN 4 THEN 'Thursday'
                    WHEN 5 THEN 'Friday'
                    WHEN 6 THEN 'Saturday'
                END as day_name,
                AVG(views) as avg_views
            FROM messages
            GROUP BY strftime('%w', date)
            ORDER BY strftime('%w', date)
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return results