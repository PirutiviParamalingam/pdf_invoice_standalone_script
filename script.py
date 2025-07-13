import os
import platform
from pathlib import Path
from jinja2 import Environment
from weasyprint import HTML

# -------- Order Data --------
order_data = {
    "order_number": "INV-1001",
    "po_number": "PO-7890",
    "created_at": "2025-07-01",
    "billing_address": {
        "name": "John Doe",
        "address1": "123 Street Name",
        "city": "Sydney",
        "zip": "2000",
        "country": "Australia"
    },
    "shipping_address": {
        "name": "John Doe",
        "address1": "123 Street Name",
        "city": "Sydney",
        "zip": "2000",
        "country": "Australia",
        "phone": "+61 400 123 456"
    },
    "line_items": [
        {
            "quantity": 2,
            "title": "Keyboard",
            "original_price": 50,
            "final_price": 40,
            "line_level_discount_allocations": [
                {"discount_application": {"title": "10% Off"}, "amount": 10}
            ]
        },
        {
            "quantity": 1,
            "title": "Mouse",
            "original_price": 30,
            "final_price": 30,
            "line_level_discount_allocations": []
        }
    ],
    "line_items_subtotal_price": 110,
    "total_price": 115,
    "tax_price": 5,
    "shipping_price": 0,
    "net_payment": 115,
    "discount_applications": [],
    "note": "Deliver ASAP."
}

shop_data = {
    "address": "BITSmart HQ, 456 Tech Park, Sydney, Australia",
    "phone": "+61 411 111 111"
}

# -------- Jinja2 Filters --------
def money(value):
    return "${:,.2f}".format(float(value))

def file_url(filename):
    # Converts static path to file:/// URI
    static_path = os.path.abspath("static")
    return Path(static_path, filename).as_uri()

def format_address(address):
    return f"{address.get('name', '')}<br>{address.get('address1', '')}<br>{address.get('city', '')} {address.get('zip', '')}<br>{address.get('country', '')}"

# -------- HTML Template --------
invoice_template = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Invoice</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      font-size: 14px;
      margin: 40px;
    }
    /* Light horizontal lines only */
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 1em;
    }
    thead tr {
      border-top: 1px solid #ddd;
      border-bottom: 1px solid #ddd;
    }
    tbody tr {
      border-bottom: 1px solid #ddd;
    }
    th, td {
      padding: 12px;
      text-align: left;
    }
    th.price, td.price {
      text-align: right;
    }
    /* Remove vertical column borders */
    table, th, td {
      border-left: none !important;
      border-right: none !important;
      border-style: none !important;
    }
  </style>
</head>
<body>
  <!-- Header -->
  <div style="margin-top: 1.5em; margin-bottom: 1.5em;">
    <img src="{{ 'bitsmart.svg' | file_url }}" style="width: 210px;">
    <p style="margin-top: 1.5em;">
      <strong style="font-size: 1.7em; color: #00B67A;">FOR ALL THINGS TECH</strong><br />
      Visit: <a href="https://bits-mart.com/" target="_blank" style="text-decoration: none;">bits-mart.com</a>
      {% if shop.phone %}<br /> Phone: {{ shop.phone }}{% endif %}
    </p>
  </div>

  <!-- Invoice Header -->
  <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-top: 2em;">
    <h1 style="margin: 0;">Tax Invoice</h1>
    <div style="text-align: right;">
      <p style="margin: 0;">
        <strong>Invoice Number: {{ order.order_number }}</strong><br />
        {% if order.po_number %}PO: {{ order.po_number }}<br />{% endif %}
        Invoice Date: {{ order.created_at }}
      </p>
    </div>
  </div>

  <!-- Addresses -->
  <div style="display: flex; justify-content: space-between; margin-top: 2em;">
    <div style="width: 30%;">
      <strong>From</strong><br/>
      {{ shop.address }}<br/>
      ABN: 90 628 950 676
    </div>
    {% if order.billing_address %}
    <div style="width: 30%;">
      <strong>Bill to</strong><br/>
      {{ order.billing_address | format_address }}
    </div>
    {% endif %}
    {% if order.shipping_address %}
    <div style="width: 30%;">
      <strong>Ship to</strong><br/>
      {{ order.shipping_address | format_address }}
      {% if order.shipping_address.phone %}<br>{{ order.shipping_address.phone }}{% endif %}
    </div>
    {% endif %}
  </div>

  <hr style="margin: 2em 0;" />

  <!-- Order Table -->
  <h2>Order Details</h2>
  <table>
    <thead>
      <tr>
        <th>Qty</th>
        <th>Item</th>
        <th class="price">Price</th>
      </tr>
    </thead>
    <tbody>
      {% for item in order.line_items %}
      <tr>
        <td>{{ item.quantity }}</td>
        <td>
          {{ item.title }} <br>
          {% if item.line_level_discount_allocations %}
          <div style="font-size: 12px; color: gray;">
            {% for discount in item.line_level_discount_allocations %}
              <br>{{ discount.discount_application.title }} (-{{ discount.amount | money }})
            {% endfor %}
          </div>
          {% endif %}
        </td>
        <td class="price">
          {% if item.original_price != item.final_price %}
            <span style="text-decoration: line-through; color: gray;">{{ item.original_price | money }}</span><br>
          {% endif %} <br>
          {{ item.final_price | money }}
        </td>
      </tr>
      {% endfor %}

      <!-- Totals -->
      <tr>
        <td colspan="2" style="text-align: right; padding: 12px;">Subtotal</td>
        <td class="price">{{ order.line_items_subtotal_price | money }}</td>
      </tr>
      <tr>
        <td colspan="2" style="text-align: right; padding: 12px;">Tax</td>
        <td class="price">{{ order.tax_price | money }}</td>
      </tr>
      <tr>
        <td colspan="2" style="text-align: right; padding: 12px;">Shipping</td>
        <td class="price">{% if order.shipping_price == 0 %}FREE{% else %}{{ order.shipping_price | money }}{% endif %}</td>
      </tr>
      <tr>
        <td colspan="2" style="text-align: right; padding: 12px;"><strong>Total</strong></td>
        <td class="price"><strong>{{ order.total_price | money }}</strong></td>
      </tr>
      <tr>
        <td colspan="2" style="text-align: right; padding: 12px;">Total Paid</td>
        <td class="price">{{ order.net_payment | money }}</td>
      </tr>
    </tbody>
  </table>

  <!-- Note -->
  {% if order.note %}
  <div style="margin-top: 2em;">
    <strong>Note:</strong><br />
    {{ order.note }}
  </div>
  {% endif %}

  <p style="margin-top: 2em;">
    If you have any questions, please send an email to
    <a href="mailto:accounts@bits-mart.com?subject=BITSmart%20Order%20{{ order.order_number }}"
       style="text-decoration: none; color: #000;">
       <strong>accounts@bits-mart.com</strong>
    </a>
  </p>
</body>
</html>
"""

# -------- Render Template --------
env = Environment()
env.filters["money"] = money
env.filters["file_url"] = file_url
env.filters["format_address"] = format_address

template = env.from_string(invoice_template)
html_out = template.render(order=order_data, shop=shop_data)

# -------- Save PDF to Downloads Folder --------
def get_downloads_folder():
    if platform.system() == "Windows":
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    else:
        return str(Path.home() / "Downloads")

downloads_folder = get_downloads_folder()
pdf_filename = f"invoice_{order_data['order_number']}.pdf"
pdf_path = os.path.join(downloads_folder, pdf_filename)

# -------- Generate PDF --------
HTML(string=html_out).write_pdf(pdf_path)
print(f"✅ Invoice PDF saved to: {pdf_path}")
