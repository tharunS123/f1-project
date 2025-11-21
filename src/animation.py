import os
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from src.f1_data import DT

def create_plot(example_lap):
  fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
  ax.axis('off')

  plot_x_ref = example_lap['X'].to_numpy()
  plot_y_ref = example_lap['Y'].to_numpy()

  # compute tangents
  dx = np.gradient(plot_x_ref)
  dy = np.gradient(plot_y_ref)

  # Create a map of the track from the fastf1 data
  norm = np.sqrt(dx**2 + dy**2)
  dx /= norm
  dy /= norm

  nx = -dy
  ny = dx

  track_width = 500

  x_outer = plot_x_ref + nx * (track_width / 2)
  y_outer = plot_y_ref + ny * (track_width / 2)
  x_inner = plot_x_ref - nx * (track_width / 2)
  y_inner = plot_y_ref - ny * (track_width / 2)

  # Check if a background image exists in the resources folder
  background_image_path = os.path.join("resources", "background.png")
  if os.path.exists(background_image_path):
    # Load and display the background image
    img = mpimg.imread(background_image_path)
    ax.imshow(img, extent=[-1, 1, -1, 1], aspect='auto', zorder=-1)
  else:
    # draw track on the same axes used for animation and enforce equal aspect
    ax.plot(plot_x_ref, plot_y_ref, linewidth=10, color='gray', label="centre")
    ax.plot(x_outer, y_outer, linewidth=5, color='gray', label="outer")
    ax.plot(x_inner, y_inner, linewidth=5, color='gray', label="inner")

  ax.set_aspect('equal', adjustable='box')
  ax.axis('off')

  return fig, ax, plot_x_ref, plot_y_ref, x_inner, y_inner, x_outer, y_outer

def create_animation(frames, example_lap, drivers, output_file, playback_speed=1, still_frame=False): 

  n_frames = 1 if still_frame else len(frames)

  # Create the track map

  fig, ax, plot_x_ref, plot_y_ref, x_inner, y_inner, x_outer, y_outer = create_plot(example_lap)

  # precompute limits with a small padding to avoid autoscaling changing aspect
  x_min = min(plot_x_ref.min(), x_inner.min(), x_outer.min())
  x_max = max(plot_x_ref.max(), x_inner.max(), x_outer.max())
  y_min = min(plot_y_ref.min(), y_inner.min(), y_outer.min())
  y_max = max(plot_y_ref.max(), y_inner.max(), y_outer.max())
  # pad_x = (x_max - x_min) * 0.03
  # pad_y = (y_max - y_min) * 0.03
  # xlims = (x_min - pad_x, x_max + pad_x)
  # ylims = (y_min - pad_y, y_max + pad_y)
  # ax.set_xlim(*xlims)
  # ax.set_ylim(*ylims)

  # initialize scatter with empty Nx2 array shape when setting offsets in init()
  car_scatter = ax.scatter([], [], s=20)

  # Animate the cars for the first 100 frames

  # labels = []
  # for _ in drivers:
  #   txt = ax.text(0, 0, "", fontsize=6, ha="center", va="center")
  #   labels.append(txt)

  def init():
    ax.axis('off')
    # set_offsets expects an (N,2) array — use an explicitly-shaped empty array for zero points
    car_scatter.set_offsets(np.empty((0, 2)))
    return [car_scatter]

  def update(frame_num):
    if not still_frame:  # Only clear the axes during animation
      ax.clear()
    # Redraw track each frame but keep fixed aspect and limits so the track doesn't squash
    ax.plot(plot_x_ref, plot_y_ref, linewidth=1, color='gray')
    ax.plot(x_outer, y_outer, linewidth=1, color='gray')
    ax.plot(x_inner, y_inner, linewidth=1, color='gray')
    ax.set_aspect('equal', adjustable='box')
    # ax.set_xlim(*xlims)
    # ax.set_ylim(*ylims)
    ax.axis('off')

    if not still_frame:  # Only add cars and title during animation
        frame = frames[frame_num]
        print(f"Animating frame {frame_num+1}/{n_frames}, time={frame['t']:.1f}s")
        for driver_code, pos in frame['drivers'].items():
            ax.plot(pos['x'], pos['y'], 'o')
        ax.set_title(f"Time: {frame['t']:.1f} s")

  anim = animation.FuncAnimation(
    fig,
    update,
    frames=n_frames,
    init_func=init,
    blit=False,
    interval=DT * 1000 / playback_speed,  # ms between frames
    repeat=False
  )

  if still_frame:
    print("Saving still frame...")
    update(0)
    fig.savefig("still_frame.png", dpi=150, bbox_inches='tight')
    print(f"Done! Saved to {output_file}")
    return

  # 7. Save animation (mp4)
  print("Saving animation... (this can take a bit)")
  anim.save(output_file, writer="ffmpeg", fps=int(playback_speed / DT), dpi=150)
  print(f"Done! Saved to {output_file}")