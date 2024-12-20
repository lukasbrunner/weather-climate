from script_main import main
from core.bluesky import post

fn, get_statistics = main()
post(fn)
