# Chapter to PDF Converter

A Python tool that converts zipped folders containing chapters with images into organized PDF files.

## Features

- **Processes zipped archives** containing multiple chapter folders
- **Automatically sorts chapters** by number (Chapter 1, Chapter 2, etc.)
- **Sorts images within chapters** by filename number (1.jpg, 2.jpg, etc.)
- **Converts images to PDF** with proper scaling and aspect ratio preservation
- **Creates individual chapter PDFs** for each chapter
- **Merges all chapters** into a single complete PDF
- **Supports multiple image formats**: JPG, PNG, BMP, GIF, TIFF

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line
```bash
python main.py <zip_file> [-o output_dir] [-n output_name]
```

**Examples:**
```bash
# Basic usage
python main.py manga.zip

# Specify output directory and name
python main.py manga.zip -o converted_pdfs -n my_manga

# Process a manga/comic book
python main.py "C:\Downloads\One Piece Vol 1.zip" -o manga_pdfs -n one_piece_vol1
```

### Interactive Mode
If you run the script without arguments, it will prompt you for the zip file path:
```bash
python main.py
```

## Expected Zip File Structure

```
manga.zip
├── Chapter 1/
│   ├── 1.jpg
│   ├── 2.jpg
│   ├── 3.jpg
│   └── ...
├── Chapter 2/
│   ├── 1.jpg
│   ├── 2.jpg
│   └── ...
├── Chapter 3/
│   └── ...
└── Chapter 10/
    └── ...
```

## Output

The tool creates:

1. **Individual chapter PDFs**: `output_name_chapter_01_Chapter 1.pdf`
2. **Complete merged PDF**: `output_name_complete.pdf`

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)
- TIFF (.tiff)

## Features in Detail

### Automatic Sorting
- Chapters are sorted numerically (Chapter 1, Chapter 2, Chapter 10)
- Images within chapters are sorted by number (1.jpg, 2.jpg, 10.jpg)

### Image Processing
- Maintains aspect ratio when scaling images to fit PDF pages
- Converts RGBA/transparency images to RGB for PDF compatibility
- Centers images on A4 pages with appropriate margins

### Error Handling
- Skips corrupted or unreadable images
- Continues processing even if some images fail
- Provides detailed progress and error messages

## Dependencies

- **Pillow**: Image processing and manipulation
- **reportlab**: PDF generation and image embedding
- **PyPDF2**: PDF merging (optional but recommended)

## Troubleshooting

### Common Issues

1. **"No images found"**: Check that your zip contains folders with image files
2. **"Invalid file path"**: Ensure the zip file path is correct and accessible
3. **PDF merging issues**: Install PyPDF2 for better PDF merging: `pip install PyPDF2`

### Performance Tips

- For large collections, process one volume/series at a time
- Ensure sufficient disk space (images can be large)
- Use SSD storage for faster processing

## Example Use Cases

- **Manga/Comic conversion**: Convert downloaded manga chapters to PDF
- **Scanned documents**: Organize scanned book chapters
- **Digital comics**: Process CBZ-like archives
- **Art portfolios**: Convert image collections to PDF books
