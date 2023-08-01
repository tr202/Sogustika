from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "ингредиенты"
        verbose_name = "игредиент"
        ordering = ("name",)

    def __str__(self):
        return str(self.id) + " " + self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
    )
    color = models.CharField(
        max_length=7,
    )
    slug = models.SlugField(
        "Slug-тега",
        unique=True,
        max_length=200,
    )

    class Meta:
        verbose_name_plural = "Теги"
        verbose_name = "тег"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    pub_date = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(
        "users.User",
        on_delete=models.DO_NOTHING,
        related_name="recipes",
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
    )
    name = models.CharField(
        max_length=200,
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        null=True,
        default=None,
    )
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = "рецепты"
        verbose_name = "рецепт"
        ordering = ("-pub_date",)

    def __str__(self):
        return (
            self.name
            + " "
            + self.author.username
            + " "
            + str(self.cooking_time)
            + " "
            + self.text[:100]
        )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ("recipe",)

    def __str__(self):
        return (
            self.recipe.name
            + " "
            + self.ingredient.name
            + " "
            + str("amoumt")
            + self.ingredient.measurement_unit
        )
