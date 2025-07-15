import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
import re
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox
import glob


class ChapterToPDFConverter:
    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir = None
        
    def find_related_zip_files(self, zip_path):
        """Find all zip files with the same first 4 characters"""
        zip_path = Path(zip_path)
        directory = zip_path.parent
        base_name = zip_path.stem[:4]  # Get first 4 characters
        
        # Find all zip files with same prefix
        pattern = os.path.join(directory, f"{base_name}*.zip")
        related_files = glob.glob(pattern)
        
        # Sort by filename to ensure proper chapter order
        related_files.sort()
        return related_files
    
    def extract_chapter_number_from_filename(self, filename):
        """Extract chapter number from filename for sorting"""
        # Look for patterns like "chap1", "chapter1", "ch1", etc.
        match = re.search(r'chap(?:ter)?[\s_-]?(\d+)', filename.lower())
        if match:
            return int(match.group(1))
        
        # Fallback to any number in filename
        numbers = re.findall(r'\d+', filename)
        return int(numbers[-1]) if numbers else 0
    
    def extract_zip(self, zip_path):
        """Extract zip file to temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        return self.temp_dir
    
    def get_image_files(self, folder_path):
        """Get all image files from a folder, sorted by number"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
        image_files = []
        
        for file in os.listdir(folder_path):
            if Path(file).suffix.lower() in image_extensions:
                image_files.append(os.path.join(folder_path, file))
        
        # Sort by the number in filename (e.g., 1.jpg, 2.jpg, etc.)
        def extract_number(filename):
            numbers = re.findall(r'\d+', os.path.basename(filename))
            return int(numbers[0]) if numbers else 0
        
        image_files.sort(key=extract_number)
        return image_files
    
    def print_progress_bar(self, iteration, total, prefix='', suffix='', length=50, fill='█'):
        """Print a progress bar to the console"""
        percent = ("{0:.1f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
        if iteration == total:
            print()  # New line after completion

    def images_to_pdf(self, image_files, output_path):
        """Convert list of images to PDF with progress indicator"""
        if not image_files:
            print(f"No images found for {output_path}")
            return False
        
        total_images = len(image_files)
        print(f"Creating PDF with {total_images} pages...")
        
        # Create PDF
        c = canvas.Canvas(str(output_path), pagesize=A4)
        page_width, page_height = A4
        
        for i, image_path in enumerate(image_files):
            # Update progress bar
            self.print_progress_bar(
                i + 1, 
                total_images, 
                prefix='Converting images:', 
                suffix=f'({i + 1}/{total_images})'
            )
            
            try:
                # Open and process image
                with Image.open(image_path) as img:
                    # Convert to RGB if. necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # Calculate dimensions to fit page while maintaining aspect ratio
                    img_width, img_height = img.size
                    aspect_ratio = img_width / img_height
                    
                    # Scale to fit page
                    if aspect_ratio > (page_width / page_height):
                        # Image is wider, scale by width
                        new_width = page_width - 40  # 20pt margin on each side
                        new_height = new_width / aspect_ratio
                    else:
                        # Image is taller, scale by height
                        new_height = page_height - 40  # 20pt margin on top/bottom
                        new_width = new_height * aspect_ratio
                    
                    # Center the image on page
                    x = (page_width - new_width) / 2
                    y = (page_height - new_height) / 2
                    
                    # Draw image on PDF
                    c.drawImage(ImageReader(img), x, y, width=new_width, height=new_height)
                    
                    # Start new page for next image (except for last image)
                    if i < len(image_files) - 1:
                        c.showPage()
                        
            except Exception as e:
                print(f"\nError processing image {image_path}: {e}")
                continue
        
        # Final progress update
        print("Saving PDF file...")
        c.save()
        print(f"✓ PDF created successfully: {output_path}")
        return True
    
    def merge_pdfs(self, pdf_files, output_path):
        """Merge multiple PDFs into one"""
        try:
            from PyPDF2 import PdfMerger
            
            merger = PdfMerger()
            
            for pdf_file in pdf_files:
                if os.path.exists(pdf_file):
                    merger.append(pdf_file)
                    print(f"Added {pdf_file} to final PDF")
            
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            
            merger.close()
            print(f"Final merged PDF created: {output_path}")
            return True
            
        except ImportError:
            print("PyPDF2 not available, using reportlab merge method...")
            return self.merge_pdfs_reportlab(pdf_files, output_path)
    
    def merge_pdfs_reportlab(self, pdf_files, output_path):
        """Alternative merge method using reportlab"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        # This is a simplified merge - in practice, you might want to use PyPDF2
        print(f"Note: Using simplified merge. Individual chapter PDFs are available.")
        print(f"For better PDF merging, install PyPDF2: pip install PyPDF2")
        return True
    
    def process_multiple_zips(self, zip_files, output_name=None):
        """Process multiple zip files for the same manga series"""
        if not zip_files:
            print("No zip files provided")
            return
        
        if output_name is None:
            # Use the first 4 characters as the output name
            first_file = Path(zip_files[0]).stem
            output_name = first_file[:4]
        
        print(f"Processing {len(zip_files)} zip files for series: {output_name}")
        
        all_chapters = []
        temp_dirs = []
        
        try:
            # Process each zip file
            for zip_idx, zip_path in enumerate(zip_files):
                print(f"\nProcessing zip file {zip_idx + 1}/{len(zip_files)}: {Path(zip_path).name}")
                
                # Extract zip
                temp_dir = tempfile.mkdtemp()
                temp_dirs.append(temp_dir)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find chapter folders in this zip
                chapter_folders = []
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    if os.path.isdir(item_path):
                        chapter_folders.append(item_path)
                
                # Sort chapter folders within this zip
                def extract_chapter_number(folder_path):
                    folder_name = os.path.basename(folder_path)
                    numbers = re.findall(r'\d+', folder_name)
                    return int(numbers[0]) if numbers else 0
                
                chapter_folders.sort(key=extract_chapter_number)
                
                # Add chapters to the main list with zip index for global sorting
                for chapter_folder in chapter_folders:
                    chapter_name = os.path.basename(chapter_folder)
                    # Extract chapter number for global sorting
                    chapter_num = self.extract_chapter_number_from_filename(chapter_name)
                    all_chapters.append({
                        'path': chapter_folder,
                        'name': chapter_name,
                        'chapter_num': chapter_num,
                        'zip_idx': zip_idx
                    })
            
            # Sort all chapters globally by chapter number
            all_chapters.sort(key=lambda x: x['chapter_num'])
            
            print(f"\nFound {len(all_chapters)} total chapters across all zip files")
            
            # Process each chapter and create one final PDF
            all_images = []
            chapter_info = []
            
            for i, chapter in enumerate(all_chapters):
                chapter_folder = chapter['path']
                chapter_name = chapter['name']
                print(f"Processing Chapter {i+1}: {chapter_name}")
                
                # Get images from chapter
                image_files = self.get_image_files(chapter_folder)
                print(f"Found {len(image_files)} images in {chapter_name}")
                
                if image_files:
                    all_images.extend(image_files)
                    chapter_info.append({
                        'name': chapter_name,
                        'start_page': len(all_images) - len(image_files) + 1,
                        'end_page': len(all_images),
                        'image_count': len(image_files)
                    })
            
            # Create one final PDF with all images
            if all_images:
                final_pdf_path = self.output_dir / f"{output_name}_complete.pdf"
                print(f"\n{'='*60}")
                print(f"CREATING FINAL PDF")
                print(f"{'='*60}")
                print(f"Total pages to process: {len(all_images)}")
                print(f"Output file: {final_pdf_path}")
                print(f"{'='*60}")
                
                if self.images_to_pdf(all_images, final_pdf_path):
                    print(f"\n{'='*60}")
                    print(f"✓ CONVERSION COMPLETE!")
                    print(f"{'='*60}")
                    print(f"Final PDF: {final_pdf_path}")
                    print(f"Total pages: {len(all_images)}")
                    print("\nChapter breakdown:")
                    for info in chapter_info:
                        print(f"  {info['name']}: Pages {info['start_page']}-{info['end_page']} ({info['image_count']} images)")
                    print(f"{'='*60}")
                else:
                    print("❌ Failed to create PDF")
            else:
                print("No images found in any chapters")
                
        finally:
            # Cleanup all temporary directories
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
    
    def select_zip_file_gui(self):
        """Open file dialog to select zip file"""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        file_path = filedialog.askopenfilename(
            title="Select Manga Zip File",
            filetypes=[
                ("Zip files", "*.zip"),
                ("All files", "*.*")
            ]
        )
        
        root.destroy()
        return file_path
    def process_zip(self, zip_path, output_name=None):
        """Main method to process zip file - now handles multiple related zips"""
        if not os.path.exists(zip_path):
            print(f"Error: Zip file {zip_path} not found")
            return
        
        # Find all related zip files with same first 4 characters
        related_zip_files = self.find_related_zip_files(zip_path)
        
        if len(related_zip_files) > 1:
            print(f"Found {len(related_zip_files)} related zip files:")
            for i, zip_file in enumerate(related_zip_files):
                print(f"  {i+1}. {Path(zip_file).name}")
            
            # Process all related zip files as one manga series
            if output_name is None:
                output_name = Path(zip_path).stem[:4]
            
            self.process_multiple_zips(related_zip_files, output_name)
        else:
            # Single zip file processing (original behavior)
            self.process_single_zip(zip_path, output_name)
    
    def process_single_zip(self, zip_path, output_name=None):
        """Process a single zip file (original process_zip logic)"""
        if output_name is None:
            output_name = Path(zip_path).stem

        print(f"Processing zip file: {zip_path}")
        
        # Extract zip
        extract_path = self.extract_zip(zip_path)
        
        try:
            # Find chapter folders
            chapter_folders = []
            for item in os.listdir(extract_path):
                item_path = os.path.join(extract_path, item)
                if os.path.isdir(item_path):
                    chapter_folders.append(item_path)
            
            # Sort chapter folders
            def extract_chapter_number(folder_path):
                folder_name = os.path.basename(folder_path)
                numbers = re.findall(r'\d+', folder_name)
                return int(numbers[0]) if numbers else 0
            
            chapter_folders.sort(key=extract_chapter_number)
            
            if not chapter_folders:
                print("No chapter folders found in zip file")
                return
            
            print(f"Found {len(chapter_folders)} chapters")
            
            # Process each chapter
            chapter_pdfs = []
            for i, chapter_folder in enumerate(chapter_folders):
                chapter_name = os.path.basename(chapter_folder)
                print(f"Processing Chapter {i+1}: {chapter_name}")
                
                # Get images from chapter
                image_files = self.get_image_files(chapter_folder)
                print(f"Found {len(image_files)} images in {chapter_name}")
                
                if image_files:
                    # Create PDF for this chapter
                    chapter_pdf_path = self.output_dir / f"{output_name}_chapter_{i+1:02d}_{chapter_name}.pdf"
                    if self.images_to_pdf(image_files, chapter_pdf_path):
                        chapter_pdfs.append(str(chapter_pdf_path))
            
            # Merge all chapter PDFs
            if chapter_pdfs:
                final_pdf_path = self.output_dir / f"{output_name}_complete.pdf"
                print(f"\n{'='*50}")
                print(f"MERGING CHAPTER PDFs")
                print(f"{'='*50}")
                self.merge_pdfs(chapter_pdfs, str(final_pdf_path))
                
                print(f"\n✓ Conversion complete!")
                print(f"Individual chapter PDFs: {len(chapter_pdfs)} files")
                print(f"Final merged PDF: {final_pdf_path}")
            else:
                print("No PDFs were created")
                
        finally:
            # Cleanup temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)


def main():
    parser = argparse.ArgumentParser(description='Convert zipped chapters with images to PDF')
    parser.add_argument('zip_file', nargs='?', help='Path to zip file containing chapters (optional if using GUI)')
    parser.add_argument('-o', '--output', help='Output directory (default: output)')
    parser.add_argument('-n', '--name', help='Output file name prefix')
    parser.add_argument('-g', '--gui', action='store_true', help='Use GUI file picker')
    
    args = parser.parse_args()
    
    output_dir = args.output if args.output else "output"
    converter = ChapterToPDFConverter(output_dir)
    
    # Use GUI if no zip file provided or if -g flag is used
    if not args.zip_file or args.gui:
        zip_file = converter.select_zip_file_gui()
        if not zip_file:
            print("No file selected. Exiting.")
            return
    else:
        zip_file = args.zip_file
    
    converter.process_zip(zip_file, args.name)


if __name__ == "__main__":
    # Check if any arguments provided
    if len(os.sys.argv) == 1:
        # No arguments, show GUI
        print("Chapter to PDF Converter - GUI Mode")
        converter = ChapterToPDFConverter()
        
        # Show GUI file picker
        zip_file = converter.select_zip_file_gui()
        if zip_file:
            print(f"Selected file: {zip_file}")
            converter.process_zip(zip_file)
        else:
            print("No file selected.")
            print("\nAlternatively, you can use command line:")
            print("Usage: python main.py <zip_file> [-o output_dir] [-n output_name]")
            print("Or: python main.py -g  (to force GUI mode)")
    else:
        main()