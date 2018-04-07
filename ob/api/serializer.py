import json
from rest_framework import serializers
from ob.models import Listing, Profile, Image, ListingImage, ListingReport

from django.utils.translation import ugettext_lazy as _



class ListingReportSerializer(serializers.ModelSerializer):

    listing = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        exclude = ('id',)
        model = ListingReport


class ImageMedSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('medium','small')
        model = Image


class ImageSmallSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('small','tiny')
        model = Image

class ProfileSerializer(serializers.ModelSerializer):

    avatarHashes = ImageSmallSerializer(source='avatar')

    shortDescription = serializers.CharField(source='short_description')

    class Meta:
        exclude = ('avatar', 'short_description',)
        model = Profile


class ProfileBadgeSerializer(serializers.ModelSerializer):

    avatarHashes = serializers.SerializerMethodField()
    #shortDescription = serializers.CharField(source='short_description')

    class Meta:
        fields = ('avatarHashes', 'name','peerID',)
        model = Profile

    def get_avatarHashes(self, o):
        try:
            return ImageSmallSerializer(o.avatar_prefetch).data
        except ListingImage.DoesNotExist:
            return ""

class ListingSerializer(serializers.ModelSerializer):

    thumbnail = serializers.SerializerMethodField(source='thumbnail')
    contractType = serializers.IntegerField(source='contract_type')
    price = serializers.SerializerMethodField()
    averageRating = serializers.FloatField(source='rating_average')
    ratingCount = serializers.FloatField(source='rating_count')
    freeShipping = serializers.ListField(source='free_shipping')

    class Meta:
        #exclude = ('condition_type', 'pricing_currency','contract_type','rating_average','rating_count',)
        fields = ('thumbnail','contractType','price','averageRating','ratingCount','slug','nsfw','title','freeShipping')
        model = Listing

    #def get_freeShipping(self,o):
    #    return o.free_shipping[1:-1].replace("'","").split(",")

    def get_thumbnail(self, o):
        try:
            return ImageMedSerializer(o.thumbnail[0]).data
        except ListingImage.DoesNotExist:
            return ""
        except IndexError:
            return ""

    def get_price(self, o):
        return {
            "currencyCode": o.pricing_currency,
            "amount": o.price
        }




class ProfileAsListingSerializer(serializers.ModelSerializer):

    thumbnail = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    title = serializers.CharField(source='name')
    averageRating = serializers.FloatField(source='rating_average')
    ratingCount = serializers.FloatField(source='rating_count')
    #moderators = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()


    class Meta:
        fields = ('peerID', 'price', 'thumbnail','title','ratingCount','averageRating','slug','nsfw',)
        model = Profile

    def get_slug(self, o):
        return "%20"

    # prevent it client from barfing on undefined?
    def get_moderators(self, o):
        return []

    def get_thumbnail(self, o):
        try:
            return ImageMedSerializer(o.header_prefetch).data
        except ListingImage.DoesNotExist:
            return ""

    def get_price(self, o):
        if o.moderator_fee_fixed_amount:
            return {
                "currencyCode": o.moderator_fee_fixed_currency,
                "amount":  o.moderator_fee_fixed_amount
            }
        else:
            return {
                "currencyCode": "USD",
                "amount":  0.00
            }

class ProfileWrapSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('')
        model = Profile

    def to_representation(self, obj):
        return {
            "type": "listing",
            "relationships": {
                "vendor": {'data': ProfileBadgeSerializer(obj).data},
                "moderators": [obj.peerID] if obj.verified else []
            },
            'data': ProfileAsListingSerializer(obj).data
        }


class ListingWrapSerializer(serializers.ModelSerializer):


    class Meta:
        exclude = ('')
        model = Listing

    def to_representation(self, obj):
        return {
            "type": "listing",
            "relationships": {
                "vendor": {'data': ProfileBadgeSerializer(obj.profile).data},
                "moderators": [p.peerID for p in obj.moderators.all()]
            },
            'data': ListingSerializer(obj).data
        }
