# Monitoring Sourdough Starter with Simple Computer Vision
Fermentation tracker for making the best bread possible.

# Instructions
1. Copy image folder from Pi to here
2. Run analysis in Jupyter Notebook
3. Export gif
4. Copy gif to Final Images folder
5. Run the following to convert to mp4 (optional)

```
ffmpeg -i timelapse.gif -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" timelapse.mp4
```

Saving figures from Jupyter Notebook have transparent backgrounds, which don't render as nicely on the web. To make the background white, use:

```
convert -flatten img1.png img1-white.png
```
