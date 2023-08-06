# Scripts

- `batch_compress`: go into each folder and compress everything inside into `zip`/`7z` and move the archive `../`
- `batch_jxl`: batch convert images in the working folder to `.jxl`
  - Require: cjxl and djxl in path, download @ [github](https://github.com/libjxl/libjxl/releases) or [artifacts.lucaversari.it](https://artifacts.lucaversari.it/libjxl/libjxl/latest/) (dev's personal page)
- `batch_mkv_2_hls`: spliting multiple MKV into HLS streams
- `batch_resize`: batch resize images
- `cctv_toolbox`: concat all segments of videos in folder(s) in working folder to mp4

## Deprecated
- `batch_avif`: batch convert images in the working folder to `.avif`
  - Require: `ffmpeg`, `aomenc`, `mp4box`
- `batch_har_extractor`: extract all `.har` files in the working folder to folders
  - Require: [har-extractor](https://github.com/azu/har-extractor)
- `compare_png`: MSE, SSIM
- `complete`: early implementation of [gallery-preprocessor](https://github.com/Delnegend/gallery-preprocessor-go)
- `merge_all_mp4`: same as `cctv_toolbox`
- `move_new_larger_file`: compare 2 same-name, different-extension files and move the larger one to the other's folder
- `push`: split video into segments and upload to GitLab
- `resize`: resize image using [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) then transcode to `jxl/avif/webp/jpg/png`
- `sort_by_dimension`: sort images in the working folder by their dimensions
  - Require: [Pillow](https://pypi.org/project/Pillow/)
- `upscale_frames`: export frames from a video then upscale them using [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)