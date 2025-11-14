import threading 
import time
import json 

class ChannelManager: 
    """
    Manage channels and members
    """
    
    def __init__(self):
        self.channel = {}
        self.user_channels = {}
        self.lock = threading.Lock()
        
        
    def create_channel(self, channel_name, creator_username):
        """
        Create a new channel.
        
        :param channel_name: The name of the channel to create (unique)
        :param creator_username: The username of the channel creator
        :return: True if create successful , create this channel 
        """

        with self.lock: 
            if channel_name in self.channel:
                return False
            self.channel[channel_name] = {
                'creator' : creator_username,
                'members' : [creator_username],
                'created_at': time.time()
            }
        if creator_username not in self.user_channels: 
            self.user_channels[creator_username] = []
        self.user_channels[creator_username].append(channel_name)
        print(f"[ChannelManager] Channel '{channel_name}' created by {creator_username}")
        return True
    
    def list_all_channels(self):
        """
        Get all active channels in this app
        
        :return: List of channels
        """
        with self.lock:
            channels = []
            for channel_name, channel_info in self.channel.items():
                channels.append({
                    'name' : channel_name,
                    'creator': channel_info['creator'], 
                    'members_count': len(channel_info['members']),
                    'created_at': channel_info['created_at']
                })
            return channels 
    
    def join_channel(self, channel_name, username):
        """
        Join a channel.
        
        :param channel_name: The name of the channel to join
        :param username: The username of the user joining the channel       
        :return: True if join successful 
        """
        with self.lock: 
            if channel_name not in self.channel:
                return False

            channel_info = self.channel[channel_name]
            if username not in channel_info['members']:
                channel_info['members'].append(channel_name)
                
                if username not in self.user_channels: 
                    self.user_channels[username] = []
                self.user_channels[username].append(channel_name)
                
                print(f"[ChannelManager] User '{username}' joined channel '{channel_name}'")
            else:
                print(f"[ChannelManager] User ''{username}' is already in channel '{channel_name}'")
        return True 
    
    
    def get_channel_members(self, channel_name): 
        """"
        Get the members of a channel.
        
        :param channel_name: the name of channel 
        :return: lis of usernames have joined this channel
        """
        
        with self.lock:
            if channel_name not in self.channel:
                return []
            return self.channel[channel_name]['members']
        

channel_manager = ChannelManager()