from flask_wtf import FlaskForm
from wtforms import SubmitField, URLField
from wtforms.validators import URL, DataRequired, Length, Optional, Regexp

CUSTOM_ID_MIN_LENGTH = 1
CUSTOM_ID_MAX_LENGTH = 16


class URLForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле'),
                    URL(require_tld=True, message="Некорректная ссылка")]
    )
    custom_id = URLField(
        'Ваш вариант короткой ссылки',
        validators=[Length(CUSTOM_ID_MIN_LENGTH, CUSTOM_ID_MAX_LENGTH),
                    Optional(),
                    Regexp(regex=r'^[A-Za-z0-9_]+$', message="Недопустимые символы")]
    )
    submit = SubmitField('Создать')
