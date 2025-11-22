# PWA Icons

This directory should contain the following icon files for the Progressive Web App:

## Required Icons

- `icon-72x72.png` - 72x72px icon
- `icon-96x96.png` - 96x96px icon
- `icon-128x128.png` - 128x128px icon
- `icon-144x144.png` - 144x144px icon
- `icon-152x152.png` - 152x152px icon
- `icon-192x192.png` - 192x192px icon (required)
- `icon-384x384.png` - 384x384px icon
- `icon-512x512.png` - 512x512px icon (required)

## Icon Guidelines

1. **Format**: PNG with transparent background
2. **Safe Zone**: Keep important content within 80% of the icon area
3. **Purpose**: Set `purpose: "any maskable"` in manifest
4. **Colors**: Use brand colors (#1976d2 for TritIQ)
5. **Design**: Simple, recognizable logo that works at all sizes

## Generating Icons

You can use the existing `Tritiq.png` logo and resize it to the required dimensions using:

```bash
# Using ImageMagick
convert Tritiq.png -resize 192x192 icons/icon-192x192.png
convert Tritiq.png -resize 512x512 icons/icon-512x512.png
# ... repeat for all sizes
```

Or use online tools like:
- https://realfavicongenerator.net/
- https://www.pwa-icon-generator.com/

## Testing

After adding icons, test the PWA installation on:
- Chrome/Edge on Android
- Safari on iOS
- Chrome on Desktop

Verify that:
- Icons appear correctly in the install prompt
- Home screen icon looks good
- Splash screen shows the correct icon
