from enum import Enum


class Scope:
    ...


class Address(Scope, Enum):
    read = "address_r"
    write = "address_w"


class Billing(Scope, Enum):
    read = "billing_r"


class Cart(Scope, Enum):
    read = "cart_r"
    write = "cart_w"


class Email(Scope, Enum):
    read = "email_r"


class Favorites(Scope, Enum):
    read = "favorites_r"
    write = "favorites_w"


class Listings(Scope, Enum):
    delete = "listings_d"
    read = "listings_r"
    write = "listings_w"


class Profile(Scope, Enum):
    read = "profile_r"
    write = "profile_w"


class Recommend(Scope, Enum):
    read = "recommend_r"
    write = "recommend_w"


class Shops(Scope, Enum):
    read = "shops_r"
    write = "shops_w"


class Transactions(Scope, Enum):
    read = "transactions_r"
    write = "transactions_w"
