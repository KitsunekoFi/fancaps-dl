# Fancaps Downloader

Fancaps Downloader is a Python script that allows you to download images from the Fancaps.net website.

## Installation

To run this script, you must have Python 3.x installed on your computer. You also need to install the BeautifulSoup4 library by running the following command:

```pip install beautifulsoup4```

## Usage

You can run this script from the command line by providing the appropriate arguments. Here is a list of supported arguments:

- `url`: URL to open. This should be an episode or movie URL from the Fancaps.net website.
- `--bulk`: A txt file containing a list of URLs to process.
- `--user-agent`: User Agent to use. Default: `Mozilla/5.0`.
- `--max-workers`: Maximum number of worker threads to use for downloading files simultaneously. Default: `4`.
- `--output-folder`: Folder to save downloaded images. If not specified, the script will try to determine the output folder name automatically from the URL provided as the `url` argument or use the current working directory as the output folder if it cannot determine the output folder name from the URL.
- `--interval`: Interval of images to download. Default: `1`.
- `--same-folder`: Save all images to the same folder.
- `--each-folder`: Save images to separate subfolders for each URL. This is the default option.

Example usage:

```python fancaps-dl.py <Episode URL> --interval 5```



The above command will collect page links from a specific episode URL and then download only every fifth image from each URL to separate subfolders for each URL under a main folder determined automatically from the URL provided as a positional argument.

## Limitations

- Currently does not support movies
- There may still be many bugs

## To-do List

- Add support for movies
- Add support for zipping downloaded images
- Add support for renaming downloaded images
- Add support for multiple Fancaps titles

## License

This code is licensed under the MIT license.

