import redis

# скорее всего -- redis - с контейнером, localhost - локально
r = redis.Redis(host='localhost', port=6379, db=1)


class Cache:

    def __init__(self, host='localhost', port=6379, db=0):
        r = redis.Redis(host=host, port=port, db=db)

    @staticmethod
    def find_free_user(user_id):
        partner = r.rpop('order')
        # check_cache = r.hget('users', user_id)
        if partner is None:
            Cache.add_user_to_order(user_id)
        return partner.decode('utf-8') if partner and partner.decode('utf-8') != str(user_id) else None

    @staticmethod
    def add_user_to_order(user_id):
        return r.lpush('order', user_id)

    @staticmethod
    def rem_user_from_order(user_id):
        partner = r.hget('users', user_id)
        if not partner:
            r.lpop('order')
        return partner

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

