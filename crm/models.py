from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    pan = models.CharField(max_length=10, blank=True, null=True)  # Added PAN field
    relationship_manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='clients'
    )

    def __str__(self):
        return self.name

    def clean(self):
        import re
        from django.core.exceptions import ValidationError

        # Validate PAN format if provided
        if self.pan and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', self.pan):
            raise ValidationError("Invalid PAN format.")
class Lead(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='leads')
    lead_info = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lead for {self.client.name}"

class Meeting(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='meetings')
    relationship_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='meetings')
    date = models.DateTimeField()
    notes = models.TextField()
    remark = models.CharField(
        max_length=255,
        choices=[('Completed', 'Completed'), ('Pending', 'Pending')],
        default='Pending'
    )
    updated_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Meeting with {self.client.name} on {self.date}"


from django.db import models

class Sale(models.Model):
    PRODUCT_CHOICES = [
        ('SIP', 'SIP'),
        ('LUMP', 'Lumpsum'),
        ('HI', 'Health Insurance'),
        ('TI', 'Term Insurance'),
        ('PMS', 'PMS'),
        ('AIF', 'AIF'),
        ('WILL', 'Will'),
        ('GI', 'General Insurance'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sales')
    product = models.CharField(choices=PRODUCT_CHOICES, max_length=10)
    fund_name = models.CharField(max_length=255, blank=True, null=True)  # Optional field for SIP
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateField()

    def clean(self):
        from django.core.exceptions import ValidationError

        # If the product is SIP, fund_name must be provided
        if self.product == 'SIP' and not self.fund_name:
            raise ValidationError("Fund Name is required for Systematic Investment Plan (SIP).")

        # Validate amount
        if self.amount <= 0:
            raise ValidationError("Sale amount must be greater than zero.")

    def __str__(self):
        product_name = dict(self.PRODUCT_CHOICES).get(self.product, self.product)
        if self.product == 'SIP' and self.fund_name:
            return f"{product_name} ({self.fund_name}) for {self.client.name}"
        return f"{product_name} for {self.client.name}"
