# Scripts
Some script I wrote to do some automation stuffs.

## File processing
- BatchCompress: go into each folder and compress everything inside into zip or 7z and move the archive `../`
- BatchHarExtractor (to be upgraded)
- BatchJXL: batch convert images in the working folder to `.jxl`
  - Require: cjxl and djxl in path, download @ [github](https://github.com/libjxl/libjxl/releases) or [artifacts.lucaversari.it](https://artifacts.lucaversari.it/libjxl/libjxl/latest/) (dev's personal page)
- MoveNewLargerFile: comparing sizes of 2 same-name file. If a pair has a new larger file, both of them will be moved into the `newFilesBigger` folder (auto create if not exist)

## Image processing
- BatchUpscale:
- BatchMKV2HLS: spliting multiple MKV into HLS streams
- ComparePNG: compare differences of two PNG files
- merge-all-mp4: merge all segments of videos in folder(s) in working folder to mp4

## Video processing

- SortByDimension: sort images in the working folder by their dimensions
  - Require: [Pillow](https://pypi.org/project/Pillow/)