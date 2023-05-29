from rest_framework import serializers
from .models import Variant, Product, ProductImage, ProductVariant, ProductVariantPrice
from drf_extra_fields.fields import Base64FileField, Base64ImageField

class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductImageCreateSerializer(serializers.ModelSerializer):
    file_path = Base64ImageField(required=True)

    class Meta:
        model = ProductImage
        fields = '__all__'

    def create(self, validated_data):
        return ProductImage.objects.create(**validated_data)

            

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'

class ProductVariantPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantPrice
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    product_images = ProductImageSerializer(many=True, read_only=True)
    product_variants = ProductVariantSerializer(many=True, read_only=True)
    product_variant_prices = ProductVariantPriceSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def get_product_images(self, obj):
        return ProductImageSerializer(obj.product_images.all(), many=True).data

    def get_product_variants(self, obj):
        return ProductVariantSerializer(obj.product_variants.all(), many=True).data

    def get_product_variant_prices(self, obj):
        return ProductVariantPriceSerializer(obj.product_variant_prices.all(), many=True).data

