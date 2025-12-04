import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from datetime import datetime, timedelta
import schedule
import time
import pandas as pd
from database import Database
import config

class TelegramCollector:
    def __init__(self):
        self.client = TelegramClient('session', config.API_ID, config.API_HASH)
        self.db = Database(config.DATABASE_PATH)
        self.channel_username = config.CHANNEL_USERNAME
    
    async def collect_data(self):
        '''Collect data from Telegram channel'''
        print(f"[{datetime.now()}] Starting data collection...")
        
        try:
            await self.client.start(phone=config.PHONE)
            
            # Get channel entity
            channel = await self.client.get_entity(self.channel_username)
            channel_id = channel.id
            
            # Get full channel info
            full_channel = await self.client(GetFullChannelRequest(channel))
            members_count = full_channel.full_chat.participants_count
            
            # Save channel info
            self.db.save_channel_info(channel_id, channel.title, members_count)
            print(f"Channel: {channel.title}, Members: {members_count}")
            
            # Get messages from last 30 days
            messages_data = []
            from datetime import timezone
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
            
            async for message in self.client.iter_messages(channel, limit=1000):
                if message.date < cutoff_date:
                    break
                
                self.db.save_message(
                    message_id=message.id,
                    channel_id=channel_id,
                    date=message.date,
                    text=message.text[:200] if message.text else '',
                    views=message.views,
                    forwards=message.forwards,
                    replies=message.replies.replies if message.replies else 0
                )
                
                messages_data.append({
                    'date': message.date.date(),
                    'views': message.views or 0,
                    'forwards': message.forwards or 0
                })
            
            # Calculate daily stats
            if messages_data:
                df = pd.DataFrame(messages_data)
                daily_stats = df.groupby('date').agg({
                    'views': ['count', 'sum', 'mean'],
                    'forwards': 'sum'
                }).reset_index()
                
                # Flatten the multi-level columns
                daily_stats.columns = ['date', 'msg_count', 'total_views', 'avg_views', 'total_forwards']
                
                for _, row in daily_stats.iterrows():
                    self.db.save_daily_stats(
                        date=row['date'],
                        channel_id=channel_id,
                        total_messages=int(row['msg_count']),
                        total_views=int(row['total_views']),
                        total_forwards=int(row['total_forwards']),
                        avg_views=float(row['avg_views'])
                    )
            
            print(f"[{datetime.now()}] Data collection completed successfully!")
            
        except Exception as e:
            print(f"Error during data collection: {e}")
        finally:
            await self.client.disconnect()
    
    def run_once(self):
        '''Run collection once'''
        asyncio.run(self.collect_data())
    
    def run_scheduled(self):
        '''Run collection on schedule'''
        print(f"Starting scheduled data collection (every {config.COLLECTION_INTERVAL} seconds)")
        
        # Run immediately on start
        self.run_once()
        
        # Schedule regular collections
        schedule.every(config.COLLECTION_INTERVAL).seconds.do(self.run_once)
        
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    collector = TelegramCollector()
    
    # For first run or testing, use run_once()
    # For continuous collection, use run_scheduled()
    collector.run_scheduled()