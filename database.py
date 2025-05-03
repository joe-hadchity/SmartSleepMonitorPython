from pymongo import MongoClient
from pymongo.server_api import ServerApi
from typing import Optional
import certifi

# Use a class to manage the database connection, handling potential errors and ensuring proper connection management.
class DatabaseManager:
    _instance: Optional['DatabaseManager'] = None

    def __new__(cls, mongodb_uri: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
            cls._instance.mongodb_uri = mongodb_uri  # Store the URI
        return cls._instance

    def connect(self):
        """
        Connect to the MongoDB database.  Handles connection errors.
        """
        if self.client is None:
            try:
                # Use the stored URI
                self.client = MongoClient(self.mongodb_uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
                self.client.admin.command('ping') # Send a ping command to check the connection
                self.db = self.client.get_database("sleep_monitor")  # Connect to the specific database
                print("Connected to MongoDB!")
            except Exception as e:
                print(f"Error connecting to MongoDB: {e}")
                raise  # Re-raise the exception to be handled by caller

    def disconnect(self):
        """
        Disconnect from the MongoDB database.
        """
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            print("Disconnected from MongoDB.")

    def get_database(self):
        """
        Return the database object.  Ensures a connection exists.

        Returns:
            The MongoDB database object.

        Raises:
            RuntimeError: If not connected to the database.
        """
        if self.db is None:
            raise RuntimeError("Not connected to the database. Call connect() first.")
        return self.db

    @classmethod
    def get_instance(cls, mongodb_uri: str = None) -> 'DatabaseManager':
        """
        Get the singleton instance of the DatabaseManager.

        Returns:
            The singleton instance.
        """
        if not cls._instance:
            if not mongodb_uri:
                raise ValueError("MongoDB URI must be provided when the DatabaseManager is first initialized.")
            cls._instance = cls(mongodb_uri) #store the uri
        return cls._instance
        