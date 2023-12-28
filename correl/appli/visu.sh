ffmpeg -framerate 250 -i Out_correl/vignets/50/IGN2_202311281603-00-cam-22348136-%4d_50.png -c:v libx264 target_50.mp4
ffmpeg -framerate 250 -i Out_correl/vignets/51/IGN2_202311281603-00-cam-22348136-%4d_51.png -c:v libx264 target_51.mp4
ffmpeg -framerate 250 -i Out_correl/vignets/52/IGN2_202311281603-00-cam-22348136-%4d_52.png -c:v libx264 target_52.mp4
ffmpeg -framerate 250 -i Out_correl/vignets/53/IGN2_202311281603-00-cam-22348136-%4d_53.png -c:v libx264 target_53.mp4
ffmpeg -framerate 250 -i Out_correl/vignets/54/IGN2_202311281603-00-cam-22348136-%4d_54.png -c:v libx264 target_54.mp4
ffmpeg -framerate 250 -i Out_correl/vignets/G2/IGN2_202311281603-00-cam-22348136-%4d_G2.png -c:v libx264 target_G2.mp4
ffmpeg -framerate 250 -i Out_correl/vignets/55/IGN2_202311281603-00-cam-22348136-%4d_55.png -c:v libx264 target_55.mp4
ffmpeg -framerate 250 -i Out_correl/vignets/56/IGN2_202311281603-00-cam-22348136-%4d_56.png -c:v libx264 target_56.mp4
ffmpeg -framerate 250 -i Out_correl/vignets/57/IGN2_202311281603-00-cam-22348136-%4d_57.png -c:v libx264 target_57.mp4
ffmpeg -framerate 250 -i Out_correl/vignets/S32/IGN2_202311281603-00-cam-22348136-%4d_S32.png -c:v libx264 target_S32.mp4
ffmpeg -framerate 250 -i Out_correl/vignets/S33/IGN2_202311281603-00-cam-22348136-%4d_S33.png -c:v libx264 target_S33.mp4
ffmpeg -framerate 250 -i Out_correl/vignets/S34/IGN2_202311281603-00-cam-22348136-%4d_S34.png -c:v libx264 target_S34.mp4

/usr/bin/Rscript plot.r
