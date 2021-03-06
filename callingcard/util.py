from flask import current_app, request, Response, render_template
from textwrap import dedent
from functools import wraps


def get_twiml_params(f):
    """gets the twiml parameters from the JSON post body, or the GET params"""

    @wraps(f)
    def decorated(*args, **kwargs):
        param_dict = {
            "GET": request.args,
            "POST": request.form
        }
        twiml_params = param_dict.get(request.method, {})

        return f(twiml_params, *args, **kwargs)

    return decorated


def verify_caller_allowed(f):
    """verifies that caller is a permitted number"""

    @wraps(f)
    def decorated(twiml_params, *args, **kwargs):
        print twiml_params
        if "From" not in twiml_params:
            return render_template('invalid.xml')

        caller = twiml_params.get('From')
        permited_callers = current_app.config.get('PERMITTED_CALLERS')

        if caller not in permited_callers:
            return render_template('caller_not_permitted.xml')

        return f(twiml_params, *args, **kwargs)

    return decorated


def get_digits_entered(f):
    """gets the digits entered from the twiml_params"""

    @wraps(f)
    def decorated(twiml_params, *args, **kwargs):
        if "Digits" not in twiml_params:
            return render_template('invalid.xml')

        try:
            digits = int(twiml_params.get('Digits'))
        except ValueError:
            return render_template('invalid.xml')

        return f(twiml_params, digits, *args, **kwargs)

    return decorated


def produces_xml(f):
    """converts response txt to XML response object"""

    @wraps(f)
    def decorated(*args, **kwargs):
        xml = f(*args, **kwargs)
        return Response(dedent(xml), mimetype="text/xml")

    return decorated
