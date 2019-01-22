from collections import OrderedDict
from ob.models import Listing, Profile
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from .util import build_options, build_checkbox
from .common import get_nsfw_options, get_currency_type_options, get_clear_all_options


def get_listing_options(params):
    available_options = [
        ("acceptedCurrencies", {
            "type": "checkbox",
            "label": _("Accepted Currencies"),
            "options": get_currency_type_options(params)
        }),
        ("moderator_verified", {
            "type": "checkbox",
            "label": _("Verified Moderator"),
            "options": get_moderator_verified_options(params)
        }),
        ("moderator_count", {
            "type": "radio",
            "label": _("Moderators Available"),
            "options": get_moderator_options(params)
        }),
        ("nsfw", {
            "type": "radio",
            "label": _("Adult Content"),
            "options": get_nsfw_options(params)
        }),
        ("condition_type", {
            "type": "radio",
            "label": _("Condition"),
            "options": get_condition_type_options(params)
        }),
        ("rating", {
            "type": "radio",
            "label": _("Rating"),
            "options": get_rating_options(params)
        }),
        ("contract_type", {
            "type": "radio",
            "label": _("Type"),
            "options": get_contract_type_options(params)
        }),
        ("shipping", {
            "type": "dropdown",
            "label": _("Ships to"),
            "options": get_region_options(params)
        }),
        ("free_shipping_region", {
            "type": "checkbox",
            "label": _("Ships Free"),
            "options": get_free_shipping_options(params)
        }),
        ("connection", {
            "type": "radio",
            "label": _("Connection Type (Alpha)"),
            "options": get_connection_options(params)
        }),
        ("network", {
            "type": "radio",
            "label": _("Network"),
            "options": get_network_options(params)
        }),
        ("dust", {
            "type": "checkbox",
            "label": _("Show Dust"),
            "options": get_dust_options(params)
        }),
        ("clear_all", {
            "type": "checkbox",
            "label": _("Reset"),
            "options": get_clear_all_options()
        }),
    ]

    if settings.DEV:
        from .dev import get_debug_options
        available_options += get_debug_options(params)

    options = OrderedDict(available_options)

    return options


def get_moderator_verified_options(params):
    # Build verified moderator options

    if 'moderator_verified' in params.keys():
        try:
            if params['moderator_verified'] == 'true':
                moderator_verified = True
            elif params['moderator_verified'] == 'false':
                moderator_verified = ''
            elif params['moderator_verified'] == '':
                moderator_verified = ''
            else:
                moderator_verified = ''
        except ValueError:
            moderator_verified = ''
    else:
        moderator_verified = ''

    moderator_verified_choices = OrderedDict([(True, 'OB1 Verified Moderator'), ])

    return build_options(moderator_verified, moderator_verified_choices)


def get_moderator_options(params):

    # Build number of moderator options

    if 'moderator_count' in params.keys():
        try:
            moderator_count = int(params['moderator_count'])
        except ValueError:
            moderator_count = 0
    else:
        moderator_count = 0

    moderator_options = [
        {
            "value": v,
            "label": '\u2696' * v + ' ' + str(v) + '+',
            "checked": v == moderator_count,
            "default": False
        } for v in range(3, -1, -1)
    ]
    moderator_options[1]['default'] = True

    return moderator_options


def get_region(params):

    return params['shipping'] if 'shipping' in params.keys() else 'any'


def get_region_options(params):

    region = get_region(params)

    distinct_region = OrderedDict(
        [
            ("", "(Any country)"), ("united_states", "🇺🇸 United States of America (The)"),
            ("india", "🇮🇳 India"), ("nigeria", "🇳🇬 Nigeria"),
            ("china", "🇨🇳 China"), ("russia", "🇷🇺 Russia"), ("afghanistan", "🇦🇫 Afghanistan"),
            ("aland_islands", "🇦🇽 Åland Islands"), ("albania", "🇦🇱 Albania"), ("algeria", "🇩🇿 Algeria"),
            ("american_samoa", "🇦🇸 American Samoa"), ("andorra", "🇦🇩 Andorra"), ("angola", "🇦🇴 Angola"),
            ("anguilla", "🇦🇮 Anguilla"), ("antigua", "🇦🇬 Antigua and Barbuda"), ("argentina", "🇦🇷 Argentina"),
            ("armenia", "🇦🇲 Armenia"), ("aruba", "🇦🇼 Aruba"), ("australia", "🇦🇺 Australia"),
            ("austria", "🇦🇹 Austria"), ("azerbaijan", "🇦🇿 Azerbaijan"), ("bahamas", "🇧🇸 Bahamas (The)"),
            ("bahrain", "🇧🇭 Bahrain"), ("bangladesh", "🇧🇩 Bangladesh"), ("barbados", "🇧🇧 Barbados"),
            ("belarus", "🇧🇾 Belarus"), ("belgium", "🇧🇪 Belgium"), ("belize", "🇧🇿 Belize"),
            ("benin", "🇧🇯 Benin"), ("bermuda", "🇧🇲 Bermuda"), ("bhutan", "🇧🇹 Bhutan"),
            ("bolivia", "🇧🇴 Bolivia (Plurinational State of)"),
            ("bonaire_sint_eustatius_saba", "🏴󠁮󠁬󠁢󠁱󠀳󠁿 Bonaire, Sint Eustatius and Saba"),
            ("bosnia", "🇧🇦 Bosnia and Herzegovina"), ("botswana", "🇧🇼 Botswana"),
            ("bouvet_island", "🇧🇻 Bouvet Island"), ("brazil", "🇧🇷 Brazil"),
            ("british_indian_ocean_territory", "🇮🇴 British Indian Ocean Territory (The)"),
            ("brunei_darussalam", "🇧🇳 Brunei Darussalam"), ("bulgaria", "🇧🇬 Bulgaria"),
            ("burkina_faso", "🇧🇫 Burkina Faso"), ("burundi", "🇧🇮 Burundi"), ("cabo_verde", "🇨🇻 Cabo Verde"),
            ("cambodia", "🇰🇭 Cambodia"), ("cameroon", "🇨🇲 Cameroon"), ("canada", "🇨🇦 Canada"),
            ("cayman_islands", "🇰🇾 Cayman Islands (The)"),
            ("central_african_republic", "🇨🇫 Central African Republic (The)"), ("chad", "🇹🇩 Chad"),
            ("chile", "🇨🇱 Chile"), ("christmas_island", "🇨🇽 Christmas Island"),
            ("cocos_islands", "🇨🇨 Cocos (KEELING) Islands (The)"), ("colombia", "🇨🇴 Colombia"),
            ("comoros", "🇰🇲 Comoros (The)"), ("congo_republic", "🇩🇴 Congo (The Democratic Republic of the)"),
            ("congo", "🇨🇩 Congo (The)"), ("cook_islands", "🇨🇰 Cook Islands (The)"),
            ("costa_rica", "🇨🇷 Costa Rica"), ("cote_divoire", "🇨🇮 Cte D'Ivoire"), ("croatia", "🇭🇷 Croatia"),
            ("cuba", "🇨🇺 Cuba"), ("curacao", "🇨🇼 Curaçao"), ("cyprus", "🇨🇾 Cyprus"),
            ("czech_republic", "🇨🇿 Czech Republic (The)"), ("denmark", "🇩🇰 Denmark"),
            ("djibouti", "🇩🇯 Djibouti"), ("dominica", "🇩🇲 Dominica"),
            ("dominican_republic", "🇩🇴 Dominican Republic (The)"), ("ecuador", "🇪🇨 Ecuador"),
            ("egypt", "🇪🇬 Egypt"), ("el_salvador", "🇸🇻 El Salvador"),
            ("equatorial_guinea", "🇬🇶 Equatorial Guinea"), ("eritrea", "🇪🇷 Eritrea"), ("estonia", "🇪🇪 Estonia"),
            ("ethiopia", "🇪🇹 Ethiopia"), ("falkland_islands", "🇫🇰 Falkland Islands (The)"),
            ("faroe_islands", "🇫🇴 Faroe Islands (The)"), ("fiji", "🇫🇯 Fiji"), ("finland", "🇫🇮 Finland"),
            ("france", "🇫🇷 France"), ("french_guiana", "🇬🇫 French Guiana"),
            ("french_polynesia", "🇵🇫 French Polynesia"),
            ("french_southern_territories", "🇹🇫 French Southern Territories (The)"), ("gabon", "🇬🇦 Gabon"),
            ("gambia", "🇬🇲 Gambia (The)"), ("georgia", "🇬🇪 Georgia"), ("germany", "🇩🇪 Germany"),
            ("ghana", "🇬🇭 Ghana"), ("gibraltar", "🇬🇮 Gibraltar"), ("greece", "🇬🇷 Greece"),
            ("greenland", "🇬🇱 Greenland"), ("grenada", "🇬🇩 Grenada"), ("guadeloupe", "🇬🇵 Guadeloupe"),
            ("guam", "🇬🇺 Guam"), ("guatemala", "🇬🇹 Guatemala"), ("guernsey", "🇬🇬 Guernsey"),
            ("guinea", "🇬🇳 Guinea"), ("guinea_bissau", "🇬🇼 Guinea-Bissau"), ("guyana", "🇬🇾 Guyana"),
            ("haiti", "🇭🇹 Haiti"), ("heard_island", "🇭🇲 Heard Island and McDonald Islands"),
            ("holy_see", "🇻🇦 Holy See (The)"), ("honduras", "🇭🇳 Honduras"), ("hong_kong", "🇭🇰 Hong Kong"),
            ("hungary", "🇭🇺 Hungary"), ("iceland", "🇮🇸 Iceland"),
            ("indonesia", "🇮🇩 Indonesia"), ("iran", "🇮🇷 Iran (Islamic Republic of)"), ("iraq", "🇮🇶 Iraq"),
            ("ireland", "🇮🇪 Ireland"), ("isle_of_man", "🇮🇲 Isle of Man"), ("israel", "🇮🇱 Israel"),
            ("italy", "🇮🇹 Italy"), ("jamaica", "🇯🇲 Jamaica"), ("japan", "🇯🇵 Japan"), ("jersey", "🇯🇪 Jersey"),
            ("jordan", "🇯🇴 Jordan"), ("kazakhstan", "🇰🇿 Kazakhstan"), ("kenya", "🇰🇪 Kenya"),
            ("kiribati", "🇰🇮 Kiribati"), ("north_korea", "🇰🇵 Korea (The Democratic People's Republic of)"),
            ("south_korea", "🇰🇷 Korea (The Republic of)"), ("kuwait", "🇰🇼 Kuwait"),
            ("kyrgyzstan", "🇰🇬 Kyrgyzstan"), ("lao", "🇱🇦 Lao People's Democratic Republic (The)"),
            ("latvia", "🇱🇻 Latvia"), ("lebanon", "🇱🇧 Lebanon"), ("lesotho", "🇱🇸 Lesotho"),
            ("liberia", "🇱🇷 Liberia"), ("libya", "🇱🇾 Libya"), ("liechtenstein", "🇱🇮 Liechtenstein"),
            ("lithuania", "🇱🇹 Lithuania"), ("luxembourg", "🇱🇺 Luxembourg"), ("macao", "🇲🇴 Macao"),
            ("macedonia", "🇲🇰 Macedonia (The Former Yugoslav Republic of)"), ("madagascar", "🇲🇬 Madagascar"),
            ("malawi", "🇲🇼 Malawi"), ("malaysia", "🇲🇾 Malaysia"), ("maldives", "🇲🇻 Maldives"),
            ("mali", "🇲🇱 Mali"), ("malta", "🇲🇹 Malta"), ("marshall_islands", "🇲🇭 Marshall Islands (The)"),
            ("martinique", "🇲🇶 Martinique"), ("mauritania", "🇲🇷 Mauritania"), ("mauritius", "🇲🇺 Mauritius"),
            ("mayotte", "🇾🇹 Mayotte"), ("mexico", "🇲🇽 Mexico"),
            ("micronesia", "🇫🇲 Micronesia (Federated States of)"), ("moldova", "🇲🇩 Moldova (The Republic of)"),
            ("monaco", "🇲🇨 Monaco"), ("mongolia", "🇲🇳 Mongolia"), ("montenegro", "🇲🇪 Montenegro"),
            ("montserrat", "🇲🇸 Montserrat"), ("morocco", "🇲🇦 Morocco"), ("mozambique", "🇲🇿 Mozambique"),
            ("myanmar", "🇲🇲 Myanmar"), ("namibia", "🇳🇦 Namibia"), ("nauru", "🇳🇷 Nauru"), ("nepal", "🇳🇵 Nepal"),
            ("netherlands", "🇳🇱 Netherlands (The)"), ("new_caledonia", "🇳🇨 New Caledonia"),
            ("new_zealand", "🇳🇿 New Zealand"), ("nicaragua", "🇳🇮 Nicaragua"), ("niger", "🇳🇪 Niger (The)"),
            ("niue", "🇳🇺 Niue"), ("norfolk_island", "🇳🇫 Norfolk Island"),
            ("northern_mariana_islands", "🇲🇵 Northern Mariana Islands (The)"), ("norway", "🇳🇴 Norway"),
            ("oman", "🇴🇲 Oman"), ("pakistan", "🇵🇰 Pakistan"), ("palau", "🇵🇼 Palau"), ("panama", "🇵🇦 Panama"),
            ("papua_new_guinea", "🇵🇬 Papua New Guinea"), ("paraguay", "🇵🇾 Paraguay"), ("peru", "🇵🇪 Peru"),
            ("philippines", "🇵🇭 Philippines (The)"), ("pitcairn", "🇵🇳 Pitcairn"), ("poland", "🇵🇱 Poland"),
            ("portugal", "🇵🇹 Portugal"), ("puerto_rico", "🇵🇷 Puerto Rico"), ("qatar", "🇶🇦 Qatar"),
            ("reunion", "🇷🇪 Réunion"), ("romania", "🇷🇴 Romania"), ("rwanda", "🇷🇼 Rwanda"),
            ("saint_barthelemy", "🇧🇱 Saint Barthélemy"),
            ("saint_helena", "🇸🇭 Saint Helena, Ascension and Tristan da Cunha"),
            ("saint_kitts", "🇰🇳 Saint Kitts and Nevis"), ("saint_lucia", "🇱🇨 Saint Lucia"),
            ("saint_martin", "🇲🇫 Saint Martin (French Part)"), ("saint_pierre", "🇵🇲 Saint Pierre and Miquelon"),
            ("saint_vincent", "🇻🇨 Saint Vincent and The Grenadines"), ("samoa", "🇼🇸 Samoa"),
            ("san_marino", "🇸🇲 San Marino"), ("sao_tome", "🇸🇹 São Tomé \u0026 Príncipe"),
            ("saudi_arabia", "🇸🇦 Saudi Arabia"), ("senegal", "🇸🇳 Senegal"), ("serbia", "🇷🇸 Serbia"),
            ("seychelles", "🇸🇨 Seychelles"), ("sierra_leone", "🇸🇱 Sierra Leone"), ("singapore", "🇸🇬 Singapore"),
            ("sint_maarten", "🇸🇽 Sint Maarten (Dutch Part)"),
            ("sucre", "Sistema Unitario de Compensacion Regional de Pagos 'Sucre"), ("slovakia", "🇸🇰 Slovakia"),
            ("slovenia", "🇸🇮 Slovenia"), ("solomon_islands", "🇸🇧 Solomon Islands"), ("somalia", "🇸🇴 Somalia"),
            ("south_africa", "🇿🇦 South Africa"), ("south_sudan", "🇸🇸 South Sudan"), ("spain", "🇪🇸 Spain"),
            ("sri_lanka", "🇱🇰 Sri Lanka"), ("sudan", "🇸🇩 Sudan (The)"), ("suriname", "🇸🇷 Suriname"),
            ("svalbard", "🇸🇯 Svalbard and Jan Mayen"), ("swaziland", "🇸🇿 Swaziland"), ("sweden", "🇸🇪 Sweden"),
            ("switzerland", "🇨🇭 Switzerland"), ("syrian_arab_republic", "Syrian Arab Republic"),
            ("taiwan", "🇹🇼 Taiwan"), ("tajikistan", "🇹🇯 Tajikistan"),
            ("tanzania", "🇹🇿 Tanzania, United Republic of"), ("thailand", "🇹🇭 Thailand"),
            ("timor_leste", "🇹🇱 Timor-Leste"), ("togo", "🇹🇬 Togo"), ("tokelau", "🇹🇰 Tokelau"),
            ("tonga", "🇹🇴 Tonga"), ("trinidad", "🇹🇹 Trinidad and Tobago"), ("tunisia", "🇹🇳 Tunisia"),
            ("turkey", "🇹🇷 Turkey"), ("turkmenistan", "🇹🇲 Turkmenistan"),
            ("turks_and_caicos_islands", "🇹🇨 Turks \u0026 Caicos Islands (The)"), ("tuvalu", "🇹🇻 Tuvalu"),
            ("uganda", "🇺🇬 Uganda"), ("ukraine", "🇺🇦 Ukraine"),
            ("united_arab_emirates", "🇦🇪 United Arab Emirates (The)"),
            ("united_kingdom", "🇬🇧 United Kingdom of Great Britain and Northern Ireland (The)"),
            ("uruguay", "🇺🇾 Uruguay"), ("uzbekistan", "🇺🇿 Uzbekistan"), ("vanuatu", "🇻🇺 Vanuatu"),
            ("venezuela", "🇲🇻 Venezuela (Bolivarian Republic Of)"), ("vietnam", "🇻🇳 Vietnam"),
            ("virgin_islands_british", "🇻🇬 Virgin Islands (British)"),
            ("virgin_islands_us", "🇻🇮 Virgin Islands (U.S.)"), ("wallis_and_futuna", "🇼🇫 Wallis and Futuna"),
            ("western_sahara", "🇪🇭 Western Sahara"), ("yemen", "🇾🇪 Yemen"), ("zambia", "🇿🇲 Zambia"),
            ("zimbabwe", "🇿🇼 Zimbabwe")
        ]
    )

    return build_options(region, distinct_region)


def get_free_shipping_options(params):
    region = get_region(params)
    # Free shipping

    if 'free_shipping_region' in params.keys():
        try:
            if params['free_shipping_region'] == 'true':
                free_shipping = True
            else:
                free_shipping = ''
        except ValueError:
            free_shipping = ''
    else:
        free_shipping = ''

    if region and region.lower() != 'any':
        to_str = _('to {place}').format(place=region.title().replace('_', ' '))
        free_shipping_choices = OrderedDict([(True, to_str), ])
    else:
        free_shipping_choices = OrderedDict([(True, _('to Anywhere')), ])

    return build_options(free_shipping, free_shipping_choices)


def get_contract_type_options(params):

    # build contract type options

    if 'contract_type' in params.keys():
        try:
            contract = int(params['contract_type'])
        except ValueError:
            contract = ''
    else:
        contract = ''

    return build_options(contract, Listing.CONTRACT_TYPE_DICT)


def get_condition_type_options(params):

    # Build condition type options

    if 'condition_type' in params.keys():
        try:
            condition = int(params['condition_type'])
        except ValueError:
            condition = ''
    else:
        condition = ''

    return build_options(condition, Listing.CONDITION_TYPE_DICT)


def get_rating_options(params):
    # Ratings

    if 'rating' in params.keys():
        try:
            rating = float(params['rating'])
        except ValueError:
            rating = 0
    else:
        rating = 0

    return [
        {
            "value": v,
            "label": "{:.2f}".format(v) + ' >=',
            "checked": v == rating,
            "default": False
        } for v in [5.0, 4.95, 4.8, 4.5, 4.0, 0.0]
    ]


def get_connection_options(params):
    # Connection type

    if 'connection' in params.keys():
        try:
            connection = int(params['connection'])
        except ValueError:
            connection = ''
    else:
        connection = ''

    return build_options(connection, Profile.CONNECTION_TYPE_DICT)


def get_dust_options(params):
    # Dust

    if 'dust' in params.keys():
        try:
            if params['dust'] == 'true':
                dust = True
            else:
                dust = ''
        except ValueError:
            dust = ''
    else:
        dust = ''

    dust_choices = OrderedDict(
        [
            (True, _('> ~{percentage}% Bitcoin Fee').format(percentage=settings.DUST_FEE_PERCENT)),
        ]
    )

    return build_options(dust, dust_choices)


