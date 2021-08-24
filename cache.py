import redis

# скорее всего -- redis - с контейнером, localhost - локально
r = redis.Redis(host='localhost', port=6379, db=0)

# def redis_add_new_user(chatID):
#     r.hset(0, chatID, "")
#
#
# def redis_add_order(chatID):
#
#     r.zadd("mylist", {chatID: 0})
#     return r.zrange("mylist", 0, -1, withscores=True)


class Cache():

    def __init__(self, host='localhost', port=6379, db=0):
        r = redis.Redis(host=host, port=port, db=db)

    @staticmethod
    def find_free_user(user_id):
        partner = r.rpop('order')
        # check_cache = r.hget('users', user_id)
        if partner is None:
            Cache.add_user_to_order(user_id)
            print(r.lrange('order', 0, -1))
        return partner.decode('utf-8') if partner else None

    @staticmethod
    def add_user_to_order(user_id):
        return r.lpush('order', user_id)

    @staticmethod
    def rem_user_from_order(user_id):
        return r.lpop('order')

    @staticmethod
    def add_connects_cache(user_1, user_2):
        p = r.pipeline()
        p.hset('users', user_1, user_2)
        p.hset('users', user_2, user_1)
        p.execute()

    @staticmethod
    def get_partner_id(user_id):
        partner = r.hget('users', user_id)
        return partner.decode('utf-8') if partner else None

    @staticmethod
    def rem_connects_cache(user_1, user_2):
        p = r.pipeline()
        p.hdel('users', user_1)
        p.hdel('users', user_2)
        p.execute()

