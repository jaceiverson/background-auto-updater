import os

from src.image_comparison.compare import main

# run
# export FAV_FILE_PATH={your_path_here}
favs = os.environ["FAV_FILE_PATH"]
main(favs)
