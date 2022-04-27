# Scripts
Some script I wrote to do some automation stuffs.

- BatchCompress: compress file(s) and folder(s) in folder(s) (not the folder(s) themselves) in the working folder to `zip`

  - <details>
    <summary>Visualization</summary>

    - Before
        ```
        working-folder
        │  BatchCompress.py
        │
        |__folder1
        │  │   file011.txt
        │  │   file012.txt
        │  │
        │  └───subfolder1
        │      │   file111.txt
        │      │   file112.txt
        │      │   ...
        └───folder2
          │   file021.txt
          │   file022.txt
        ```
    - After
      ```
      working-folder
      │  BatchCompress.py
      │
      |__folder1
      |  |...
      |  folder2
      |  |...
      |
      |__folder1.zip
      │  │   file011.txt
      │  │   file012.txt
      │  │
      │  └───subfolder1
      │      │   file111.txt
      │      │   file112.txt
      │      │   ...
      └───folder2.zip
        │   file021.txt
        │   file022.txt
      ```
  </details>

  - Usages: specify `7z` to compress to `7z`
    ```
    BatchCompress.py [7z]
    ```
- BatchHarExtractor (to be upgraded)
- BatchJXL: batch convert images in the working folder to `.jxl`
  - Require: cjxl and djxl in path, download @ [github](https://github.com/libjxl/libjxl/releases) or [artifacts.lucaversari.it](https://artifacts.lucaversari.it/libjxl/libjxl/latest/) (dev's personal page)
  - Usages: specify `-d` to convert back to png
    ```
    BatchJXL.py [-d]
    ```
- BatchMKV2HLS: spliting multiple MKV into HLS streams
- ComparePNG: compare differences of two PNG files
- merge-all-mp4: merge all segments of videos in folder(s) in working folder to mp4

  - <details>
    <summary>Visualization</summary>

    - Before
        ```
        📁 working-folder
        │  merge-all-mp4.bat
        │
        |__📁 VID1
        │  │   seg1.mp4
        │  │   seg2.mp4
        │  │
        │  └───📁 subfolder1
        │      │   seg3.mp4
        │      │   seg4.mp4
        │      │   ...
        └───📁 VID2
          │   seg1.mp4
          │   seg2.mp4
        ```
    - After
      ```
        📁 working-folder
        │  merge-all-mp4.bat
        │  VID1.mp4
        |  VID2.mp4
        |__📁 VID1
        │  │   seg1.mp4
        │  │   seg2.mp4
        │  │
        │  └───📁 subfolder1
        │      │   seg3.mp4
        │      │   seg4.mp4
        │      │   ...
        └───📁 VID2
          │   seg1.mp4
          │   seg2.mp4
      ```
  </details>

- MoveNewLargerFile: comparing sizes of 2 same-name file. If a pair has a new larger file, both of them will be moved into the `newFilesBigger` folder (auto create if not exist)

- SortByDimension: sort images in the working folder by their dimensions
  - Require: [Pillow](https://pypi.org/project/Pillow/)