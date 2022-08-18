from enum import Enum


class Scope(Enum):
    ...


class Address(Scope):
    read = "address_r"
    write = "address_w"


class Billing(Scope):
    read = "billing_r"


class Cart(Scope):
    read = "cart_r"
    write = "cart_w"


class Email(Scope):
    read = "email_r"


class Favorites(Scope):
    read = "favorites_r"
    write = "favorites_w"


class Listings(Scope):
    delete = "listings_d"
    read = "listings_r"
    write = "listings_w"


class Profile(Scope):
    read = "profile_r"
    write = "profile_w"


class Recommend(Scope):
    read = "recommend_r"
    write = "recommend_w"


class Shops(Scope):
    read = "shops_r"
    write = "shops_w"


class Transactions(Scope):
    read = "transactions_r"
    write = "transactions_w"
