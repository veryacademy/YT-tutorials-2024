import uuid

from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)

    name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True, blank=True, max_length=120)
    is_active = models.BooleanField(default=False)
    level = models.IntegerField(default=0)

    # class Meta:
    #     verbose_name_plural = "Categories"
    #     constraints = [
    #         models.CheckConstraint(check=~Q(name=''), name='name_not_empty'),
    #     ]

    # def clean(self):
    #     super().clean()
    #     if self.name == '':
    #         raise ValidationError({'name': "This field cannot be empty."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SeasonalEvent(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    name = models.CharField(max_length=100, unique=True, blank=False)

    class Meta:
        db_table = "inventory_seasonal_event"

    def __str__(self):
        return self.name


class ProductType(models.Model):
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)

    name = models.CharField(max_length=100)
    level = models.IntegerField(default=0)

    class Meta:
        db_table = "inventory_product_type"

    def __str__(self):
        return self.name


class Product(models.Model):
    IN_STOCK = "IS"
    OUT_OF_STOCK = "OOS"
    BACKORDERED = "BO"

    STOCK_STATUS = {
        IN_STOCK: "In Stock",
        OUT_OF_STOCK: "Out of stock",
        BACKORDERED: "Back Ordered",
    }

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=True, blank=True
    )
    seasonal_event = models.ForeignKey(
        SeasonalEvent, on_delete=models.PROTECT, null=True, blank=True
    )
    product_type = models.ManyToManyField(
        ProductType,
        through="Product_ProductType",
        related_name="product_type",
        blank=False,
    )

    pid = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(null=True)
    is_digital = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    stock_status = models.CharField(
        max_length=3,
        choices=STOCK_STATUS,
        default=OUT_OF_STOCK,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Attribute(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT)

    attribute_value = models.CharField(max_length=100)

    class Meta:
        db_table = "inventory_attribute_value"

    def __str__(self):
        return f"{self.attribute.name}: {self.attribute_value}"


class ProductLine(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    attribute_values = models.ManyToManyField(
        AttributeValue,
        through="ProductLine_AttributeValue",
        related_name="attribute_values",
    )

    price = models.DecimalField(decimal_places=2, max_digits=5)
    sku = models.UUIDField(default=uuid.uuid4, unique=True)
    stock_qty = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    order = models.IntegerField()
    weight = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inventory_product_line"


class ProductImage(models.Model):
    product_line = models.ForeignKey(ProductLine, on_delete=models.PROTECT)

    alternative_text = models.CharField(max_length=100)
    url = models.ImageField()
    order = models.IntegerField()

    class Meta:
        db_table = "inventory_product_image"


class ProductLine_AttributeValue(models.Model):
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
    product_line = models.ForeignKey(ProductLine, on_delete=models.CASCADE)


class Product_ProductType(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
