import io

from django.db.models import Sum

from recipes.models import RecipeIngredient, ShoppingCart
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

pdfmetrics.registerFont(
    TTFont(
        'beer-money12',
        'recipes/fonts/beer-money12.ttf'
    )
)
pdfmetrics.registerFont(
    TTFont(
        'dewberry-bold-italic.ttf',
        'recipes/fonts/dewberry-bold-italic.ttf'
    )
)


def get_query(user):
    return RecipeIngredient.objects.filter(
        recipe_id__in=ShoppingCart.objects.filter(
            byer=user).values('recipe_id')
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit__unit',
        'ingredient__measurement_unit__counted'
    ).order_by(
        'ingredient_id'
    ).annotate(
        total=Sum('amount')
    )


def get_pdf(user):
    query = get_query(user)
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont('beer-money12', 36)
    pdf.setTitle('Список покупок')
    pdf.drawCentredString(300, 750, 'Список покупок.')
    pdf.line(80, 700, 480, 700)
    pdf.setFont('dewberry-bold-italic.ttf', 20)
    position_x = 100
    start_position_y = 650
    step_position_y = 25
    for ingredient in query:
        name = ingredient.get('ingredient__name')
        amount = ingredient.get('total')
        unit = ingredient.get('ingredient__measurement_unit__unit')
        counted = ingredient.get('ingredient__measurement_unit__counted')
        if not counted:
            amount = ''
        ingredient_string = (name + ' ' + str(amount) + unit)
        pdf.drawString(position_x, start_position_y, ingredient_string)
        start_position_y -= step_position_y
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer
