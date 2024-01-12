from flask_wtf import FlaskForm
from wtforms import SubmitField, URLField
from wtforms.validators import URL, DataRequired, Length, Optional, Regexp


class URLForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле'),
                    URL(require_tld=True, message="Некорректная ссылка")]
    )
    custom_id = URLField(
        'Ваш вариант короткой ссылки',
        validators=[Length(1, 16),
                    Optional(),
                    Regexp(regex=r'^[A-Za-z0-9_]+$', message="Недопустимые символы")]
    )
    submit = SubmitField('Создать')
