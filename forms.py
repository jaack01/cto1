from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional


class InventoryItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    category = SelectField('Category', 
                          choices=[
                              ('detergent', 'Detergent'),
                              ('softener', 'Fabric Softener'),
                              ('bleach', 'Bleach'),
                              ('stain_remover', 'Stain Remover'),
                              ('supplies', 'General Supplies'),
                              ('packaging', 'Packaging Materials'),
                              ('other', 'Other')
                          ],
                          validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    unit = SelectField('Unit',
                      choices=[
                          ('kg', 'Kilograms'),
                          ('liters', 'Liters'),
                          ('pieces', 'Pieces'),
                          ('bottles', 'Bottles'),
                          ('boxes', 'Boxes'),
                          ('packs', 'Packs')
                      ],
                      validators=[DataRequired()])
    reorder_level = FloatField('Reorder Level', validators=[DataRequired(), NumberRange(min=0)])
    cost_per_unit = FloatField('Cost Per Unit', validators=[Optional(), NumberRange(min=0)])
    supplier = StringField('Supplier', validators=[Optional()])


class AdjustmentForm(FlaskForm):
    transaction_type = SelectField('Transaction Type',
                                   choices=[
                                       ('purchase', 'Purchase/Restock'),
                                       ('usage', 'Usage/Consumption'),
                                       ('adjustment', 'Manual Adjustment'),
                                       ('damage', 'Damage/Loss'),
                                       ('return', 'Return to Supplier')
                                   ],
                                   validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired()])
    reference_type = StringField('Reference Type', validators=[Optional()])
    reference_id = StringField('Reference ID', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
