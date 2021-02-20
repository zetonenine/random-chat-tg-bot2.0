import redis


r = redis.Redis(db=None)


def redis_add_new_user(chatID):
    r.hset(0, chatID, "")


def redis_add_order(chatID):

    r.zadd("mylist", {chatID: 0})
    return r.zrange("mylist", 0, -1, withscores=True)



class Redis():
    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db
