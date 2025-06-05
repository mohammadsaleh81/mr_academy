def environment_callback(request):
    """
    Callback has to return a list of two values represeting text value and the color
    type of the label displayed in top right corner.
    """
    return ["Production", "danger"] # info, danger, warning, success



def dashboard_callback(request, context):
    context.update({
        "custom_variable": "value",
    })

    return context
