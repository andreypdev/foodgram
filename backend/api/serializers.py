from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField)
from rest_framework.validators import ValidationError

from users.models import Subscription
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)

User = get_user_model()


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class RecipeSummarySerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class IngredientForRecipeSerializer(ModelSerializer):
    id = IntegerField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')
    amount = IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class UserDataSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        if request.user.is_anonymous:
            return False

        return Subscription.objects.filter(
            user=request.user, author=obj.id
        ).exists()


class NewAccountSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = '__all__'

    @staticmethod
    def validate_username(value):
        if value.lower() == 'me':
            raise ValidationError(
                'Cannot use "me" as login.'
            )

        if User.objects.filter(username=value).exists():
            raise ValidationError(
                'User already exists.'
            )

        return value

    @staticmethod
    def validate_email(value):
        if User.objects.filter(email=value).exists():
            raise ValidationError(
                'E-mail is already registered.'
            )
        return value


class RecipeDetailSerializer(ModelSerializer):
    author = UserDataSerializer(read_only=True)
    ingredients = IngredientForRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredient_in_recipe',
    )
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'text',
            'ingredients',
            'tags',
            'image',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user

        if user.is_anonymous:
            return False

        return obj.favorite.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user

        if user.is_anonymous:
            return False

        return obj.cart.filter(user=user).exists()


class RecipeWriteSerializer(ModelSerializer):
    author = UserDataSerializer(read_only=True)
    ingredients = IngredientForRecipeSerializer(many=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'name',
            'author',
            'text',
            'ingredients',
            'tags',
            'image',
            'cooking_time',
        )

    def to_representation(self, instance):
        return RecipeSummarySerializer(
            instance,
            context={'request': self.context.get('request')},
        ).data

    @staticmethod
    def validate(data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise ValidationError(
                'Recipe should contain at least 1 ingredient.'
            )

        unique_ingredient_set = set(
            [ingredient['ingredient']['id'] for ingredient in ingredients]
        )

        if (len(unique_ingredient_set) != (len(ingredients))):
            raise ValidationError(
                'Ingredients must be unique.'
            )

        tags = data.get('tags')
        if not tags:
            raise ValidationError(
                'Recipe needs at least one tag.'
            )

        if len(set(tags)) != len(tags):
            raise ValidationError(
                'Tags must be unique.'
            )

        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('ingredient').get('id'),
                amount=ingredient.get('amount'),
            )

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        instance.tags.set(tags)

        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get('ingredient').get('id'),
                amount=ingredient.get('amount'),
            )

        return super().update(instance, validated_data)


class ShoppingCartRecipeSerializer(ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'


class FavoriteRecipeSerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class SubscriptionInfoSerializer(ModelSerializer):
    id = ReadOnlyField(source='author.id')
    email = ReadOnlyField(source='author.email')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        if request.user.is_anonymous:
            return False

        return Subscription.objects.filter(
            user=request.user, author=obj.author.id
        ).exists()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author.id).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipe_count = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author.id)

        if recipe_count:
            queryset = queryset[:int(recipe_count)]

        return RecipeSummarySerializer(
            queryset,
            many=True
        ).data
