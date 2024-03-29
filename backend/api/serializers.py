from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Follow, User


NEED_INGREDIENTS = 'Добавьте минимум один ингредиент!'
UNIQUE_INGREDIENTS = 'Ингредиенты должны быть уникальными!'
AMOUNT_INGREDIENTS = 'Количество ингредиента должно быть больше нуля!'
NEED_TAGS = 'Добавьте минимум один тег!'
UNIQUE_TAGS = 'Теги должны быть уникальными!'
UNIQUE_FAVORITE_RECIPE = 'Данный рецепт был добавлен ранее.'


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomUserSerializer(UserSerializer):
    """
    Отображает, подписан ли текущий пользователь на запрашиваемого.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class FollowSerializer(CustomUserSerializer):
    """
    Вывод подписок пользователя.
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        recipes_limit = (self.context.get('request')
                         .query_params.get('recipes_limit')
                         )
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return MinimumRecipeSerializer(recipes, many=True).data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('__all__',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Вывод количества ингредиентов.
    """
    id = serializers.StringRelatedField(source='ingredient.id')
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    """
    Отображение рецептов.
    """
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', read_only=True, many=True
        )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated
                and Recipe.objects.filter(favorites__user=user, id=obj.id)
                .exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (user.is_authenticated
                and Recipe.objects.filter(shopping_cart__user=user, id=obj.id)
                .exists())


class AddIngredientSerializer(serializers.ModelSerializer):
    """
    Добавление ингредиентов.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Создание и изменение рецептов.
    """
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(many=True)
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    @staticmethod
    def create_tags(tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    @staticmethod
    def create_ingredients(ingredients, recipe):
        RecipeIngredient.objects.bulk_create([RecipeIngredient(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount']
            ) for ingredient in ingredients])

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user, **validated_data
        )
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance, context={'request': self.context.get('request')}
        ).data

    def update(self, instance, validated_data):
        instance.tags.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = data['ingredients']
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': NEED_INGREDIENTS
                })
        ingredients_list = []
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': UNIQUE_INGREDIENTS
                })
            ingredients_list.append(ingredient['id'])
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError({
                    'amount': AMOUNT_INGREDIENTS
                })
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError({'tags': NEED_TAGS})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError({'tags': UNIQUE_TAGS})
            tags_list.append(tag)
        return data


class MinimumRecipeSerializer(serializers.ModelSerializer):
    """
    Краткое отображение рецептов.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)
