sh.enableSharding("social_network")
sh.shardCollection("social_network.posts", { user_id: 1 })
sh.shardCollection("social_network.comments", { user_id: 1 })
sh.shardCollection("social_network.friendships", { user_id: 1 })
sh.shardCollection("social_network.likes", { post_id: 1 })
    