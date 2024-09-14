from tortoise import fields, models

class PriceHistory(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(50)
    price = fields.DecimalField(max_digits=20, decimal_places=8)
    max_price = fields.DecimalField(max_digits=20, decimal_places=8)
    min_price = fields.DecimalField(max_digits=20, decimal_places=8)
    date = fields.DatetimeField(auto_now_add=True)
    difference = fields.DecimalField(max_digits=20, decimal_places=8)
    total_amount = fields.DecimalField(max_digits=20, decimal_places=2)

    class PydanticMeta:
        exclude = ["id"]