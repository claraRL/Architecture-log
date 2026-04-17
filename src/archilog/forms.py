from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length

class ExpenseForm(FlaskForm):
    # Validation syntaxique (FloatField) et sémantique (NumberRange > 0)
    paid_by = SelectField('Payé par', choices=[], validators=[DataRequired()])
    amount = FloatField('Montant', validators=[DataRequired(), NumberRange(min=0.01)])

class MoneyPotForm(FlaskForm):
    pot_name = StringField('Nom de la cagnotte', validators=[DataRequired(), Length(min=3)])
    # Pour l'ajout initial
    paid_by = StringField('Premier contributeur', validators=[DataRequired()])
    amount = FloatField('Montant', validators=[DataRequired(), NumberRange(min=0)])