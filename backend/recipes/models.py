from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    COLOR_CHOICES = [
        ('blue', '#005DFF'),
        ('green', '#00D300'),
        ('orange', '#EE8D00'),
        ('purple', '#5300C4'),
        ('black', '#000000'),
        ('mint', '#3EB489'),
    ]

    name = models.CharField(
        'Name',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        'Color',
        max_length=7,
        choices=COLOR_CHOICES,
        unique=True,
    )
    slug = models.SlugField(
        'Slug',
        unique=True
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Ingredient name',
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Measurement unit',
        max_length=10
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Recipe author',
    )
    name = models.CharField('Recipe name', max_length=200)
    image = models.ImageField(
        'Recipe photo',
        upload_to='recipe/',
    )
    text = models.TextField(
        'Recipe description'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Tags')
    cooking_time = models.IntegerField(
        'Cooking time.',
        validators=[MinValueValidator(1)],
    )
    pub_date = models.DateTimeField(
        'Publish date',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipies'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Recipe',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                message='Minimum amount of ingredients - 1',
            )
        ],
        verbose_name='Ingredient measurements',
    )

    class Meta:
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            )
        ]
        verbose_name = 'Recipe ingredient'
        verbose_name_plural = 'Recipe ingredients'

    def __str__(self):
        return f'{self.recipe} contains {self.amount}x {self.ingredient}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='User'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe'
    )

    class Meta:
        default_related_name = 'cart'
        verbose_name = 'Shopping list'
        verbose_name_plural = 'Shopping lists'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_shopping_cart_unique',
            )
        ]

    def __str__(self):
        return (f'{self.user.username} has '
                f'{self.recipe.name} on their shopping list.')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe'
    )

    class Meta:
        default_related_name = 'favorite'
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_favorite_unique',
            )
        ]

    def __str__(self):
        return (f'{self.user.username} has '
                f'{self.recipe.name} in their favorites.')
