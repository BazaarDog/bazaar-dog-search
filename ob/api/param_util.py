def build_checkbox(checked, label):
    return [
        {
            "value": True,
            "label": label,
            "checked": checked,
            "default": False
        }
    ]

def build_options(selected, options):
    return [
        {
            "value": k,
            "label": v,
            "checked": k == selected,
            "default": False
        } for k, v in options.items()
    ]
