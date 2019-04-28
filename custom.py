import math
from django.conf import settings

from random import randint


def get_listing_rank(self):
    return 1


def get_profile_rank(self):
    return 1


def mark_scammers():
    from ob.models import Profile
    known_scammers = []
    Profile.objects.filter(pk__in=known_scammers).update(scam=True)


def do_dog_follow(self, testnet=False):
    pass


def mark_dust():
    update_count = Listing.objects \
        .filter(price_value__lt=0.001,
                accepted_currencies__icontains='BTC')\
        .exclude(accepted_currencies__icontains='BCH')\
        .exclude(accepted_currencies__icontains='ETH')\
        .exclude(accepted_currencies__icontains='LTC')\
        .exclude(accepted_currencies__icontains='ZEC')\
        .update(dust=True)
    print("{} listings marked as dust".format(update_count))


good_nodes = [
    "QmdrBJq88kKVu3SSba9h4deoCkvx3kDwVFTS7Piy6bX652",  # "Jack of all trades"
    "QmazDcPBtDNXXCypDJbQXWSJmihUx4ChmMVCLDLPXKB8Bi",  # "Crypto Shoppe"
    "QmXjNwM5yxWcCzvyEn9LdNwY6a66XQSzGUK1q5jaj9tZR2",  # "The Corner Bazaar"
    "QmX6s5DNJZ5uVA1im1BfxrmTUfYoZTZxFL2zzfjFgDUhXN",  # "BTC EMPORIUM - BTC"
    "QmYTRdwd4nhBRJX5QLNCbKxzPNrNaGCUVnvhFMK1tm3fhz",  # "🆆🅾🅻🅵"
    "QmcLfrGiJVXFfzJWSB87tv4GJ7KNPfSw6y2vxJpmyBvpq3",  # "Cryptor Trust"
    "QmaeNaBvbxEy5KJhQaW64MGL3XgJGXWKqpJuFSPe1WXQ2A",  # "link"
    "QmVFNEj1rv2d3ZqSwhQZW2KT4zsext4cAMsTZRt5dAQqFJ",  # "Jacob Ian"
    "QmVs41UchsbEXDdA7MBHqcX4Db4RQJFQZENDRY9m3HixUq",  # "FutureBong"
    "QmVqRtEbWTTxUfM7WP7MQLaY2jk7aqBkZKWXNWHz97FUvM",  # "Billd Labs"
    "Qmf8iAdt7DVkUiNkf2QQwD6Spp7bMRtMRTeZ1dbrANMjwR",  # "Motion Dogs"
    "QmeRw4K4s5HvWmYZhTdDt8mdr5rf6MCNZHW51T8ZmKKF9g",  # "Max aka @Anyone"
    "QmbtunGFSjMJhz1LVrjnnpckB25iZ7BeMb3oYgcdEKQ3E2",  # "Select Woodcraft"
    "QmZ1vWZKrpPPte2T9WYDmUbEkU34G5gfDqMDUwtEjJePRj",  # "Nature's Crafts"
    "QmYb9TA7EfvFzN1VtHpEczquu9atSfYu2bodfhVibB642X",  # "MadeInJapan"
    "QmdRKB9CuzFu8nzt8W9PR6DyWwYsxocVrzfzCUEGqxY1AT",  # "OB 537nvc"
    "QmPeo9Qjd84ZAuRZPw4CfYwvQF58LobzKdAyu4WKX7jLZr",  # "Refur"
    "QmWcuhdvNUDDdoKg17AKGTm1YXVJcLdG66wUUaRd7wj3Nu",  # "Tom Woods Jewelry"
    "QmamG5uQjRqrdxAxp4DJK4TLvs2Yet8Nuiztip4ALD7i1U",  # "Wayne's Trading Post"
    "QmYX3xErnCVXSF3aK6zoAWwfDqmbTufeE51J7J7u5G9sFi",  # "Oslo Knitting "
    "QmbbsQFShrTBU6cnUQf6HNiAtZ9sLfNyQqgGFe2ZoZqWxg",  # "EnergyExpressions"
    "QmNf5cCZRvbCYCdtmU5pkDxkHpNgtkgwyzpeYfAUG5yvUz",  # "P2P VPS Alpha"
    "QmPFvqyMp13EQHP94AZhFWQWQtmUQteeCoS75wEfyKu2Wb",  # "Anonymous Artist"
    "QmRrwvM4bRSKSTsyy1K3jkjJow67H52n39iBuuaCi48EZn",  # "OB Lawyer"
    "QmToMDNbbikVDxJvqH8oyeVWegbJZyAU7fW16vMp5HgrGA",  # "Fr0Man"
    "QmfUNUFM5B4PJh73Ht4Gd7qa1TAWV1BBUAhbrYRa2E9hXe",  # "DrApis"
    "Qme3KKw6BABTsKmFYMdmPZsf8KE1j4djX7PSaCAt4cE3n9",  # "Fifties Finds BCN"
    "QmWyRmLLGxSbRMcz8eDqZqKzrzAavBHBPUR2cuAA3uqyRo",  # "Xnopyt"
    "QmfWsC79U312NHEmERHKRiRwFHaYF6wESkM87rGRJHyCUB",  # "SOP-TECHNOLOGIES"
    "QmXcXbTiB363fug1SD7PYcr77mx5VzmKF14Rr6jDrhRygT",  # "cactusseeds"
    "QmSmBg7327d4dNY8N1dvjzhmVN4mgD9CT7R4gG13rmKM2c",  # "debieswax"
    "QmXpn3aQdN5qBQCeibnqyDRrHdtQEkAz7HC7vUcCrTymjg",  # "Oleg from Moldova"
    "QmQ1zG7QyY1Jk7diRW4BBtotMkJsVNznM8JyWDuQLYQan1",  # "MicroForex"
    "QmcKCjWaM3uyR1b6yMAut9qzqSTU41ZRVVKktApRsTii3r",  # "BitcoinCat"
    "Qmeihye4sGWbspZ5W3f1ohEy3yz3XCurTS3rkUb4e5ndBV",  # "Sovereign Threads"
    "QmfGL6dWz8NHwcD9aedL4Y73veqrBQ5Qw7EpQHa3EZ3t4c",  # "coinedbits®"
    "QmeSyTRaNZMD8ajcfbhC8eYibWgnSZtSGUp3Vn59bCnPWC",  # "Matthew Zipkin"
    "QmX4dToBygh9h5o1vyWNaoyni2v2UFg8hrESvKzBLriAcz",  # "Bahremon"
    "QmWKMZnRimcwRu4VENjvAPmVjyE2eo7HR7HnyxEsXb3Ygs",  # "declutter69"
    "QmUX6cF4L3fwjg1mBfUtECZssYL4FvaccQJRFjm9aNbJn4",  # "Efilenka"
    "QmUgqCQ2BYWHioPozrGDPmyrvkZKVbHeSdxe62fRdFPGp7",  # "Gadgets Plus More "
    "QmWdNQE9ndY4TWVBSMnj69NvX87F6bMAjwcafh8Jj1KjD9",  # "Jacob Ian Long, Esq."
    "QmU5ZSKVz2GhsqE6EmBGVCtrui4YhUXny6rbvsSf5h2xvH",  # "BTC EMPORIUM - BCH"
    "QmcUgAKG5Hd4hECYQLYWpbtdsPZw8FqR33zCX3sBjQSikM",  # "MultiMedia One"
    "QmfCtcdJkoH6YMQCKpxS6Wi1zn3Gj3LQvb2kkxjKJGWk8C",  # "Print It!"
    "QmXvRRt5Dg47LfzruocRTfnrpvGjzVnZSedRqubs6JpzS2",  # "LeftCoastCryptoGirl"
    "QmT39cw2SpBYQe5AiaDWvnDTSbhWY6ZGn8CStyLWdSSxb2",  # "Crypto Shoppe"
    "QmY8gzdEHTTE1ePcGDEjQuGgZXNz7MeWQWFF8mvy8FKJXj",  # "Goji & More Store"
    "QmY1wxjnsJuBYKsHGmaF7TYpKbjH9SfJZcBByMfzgpvjBm",  # "Photo Spell Gifts"
    "QmcFDsYzYbqiHQ3MZB6qRTWemjkhC5LRaorBvXiQ4Wcja6",  # "Rob's Stuff"
    "QmUkQuY5ChYhutKuy4qmgqg6HPzqYvG4xSJtPHY7RCAcMQ",  # "CriptoAiuto"
    "QmaW2iTEkAMhDCEm1pKtD2DXhivCvrHmkbnbwLBdsK1ccS",  # "openoms"
    "QmWQWkzy5uL6PpZrWACxtQEXekAXhmKmKjMWiSPq1sv3QP",  # "PhysiBit"
    "QmexN16BRNikixVeTvZfWkEZMXzB6rcnSiH1pm55k16zEN",  # "Ohm, Inc"
    "QmZkcNYLHfcnw6w6G6VhsswKhPiywwcQasWpDPsTnWMHLh",  # "Pharaoh USA"
    "QmNU2H1S1gNf782s9gvFFV9jUKBSy7uuWU8QtAA2N3bhFZ",  # "🥃 Brian Hoffman"
    "QmZb7cTkEVgXTGskHVbNEKyoUKDSfhpFamHu1X2Yvkh37P",  # "Hlebushka"
    "QmQnVRoiZdmpkBsKGsesHydNsJow1R3GHa3Mv3D4GsvcJA",  # "Soular ECryptz"
    "QmUyi8BikSpVXCsqgpLKmfoWSS6L2VrhbZ3mQ4hxWeig6D",  # "OB ytgio6"
    "QmUxviboTQXaaqsGrwZfCpS83NoW2ege16o4DpnZKVo16z",  # "cake weather"
    "QmcNqUgkrWpy4XfbjPYX7ZicU23LLLVP65Y5vpmr9epgyd",  # "SamPatt (OB1)"
    "QmZuTqFBi2cWFAREajSTxKf8YLZJ1fKzSG2q5xD9NdhaLe",  # "Pure Chimp"
    "QmXDVJ8AAoyM4nkSVKEJ3GwSLJBBoakxZfmDkyqAHK12HZ",  # "troed"
    "QmcUDmZK8PsPYWw5FRHKNZFjszm2K6e68BQSTpnJYUsML7",  # "OpenBazaar Store"
    "QmWFVJsCXeCe1whgRgPGXQyb9aMfwcUCV8ECKX4oNrwRtd",  # "Arne Bolen"
    "Qmf9kucB3YV9Kqx7aSSQTVHR6uiepJWGbPD3B3HcPsjayi",  # "OpenBazaar Fan"
    "QmdHduEXHFwswBoGahj3o8C6R71E3r7B2THvPcgsmRecaF",  # "ThePub"
    "QmduBPTQNaXYWivhjNEs8fx5psgazDpH4x1DJqtTcVXhPs",  # "Magpie Finds"
    "QmUGCXBcMFT5YJvuzesyX7GvkYpJ8PpULcn2bjZpH63wzZ",  # "Magpie Finds (BCH)"
]
