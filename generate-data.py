from pymongo import MongoClient
from faker import Faker
import random
from datetime import datetime, timedelta

# Connect to mongos router
client = MongoClient("mongodb://localhost:27020")
db = client.social_network

fake = Faker()
NUM_USERS = 1000
NUM_POSTS = 100000
TOPICS = ["sports", "music", "movies", "tech", "travel"]

# Clear previous data
db.users.delete_many({})
db.friendships.delete_many({})
db.posts.delete_many({})
db.comments.delete_many({})
db.likes.delete_many({})

# Create users
user_ids = []
for _ in range(NUM_USERS):
    user = {"name": fake.name()}
    user_id = db.users.insert_one(user).inserted_id
    user_ids.append(user_id)

# Create uni-directional friendships
for user in user_ids:
    friends = random.sample(user_ids, random.randint(1, 10))
    for friend in friends:
        if friend != user:
            db.friendships.insert_one({
                "user_id": user,  # shard key
                "follows": friend
            })

# Create posts
post_ids = []
for _ in range(NUM_POSTS):
    user_id = random.choice(user_ids)
    topic = random.choice(TOPICS)
    post = {
        "user_id": user_id,  # shard key
        "text": fake.text(max_nb_chars=200),
        "topic": topic,
        "created_at": fake.date_time_between(start_date="-7d", end_date="now"),
        "like_count": 0,
        "comment_count": 0
    }
    post_id = db.posts.insert_one(post).inserted_id
    post_ids.append(post_id)

# Add likes
for post_id in random.sample(post_ids, int(NUM_POSTS * 0.8)):
    likers = random.sample(user_ids, random.randint(0, 10))
    for liker in likers:
        db.likes.insert_one({
            "post_id": post_id,  # shard key
            "user_id": liker
        })
        db.posts.update_one({"_id": post_id}, {"$inc": {"like_count": 1}})

# Add comments
for post_id in random.sample(post_ids, int(NUM_POSTS * 0.7)):
    commenters = random.sample(user_ids, random.randint(0, 5))
    for commenter in commenters:
        db.comments.insert_one({
            "post_id": post_id,
            "user_id": commenter,  # shard key
            "text": fake.sentence(),
            "created_at": datetime.utcnow()
        })
        db.posts.update_one({"_id": post_id}, {"$inc": {"comment_count": 1}})
