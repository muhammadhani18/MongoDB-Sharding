from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import json
import os

client = MongoClient("mongodb://localhost:27020")
db = client.social_network

# Ensure output directory exists
os.makedirs("query_results", exist_ok=True)

def write_to_file(filename, data):
    with open(os.path.join("query_results", filename), "w") as f:
        json.dump(data, f, default=str, indent=2)

def get_all_posts_of_user(user_id):
    result = list(db.posts.find({"user_id": user_id}))
    write_to_file("all_posts_of_user.json", result)
    return result

def get_top_k_liked_posts_of_user(user_id, k):
    result = list(
        db.posts.find({"user_id": user_id}).sort("like_count", -1).limit(k)
    )
    write_to_file("top_k_liked_posts.json", result)
    return result

def get_top_k_commented_posts_of_user(user_id, k):
    result = list(
        db.posts.find({"user_id": user_id}).sort("comment_count", -1).limit(k)
    )
    write_to_file("top_k_commented_posts.json", result)
    return result

def get_all_comments_of_user(user_id):
    result = list(db.comments.find({"user_id": user_id}))
    write_to_file("all_comments_of_user.json", result)
    return result

def get_all_posts_on_topic(topic):
    result = list(db.posts.find({"topic": topic}))
    write_to_file("all_posts_on_topic.json", result)
    return result

def get_top_k_popular_topics(k):
    result = list(
        db.posts.aggregate([
            {"$group": {"_id": "$topic", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": k}
        ])
    )
    write_to_file("top_k_popular_topics.json", result)
    return result

def get_friends_recent_posts(user_id):
    # Step 1: Find user's friends
    friend_ids = db.friendships.find({"user_id": user_id})
    friend_ids = [f["follows"] for f in friend_ids]

    # Step 2: Get posts by friends in last 24 hours
    since = datetime.utcnow() - timedelta(hours=24)
    result = list(
        db.posts.find({
            "user_id": {"$in": friend_ids},
            "created_at": {"$gte": since}
        }).sort("created_at", -1)
    )
    write_to_file("friends_recent_posts.json", result)
    return result

if __name__ == "__main__":
    user = db.users.find_one()
    user_id = user["_id"]

    get_all_posts_of_user(user_id)
    get_top_k_liked_posts_of_user(user_id, 3)
    get_top_k_commented_posts_of_user(user_id, 3)
    get_all_comments_of_user(user_id)
    get_all_posts_on_topic("tech")
    get_top_k_popular_topics(3)
    get_friends_recent_posts(user_id)

    print("All query results saved to 'query_results' directory.")
