#!/home/b/b381815/miniconda3/envs/py/bin/python
from script_main import main_lineplot, main_barplot
from core.bluesky import post
from core.text import (
    get_default_text_line, 
    get_default_text_bar,
    get_image_alt_line, 
    get_image_alt_bar, 
)
from core.utilities import (
    add_license, 
    get_location_coordinates,
)


fn_line, info = main_lineplot(
    location=get_location_coordinates('Hamburg'),
    language='dt',
)
text_line = get_default_text_line(info)
alt_line = get_image_alt_line(info)

fn_bar = main_barplot(info)
text_bar = get_default_text_bar(info)
alt_bar = get_image_alt_bar(info)

bsky = post(fn_line, text_line, alt_line, langs=info['metadata']['language'])
_ = post(fn_bar, text_bar, alt_bar, reply_root=bsky, langs=info['metadata']['language'])

