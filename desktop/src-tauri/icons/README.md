# App Icons

Tauri requires icons in multiple formats and sizes. 

## Generate Icons

Use the Tauri icon generator:

```bash
npm run tauri icon public/icon.svg
```

Or generate manually from the SVG:

### Required files:
- `32x32.png` - 32x32 pixels
- `128x128.png` - 128x128 pixels  
- `128x128@2x.png` - 256x256 pixels
- `icon.icns` - macOS app icon
- `icon.ico` - Windows icon

### Using ImageMagick:

```bash
# Install ImageMagick
brew install imagemagick

# Convert SVG to PNGs
convert -background none -resize 32x32 ../public/icon.svg 32x32.png
convert -background none -resize 128x128 ../public/icon.svg 128x128.png
convert -background none -resize 256x256 ../public/icon.svg 128x128@2x.png

# For macOS icns (requires iconutil)
mkdir icon.iconset
convert -background none -resize 16x16 ../public/icon.svg icon.iconset/icon_16x16.png
convert -background none -resize 32x32 ../public/icon.svg icon.iconset/icon_16x16@2x.png
convert -background none -resize 32x32 ../public/icon.svg icon.iconset/icon_32x32.png
convert -background none -resize 64x64 ../public/icon.svg icon.iconset/icon_32x32@2x.png
convert -background none -resize 128x128 ../public/icon.svg icon.iconset/icon_128x128.png
convert -background none -resize 256x256 ../public/icon.svg icon.iconset/icon_128x128@2x.png
convert -background none -resize 256x256 ../public/icon.svg icon.iconset/icon_256x256.png
convert -background none -resize 512x512 ../public/icon.svg icon.iconset/icon_256x256@2x.png
convert -background none -resize 512x512 ../public/icon.svg icon.iconset/icon_512x512.png
convert -background none -resize 1024x1024 ../public/icon.svg icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset
rm -rf icon.iconset
```

### Online Tools:
- https://cloudconvert.com/svg-to-icns
- https://www.icoconverter.com/
